import os
import shutil
import tempfile
from typing import Tuple, Dict, Any, Optional, TypeVar, Iterator

# noinspection PyTypeChecker
from flask_login import current_user

L = TypeVar("L", bound="Lecture")
# noinspection PyTypeChecker
LP = TypeVar("LP", bound="LecturePage")


class LectureWrapper:
    @staticmethod
    def get_lectures(user=None) -> Iterator[L]:
        from ..lecture import Lecture

        if not user and current_user and current_user.is_authenticated:
            user = current_user

        query = Lecture.query
        if user:
            query = query.filter_by(creator_id=user.id)

        return query

    @staticmethod
    def get_by_name(name: str, user=None) -> Optional[L]:
        from ..lecture import Lecture

        if not user and current_user and current_user.is_authenticated:
            user = current_user

        if not user:
            return None

        query = Lecture.query

        query = query.filter_by(creator_id=user.id)

        query = query.filter_by(name=name)

        if query.count() != 1:
            return None

        return query.first()

    def create_export_file(self: L) -> Tuple[str, str]:
        fname = f"lecture_{self.name}"
        export_fname = os.path.join("/tmp", "blackboard", fname)
        dir = os.path.dirname(export_fname)
        os.makedirs(dir, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmp_dirname:
            export_data: Dict[str, Any] = dict()
            export_data["lecture.json"] = self.get_data()

            for page in self.pages:
                base_page_path = os.path.join(tmp_dirname, "pages", str(page.id))

                page.export_to(base_page_path)

            for path, data in export_data.items():
                full_path = os.path.join(tmp_dirname, path)
                dir_path = os.path.dirname(full_path)

                os.makedirs(dir_path, exist_ok=True)
                with open(full_path, "w") as fs:
                    fs.write(data.to_json())
            shutil.make_archive(export_fname, "zip", tmp_dirname)

        return fname + ".zip", export_fname + ".zip"

    @property
    def start_page(self: L) -> Optional[LP]:
        from ..lecture_page import LecturePage

        query = LecturePage.query.filter_by(lecture_id=self.id).order_by(LecturePage.id)

        return query.first()

    @property
    def current_page(self: L) -> Optional[LP]:
        from ..lecture_page import LecturePage

        if self.current_page_id:
            return LecturePage.get(self.current_page_id)

        query = LecturePage.query.filter_by(lecture_id=self.id).order_by(
            LecturePage.id.desc()
        )

        return query.first()
