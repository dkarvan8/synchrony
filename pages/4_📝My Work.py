# my_work.py  ────────────────────────────────────────────────────────
"""
🧑‍💻  My Work  –  per-user checklist
• Reads every project in projects.json
• Filters tasks where task["assignee"] == logged-in user
• Shows parent tasks and nested subtasks (parent_id links)
• Lets you mark status  ⇆  'In Progress' ↔ 'Complete'
"""

from __future__ import annotations
import streamlit as st
from datetime import date
from collections import defaultdict

# project helpers
from utils.backend_manager import (
    load_data,                              # returns {"projects":[…]}
    update_task_status                      # (project_id, task_id, status)
)

# ─────────────────────────────  get logged-in username
if not st.session_state.get("authenticated"):
    st.error("🔒 Please log in from the *User Auth* page first.")
    st.stop()

username = str(st.session_state.user.get("name", "guest")).strip().lower()


# ─────────────────────────────  page config & nav
# st.set_page_config(page_title="My Work", page_icon="🧑‍💻", layout="wide")
# st.sidebar.page_link("Home.py",                       label="🏠 Home")
# st.sidebar.page_link("pages/2_dashboard.py",          label="📊 Dashboard")
# st.sidebar.page_link("pages/3_projectboard.py",       label="📋 Project Board")
# st.sidebar.page_link("pages/4_my_work.py",            label="🧑‍💻 My Work")

# st.title(f"🧑‍💻 Tasks for **{username}**")

# ─────────────────────────────  pull & bucket tasks
data = load_data()
user_tasks      = []                     # all tasks assigned to me
subtask_lookup  = defaultdict(list)      # parent_id → list[subtask]

for project in data["projects"]:
    for t in project["tasks"]:
        if t["assignee"].strip().lower() == username:
            t["_project_id"] = project["id"]     # remember origin project
            user_tasks.append(t)

            # bucket subtasks by parent
            if t.get("parent_id"):
                subtask_lookup[t["parent_id"]].append(t)

# split parents / standalone vs real subtasks
parent_tasks = [t for t in user_tasks if not t.get("parent_id")]

if not parent_tasks and not subtask_lookup:
    st.info("🎉 Nothing assigned to you yet.")
    st.stop()

# ─────────────────────────────  progress helper
def completion_ratio() -> float:
    total = len(user_tasks)
    done  = sum(1 for t in user_tasks if t["status"] == "Complete")
    return done / total if total else 0.0

st.progress(completion_ratio(), text="Overall completion")

st.divider()

# ─────────────────────────────  render checklist
STATUS_CYCLE = {                     # click-to-toggle order
    "To Do": "In Progress",
    "In Progress": "Complete",
    "Complete": "In Progress",       # allow undo
}

def toggle_status(proj_id: str, task_id: str, cur_status: str):
    new_status = STATUS_CYCLE.get(cur_status, "In Progress")
    update_task_status(proj_id, task_id, new_status)
    st.rerun() if hasattr(st, "experimental_rerun") else st.rerun()

for task in sorted(
        parent_tasks,
        key=lambda t: (
            {"High": 0, "Med": 1, "Low": 2}.get(t["priority"], 3),
            t["deadline"],
        )):
    proj_id = task["_project_id"]
    tid     = task["id"]
    subtasks = subtask_lookup.get(tid, [])

    header = (
        f"{'✅ ' if task['status']=='Complete' else ''}"
        f"{task['title']} • 🗓 {task['deadline']} • {task['priority']}"
    )
    with st.expander(header, expanded=False):
        # Top-level status toggle
        st.markdown("**Status**")
        st.button(
            task["status"],
            key=f"toggle_{tid}",
            help="Click to advance status",
            on_click=toggle_status,
            args=(proj_id, tid, task["status"]),
        )

        # Description
        if task["category"] or task["status"] != "To Do":
            st.caption(f"Category • {task['category']}")
        if task["deadline"]:
            overdue = date.fromisoformat(task["deadline"]) < date.today()
            if overdue and task["status"] != "Complete":
                st.error("⚠ Past Deadline")
        if task["title"]:
            st.write(task.get("desc", "_No description_"))

        # --------  subtasks
        if subtasks:
            st.markdown("---")
            st.markdown("**Sub-tasks**")
            for sub in subtasks:
                st.button(
                    f"{'✅ ' if sub['status']=='Complete' else ''}{sub['title']}",
                    key=f"sub_{sub['id']}",
                    on_click=toggle_status,
                    args=(proj_id, sub["id"], sub["status"]),
                    help="Toggle completion",
                )

st.caption(
    "💾 All task data lives in **projects.json** and is shared across pages.  "
    "Your clicks immediately update the dashboard & project board."
)
