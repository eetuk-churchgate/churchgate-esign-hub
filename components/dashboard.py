import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_dashboard():
    st.title("📊 Digital Approval Dashboard")
    
    st.markdown("""
    ### Paperless Approval System
    Manage all e-signatures and approvals from a single platform.
    """)
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Workflows", "24", "+5 this week")
    with col2:
        st.metric("Pending Approvals", "8", "⚠️ 2 overdue")
    with col3:
        st.metric("Avg. Approval Time", "2.1 days", "↓ 15%")
    with col4:
        st.metric("Platforms Active", "3/4", "All connected")
    
    st.markdown("---")
    
    # Recent workflows and platform usage
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🔄 Recent Workflows")
        
        if st.session_state.workflows:
            df = pd.DataFrame(st.session_state.workflows)
            st.dataframe(
                df[['id', 'title', 'platform', 'status', 'priority']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No workflows yet. Create your first workflow!")
    
    with col_right:
        st.subheader("📈 Platform Usage")
        
        fig = px.pie(
            values=[35, 30, 20, 15],
            names=['DocuSign', 'MS365', 'HelloSign', 'Google Sign'],
            title="Platform Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Quick actions
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🚀 New Workflow", use_container_width=True):
            st.session_state.current_page = "Create"
            st.rerun()
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = "Analytics"
            st.rerun()
    with col3:
        if st.button("🔗 Integrations", use_container_width=True):
            st.session_state.current_page = "Integrations"
            st.rerun()
    with col4:
        if st.button("📑 Audit Trail", use_container_width=True):
            st.session_state.current_page = "Audit"
            st.rerun()
    
    # Features
    st.markdown("---")
    st.subheader("🎯 Key Features")
    
    feat1, feat2, feat3 = st.columns(3)
    
    with feat1:
        st.markdown("""
        ### 🔗 Multi-Platform
        - DocuSign Integration
        - Microsoft 365 Approvals
        - HelloSign Support
        - Google Sign Ready
        """)
    
    with feat2:
        st.markdown("""
        ### 📊 Smart Analytics
        - Real-time Tracking
        - Bottleneck Detection
        - Platform Comparison
        """)
    
    with feat3:
        st.markdown("""
        ### 🔒 Enterprise Security
        - 2FA Authentication
        - Complete Audit Trail
        - Encrypted Storage
        """)
