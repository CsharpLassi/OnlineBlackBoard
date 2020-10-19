from __future__ import annotations

from operator import or_
from typing import Optional, Iterator

from ..ext import db

default_draw_height = 256
default_visibility = 'creator_only'

blackboardRoom_visibilities = ('creator_only', 'public')


def create_default_id() -> str:
    from obb.tools import id_generator
    return id_generator(12)


class BlackboardRoom(db.Model):
    id = db.Column(db.String, primary_key=True, default=create_default_id)
    name = db.Column(db.String,
                     nullable=False,
                     index=True)
    full_name = db.Column(db.String,
                          nullable=False,
                          index=True,
                          unique=True)

    draw_height = db.Column(db.Integer,
                            nullable=False,
                            default=default_draw_height,
                            server_default=str(default_draw_height))

    visibility = db.Column(db.String, nullable=False,
                           server_default=default_visibility,
                           default=default_visibility)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User')

    def can_join(self, user=None) -> bool:
        from flask_login import current_user
        from ..users.models import User

        if isinstance(user, int):
            user = User.get(user)

        if not user:
            user = current_user

        if user.id == self.creator_id:
            return True

        if self.visibility == 'public':
            return True

        return False

    def get_style(self) -> str:
        style = ''
        if self.draw_height > 0:
            style += f'height:{self.draw_height}px;'
        return style

    @staticmethod
    def get(id) -> Optional[BlackboardRoom]:
        return BlackboardRoom.query.get(id)

    @staticmethod
    def get_by_name(name: str) -> Optional[BlackboardRoom]:
        query_name = BlackboardRoom.query.filter_by(name=name)
        if query_name.count() == 1:
            return query_name.first()

        query_fullname = BlackboardRoom.query.filter_by(full_name=name)
        return query_fullname.first()

    @staticmethod
    def get_rooms(user=None) -> Iterator[BlackboardRoom]:
        from flask_login import current_user
        from ..users.models import User

        if isinstance(user, int):
            user = User.get(user)

        if not user:
            user = current_user

        return BlackboardRoom.query.filter_by(creator_id=user.id).all()
