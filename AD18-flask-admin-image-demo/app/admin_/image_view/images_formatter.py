from flask import render_template
from wtforms.widgets import HTMLString

from .image import get_image_endpoint


def images_formatter(view, context, model, name):
    val = getattr(model, name)
    return HTMLString(render_template("components/images_display.html",
                                      associated_images=val,
                                      image_endpoint=get_image_endpoint()))
