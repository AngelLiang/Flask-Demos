from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
admin.init_app(app)


class UserModelView(ModelView):
    column_list = ('id', 'name', 'email')
    column_default_sort = 'id'


@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


from .database import db_session, init_db, init_data
from .models import User

init_db(app)
init_data(db_session)
admin.add_view(UserModelView(User, db_session))


if __name__ == "__main__":
    app.run(debug=True)
