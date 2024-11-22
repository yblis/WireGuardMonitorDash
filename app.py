from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from datetime import datetime, timedelta
import json
from models import db, Connection
from data_processor import VPNDataProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # For development only
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vpn_monitor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app)

with app.app_context():
    db.create_all()
    vpn_processor = VPNDataProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/metrics')
def get_metrics():
    metrics = vpn_processor.get_usage_metrics()
    return jsonify(metrics)

@app.route('/api/active_sessions')
def get_active_sessions():
    active_sessions = Connection.query.filter(
        Connection.timestamp >= datetime.utcnow() - timedelta(minutes=5)
    ).all()
    return jsonify([{
        'user': session.user,
        'timestamp': session.timestamp.isoformat(),
        'bytes_received': session.bytes_received,
        'bytes_sent': session.bytes_sent
    } for session in active_sessions])

@app.route('/api/usage_history')
def get_usage_history():
    history = Connection.query.filter(
        Connection.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).all()
    return jsonify([{
        'timestamp': entry.timestamp.isoformat(),
        'bytes_received': entry.bytes_received,
        'bytes_sent': entry.bytes_sent,
        'user': entry.user
    } for entry in history])

def update_metrics():
    """Send updated metrics via WebSocket"""
    with app.app_context():  # Add application context here
        while True:
            try:
                vpn_processor.process_logs()
                metrics = vpn_processor.get_usage_metrics()
                socketio.emit('metrics_update', metrics)
                socketio.sleep(10)
            except Exception as e:
                print(f"Error in update_metrics: {e}")
                socketio.sleep(10)  # Wait before retrying

@socketio.on('connect')
def handle_connect():
    socketio.start_background_task(update_metrics)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
