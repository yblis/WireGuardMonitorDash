import streamlit as st
import time
from datetime import datetime
import plotly.graph_objects as go
from data_processor import VPNDataProcessor
from visualizations import (
    create_usage_graph,
    create_user_activity_heatmap,
    create_active_sessions_table
)
from utils import format_bytes

# Page configuration
st.set_page_config(
    page_title="WireGuard VPN Monitor",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = VPNDataProcessor()

# Header
st.title('🔒 WireGuard VPN Monitor')

# Sidebar controls
st.sidebar.header('Dashboard Controls')
refresh_interval = st.sidebar.slider('Refresh Interval (seconds)', 5, 60, 10)
log_path = st.sidebar.text_input('Log File Path', '/var/log/wireguard/wg0.log')

# Main dashboard layout
col1, col2, col3 = st.columns(3)

# Update data
data_processor = st.session_state.data_processor
data_processor.process_logs(log_path)
metrics = data_processor.get_usage_metrics()

# Metrics cards
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        "Active Users",
        metrics['active_users'],
        delta=None
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        "Total Download",
        format_bytes(metrics['bandwidth_usage']['download']),
        delta=None
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        "Total Upload",
        format_bytes(metrics['bandwidth_usage']['upload']),
        delta=None
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Network usage graph
st.subheader('Network Usage')
usage_data = data_processor.traffic_data
if not usage_data.empty:
    usage_graph = create_usage_graph(usage_data)
    st.plotly_chart(usage_graph, use_container_width=True)

# User activity heatmap
st.subheader('User Activity Patterns')
historical_data = data_processor.get_historical_data()
if not historical_data.empty:
    activity_heatmap = create_user_activity_heatmap(historical_data)
    st.plotly_chart(activity_heatmap, use_container_width=True)

# Active sessions table
st.subheader('Active Sessions')
active_sessions = data_processor.connection_data[
    data_processor.connection_data['timestamp'] >= datetime.now() - timedelta(minutes=5)
]
if not active_sessions.empty:
    sessions_table = create_active_sessions_table(active_sessions)
    st.plotly_chart(sessions_table, use_container_width=True)

# Auto-refresh
time.sleep(refresh_interval)
st.experimental_rerun()
