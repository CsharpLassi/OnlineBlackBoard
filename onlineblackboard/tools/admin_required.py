from functools import wraps

from flask import abort

from flask_login import current_user


def admin_required(func):
    @wraps(func)
    def check_user(*args, **kwargs):
        if not current_user or not current_user.is_authenticated:
            return abort(401)
        if not current_user.is_admin:
            # Todo: Logging
            return abort(401)
        return func(*args, **kwargs)

    return check_user
