from typing import TypeVar, Sequence, Dict, Type, List, Union, cast
from .. import db
from sqlalchemy.orm import joinedload, subqueryload, Query

X = TypeVar('X', bound=db.Model)


class GetByID():

    _joined_load = []  # type: List[str]
    _subquery_load = []  # type: List[str]

    @classmethod
    def prepare_query(cls: Type[X]) -> Query:
        query = cls.query
        options = []
        for attr in cls._joined_load:
            options.append(joinedload(attr))
        for attr in cls._subquery_load:
            options.append(subqueryload(attr))

        if options:
            query = query.options(*options)
        return query

    @classmethod
    def get_by_id_or_dict(cls: Type[X], id: Union[int, dict]) -> X:
        if isinstance(id, dict):  # for lazy dict passing
            id = id['id']
        return cls.get_by_id(id)

    @classmethod
    def get_by_id(cls: Type[X], id: int) -> X:
        query = cls.prepare_query()
        return query.filter_by(id=id).first()

    @classmethod
    def get_list_by_id(cls: Type[X], ids: Sequence[int]) -> List[X]:
        query = cls.prepare_query()
        return query.filter(cls.id.in_(ids)).all()

    @classmethod
    def get_multiple_by_id(cls: Type[X], ids: Sequence[int]) -> Dict[int, X]:
        query = cls.prepare_query()
        result = query.filter(cls.id.in_(ids)).all()
        return {obj.id: obj for obj in result}


K = TypeVar('K', bound=GetByID)
V = TypeVar('V', bound=GetByID)


class UpdateListMixin():

    def update_list(self, item_list: Union[Sequence[int], Sequence[dict]],
                    old_items: Dict[int, K], mapping_cls: Type[K], item_cls: Type[V],
                    mapping_cls_attribute: str):

        to_add = []  # type: List[int]

        for item in item_list:
            if isinstance(item, dict):
                item = item.get('id')
                if item is None:
                    continue
            item = cast(int, item)
            if item in old_items:
                del old_items[item]
            else:
                to_add.append(item)

        items_to_add = item_cls.get_list_by_id(to_add)  # type: List[V]
        to_delete = list(old_items.values())  # type: List[K]
        for item_to_add in items_to_add:  # type: V
            if to_delete:
                mapping = to_delete.pop()
                setattr(mapping, mapping_cls_attribute, item_to_add)
            else:
                mapping = mapping_cls(self, item_to_add)
                db.session.add(mapping)
        for mapping in to_delete:
            db.session.delete(mapping)
