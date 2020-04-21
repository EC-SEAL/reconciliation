#!/usr/bin/python
# -*- coding: UTF-8 -*-
from sqlalchemy.exc import OperationalError

from config import config, config_file_path
from definitions import API_DIR, API_ROOT_PACKAGE
from engine import app
import loader
import logging
import database

# Read Server configuration
host = config.get('Server', 'host', fallback='localhost')
port = config.getint('Server', 'port', fallback=8080)
debug = config.getboolean('Server', 'debug', fallback=False)

# Read SSL configuration
enableSSL = config.getboolean('SSL', 'enable', fallback=False)
cert = config.get('SSL', 'cert', fallback=None)
key = config.get('SSL', 'key', fallback=None)

# Logging configuration
loglevel = config.get('Log', 'level', fallback=logging.INFO)
logfile = config.get('Log', 'file', fallback=None)

# Database config
db_debug = config.getboolean('Database', 'logs', fallback=False)
db_driver = config.get('Database', 'driver', fallback='sqlite')
db_dialect = config.get('Database', 'dialect', fallback='')
db_host = config.get('Database', 'host', fallback='')
db_port = config.get('Database', 'port', fallback='')
db_user = config.get('Database', 'user', fallback='')
db_pass = config.get('Database', 'password', fallback='')
db_path = config.get('Database', 'path', fallback='data/requests.db')

# Setup logger
logging.basicConfig(level=loglevel,
                    format='%(asctime)s %(levelname)s:%(name)s: %(message)s',
                    filename=logfile)

logging.info("Using configuration file in: " + config_file_path)

# Get database engine
database_engine = database.db_engine(db_driver, db_path,
                                     debug=db_debug, dialect=db_dialect,
                                     host=db_host, port=db_port,
                                     user=db_user, password=db_pass)

# Bind engine to database session generator and to schema generator
database.DbSession.configure(bind=database_engine)
database.DbTable.metadata.bind = database_engine

# Drop the existing database
try:
    for tbl in reversed(database.DbTable.metadata.sorted_tables):
        database_engine.execute(tbl.delete())
except OperationalError:
    logging.warning("No tables are dropped")

# Create (or update) database schema
database.DbTable.metadata.create_all()


# Publish root test service
@app.route('/')
def hello_world():
    return 'IT WORKS'


# Publish the rest of the services defined on the api directory
loader.load_libs(API_DIR, API_ROOT_PACKAGE)

# Launch server
#   to launch in production:
#   gunicorn -w 4 -b 0.0.0.0:8080 --certfile=server.crt --keyfile=server.key app:app
#   -w : worker threads
#   -b : bind address and port
#   to enable ssl, specify cert and key files
if __name__ == '__main__':
    if enableSSL:
        app.run(host=host, port=port, debug=debug, ssl_context=(cert, key))
    else:
        app.run(host=host, port=port, debug=debug)
