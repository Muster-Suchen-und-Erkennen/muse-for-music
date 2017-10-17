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
                          ('nr_of_different_chords_per_measure', float),
                          ('harmonic_density', HarmonischeDichte),
                          ('nr_of_melody_tones_per_harmony', float),
                          ('melody_tones_in_melody_one_id', AnzahlMelodietoene),
                          ('melody_tones_in_melody_two_id', AnzahlMelodietoene),
                          ('harmonic_rythm_is_static', bool),
                          ('harmonic_rythm_follows_rule', bool),
                          ('harmonic_complexity', HarmonischeKomplexitaet),
                          ('harmonische_funktion', HarmonischeFunktionVerwandschaft))

    _list_attributes = ('harmonic_centers', 'harmonic_changes', 'harmonic_phenomenons', 'dissonances')

    __tablename__ = 'harmonics'
    id = db.Column(db.Integer, primary_key=True)
    harmonic_function_modulation_id = db.Column(db.Integer, db.ForeignKey('harmonische_funktion_verwandschaft.id'))
    degree_of_dissonance_id = db.Column(db.Integer, db.ForeignKey('dissonanzgrad.id'))
    nr_of_different_chords_per_measure = db.Column(db.Float)
    harmonic_density_id = db.Column(db.Integer, db.ForeignKey('harmonische_dichte.id'))
    harmonic_complexity_id = db.Column(db.Integer, db.ForeignKey('harmonische_komplexitaet.id'))
    nr_of_melody_tones_per_harmony = db.Column(db.Float)
    melody_tones_in_melody_one_id = db.Column(db.Integer, db.ForeignKey('anzahl_melodietoene.id'))
    melody_tones_in_melody_two_id = db.Column(db.Integer, db.ForeignKey('anzahl_melodietoene.id'))
    harmonic_rythm_is_static = db.Column(db.Boolean, default=False)
    harmonic_rythm_follows_rule = db.Column(db.Boolean, default=False)

    harmonische_funktion = db.relationship('HarmonischeFunktionVerwandschaft', lazy='joined')
    degree_of_dissonance = db.relationship('Dissonanzgrad', lazy='joined')
    harmonic_density = db.relationship('HarmonischeDichte', lazy='joined')
    harmonic_complexity = db.relationship('HarmonischeKomplexitaet', lazy='joined')
    melody_tones_in_melody_one = db.relationship('AnzahlMelodietoene', lazy='joined')
    melody_tones_in_melody_two = db.relationship('AnzahlMelodietoene', lazy='joined')

    @property
    def harmonic_centers(self):
        return self._harmonic_centers

    @harmonic_centers.setter
    def harmonic_centers(self, harmonic_centers_list: Sequence[dict]):
        old_items = {center.id: center for center in self._harmonic_centers}
        to_add = []  # type: List[HarmonicCenter]

        for harmonic_center in harmonic_centers_list:
            harmonic_center_id = harmonic_center.get('id')
            if harmonic_center_id in old_items:
                old_items[harmonic_center_id].update(**harmonic_center)
                del old_items[harmonic_center_id]
            else:
                to_add.append(HarmonicCenter(self, **harmonic_center))

        for center in to_add:
            db.session.add(center)
        to_delete = list(old_items.values())  # type: List[HarmonicCenter]
        for center in to_delete:
            db.session.delete(center)

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
    def special_chords(self):
        return [mapping.akkord for mapping in self._special_chords]

    @special_chords.setter
    def special_chords(self, special_chords_list: Union[Sequence[int], Sequence[dict]]):
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


class HarmonicCenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'))
    grundton_id = db.Column(db.Integer, db.ForeignKey('grundton.id'))
    tonalitaet_id = db.Column(db.Integer, db.ForeignKey('tonalitaet.id'))
    harmonische_funktion_id = db.Column(db.Integer, db.ForeignKey('harmonische_funktion.id'))
    harmonische_stufe_id = db.Column(db.Integer, db.ForeignKey('harmonische_stufe.id'))

    harmonics = db.relationship(Harmonics, backref=db.backref('_harmonic_centers', lazy='joined'))
    grundton = db.relationship('Grundton', lazy='joined')
    tonalitaet = db.relationship('Tonalitaet', lazy='joined')
    harmonische_funktion = db.relationship('HarmonischeFunktion', lazy='joined')
    harmonische_stufe = db.relationship('HarmonischeStufe', lazy='joined')

    def __init__(self, harmonics, grundton, tonalitaet, harmonische_funktion, harmonische_stufe, **kwargs):
        self.harmonics = harmonics
        self.update(grundton, tonalitaet, harmonische_funktion, harmonische_stufe)

    def update(self, grundton, tonalitaet, harmonische_funktion, harmonische_stufe):
        self.grundton = Grundton.get_by_id_or_dict(grundton)
        self.tonalitaet = Tonalitaet.get_by_id_or_dict(tonalitaet)
        self.harmonische_funktion = HarmonischeFunktion.get_by_id_or_dict(harmonische_funktion)
        self.harmonische_stufe = HarmonischeStufe.get_by_id_or_dict(harmonische_stufe)


class HarmonischePhaenomeneToHarmonics(db.Model):
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), primary_key=True)
    harmonische_phaenomene_id = db.Column(db.Integer, db.ForeignKey('harmonische_phaenomene.id'), primary_key=True)

    harmonics = db.relationship(Harmonics, backref=db.backref('_harmonic_phenomenons', lazy='joined'))
    harmonische_phaenomene = db.relationship('HarmonischePhaenomene')

    def __init__(self, harmonics, harmonische_phaenomene, **kwargs):
        self.harmonics = harmonics
        self.harmonische_phaenomene = harmonische_phaenomene


class HarmonischeEntwicklungToHarmonics(db.Model):
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), primary_key=True)
    harmonische_entwicklung_id = db.Column(db.Integer, db.ForeignKey('harmonische_entwicklung.id'), primary_key=True)

    harmonics = db.relationship(Harmonics, backref=db.backref('_harmonic_changes', lazy='joined'))
    harmonische_entwicklung = db.relationship('HarmonischeEntwicklung')

    def __init__(self, harmonics, harmonische_entwicklung, **kwargs):
        self.harmonics = harmonics
        self.harmonische_entwicklung = harmonische_entwicklung


class AkkordToHarmonics(db.Model):
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), primary_key=True)
    akkord_id = db.Column(db.Integer, db.ForeignKey('akkord.id'), primary_key=True)

    harmonics = db.relationship(Harmonics, backref=db.backref('_special_cords', lazy='joined'))
    akkord = db.relationship('Akkord')

    def __init__(self, harmonics, akkord, **kwargs):
        self.harmonics = harmonics
        self.akkord = akkord


class DissonanzenToHarmonics(db.Model):
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), primary_key=True)
    dissonanzen_id = db.Column(db.Integer, db.ForeignKey('dissonanzen.id'), primary_key=True)

    harmonics = db.relationship(Harmonics, backref=db.backref('_dissonances', lazy='joined'))
    dissonanzen = db.relationship('Dissonanzen')

    def __init__(self, harmonics, dissonanzen, **kwargs):
        self.harmonics = harmonics
        self.dissonanzen = dissonanzen
