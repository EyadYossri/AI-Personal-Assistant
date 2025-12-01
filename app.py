import streamlit as st
from auth import get_auth_url, exchange_code, save_credentials, get_credentials
from utils import init_session
from graph import run_agent
import traceback

# --------------------- Error UI Helpers ---------------------
def show_error(message: str, details: str = None):
    st.error(f"❌ **Error:** {message}")
    with st.expander("Show error details"):
        if details:
            st.code(details)
        else:
            st.write("No further details.")

def error_banner(text):
    st.markdown(
        f"""
        <div style="
            background-color:#ffe6e6;
            color:#990000;
            padding:15px;
            border-radius:12px;
            border-left: 8px solid #ff4d4d;
            font-size:16px;
            margin-bottom:15px;
        ">
            ❌ {text}
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------- PAGE SETUP ---------------------
st.set_page_config(page_title="AI Personal Assistant", page_icon="🤖")
init_session()

st.markdown("""
<style>
    .block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI Personal Assistant")

creds = get_credentials()

# --------------------- LOGIN FLOW ---------------------
if not creds:
    st.info("Login with Google to continue.")
    auth_url = get_auth_url()

    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 20px;">
            <a href="{auth_url}" target="_self" style="
                display: flex;
                align-items: center;
                background-color: white;
                border: 1px solid #dadce0;
                border-radius: 20px;
                color: #3c4043;
                font-family: sans-serif;
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
                text-decoration: none;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.1s;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" 
                     style="width: 20px; height: 20px; margin-right: 12px;">
                Sign in with Google
            </a>
        </div>
    """, unsafe_allow_html=True)

    if "code" in st.query_params:
        code = st.query_params["code"]
        try:
            creds = exchange_code(code)
            save_credentials(creds)
            st.query_params.clear()
            st.rerun()

        except Exception as e:
            tb = traceback.format_exc()
            error_banner("Google login failed.")
            show_error(str(e), tb)

else:
    # --------------------- CHAT HISTORY ---------------------
    for role_icon, content in st.session_state["messages"]:
        role = "user" if role_icon == "🧑" else "assistant"
        avatar = "🧑‍💻" if role == "user" else "🤖"
        
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)

    # --------------------- PROMPT INPUT ---------------------
    if prompt := st.chat_input("Ask me anything (email, calendar, drive...)?"):

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        st.session_state["messages"].append(("🧑", prompt))

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Processing..."):
                try:
                    response = run_agent(prompt)
                    st.markdown(response)
                    st.session_state["messages"].append(("🤖", response))

                except Exception as e:
                    tb = traceback.format_exc()
                    error_banner("The assistant encountered an error.")
                    show_error("Something went wrong while processing your request.", tb)
