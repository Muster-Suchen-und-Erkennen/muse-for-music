from datetime import date, datetime
from logging import Logger
from typing import (
    ClassVar,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)

from flask import current_app
from flask_restx.errors import ValidationError
from flask_sqlalchemy.model import Model
from sqlalchemy.orm import selectinload, MappedColumn
from sqlalchemy.sql import Select, select
from typing_extensions import Self

from .. import db

ModelBase: TypeAlias = Model
X = TypeVar("X", bound=ModelBase)


class GetByID:

    _eager_load: ClassVar[Union[List[str], Tuple[str, ...]]] = tuple()

    id: MappedColumn[int]

    @classmethod
    def prepare_query(cls: Type[Self], lazy: bool = False) -> Select[Tuple[Self]]:
        q = select(cls)
        if lazy:
            return q
        options = []
        for attr in cls._eager_load:
            column = getattr(cls, attr)
            options.append(selectinload(column))

        if options:
            q = q.options(*options)
        return q

    @staticmethod
    def get_id_from_object(id_: Union[int, dict, X]) -> int:
        if isinstance(id_, GetByID):  # for lazy direct object passing
            return id_.id
        if isinstance(id_, dict):  # for lazy dict passing
            return id_["id"]
        if isinstance(id_, int):
            if id_ < 0:  # no negative ids in system (all negative ids mapped to -1)
                return -1
            return id_
        if id_ is None:  # None object is associated with negative id
            return -1
        raise TypeError(
            '"id" is of wrong type. Expected: int, dict or {}, Got {}'.format(
                GetByID, type(id_)
            )
        )

    @classmethod
    def get_by_id_or_dict(
        cls: Type[Self], id_: Union[int, dict, Self], lazy: bool = False
    ) -> Optional[Self]:
        if isinstance(id_, cls):  # for lazy direct object passing
            return id_
        if isinstance(id_, dict):  # for lazy dict passing
            id_ = id_["id"]
        assert isinstance(id_, int)
        return cls.get_by_id(id_, lazy)

    @classmethod
    def get_by_id(cls: Type[Self], id_: int, lazy: bool = False) -> Optional[Self]:
        if id_ < 0:
            return None
        query = cls.prepare_query(lazy).where(cls.id == id_)
        return db.session.execute(query).scalar_one_or_none()

    @classmethod
    def get_list_by_id(
        cls: Type[Self], ids: Sequence[int], lazy: bool = True
    ) -> Sequence[Self]:
        if not ids:
            return []
        if len(ids) == 1:
            result = cls.get_by_id(ids[0], lazy)
            return [result] if result is not None else []
        query = cls.prepare_query(lazy).where(cls.id.in_(ids))
        return db.session.execute(query).scalars().all()

    @classmethod
    def get_multiple_by_id(
        cls: Type[Self], ids: Sequence[int], lazy: bool = True
    ) -> Dict[int, Self]:
        if not ids:
            return {}
        if len(ids) == 1:
            result = cls.get_by_id(ids[0], lazy)
            if result is None:
                return {}
            return {result.id: result}
        query = cls.prepare_query(lazy).where(cls.id.in_(ids))
        result = db.session.execute(query).scalars().all()
        return {obj.id: obj for obj in result}


class UpdateableModelMixin:

    _normal_attributes: Tuple[Tuple[str, Type], ...] = tuple()
    _reference_only_attributes: Tuple[str, ...] = tuple()
    _optional_attributes: Tuple[str, ...] = tuple()
    _list_attributes: Tuple[str, ...] = tuple()

    def _update_normal_attributes(  # noqa: C901
        self, new_values: Dict, partial: bool = False
    ):
        expire_self = False
        for name, cls in self._normal_attributes:
            self.check_for_required_attr(name, new_values, cls, partial)
            value = new_values.get(name)
            if issubclass(cls, UpdateableModelMixin) and (
                name not in self._reference_only_attributes
            ):
                expire_self = self.update_complex_object(name, value, cls, expire_self)
            elif issubclass(cls, GetByID):
                if value is None:
                    setattr(self, name, None)
                    continue
                cls = cast(GetByID, cls)
                if cls.get_id_from_object(getattr(self, name)) == cls.get_id_from_object(
                    value
                ):
                    # object already set!
                    continue
                resolved_value = cls.get_by_id_or_dict(value, True)
                setattr(self, name, resolved_value)
            elif cls in (int, float, str, bool):
                if getattr(self, name) != value:
                    setattr(self, name, value)
            elif cls is date:
                if value is None:
                    setattr(self, name, None)
                    continue
                parsed_value = datetime.strptime(value, "%Y-%m-%d")
                parsed_date = parsed_value.date()
                if getattr(self, name) != parsed_date:
                    setattr(self, name, parsed_date)
        if expire_self:
            db.session.expire(self)

    def check_for_required_attr(self, name, new_values, cls, partial: bool = False):
        if name not in new_values and name not in self._optional_attributes:
            if not partial:
                raise ValidationError(
                    "'{}' is a required property for class {}".format(
                        name, self.__class__
                    )
                )
            else:
                if issubclass(cls, str):
                    new_values.name = ""
                elif issubclass(cls, bool):
                    # bool check must happen before int
                    # as bool is subclass of int
                    new_values = False
                elif issubclass(cls, int):
                    new_values = -1
                elif issubclass(cls, float):
                    new_values = -1
                else:
                    raise ValidationError("'{}' is a required property".format(name))

    def update_complex_object(self, name, value, cls, expire_self):
        attr_to_update: UpdateableModelMixin = getattr(self, name)
        if value is None:
            setattr(self, name, None)
            if attr_to_update is not None:
                db.session.delete(attr_to_update)
                expire_self = True
        elif attr_to_update is None:
            try:
                attr_to_update = cls()
                setattr(self, name, attr_to_update)
                db.session.add(attr_to_update)
                attr_to_update.update(value)
            except Exception as e:
                print(type(e))
                logger: Logger = current_app.logger
                logger.exception(
                    "Failed to auto instantiate class %s on update of %s",
                    cls.__name__,
                    self.__class__.__name__,
                )
        else:
            attr_to_update.update(value)
        return expire_self

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


V = TypeVar("V", bound=GetByID)
W = TypeVar("W", bound=UpdateableModelMixin)


class UpdateListMixin:

    def _update_reference_only_list(
        self,
        item_list: Union[Sequence[int], Sequence[dict]],
        old_items: Mapping[int, X],
        mapping_cls: Type[X],
        item_cls: Type[V],
        mapping_cls_attribute: str,
    ):
        to_add: List[int] = []
        old_items = dict(old_items)

        for item in item_list:
            if isinstance(item, dict):
                item = item.get("id")
                if item is None:
                    continue
            item = cast(int, item)
            if item in old_items:
                del old_items[item]
            else:
                to_add.append(item)

        items_to_add: Sequence[V] = item_cls.get_list_by_id(to_add)
        to_delete: List[X] = list(old_items.values())
        item_to_add: V
        for item_to_add in items_to_add:
            if to_delete:
                mapping = to_delete.pop()
                setattr(mapping, mapping_cls_attribute, item_to_add)
            else:
                mapping = mapping_cls(self, item_to_add)  # type: ignore
                db.session.add(mapping)
        for mapping in to_delete:
            db.session.delete(mapping)
        if to_delete:
            db.session.expire(self)

    def _update_updateable_model_list(
        self, item_list: Sequence[dict], old_items: Mapping[int, W], item_cls: Type[W]
    ):
        old_items = dict(old_items)
        for item_dict in item_list:
            item_id = item_dict.get("id")
            if item_id in old_items:
                old_items[item_id].update(item_dict)
                db.session.add(old_items[item_id])
                del old_items[item_id]
            else:
                new_item: W = item_cls(self)  # type: ignore
                new_item.update(item_dict)
                db.session.add(new_item)

        to_delete: List[W] = list(old_items.values())
        for item in to_delete:
            db.session.delete(item)
        if to_delete:
            db.session.expire(self)

    def update_list(
        self,
        item_list: Union[Sequence[int], Sequence[dict], None],
        old_items: Mapping[int, X],
        mapping_cls: Type[X],
        item_cls: Type[V] | None = None,
        mapping_cls_attribute: str | None = None,
    ):

        # consider None an empty list
        if item_list is None:
            item_list = tuple()

        assert issubclass(mapping_cls, ModelBase)
        if issubclass(mapping_cls, UpdateableModelMixin):
            self._update_updateable_model_list(
                item_list,  # type: ignore
                old_items,  # type: ignore
                mapping_cls,
            )
        elif (
            item_cls is not None
            and issubclass(item_cls, GetByID)
            and mapping_cls_attribute
        ):
            self._update_reference_only_list(
                item_list,
                old_items,  # type: ignore
                mapping_cls,
                item_cls,
                mapping_cls_attribute,
            )
        else:
            raise TypeError(
                "Either mapping_cls was not an UpdateableModelMixin or too few Arguments were provided!"
            )
