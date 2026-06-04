import streamlit as st
import pandas as pd
from datetime import datetime

def render_audit():
    st.title("📑 Audit Trail")
    
    col1, col2 = st.columns(2)
    with col1:
        st.date_input("Date Range")
    with col2:
        st.multiselect("Action Type", ["Created", "Modified", "Signed", "Approved"])
    
    st.markdown("---")
    
    entries = [
        {"timestamp": "2024-01-15 14:30", "user": "etuk@company.com", "action": "Signed", "workflow": "WF-001"},
        {"timestamp": "2024-01-15 14:15", "user": "lawal@company.com", "action": "Approved", "workflow": "WF-002"},
        {"timestamp": "2024-01-15 13:45", "user": "admin@company.com", "action": "Created", "workflow": "WF-003"}
    ]
    
    df = pd.DataFrame(entries)
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False)
    st.download_button("📥 Export CSV", csv, f"audit_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
