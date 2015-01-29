from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
        Allow,
        Everyone,
        Authenticated,
        )

from deform.widget import CheckedPasswordWidget

import cryptacular.bcrypt

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

def hash_password(password):
    return crypt.encode(password)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(length=100), unique=True)

    _password = Column("password", String(length=60),
                       info={'colanderalchemy': {'widget': CheckedPasswordWidget(size=20)}})

    @property
    def password(self):
        """Return the password hash."""
        return self._password

    @password.setter
    def password(self, password):
        self._password = hash_password(password)

    @classmethod
    def get_by_username(cls, username):
        return DBSession.query(cls).filter(cls.username == username).first()

    @classmethod
    def check_password(cls, username, password):
        user = cls.get_by_username(username)
        if not user:
            return False
        return crypt.check(user.password, password)

class Page(Base):
    """ The SQLAlchemy declarative model class for a Page object. """
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=100), unique=True)
    data = Column(Text)

# class Group(Base):
#     __tablename__ = 'groups'
#     id = Column(Integer, primary_key=True)
#     group = Column(String(length=100), unique=True)
# 
#     user = relationship("User", backref=backref('groups', order_by=id))

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, Authenticated, 'edit') ]
    def __init__(self, request):
        pass
