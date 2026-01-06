"""
Gmail RAG Service.
Processes extracted emails into the vector database using the existing RAG pipeline.
"""
import logging
import uuid
import os
from typing import List, Dict
from sqlalchemy.orm import Session

# Import existing services we want to reuse to ensure consistency
from app.services.chunking_service import chunk_blocks
from app.services.embedding_service import create_embeddings, load_embedding_model
from app.services.qdrant_service import get_qdrant_client, create_collection_if_not_exists, upload_to_qdrant
from app.services.tenant_service import get_tenant_service
from app.models.tenant_knowledge_base import TenantKnowledgeBase
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)

# Load models once (singleton pattern usage from existing codebase)
embedding_model = load_embedding_model()
qdrant_client = get_qdrant_client()

class GmailRAGService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        
    def process_emails_to_kb(self, emails: List[Dict]) -> int:
        """
        Process a list of parsed emails into the tenant's Gmail knowledge base.
        
        Args:
            emails: List of dicts containing 'subject', 'body', 'sender', etc.
            
        Returns:
            Number of chunks uploaded.
        """
        if not emails:
            return 0
            
        # 0. Filter out duplicates (already processed emails)
        from app.models.gmail import GmailMessage
        
        # Get IDs of all emails in this batch
        email_ids = [e['id'] for e in emails]
        
        # Find which of these IDs already exist in DB
        existing_ids = self.db.query(GmailMessage.gmail_message_id).filter(
            GmailMessage.tenant_id == self.tenant_id,
            GmailMessage.gmail_message_id.in_(email_ids)
        ).all()
        existing_ids_set = {id[0] for id in existing_ids}
        
        # Filter the list to only new emails
        new_emails = [e for e in emails if e['id'] not in existing_ids_set]
        
        if not new_emails:
            logger.info("All emails in this batch have already been processed.")
            return 0
            
        logger.info(f"Processing {len(new_emails)} new emails (filtered out {len(emails) - len(new_emails)} duplicates)")

        # 1. Prepare Content Blocks
        # Convert emails to the "Block" format expected by our cleaning/chunking service
        blocks = []
        for email in new_emails:
            # Create a header block (context)
            header_text = f"Email from {email['sender']} on {email['date']}\nSubject: {email['subject']}"
            blocks.append({
                "type": "Title",
                "text": header_text,
                "metadata": {"email_id": email['id'], "source": "gmail", "type": "header"}
            })
            
            # Create body block
            if email['body']:
                # DEBUG: Log the body length and snippet
                logger.info(f"Email {email.get('id')} body length: {len(email['body'])}")
                logger.info(f"Email body snippet: {email['body'][:200]}")

                blocks.append({
                    "type": "Text",
                    "text": email['body'],
                    "metadata": {
                        "email_id": email['id'], 
                        "source": "gmail", 
                        "sender": email['sender'],
                        "subject": email['subject'],
                        "date": email['date']
                    }
                })
            else:
                logger.warning(f"Email {email.get('id')} has empty body.")


        # 2. Reuse Existing Chunking Logic
        # This breaks large emails into smaller, semantic pieces suitable for RAG
        # We use a smaller target_chunk_words because emails can be short
        final_chunks = chunk_blocks(blocks, target_chunk_words=50)
        if not final_chunks:
            logger.info(f"No valid chunks generated from {len(new_emails)} emails.")
            return 0
            
        # 3. Reuse Existing Embedding Logic
        # Turns text chunks into vectors using the standard model
        chunks_with_embeddings = create_embeddings(final_chunks, embedding_model)
        
        # 4. Get/Create Tenant Gmail Collection
        # We start by ensuring a dedicated KB entry exists for Gmail
        kb_name = "gmail_emails"
        collection_name = self._ensure_gmail_collection(kb_name)
        
        # 5. Reuse Existing Upload Logic
        # Uploads vectors to Qdrant with proper tenant isolation
        upload_to_qdrant(qdrant_client, collection_name, chunks_with_embeddings, tenant_id=self.tenant_id)
        
        # 5. Save Metadata to SQL for History
        self._save_gmail_messages(new_emails)
        
        logger.info(f"Successfully processed {len(new_emails)} emails into {len(final_chunks)} vector chunks for tenant {self.tenant_id}")
        return len(final_chunks)

    def _save_gmail_messages(self, emails: List[Dict]):
        """Save metadata of processed emails to Postgres."""
        from app.models.gmail import GmailMessage
        from dateutil import parser
        
        for email in emails:
            # Check for duplicate using gmail_message_id
            exists = self.db.query(GmailMessage).filter(
                GmailMessage.tenant_id == self.tenant_id,
                GmailMessage.gmail_message_id == email['id']
            ).first()
            
            if not exists:
                try:
                    # Parse date string (e.g., "Mon, 06 Jan 2026 12:00:00 +0000")
                    received_at = parser.parse(email['date']) if email.get('date') else None
                except Exception:
                    received_at = None
                    
                msg = GmailMessage(
                    tenant_id=self.tenant_id,
                    gmail_message_id=email['id'],
                    thread_id=email.get('threadId'),
                    subject=email.get('subject')[:500] if email.get('subject') else None,
                    sender=email.get('sender')[:255] if email.get('sender') else None,
                    snippet=email.get('snippet')[:1000] if email.get('snippet') else None,
                    received_at=received_at
                )
                self.db.add(msg)
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to save Gmail message metadata: {e}")
            self.db.rollback()

    def _ensure_gmail_collection(self, kb_name: str) -> str:
        """
        Ensure a 'gmail_emails' knowledge base and Qdrant collection exist.
        Returns the physical collection name.
        """
        # Check if KB record exists
        kb = self.db.query(TenantKnowledgeBase).filter(
            TenantKnowledgeBase.tenant_id == self.tenant_id,
            TenantKnowledgeBase.kb_name == kb_name
        ).first()

        # Get physical collection name from TenantService
        tenant_service = get_tenant_service(qdrant_client)
        collection_name = tenant_service.get_collection_name(self.tenant_id, kb_name)
        
        if not kb:
            # Create KB record
            model_name = os.getenv('EMBEDDING_MODEL_NAME', 'BAAI/bge-m3')
            
            kb = TenantKnowledgeBase(
                tenant_id=self.tenant_id,
                kb_name=kb_name,
                collection_name=collection_name, 
                description="Automatically synced emails from Gmail",
                embedding_model=model_name,
                is_active=True
            )
            self.db.add(kb)
            self.db.commit()
        
        # Ensure Qdrant collection exists
        create_collection_if_not_exists(qdrant_client, collection_name)
        
        return collection_name
