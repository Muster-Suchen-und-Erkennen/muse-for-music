from typing import List, Sequence, Union

from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import BewegungImTonraum, Intervall, Verarbeitungstechnik


class Composition(db.Model, GetByID, UpdateListMixin, UpdateableModelMixin):

    _normal_attributes = (
        ("nr_repetitions_1_2", int),
        ("nr_repetitions_3_4", int),
        ("nr_repetitions_5_6", int),
        ("nr_repetitions_5_6", int),
    )
    _list_attributes = ("sequences", "composition_techniques")

    __tablename__ = "composition"
    id = db.Column(db.Integer, primary_key=True)

    nr_repetitions_1_2: MappedColumn[int] = db.Column(
        db.Integer, server_default=db.text("'0'")
    )
    nr_repetitions_3_4: MappedColumn[int] = db.Column(
        db.Integer, server_default=db.text("'0'")
    )
    nr_repetitions_5_6: MappedColumn[int] = db.Column(
        db.Integer, server_default=db.text("'0'")
    )
    nr_repetitions_7_10: MappedColumn[int] = db.Column(
        db.Integer, server_default=db.text("'0'")
    )

    # backrefs
    _techniques: Mapped[list["CompositionTechniqueToComposition"]] = relationship(
        lambda: CompositionTechniqueToComposition,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="composition",
    )
    _sequences: Mapped[list["MusicialSequence"]] = relationship(
        lambda: MusicialSequence,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="composition",
    )

    @property
    def composition_techniques(self):
        return [mapping.verarbeitungstechnik for mapping in self._techniques]

    @composition_techniques.setter
    def composition_techniques(
        self, techniques_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.verarbeitungstechnik.id: mapping for mapping in self._techniques
        }
        self.update_list(
            techniques_list,
            old_items,
            CompositionTechniqueToComposition,
            Verarbeitungstechnik,
            "verarbeitungstechnik",
        )

    @property
    def sequences(self):
        return self._sequences

    @sequences.setter
    def sequences(self, sequence_list: Sequence[dict]):
        old_items = {seq.id: seq for seq in self._sequences}
        to_add: List[MusicialSequence] = []

        for sequence in sequence_list:
            sequence_id = sequence.get("id")
            if sequence_id in old_items:
                old_items[sequence_id].update(**sequence)
                del old_items[sequence_id]
            else:
                to_add.append(MusicialSequence(self, **sequence))

        for seq in to_add:
            db.session.add(seq)
        to_delete: List[MusicialSequence] = list(old_items.values())
        for seq in to_delete:
            db.session.delete(seq)


class CompositionTechniqueToComposition(db.Model):
    composition_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Composition.id), primary_key=True
    )
    verarbeitungstechnik_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Verarbeitungstechnik.id), primary_key=True
    )

    composition: Mapped[Composition] = relationship(
        Composition, back_populates="_techniques"
    )
    verarbeitungstechnik: Mapped[Verarbeitungstechnik] = relationship(
        Verarbeitungstechnik, lazy="selectin"
    )

    def __init__(self, composition, verarbeitungstechnik, **kwargs):
        self.composition = composition
        self.verarbeitungstechnik = verarbeitungstechnik


class MusicialSequence(db.Model, GetByID):
    __tablename__ = "sequence"
    id: MappedColumn[int] = db.Column(db.Integer, primary_key=True)
    composition_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Composition.id)
    )
    tonal_corrected: MappedColumn[bool] = db.Column(db.Boolean, default=False)
    exact_repetition: MappedColumn[bool] = db.Column(db.Boolean, default=False)
    starting_interval_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Intervall.id)
    )
    flow_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(BewegungImTonraum.id)
    )
    beats: MappedColumn[int | None] = db.Column(db.Integer)

    starting_interval: Mapped[Intervall] = relationship(Intervall, lazy="selectin")
    flow: Mapped[BewegungImTonraum] = relationship(BewegungImTonraum, lazy="selectin")
    composition: Mapped[Composition] = relationship(
        Composition, back_populates="_sequences"
    )

    def __init__(
        self,
        composition,
        starting_interval,
        flow,
        beats: int,
        tonal_corrected: bool = False,
        exact_repetition: bool = False,
        **kwargs,
    ):
        if isinstance(composition, Composition):
            self.composition = composition
        else:
            found_composition = Composition.get_by_id(composition)
            if found_composition is None:
                raise KeyError(
                    f"Did not find composition with Compisition.id=={composition}!"
                )
            self.composition = found_composition
        self.update(starting_interval, flow, beats, tonal_corrected, exact_repetition)

    def update(
        self,
        starting_interval: int | dict | Intervall,
        flow: int | dict | BewegungImTonraum,
        beats: int,
        tonal_corrected: bool,
        exact_repetition: bool,
        **kwargs,
    ):
        found_intervall = Intervall.get_by_id_or_dict(starting_interval)
        if found_intervall is None:
            raise KeyError(f"Did not find intervall matching '{starting_interval}'!")
        found_flow = BewegungImTonraum.get_by_id_or_dict(flow)
        if found_flow is None:
            raise KeyError(f"Did not find BewegungImTonraum matching '{flow}'!")
        self.starting_interval = found_intervall
        self.flow = found_flow
        self.beats = beats
        self.tonal_corrected = tonal_corrected
        self.exact_repetition = exact_repetition
