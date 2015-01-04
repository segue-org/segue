from ..helpers import JsonSerializer
from ..core import db

class Proposal(JsonSerializer, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.Text)
  abstract = db.Column(db.Text)
  description = db.Column(db.Text)
  language = db.Column(db.String(100))
  level = db.Column(db.String(100))
