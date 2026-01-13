"""
Dynamics 365 RAG Service.
Processes fetched emails into the vector database.
"""
import logging
import os
from typing import List, Dict
from sqlalchemy.orm import Session
from dateutil import parser

# Import reusable services
from app.services.chunking_service import chunk_blocks
from app.services.embedding_service import create_embeddings, load_embedding_model
from app.services.qdrant_service import get_qdrant_client, create_collection_if_not_exists, upload_to_qdrant
from app.services.tenant_service import get_tenant_service
from app.models.tenant_knowledge_base import TenantKnowledgeBase
from app.models.dynamics import DynamicsMessage

logger = logging.getLogger(__name__)

# Load models once
embedding_model = load_embedding_model()
qdrant_client = get_qdrant_client()

class DynamicsRAGService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        
    def process_emails_to_kb(self, emails: List[Dict]) -> int:
        """
        Process a list of Dynamics emails into the tenant's Dynamics KB.
        """
        if not emails:
            return 0
            
        # 0. Filter duplicates
        # Get IDs of all emails in this batch
        activity_ids = [e['id'] for e in emails]
        
        # Check against DB
        existing_ids = self.db.query(DynamicsMessage.activity_id).filter(
            DynamicsMessage.tenant_id == self.tenant_id,
            DynamicsMessage.activity_id.in_(activity_ids)
        ).all()
        existing_ids_set = {id[0] for id in existing_ids}
        
        new_emails = [e for e in emails if e['id'] not in existing_ids_set]
        
        if not new_emails:
            logger.info("All Dynamics emails in this batch have already been processed.")
            return 0
            
        logger.info(f"Processing {len(new_emails)} new Dynamics emails")

        # 1. Prepare Content Blocks
        blocks = []
        for email in new_emails:
            header_text = f"Dynamics Email from {email['sender']}\nSubject: {email['subject']}\nDate: {email['created_at']}"
            blocks.append({
                "type": "Title",
                "text": header_text,
                "metadata": {"activity_id": email['id'], "source": "dynamics", "type": "header"}
            })
            
            if email['body']:
                blocks.append({
                    "type": "Text",
                    "text": email['body'],
                    "metadata": {
                        "activity_id": email['id'], 
                        "source": "dynamics", 
                        "sender": email['sender'],
                        "subject": email['subject']
                    }
                })

        # 2. Chunking
        final_chunks = chunk_blocks(blocks, target_chunk_words=50)
        if not final_chunks:
            return 0
            
        # 3. Embedding
        chunks_with_embeddings = create_embeddings(final_chunks, embedding_model)
        
        # 4. Get/Create Collection
        kb_name = "dynamics_emails"
        collection_name = self._ensure_dynamics_collection(kb_name)
        
        # 5. Upload
        upload_to_qdrant(qdrant_client, collection_name, chunks_with_embeddings, tenant_id=self.tenant_id)
        
        # 6. Save History
        self._save_messages(new_emails)
        
        return len(final_chunks)

    def _save_messages(self, emails: List[Dict]):
        """Save metadata to SQL."""
        for email in emails:
            # Re-check for safety
            exists = self.db.query(DynamicsMessage).filter(
                DynamicsMessage.tenant_id == self.tenant_id,
                DynamicsMessage.activity_id == email['id']
            ).first()
            
            if not exists:
                created_at = None
                if email.get('created_at'):
                    try:
                        created_at = parser.parse(email['created_at'])
                    except:
                        pass
                
                msg = DynamicsMessage(
                    tenant_id=self.tenant_id,
                    activity_id=email['id'],
                    subject=email.get('subject')[:500] if email.get('subject') else None,
                    sender=email.get('sender')[:255] if email.get('sender') else None,
                    raw_body=email.get('raw_body'),
                    created_at=created_at
                )
                self.db.add(msg)
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to save Dynamics message history: {e}")
            self.db.rollback()

    def _ensure_dynamics_collection(self, kb_name: str) -> str:
        """Ensure specific KB collection exists."""
        kb = self.db.query(TenantKnowledgeBase).filter(
            TenantKnowledgeBase.tenant_id == self.tenant_id,
            TenantKnowledgeBase.kb_name == kb_name
        ).first()

        tenant_service = get_tenant_service(qdrant_client)
        collection_name = tenant_service.get_collection_name(self.tenant_id, kb_name)
        
        if not kb:
            model_name = os.getenv('EMBEDDING_MODEL_NAME', 'BAAI/bge-m3')
            kb = TenantKnowledgeBase(
                tenant_id=self.tenant_id,
                kb_name=kb_name,
                collection_name=collection_name, 
                description="Synced emails from Dynamics 365",
                embedding_model=model_name,
                is_active=True
            )
            self.db.add(kb)
            self.db.commit()
        
        create_collection_if_not_exists(qdrant_client, collection_name)
        return collection_name
