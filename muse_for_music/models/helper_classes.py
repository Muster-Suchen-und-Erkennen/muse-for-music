from typing import TypeVar, Sequence, Dict, Type
from .. import db

T = TypeVar('T', bound=db.Model)


class GetByID():

    @classmethod
    def get_by_id(cls: Type[T], id: int) -> T:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_multiple_by_id(cls: Type[T], ids: Sequence[int]) -> Dict[int, T]:
        result = cls.query.filter(cls.id.in_(ids))
        return {obj.id: obj for obj in result}
