import flask

from .components.session_manager import BlackBoardSessionManager

namespace = '/blackboard'

bb_session_manager = BlackBoardSessionManager()
