from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from typing import Dict, List

from dataclasses_json import LetterCase, dataclass_json
from flask import current_app

from obb.blackboard.datas import StrokeData
from obb.users.models import User, UserData


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MemorySessionUserData:
    base: UserData
    session_id: str
    current_room: str
    current_page: int
    mode: str
    allow_draw: bool
    allow_new_page: bool


class MemorySessionUser:
    def __init__(self, sid: str, id: int = None):
        self.sid = sid
        self.id = id
        self.socket_id = None

        self.current_room: str = ""
        self.current_page = 0

        self.mode: str = "blackboard"
        self.allow_draw: bool = False
        self.allow_new_page: bool = False

        self.strokes: Dict[int, List[StrokeData]] = dict()

        self.temp_paths = list()

        self.read_strokes()

    @property
    def model(self) -> User:
        return User.get(self.id)

    def get_data(self) -> MemorySessionUserData:
        user = self.model

        user_data = UserData() if user is None else user.get_data()
        return MemorySessionUserData(
            base=user_data,
            session_id=self.sid,
            current_room=self.current_room,
            current_page=self.current_page,
            mode=self.mode,
            allow_draw=self.allow_draw,
            allow_new_page=self.allow_new_page,
        )

    def emit_self(self, changes: list = None):
        from obb.api import emit_success
        from ..events.global_message import UserUpdatedEvent

        if not self.socket_id:
            return

        emit_success(
            "self:update",
            UserUpdatedEvent(
                user=self.get_data(),
                all=not list,
                changes=list() if changes is None else changes,
            ),
            room=self.socket_id,
        )

    def save_strokes(self):
        base_path = self.get_base_path()
        for page_id, stroke_list in self.strokes.items():
            page_page = os.path.join(base_path, "page", str(page_id))
            file_path = os.path.join(page_page, "strokes.json")

            os.makedirs(page_page, exist_ok=True)
            save_list = [stroke.to_dict() for stroke in stroke_list]

            json_txt = json.dumps(save_list)
            with open(file_path, "w") as fs:
                fs.write(json_txt)

    def read_strokes(self):
        # Todo: Thread Safe
        base_path = self.get_base_path()

        base_page_path = os.path.join(base_path, "page")

        if not os.path.exists(base_page_path):
            return

        for child_path in os.listdir(base_page_path):
            page_path = os.path.join(base_page_path, child_path)
            if os.path.isdir(page_path):
                file_path = os.path.join(page_path, "strokes.json")
                if os.path.exists(file_path):
                    json_list: list

                    with open(file_path, "r") as fs:
                        txt: str = ""
                        while True:
                            read_txt = fs.read(1024)
                            if not read_txt:
                                break
                            txt += read_txt
                        json_list = json.loads(txt)

                    stroke_list = self.strokes.get(int(child_path))
                    if not stroke_list:
                        stroke_list = list()
                        self.strokes[int(child_path)] = stroke_list

                    if stroke_list:
                        stroke_list.clear()

                    for item in json_list:
                        stroke_list.append(StrokeData.from_dict(item))

    def get_base_path(self):
        if self.id:
            base_dir = current_app.config["BLACKBOARD_DATA_PATH"]
            base_path = os.path.join(base_dir, "user", str(self.id))
        else:
            base_dir = os.path.join("/tmp", "blackboard")
            base_path = os.path.join(base_dir, "user", str(self.sid))
            if base_path not in self.temp_paths:
                self.temp_paths.append(base_path)

        return base_path

    def clear_temp_data(self):
        while len(self.temp_paths) > 0:
            path = self.temp_paths.pop()
            shutil.rmtree(path, ignore_errors=True)
