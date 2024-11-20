import pandas as pd
from datetime import datetime, timedelta
import re
from utils import parse_wireguard_log, calculate_bandwidth_usage

class VPNDataProcessor:
    def __init__(self):
        self.connection_data = pd.DataFrame(columns=['timestamp', 'user', 'event'])
        self.traffic_data = pd.DataFrame(columns=['timestamp', 'user', 'bytes_received', 'bytes_sent'])
        
    def process_logs(self, log_path):
        """Process WireGuard log file and update data frames."""
        raw_logs = []
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    parsed = parse_wireguard_log(line)
                    if parsed:
                        raw_logs.append(parsed)
        except FileNotFoundError:
            print(f"Log file not found: {log_path}")
            return
        except Exception as e:
            print(f"Error reading log file: {e}")
            return
        
        if raw_logs:
            # Split logs by type
            connection_logs = [log for log in raw_logs if log['type'] == 'connection']
            traffic_logs = [log for log in raw_logs if log['type'] == 'traffic']
            
            if connection_logs:
                self._process_connection_data(connection_logs)
            if traffic_logs:
                self._process_traffic_data(traffic_logs)
    
    def _process_connection_data(self, logs):
        """Extract connection events from log data."""
        if not logs:
            return
            
        new_connections = pd.DataFrame(logs)
        # Ensure required columns exist
        required_cols = ['timestamp', 'user', 'event']
        if not all(col in new_connections.columns for col in required_cols):
            print("Missing required columns in connection data")
            return
            
        self.connection_data = pd.concat([
            self.connection_data,
            new_connections[required_cols]
        ]).drop_duplicates()
    
    def _process_traffic_data(self, logs):
        """Extract traffic statistics from log data."""
        if not logs:
            return
            
        new_traffic = pd.DataFrame(logs)
        # Ensure required columns exist
        required_cols = ['timestamp', 'user', 'bytes_received', 'bytes_sent']
        if not all(col in new_traffic.columns for col in required_cols):
            print("Missing required columns in traffic data")
            return
            
        self.traffic_data = pd.concat([
            self.traffic_data,
            new_traffic[required_cols]
        ]).drop_duplicates()
    
    def get_usage_metrics(self):
        """Get current usage metrics."""
        active_users = 0
        if not self.connection_data.empty and 'timestamp' in self.connection_data.columns:
            current_time = datetime.now()
            timeout = current_time - timedelta(minutes=5)
            active_users = len(self.connection_data[
                self.connection_data['timestamp'] >= timeout
            ]['user'].unique())
        
        bandwidth_usage = calculate_bandwidth_usage(self.traffic_data)
        
        return {
            'active_users': active_users,
            'bandwidth_usage': bandwidth_usage,
            'total_connections': len(self.connection_data) if not self.connection_data.empty else 0
        }
    
    def get_historical_data(self, days=7):
        """Get historical connection data for the specified period."""
        if self.connection_data.empty or 'timestamp' not in self.connection_data.columns:
            return pd.DataFrame()
            
        cutoff = datetime.now() - timedelta(days=days)
        return self.connection_data[self.connection_data['timestamp'] >= cutoff]
