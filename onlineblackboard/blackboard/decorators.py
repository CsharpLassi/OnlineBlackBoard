from functools import wraps
from typing import Type

from flask import request, flash, redirect, url_for

from .ext import room_db
from .server_models import BlackboardRoomSession
from .models import BlackboardRoom

from ..tools.dataclasses import dataclass_from_dict


def convert(cls: Type):
    def helper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args = list(args)
            args[0] = dataclass_from_dict(cls, args[0])

            return func(*args, **kwargs)

        return wrapper

    return helper


def check_room(fallback: str, create_room_from_db: bool = False):
    def check_room_helper(func):
        @wraps(func)
        def room_checker(*args, **kwargs):
            room_id = request.args.get('room_id')
            if not room_id:
                flash(f'room does not exist')
                return redirect(url_for(fallback))

            db_room = BlackboardRoom.get_active_room_by_room_id(room_id)

            room: BlackboardRoomSession = room_db.get(room_id)
            if not room and create_room_from_db:
                room = room_db.add(room_id, BlackboardRoomSession(db_room.name))

            if not room:
                flash(f'room does not exist')
                return redirect(url_for(fallback))

            kwargs['room'] = room
            return func(*args, **kwargs)

        return room_checker

    return check_room_helper
