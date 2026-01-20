import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@ecostance.com")

    def send_invite_email(self, to_email: str, invite_link: str) -> bool:
        subject = "Invitation to EcoStance"
        body = f"""
        <html>
            <body>
                <h2>Welcome to EcoStance!</h2>
                <p>You have been invited to join EcoStance.</p>
                <p>Please click the link below to set your password and access your account:</p>
                <p><a href="{invite_link}">Accept Invitation</a></p>
                <p>This link will expire in 48 hours.</p>
                <p>If you did not expect this invitation, please ignore this email.</p>
            </body>
        </html>
        """
        return self._send_email(to_email, subject, body, is_html=True)
    
    def _send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        if not self.username or not self.password:
            # For development, just log the email if credentials are missing
            logger.warning("SMTP credentials not configured. Email not sent.")
            logger.info(f"--- MOCK EMAIL ---")
            logger.info(f"To: {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Link present: {'Invite Link' in body or 'href' in body}")
            logger.info(f"------------------")
            return True # Return True to not block the flow in dev

        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
