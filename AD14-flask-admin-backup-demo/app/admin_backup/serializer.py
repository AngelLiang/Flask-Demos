from sqlalchemy.ext.serializer import dumps, loads


class Serializer:
    def __init__(self, db=None):
        self.db = db
        self.models = []

    def get_mapped_classes(self):
        db = self.db
        self.add_subclasses(db.Model)
        return self.models

    def add_subclasses(self, model):
        if model.__subclasses__():
            for submodel in model.__subclasses__():
                self.add_subclasses(submodel)
        else:
            self.models.append(model)

    def dump_data(self, contents):
        return dumps(contents)

    def load_data(self, contents):
        db = self.db
        return loads(contents, db.metadata, db.session)
