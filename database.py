import logging
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from config import config

db_debug = config.getboolean('Database', 'logs', fallback=False)
db_driver = config.get('Database', 'driver', fallback='sqlite')
db_dialect = config.get('Database', 'dialect', fallback='')
db_host = config.get('Database', 'host', fallback='')
db_port = config.get('Database', 'port', fallback='')
db_user = config.get('Database', 'user', fallback='')
db_pass = config.get('Database', 'password', fallback='')
db_path = config.get('Database', 'path', fallback=':memory:')


def get_db_engine():
    global db_debug, db_driver, db_dialect, db_host, db_port, db_user, db_pass, db_path

    db_dialect_spec = ''
    if db_dialect != '':
        db_dialect_spec = '+' + db_dialect

    db_host_spec = ''
    if db_user != '':
        db_host_spec = db_user
        if db_pass != '':
            db_host_spec = db_host_spec + ':' + db_pass
        db_host_spec = db_host_spec + '@'
    if db_host != '':
        db_host_spec = db_host_spec + db_host
    if db_port != '':
        db_host_spec = db_host_spec + ':' + db_port

    connect_string = db_driver + db_dialect_spec + '://' + db_host_spec + '/' + db_path
    logging.debug("Database connect string: " + connect_string)

    return sqlalchemy.create_engine(connect_string, echo=db_debug)


# Declare base SQLAlchemy declarative class
Base = declarative_base()


class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    # TODO SEGUIR: create linkRequest DTO, create request table (equivalent or store parts as strings?) . see how to build the schema on the fy and fill it
    def __repr__(self):
        return ""#"<User(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)

#     title = Column('title', String(32))
#     in_stock = Column('in_stock', Boolean)
#     quantity = Column('quantity', Integer)
#     price = Column('price', Numeric)


# TODO: implement database encryption with runtime key creation, reset database on each startup
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    db_debug = True
    get_db_engine()
