import os
from dataclasses import dataclass
from typing import Optional

from flask import current_app

from obb.tools.MemDb import MemDb
from ..models import LecturePage, Lecture
from ..messages.base_data_class import BaseDataClass


@dataclass
class PageSession(BaseDataClass):
    page_id: int
    markdown: str = ''

    def get_base_path(self):
        base_dir = current_app.config['BLACKBOARD_DATA_PATH']
        base_path = os.path.join(base_dir, 'pages', str(self.page_id))

        return base_path

    def read_markdown(self) -> str:
        if self.markdown:
            return self.markdown
        # Todo: Thread Safe

        file_path = os.path.join(self.get_base_path(), 'markdown.md')

        raw_text: str = ''
        if os.path.exists(file_path):
            with open(file_path, 'r')as fs:
                while buffer := fs.read(1024):
                    raw_text += buffer

        self.markdown = raw_text
        return raw_text

    def save_markdown(self, markdown: str = None):
        if markdown:
            self.markdown = markdown
        else:
            markdown = self.markdown

        if markdown is None:
            return

        # Todo: Thread Safe

        base_path = self.get_base_path()
        file_path = os.path.join(base_path, 'markdown.md')

        os.makedirs(base_path, exist_ok=True)
        with open(file_path, 'w')as fs:
            fs.write(markdown)


class PageManager(MemDb[int, PageSession]):

    def _on_get(self, key: int, item: Optional[PageSession], lecture: Lecture = None) \
            -> Optional[PageSession]:

        page = lecture.get_page(key)

        if not page:
            return None

        if not item:
            item = PageSession(page.id)

        return item
