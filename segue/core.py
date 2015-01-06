import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()

def log(*args):
    with open("/tmp/segue.log", "a+") as logfile:
        print >> logfile, args
