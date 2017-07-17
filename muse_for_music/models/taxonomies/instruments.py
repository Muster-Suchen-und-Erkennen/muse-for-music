from csv import DictReader
from logging import Logger
from ... import db
from .loadable_mixin import LoadableMixin

from typing import Dict


class Instrument(db.Model, LoadableMixin):
    """DB Model for instruments."""

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('instrument.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    children = db.relationship('Instrument',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )

    def __init__(self, name: str, parent: 'Instrument'=None) -> None:
        """Create new Instrument object."""
        self.name = name
        self.parent = parent

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<Instrument {}, children {}>'.format(self.name, [child.__repr__() for child in self.children])

    @staticmethod
    def get_root():
        """Get root node of taxonomy."""
        return Instrument.query.filter_by(name='root').first()

    @staticmethod
    def load(input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        instruments = {}  # type: Dict[str, Instrument]
        for row in input_data:
            name = row['name']
            if name in instruments:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but "%r" is already used.',
                               name, instruments[name])
                break
            if not row.get('parent'):
                instruments[name] = Instrument(name)
            else:
                parent_name = row['parent']
                if parent_name not in instruments:
                    logger.warning('Child "%s" defined before Parent "%s"!',
                                   name, parent_name)
                    break
                parent = instruments[parent_name]
                instruments[name] = Instrument(name, parent)
        else:
            for name, value in instruments.items():
                db.session.add(value)
            db.session.commit()
            return
        logger.error('Taxonomy "Instrument" could not be loaded!')
