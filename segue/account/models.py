from ..json import SQLAlchemyJsonSerializer
from ..core import db

class Account(SQLAlchemyJsonSerializer, db.Model):
  id       = db.Column(db.Integer, primary_key=True)
  email    = db.Column(db.Text)
  name     = db.Column(db.Text)
  password = db.Column(db.Text)
  role     = db.Column(db.Enum("user","operator","admin"))
