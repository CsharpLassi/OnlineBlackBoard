from __future__ import annotations

from operator import or_
from typing import Optional, Iterator

from ..ext import db


class BlackboardRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)

    visibility = db.Column(db.String, nullable=False,
                           server_default='creator_only',
                           default='creator_only')

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User')

    @staticmethod
    def get(id) -> Optional[BlackboardRoom]:
        return BlackboardRoom.query.get(id)

    @staticmethod
    def get_active_rooms() -> Iterator[BlackboardRoom]:
        from flask_login import current_user
        query = BlackboardRoom.query

        query = query.filter(or_(BlackboardRoom.visibility != 'creator_only',
                                 BlackboardRoom.creator_id == current_user.id))

        return query.all()

    @staticmethod
    def get_active_room(name: str) -> Optional[BlackboardRoom]:
        query = BlackboardRoom.query.filter_by(name=name)
        return query.first()
