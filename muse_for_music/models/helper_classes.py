from typing import TypeVar, Sequence, Dict, Type, List, Union, cast
from logging import Logger
from .. import db, app
from sqlalchemy.orm import joinedload, subqueryload, Query
from datetime import datetime, date
from flask_restplus.errors import ValidationError

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
    def get_by_id_or_dict(cls: Type[X], id: Union[int, dict, X]) -> X:
        if isinstance(id, cls):  # for lazy direct object passing
            return id
        if isinstance(id, dict):  # for lazy dict passing
            print(cls.__name__)
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


class UpdateableModelMixin():

    _normal_attributes = tuple()  # type: Tuple[Tuple(str,Type)]
    _reference_only_attributes = tuple()  # type: Tuple[str]
    _list_attributes = tuple()  # type: Tuple[str]

    def _update_normal_attributes(self, new_values: Dict):
        for name, cls in self._normal_attributes:
            if name not in new_values:
                print('HI_'*1000)
                raise ValidationError("'{}' is a required property".format(name))
            value = new_values[name]
            if issubclass(cls, UpdateableModelMixin):
                attr_to_update = getattr(self, name)  # type: UpdateableModelMixin
                if value is None:
                    setattr(self, name, None)
                    if attr_to_update is not None:
                        db.session.delete(attr_to_update)
                elif attr_to_update is None:
                    try:
                        attr_to_update = cls()
                        setattr(self, name, attr_to_update)
                        db.session.add(attr_to_update)
                        if name not in self._reference_only_attributes:
                            attr_to_update.update(value)
                    except Exception as e:
                        logger = app.logger  # type: Logger
                        logger.exception("Failed to auto instantiate class %s on update of %s",
                                         cls.__name__, self.__class__.__name__)
                else:
                    if name not in self._reference_only_attributes:
                        attr_to_update.update(value)
            elif issubclass(cls, GetByID):
                if value is None:
                    setattr(self, name, None)
                    continue
                cls = cast(GetByID, cls)
                resolved_value = cls.get_by_id_or_dict(value)
                setattr(self, name, resolved_value)
            elif cls in (int, float, str, bool):
                setattr(self, name, value)
            elif cls is date:
                if value is None:
                    setattr(self, name, None)
                    continue
                parsed_value = datetime.strptime(value, '%Y-%m-%d')
                parsed_date = parsed_value.date()
                setattr(self, name, parsed_date)

    def _update_list_attributes(self, new_values: Dict):
        for name in self._list_attributes:
            if name not in new_values:
                raise ValidationError("'{}' is a required property".format(name))
            value = new_values[name]
            setattr(self, name, value)

    def update(self, new_values: Dict):
        self._update_normal_attributes(new_values)
        self._update_list_attributes(new_values)
        db.session.add(self)


K = TypeVar('K', bound=GetByID)
V = TypeVar('V', bound=GetByID)
W = TypeVar('W', bound=UpdateableModelMixin)


class UpdateListMixin():

    def _update_reference_only_list(self, item_list: Union[Sequence[int],
                                    Sequence[dict]], old_items: Dict[int, K],
                                    mapping_cls: Type[K], item_cls: Type[V],
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

    def _update_updateable_model_list(self, item_list: Sequence[dict],
                                      old_items: Dict[int, W],
                                      item_cls: Type[W]):
        to_add = []  # type: List[W]

        for item_dict in item_list:
            item_id = item_dict.get('id')
            if item_id in old_items:
                old_items[item_id].update(item_dict)
                del old_items[item_id]
            else:
                new_item = item_cls(self, item_dict)  # type: W
                db.session.add(new_item)
                to_add.append(new_item)

        for item in to_add:
            db.session.add(item)
        to_delete = list(old_items.values())  # type: List[W]
        for item in to_delete:
            db.session.delete(item)

    def update_list(self, item_list: Union[Sequence[int], Sequence[dict]],
                    old_items: Dict[int, Union[K, W]], mapping_cls: Union[Type[K], Type[W]],
                    item_cls: Type[V] = None, mapping_cls_attribute: str = None):

        if mapping_cls, UpdateableModelMixin:
            self._update_updateable_model_list(item_list, old_items, mapping_cls)
        elif issubclass(item_cls, GetByID) and item_cls is not None and mapping_cls_attribute:
            self._update_reference_only_list(item_list, old_items, mapping_cls,
                                             item_cls, mapping_cls_attribute)
        else:
            raise TypeError('Either mapping_cls was not an UpdateableModelMixin or too few Arguments were provided!')
