import string
import random

from ..tools import MemDb
from .models import BoardSession

namespace = '/blackboard'
room_db = MemDb[str, BoardSession]()


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
