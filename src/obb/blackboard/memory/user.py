from typing import Dict

from obb.tools import id_generator


class MemoryUser:
    def __init__(self):
        self.id = id_generator(24)
        self.sessions: Dict[str, str] = dict()

    def clear_temp_data(self):
        pass
