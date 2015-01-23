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
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
        Allow,
        Everyone,
        Authenticated,
        )

from deform.widget import CheckedPasswordWidget

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Page(Base):
    """ The SQLAlchemy declarative model class for a Page object. """
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=100), unique=True)
    data = Column(Text)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user = Column(String(length=100), unique=True)
    password = Column(String(length=50),
                      info={'colanderalchemy': {'widget': CheckedPasswordWidget(size=20)}})

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
