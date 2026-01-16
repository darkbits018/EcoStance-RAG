from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.models.connection import GmailConnection
from app.core.config import settings
from google_auth_oauthlib.flow import Flow

router = APIRouter()

@router.get("/login")
def login():
    if not settings.GOOGLE_CLIENT_ID or "dummy" in settings.GOOGLE_CLIENT_ID:
         # Return a special error or just a url that will fail but let the user know
         return {
             "url": "", 
             "error": "Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your backend .env file."
         }

    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    
    # Scopes required for the app
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    # Generate URL
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    return {"url": auth_url}

from googleapiclient.discovery import build
from sqlmodel import select

@router.get("/callback")
def callback(code: str, session: Session = Depends(get_session)):
    if not settings.GOOGLE_CLIENT_ID or "dummy" in settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Backend configuration error: credentials missing")

    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    # Exchange code for token
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    # Fetch User Profile to get Email Address
    try:
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile['emailAddress']
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Failed to fetch user profile: {str(e)}")
    
    # Check if exists
    existing = session.exec(select(GmailConnection).where(GmailConnection.email_address == email_address)).first()
    
    if existing:
        existing.access_token = creds.token
        # Refresh token is only returned when prompt='consent' is used and it's the first time
        if creds.refresh_token:
            existing.refresh_token = creds.refresh_token
        existing.token_expiry = creds.expiry
        existing.is_active = True
        session.add(existing)
    else:
        new_conn = GmailConnection(
            email_address=email_address,
            access_token=creds.token,
            refresh_token=creds.refresh_token, 
            token_expiry=creds.expiry
        )
        session.add(new_conn)
        

    session.commit()
    
    # Redirect back to the frontend
    from fastapi.responses import RedirectResponse
    return RedirectResponse("http://localhost:5173/connections")
