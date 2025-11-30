# tools_google.py
from langchain.tools import tool
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload , MediaIoBaseDownload
import io
import datetime
import base64
from email.mime.text import MIMEText
import pypdf  
import docx  

# --- Global Credential Handling ---
_ACTIVE_CREDENTIALS = None

def set_user_credentials(creds):
    global _ACTIVE_CREDENTIALS
    _ACTIVE_CREDENTIALS = creds

def get_safe_creds():
    if _ACTIVE_CREDENTIALS is None:
        raise ValueError("Auth Error: Credentials not set.")
    return _ACTIVE_CREDENTIALS

def get_user_name():
    """Fetch the full name from the Google Profile of the CURRENT user."""
    try:
        creds = get_safe_creds()
        # Connect to Google's User Info API
        service = build('oauth2', 'v2', credentials=creds)
        user_info = service.userinfo().get().execute()
        
        # Return the user's real name, or "AI Assistant" if hidden
        return user_info.get('name', 'AI Assistant') 
        
    except Exception as e:
        # If API fails (e.g. internet issue), fall back to neutral name
        return "AI Assistant"

# --- Service Builders ---
def gmail_service():
    return build("gmail", "v1", credentials=get_safe_creds())

def calendar_service():
    return build("calendar", "v3", credentials=get_safe_creds())

def drive_service():
    return build("drive", "v3", credentials=get_safe_creds())

# ==========================
# 📅 CALENDAR TOOLS
# ==========================

@tool
def get_upcoming_events(n: int = 10, year: int = None):
    """
    Get calendar events.
    Args:
        n: Number of events to retrieve (default 10).
        year: (Optional) A specific 4-digit year (e.g., 2026) to list events for.
              If not provided, lists upcoming events starting from strictly right now.
    """
    service = calendar_service()
    
    if year:
        # Search range: Jan 1 to Dec 31 of the specified year
        time_min = f"{year}-01-01T00:00:00Z"
        time_max = f"{year}-12-31T23:59:59Z"
    else:
        # Search range: Now onwards (standard upcoming)
        time_min = datetime.datetime.utcnow().isoformat() + 'Z'
        time_max = None

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        maxResults=n,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    if not events:
        period = f"the year {year}" if year else "the future"
        return f"No events found for {period}."

    result = []
    for event in events:
        # Handle full datetime (2025-01-01T10:00:00) vs all-day events (2025-01-01)
        start = event['start'].get('dateTime', event['start'].get('date'))
        result.append(f"Event: {event['summary']} | Time: {start} | ID: {event['id']}")
    
    return "\n".join(result)

@tool
def create_event(title: str, date: str, time: str):
    """Create a new event. Format: Date YYYY-MM-DD, Time HH:MM."""
    service = calendar_service()
    
    # --- FIX: CHANGE "UTC" TO YOUR TIMEZONE ---
    # Common Timezones: "Africa/Cairo", "Europe/London", "America/New_York", "Asia/Dubai"
    my_timezone = "Africa/Cairo"  
    
    event = {
        "summary": title,
        "start": {
            "dateTime": f"{date}T{time}:00", 
            "timeZone": my_timezone 
        },
        "end": {
            "dateTime": f"{date}T{time}:00", 
            "timeZone": my_timezone
        },
    }
    event = service.events().insert(calendarId="primary", body=event).execute()
    return f"Event created: {event.get('htmlLink')}"

@tool
def delete_event(event_id: str):
    """Delete a calendar event by its ID."""
    try:
        service = calendar_service()
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"Event {event_id} deleted successfully."
    except Exception as e:
        return f"Failed to delete event: {str(e)}"

# ==========================
# 📧 GMAIL TOOLS
# ==========================

@tool
def create_email_draft(to: str, subject: str, body: str):
    """Create a draft email (safer than sending directly)."""
    service = gmail_service()
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    draft_body = {'message': {'raw': raw}}
    draft = service.users().drafts().create(userId="me", body=draft_body).execute()
    return f"Draft created. ID: {draft['id']}"

@tool
def send_email(to: str, subject: str, body: str):
    """Send an email immediately."""
    service = gmail_service()
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return f"Email sent to {to}"

@tool
def search_emails(query: str):
    """Search for emails using Gmail queries (e.g., 'from:boss', 'subject:meeting')."""
    service = gmail_service()
    results = service.users().messages().list(userId="me", q=query, maxResults=5).execute()
    messages = results.get('messages', [])
    
    if not messages:
        return "No emails found matching that query."
    
    # Fetch details for the found emails
    output = []
    for msg in messages:
        # FIX: format must be 'metadata' (which includes the snippet), not 'snippet'
        m = service.users().messages().get(userId="me", id=msg['id'], format="metadata").execute()
        
        snippet = m.get('snippet', 'No snippet available')
        
        # improved formatting to show sender/subject if available in headers
        headers = m.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown)')
        
        output.append(f"From: {sender} | Subject: {subject} | Snippet: {snippet}")
    
    return "\n".join(output)

@tool
def read_latest_email(query: str = "label:INBOX"):
    """Read the latest email."""
    service = gmail_service()
    msgs = service.users().messages().list(userId="me", q=query, maxResults=1).execute()
    if "messages" not in msgs:
        return "Inbox is empty."
    msg_id = msgs["messages"][0]["id"]
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    snippet = msg.get("snippet", "")
    return f"Latest email: {snippet}"

# ==========================
# 📂 DRIVE TOOLS
# ==========================

# tools_google.py

# ... (keep your service functions and other tools) ...

@tool
def list_files(query: str = None, n: int = 30):
    """
    List files in 'My Drive' (Owned by me).
    Args:
        query: (Optional) Name to search for.
        n: Max results (default 30).
    """
    service = drive_service()
    
    q = "trashed = false and 'me' in owners"
    
    if query:
        clean_name = query.replace("'", "").replace('"', "")
        if "name =" in clean_name or "name contains" in clean_name:
            clean_name = clean_name.split()[-1]
        q += f" and name contains '{clean_name}'"

    results = service.files().list(
        pageSize=n, 
        fields="nextPageToken, files(id, name, mimeType, shortcutDetails)", 
        q=q,
        orderBy="folder,name"
    ).execute()
    
    items = results.get('files', [])

    if not items:
        return f"No files found matching '{query}'."
    
    # --- GROUPING LOGIC ---
    folders_list = []
    files_list = []

    for item in items:
        name = item.get('name')
        file_id = item.get('id')
        mime = item.get('mimeType')
        
        # We append the ID with a separator ":::" so the Agent sees it
        entry = f"{name} ::: {file_id}"

        # Shortcut logic
        is_shortcut = (mime == 'application/vnd.google-apps.shortcut')
        target_mime = ""
        if is_shortcut:
            target_mime = item.get('shortcutDetails', {}).get('targetMimeType', '')

        # Folder Logic
        if mime == 'application/vnd.google-apps.folder' or 'folder' in target_mime:
            folders_list.append(entry)
        else:
            files_list.append(entry)

    output = []
    if folders_list:
        output.append("--- FOLDERS ---")
        output.extend(folders_list)
        output.append("")
        
    if files_list:
        output.append("--- FILES ---")
        output.extend(files_list)
        
    return "\n".join(output)

@tool
def find_file(name: str):
    """
    Check if a specific file exists.
    Args:
        name: The keyword to search for (e.g. 'Project A').
    Returns:
        The exact full name(s) if found, or 'The file does not exist'.
    """
    service = drive_service()
    
    # Sanitize
    clean_name = name.replace("'", "").replace('"', "")
    if "name =" in clean_name:
        clean_name = clean_name.split()[-1]

    # Search query
    q = f"trashed = false and 'me' in owners and name contains '{clean_name}'"

    results = service.files().list(
        pageSize=10, 
        fields="files(name)", 
        q=q
    ).execute()
    
    items = results.get('files', [])

    if not items:
        return "The file does not exist."
    
    # Return the exact full names found
    found_names = [item['name'] for item in items]
    return "Found:\n" + "\n".join(found_names)

@tool
def read_file_content(file_id: str):
    """
    Read the content of a file. Supports Google Docs, Text, PDF, and Word (.docx).
    Args:
        file_id: The Google Drive file ID.
    """
    service = drive_service()
    try:
        # 1. Get file metadata to check type
        file_meta = service.files().get(fileId=file_id).execute()
        mime_type = file_meta.get('mimeType')
        file_name = file_meta.get('name')
        
        content_bytes = None

        # 2. DOWNLOAD LOGIC
        if mime_type == 'application/vnd.google-apps.document':
            # Case A: Google Doc -> Export to plain text
            request = service.files().export_media(fileId=file_id, mimeType='text/plain')
            content_bytes = request.execute()
            # Google Docs export comes as bytes, usually utf-8
            return content_bytes.decode('utf-8')

        else:
            # Case B: Binary File (PDF, Word, Text) -> Download raw bytes
            request = service.files().get_media(fileId=file_id)
            content_bytes = request.execute()
            
            # Create a file-like object in memory
            file_stream = io.BytesIO(content_bytes)

            # 3. PARSING LOGIC based on type
            
            # --- PDF Handling ---
            if mime_type == 'application/pdf':
                try:
                    reader = pypdf.PdfReader(file_stream)
                    text = []
                    for page in reader.pages:
                        text.append(page.extract_text())
                    return f"--- Content of {file_name} (PDF) ---\n" + "\n".join(text)
                except Exception as e:
                    return f"Error parsing PDF: {e}"

            # --- Word (.docx) Handling ---
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                try:
                    doc = docx.Document(file_stream)
                    text = [para.text for para in doc.paragraphs]
                    return f"--- Content of {file_name} (Word) ---\n" + "\n".join(text)
                except Exception as e:
                    return f"Error parsing Word Doc: {e}"

            # --- Plain Text / Code Handling ---
            elif mime_type.startswith('text/') or mime_type == 'application/json':
                return content_bytes.decode('utf-8')

            else:
                return f"Error: Unsupported file type ({mime_type}). I can only read Google Docs, PDFs, Word, and Text files."

    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def drive_upload(file_name: str, content: str):
    """Upload a text file to Drive."""
    service = drive_service()
    metadata = {"name": file_name}
    media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain')
    file = service.files().create(body=metadata, media_body=media, fields="id").execute()
    return f"Uploaded '{file_name}' with ID: {file.get('id')}"