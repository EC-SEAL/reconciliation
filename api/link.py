#!/usr/bin/python
# -*- coding: UTF-8 -*-

from config import config
from definitions import DEFAULT_DATA_DIR
from engine import app
from lib.Tools import load_json_file
from lib.reconciliation import Reconciliation


# Config location
data_dir = config.get('Configuration', 'dir', fallback=DEFAULT_DATA_DIR)


@app.route('/link/request/submit')
def submit_linking_request():

    # Load mappings to apply
    # TODO: for now, load them on each request. Later decide if we load them
    #  on launch time and we add some mechanism for refreshing (or not, just reload service)
    mappings_dicts = load_json_file(data_dir+'attributeMaps.json')
    r = Reconciliation()
    r.set_mappings(mappings_dicts)

    return 'Hello World! 2'


@app.route('/link/<requestId>/status', methods=['POST'])
def ccc(requestId):
    return 'Hello World status! ' + requestId


