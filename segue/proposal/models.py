from ..json import SQLAlchemyJsonSerializer
from ..core import db

import schema

class Proposal(SQLAlchemyJsonSerializer, db.Model):
  id          = db.Column(db.Integer, primary_key=True)
  title       = db.Column(db.Text)
  summary     = db.Column(db.Text)
  full        = db.Column(db.Text)
  language    = db.Column(db.String(100))
  level       = db.Column(db.Enum(*schema.PROPOSAL_LEVELS, name="proposal_levels"))
