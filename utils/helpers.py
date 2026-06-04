from datetime import datetime, timedelta
import uuid
import streamlit as st

def generate_workflow_id():
    return f"WF-{uuid.uuid4().hex[:8].upper()}"

def format_date(date_string):
    return datetime.fromisoformat(date_string).strftime("%B %d, %Y")

def calculate_progress(signed, total):
    if total == 0:
        return 0
    return int((signed / total) * 100)

def add_notification(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    st.session_state.notifications.append({
        'message': message,
        'timestamp': timestamp
    })

def get_status_icon(status):
    icons = {
        'Draft': '📝',
        'Pending Approval': '🟡',
        'Approved': '✅',
        'Rejected': '❌',
        'Expired': '⏰'
    }
    return icons.get(status, '📄')
