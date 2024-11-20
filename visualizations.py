import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_usage_graph(data, timeframe='1h'):
    """Create an interactive network usage graph."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['bytes_received'],
        name='Download',
        line=dict(color='#00ff00', width=2),
        fill='tozeroy'
    ))
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['bytes_sent'],
        name='Upload',
        line=dict(color='#ff4b4b', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        title='Network Usage Over Time',
        xaxis_title='Time',
        yaxis_title='Bytes',
        showlegend=True
    )
    
    return fig

def create_user_activity_heatmap(data):
    """Create a heatmap showing user activity patterns."""
    activity_matrix = data.pivot_table(
        index=data['timestamp'].dt.hour,
        columns=data['timestamp'].dt.dayofweek,
        values='user',
        aggfunc='count'
    ).fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=activity_matrix.values,
        x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        y=list(range(24)),
        colorscale='Viridis'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title='User Activity Patterns',
        xaxis_title='Day of Week',
        yaxis_title='Hour of Day'
    )
    
    return fig

def create_active_sessions_table(data):
    """Create an interactive table of active sessions."""
    return go.Figure(data=[go.Table(
        header=dict(
            values=['User', 'Connected Since', 'Data Transferred'],
            fill_color='#1B1F27',
            align='left'
        ),
        cells=dict(
            values=[
                data['user'],
                data['timestamp'],
                data['bytes_total']
            ],
            fill_color='#262B36',
            align='left'
        )
    )])
