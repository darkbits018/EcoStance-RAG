import logging
import os
from typing import List, Dict
from sqlalchemy.orm import Session
from dateutil import parser

# Reuse existing services
from app.services.chunking_service import chunk_blocks
from app.services.embedding_service import create_embeddings, load_embedding_model
from app.services.qdrant_service import get_qdrant_client, create_collection_if_not_exists, upload_to_qdrant
from app.services.tenant_service import get_tenant_service
from app.models.tenant_knowledge_base import TenantKnowledgeBase
from app.models.custom_crm import CustomCRMEmail

logger = logging.getLogger(__name__)

# Load models once (singleton pattern usage)
embedding_model = load_embedding_model()
qdrant_client = get_qdrant_client()

class CustomCRMRAGService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def process_emails_to_kb(self, emails: List[Dict]) -> int:
        """
        Process a list of CRM emails into the tenant's Custom CRM knowledge base.
        """
        if not emails:
            return 0

        # Filter duplicates based on crm_email_id
        email_ids = [e['id'] for e in emails]
        existing_ids = self.db.query(CustomCRMEmail.crm_email_id).filter(
            CustomCRMEmail.tenant_id == self.tenant_id,
            CustomCRMEmail.crm_email_id.in_(email_ids)
        ).all()
        existing_ids_set = {id[0] for id in existing_ids}
        
        new_emails = [e for e in emails if e['id'] not in existing_ids_set]
        
        if not new_emails:
            logger.info("All Custom CRM emails have already been processed.")
            return 0
            
        logger.info(f"Processing {len(new_emails)} new emails from Custom CRM")

        # 1. Prepare Content Blocks
        blocks = []
        for email in new_emails:
            header_text = f"Email from {email.get('sender', 'Unknown')} on {email.get('received_at', 'Unknown Pattern')}\nSubject: {email.get('subject', 'No Subject')}"
            
            blocks.append({
                "type": "Title",
                "text": header_text,
                "metadata": {
                    "email_id": email['id'], 
                    "source": "custom_crm", 
                    "type": "header"
                }
            })
            
            # Prefer body_text, fallback to body_html (stripped), or snippet
            content = email.get('body_text') or email.get('snippet') or ""
            if content:
                blocks.append({
                    "type": "Text",
                    "text": content,
                    "metadata": {
                        "email_id": email['id'],
                        "source": "custom_crm",
                        "sender": email.get('sender'),
                        "subject": email.get('subject'),
                        "date": email.get('received_at')
                    }
                })

        # 2. Chunking
        final_chunks = chunk_blocks(blocks, target_chunk_words=100)
        if not final_chunks:
            return 0

        # 3. Embedding
        chunks_with_embeddings = create_embeddings(final_chunks, embedding_model)

        # 4. Collection Management
        kb_name = "custom_crm_emails"
        collection_name = self._ensure_collection(kb_name)

        # 5. Upload
        upload_to_qdrant(qdrant_client, collection_name, chunks_with_embeddings, tenant_id=self.tenant_id)

        # 6. Save History
        self._save_sync_history(new_emails)

        return len(final_chunks)

    def _save_sync_history(self, emails: List[Dict]):
        """Record synced emails in the SQL database."""
        for email in emails:
            try:
                # CRM likely sends ISO format string, but verify parsing
                received_at = None
                if email.get('received_at'):
                    if isinstance(email['received_at'], str):
                         received_at = parser.parse(email['received_at'])
                    else:
                        received_at = email['received_at'] # already datetime?

                record = CustomCRMEmail(
                    tenant_id=self.tenant_id,
                    crm_email_id=email['id'],
                    subject=email.get('subject'),
                    sender=email.get('sender'),
                    received_at=received_at
                )
                self.db.add(record)
            except Exception as e:
                logger.error(f"Error saving history for email {email.get('id')}: {e}")
        
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"DB Commit error: {e}")
            self.db.rollback()

    def _ensure_collection(self, kb_name: str) -> str:
        """Ensure KB record and Qdrant collection exist."""
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
                description="Synced emails from Custom CRM",
                embedding_model=model_name,
                is_active=True
            )
            self.db.add(kb)
            self.db.commit()

        create_collection_if_not_exists(qdrant_client, collection_name)
        return collection_name
