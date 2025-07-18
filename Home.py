import streamlit as st
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

st.set_page_config(
    page_title="Synchrony Project Management",
    page_icon="📊",
    layout="wide"
)

# Check authentication
if not st.session_state.authenticated:
    st.switch_page("pages/1_🔐User Auth.py")

st.title(f"Welcome to Synchrony Project Management, {st.session_state.user['name']}!")

# Add logout button in sidebar
with st.sidebar:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.switch_page("pages/1_user_auth.py")

st.markdown("""
### 👈 Select a page from the sidebar to get started:

- **📊 Dashboard**: Overview of all projects and their status
- **📋 Project Board**: Manage projects and tasks
- **💬 Chatbot**: Get help and assistance
""")
