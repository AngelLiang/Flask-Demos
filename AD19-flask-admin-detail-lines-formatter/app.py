import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
admin.init_app(app)


####################################################################
# models

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property


class Product(db.Model):
    """产品"""
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))

    def __repr__(self):
        return self.name


class Order(db.Model):
    """订购单"""
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    order_number = Column(String(32))


class OrderLine(db.Model):
    __tablename__ = 'order_line'

    id = Column(Integer, primary_key=True)
    unit_price = Column(Numeric(
        precision=8, scale=2, decimal_return_scale=2), nullable=False)
    quantity = Column(Numeric(
        precision=8, scale=2, decimal_return_scale=2), nullable=False)

    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    order = relationship('Order', backref=backref(
        'lines', cascade='all, delete-orphan'))

    # 产品
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')

####################################################################
# formatter


from jinja2 import Markup
from flask import render_template


def boolean_formatter(val_to_format):
    if val_to_format is None:
        return ''
    if isinstance(val_to_format, bool):
        if val_to_format is True:
            val_to_format = '<span class="fa fa-check-circle glyphicon glyphicon-ok-circle icon-ok-circle"></span>'
        else:
            val_to_format = '<span class="fa fa-minus-circle glyphicon glyphicon-minus-sign icon-minus-sign"></span>'
    return val_to_format


def line_formatter(view, context, model, name):
    value = getattr(model, name, [])
    fields = view.line_fields
    labels, values = [], []

    if isinstance(fields, dict):
        fields = fields.get(name, [])

    for field in fields:
        labels.append(field['label'])

    for line in value:
        line_val = []
        for f in fields:
            val = getattr(line, f['field'])
            line_val.append(str(boolean_formatter(val)))
        values.append(line_val)
    result = render_template('components/detail_lines.html',
                             detail_labels=labels,
                             detail_lines=values)
    return result

###################################################################
# utils


def is_list_field(model, field):
    """
    Whether a field is a list field
    :param model:  Model of the field
    :param field: name of the field to check 
    :return: True if attribute with the name is a list field, False otherwise. 
    """
    import sqlalchemy
    return (type(getattr(model, field)) == sqlalchemy.orm.collections.InstrumentedList)\
        if hasattr(model, field) else False


def has_detail_field(form_or_view):
    """
    Whether a form or view has a inline field
    This is used in template to decide how to display the form 
    :param form_or_view: the admin form or admin view to check
    :return: True if has detail field, otherwise false 
    """
    if hasattr(form_or_view, 'line_fields'):
        line_fields = getattr(form_or_view, 'line_fields', None)
        if line_fields is not None:
            return len(line_fields) > 0
    else:
        try:
            for f in form_or_view:
                if is_inline_field(f):
                    return True
        except TypeError:
            return False


def is_inline_field(field):
    """
    Whether a field in create or edit form is an inline field
    :param field: THe field to check 
    :return: True if field is of instance InlineModelFormList, otherwise false 
    """
    from flask_admin.contrib.sqla.form import InlineModelFormList
    r = isinstance(field, InlineModelFormList)
    return r


def init_jinja2_functions(app):
    app.add_template_global(has_detail_field, 'has_detail_field')
    app.add_template_global(is_inline_field, 'is_inline_field')
    app.add_template_global(is_list_field, 'is_list_field')


####################################################################
# views


from flask_admin.contrib.sqla import ModelView as BaseModelView


class ModelView(BaseModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self.model, 'can_edit', self.can_edit)
        setattr(self.model, 'can_delete', self.can_delete)
        setattr(self.model, 'can_view_details', self.can_view_details)


class OrderModelView(ModelView):
    can_view_details = True
    column_details_list = ('order_number', 'lines',)

    column_formatters = {
        'lines': line_formatter
    }

    # for object_ref
    line_fields = {
        'lines': [
            {
                'label': 'product',
                'field': 'product'
            },
            {
                'label': 'unit_price',
                'field': 'unit_price'
            },
            {
                'label': 'quantity',
                'field': 'quantity'
            }
        ]
    }


admin.add_view(OrderModelView(Order, db.session))


def initdb(product_count=100, order_count=50, order_line_count=500):
    import random
    from faker import Faker
    fake = Faker('zh_CN')

    db.drop_all()
    db.create_all()

    products = []
    for i in range(product_count):
        product = Product(name=fake.word())
        products.append(product)
    db.session.add_all(products)
    db.session.commit()

    orders = []
    for i in range(order_count):
        order = Order(
            order_number=f'{int(time.time())}{i}'
        )
        orders.append(order)
    db.session.add_all(orders)
    db.session.commit()

    order_lines = []
    for i in range(order_line_count):
        order_line = OrderLine(
            product_id=random.randrange(1, Product.query.count()),
            order_id=random.randrange(1, Order.query.count()),
            unit_price=random.randint(1, 100),
            quantity=random.randint(1, 100),
        )
        order_lines.append(order_line)
    db.session.add_all(order_lines)
    db.session.commit()


@app.before_first_request
def init_data():
    initdb()


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'


init_jinja2_functions(app)

if __name__ == "__main__":
    app.run(debug=True)
