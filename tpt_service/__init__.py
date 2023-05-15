from flask import Flask, jsonify
from flask_cors import CORS
from logging.config import dictConfig
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy.pool import NullPool
from tpt import TPT


echo_pool = False
level = 'INFO'
debug = False
if int(os.getenv('DEBUG', 0)):
    echo_pool = 'debug'
    level = 'DEBUG'
    debug = True

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': level,
        'handlers': ['wsgi']
    }
})

# Create flask app
app = Flask(__name__)

# customize as JSON errors
@app.errorhandler(403)
def forbidden(e):
    return jsonify(error=str(e)), 403

# accepts requests from all sources, may change in future for security reasons
cors = CORS(app, resources={r"*": {"origins": "*"}})

# create database
db_address = os.getenv('DB_ADDRESS', None)
db_port = os.getenv('DB_PORT', None)
db_name = os.getenv('DB_NAME', None)
db_user = os.getenv('DB_USER', None)
db_password = os.getenv('DB_PASSWORD', None)
db_schema = os.getenv('DB_SCHEMA', None)
db_engine = os.getenv('DB_ENGINE', None)
settings_file = os.getenv('SETTINGS_FILE', 'tpt_service/tpt.ini')
db_force_create = os.getenv('DB_FORCE_CREATE', True)

database_string = u'{0}://{1}:{2}@{3}:{4}/{5}'.format(db_engine, db_user, db_password, db_address,
                                                      db_port, db_name)

database_engine = create_engine(database_string, echo_pool=echo_pool, echo=debug, #pool_recycle=3600,
                                poolclass=SingletonThreadPool)

tpt = TPT(engine=database_engine, logger=app.logger, settings_file=settings_file,
          create_db=db_force_create, debug=True)

# Import all API endpoints
from tpt_service.api.activity import *
from tpt_service.api.enrolment import *
from tpt_service.api.errors import *
from tpt_service.api.health import *
from tpt_service.api.learner import *
from tpt_service.api.verification import *
from tpt_service.report.detail import *
