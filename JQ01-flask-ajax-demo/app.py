from flask import Flask
from flask import request, render_template, current_app
from wtforms import ValidationError
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import validate_csrf

####################################################################
# extensions

csrf = CSRFProtect()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
csrf.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ajax/delete', methods=['DELETE'])
def ajax_delete():
    csrf_token = request.headers.get('X-Csrftoken')
    current_app.logger.debug(csrf_token)
    try:
        validate_csrf(csrf_token)
    except ValidationError as e:
        current_app.logger.error(e)
        return '', 400

    current_app.logger.debug(request.values)
    return '', 204


if __name__ == "__main__":
    app.run(debug=True)
