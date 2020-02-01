from app.extensions import db


class Tag(db.Model):
    """标签"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    created_at = db.Column(db.DateTime)

    def __str__(self):
        return f'{self.name}'
