from .basemodel import BaseModel
from ...ext import db


class IntegerKeyModel(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
