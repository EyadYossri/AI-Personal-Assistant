import streamlit as st
from auth import get_auth_url, exchange_code, save_credentials, get_credentials
from utils import init_session
from graph import run_agent

st.set_page_config(page_title="AI Personal Assistant", page_icon="🤖")
init_session()

# --- CSS to remove top spacing for a cleaner look ---
st.markdown("""
<style>
    .block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI Personal Assistant")

# --- OAuth Login Flow ---
creds = get_credentials()

if not creds:
    st.info("Login with Google to continue.")
    auth_url = get_auth_url()
    
    # Modern Google Login Button
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
            st.error(f"Error: {e}")

else:
    # --- 1. DISPLAY CHAT HISTORY FIRST ---
    # This loop renders existing messages in bubbles
    for role_icon, content in st.session_state["messages"]:
        # Map your icons to Streamlit roles
        role = "user" if role_icon == "🧑" else "assistant"
        avatar = "🧑‍💻" if role == "user" else "🤖"
        
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)

    # --- 2. CHAT INPUT (Pinned to Bottom) ---
    if prompt := st.chat_input("Ask me anything (email, calendar, drive...)?"):
        
        # Display User Message Immediately
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        # Add to history
        st.session_state["messages"].append(("🧑", prompt))

        # Generate and Display Assistant Response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Processing..."):
                response = run_agent(prompt)
                st.markdown(response)
        
        # Add to history
        st.session_state["messages"].append(("🤖", response))