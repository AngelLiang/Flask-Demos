from wtforms import StringField

DEFAULT_ENDPOINT = 'imagefileadmin.download'


class ImageInput(object):
    """
    Image upload controller, supports
    1. Multiple file upload one time
    2. Preview existing image files on server.
    3. Preview to be uploaded image files on the fly before uploading.
    Template file components/image_field.html is needed for this controller
    to work correctly.
    """

    def __call__(self, field, **kwargs):
        # Use field.data to get current data.
        from flask import render_template
        associated_images = []
        if ((field.data is not None and hasattr(field.data, 'filename') and len(field.data.filename) > 0)
                or (field.data is not None and hasattr(field.data, '__len__') and len(field.data) > 0)):
            for p_i in field.data:
                associated_images.append(p_i)
        else:
            associated_images = []
        return render_template('components/images_input.html',
                               associated_images=associated_images,
                               image_endpoint=DEFAULT_ENDPOINT)


class ImageField(StringField):
    widget = ImageInput()

    def __call__(self, **kwargs):
        return super(ImageField, self).__call__(**kwargs)

    def set_object_type(self, object_type):
        self.object_type = object_type

    def populate_obj(self, obj, name):
        from flask import request
        images_to_del = request.form.get('images-to-delete')
        if len(images_to_del) > 0:
            to_del_ids = images_to_del.split(',')
            for to_del_id in to_del_ids:
                pass
                # TODO:
                # db_util.delete_by_id(self.object_type, to_del_id, commit=False)
        files = request.files.getlist('images_placeholder')
        images = getattr(obj, name)
        for f in files:
            if len(f.filename) > 0:
                pass
                # TODO:
                # image_owner = self.object_type()
                # image = file_util.save_image(image_owner, f)
                # Info.get_db().session.add(image)
                # Info.get_db().session.add(image_owner)
                # images.append(image_owner)
        setattr(obj, name, images)


def images_formatter(view, context, model, name):
    from flask import render_template
    from wtforms.widgets import HTMLString
    val = getattr(model, name)
    return HTMLString(render_template("components/images_display.html",
                                      associated_images=val,
                                      image_endpoint=DEFAULT_ENDPOINT))
