from sqlalchemy_mptt.mixins import BaseNestedSets

from .extensions import db


class Tree(db.Model, BaseNestedSets):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    # parent_id = db.Column(db.Integer, db.ForeignKey('tree.id'))
    # parent = db.relationship('Tree', remote_side=[id], backref='children')

    def __str__(self):
        return "{}".format(self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'left': self.left,
            'right': self.right,
            'parent_id': self.parent_id,
            'tree_id': self.tree_id,
        }
