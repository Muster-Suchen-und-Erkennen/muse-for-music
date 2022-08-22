from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = ['AmbitusEntwicklung', 'AmbitusEinbettung']


class AmbitusEntwicklung(db.Model, TreeTaxonomy):
    """DB Model for ambitus change."""
    __tablename__ = 'ambitus_entwicklung'

    display_name = 'Ambitus-Entwicklung'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('ambitus_entwicklung.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('AmbitusEntwicklung',
                               passive_deletes='all',
                               lazy='joined',
                               join_depth=8,
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='select',
                                                  join_depth=1
                                                 )
                              )


class AmbitusEinbettung(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'ambitus_einbettung'

    display_name = 'Ambitus-Einbettung'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
