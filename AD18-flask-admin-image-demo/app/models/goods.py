
from app.extensions import db

from .image import HasImagesMixin


class Goods(db.Model, HasImagesMixin):
    __tablename__ = 'goods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
