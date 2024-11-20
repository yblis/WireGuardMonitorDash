from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)  # connected/disconnected/SESSION_END
    bytes_received = db.Column(db.BigInteger, default=0)
    bytes_sent = db.Column(db.BigInteger, default=0)
