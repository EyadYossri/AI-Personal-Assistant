<p align="center">
  <img src="Demo/demo.gif" alt="AI Assistant Demo" width="700" />
</p>

# 🤖 AI Personal Assistant

**AI Workspace Assistant** is a smart, context-aware personal agent built with **Streamlit** and **LangGraph**. It acts as a bridge between **Google's Gemini LLM** and your **Google Workspace**, allowing you to manage emails, files, and calendar events using natural language.

It automates daily tasks:
- 📅 **Calendar:** Smart scheduling with timezone awareness (e.g., "Meeting tomorrow at 4 PM").
- 📧 **Gmail:** Drafts professional emails, searches history, and summarizes threads.
- 📂 **Drive:** Searches for files (PDF, Docx, Text) and reads their content to answer questions.
- 🔐 **Secure:** Uses OAuth 2.0 so you log in with your own Google Account.

---

## 🧠 Key Features
- 🗣️ **Natural Language Control**: Uses `LangGraph` to reason and pick the right tools.
- 📁 **Smart Drive Search**: Distinguishes between folders, files, and shortcuts. Can read **PDFs** and **Word Docs**.
- ✉️ **Context-Aware Emailing**: Auto-generates professional email bodies with your real signature.
- 🛡️ **OAuth 2.0 Authentication**: Secure login via Google; no hardcoded user credentials.
- ⚡ **Real-Time Responses**: Powered by `gemini-flash-latest` for speed.

---

## 🧰 Tech Stack
| Component | Technology |
|------------|-------------|
| **Frontend** | Streamlit |
| **Agent Logic** | LangGraph & LangChain |
| **AI Model** | Google Gemini (via Vertex AI/Studio) |
| **Integrations** | Google Drive, Gmail, Calendar APIs |
| **Auth** | OAuth 2.0 (Google Auth Lib) |
| **Document Parsing** | PyMuPDF (PDF), python-docx (Word) |

---

## 🚀 How It Works
1. **Login** using your Google Account (OAuth).
2. The agent **authenticates** and connects to your specific Drive, Calendar, and Gmail.
3. You type a command, e.g., *"Find the file 'Project Specs', read it, and email a summary to John."*
4. The agent:
   - 🔍 Searches Drive for the file ID.
   - 📖 Downloads and extracts text from the PDF/Docx.
   - 🧠 Summarizes the content using Gemini.
   - 📝 Creates a draft email in your Gmail.

---

## ⚙️ Setup Instructions

### 1. Google Cloud Configuration
Before running the code, you must set up a project in [Google Cloud Console](https://console.cloud.google.com/):
1. Create a Project.
2. Enable APIs: **Gmail API**, **Google Drive API**, **Google Calendar API**.
3. Configure **OAuth Consent Screen** (Add your email as a "Test User").
4. Create **OAuth 2.0 Client IDs** (Desktop/Web) and download the credentials.

### 2. Local Installation
```bash
# Clone the repository
git clone [https://github.com/EyadYossri/AI-Personal-Assistant.git](https://github.com/EyadYossri/AI-Personal-Assistant.git)
cd AI-Personal-Assistant

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # (Windows)
# source .venv/bin/activate (Mac/Linux)

# Install dependencies
pip install -r requirements.txt
