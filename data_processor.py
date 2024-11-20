from datetime import datetime, timedelta
import pandas as pd
from flask import current_app
from models import db, Connection
from utils import parse_wireguard_log, calculate_bandwidth_usage, generate_mock_data

class VPNDataProcessor:
    # Add log file paths as class variables
    TRAFFIC_LOG = '/var/log/wireguard_traffic.txt'
    CONNECTIONS_LOG = '/var/log/wireguard_connections.log'
    
    def __init__(self):
        self.connection_data = pd.DataFrame(columns=['timestamp', 'user', 'event'])
        self.traffic_data = pd.DataFrame(columns=['timestamp', 'user', 'bytes_received', 'bytes_sent'])
        
        # Initialize with mock data in development
        with current_app.app_context():
            if not Connection.query.first():  # If no data exists
                self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize the database with mock data for development."""
        mock_data = generate_mock_data()
        for data in mock_data:
            connection = Connection(
                timestamp=data['timestamp'],
                user=data['user'],
                event_type=data['event_type'],
                bytes_received=data['bytes_received'],
                bytes_sent=data['bytes_sent']
            )
            db.session.add(connection)
        
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error saving mock data: {e}")
            db.session.rollback()
    
    def process_logs(self):
        """Process both WireGuard log files and update database."""
        # In development, just update some random active connections
        if current_app.debug:
            self._update_mock_data()
            return
            
        self._process_connection_logs()
        self._process_traffic_logs()
    
    def _update_mock_data(self):
        """Update mock data with some random new connections."""
        mock_data = generate_mock_data()
        current_time = datetime.now()
        
        # Only add very recent mock data
        recent_mock_data = [
            data for data in mock_data 
            if (current_time - data['timestamp']).total_seconds() < 300  # Last 5 minutes
        ]
        
        for data in recent_mock_data:
            connection = Connection(
                timestamp=data['timestamp'],
                user=data['user'],
                event_type=data['event_type'],
                bytes_received=data['bytes_received'],
                bytes_sent=data['bytes_sent']
            )
            db.session.add(connection)
        
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error updating mock data: {e}")
            db.session.rollback()
    
    def _process_connection_logs(self):
        """Process connection log file and store in database."""
        try:
            with open(self.CONNECTIONS_LOG, 'r') as f:
                for line in f:
                    parsed = parse_wireguard_log(line)
                    if parsed and parsed['type'] == 'connection':
                        self._process_connection_data([parsed])
        except FileNotFoundError:
            print(f"Connection log file not found: {self.CONNECTIONS_LOG}")
        except Exception as e:
            print(f"Error reading connection log file: {e}")

    def _process_traffic_logs(self):
        """Process traffic log file and store in database."""
        try:
            with open(self.TRAFFIC_LOG, 'r') as f:
                for line in f:
                    parsed = parse_wireguard_log(line)
                    if parsed and parsed['type'] == 'traffic':
                        self._process_traffic_data([parsed])
        except FileNotFoundError:
            print(f"Traffic log file not found: {self.TRAFFIC_LOG}")
        except Exception as e:
            print(f"Error reading traffic log file: {e}")

    def _process_connection_data(self, logs):
        """Store connection events in database."""
        if not logs:
            return
            
        for log in logs:
            # Check for existing entry to avoid duplicates
            existing = Connection.query.filter_by(
                timestamp=log['timestamp'],
                user=log['user'],
                event_type=log['event']
            ).first()
            
            if not existing:
                connection = Connection(
                    timestamp=log['timestamp'],
                    user=log['user'],
                    event_type=log['event'],
                    bytes_received=0,
                    bytes_sent=0
                )
                db.session.add(connection)
                try:
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving connection data: {e}")
                    db.session.rollback()
    
    def _process_traffic_data(self, logs):
        """Store traffic statistics in database."""
        if not logs:
            return
            
        for log in logs:
            # Check for existing entry to avoid duplicates
            existing = Connection.query.filter_by(
                timestamp=log['timestamp'],
                user=log['user'],
                event_type='SESSION_END'
            ).first()
            
            if not existing:
                connection = Connection(
                    timestamp=log['timestamp'],
                    user=log['user'],
                    event_type='SESSION_END',
                    bytes_received=log['bytes_received'],
                    bytes_sent=log['bytes_sent']
                )
                db.session.add(connection)
                try:
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving traffic data: {e}")
                    db.session.rollback()
    
    def get_usage_metrics(self):
        """Get current usage metrics from database."""
        current_time = datetime.now()
        timeout = current_time - timedelta(minutes=5)
        
        active_users = db.session.query(Connection.user).distinct().filter(
            Connection.timestamp >= timeout,
            Connection.event_type == 'connected'
        ).count()
        
        bandwidth = db.session.query(
            db.func.sum(Connection.bytes_received).label('download'),
            db.func.sum(Connection.bytes_sent).label('upload')
        ).first()
        
        return {
            'active_users': active_users,
            'bandwidth_usage': {
                'download': bandwidth[0] or 0,
                'upload': bandwidth[1] or 0
            },
            'total_connections': Connection.query.count()
        }
    
    def get_historical_data(self, days=7):
        """Get historical connection data from database."""
        cutoff = datetime.now() - timedelta(days=days)
        
        historical_data = Connection.query.filter(
            Connection.timestamp >= cutoff
        ).order_by(Connection.timestamp.asc()).all()
        
        # Convert to DataFrame for visualization compatibility
        return pd.DataFrame([{
            'timestamp': entry.timestamp,
            'user': entry.user,
            'event_type': entry.event_type,
            'bytes_received': entry.bytes_received,
            'bytes_sent': entry.bytes_sent
        } for entry in historical_data])
