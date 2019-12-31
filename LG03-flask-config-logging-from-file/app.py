from logging.config import dictConfig
from flask import Flask
import yaml


with open('log_config.yaml', 'r', encoding='utf-8') as f:
    log_config = yaml.unsafe_load(f.read())
    print(log_config)
    dictConfig(log_config)


app = Flask(__name__)
app.logger.debug('debug')
app.logger.info('info')  # [%(asctime)s] INFO in app: info
app.logger.error('error')  # [%(asctime)s] ERROR in app: error
