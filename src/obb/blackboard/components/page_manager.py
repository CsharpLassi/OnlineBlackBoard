import json
import os
from typing import Optional, List, Iterator

from flask import current_app

from obb.tools.MemDb import MemDb
from obb.tools.dataclasses import dataclass_from_dict
from ..messages.datas import StrokeData
from ..models import Lecture


class PageSession:
    def __init__(self, page_id: int):
        self.page_id: int = page_id
        self.__markdown: str = ''
        self.__stroke_history: List[StrokeData] = list()

        self.__read_markdown()
        self.__read_strokes()

    def __read_markdown(self):
        file_path = os.path.join(self.get_base_path(), 'markdown.md')
        if not os.path.exists(file_path):
            return

        raw_text: str = ''
        if os.path.exists(file_path):
            with open(file_path, 'r')as fs:
                while buffer := fs.read(1024):
                    raw_text += buffer

        self.__markdown = raw_text

    def __save_markdown(self, ):
        # Todo: Thread Safe
        base_path = self.get_base_path()
        file_path = os.path.join(base_path, 'markdown.md')

        os.makedirs(base_path, exist_ok=True)
        with open(file_path, 'w')as fs:
            fs.write(self.__markdown)

    def __read_strokes(self):
        base_path = self.get_base_path()
        file_path = os.path.join(base_path, 'strokes.json')
        if not os.path.exists(file_path):
            return

        json_list: list

        with open(file_path, 'r') as fs:
            txt: str = ''
            while read_txt := fs.read(1024):
                txt += read_txt
            json_list = json.loads(txt)

        self.__stroke_history.clear()
        for item in json_list:
            self.__stroke_history.append(dataclass_from_dict(StrokeData, item))

    def __save_strokes(self):
        base_path = self.get_base_path()
        file_path = os.path.join(base_path, 'strokes.json')

        os.makedirs(base_path, exist_ok=True)
        save_list = [stroke.to_dict() for stroke in self.__stroke_history]

        json_txt = json.dumps(save_list)
        with open(file_path, 'w') as fs:
            fs.write(json_txt)

    def get_base_path(self):
        base_dir = current_app.config['BLACKBOARD_DATA_PATH']
        base_path = os.path.join(base_dir, 'pages', str(self.page_id))

        return base_path

    def set_markdown(self, markdown: str):
        self.__markdown = markdown
        self.__save_markdown()

    def get_markdown(self) -> str:
        return self.__markdown

    def add_stroke(self, data: StrokeData):
        self.__stroke_history.append(data)
        self.__save_strokes()

    def get_strokes(self) -> Iterator[StrokeData]:
        for item in self.__stroke_history:
            yield item


class PageManager(MemDb[int, PageSession]):
    def _on_get(self, key: int, item: Optional[PageSession], lecture: Lecture = None,
                **kwargs) -> Optional[PageSession]:

        page = lecture.get_page(key, **kwargs)

        if not page:
            return None

        if not item:
            item = PageSession(page.id)

        return item
