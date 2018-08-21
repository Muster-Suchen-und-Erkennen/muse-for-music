from ... import db
from ..taxonomies import AmbitusEinbettung, AmbitusEntwicklung, Melodiebewegung
from ..helper_classes import GetByID, UpdateableModelMixin


class DramaturgicContext(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('ambitus_context_before', AmbitusEinbettung),
                          ('melodic_line_before', Melodiebewegung),
                          ('ambitus_change_before', AmbitusEntwicklung),
                          ('ambitus_change_after', AmbitusEntwicklung),
                          ('melodic_line_after', Melodiebewegung),
                          ('ambitus_context_after', AmbitusEinbettung))

    __tablename__ = 'dramaturgic_context'
    id = db.Column(db.Integer, primary_key=True)
    ambitus_context_before_id = db.Column(db.Integer, db.ForeignKey('ambitus_einbettung.id'), nullable=True)
    ambitus_context_after_id = db.Column(db.Integer, db.ForeignKey('ambitus_einbettung.id'), nullable=True)
    ambitus_change_before_id = db.Column(db.Integer, db.ForeignKey('ambitus_entwicklung.id'), nullable=True)
    ambitus_change_after_id = db.Column(db.Integer, db.ForeignKey('ambitus_entwicklung.id'), nullable=True)
    melodic_line_before_id = db.Column(db.Integer, db.ForeignKey('melodiebewegung.id'), nullable=True)
    melodic_line_after_id = db.Column(db.Integer, db.ForeignKey('melodiebewegung.id'), nullable=True)

    ambitus_context_before = db.relationship(AmbitusEinbettung, foreign_keys=[ambitus_context_before_id])
    ambitus_context_after = db.relationship(AmbitusEinbettung, foreign_keys=[ambitus_context_after_id])
    ambitus_change_before = db.relationship(AmbitusEntwicklung, foreign_keys=[ambitus_change_before_id])
    ambitus_change_after = db.relationship(AmbitusEntwicklung, foreign_keys=[ambitus_change_after_id])
    melodic_line_before = db.relationship(Melodiebewegung, foreign_keys=[melodic_line_before_id])
    melodic_line_after = db.relationship(Melodiebewegung, foreign_keys=[melodic_line_after_id])
