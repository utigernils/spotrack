from datetime import datetime
from app import db


class Track(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    play_count = db.Column(db.Integer, nullable=False, default=0)
    total_listen_time_ms = db.Column(db.Integer, nullable=False, default=0)
    last_listened = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'artist': self.artist,
            'play_count': self.play_count,
            'total_listen_time': self.total_listen_time_ms // 1000,  # Convert to seconds
            'last_listened': self.last_listened.isoformat()
        }