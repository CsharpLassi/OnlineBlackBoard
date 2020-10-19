from functools import wraps
from typing import Type, Optional

from flask import request, flash, redirect, url_for, current_app
from werkzeug.datastructures import ImmutableMultiDict

from .models import BlackboardRoom
from .components.session_manager import BlackBoardSession, BlackBoardSessionToken
from .ext import bb_session_manager
from .messages.base_messages import BaseRequestMessage

from ..tools.dataclasses import dataclass_from_dict


def convert(cls):
    def helper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args = list(args)
            try:
                args[0] = dataclass_from_dict(cls, args[0])

                return func(*args, **kwargs)
            except Exception as ex:
                current_app.logger.exception(ex)

        return wrapper

    return helper


def to_form_dict(item: str = None):
    def helper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args = list(args)
            msg = args[0]
            if item:
                msg = msg[item]

            dict_values = dict()

            for value_item in msg:
                name = value_item['name']
                value = value_item['value']
                dict_values[name] = value
            if item:
                args.append(ImmutableMultiDict(dict_values))

            return func(*args, **kwargs)

        return wrapper

    return helper


def event_login_required(func):
    @wraps(func)
    def helper(*args, **kwargs):
        msg = args[0]

        room: Optional[BlackboardRoom] = None
        if isinstance(msg, BaseRequestMessage):
            if msg.session is None:
                return

            session: BlackBoardSession = bb_session_manager.get(msg.session.session_id)
            if session is None:
                return

            room = BlackboardRoom.get(session.room_id)
            if room is None or not room.can_join(session.user_id):
                return

        kwargs['room'] = room
        return func(*args, **kwargs)

    return helper
