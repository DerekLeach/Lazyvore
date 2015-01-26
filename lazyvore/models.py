from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    synonym,
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
    user = Column(String(length=100), unique=True)

    _password = Column(String(length=50),
                       info={'colanderalchemy': {'widget': CheckedPasswordWidget(size=20)}})

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = hash_password(password)

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    # @classmethod
    # def check_password(cls, username

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
