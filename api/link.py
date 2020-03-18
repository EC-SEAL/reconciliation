#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Response
import logging

from config import config
from definitions import DEFAULT_DATA_DIR
from engine import app
from lib.Tools import load_json_file
from lib.reconciliation import Reconciliation

# Config location
data_dir = config.get('Configuration', 'dir', fallback=DEFAULT_DATA_DIR)


@app.route('/link/request/submit', methods=['POST'])
def submit_linking_request():
    # Load mappings to apply
    # TODO: for now, load them on each request. Later decide if we load them
    #  on launch time and we add some mechanism for refreshing (or not, just reload service)
    mappings_dicts = load_json_file(data_dir + 'attributeMaps.json')
    r = Reconciliation()
    r.set_mappings(mappings_dicts)

    # Parse request, store it on DB, clean expired requests, calculate similarity, update result on db, return
    return 'Hello World! 1'


@app.route('/link/<request_id>/status', methods=['GET'])
def linking_request_status(request_id):
    # Get status in DB, return
    return 'Hello World status! ' + request_id


@app.route('/link/<request_id>/cancel', methods=['POST'])
def cancel_linking_request(request_id):
    # Delete request from DB, return
    pass


@app.route('/link/<request_id>/result/get', methods=['POST'])
def linking_request_result(request_id):
    # Return result and delete from db, return
    pass


# TODO: integrate httpSig, integrate DB to store request results, implement unit tests on each api function


# As this is an automated matching module, there is no interaction with the user,
# so these api calls will be just be idle and return successfully

@app.route('/link/<request_id>/files/upload', methods=['POST'])
def linking_request_upload_evidence(request_id):
    logging.debug("Called file upload for request_id: " + request_id)
    return "", 200


@app.route('/link/<request_id>/messages/send/<recipient>', methods=['POST'])
def linking_request_send_message(request_id, recipient):
    logging.debug("Called send message for request_id: " + request_id + " recipient:" + recipient)
    return "", 200


@app.route('/link/<request_id>/messages/receive', methods=['GET'])
def linking_request_receive_messages(request_id):
    logging.debug("Called receive messages for request_id: " + request_id)
    return Response("[]", status=200, mimetype='application/json')


# These APIs don't apply to this module, as it does not involve
# validator users so no validator client will use this
@app.route('/link/<request_id>/lock', methods=['GET'])
@app.route('/link/<request_id>/unlock', methods=['GET'])
@app.route('/link/<request_id>/get', methods=['GET'])
@app.route('/link/list', methods=['GET'])
@app.route('/link/<request_id>/approve', methods=['GET'])
@app.route('/link/<request_id>/reject', methods=['GET'])
@app.route('/link/<request_id>/files/download/list', methods=['GET'])
@app.route('/link/<request_id>/files/download/<file_id>', methods=['GET'])
def not_implemented(request_id="", file_id=""):
    logging.debug("Someone invoked a not implemented api. request_id: " + request_id + " file_id: " + file_id)
    return "API not implemented", 501
