from __future__ import annotations

from typing import Optional, Iterator

from ..ext import db


class BlackboardRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User')

    @staticmethod
    def get(id) -> Optional[BlackboardRoom]:
        return BlackboardRoom.query.get(id)

    @staticmethod
    def get_active_rooms() -> Iterator[BlackboardRoom]:
        return BlackboardRoom.query.all()

    @staticmethod
    def get_active_room(name: str) -> Optional[BlackboardRoom]:
        query = BlackboardRoom.query.filter_by(name=name)
        return query.first()
