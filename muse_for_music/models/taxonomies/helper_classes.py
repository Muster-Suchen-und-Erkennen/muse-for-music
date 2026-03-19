import re
from collections import OrderedDict
from csv import DictReader, DictWriter
from logging import Logger
from typing import ClassVar, List, Sequence, Type, Union

from sqlalchemy.orm import Mapped, MappedColumn, selectinload
from sqlalchemy.sql import select
from typing_extensions import Self

from ... import db
from ..helper_classes import GetByID


class Taxonomy(GetByID):

    taxonomy_type: ClassVar[str]
    select_multiple: ClassVar[bool] = False
    display_name: ClassVar[str | None] = None
    specification: ClassVar[str | None] = None

    # common types
    name: MappedColumn[str]
    description: MappedColumn[str | None]

    def __init__(self, name: str, description: str | None) -> None:
        """Create new List Taxonomy object."""
        self.name = name
        self.description = description

    @classmethod
    def clear_all(cls, logger: Logger):
        q = select(cls)
        objects = db.session.execute(q).scalars().all()
        for obj in objects:
            db.session.delete(obj)
        db.session.commit()

    @classmethod
    def load(cls, input_data: DictReader, logger: Logger):
        raise NotImplementedError

    @classmethod
    def save(cls, output_data: DictWriter, logger: Logger):
        raise NotImplementedError

    @classmethod
    def items(cls) -> Union[Sequence[Self], Self, None]:
        raise NotImplementedError

    @classmethod
    def not_applicable_item(cls):
        q = select(cls).where(cls.name == "na").limit(1)
        return db.session.execute(q).scalar_one_or_none()


class ListTaxonomy(Taxonomy):
    """Base class for list taxonomies."""

    taxonomy_type = "list"

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<{} "{}">'.format(type(self).__name__, self.name)

    @classmethod
    def get_all(cls: Type[Self]) -> Sequence[Self]:
        """Get all elements of taxonomy."""
        q = select(cls).where(cls.name != "na")
        return db.session.execute(q).scalars().all()

    items = get_all

    @classmethod
    def load(cls, input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        items: OrderedDict[str, ListTaxonomy] = OrderedDict()
        row: dict[str, str]
        for row in input_data:
            name: str = row["name"]
            description: str | None = row.get("description")
            if name.upper() == "ROOT":
                continue
            if name in items:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but name is already used.', name)
                break
            items[name] = cls(name=name, description=description)
        else:
            for value in items.values():
                db.session.add(value)
            db.session.commit()
            return
        logger.error('Taxonomy "{}" could not be loaded!'.format(cls.__name__))

    @classmethod
    def save(cls, output_data: DictWriter, logger: Logger):
        output_data.writeheader()
        output_data.writerow(
            {
                "name": "root",
                "parent": "",
                "description": "",
            }
        )
        items = cls.get_all()
        names = set()
        for item in items:
            if item.name in names:
                logger.warning('An item with name "%s" was already exported!', item.name)
            names.add(item.name)
            output_data.writerow(
                {
                    "name": item.name,
                    "parent": "root",
                    "description": item.description,
                }
            )


class TreeTaxonomy(Taxonomy):
    """Base class for tree taxonomies."""

    taxonomy_type = "tree"
    select_leafs_only = False

    # common types
    parent_id: MappedColumn[int | None]
    parent: Mapped[Self | None]
    children: Mapped[List[Self]]

    _eager_load = ["children"]

    def __init__(
        self, name: str, description: str | None = None, parent: Self | None = None
    ) -> None:
        """Create new TreeTaxonomy object."""
        self.parent = parent
        super().__init__(name=name, description=description)

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<{} "{}", children {}>'.format(
            type(self).__name__, self.name, [child.__repr__() for child in self.children]
        )

    @classmethod
    def get_root(cls: Type[Self]) -> Self | None:
        """Get root node of taxonomy."""
        # loading all items with recursion depth 1 and then selecting the root
        # in python is faster than recursively loading the children
        q = select(cls).options(selectinload(cls.children, recursion_depth=1))
        all_items = db.session.execute(q).scalars().all()
        for item in all_items:
            if item.name == "root":
                return item
        return None

    items = get_root

    @classmethod
    def load(cls, input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        pattern = re.compile(r"^(\d+|\(\d+\)|\[\d+\]|\{\d+\}|<\d+>),?\s+")
        items: OrderedDict[str, TreeTaxonomy] = OrderedDict()
        for row in input_data:
            name: str = row["name"]
            description: str | None = row.get("description")
            if name in items:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but "%r" is already used.', name, items[name])
                break
            if not row.get("parent"):
                items[name] = cls(name=pattern.sub("", name))
            else:
                parent_name = row["parent"]
                if parent_name not in items:
                    logger.warning(
                        'Child "%s" defined before Parent "%s"!', name, parent_name
                    )
                    break
                parent = items[parent_name]
                items[name] = cls(
                    name=pattern.sub("", name), parent=parent, description=description
                )
        else:
            for value in items.values():
                db.session.add(value)
            db.session.commit()
            return
        logger.error('Taxonomy "{}" could not be loaded!'.format(cls.__name__))

    @classmethod
    def save(cls, output_data: DictWriter, logger: Logger):
        output_data.writeheader()
        stack = []
        stack.append(cls.get_root())
        names = {}
        name_mappings = {}
        while len(stack) > 0:
            item = stack.pop()
            count = names.get(item.name, 0) + 1
            names[item.name] = count
            if count == 1:
                name_mappings[item.id] = item.name
            else:
                name_mappings[item.id] = "({count}) {name}".format(
                    count=count, name=item.name
                )
            output_data.writerow(
                {
                    "name": name_mappings.get(item.id, item.name),
                    "parent": (
                        ""
                        if item.name.upper() == "ROOT"
                        else name_mappings.get(item.parent.id, item.parent.name)
                    ),
                    "description": item.description,
                }
            )
            for child in reversed(item.children):
                stack.append(child)
