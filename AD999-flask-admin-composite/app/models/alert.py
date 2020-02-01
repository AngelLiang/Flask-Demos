import datetime as dt
from app.extensions import db


class Alert(db.Model):
    """通知"""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(16))
    title = db.Column(db.String(128))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=dt.datetime.now)
    updated_at = db.Column(db.DateTime, default=dt.datetime.now)

    @property
    def time(self):
        return self.created_at

    def __str__(self):
        return f'{self.title}'
