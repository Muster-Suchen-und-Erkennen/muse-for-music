from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy


class HarmonischeEntwicklung(db.Model, TreeTaxonomy):
    """DB Model for harmonic modulation."""

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('harmonische_entwicklung.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    children = db.relationship('HarmonischeEntwicklung',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )
