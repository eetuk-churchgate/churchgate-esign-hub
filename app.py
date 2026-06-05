import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import hashlib
import time
import uuid

sys.path.append(str(Path(__file__).parent))
from database_setup import init_database
from database_helper import Database

if not os.path.exists('esign_hub.db'):
    init_database()

st.set_page_config(
    page_title="eSign Hub - Digital Approvals",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'db' not in st.session_state:
    st.session_state.db = Database()

db = st.session_state.db

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'
if 'workflow_created' not in st.session_state:
    st.session_state.workflow_created = False

if not st.session_state.authenticated:
    st.title("🔐 eSign Hub Login")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            if submitted:
                user = db.verify_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        st.markdown("---")
        st.info("Login Credentials:\n- Admin: etuk / password123\n- Approvers: jerome.das, partab.lalchandani, vinay.mahtani / password123")
else:
    user = st.session_state.user
    with st.sidebar:
        st.title("✍️ eSign Hub")
        st.markdown("---")
        st.markdown(f"### 👤 {user['full_name']}")
        st.caption(f"{user['department']} | {user['role'].title()}")
        st.markdown("---")
        pages = {
            "📊 Dashboard": "Dashboard",
            "📝 Create Workflow": "Create",
            "📋 My Approvals": "Approvals",
            "📈 Analytics": "Analytics",
            "🔗 Integrations": "Integrations",
            "📑 Audit Trail": "Audit",
            "➕ Add Team": "AddTeam",
            "🗑️ Clear Workflows": "ClearDup",
        }
        for label, page in pages.items():
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        st.markdown("---")
        workflows = db.get_workflows_by_user(user['id'], user['role'])
        pending = len([w for w in workflows if w['status'] == 'pending'])
        st.metric("My Workflows", len(workflows))
        st.metric("Pending", pending)
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    page = st.session_state.current_page
    
    if page == "Dashboard":
        st.title(f"📊 Welcome, {user['full_name']}!")
        stats = db.get_workflow_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Workflows", stats['total'])
        with col2:
            pending_count = stats['status_counts'].get('pending', 0)
            st.metric("Pending", pending_count)
        with col3:
            st.metric("Avg. Approval Time", f"{stats['avg_approval_time']} days")
        with col4:
            platforms_connected = sum(1 for v in stats['platform_counts'].values() if v > 0)
            st.metric("Active Platforms", platforms_connected)
        st.markdown("---")
        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.subheader("🔄 Your Workflows")
            if workflows:
                workflow_data = []
                for wf in workflows[:10]:
                    signed_count = len([a for a in wf['approvers'] if a['status'] == 'signed'])
                    total_approvers = len(wf['approvers'])
                    progress = int((signed_count / total_approvers) * 100) if total_approvers > 0 else 0
                    workflow_data.append({
                        'ID': wf['id'],
                        'Title': wf['title'],
                        'Platform': wf['platform'],
                        'Status': wf['status'].title(),
                        'Progress': f"{progress}%",
                        'Created': wf['created_at'][:10]
                    })
                df = pd.DataFrame(workflow_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No workflows yet. Create your first workflow!")
        with col_right:
            st.subheader("📈 Platform Usage")
            if stats['platform_counts']:
                fig = px.pie(values=list(stats['platform_counts'].values()), names=list(stats['platform_counts'].keys()), title="Workflows by Platform")
                st.plotly_chart(fig, use_container_width=True)
        if st.button("🚀 Create New Workflow", type="primary", use_container_width=True):
            st.session_state.current_page = "Create"
            st.rerun()
    
    elif page == "Create":
        st.title("📝 Create New Workflow")
        all_users = db.get_all_users()
        user_options = {u['full_name']: u['id'] for u in all_users if u['id'] != user['id']}
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Workflow Title*", key="wf_title")
            description = st.text_area("Description*", key="wf_desc")
            platform = st.selectbox("Platform*", ["DocuSign", "HelloSign", "Microsoft 365", "Google Sign"], key="wf_platform")
            priority = st.select_slider("Priority", ["Low", "Medium", "High", "Critical"], key="wf_priority")
        with col2:
            approvers = st.multiselect("Select Approvers*", list(user_options.keys()), key="wf_approvers")
            expiration = st.number_input("Expiration (days)", 1, 90, 30, key="wf_expiration")
            uploaded_file = st.file_uploader("Upload Document*", type=['pdf', 'doc', 'docx'], key="wf_file")
        if st.button("🚀 Create Workflow", type="primary", use_container_width=True, disabled=st.session_state.workflow_created):
            if not title:
                st.error("Please enter Workflow Title")
            elif not description:
                st.error("Please enter Description")
            elif not approvers:
                st.error("Please select at least one Approver")
            elif not uploaded_file:
                st.error("Please upload a document")
            else:
                upload_dir = "uploads"
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}")
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                approver_ids = [user_options[name] for name in approvers]
                workflow_id = db.create_workflow_with_doc(title, description, platform, user['id'], approver_ids, file_path, expiration)
                if platform == "DocuSign":
                    from utils.helpers import send_docusign_envelope
                    recipients = []
                    for approver_id in approver_ids:
                        approver_data = db.get_user_by_id(approver_id)
                        recipients.append({'email': approver_data['email'], 'name': approver_data['full_name']})
                    success, result = send_docusign_envelope(file_path, recipients, title)
                    if success:
                        st.success(f"✅ Document sent to DocuSign! {result}")
                        st.info("📧 Approver will receive an email from DocuSign.")
                    else:
                        st.warning(f"⚠️ DocuSign: {result}")
                for approver_id in approver_ids:
                    db.add_notification(approver_id, f"New workflow requires your approval: {title}", 'approval_required')
                st.session_state.workflow_created = True
                st.success(f"✅ Workflow created! ID: {workflow_id}")
                st.balloons()
                time.sleep(2)
                st.session_state.workflow_created = False
                st.rerun()
    
    elif page == "Approvals":
        st.title("📋 My Approvals")
        tab1, tab2 = st.tabs(["Pending My Approval", "My Initiated Workflows"])
        with tab1:
            pending_approvals = [w for w in workflows if any(a['user_id'] == user['id'] and a['status'] == 'pending' for a in w['approvers'])]
            if pending_approvals:
                for wf in pending_approvals:
                    with st.expander(f"📄 {wf['title']} - {wf['platform']}", expanded=True):
                        st.write(f"**Description:** {wf['description']}")
                        st.write(f"**Initiator:** {wf['initiator_name']}")
                        st.write(f"**Created:** {wf['created_at'][:10]}")
                        if wf.get('document_path'):
                            st.markdown("**📎 Attached Document:**")
                            try:
                                with open(wf['document_path'], 'rb') as doc_file:
                                    st.download_button(label="📥 Download Document", data=doc_file, file_name=f"document_{wf['id']}.pdf", mime="application/pdf", key=f"doc_{wf['id']}")
                            except:
                                st.info("📎 Document available in DocuSign email")
                        if wf.get('platform') == 'DocuSign':
                            st.info("📧 Check your email for DocuSign signing link.")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Approve & Sign", key=f"approve_{wf['id']}"):
                                db.sign_workflow(wf['id'], user['id'], 'Approved')
                                st.success("Signed!")
                                st.rerun()
                        with col2:
                            if st.button("❌ Reject", key=f"reject_{wf['id']}"):
                                db.update_workflow_status(wf['id'], 'rejected', user['id'])
                                st.error("Rejected")
                                st.rerun()
            else:
                st.info("No pending approvals")
        with tab2:
            my_workflows = [w for w in workflows if w['initiator_id'] == user['id']]
            if my_workflows:
                for wf in my_workflows:
                    with st.expander(f"{wf['title']} - {wf['status'].title()}"):
                        signed = len([a for a in wf['approvers'] if a['status'] == 'signed'])
                        total = len(wf['approvers'])
                        st.progress(signed/total if total > 0 else 0, text=f"{signed}/{total} signatures")
                        for approver in wf['approvers']:
                            icon = "✅" if approver['status'] == 'signed' else "⏳"
                            st.write(f"{icon} {approver['full_name']}")
            else:
                st.info("No workflows yet")
    
    elif page == "Analytics":
        st.title("📈 Analytics")
        stats = db.get_workflow_stats()
        col1, col2 = st.columns(2)
        with col1:
            if stats['status_counts']:
                fig = px.pie(values=list(stats['status_counts'].values()), names=list(stats['status_counts'].keys()))
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            if stats['platform_counts']:
                fig = px.bar(x=list(stats['platform_counts'].keys()), y=list(stats['platform_counts'].values()))
                st.plotly_chart(fig, use_container_width=True)
    
    elif page == "Integrations":
        from components.integrations import render_integrations
        render_integrations()
    
    elif page == "AddTeam":
        st.title("➕ Add Team Members")
        st.subheader("Add Individual User")
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username", key="new_user")
            new_email = st.text_input("Email", key="new_email")
            new_fullname = st.text_input("Full Name", key="new_name")
        with col2:
            new_dept = st.text_input("Department", value="Executive", key="new_dept")
            new_role = st.selectbox("Role", ["approver", "admin", "manager"], key="new_role")
        if st.button("➕ Add This User", type="primary"):
            if new_username and new_email and new_fullname:
                cursor = db.conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO users (id, username, email, password_hash, full_name, department, role) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (f"USR-{uuid.uuid4().hex[:6].upper()}", new_username, new_email, hashlib.sha256('password123'.encode()).hexdigest(), new_fullname, new_dept, new_role))
                db.conn.commit()
                st.success(f"✅ {new_fullname} added! Login: {new_username} / password123")
                st.rerun()
            else:
                st.error("Please fill all fields")
        st.markdown("---")
        st.subheader("Add Executive Team")
        if st.button("Add Jerome, Partab, Vinay", type="secondary"):
            cursor = db.conn.cursor()
            users = [
                ('USR-003', 'jerome.das', 'Jeromedas@churchgate.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Jerome Das', 'Executive', 'approver'),
                ('USR-004', 'partab.lalchandani', 'partab@churchgate.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Partab Lalchandani', 'Executive', 'approver'),
                ('USR-005', 'vinay.mahtani', 'vbmahtani@churchgate.com', hashlib.sha256('password123'.encode()).hexdigest(), 'Vinay Mahtani', 'Executive', 'approver'),
            ]
            for user_data in users:
                cursor.execute('INSERT OR IGNORE INTO users (id, username, email, password_hash, full_name, department, role) VALUES (?, ?, ?, ?, ?, ?, ?)', user_data)
            db.conn.commit()
            st.success("✅ Team added!")
            st.rerun()
    
    elif page == "ClearDup":
        st.title("🗑️ Clear All Workflows")
        if st.button("Delete All", type="secondary"):
            cursor = db.conn.cursor()
            cursor.execute("DELETE FROM approvers")
            cursor.execute("DELETE FROM workflows")
            cursor.execute("DELETE FROM audit_trail")
            db.conn.commit()
            st.success("✅ Cleared!")
            st.rerun()
    
    elif page == "Audit":
        st.title("📑 Audit Trail")
        audit_entries = db.get_audit_trail()
        if audit_entries:
            audit_data = [{'Timestamp': e['timestamp'], 'User': e['full_name'], 'Action': e['action'].title(), 'Details': e['details']} for e in audit_entries]
            df = pd.DataFrame(audit_data)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False)
            st.download_button("📥 Export CSV", csv, f"audit_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No audit entries yet")

if st.session_state.get('authenticated'):
    st.sidebar.markdown("---")
    st.sidebar.caption("Paperless • Trackable • Efficient")