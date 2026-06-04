import streamlit as st

def render_integrations():
    st.title("🔗 Platform Integrations")
    
    platforms = [
        {"name": "DocuSign", "icon": "📝", "connected": True},
        {"name": "Microsoft 365", "icon": "🔷", "connected": True},
        {"name": "HelloSign", "icon": "✍️", "connected": True},
        {"name": "Google Sign", "icon": "📱", "connected": False}
    ]
    
    for p in platforms:
        with st.expander(f"{p['icon']} {p['name']} - {'🟢 Connected' if p['connected'] else '⚪ Not Connected'}", expanded=not p['connected']):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if p['connected']:
                    st.success("Active and configured")
                    st.markdown("- Templates\n- Bulk Send\n- Audit Trail")
                else:
                    st.warning("Needs configuration")
            
            with col2:
                if p['connected']:
                    st.button("Disconnect", key=f"dis_{p['name']}")
                else:
                    api_key = st.text_input("API Key", type="password", key=f"key_{p['name']}")
                    if st.button("Connect", key=f"con_{p['name']}", type="primary"):
                        if api_key:
                            st.success(f"Connected to {p['name']}!")
                        else:
                            st.error("Enter API key")
