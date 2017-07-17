from csv import DictReader
from logging import Logger
from ... import db
from .loadable_mixin import LoadableMixin

from typing import Dict


class AuftretenWerkausschnitt(db.Model, LoadableMixin):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name: str) -> None:
        """Create new AuftretenWerkausschnitt object."""
        self.name = name

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<AuftretenWerkausschnitt {}>'.format(self.name)

    @staticmethod
    def load(input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        choices = {}  # type: Dict[str, AuftretenWerkausschnitt]
        for row in input_data:
            name = row['name']
            if name in choices:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but name is already used.',
                               name)
                break
            choices[name] = AuftretenWerkausschnitt(name)
        else:
            for name, value in choices.items():
                db.session.add(value)
            db.session.commit()
            return
        logger.error('Taxonomy "AuftretenWerkausschnitt" could not be loaded!')


class AuftretenSatz(db.Model, LoadableMixin):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name: str) -> None:
        """Create new AuftretenSatz object."""
        self.name = name

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<AuftretenSatz {}>'.format(self.name)

    @staticmethod
    def load(input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        choices = {}  # type: Dict[str, AuftretenSatz]
        for row in input_data:
            name = row['name']
            if name in choices:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but name is already used.',
                               name)
                break
            choices[name] = AuftretenSatz(name)
        else:
            for name, value in choices.items():
                db.session.add(value)
            db.session.commit()
            return
        logger.error('Taxonomy "AuftretenSatz" could not be loaded!')


class Anteil(db.Model, LoadableMixin):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name: str) -> None:
        """Create new Auftreten object."""
        self.name = name

    def __repr__(self):
        """Get repr of taxonomy."""
        return '<Anteil {}>'.format(self.name)

    @staticmethod
    def load(input_data: DictReader, logger: Logger):
        """Load taxonomy from csv file."""
        choices = {}  # type: Dict[str, Anteil]
        for row in input_data:
            name = row['name']
            if name in choices:
                logger.warning('Duplicate names are not allowed! \
                                Found "%s" but name is already used.',
                               name)
                break
            choices[name] = Anteil(name)
        else:
            for name, value in choices.items():
                db.session.add(value)
            db.session.commit()
            return
        logger.error('Taxonomy "Anteil" could not be loaded!')
