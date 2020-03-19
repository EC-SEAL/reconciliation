import logging
import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Text, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from definitions import ENCRYPTION_KEY


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
db_enc_key = os.getenv('ENCRYPTION_KEY', ENCRYPTION_KEY)


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
