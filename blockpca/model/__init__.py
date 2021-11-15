
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
maker = sessionmaker(autoflush=True, autocommit=False,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)


DeclarativeBase = declarative_base()

metadata = DeclarativeBase.metadata




def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    DBSession.configure(bind=engine)



from blockpca.model.auth import User, Group, Permission, PrivateKey

__all__ = ('User', 'Group', 'Permission', 'PrivateKey')
