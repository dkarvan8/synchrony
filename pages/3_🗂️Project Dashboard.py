# project_board.py (Streamlit Project Management Interface)
import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.backend_manager import load_data, create_project, add_task, update_task_status
from datetime import datetime

if not st.session_state.get("authenticated"):
    st.error("🔒 Please log in from the User Auth page first.")
    st.stop()

st.set_page_config(page_title="Project Board", layout="wide")
st.title("📋 Project Board")

# ---- Project Creation Section ----
with st.expander("➕ Create New Project"):
    with st.form("create_project_form"):
        title = st.text_input("Project Title", placeholder="e.g. AI Assistant Dev")
        description = st.text_area("Project Description")
        team_lead = st.text_input("Team Lead", placeholder="e.g. Kruthik")
        members_input = st.text_area("Team Members (comma-separated)", placeholder="e.g. Alice, Bob, Charlie")

        submitted = st.form_submit_button("Create Project")
        if submitted:
            if not title or not team_lead or not members_input:
                st.error("Please fill in all required fields.")
            else:
                members = [m.strip() for m in members_input.split(",") if m.strip()]
                create_project(title, description, team_lead, members)
                st.success(f"✅ Project '{title}' created successfully!")
                st.rerun()

# ---- Load Projects ----
data = load_data()
project_titles = {p['title']: p['id'] for p in data['projects']}

if not project_titles:
    st.warning("⚠️ No projects available. Please create a project above.")
    st.stop()

selected_project_title = st.selectbox("Select Project", list(project_titles.keys()))
selected_project_id = project_titles[selected_project_title]
selected_project = next(p for p in data['projects'] if p['id'] == selected_project_id)

# ---- Task Creation Section ----
st.subheader(f"📌 Tasks for Project: {selected_project['title']}")

with st.expander("➕ Add Task"):
    task_title = st.text_input("Task Title")
    assignee = st.selectbox("Assignee", selected_project['members'])
    status = st.selectbox("Status", ["To Do", "In Progress", "Complete"])
    deadline = st.date_input("Deadline")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    category = st.text_input("Category (e.g., Design, Dev)")
    parent_options = ["None"] + [t['title'] for t in selected_project['tasks'] if not t.get('parent_id')]
    parent_id = st.selectbox("Is Subtask Of", parent_options)
    
    if st.button("Add Task"):
        parent_task = None if parent_id == "None" else next(t for t in selected_project['tasks'] if t['title'] == parent_id)
        add_task(selected_project_id, task_title, assignee, status, str(deadline), priority, category, parent_task['id'] if parent_task else None)
        st.success("✅ Task added successfully!")
        st.rerun()

# ---- Kanban Board ----
statuses = ["To Do", "In Progress", "Complete"]
st.markdown("### 🧾 Kanban Board")
cols = st.columns(3)

for i, status in enumerate(statuses):
    with cols[i]:
        st.markdown(f"#### {status}")
        for task in selected_project['tasks']:
            if task['status'] == status:
                indent = "↳ " if task.get('parent_id') else ""
                st.markdown(f"""
**{indent}{task['title']}**
- Assignee: {task['assignee']}
- Priority: {task['priority']}
- Deadline: {task['deadline']}
- Category: {task['category']}
""")
                new_status = st.selectbox(
                    "Change Status", statuses, index=statuses.index(status), key=task['id']
                )
                if new_status != task['status']:
                    update_task_status(selected_project_id, task['id'], new_status)
                    st.success(f"✅ Task '{task['title']}' updated!")
                    st.experimental_rerun()
