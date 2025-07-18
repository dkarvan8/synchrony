# main_dashboard.py (Streamlit Project Dashboard)
import streamlit as st
from utils.backend_manager import load_data
from collections import Counter

if not st.session_state.get("authenticated"):
    st.error("🔒 Please log in from the User Auth page first.")
    st.stop()

st.set_page_config(page_title="Main Dashboard", layout="wide")
st.title("📊 Main Project Dashboard")

# Load data
data = load_data()
project_titles = {p['title']: p['id'] for p in data['projects']}

if not project_titles:
    st.warning("⚠️ No projects available yet. Please ask the Team Lead to create one in the Project Board.")
    st.stop()  # Stop further execution
else:
    selected_project_title = st.selectbox("Select Project", list(project_titles.keys()))
    selected_project_id = project_titles.get(selected_project_title)

    if selected_project_id is None:
        st.error("Something went wrong. Please refresh.")
        st.stop()

    project = next(p for p in data['projects'] if p['id'] == selected_project_id)


# Project Info
st.header("📁 Project Information")
st.markdown(f"**Title:** {project['title']}")
st.markdown(f"**Description:** {project['description']}")

# Team Overview
st.header("👥 Team Overview")
st.markdown(f"**Team Lead:** {project['team_lead']}")
st.markdown("**Team Members:**")
st.markdown(", ".join(project['members']))

# Progress Calculation
status_counts = Counter(task['status'] for task in project['tasks'])
total_tasks = sum(status_counts.values())
completed_tasks = status_counts.get("Complete", 0)
overall_progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

st.header("📈 Overall Progress")
st.progress(overall_progress / 100)
st.metric("Project Completion", f"{overall_progress:.2f}%")

# Individual Progress
st.header("📌 Individual Progress")
for member in project['members']:
    member_tasks = [t for t in project['tasks'] if t['assignee'] == member]
    if member_tasks:
        done = len([t for t in member_tasks if t['status'] == "Complete"])
        perc = (done / len(member_tasks)) * 100
        st.write(f"**{member}**")
        st.progress(perc / 100)
        st.caption(f"{done}/{len(member_tasks)} tasks complete")
    else:
        st.write(f"**{member}** - No tasks assigned yet")
