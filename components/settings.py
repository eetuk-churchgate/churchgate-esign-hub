import streamlit as st

def render_settings():
    st.title("⚙️ Settings")
    
    tabs = st.tabs(["General", "Notifications", "Security"])
    
    with tabs[0]:
        st.subheader("General Settings")
        st.text_input("Company Name", "Etuk/Lawal Corp")
        st.selectbox("Default Platform", ["DocuSign", "MS365", "HelloSign", "Google Sign"])
        st.number_input("Default Expiration (days)", 1, 90, 30)
        if st.button("Save General", type="primary"):
            st.success("✅ Saved!")
    
    with tabs[1]:
        st.subheader("Notifications")
        st.checkbox("Email", value=True)
        st.checkbox("In-app", value=True)
        st.checkbox("Slack")
        st.selectbox("Frequency", ["Daily", "Weekly"])
        if st.button("Save Notifications"):
            st.success("✅ Saved!")
    
    with tabs[2]:
        st.subheader("Security")
        st.checkbox("2FA", value=True)
        st.checkbox("Session Timeout", value=True)
        st.selectbox("Signature Level", ["Basic", "Enhanced", "Qualified"])
        if st.button("Update Security"):
            st.success("✅ Updated!")
