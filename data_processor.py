import pandas as pd
from datetime import datetime, timedelta
from utils import parse_wireguard_log, calculate_bandwidth_usage

class VPNDataProcessor:
    def __init__(self):
        self.connection_data = pd.DataFrame()
        self.traffic_data = pd.DataFrame()
        
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
            return
        
        if raw_logs:
            new_data = pd.DataFrame(raw_logs)
            self._process_connection_data(new_data)
            self._process_traffic_data(new_data)
    
    def _process_connection_data(self, data):
        """Extract connection events from log data."""
        connections = data[data['message'].str.contains('connected|disconnected', na=False)]
        self.connection_data = pd.concat([
            self.connection_data,
            connections
        ]).drop_duplicates()
    
    def _process_traffic_data(self, data):
        """Extract traffic statistics from log data."""
        traffic = data[data['message'].str.contains('transfer:', na=False)]
        
        def extract_traffic_stats(message):
            received = sent = 0
            if 'received' in message:
                received = int(re.search(r'received (\d+)', message).group(1))
            if 'sent' in message:
                sent = int(re.search(r'sent (\d+)', message).group(1))
            return pd.Series({'bytes_received': received, 'bytes_sent': sent})
        
        if not traffic.empty:
            traffic_stats = traffic['message'].apply(extract_traffic_stats)
            traffic = pd.concat([traffic, traffic_stats], axis=1)
            self.traffic_data = pd.concat([self.traffic_data, traffic_stats])
    
    def get_usage_metrics(self):
        """Get current usage metrics."""
        return {
            'active_users': len(self.connection_data[
                self.connection_data['timestamp'] >= datetime.now() - timedelta(minutes=5)
            ]),
            'bandwidth_usage': calculate_bandwidth_usage(self.traffic_data),
            'total_connections': len(self.connection_data)
        }
    
    def get_historical_data(self, days=7):
        """Get historical connection data for the specified period."""
        cutoff = datetime.now() - timedelta(days=days)
        return self.connection_data[self.connection_data['timestamp'] >= cutoff]
