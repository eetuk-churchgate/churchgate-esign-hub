import streamlit as st
from database_helper import Database
from datetime import datetime
import json

def render_integrations():
    st.title("🔗 Platform Integrations")
    db = Database()
    
    st.markdown("""
    ### 🔑 Enter Your Real API Keys
    Once saved, these credentials work permanently for all future workflows.
    """)
    
    # DocuSign Integration
    with st.expander("📝 DocuSign", expanded=True):
        st.markdown("[Get Free API Key →](https://developers.docusign.com/)")
        
        col1, col2 = st.columns(2)
        with col1:
            docusign_key = st.text_input("Integration Key (API Key)", type="password", key="ds_key")
            docusign_account = st.text_input("Account ID", key="ds_account")
        with col2:
            docusign_secret = st.text_input("Secret Key", type="password", key="ds_secret")
            docusign_env = st.selectbox("Environment", ["demo.docusign.net", "docusign.net"], key="ds_env")
        
        if st.button("💾 Save & Connect DocuSign", type="primary", key="save_ds"):
            if docusign_key and docusign_account:
                config = {
                    'api_key': docusign_key,
                    'account_id': docusign_account,
                    'api_secret': docusign_secret,
                    'base_url': f'https://{docusign_env}',
                    'connected': True,
                    'connected_at': datetime.now().isoformat()
                }
                db.save_platform_config('DocuSign', config)
                st.success("✅ DocuSign connected PERMANENTLY!")
                st.rerun()
            else:
                st.error("Please provide Integration Key and Account ID")
    
    # HelloSign Integration
    with st.expander("✍️ HelloSign", expanded=False):
        st.markdown("[Get Free API Key →](https://www.hellosign.com/developers)")
        
        hellosign_key = st.text_input("HelloSign API Key", type="password", key="hs_key")
        
        if st.button("💾 Save & Connect HelloSign", type="primary", key="save_hs"):
            if hellosign_key:
                config = {
                    'api_key': hellosign_key,
                    'base_url': 'https://api.hellosign.com/v3',
                    'connected': True,
                    'connected_at': datetime.now().isoformat()
                }
                db.save_platform_config('HelloSign', config)
                st.success("✅ HelloSign connected!")
                st.rerun()
            else:
                st.error("Please provide API Key")
    
    # Microsoft 365 Integration
    with st.expander("🔷 Microsoft 365", expanded=False):
        st.markdown("[Get Free Developer Account →](https://developer.microsoft.com/microsoft-365/dev-program)")
        
        col1, col2 = st.columns(2)
        with col1:
            ms_client_id = st.text_input("Azure Client ID", key="ms_client")
            ms_tenant_id = st.text_input("Azure Tenant ID", key="ms_tenant")
        with col2:
            ms_client_secret = st.text_input("Azure Client Secret", type="password", key="ms_secret")
        
        if st.button("💾 Save & Connect Microsoft 365", type="primary", key="save_ms"):
            if ms_client_id and ms_tenant_id:
                config = {
                    'client_id': ms_client_id,
                    'tenant_id': ms_tenant_id,
                    'client_secret': ms_client_secret,
                    'connected': True,
                    'connected_at': datetime.now().isoformat()
                }
                db.save_platform_config('Microsoft 365', config)
                st.success("✅ Microsoft 365 connected!")
                st.rerun()
            else:
                st.error("Please provide Client ID and Tenant ID")
    
    # Google Sign Integration
    with st.expander("📱 Google Sign", expanded=False):
        st.markdown("[Get Free API Credentials →](https://console.cloud.google.com/)")
        
        col1, col2 = st.columns(2)
        with col1:
            google_client_id = st.text_input("Google Client ID", key="g_client")
        with col2:
            google_client_secret = st.text_input("Google Client Secret", type="password", key="g_secret")
        
        if st.button("💾 Save & Connect Google", type="primary", key="save_g"):
            if google_client_id:
                config = {
                    'client_id': google_client_id,
                    'client_secret': google_client_secret,
                    'connected': True,
                    'connected_at': datetime.now().isoformat()
                }
                db.save_platform_config('Google Sign', config)
                st.success("✅ Google Sign connected!")
                st.rerun()
            else:
                st.error("Please provide Client ID")
    
    # Show connection status from database
    st.markdown("---")
    st.subheader("📊 Current Integration Status")
    
    cursor = db.conn.cursor()
    cursor.execute('SELECT platform_name, is_connected, last_sync FROM platform_configs')
    platforms = cursor.fetchall()
    
    if platforms:
        cols = st.columns(len(platforms))
        for i, platform in enumerate(platforms):
            with cols[i]:
                if platform['is_connected']:
                    status = "🟢 Connected"
                else:
                    status = "⚪ Not Connected"
                last = platform['last_sync'][:10] if platform['last_sync'] else "Never"
                st.metric(platform['platform_name'], status, f"Since: {last}")
    else:
        st.info("No platforms configured yet. Add your API keys above.")