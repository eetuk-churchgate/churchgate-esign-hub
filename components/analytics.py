import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_analytics():
    st.title("📈 Approval Analytics")
    
    period = st.selectbox("Time Period", ["Last 7 days", "Last 30 days", "Last Quarter", "Year to Date"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Approval Trends")
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        trend_data = pd.DataFrame({
            'Date': dates,
            'Approved': [3, 5, 2, 8, 6, 4, 7, 9, 5, 3] * 3,
            'Pending': [1, 2, 3, 1, 2, 4, 2, 1, 3, 2] * 3,
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_data['Date'], y=trend_data['Approved'], mode='lines+markers', name='Approved', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=trend_data['Date'], y=trend_data['Pending'], mode='lines+markers', name='Pending', line=dict(color='orange')))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚡ Platform Performance")
        metrics = pd.DataFrame({
            'Platform': ['DocuSign', 'MS365', 'HelloSign', 'Google Sign'],
            'Avg Time (days)': [2.1, 1.8, 2.5, 2.3],
            'Completion (%)': [95, 92, 88, 90]
        })
        fig = px.bar(metrics, x='Platform', y='Avg Time (days)', color='Platform')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("🏢 Department Analysis")
    dept_data = pd.DataFrame({
        'Department': ['Legal', 'Finance', 'HR', 'Operations', 'Sales'],
        'Requests': [45, 38, 25, 52, 30],
        'Avg Time': [2.1, 3.2, 1.8, 2.5, 2.8]
    })
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(dept_data, x='Department', y='Requests', color='Department')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(dept_data, x='Avg Time', y='Requests', size='Requests', color='Department')
        st.plotly_chart(fig, use_container_width=True)
