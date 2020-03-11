#!/usr/bin/python
# -*- coding: UTF-8 -*-

from engine import app
from lib.Tools import load_json_file
from lib.reconciliation import Reconciliation


@app.route('/link/request/submit')
def submit_linking_request():

    # Load matchings to apply
    # TODO: for now, load them on each request. Later decide if we load them
    #  on launch time and we add some mechanism for refreshing (or not, just reload service)
    matchings_dicts = load_json_file('attributeMaps.json')
    r = Reconciliation()
    r.set_matchings(matchings_dicts)

    return 'Hello World! 2'


@app.route('/link/<requestId>/status', methods=['POST'])
def ccc(requestId):
    return 'Hello World status! ' + requestId


