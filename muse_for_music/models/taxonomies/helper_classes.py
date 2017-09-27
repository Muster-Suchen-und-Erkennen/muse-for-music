from csv import DictReader
from collections import OrderedDict
from logging import Logger
from ... import db
from ..helper_classes import GetByID, X
from typing import Dict, List, Sequence, Any, Type, TypeVar


class Taxonomy(GetByID):

    taxonomy_type = None  # type: str
    select_multiple = False  # type: bool
    radio_buttons = False  # type: bool

    def __init__(self, name: str, description: None) -> None:
        """Create new List Taxonomy object."""
        self.name = name
        self.description = description

    @classmethod
    def class_name(cls):
        print(cls, cls.__name__)
        return cls.__name__

    @classmethod
    def clear_all(cls, logger: Logger):
        objects = cls.query.all()
        for obj in objects:
            db.session.delete(obj)
        db.session.commit()

    @classmethod
    def load(cls, input_data: DictReader, logger: Logger):
        NotImplementedError

    @classmethod
    def items(cls):
        NotImplementedError


class ListTaxonomy(Taxonomy):
    """Base class for list taxonomies."""

    taxonomy_type = 'list'  # type: str

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<{} "{}">'.format(type(self).__name__, self.name)

    @classmethod
    def get_all(cls: Type[X]) -> List[X]:
        """Get all elements of taxonomy."""
        return cls.query.all()

    items = get_all

    @classmethod
    def load(cls, input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        items = OrderedDict()  # type: Dict[str, ListTaxonomy]
        for row in input_data:
            name = row['name']  # type: str
            if name.upper() == 'ROOT':
                continue
            if name in items:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but name is already used.',
                               name)
                break
            items[name] = cls(name=name)
        else:
            for name, value in items.items():
                db.session.add(value)
            db.session.commit()
            return
        logger.error('Taxonomy "{}" could not be loaded!'.format(cls.__name__))


class TreeTaxonomy(Taxonomy):
    """Base class for tree taxonomies."""

    taxonomy_type = 'tree'  # type: str
    select_leafs_only = False  # type: bool

    children = []  # type: List[TreeTaxonomy]

    def __init__(self, name: str, description=None, parent: 'TreeTaxonomy'=None) -> None:
        """Create new TreeTaxonomy object."""
        self.parent = parent
        super().__init__(name=name, description=description)

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<{} "{}", children {}>'.format(type(self).__name__, self.name,
                                               [child.__repr__() for child in self.children])

    @classmethod
    def get_root(cls: Type[X]) -> X:
        """Get root node of taxonomy."""
        return cls.query.filter_by(name='root').first()

    items = get_root

    @classmethod
    def load(cls, input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        items = OrderedDict  # type: Dict[str, TreeTaxonomy]
        for row in input_data:
            name = row['name']  # type: str
            if name in items:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but "%r" is already used.',
                               name, items[name])
                break
            if not row.get('parent'):
                items[name] = cls(name=name)
            else:
                parent_name = row['parent']
                if parent_name not in items:
                    logger.warning('Child "%s" defined before Parent "%s"!',
                                   name, parent_name)
                    break
                parent = items[parent_name]
                items[name] = cls(name=name, parent=parent)
        else:
            for name, value in items.items():
                db.session.add(value)
            db.session.commit()
            return
        logger.error('Taxonomy "{}" could not be loaded!'.format(cls.__name__))
