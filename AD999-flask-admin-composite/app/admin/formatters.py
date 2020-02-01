from jinja2 import Markup
from flask import render_template, render_template_string


def boolean_formatter(val_to_format):
    if val_to_format is None:
        return ''
    if isinstance(val_to_format, bool):
        if val_to_format is True:
            val_to_format = '<span class="fa fa-check-circle glyphicon glyphicon-ok-circle icon-ok-circle"></span>'
        else:
            val_to_format = '<span class="fa fa-minus-circle glyphicon glyphicon-minus-sign icon-minus-sign"></span>'
    return val_to_format


def _obj_formatter_str(view, context, model,
                       value=None, model_name=None, title=None, fields=None,
                       detail_fields=None, detail_field=None):

    endpoint = model_name

    header, detail_labels, detail_lines = [], [], []
    for k in fields:
        field = {}
        val = getattr(value, str(k['field']))
        field['label'] = k['label']
        field['value'] = str(boolean_formatter(val))
        header.append(field)

    detail_val = getattr(
        value, detail_field) if detail_field is not None else None
    if detail_val is not None and len(detail_val) > 0:
        for detail_key in detail_fields:
            detail_labels.append(detail_key['label'])
        for detail_line_val in detail_val:
            line_vals = []
            for detail_key in detail_fields:
                val = str(boolean_formatter(
                    getattr(detail_line_val, detail_key['field'])))
                line_vals.append(val)
            detail_lines.append(line_vals)
    # 返回 object_ref 引用模板
    return render_template('admin/components/object_ref.html',
                           title=title, value=value, endpoint=endpoint,
                           header=header, detail_labels=detail_labels,
                           detail_lines=detail_lines, view=view)


def _obj_formatter(view, context, model,
                   value=None, model_name=None, title=None, fields=None,
                   detail_fields=None, detail_field=None):
    str_markup = _obj_formatter_str(view, context, model, value, model_name,
                                    title, fields, detail_fields, detail_field)
    return Markup(str_markup)


def _user_obj_formatter(view, context, model, value, *args, **kwargs):
    fields = [
        {
            'label': 'name', 'field': 'name'
        },
        {
            'label': 'username', 'field': 'username'
        }
    ]

    return _obj_formatter(view, context, model,
                          value=value, model_name='user',
                          title=value.username, fields=fields,
                          *args, **kwargs)


def user_formatter(view, context, model, name):
    user = getattr(model, name, None)
    if user is None:
        return ''
    return _user_obj_formatter(view, context, model, value=user)


def tags_formatter(view, context, model, name):
    tags = getattr(model, name, [])
    if not tags:
        return ''
    tags_templates = []
    for tag in tags:
        name = tag.name
        template_string = f'<span style="display: inline-block;" class="label label-primary">{name}</span>'
        tags_templates.append(render_template_string(template_string))
    return Markup(' '.join(tags_templates))
