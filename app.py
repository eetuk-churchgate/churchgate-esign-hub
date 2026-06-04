import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Force database recreation on Streamlit Cloud
if os.path.exists('esign_hub.db'):
    os.remove('esign_hub.db')
    print("Old database removed - creating fresh one with new users")

sys.path.append(str(Path(__file__).parent))
from database_setup import init_database
from database_helper import Database

# Auto-create database if it doesn't exist
if not os.path.exists('esign_hub.db'):
    init_database()
# Page config
st.set_page_config(
    page_title="eSign Hub - Digital Approvals",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = Database()

db = st.session_state.db

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Login page
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
        st.info("Demo Credentials:\n- Admin: etuk / password123\n- Manager: lawal / password123")
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
                fig = px.pie(
                    values=list(stats['platform_counts'].values()),
                    names=list(stats['platform_counts'].keys()),
                    title="Workflows by Platform"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        if st.button("🚀 Create New Workflow", type="primary", use_container_width=True):
            st.session_state.current_page = "Create"
            st.rerun()
    
    elif page == "Create":
        st.title("📝 Create New Workflow")
        
        all_users = db.get_all_users()
        user_options = {u['full_name']: u['id'] for u in all_users if u['id'] != user['id']}
        
        with st.form("create_workflow"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Workflow Title*")
                description = st.text_area("Description*")
                platform = st.selectbox("Platform*", ["DocuSign", "HelloSign", "Microsoft 365", "Google Sign"])
                priority = st.select_slider("Priority", ["Low", "Medium", "High", "Critical"])
            
            with col2:
                approvers = st.multiselect("Select Approvers*", list(user_options.keys()))
                expiration = st.number_input("Expiration (days)", 1, 90, 30)
                uploaded_file = st.file_uploader("Upload Document", type=['pdf', 'doc', 'docx'])
            
            submitted = st.form_submit_button("Create Workflow", type="primary", use_container_width=True)
            
            if submitted:
                if title and description and approvers:
                    approver_ids = [user_options[name] for name in approvers]
                    workflow_id = db.create_workflow(title, description, platform, user['id'], approver_ids, expiration)
                    
                    for approver_id in approver_ids:
                        db.add_notification(approver_id, f"New workflow requires your approval: {title}", 'approval_required')
                    
                    st.success(f"✅ Workflow created! ID: {workflow_id}")
                    st.rerun()
                else:
                    st.error("Please fill all required fields")
    
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
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Approve & Sign", key=f"approve_{wf['id']}"):
                                db.sign_workflow(wf['id'], user['id'], 'Approved')
                                db.add_notification(wf['initiator_id'], f"{user['full_name']} signed {wf['title']}", 'workflow_update')
                                st.success("Document signed successfully!")
                                st.rerun()
                        with col2:
                            if st.button("❌ Reject", key=f"reject_{wf['id']}"):
                                db.update_workflow_status(wf['id'], 'rejected', user['id'])
                                db.add_notification(wf['initiator_id'], f"{user['full_name']} rejected {wf['title']}", 'workflow_update')
                                st.error("Workflow rejected")
                                st.rerun()
            else:
                st.info("No pending approvals for you!")
        
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
                            st.write(f"{icon} {approver['full_name']} - {approver['status']}")
            else:
                st.info("No workflows initiated by you yet")
    
    elif page == "Analytics":
        st.title("📈 Analytics")
        
        stats = db.get_workflow_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Workflow Status Distribution")
            if stats['status_counts']:
                fig = px.pie(values=list(stats['status_counts'].values()), names=list(stats['status_counts'].keys()))
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Platform Usage")
            if stats['platform_counts']:
                fig = px.bar(x=list(stats['platform_counts'].keys()), y=list(stats['platform_counts'].values()))
                st.plotly_chart(fig, use_container_width=True)
    
    elif page == "Integrations":
        from components.integrations import render_integrations
        render_integrations()
    
    elif page == "Audit":
        st.title("📑 Audit Trail")
        audit_entries = db.get_audit_trail()
        
        if audit_entries:
            audit_data = [{
                'Timestamp': entry['timestamp'],
                'User': entry['full_name'],
                'Action': entry['action'].title(),
                'Details': entry['details'],
                'Workflow': entry.get('workflow_title', entry['workflow_id'])
            } for entry in audit_entries]
            
            df = pd.DataFrame(audit_data)
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False)
            st.download_button("📥 Export Audit Log", csv, f"audit_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No audit entries yet")

if st.session_state.get('authenticated'):
    st.sidebar.markdown("---")
    st.sidebar.caption("Paperless • Trackable • Efficient")