from csv import DictReader
from ... import db
from .loadable_mixin import LoadableMixin


class Instrument(db.Model, LoadableMixin):
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

    def __init__(self, name: str, parent: 'Instrument'=None):
        self.name = name
        self.parent = parent

    def __repr__(self):
        return '<Instrument {}, children {}>'.format(self.name, [child.__repr__() for child in self.children])

    @staticmethod
    def load(input_data: DictReader):
        instruments = {}
        for row in input_data:
            name = row['name']
            if name in instruments:
                # FIXME proper logging
                print('No duplicate names allowed!')
                break
            if not row.get('parent'):
                instruments[name] = Instrument(name)
            else:
                if not row['parent'] in instruments:
                    # FIXME proper logging
                    print('Child defined before parent!')
                    break
                parent = instruments[row['parent']]
                instruments[name] = Instrument(name, parent)
        else:
            for name, value in instruments.items():
                db.session.add(value)
            db.session.commit()
            return
        # FIXME proper logging
        print('something bad happened')

