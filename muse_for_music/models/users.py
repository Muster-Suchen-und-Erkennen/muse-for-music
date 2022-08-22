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
    deleted = db.Column(db.Boolean(), default=False)
    roles = db.relationship('UserRole', back_populates='user', lazy='joined',
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

    def set_password(self, password: str):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password: str, ignore_deleted: bool=False) -> bool:
        if self.deleted and not ignore_deleted:
            return False
        return bcrypt.check_password_hash(self.password, password)

    @classmethod
    def get_user_by_name(cls, username: str) -> 'User':
        return cls.query.filter_by(username=username).first()


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    user = db.relationship('User', back_populates='roles')
    role = db.Column(db.Enum(RoleEnum))

    def __init__(self, user: User, role: RoleEnum):
        self.user = user
        self.role = role

    def __repr__(self):
        return '<UserRole %r>' % self.role
