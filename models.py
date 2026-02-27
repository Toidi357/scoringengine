from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize db without the app first
db = SQLAlchemy()

# --- Database Model ---
class ScoreResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Boolean, nullable=False) # True = UP, False = DOWN
    timestamp = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "check_name": self.check_name,
            "host": self.host,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }