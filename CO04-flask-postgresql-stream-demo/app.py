import os
from flask import Flask, Response, render_template
import psycopg2
import psycopg2.extensions
import select


host = os.getenv('PG_HOST', '127.0.0.1')
database = os.getenv('PG_DB', 'message')
user = os.getenv('PG_USER', 'postgres')
password = os.getenv('PG_PASS', 'postgres')


def stream_messages(channel):
    conn = psycopg2.connect(host=host, database=database,
                            user=user, password=password)
    conn.set_isolation_level(
        psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
    )

    curs = conn.cursor()
    curs.execute('LISTEN channel_%d;' % int(channel))

    while True:
        select.select([conn], [], [])
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop()
            yield 'data: ' + notify.payload + '\n\n'


app = Flask(__name__)


@app.route('/message/<channel>', methods=['GET'])
def get_messages(channel):
    return Response(stream_messages(channel),
                    mimetype='text/event-stream')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
