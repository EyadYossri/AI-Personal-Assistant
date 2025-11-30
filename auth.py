import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json
import warnings
from google.auth.transport.requests import Request


# Redirect URI
REDIRECT_URI = "http://localhost:8501/oauth2callback"  # Local dev
# REDIRECT_URI = "https://<your-space>.hf.space/oauth2callback"  # HuggingFace

# OAuth scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

# Load client secrets from Streamlit secrets
def load_client_secrets():
    return {
        "web": {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }

# Create OAuth flow
def get_flow():
    return Flow.from_client_config(
        load_client_secrets(),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

# Get auth URL
def get_auth_url():
    flow = get_flow()
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",  # ensures refresh token is returned
        include_granted_scopes="true"
    )
    return auth_url


# Exchange code for credentials safely
def exchange_code(code):
    flow = get_flow()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        flow.fetch_token(code=code)
    creds = flow.credentials

    # Make sure we have a refresh token
    if not creds.refresh_token:
        st.warning("No refresh token received. Make sure 'access_type=offline' is set in your OAuth flow.")
    return creds


# Save credentials in session
def save_credentials(creds):
    st.session_state["creds"] = json.loads(creds.to_json())

# Load credentials from session
def get_credentials():
    if "creds" in st.session_state:
        creds = Credentials.from_authorized_user_info(st.session_state["creds"])
        # Force refresh if expired
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # from google.auth.transport.requests import Request
                st.session_state["creds"] = json.loads(creds.to_json())
            except Exception as e:
                st.error(f"Failed to refresh credentials: {e}")
                return None
        return creds
    return None

