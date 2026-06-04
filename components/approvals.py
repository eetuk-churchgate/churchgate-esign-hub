import streamlit as st
from utils.helpers import get_status_icon

def render_approvals():
    st.title("📋 Active Approvals")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect("Status", ["Draft", "Pending Approval", "Approved", "Rejected"], default=["Pending Approval"])
    with col2:
        platform_filter = st.multiselect("Platform", ["DocuSign", "HelloSign", "MS365", "Google Sign"])
    with col3:
        search = st.text_input("🔍 Search", placeholder="Search...")
    
    st.markdown("---")
    
    for wf in st.session_state.workflows:
        if status_filter and wf['status'] not in status_filter:
            continue
        if platform_filter and wf['platform'] not in platform_filter:
            continue
        if search and search.lower() not in wf['title'].lower():
            continue
        
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                st.markdown(f"### {wf['title']}")
                st.caption(f"ID: {wf['id']} | Created: {wf['created']}")
                st.progress(wf['progress'] / 100, text=f"{wf['progress']}% Complete")
            
            with col2:
                st.markdown(f"**Platform:** {wf['platform']}")
                st.markdown(f"**Signatures:** {wf['signed']}/{wf['approvers']}")
                st.markdown(f"**Expires:** {wf['expires']}")
            
            with col3:
                st.markdown(f"{get_status_icon(wf['status'])} **{wf['status']}**")
            
            with col4:
                st.button("👁️ View", key=f"view_{wf['id']}")
                if wf['status'] == 'Pending Approval':
                    st.button("📧 Remind", key=f"remind_{wf['id']}")
            
            st.markdown("---")
