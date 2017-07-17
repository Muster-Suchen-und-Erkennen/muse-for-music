from csv import DictReader
from logging import Logger
from ... import db


class LoadableMixin():

    @classmethod
    def clear_all(cls, logger: Logger):
        objects = cls.query.all()
        for obj in objects:
            db.session.delete(obj)
        db.session.commit()

    @staticmethod
    def load(input_data: DictReader, logger: Logger):
        NotImplementedError
