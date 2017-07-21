from csv import DictReader
from logging import Logger
from ... import db

from typing import Dict, List


class LoadableMixin():

    @classmethod
    def clear_all(cls, logger: Logger):
        objects = cls.query.all()
        for obj in objects:
            db.session.delete(obj)
        db.session.commit()

    @classmethod
    def load(cls, input_data: DictReader, logger: Logger):
        NotImplementedError


class ListTaxonomy(LoadableMixin):
    """Base class for list taxonomies."""

    def __init__(self, name: str) -> None:
        """Create new List Taxonomy object."""
        self.name = name

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<{} "{}">'.format(type(self).__name__, self.name)

    @classmethod
    def load(cls, input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        items = {}  # type: Dict[str, ListTaxonomy]
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


class TreeTaxonomy(LoadableMixin):
    """Base class for tree taxonomies."""

    children = []  # type: List[TreeTaxonomy]

    def __init__(self, name: str, parent: 'TreeTaxonomy'=None) -> None:
        """Create new TreeTaxonomy object."""
        self.name = name
        self.parent = parent

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<{} "{}", children {}>'.format(type(self).__name__, self.name,
                                               [child.__repr__() for child in self.children])

    @classmethod
    def get_root(cls):
        """Get root node of taxonomy."""
        return cls.query.filter_by(name='root').first()

    @classmethod
    def load(cls, input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        items = {}  # type: Dict[str, TreeTaxonomy]
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
