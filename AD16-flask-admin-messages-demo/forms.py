from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm


class ChatInputForm(FlaskForm):
    message = StringField(
        'Message',
        validators=[DataRequired(), Length(min=0, max=140)],
        render_kw={'type': 'text'})
    submit = SubmitField('Send')
