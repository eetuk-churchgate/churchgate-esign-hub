import streamlit as st
from datetime import datetime, timedelta
from utils.helpers import generate_workflow_id, add_notification

def render_create_workflow():
    st.title("📝 Create New Approval Workflow")
    
    with st.form("workflow_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Workflow Title*", placeholder="e.g., Contract Signature")
            description = st.text_area("Description*", placeholder="Describe the approval process...")
            platform = st.selectbox("E-Signature Platform*", ["DocuSign", "HelloSign", "Microsoft 365 Approvals", "Google Sign"])
            priority = st.select_slider("Priority", options=["Low", "Medium", "High", "Critical"], value="Medium")
        
        with col2:
            initiator = st.text_input("Initiator Email*", placeholder="your.email@company.com")
            approvers = st.text_area("Approver Emails* (one per line)", placeholder="approver1@company.com\napprover2@company.com")
            expiration = st.number_input("Expiration (days)", min_value=1, max_value=90, value=30)
            uploaded_file = st.file_uploader("Upload Document (Optional)", type=['pdf', 'doc', 'docx'])
        
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox("Require 2FA", value=True)
                st.checkbox("Sequential Signing")
            with col2:
                st.checkbox("Auto-reminders", value=True)
                st.selectbox("Reminder Frequency", ["Daily", "Every 3 days", "Weekly"])
        
        submitted = st.form_submit_button("🚀 Create Workflow", type="primary", use_container_width=True)
        
        if submitted:
            if title and description and approvers and initiator:
                approver_list = [e.strip() for e in approvers.split('\n') if e.strip()]
                if approver_list:
                    new_wf = {
                        'id': generate_workflow_id(),
                        'title': title,
                        'platform': platform,
                        'status': 'Pending Approval',
                        'approvers': len(approver_list),
                        'signed': 0,
                        'created': datetime.now().strftime('%Y-%m-%d'),
                        'expires': (datetime.now() + timedelta(days=expiration)).strftime('%Y-%m-%d'),
                        'priority': priority,
                        'progress': 0,
                        'department': 'General'
                    }
                    st.session_state.workflows.append(new_wf)
                    add_notification(f"Workflow created: {title}")
                    st.success(f"✅ Workflow created! ID: {new_wf['id']}")
                else:
                    st.error("❌ Add at least one approver")
            else:
                st.error("❌ Fill in all required fields")
