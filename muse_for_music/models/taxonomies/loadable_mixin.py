from csv import DictReader
from ... import db


class LoadableMixin():

    @classmethod
    def clear_all(cls):
        objects = cls.query.all()
        for obj in objects:
            db.session.delete(obj)
        db.session.commit()

    @staticmethod
    def load(input_data: DictReader):
        NotImplementedError
