import enum
from typing import List
from .. import db, bcrypt


class RoleEnum(enum.Enum):
    user = 1
    admin = 2
    taxonomy_editor = 3


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, index=True)
    password = db.Column(db.String(64))
    roles = db.relationship('UserRole', backref='User', lazy='joined',
                            cascade="all, delete-orphan",
                            passive_deletes=True)

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = bcrypt.generate_password_hash(password)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def roles_json(self) -> List[str]:
        return [role.role.name for role in self.roles]

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    @classmethod
    def get_user_by_name(cls, username: str) -> 'User':
        return cls.query.filter_by(username=username).first()


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    user = db.relationship('User', backref=db.backref('UserRole'))
    role = db.Column(db.Enum(RoleEnum))

    def __init__(self, user: User, role: RoleEnum):
        self.user = user
        self.role = role

    def __repr__(self):
        return '<UserRole %r>' % self.role
