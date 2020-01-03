import os.path as op
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.fileadmin import FileAdmin

admin = Admin(template_mode='bootstrap3')

path = op.join(op.dirname(__file__), 'static')
admin.add_view(FileAdmin(path, '/static/', name='Static Files'))

app = Flask(__name__)
admin.init_app(app)


if __name__ == "__main__":
    app.run(debug=True)
