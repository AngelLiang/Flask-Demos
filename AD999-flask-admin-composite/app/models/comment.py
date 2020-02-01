from app.extensions import db
from .user import User
from .post import Post


class Comment(db.Model):
    """评论"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    user = db.relationship(User, backref='comments')

    post_id = db.Column(db.Integer(), db.ForeignKey(Post.id))
    post = db.relationship(Post, backref='comments')

    def __str__(self):
        return f'{self.content[:18]}'
