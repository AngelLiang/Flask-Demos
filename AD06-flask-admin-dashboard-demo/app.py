from flask import Flask
from flask_admin import Admin, AdminIndexView
from flask_admin import expose


class DashoboardView(AdminIndexView):
    @expose('/')
    def index(self):
        self.name = 'Dashboard'
        return self.render('admin/dashboard.html')


admin = Admin(template_mode='bootstrap3', index_view=DashoboardView(
    menu_icon_type='glyph',
    menu_icon_value='glyphicon-dashboard'))

app = Flask(__name__)
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
admin.init_app(app)


if __name__ == "__main__":
    app.run(debug=True)
