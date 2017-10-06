from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy


__all__ = ['HarmonischeEntwicklung', 'Tonalitaet', 'HarmonischeFunktion',
           'HarmonischeStufe', 'HarmonischeFunktionVerwandschaft',
           'HarmonischePhaenomene', 'HarmonischeKomplexitaet']


class HarmonischeEntwicklung(db.Model, TreeTaxonomy):
    """DB Model for harmonic modulation."""

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('harmonische_entwicklung.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('HarmonischeEntwicklung',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class Tonalitaet(db.Model, TreeTaxonomy):
    """DB Model for tonality."""
    __tablename__ = 'tonalitaet'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('tonalitaet.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Tonalitaet',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class HarmonischeFunktion(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'harmonische_funktion'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class HarmonischeStufe(db.Model, TreeTaxonomy):
    """DB Model for harmonic level."""
    __tablename__ = 'harmonische_stufe'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('harmonische_stufe.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('HarmonischeStufe',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class HarmonischeFunktionVerwandschaft(db.Model, TreeTaxonomy):
    """DB Model for harmonic function Verwandschaft."""
    __tablename__ = 'harmonische_funktion_verwandschaft'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('harmonische_funktion_verwandschaft.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('HarmonischeFunktionVerwandschaft',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class HarmonischePhaenomene(db.Model, TreeTaxonomy):
    """DB Model for harmonic phenomenons."""
    __tablename__ = 'harmonische_phaenomene'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('harmonische_phaenomene.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('HarmonischePhaenomene',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class HarmonischeKomplexitaet(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'harmonische_komplexitaet'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
