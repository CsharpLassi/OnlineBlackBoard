from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

import jwt

from flask import current_app
from flask_login import current_user

from obb.tools import id_generator
from obb.users.models import User


def calc_exp(minutes: float = 0) -> datetime.datetime:
    date = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
    return date


@dataclass_json
@dataclass
class ApiToken:
    user_id: int = 0
    sid: str = field(default_factory=lambda: id_generator(24))
    exp: float = field(default_factory=lambda: calc_exp(minutes=120).timestamp())

    def is_expired(self) -> bool:
        return datetime.datetime.utcnow() > datetime.datetime.utcfromtimestamp(self.exp)

    def encode(self, secret_key: str = None) -> str:
        if not secret_key:
            secret_key = current_app.secret_key
        session_dict = self.to_dict()
        return jwt.encode(session_dict, secret_key, "HS256").decode("UTF-8")

    @staticmethod
    def decode(token: str, secret_key: str = None) -> ApiToken:
        if not secret_key:
            secret_key = current_app.secret_key
        session_dict = jwt.decode(token, secret_key, algorithms=["HS256"])
        return ApiToken.from_dict(session_dict)

    @staticmethod
    def create_token(user=None, sid: str = None):
        assert not sid or len(sid) >= 24, "sid must be greater than 23"

        token = ApiToken(sid=sid)

        if not user and current_user.is_authenticated:
            user = current_user

        if user:
            token.user_id = user.id

        return token
