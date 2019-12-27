"""
Fork from: https://github.com/miguelgrinberg/flask-httpauth/#basic-authentication-example
"""

from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_admin import Admin
from flask_admin import AdminIndexView as BaseAdminIndexView


app = Flask(__name__)
auth = HTTPBasicAuth()


class AdminIndexView(BaseAdminIndexView):

    def is_accessible(self):
        _auth = auth.get_auth()
        password = auth.get_auth_password(_auth)
        return auth.authenticate(_auth, password)

    def inaccessible_callback(self, name, **kwargs):
        return auth.auth_error_callback()


admin = Admin(template_mode='bootstrap3', index_view=AdminIndexView())
admin.init_app(app)


users = {
    'admin': generate_password_hash("admin"),
}


@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@app.route('/')
@auth.login_required
def index():
    return "Hello, %s!" % auth.username()


if __name__ == '__main__':
    app.run()
