import json
import os
from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json
from flask import current_app

from ..datas import StrokeData
from ..models import LecturePage, LecturePageData


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MemoryLecturePageData:
    base: LecturePageData


class MemoryLecturePage:
    def __init__(self, id: int):
        self.id = id

        self.markdown: str = ""
        self.strokes = list()

        self.read_markdown()
        self.read_strokes()

    @property
    def model(self) -> LecturePage:
        return LecturePage.get(self.id)

    def get_data(self) -> MemoryLecturePageData:
        return MemoryLecturePageData(base=self.model.get_data())

    def emit_update(self, room_id, changes=None):
        from obb.api import emit_success
        from ..events.global_message import PageUpdatedEvent

        emit_success(
            "room:update:page",
            PageUpdatedEvent(
                page=self.get_data(),
                all=not list,
                changes=list() if changes is None else changes,
            ),
            room=room_id,
        )

    def read_markdown(self):
        file_path = os.path.join(self.get_base_path(), "markdown.md")
        if not os.path.exists(file_path):
            return

        raw_text: str = ""
        if os.path.exists(file_path):
            with open(file_path, "r") as fs:
                while True:
                    buffer = fs.read(1024)
                    if not buffer:
                        break
                    raw_text += buffer

        self.markdown = raw_text

    def save_markdown(self,):
        # Todo: Thread Safe
        base_path = self.get_base_path()
        file_path = os.path.join(base_path, "markdown.md")

        os.makedirs(base_path, exist_ok=True)
        with open(file_path, "w") as fs:
            fs.write(self.markdown)

    def read_strokes(self):
        # Todo: Thread Safe
        base_path = self.get_base_path()
        file_path = os.path.join(base_path, "strokes.json")
        if not os.path.exists(file_path):
            return

        json_list: list

        with open(file_path, "r") as fs:
            txt: str = ""
            while True:
                read_txt = fs.read(1024)
                if not read_txt:
                    break
                txt += read_txt
            json_list = json.loads(txt)

        self.strokes.clear()
        for item in json_list:
            self.strokes.append(StrokeData.from_dict(item))
            pass

    def save_strokes(self):
        base_path = self.get_base_path()
        file_path = os.path.join(base_path, "strokes.json")

        os.makedirs(base_path, exist_ok=True)
        save_list = [stroke.to_dict() for stroke in self.strokes]

        json_txt = json.dumps(save_list)
        with open(file_path, "w") as fs:
            fs.write(json_txt)

    def get_base_path(self):
        base_dir = current_app.config["BLACKBOARD_DATA_PATH"]
        base_path = os.path.join(base_dir, "pages", str(self.id))

        return base_path

    def clear_temp_data(self):
        pass
