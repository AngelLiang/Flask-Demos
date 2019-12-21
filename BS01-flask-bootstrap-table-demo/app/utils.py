from jinja2 import contextfunction

from .models import tree2schema


@contextfunction
def get_data_json(context):
    data = context['data']
    return [tree2schema(d) for d in data]


@contextfunction
def render_list_row_actions(context, row):
    get_pk_value = context['get_pk_value']
    list_row_actions = context['list_row_actions']
    row_actions = []
    for action in list_row_actions:
        row_actions.append(action.render_ctx(context, get_pk_value(row), row))
    return row_actions
