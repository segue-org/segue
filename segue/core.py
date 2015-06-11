import flask_sqlalchemy
import flask_jwt
import flask_mail
from flask.ext.cache import Cache

def log(*args):
    with open("/tmp/segue.log", "a+") as logfile:
        print >> logfile, args

class Config():
    def __init__(self):
        self._data = {}
    def __getattr__(self, name):
        return self._data.get(name, None)

    def init_app(self, app):
        self._data = app.config

class Logger():
    def __init__(self):
        self._logger = None

    def init_app(self, app):
        self._logger = app.logger

    def __getattr__(self, name):
        return getattr(self._logger, name)

db = flask_sqlalchemy.SQLAlchemy()
jwt = flask_jwt.JWT()
mailer = flask_mail.Mail()
cache = Cache(config={'CACHE_TYPE': 'simple'})
config = Config()
logger = Logger()

jwt_required = flask_jwt.jwt_required
