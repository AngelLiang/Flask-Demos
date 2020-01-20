from sqlalchemy.ext.serializer import dumps, loads


def dump_data(db, contents):
    return dumps(contents)


def load_data(db, contents):
    return loads(contents, db.metadata, db.session)
