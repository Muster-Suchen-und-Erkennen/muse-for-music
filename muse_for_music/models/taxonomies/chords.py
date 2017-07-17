from csv import DictReader
from logging import Logger
from ... import db
from .loadable_mixin import LoadableMixin

from typing import Dict


class Akkord(db.Model, LoadableMixin):
    """DB Model for chords."""

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('akkord.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    children = db.relationship('Akkord',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )

    def __init__(self, name: str, parent: 'Akkord'=None) -> None:
        """Create new Akkord object."""
        self.name = name
        self.parent = parent

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<Akkord {}, children {}>'.format(self.name, [child.__repr__() for child in self.children])

    @staticmethod
    def get_root():
        """Get root node of taxonomy."""
        return Akkord.query.filter_by(name='root').first()

    @staticmethod
    def load(input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        chords = {}  # type: Dict[str, Akkord]
        for row in input_data:
            name = row['name']
            if name in chords:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but "%r" is already used.',
                               name, chords[name])
                break
            if not row.get('parent'):
                chords[name] = Akkord(name)
            else:
                parent_name = row['parent']
                if parent_name not in chords:
                    logger.warning('Child "%s" defined before Parent "%s"!',
                                   name, parent_name)
                    break
                parent = chords[parent_name]
                chords[name] = Akkord(name, parent)
        else:
            for name, value in chords.items():
                db.session.add(value)
            db.session.commit()
            return
        logger.error('Taxonomy "Akkord" could not be loaded!')
