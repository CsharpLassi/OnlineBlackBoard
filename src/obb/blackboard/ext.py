import flask
from werkzeug.local import LocalProxy

from .components.session_manager import BlackBoardSessionHandler
from .server_models import BlackboardRoomSession, UserSessions
from ..tools.MemDb import MemDb

namespace = '/blackboard'

bb_manager = BlackBoardSessionHandler()

# room_db = MemDb[int, BlackboardRoomSession]()
# user_db = MemDb[str, UserSessions]()
