import os
import shutil
from typing import TypeVar, Iterator

# noinspection PyTypeChecker
from flask import current_app
from flask_login import current_user

LP = TypeVar("LP", bound="LecturePage")


class LecturePageWrapper:
    @staticmethod
    def create(lecture: "Lecture", creator=None) -> "LecturePage":
        from ..lecture_page import LecturePage

        if current_user and current_user.is_authenticated:
            creator = current_user

        new_page = LecturePage()
        new_page.lecture = lecture
        new_page.creator = creator

        return new_page

    def export_to(self: LP, path: str):
        full_path = os.path.join(path, "page.json")
        os.makedirs(path, exist_ok=True)

        data = self.get_data()
        with open(full_path, "w") as fs:
            fs.write(data.to_json())

        # Todo:
        base_dir = current_app.config["BLACKBOARD_DATA_PATH"]
        base_path = os.path.join(base_dir, "pages", str(self.id))

        for file in os.listdir(base_path):
            shutil.copy(os.path.join(base_path, file), os.path.join(path, file))

        return

    @property
    def next_pages(self: LP) -> Iterator[LP]:
        query = self.query

        query = query.filter_by(prev_page_id=self.id)

        return query.all()
