import flask

from .components.session_manager import BlackBoardSessionManager
from .components.page_manager import PageManager

namespace = '/blackboard'

bb_session_manager = BlackBoardSessionManager()
page_manager = PageManager()
