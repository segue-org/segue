import flask_sqlalchemy
import flask_jwt

db = flask_sqlalchemy.SQLAlchemy()
jwt = flask_jwt.JWT()

def log(*args):
    with open("/tmp/segue.log", "a+") as logfile:
        print >> logfile, args
