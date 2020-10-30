import os
import shutil
import tempfile
from typing import Optional, TypeVar, Tuple, Dict, Any

# noinspection PyTypeChecker
from flask import current_app

BS = TypeVar("BS", bound="BlackboardRoom")
# noinspection PyTypeChecker
L = TypeVar("L", bound="Lecture")
# noinspection PyTypeChecker
LS = TypeVar("LS", bound="LectureSession")
# noinspection PyTypeChecker
LP = TypeVar("LP", bound="LecturePage")


class BlackboardRoomWrapper:
    def get_current_lecture_session(self: BS) -> Optional[LS]:
        """
        :rtype: Optional[LectureSession]
        """
        from .models import LectureSession

        lecture: LectureSession
        for lecture in self.sessions:
            if lecture.is_open():
                return lecture

        return None


class LecturePageWrapper:
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


class LectureWrapper:
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
        from .models import LecturePage

        query = LecturePage.query.filter_by(lecture_id=self.id).order_by(LecturePage.id)

        return query.first()

    @property
    def current_page(self: L) -> Optional[LP]:
        from .models import LecturePage

        query = LecturePage.query.filter_by(lecture_id=self.id).order_by(
            LecturePage.id.desc()
        )

        return query.first()
