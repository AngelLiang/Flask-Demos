from flask import Flask
from flask_admin import Admin, AdminIndexView as _AdminIndexView
from flask_admin import expose


class AdminIndexView(_AdminIndexView):
    @expose('/')
    def index(self):
        self.name = 'Dashboard'
        return self.render('admin/dashboard.html')


admin = Admin(template_mode='bootstrap3', index_view=AdminIndexView())

app = Flask(__name__)
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
admin.init_app(app)


if __name__ == "__main__":
    app.run(debug=True)
