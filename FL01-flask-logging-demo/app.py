from logging.config import dictConfig
from flask import Flask

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.logger.debug('debug')
app.logger.info('info')  # [%(asctime)s] INFO in app: info
app.logger.error('error')  # [%(asctime)s] ERROR in app: error
