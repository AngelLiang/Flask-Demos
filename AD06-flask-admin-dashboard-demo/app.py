from flask import Flask
from flask_admin import Admin, AdminIndexView
from flask_admin import expose
from flask_admin.menu import MenuLink

import stub


class DashoboardView(AdminIndexView):

    @expose('/')
    def index(self):
        self.name = 'Dashboard'
        self.messages = stub.get_messages_summary()
        self.tasks = stub.get_tasks()
        self.alerts = stub.get_alerts()
        return self.render('admin/dashboard.html')


admin = Admin(template_mode='bootstrap3', index_view=DashoboardView(
    menu_icon_type='glyph', menu_icon_value='glyphicon-dashboard'))

# 以下 link 会向左靠齐
admin.add_link(MenuLink(name='Back Home', url='/admin', category='Links'))
admin.add_link(MenuLink(name='Flask-Demos',
                        url='https://github.com/AngelLiang/Flask-Demos',
                        category='Links'))
admin.add_link(MenuLink(
    name='Baidu', url='http://www.baidu.com/', category='Links'))
# 以下 link 会向右靠齐
# admin.add_link(MenuLink(name='Logout', url='#'))


app = Flask(__name__)
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
admin.init_app(app)


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'


if __name__ == "__main__":
    app.run(debug=True)
