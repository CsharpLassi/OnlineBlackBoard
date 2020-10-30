from flask import session

from obb.blackboard.memory import (
    user_memory,
    MemoryUser,
    user_session_memory,
    MemorySessionUser,
)
from obb.blackboard.models import BlackboardRoom
from obb.tools import id_generator
from obb.users.models import User


def get_mem_user_session(room: BlackboardRoom):
    mem_user: MemoryUser = user_memory.get(session.get("user_id", None))
    if not mem_user:
        mem_user = MemoryUser()
        user_memory.add(mem_user.id, mem_user)
        session["user_id"] = mem_user.id

    mem_user_session_id = mem_user.sessions.get(room.id)
    mem_user_session = user_session_memory.get(mem_user_session_id)

    sid = mem_user_session_id or id_generator(24)
    if not mem_user_session:
        mem_user_session = MemorySessionUser(sid, User.get_current_id())
        user_session_memory.add(sid, mem_user_session)
        mem_user.sessions[room.id] = sid

    return mem_user_session
