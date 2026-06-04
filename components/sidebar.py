import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("✍️ eSign Hub")
        st.markdown("---")
        
        st.markdown("### 👤 Etuk/Lawal")
        st.caption("Enterprise Admin")
        st.markdown("---")
        
        # Navigation
        pages = {
            "📊 Dashboard": "Dashboard",
            "📝 Create Workflow": "Create",
            "📋 Active Approvals": "Approvals",
            "📈 Analytics": "Analytics",
            "🔗 Integrations": "Integrations",
            "📑 Audit Trail": "Audit",
            "⚙️ Settings": "Settings"
        }
        
        for label, page in pages.items():
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        # Quick stats
        if 'workflows' in st.session_state:
            total = len(st.session_state.workflows)
            pending = len([w for w in st.session_state.workflows if w['status'] == 'Pending Approval'])
            
            st.metric("Total Workflows", total)
            st.metric("Pending", pending)
        
        st.markdown("---")
        st.caption("v1.0.0 | © 2024 Etuk/Lawal")
