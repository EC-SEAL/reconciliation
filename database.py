import base64
import logging
import os
import random

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Text, Integer, Binary
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


# from config import config
#
# db_debug = config.getboolean('Database', 'logs', fallback=False)
# db_driver = config.get('Database', 'driver', fallback='sqlite')
# db_dialect = config.get('Database', 'dialect', fallback='')
# db_host = config.get('Database', 'host', fallback='')
# db_port = config.get('Database', 'port', fallback='')
# db_user = config.get('Database', 'user', fallback='')
# db_pass = config.get('Database', 'password', fallback='')
# db_path = config.get('Database', 'path', fallback=':memory:')


def db_engine(driver, path,
              dialect='', debug=False,
              host='', port='',
              user='', password=''):
    dialect_spec = ''
    if dialect != '':
        dialect_spec = '+' + dialect

    host_spec = ''
    if user != '':
        host_spec = user
        if password != '':
            host_spec = host_spec + ':' + password
        host_spec = host_spec + '@'
    if host != '':
        host_spec = host_spec + host
    if port != '':
        host_spec = host_spec + ':' + port

    connect_string = driver + dialect_spec + '://' + host_spec + '/' + path
    logging.debug("Database connect string: " + connect_string)

    return sqlalchemy.create_engine(connect_string, echo=debug)


# Declare session base class
DbSession = sessionmaker()


# Declare base SQLAlchemy declarative class for tables
DbTable = declarative_base()


# Set environment encryption key for database items, or use a random one
db_enc_key = os.getenv('PROPERTIES_FILE', base64.b64encode(os.urandom(16)))
# TODO: is this loaded just once or will the key be overwritten?
# TODO: check if randomness is real in docker, and if real, check if enough, as it might block execution


# Database tables
class Request(DbTable):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    request_id = Column(String, unique=True)
    dataset_a = Column(EncryptedType(Text, db_enc_key, AesEngine, 'pkcs5'))
    dataset_b = Column(EncryptedType(Text, db_enc_key, AesEngine, 'pkcs5'))
    similarity = Column(Float)
    status = Column(String)

    def __repr__(self):
        return "<Request(id='%s', request_id ='%s', similarity='%s'," \
               " status='%s', dataset_a='%s', dataset_b='%s')>" \
               % (self.id, self.request_id, self.similarity,
                  self.status, self.dataset_a, self.dataset_b)

# TODO SEGUIR: create linkRequest DTO, create request table (equivalent or store parts as strings?) . see how to
#  build the schema on the fy and fill it


# TODO: implement database encryption with runtime key creation, reset database on each startup
