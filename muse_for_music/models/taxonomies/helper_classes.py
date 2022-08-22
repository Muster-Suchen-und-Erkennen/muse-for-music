from csv import DictReader, DictWriter
from collections import OrderedDict
from logging import Logger
import re
from ... import db
from ..helper_classes import GetByID, X
from typing import Dict, List, Sequence, Any, Type, TypeVar


class Taxonomy(GetByID):

    taxonomy_type = None  # type: str
    select_multiple = False  # type: bool
    display_name = None  # type: str

    def __init__(self, name: str, description: None) -> None:
        """Create new List Taxonomy object."""
        self.name = name
        self.description = description

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
    def save(cls, output_data: DictWriter, logger: Logger):
        NotImplementedError

    @classmethod
    def items(cls):
        NotImplementedError

    @classmethod
    def not_applicable_item(cls):
        return cls.query.filter_by(name='na').first()


class ListTaxonomy(Taxonomy):
    """Base class for list taxonomies."""

    taxonomy_type = 'list'  # type: str

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<{} "{}">'.format(type(self).__name__, self.name)

    @classmethod
    def get_all(cls: Type[X]) -> List[X]:
        """Get all elements of taxonomy."""
        return cls.query.filter(cls.name != 'na').all()

    items = get_all

    @classmethod
    def load(cls, input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        items = OrderedDict()  # type: Dict[str, ListTaxonomy]
        for row in input_data:
            name = row['name']  # type: str
            description = row.get('description')  # type: str
            if name.upper() == 'ROOT':
                continue
            if name in items:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but name is already used.',
                               name)
                break
            items[name] = cls(name=name, description=description)
        else:
            for name, value in items.items():
                db.session.add(value)
            db.session.commit()
            return
        logger.error('Taxonomy "{}" could not be loaded!'.format(cls.__name__))

    @classmethod
    def save(cls, output_data: DictWriter, logger: Logger):
        output_data.writeheader()
        output_data.writerow({
            'name': 'root',
            'parent': '',
            'description': '',
        })
        items = cls.get_all()
        names = set()
        for item in items:
            if item.name in names:
                logger.warning('An item with name "%s" was already exported!', name)
            names.add(item.name)
            output_data.writerow({
                'name': item.name,
                'parent': 'root',
                'description': item.description,
            })



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
        pattern = re.compile(r'^(\d+|\(\d+\)|\[\d+\]|\{\d+\}|<\d+>),?\s+')
        items = OrderedDict()  # type: Dict[str, TreeTaxonomy]
        for row in input_data:
            name = row['name']  # type: str
            description = row.get('description')  # type: str
            if name in items:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but "%r" is already used.',
                               name, items[name])
                break
            if not row.get('parent'):
                items[name] = cls(name=pattern.sub('', name))
            else:
                parent_name = row['parent']
                if parent_name not in items:
                    logger.warning('Child "%s" defined before Parent "%s"!',
                                   name, parent_name)
                    break
                parent = items[parent_name]
                items[name] = cls(name=pattern.sub('', name), parent=parent, description=description)
        else:
            for name, value in items.items():
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
                name_mappings[item.id] = '({count}) {name}'.format(count=count, name=item.name)
            output_data.writerow({
                'name': name_mappings.get(item.id, item.name),
                'parent': '' if item.name.upper() == 'ROOT' else name_mappings.get(item.parent.id, item.parent.name),
                'description': item.description,
            })
            for child in reversed(item.children):
                stack.append(child)
