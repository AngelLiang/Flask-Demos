from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView as BaseModelView


admin = Admin(name='SQLAlchemy Automap', template_mode='bootstrap3')

app = Flask(__name__)
admin.init_app(app)


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'


class ModelView(BaseModelView):
    pass


def init_admin(admin):
    from .database import db_session, Base
    # 反射所有 Class
    for Class in Base.classes:
        admin.add_view(ModelView(Class, db_session))


from .database import init_db

init_db(app)
init_admin(admin)

if __name__ == "__main__":
    app.run(debug=True)
