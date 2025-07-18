import streamlit as st
import json
import os
from pathlib import Path

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

USER_DATA_FILE = str(Path(__file__).parent.parent / "users.json")

def init_user_file():
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w") as f:
            json.dump({"users": []}, f)

def load_users():
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)["users"]

def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump({"users": users}, f, indent=2)

def register_user(name, email, password):
    users = load_users()
    if any(user["email"] == email for user in users):
        return False, "Email already exists."
    new_user = {
        "name": name,
        "email": email,
        "password": password
    }
    users.append(new_user)
    save_users(users)
    return True, "Registration successful!"

def login_user(email, password):
    users = load_users()
    for user in users:
        if user["email"] == email and user["password"] == password:
            return True, user
    return False, None

# Initialize the users.json file if it doesn't exist
init_user_file()

st.set_page_config(page_title="Login / Register", layout="wide")

# If already authenticated, redirect to home
if st.session_state.authenticated:
    st.switch_page("Home.py")

# Create two columns for login and registration
col1, col2 = st.columns(2)

with col1:
    st.header("🔐 Login")
    with st.form("login_form"):
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        login_submitted = st.form_submit_button("Login")
        
        if login_submitted:
            success, user = login_user(login_email, login_password)
            if success:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.success("Login successful!")
                st.switch_page("Home.py")
            else:
                st.error("Invalid email or password")

with col2:
    st.header("📝 Register")
    with st.form("register_form"):
        reg_name = st.text_input("Name", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_submitted = st.form_submit_button("Register")
        
        if reg_submitted:
            if not reg_name or not reg_email or not reg_password:
                st.error("Please fill in all fields")
            else:
                success, message = register_user(reg_name, reg_email, reg_password)
                if success:
                    st.success(message)
                    st.info("Please login with your new account")
                else:
                    st.error(message)

# Add some information about the application
st.markdown("""
---
### Welcome to Synchrony Project Management

This application helps teams manage their projects efficiently with features like:
- Project Dashboard
- Task Management
- Team Collaboration
- Project Analytics
""")
