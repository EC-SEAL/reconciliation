#!/usr/bin/python
# -*- coding: UTF-8 -*-

from config import config
from engine import app
import apiloader
import logging

# Read Server configuration
host = config.get('Server', 'host', fallback='localhost')
port = config.getint('Server', 'port', fallback=8080)
debug = config.getboolean('Server', 'debug', fallback=False)

# Read SSL configuration
enableSSL = config.getboolean('SSL', 'enable', fallback=False)
cert = config.get('SSL', 'cert', fallback=None)
key = config.get('SSL', 'key', fallback=None)

# Logging configuration
loglevel = config.get('Log', 'level', fallback=logging.WARNING)
logfile = config.get('Log', 'file', fallback=None)


# Setup logger
logging.basicConfig(level=loglevel,
                    format='%(asctime)s %(levelname)s:%(name)s: %(message)s',
                    filename=logfile)


# Publish root test service
@app.route('/')
def hello_world():
    return 'IT WORKS'


# Publish the rest of the services defined on the api directory
apiloader.load_api()

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
