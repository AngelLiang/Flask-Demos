from flask import Flask
from flask import flash
from flask import request
from flask import current_app
from flask import render_template
from wtforms import ValidationError
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import validate_csrf

csrf = CSRFProtect()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
csrf.init_app(app)


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        current_app.logger.debug(request.values)
        csrf_token = request.values.get('csrf_token')
        try:
            validate_csrf(csrf_token)
        except ValidationError as e:
            current_app.logger.error(e)
            flash(e.args[0])
        else:
            action = request.values.get('action')
            flash(f'{action} successful')

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
