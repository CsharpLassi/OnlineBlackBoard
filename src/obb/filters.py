import flask
from dateutil import tz

bp = flask.Blueprint('filter', __name__)


@bp.add_app_template_filter
def df(date, fmt=None):
    # Todo: From User Settings
    from_zone = tz.gettz('UTC')
    to_zone = tz.tzlocal()

    date = date.replace(tzinfo=from_zone).astimezone(to_zone)
    if fmt:
        return date.strftime(fmt)
    else:
        return date.strftime('%d.%m.%y %H:%M:%S')
