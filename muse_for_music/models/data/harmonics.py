from ... import db
from ..taxonomies import Frequenz, Grundton, Tonalitaet, HarmonischeFunktion, \
                         HarmonischeEntwicklung, HarmonischeKomplexitaet, \
                         HarmonischeStufe, HarmonischeFunktionVerwandschaft, \
                         HarmonischePhaenomene, Akkord, Dissonanzen, Dissonanzgrad, \
                         HarmonischeDichte, AnzahlMelodietoene
from ..helper_classes import GetByID, UpdateListMixin, UpdateableModelMixin

from typing import Union, Sequence, List


class Harmonics(db.Model, GetByID, UpdateListMixin, UpdateableModelMixin):

    _normal_attributes = (('degree_of_dissonance', Dissonanzgrad),
                          ('harmonic_density', HarmonischeDichte),
                          ('harmonic_complexity', HarmonischeKomplexitaet),
                          #('harmonische_funktion', HarmonischeFunktionVerwandschaft),
                          ('harmonic_analyse', str),)

    _list_attributes = ('harmonic_centers', 'harmonic_changes', 'harmonic_phenomenons', 'dissonances', 'chords', 'harmonische_funktion')

    __tablename__ = 'harmonics'
    id = db.Column(db.Integer, primary_key=True)
    #harmonic_function_modulation_id = db.Column(db.Integer, db.ForeignKey('harmonische_funktion_verwandschaft.id'))
    degree_of_dissonance_id = db.Column(db.Integer, db.ForeignKey('dissonanzgrad.id'))
    harmonic_density_id = db.Column(db.Integer, db.ForeignKey('harmonische_dichte.id'))
    harmonic_complexity_id = db.Column(db.Integer, db.ForeignKey('harmonische_komplexitaet.id'))
    harmonic_analyse = db.Column(db.Text, nullable=True)

    #harmonische_funktion = db.relationship('HarmonischeFunktionVerwandschaft', lazy='joined')
    degree_of_dissonance = db.relationship('Dissonanzgrad', lazy='joined')
    harmonic_density = db.relationship('HarmonischeDichte', lazy='joined')
    harmonic_complexity = db.relationship('HarmonischeKomplexitaet', lazy='joined')

    @property
    def harmonic_centers(self):
        return self._harmonic_centers

    @harmonic_centers.setter
    def harmonic_centers(self, harmonic_centers_list: Sequence[dict]):
        old_items = {center.id: center for center in self._harmonic_centers}
        self.update_list(harmonic_centers_list, old_items, HarmonicCenter)

    @property
    def harmonic_phenomenons(self):
        return [mapping.harmonische_phaenomene for mapping in self._harmonic_phenomenons]

    @harmonic_phenomenons.setter
    def harmonic_phenomenons(self, harmonic_phenomenons_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.harmonische_phaenomene.id: mapping for mapping in self._harmonic_phenomenons}
        self.update_list(harmonic_phenomenons_list, old_items, HarmonischePhaenomeneToHarmonics,
                         HarmonischePhaenomene, 'harmonische_phaenomene')

    @property
    def harmonic_changes(self):
        return [mapping.harmonische_entwicklung for mapping in self._harmonic_changes]

    @harmonic_changes.setter
    def harmonic_changes(self, harmonic_changes_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.harmonische_entwicklung.id: mapping for mapping in self._harmonic_changes}
        self.update_list(harmonic_changes_list, old_items, HarmonischeEntwicklungToHarmonics,
                         HarmonischeEntwicklung, 'harmonische_entwicklung')

    @property
    def chords(self):
        return [mapping.akkord for mapping in self._special_chords]

    @chords.setter
    def chords(self, special_chords_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.akkord.id: mapping for mapping in self._special_chords}
        self.update_list(special_chords_list, old_items, AkkordToHarmonics,
                         Akkord, 'akkord')

    @property
    def dissonances(self):
        return [mapping.dissonanzen for mapping in self._dissonances]

    @dissonances.setter
    def dissonances(self, dissonances_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.dissonanzen.id: mapping for mapping in self._dissonances}
        self.update_list(dissonances_list, old_items, DissonanzenToHarmonics,
                         Dissonanzen, 'dissonanzen')

    @property
    def harmonische_funktion(self):
        return [mapping.harmonische_funktion for mapping in self._harmonische_funktion]

    @harmonische_funktion.setter
    def harmonische_funktion(self, harmonische_funktion_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.harmonische_funktion_verwandschaft.id: mapping for mapping in self._harmonische_funktion}
        self.update_list(harmonische_funktion_list, old_items, HarmonischeFunktionToHarmonics,
                         HarmonischeFunktionVerwandschaft, 'harmonische_funktion')



class HarmonicCenter(db.Model, UpdateableModelMixin):

    _normal_attributes = (('grundton', Grundton),
                          ('harmonische_stufe', HarmonischeStufe),
                          ('tonalitaet', Tonalitaet),
                          ('harmonische_funktion', HarmonischeFunktion))

    id = db.Column(db.Integer, primary_key=True)
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'))
    grundton_id = db.Column(db.Integer, db.ForeignKey('grundton.id'))
    tonalitaet_id = db.Column(db.Integer, db.ForeignKey('tonalitaet.id'))
    harmonische_funktion_id = db.Column(db.Integer, db.ForeignKey('harmonische_funktion.id'))
    harmonische_stufe_id = db.Column(db.Integer, db.ForeignKey('harmonische_stufe.id'))

    harmonics = db.relationship(Harmonics, backref=db.backref('_harmonic_centers', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    grundton = db.relationship('Grundton', lazy='joined')
    tonalitaet = db.relationship('Tonalitaet', lazy='joined')
    harmonische_funktion = db.relationship('HarmonischeFunktion', lazy='joined')
    harmonische_stufe = db.relationship('HarmonischeStufe', lazy='joined')

    def __init__(self, harmonics, **kwargs):
        self.harmonics = harmonics
        if kwargs:
            self.update(kwargs)


class HarmonischePhaenomeneToHarmonics(db.Model):
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), primary_key=True)
    harmonische_phaenomene_id = db.Column(db.Integer, db.ForeignKey('harmonische_phaenomene.id'), primary_key=True)

    harmonics = db.relationship(Harmonics, backref=db.backref('_harmonic_phenomenons', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    harmonische_phaenomene = db.relationship('HarmonischePhaenomene')

    def __init__(self, harmonics, harmonische_phaenomene, **kwargs):
        self.harmonics = harmonics
        self.harmonische_phaenomene = harmonische_phaenomene


class HarmonischeEntwicklungToHarmonics(db.Model):
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), primary_key=True)
    harmonische_entwicklung_id = db.Column(db.Integer, db.ForeignKey('harmonische_entwicklung.id'), primary_key=True)

    harmonics = db.relationship(Harmonics, backref=db.backref('_harmonic_changes', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    harmonische_entwicklung = db.relationship('HarmonischeEntwicklung')

    def __init__(self, harmonics, harmonische_entwicklung, **kwargs):
        self.harmonics = harmonics
        self.harmonische_entwicklung = harmonische_entwicklung


class AkkordToHarmonics(db.Model):
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), primary_key=True)
    akkord_id = db.Column(db.Integer, db.ForeignKey('akkord.id'), primary_key=True)

    harmonics = db.relationship(Harmonics, backref=db.backref('_special_chords', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    akkord = db.relationship('Akkord')

    def __init__(self, harmonics, akkord, **kwargs):
        self.harmonics = harmonics
        self.akkord = akkord


class DissonanzenToHarmonics(db.Model):
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), primary_key=True)
    dissonanzen_id = db.Column(db.Integer, db.ForeignKey('dissonanzen.id'), primary_key=True)

    harmonics = db.relationship(Harmonics, backref=db.backref('_dissonances', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    dissonanzen = db.relationship('Dissonanzen')

    def __init__(self, harmonics, dissonanzen, **kwargs):
        self.harmonics = harmonics
        self.dissonanzen = dissonanzen


class HarmonischeFunktionToHarmonics(db.Model):
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), primary_key=True)
    harmonic_function_modulation_id = db.Column(db.Integer, db.ForeignKey('harmonische_funktion_verwandschaft.id'))

    harmonics = db.relationship(Harmonics, backref=db.backref('_harmonische_funktion', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    harmonische_funktion = db.relationship('HarmonischeFunktionVerwandschaft')

    def __init__(self, harmonics, harmonische_funktion, **kwargs):
        self.harmonics = harmonics
        self.harmonische_funktion = harmonische_funktion
