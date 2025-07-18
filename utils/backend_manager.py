# backend_project_manager.py
import streamlit as st
import json
import uuid
from datetime import datetime

# Load or initialize data
def load_data():
    try:
        with open("projects.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"projects": []}

def save_data(data):
    with open("projects.json", "w") as f:
        json.dump(data, f, indent=2)

# Add new project
def create_project(title, description, team_lead, members):
    data = load_data()
    project = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "team_lead": team_lead,
        "members": members,
        "tasks": []
    }
    data["projects"].append(project)
    save_data(data)

# Add task to project
def add_task(project_id, title, assignee, status, deadline, priority, category, parent_id=None):
    data = load_data()
    for project in data["projects"]:
        if project["id"] == project_id:
            task = {
                "id": str(uuid.uuid4()),
                "title": title,
                "assignee": assignee,
                "status": status,
                "deadline": deadline,
                "priority": priority,
                "category": category,
                "parent_id": parent_id,
                "created": str(datetime.now())
            }
            project["tasks"].append(task)
            break
    save_data(data)

# Update task status
def update_task_status(project_id, task_id, status):
    data = load_data()
    for project in data["projects"]:
        if project["id"] == project_id:
            for task in project["tasks"]:
                if task["id"] == task_id:
                    task["status"] = status
                    break
    save_data(data)

# Get project by ID
def get_project(project_id):
    data = load_data()
    for project in data["projects"]:
        if project["id"] == project_id:
            return project
    return None
