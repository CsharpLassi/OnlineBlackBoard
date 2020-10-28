from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from ..ext import db, login


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserData:
    name: str = "Anonymous"
    is_admin: bool = False


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.BOOLEAN, server_default="0", default=False, nullable=False)

    lectures = db.relationship("Lecture", lazy=True)

    def get_data(self) -> UserData:
        return UserData(name=self.username, is_admin=self.is_admin)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(id) -> Optional[User]:
        return User.query.get(id)

    @staticmethod
    def get_current_id() -> Optional[int]:
        if current_user and current_user.is_authenticated:
            return current_user.id
        return None

    def __repr__(self):
        return "<User {}>".format(self.username)


@login.user_loader
def load_user(user_id) -> Optional[User]:
    return User.query.get(user_id)
