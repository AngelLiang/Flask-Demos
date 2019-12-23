from flask import Flask
from flask_admin import Admin

admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
admin.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
