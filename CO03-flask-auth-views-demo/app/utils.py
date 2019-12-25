def is_field_error(errors):
    """
        Check if wtforms field has error without checking its children.

        :param errors:
            Errors list.
    """
    if isinstance(errors, (list, tuple)):
        for e in errors:
            if isinstance(e, str):
                return True

    return False
