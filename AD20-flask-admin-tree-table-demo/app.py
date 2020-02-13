from sqlalchemy_mptt.mixins import BaseNestedSets

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
# 因为依赖 bootstrap3， 所以一定要设置 template_mode='bootstrap3'
admin = Admin(template_mode='bootstrap3')


app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'

db.init_app(app)
db.app = app
admin.init_app(app)


####################################################################
# model


class Tree(db.Model, BaseNestedSets):
    """混入了 BaseNestedSets ， 使用“左右值树”数据结构来处理树状数据"""

    __tablename__ = 'tree'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __str__(self):
        return '{}'.format(self.name)


####################################################################
# admin view


class TreeTableConfigMixin(object):
    """树形表格专用配置混入类"""
    # 设置 list_template
    list_template = 'admin/model/tree_list.html'

    # 禁止分页，直接获取该数据表所有数据
    page_size = None

    # 禁止设置每页显示的数量
    can_set_page_size = False

    # 禁止任何字段的排序，以免干扰 treegrid.js 显示正确的数据顺序
    column_sortable_list = []

    # 默认以 left 字段排序，使 treegrid.js 能正确显示树形表格
    column_default_sort = 'left'


class TreeView(TreeTableConfigMixin, ModelView):
    """
    注意 TreeTableConfigMixin 要放在 ModelView 前面
    """
    column_display_pk = True
    column_list = ['id', 'name', 'left',
                   'right', 'parent_id', 'level', 'tree_id']

    can_view_details = True
    can_edit = True
    can_delete = True


admin.add_view(TreeView(Tree, db.session))


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'


####################################################################


def initdb(count=10):
    db.drop_all()
    db.create_all()

    trunk = Tree(name="Trunk")
    db.session.add(trunk)
    for i in range(count):
        branch = Tree()
        branch.name = "Branch " + str(i+1)
        branch.parent = trunk
        db.session.add(branch)
        for j in range(5):
            leaf = Tree()
            leaf.name = "Leaf " + str(j+1)
            leaf.parent = branch
            db.session.add(leaf)
            for k in range(3):
                item = Tree()
                item.name = "Item " + str(k+1)
                item.parent = leaf
                db.session.add(item)
    db.session.commit()


@app.before_first_request
def init_data():
    initdb()


if __name__ == "__main__":
    app.run(debug=True)
