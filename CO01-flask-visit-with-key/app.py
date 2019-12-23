from werkzeug.security import gen_salt
from flask import Flask
from flask import request, session, abort, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'

key = gen_salt(20)


@app.before_request
def before_request():
    validation = session.get('validation')
    if validation == key:
        return
    request_key = request.args.get('key')
    if request_key == key:
        # 把 key 存放到 flask.session
        session['validation'] = key
        # 通过重定向去掉URL参数里的key
        return redirect(request.base_url)
    abort(403)


@app.route('/')
@app.route('/index')
def index():
    return 'hello world'


print(f' * Visit: http://127.0.0.1:5000?key={key}')

if __name__ == "__main__":
    app.run(debug=True)
