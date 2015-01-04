import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()

def log(*args):
    with open("/tmp/porra.log", "a+") as logfile:
        print >> logfile, args
