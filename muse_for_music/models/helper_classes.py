from typing import TypeVar, Sequence, Dict, Type, List, Union, cast
from .. import db

X = TypeVar('X', bound=db.Model)


class GetByID():

    @classmethod
    def get_by_id(cls: Type[X], id: int) -> X:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_list_by_id(cls: Type[X], ids: Sequence[int]) -> List[X]:
        return cls.query.filter(cls.id.in_(ids))

    @classmethod
    def get_multiple_by_id(cls: Type[X], ids: Sequence[int]) -> Dict[int, X]:
        result = cls.query.filter(cls.id.in_(ids))
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
