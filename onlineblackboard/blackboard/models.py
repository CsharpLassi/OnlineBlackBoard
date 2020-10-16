from ..ext import db


class BoardSession(db.Model):
    id = db.Column(db.String, primary_key=True)
