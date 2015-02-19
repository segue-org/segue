import flask_sqlalchemy
import flask_jwt
import flask_mail


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

db = flask_sqlalchemy.SQLAlchemy()
jwt = flask_jwt.JWT()
mail = flask_mail.Mail()
jwt_required = flask_jwt.jwt_required
config = Config()
