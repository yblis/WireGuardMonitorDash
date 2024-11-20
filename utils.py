import re
from datetime import datetime, timedelta
import pandas as pd

def parse_wireguard_log(log_line):
    """Parse a WireGuard log line into structured data."""
    # Try both log formats
    connection_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\w+)\s+(connected|disconnected)'
    traffic_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\w+)\s+SESSION_END\s+durée:(\d+)h(\d+)m\s+download:(\d+\.\d+)\s+MB\s+upload:(\d+\.\d+)\s+MB'
    
    conn_match = re.match(connection_pattern, log_line)
    traffic_match = re.match(traffic_pattern, log_line)
    
    if conn_match:
        timestamp_str, user, event = conn_match.groups()
        return {
            'timestamp': datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S'),
            'user': user,
            'event': event,
            'type': 'connection'
        }
    elif traffic_match:
        timestamp_str, user, hours, minutes, download_mb, upload_mb = traffic_match.groups()
        
        # Convert MB to bytes (1 MB = 1048576 bytes)
        bytes_received = int(float(download_mb) * 1048576)
        bytes_sent = int(float(upload_mb) * 1048576)
        
        return {
            'timestamp': datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S'),
            'user': user,
            'bytes_received': bytes_received,
            'bytes_sent': bytes_sent,
            'duration': timedelta(hours=int(hours), minutes=int(minutes)),
            'type': 'traffic'
        }
    return None

def calculate_bandwidth_usage(data):
    """Calculate total bandwidth usage from traffic data."""
    if data.empty:
        return {'download': 0, 'upload': 0}
    return {
        'download': data['bytes_received'].sum(),
        'upload': data['bytes_sent'].sum()
    }

def format_bytes(bytes_value):
    """Format bytes into human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.2f} TB"

def get_active_users(data, timeout_minutes=5):
    """Get count of active users based on recent activity."""
    if data.empty or 'timestamp' not in data.columns:
        return 0
    current_time = datetime.now()
    timeout = current_time - timedelta(minutes=timeout_minutes)
    active_data = data[data['timestamp'] >= timeout]
    return len(active_data['user'].unique()) if not active_data.empty else 0
