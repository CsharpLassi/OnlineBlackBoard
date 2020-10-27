from functools import wraps

from flask import current_app, request
from jwt import ExpiredSignatureError

from .token import ApiToken
from .base_response import emit_error as error
from ..blackboard.memory import user_memory
from ..users.models import User


def convert_from_socket(cls=None):
    def helper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) == 0:
                error('invalid data')
                return

            values = args[0]

            if not isinstance(values, dict):
                error('invalid data')
                return

            token_str = values.pop('token', None)

            if not token_str:
                error('invalid token')
                return

            try:
                token = ApiToken.decode(token_str)

                if token.is_expired():
                    error('token has expired')
                    return

                item = values.pop('item', None)
                if item is None:
                    error('invalid item data')
                    return

                convert_item = None
                if isinstance(item, list):
                    convert_item = list()
                    for list_item in item:
                        convert_item.append(cls.from_dict(list_item))
                else:
                    convert_item = cls.from_dict(item)

                kwargs['sid'] = token.sid
                kwargs['socket_sid'] = request.sid
                kwargs['session'] = user_memory.get(token.sid)
                kwargs['user'] = User.get(token.user_id) if token.user_id else None

                result = func(convert_item, **kwargs)
            except ExpiredSignatureError:
                error('invalid token')
                return
            except AssertionError as ex:
                current_app.logger.exception(ex)
                error('invalid data ')
                return
            except Exception as ex:
                current_app.logger.exception(ex)
                error('Exception')
                return

            return

        return wrapper

    return helper
