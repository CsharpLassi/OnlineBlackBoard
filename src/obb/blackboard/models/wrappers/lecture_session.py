from typing import Iterator


class LectureSessionWrapper:
    @classmethod
    def get_lectures(cls, maintainer_id: int = None) -> "Iterator[LectureSession]":
        query = cls.query

        if maintainer_id:
            query = query.filter_by(maintainer_id=maintainer_id)

        return query.all()
