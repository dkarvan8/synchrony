# import streamlit as st
# import sys
# from pathlib import Path
# sys.path.append(str(Path(__file__).parent.parent))

# st.set_page_config(page_title="Project Assistant", layout="wide")
# st.title("💬 Project Assistant")

# st.markdown("""
# This is your project management assistant. You can:
# - Ask questions about your projects
# - Get help with task management
# - Request project status updates
# """)

# # Simple chat interface
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Chat input
# if prompt := st.chat_input("Ask me anything about your projects..."):
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
    
#     # Display user message
#     with st.chat_message("user"):
#         st.markdown(prompt)
    
#     # Add assistant response to chat history
#     response = "I'm still in development, but I'll be able to help you with your projects soon!"
#     st.session_state.messages.append({"role": "assistant", "content": response})
    
#     # Display assistant response
#     with st.chat_message("assistant"):
#         st.markdown(response)
import streamlit as st
import json
import os
from datetime import datetime
import re
import requests
from typing import List, Dict, Any
import sys
from pathlib import Path
if not st.session_state.get("authenticated"):
    st.error("🔒 Please log in from the User Auth page first.")
    st.stop()
# Add parent directory to path if needed
sys.path.append(str(Path(__file__).parent.parent))
import os

BASE_DIR = os.path.dirname(__file__)
TODO_FILE = os.path.join(BASE_DIR, 'todo_data.json')

CHAT_HISTORY_FILE = "chat_history.json"

class TodoChatbot:
    def __init__(self):
        self.todo_data = self.load_todo_data()
        self.chat_history = self.load_chat_history()
    
    def load_todo_data(self) -> Dict[str, Any]:
        """Load todo data from JSON file"""
        if os.path.exists(TODO_FILE):
            try:
                with open(TODO_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return self.create_sample_todo_data()
        else:
            return self.create_sample_todo_data()
    
    def create_sample_todo_data(self) -> Dict[str, Any]:
        """Create sample todo data for demonstration"""
        sample_data = {
            "tasks": [
                {
                    "id": 1,
                    "title": "Design homepage wireframes",
                    "description": "Create low-fidelity wireframes for the new homepage",
                    "priority": "high",
                    "status": "in_progress",
                    "due_date": "2024-12-01",
                    "category": "design",
                    "estimated_hours": 8
                },
                {
                    "id": 2,
                    "title": "Review design system components",
                    "description": "Audit existing components and identify gaps",
                    "priority": "medium",
                    "status": "pending",
                    "due_date": "2024-12-03",
                    "category": "design_system",
                    "estimated_hours": 4
                },
                {
                    "id": 3,
                    "title": "Create user persona documentation",
                    "description": "Document primary user personas for the project",
                    "priority": "low",
                    "status": "completed",
                    "due_date": "2024-11-28",
                    "category": "research",
                    "estimated_hours": 6
                }
            ],
            "categories": ["design", "research", "prototyping", "testing", "design_system"],
            "last_updated": datetime.now().isoformat()
        }
        
        # Save sample data
        with open(TODO_FILE, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        return sample_data
    
    def load_chat_history(self) -> List[Dict[str, str]]:
        """Load chat history from JSON file"""
        if os.path.exists(CHAT_HISTORY_FILE):
            try:
                with open(CHAT_HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_chat_history(self):
        """Save chat history to JSON file"""
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(self.chat_history, f, indent=2)
    
    def get_task_summary(self) -> str:
        """Generate a summary of current tasks"""
        tasks = self.todo_data.get("tasks", [])
        if not tasks:
            return "No tasks found."
        
        total_tasks = len(tasks)
        completed = len([t for t in tasks if t["status"] == "completed"])
        in_progress = len([t for t in tasks if t["status"] == "in_progress"])
        pending = len([t for t in tasks if t["status"] == "pending"])
        
        high_priority = len([t for t in tasks if t["priority"] == "high"])
        
        summary = f"""
**Task Summary:**
- Total tasks: {total_tasks}
- Completed: {completed}
- In Progress: {in_progress}
- Pending: {pending}
- High Priority: {high_priority}
        """
        return summary
    
    def get_productivity_context(self) -> str:
        """Generate context about tasks for the AI"""
        tasks = self.todo_data.get("tasks", [])
        context = "Current tasks:\n"
        
        for task in tasks:
            context += f"- {task['title']}: {task['status']}, Priority: {task['priority']}, Due: {task['due_date']}\n"
        
        return context
    
    def get_mistral_response(self, user_message: str) -> str:
        """Get response from Mistral AI API"""
        try:
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                return self.get_smart_response(user_message)  # Fallback to local responses
            
            # Prepare context for the AI
            context = self.get_productivity_context()
            
            system_prompt = f"""You are a helpful productivity assistant for frontend designers. 
            You help with task organization, prioritization, and provide productivity tips.
            
            Current task context:
            {context}
            
            You are friendly and conversational. Handle greetings and casual conversation naturally.
            Provide helpful, concise responses focused on:
            - Task prioritization
            - Time management
            - Design workflow optimization
            - Productivity tips specific to frontend design work
            - General conversation and support
            
            Keep responses friendly, practical, and under 300 words. Use emojis sparingly and appropriately."""
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return self.get_smart_response(user_message)  # Fallback to local responses
                
        except Exception as e:
            return self.get_smart_response(user_message)  # Fallback to local responses
    
    def get_smart_response(self, user_message: str) -> str:
        """Get intelligent response based on message analysis and task context"""
        message_lower = user_message.lower()
        
        # Handle greetings and casual conversation first
        if any(word in message_lower for word in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            return self.get_greeting_response()
        
        elif any(word in message_lower for word in ["thank", "thanks", "thank you"]):
            return self.get_thank_you_response()
        
        elif any(word in message_lower for word in ["bye", "goodbye", "see you", "later"]):
            return self.get_goodbye_response()
        
        elif any(word in message_lower for word in ["how are you", "how's it going", "what's up"]):
            return self.get_how_are_you_response()
        
        elif any(word in message_lower for word in ["good", "great", "awesome", "nice", "cool"]) and len(user_message.split()) <= 3:
            return self.get_positive_response()
        
        # Handle task-related queries
        elif any(word in message_lower for word in ["help", "what can you do", "commands"]):
            return self.get_help_response()
        
        elif any(word in message_lower for word in ["task", "tasks", "todo", "work"]):
            return self.get_task_analysis_response()
        
        elif any(word in message_lower for word in ["priority", "prioritize", "important", "urgent"]):
            return self.get_priority_response()
        
        elif any(word in message_lower for word in ["deadline", "due", "time", "schedule"]):
            return self.get_deadline_response()
        
        elif any(word in message_lower for word in ["productivity", "efficient", "tips", "advice"]):
            return self.get_productivity_response()
        
        elif any(word in message_lower for word in ["design", "wireframe", "prototype", "ui", "ux"]):
            return self.get_design_specific_response()
        
        elif any(word in message_lower for word in ["stress", "overwhelmed", "busy", "too much"]):
            return self.get_stress_management_response()
        
        elif any(word in message_lower for word in ["complete", "completed", "done", "finish"]):
            return self.get_completion_response()
        
        elif any(word in message_lower for word in ["start", "begin", "next", "what should i"]):
            return self.get_next_task_response()
        
        else:
            return self.get_contextual_response(user_message)
    
    def get_greeting_response(self) -> str:
        """Friendly greeting response"""
        import random
        greetings = [
            "Hi there! Ready to tackle your design tasks today?",
            "Hello! Hope you're having a productive day. How can I help you with your work?",
            "Hey! Good to see you. What's on your design agenda today?",
            "Hi! I'm here to help you stay organized and productive. What would you like to work on?",
            "Hello! Let's make today productive. How can I assist with your design tasks?"
        ]
        return random.choice(greetings)
    
    def get_thank_you_response(self) -> str:
        """Response to thank you messages"""
        import random
        responses = [
            "You're welcome! Happy to help you stay productive!",
            "My pleasure! That's what I'm here for. Anything else you need help with?",
            "Glad I could help! Keep up the great work on your projects!",
            "No problem at all! I'm always here when you need productivity support.",
            "You're very welcome! Let me know if you need any other assistance."
        ]
        return random.choice(responses)
    
    def get_goodbye_response(self) -> str:
        """Response to goodbye messages"""
        import random
        responses = [
            "Goodbye! Keep up the great work on your design projects!",
            "See you later! Hope you have a productive rest of your day!",
            "Bye! Remember, I'm here whenever you need help with your tasks.",
            "Take care! Come back anytime you need productivity tips or task help.",
            "Goodbye! Wishing you a creative and productive day ahead!"
        ]
        return random.choice(responses)
    
    def get_how_are_you_response(self) -> str:
        """Response to how are you questions"""
        return "I'm doing great, thanks for asking! I'm here and ready to help you with your design tasks and productivity. How are you doing today? Any projects you're excited about or challenges you're facing?"
    
    def get_positive_response(self) -> str:
        """Response to positive expressions"""
        import random
        responses = [
            "That's great to hear! Anything specific you'd like to work on today?",
            "Awesome! I love the positive energy. How can I help you channel that into your design work?",
            "Fantastic! With that attitude, you're going to get a lot done. What's first on your list?",
            "Wonderful! Ready to tackle some design challenges together?",
            "Nice! Let's keep that momentum going. What would you like to focus on?"
        ]
        return random.choice(responses)
    
    def get_help_response(self) -> str:
        return """
I'm your Project Assistant! Here's how I can help:

**Task Management:**
- "Show me my tasks" - Get current task overview
- "What should I work on next?" - Get prioritization suggestions
- "How are my deadlines?" - Review upcoming due dates

**Productivity Tips:**
- "Give me productivity tips" - Design-specific advice
- "I'm feeling overwhelmed" - Stress management strategies
- "How to organize my design work?" - Workflow optimization

**Design-Specific Help:**
- Ask about wireframing, prototyping, design systems
- Get advice on design workflows and best practices

**General Chat:**
- I'm here for casual conversation too!
- Ask me how I'm doing or just say hi

Just ask me anything about your tasks, design work, or let's just chat!
        """
    
    def get_task_analysis_response(self) -> str:
        tasks = self.todo_data.get("tasks", [])
        if not tasks:
            return "You don't have any tasks yet. Create some tasks in your to-do list and I'll help you manage them!"
        
        high_priority = [t for t in tasks if t["priority"] == "high"]
        overdue = [t for t in tasks if t["due_date"] < datetime.now().strftime("%Y-%m-%d") and t["status"] != "completed"]
        in_progress = [t for t in tasks if t["status"] == "in_progress"]
        
        response = f"**Task Analysis:**\n\n"
        response += f"You have {len(tasks)} total tasks.\n\n"
        
        if high_priority:
            response += f"**High Priority Tasks ({len(high_priority)}):**\n"
            for task in high_priority[:3]:  # Show first 3
                response += f"• {task['title']} - {task['status']}\n"
        
        if overdue:
            response += f"\n**Overdue Tasks ({len(overdue)}):**\n"
            for task in overdue[:3]:
                response += f"• {task['title']} - Due: {task['due_date']}\n"
        
        if in_progress:
            response += f"\n**In Progress ({len(in_progress)}):**\n"
            for task in in_progress[:3]:
                response += f"• {task['title']}\n"
        
        response += "\n**Suggestion:** Focus on high-priority and overdue tasks first!"
        return response
    
    def get_priority_response(self) -> str:
        tasks = self.todo_data.get("tasks", [])
        high_priority = [t for t in tasks if t["priority"] == "high" and t["status"] != "completed"]
        
        if not high_priority:
            return """
**Good news!** You don't have any high-priority tasks pending.

**Priority Framework for Designers:**
1. **User-blocking issues** (broken UI, accessibility problems)
2. **Deadline-driven work** (client presentations, sprint deliverables)
3. **Design system foundations** (components that unblock others)
4. **Research and planning** (important but not urgent)
5. **Polish and optimization** (nice-to-haves)
            """
        
        response = f"**High Priority Tasks Need Attention:**\n\n"
        for task in high_priority:
            response += f"• **{task['title']}** - Due: {task['due_date']}\n"
        
        response += "\n**Tip:** Tackle high-priority tasks when your energy is highest (usually mornings)!"
        return response
    
    def get_deadline_response(self) -> str:
        tasks = self.todo_data.get("tasks", [])
        upcoming = []
        
        for task in tasks:
            if task["status"] != "completed":
                try:
                    due_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
                    days_left = (due_date - datetime.now()).days
                    if days_left <= 7:  # Within a week
                        upcoming.append((task, days_left))
                except:
                    continue
        
        if not upcoming:
            return "**Great!** No urgent deadlines in the next week. Good time to work on important but not urgent tasks!"
        
        upcoming.sort(key=lambda x: x[1])  # Sort by days left
        
        response = "**Upcoming Deadlines:**\n\n"
        for task, days_left in upcoming:
            if days_left < 0:
                response += f"🔴 **{task['title']}** - OVERDUE by {abs(days_left)} days\n"
            elif days_left == 0:
                response += f"🟡 **{task['title']}** - Due TODAY\n"
            else:
                response += f"🟠 **{task['title']}** - Due in {days_left} days\n"
        
        response += "\n**Tip:** Use time-blocking to dedicate focused time to deadline-driven work!"
        return response
    
    def get_productivity_response(self) -> str:
        return """
**Frontend Designer Productivity Tips:**

**Time Management:**
• Use the Pomodoro Technique (25 min focused work + 5 min break)
• Block similar tasks together (all wireframing, then all prototyping)
• Schedule creative work during your peak energy hours

**Design Workflow:**
• Start with low-fidelity sketches before high-fidelity designs
• Create reusable components to speed up future work
• Use design systems and style guides consistently

**Process Optimization:**
• Get feedback early and often to avoid rework
• Use version control for design files
• Document design decisions for future reference

**Focus Strategies:**
• Eliminate distractions during deep work sessions
• Use music or ambient sounds to maintain focus
• Take regular breaks to prevent creative burnout
        """
    
    def get_design_specific_response(self) -> str:
        return """
**Design Work Best Practices:**

**Wireframing:**
• Start with paper sketches for rapid iteration
• Focus on layout and functionality, not visual details
• Test with real content, not lorem ipsum

**Prototyping:**
• Choose the right fidelity for your testing goals
• Include realistic interactions and transitions
• Test on actual devices when possible

**Design Systems:**
• Build components before full designs
• Document usage guidelines and variations
• Involve developers in the design system process

**Collaboration:**
• Share work-in-progress regularly
• Use design handoff tools for developer collaboration
• Create design specs that answer common questions
        """
    
    def get_stress_management_response(self) -> str:
        return """
**Feeling Overwhelmed? Here's How to Manage:**

**Immediate Relief:**
• Take 5 deep breaths and step away from your screen
• Write down everything on your mind (brain dump)
• Break large tasks into smaller, manageable pieces

**Organization Strategy:**
• Use the "2-minute rule" - if it takes less than 2 minutes, do it now
• Identify your 1-3 most important tasks for today
• Say no to non-essential requests when possible

**Energy Management:**
• Schedule demanding creative work during your peak hours
• Take regular breaks to prevent burnout
• Don't skip meals or hydration

**Long-term Solutions:**
• Set realistic expectations with stakeholders
• Build buffer time into project estimates
• Create templates and reusable components
        """
    
    def get_completion_response(self) -> str:
        tasks = self.todo_data.get("tasks", [])
        completed = [t for t in tasks if t["status"] == "completed"]
        
        if not completed:
            return "**Ready to mark something as complete?** Finishing tasks gives you momentum and dopamine boost!"
        
        response = f"**Awesome! You've completed {len(completed)} tasks!**\n\n"
        response += "**Recently Completed:**\n"
        for task in completed[-3:]:  # Show last 3 completed
            response += f"✅ {task['title']}\n"
        
        response += "\n**Tip:** Celebrate your wins! Take a moment to acknowledge your progress before moving to the next task."
        return response
    
    def get_next_task_response(self) -> str:
        tasks = self.todo_data.get("tasks", [])
        pending = [t for t in tasks if t["status"] == "pending"]
        
        if not pending:
            return "**All caught up!** No pending tasks. Time to either take a break or plan your next project!"
        
        # Sort by priority and due date
        def task_priority_score(task):
            priority_scores = {"high": 3, "medium": 2, "low": 1}
            priority_score = priority_scores.get(task["priority"], 1)
            
            try:
                due_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
                days_left = (due_date - datetime.now()).days
                urgency_score = max(0, 7 - days_left)  # More urgent = higher score
            except:
                urgency_score = 0
            
            return priority_score + urgency_score
        
        pending.sort(key=task_priority_score, reverse=True)
        
        next_task = pending[0]
        response = f"**I recommend starting with:**\n\n"
        response += f"**{next_task['title']}**\n"
        response += f"• Priority: {next_task['priority']}\n"
        response += f"• Due: {next_task['due_date']}\n"
        response += f"• Category: {next_task['category']}\n"
        
        if next_task.get('description'):
            response += f"• Description: {next_task['description']}\n"
        
        response += f"\n**Why this task?** It's your highest priority item with the nearest deadline!"
        return response
    
    def get_contextual_response(self, user_message: str) -> str:
        """Provide a helpful response based on context"""
        import random
        
        responses = [
            "That's interesting! Is there anything specific about your design work or tasks I can help you with?",
            "I hear you! How are your current projects going? Any challenges you're facing?",
            "Sounds good! What's keeping you busy on the design front these days?",
            "I'm here to help! Whether it's about your tasks, design work, or just to chat - what's on your mind?",
            "Got it! Feel free to ask me about your tasks, productivity tips, or anything else you'd like to discuss."
        ]
        
        return random.choice(responses)
    
    def get_predefined_response(self, message_type: str) -> str:
        """Get predefined responses for common queries"""
        responses = {
            "task_summary": self.get_task_summary(),
            "productivity_tips": """
**Productivity Tips for Frontend Designers:**

1. **Time Blocking**: Dedicate specific time blocks for different types of design work
2. **Design System First**: Establish components before diving into specific designs
3. **Regular Reviews**: Schedule weekly reviews of your design progress
4. **Prototype Early**: Create quick prototypes to validate ideas faster
5. **Feedback Loops**: Set up regular feedback sessions with stakeholders
            """,
            "prioritization": """
**Task Prioritization Framework:**

1. **Urgent & Important**: Do first (deadlines, critical bugs)
2. **Important, Not Urgent**: Schedule (design system work, planning)
3. **Urgent, Not Important**: Delegate if possible
4. **Neither**: Eliminate or postpone

Focus on impact and deadlines when deciding task order.
            """
        }
        return responses.get(message_type, "I'm here to help! What would you like to know about your tasks or design work?")

# Streamlit App Configuration
st.set_page_config(
    page_title="💬 Project Assistant",
    page_icon="💬",
    layout="wide"
)

# Initialize chatbot
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = TodoChatbot()

# Initialize chat history in session state
if 'messages' not in st.session_state:
    st.session_state.messages = st.session_state.chatbot.chat_history

# Main UI
st.title("💬 Project Assistant")
st.markdown("*Your AI-powered productivity companion for design tasks and project management*")

# Sidebar with quick actions
with st.sidebar:
    st.header("🚀 Quick Actions")
    
    if st.button("📊 Task Summary"):
        response = st.session_state.chatbot.get_predefined_response("task_summary")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    if st.button("💡 Productivity Tips"):
        response = st.session_state.chatbot.get_predefined_response("productivity_tips")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    if st.button("🎯 Prioritization Help"):
        response = st.session_state.chatbot.get_mistral_response("What task should I do first?")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    if st.button("🔄 Refresh Tasks"):
        st.session_state.chatbot.todo_data = st.session_state.chatbot.load_todo_data()
        st.success("Tasks refreshed!")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chatbot.chat_history = []
        st.session_state.chatbot.save_chat_history()
        st.rerun()

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about your tasks, productivity tips, or just say hi!"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response (Mistral AI with fallback)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chatbot.get_mistral_response(prompt)
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Save chat history
    st.session_state.chatbot.chat_history = st.session_state.messages
    st.session_state.chatbot.save_chat_history()