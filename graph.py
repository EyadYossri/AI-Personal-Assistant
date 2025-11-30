import streamlit as st
import datetime
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage  # <--- NEW IMPORT

# Import your tools
from auth import get_credentials
from tools_google import (
    set_user_credentials,
    get_user_name,
    # Calendar
    get_upcoming_events, create_event, delete_event,
    # Gmail
    create_email_draft, send_email, search_emails, read_latest_email,
    # Drive
    list_files, read_file_content, drive_upload
)

# --- LLM SETUP ---
api_key = st.secrets["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    api_key=api_key,
    temperature=0.1
)

tools = [
    get_upcoming_events, create_event, delete_event,
    create_email_draft, send_email, search_emails, read_latest_email,
    list_files, read_file_content, drive_upload
]
agent = create_react_agent(llm, tools=tools)

def run_agent(user_input: str):
    # 1. Credentials Setup
    creds = get_credentials()
    if not creds:
        return "Authentication Error: Please refresh and log in again."
    set_user_credentials(creds)

    # 2. CALCULATE "NOW"
    # We explicitly tell the AI what day it is.
    now = datetime.datetime.now().strftime("%A, %Y-%m-%d %H:%M")
    user_name = get_user_name()
    
    # 3. INJECT SYSTEM PROMPT
    # We add a hidden "System Message" at the start of the conversation
    system_prompt = f"""
    System Time: {now}. 
    You are a helpful AI Personal Assistant.

    --- DATA HANDLING RULES ---
    1. **HIDDEN IDs**: The 'list_files' tool will return files in this format: "Filename ::: FileID".
       - You MUST use the "FileID" internally to read or delete files.
       - You MUST NOT show the "FileID" or the ":::" separator to the user in your final response.
       - Example: If tool returns "Budget.pdf ::: 12345", you simply say "I found 'Budget.pdf'".
    
    2. **SHOW THE DATA**: Copy the list of filenames into your response, but stripped of IDs.

    --- IMPORTANT RULES ---
    1. **SHOW THE DATA**: When a tool returns a list (files, emails, events), you MUST copy that list into your final response. Do NOT just say "I have listed them." 
    2. **BE VERBOSE**: If the user asks for a list, show the items one by one.
    
    --- EMAIL FORMATTING RULES ---
    When the user asks you to draft or send an email, you must format the 'body' input professionally. 
    NEVER just write the raw message. ALWAYS use this structure:
    
    Dear [Recipient Name],
    
    [The message content in clear paragraphs]
    
    Best regards,
    {user_name}
    ------------------------------
    
    For Calendar: When the user mentions 'tomorrow' or 'next Friday', use the System Time ({now}) to calculate the exact YYYY-MM-DD.
    """
    
    inputs = {
        "messages": [
            SystemMessage(content=system_prompt),
            ("user", user_input)
        ]
    }
    
    # 4. RUN AGENT
    result = agent.invoke(inputs)
    
    # 5. CLEAN OUTPUT (Fix for the [{'type': 'text'}] messy output)
    content = result["messages"][-1].content
    
    # If the model returns a list of blocks (JSON style), join them into text
    if isinstance(content, list):
        return " ".join([block['text'] for block in content if 'text' in block])
        
    return content