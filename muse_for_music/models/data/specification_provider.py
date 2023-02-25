from ... import db
from ..taxonomies import SpecAnteil, SpecAuftreten
from ..helper_classes import GetByID, UpdateListMixin, UpdateableModelMixin

from typing import Union, Sequence

class SpecificationProviderMixin():
    def __init_subclass__(cls) -> None:
        
        tablename = cls.__tablename__

        class Specification (db.Model, GetByID, UpdateListMixin, UpdateableModelMixin):
            _normal_attributes = (('share', SpecAnteil),
                                ('occurence', SpecAuftreten),
                                ('path', str))
            
            # _list_attributes = (('spezifikation_instrument'))

            __tablename__ = tablename + '_specification'

            id = db.Column(db.Integer, primary_key=True)
            path = db.Column(db.Text)
            parent_id = db.Column(db.Integer, db.ForeignKey(tablename + '.id'))
            share_id = db.Column(db.Integer, db.ForeignKey(SpecAnteil.id), nullable=True)
            occurence_id = db.Column(db.Integer, db.ForeignKey(SpecAuftreten.id), nullable=True)

            share = db.relationship(SpecAnteil, lazy='joined')
            occurence = db.relationship(SpecAuftreten, lazy='joined')

            parent = db.relationship(cls, backref=db.backref('_specifications', lazy='joined', single_parent=True, cascade='all, delete-orphan'),
                            foreign_keys=[parent_id])
            
            def __init__(self, parent, **kwargs) -> None:
                super().__init__()
                self.parent = parent
                if kwargs:
                    self.update(kwargs)

            # @property
            # def spezifikation_instrument(self):
            #     return [mapping.spezifikation_instrument for mapping in self._spezifikation_instrument]

            # @spezifikation_instrument.setter
            # def spezifikation_instrument(self, spezifikation_instrument_list:Union[Sequence[int], Sequence[dict]]):
            #     old_items = {mapping.spezifikation_instrument.id: mapping for mapping in self._spezifikation_instrument}
            #     self.update_list(spezifikation_instrument_list, old_items, SpecInstrumentToSpecification,
            #                     SpecInstrument, 'spezifikation_instrument')


        # class SpecInstrumentToSpecification(db.Model):

        #     __tablename__ = tablename + '_spec_instrument_to_specification'

        #     specifications_id = db.Column(db.Integer, db.ForeignKey('specifications.id'), primary_key=True)
        #     spezifikation_instrument_id = db.Column(db.Integer, db.ForeignKey('spezifikation_instrument.id'), primary_key=True)

        #     specifications = db.relationship(Specification, backref=db.backref('_spezifikation_instrument', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
        #     spezifikation_instrument = db.relationship('SpecInstrument')

        #     def __init__(self, specifications, spezifikation_instrument, **kwargs):
        #         self.specifications = specifications
        #         self.spezifikation_instrument = spezifikation_instrument

        cls._Specification = Specification

    @property
    def specifications(self):
        return self._specifications

    @specifications.setter
    def specifications(self, specifications_list:Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.id: mapping for mapping in self._specifications}
        self.update_list(specifications_list, old_items, self._Specification)