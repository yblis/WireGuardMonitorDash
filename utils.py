import re
from datetime import datetime, timedelta
import pandas as pd

def parse_wireguard_log(log_line):
    """Parse a WireGuard log line into structured data."""
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[([^\]]+)\]\s+(.+)'
    match = re.match(pattern, log_line)
    if match:
        timestamp, level, message = match.groups()
        return {
            'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
            'level': level,
            'message': message
        }
    return None

def calculate_bandwidth_usage(data):
    """Calculate total bandwidth usage from traffic data."""
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
    current_time = datetime.now()
    timeout = current_time - timedelta(minutes=timeout_minutes)
    return len(data[data['last_seen'] >= timeout]['user'].unique())
