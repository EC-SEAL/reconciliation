#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Response, jsonify, request
import logging

from config import config
from definitions import DEFAULT_DATA_DIR
from engine import app
from lib.Tools import load_json_file
from lib.dto.StatusResponse import StatusResponse
from lib.reconciliation import Reconciliation
import database

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

    # TODO: SEGUIR:
    # - Parse request
    # - Store it on DB (set uuid requestId, status PENDING, similarity null)
    # - clean expired requests
    # - calculate similarity
    # - update request on db (similarity, status ACCEPTED/REJECT)
    # - return reqId?

    # Create a row object
    req = database.Request(request_id="1234", similarity=1.0, status='SUBMITTED',
                           dataset_a='aaaaaaaaaaaa', dataset_b='bbbbbbbbb')

    session = database.DbSession()
    session.add(req)
    session.commit()
    session.close()


    return 'Hello World! 1'
# TODO: SEGUIR: integrate httpSig (server) or sessionmanager token validation (client) in all calls
# TODO: implement unit tests on each api function


# Get request status in DB
@app.route('/link/<request_id>/status', methods=['GET'])
def linking_request_status(request_id):
    # TODO: httpsig secured (do we have httpsig server)?
    req = get_request(request_id)
    if not req:
        return "Request ID not found", 403
    if not req.status:
        return "Request status not found", 404

    if not check_owner(request.args.get('sessionToken'), req.request_owner):
        return "Request does not belong to the authenticated user", 403

    resp = StatusResponse()
    resp.primaryCode = req.status
    resp.secondaryCode = None
    resp.message = None
    return Response(resp.json_marshall(),
                    status=200,
                    mimetype='application/json')


@app.route('/link/<request_id>/cancel', methods=['POST'])
def cancel_linking_request(request_id):
    # TODO: msToken secured
    req = get_request(request_id)
    if not req:
        return "Request ID not found", 403

    if not check_owner(request.args.get('sessionToken'), req.request_owner):
        return "Request does not belong to the authenticated user", 403

    try:
        delete_request(request_id)
        return "Request Deleted", 200
    except RegisterNotFound:
        return "Request not found", 403


@app.route('/link/<request_id>/result/get', methods=['POST'])
def linking_request_result(request_id):
    # TODO: msToken secured
    req = get_request(request_id)
    if not req:
        return "Request ID not found", 403

    if not check_owner(request.args.get('sessionToken'), req.request_owner):
        return "Request does not belong to the authenticated user", 403

    try:
        delete_request(request_id)
    except RegisterNotFound:
        logging.warning("Can't delete a register. Not found. But I have just red it. Review")

    # TODO: SEGUIR: build linkRequest object con los datos esperados y devolver


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


# Support functions

def check_owner(session_id, request_owner):
    if not session_id:
        logging.warning("No session passed")
        return True  # TODO: disallow access without a session?

    logging.debug("Session_ID: " + session_id)
    # TODO: check session in sessionmanager and get authenticated user ID, if any
    user_id = None

    if not user_id:
        logging.warning("No user id in session")
        return True  # TODO: disallow unauthenticated requests?

    if request_owner != user_id:
        logging.warning("Request owner does not match session user")
        return False


def get_request(request_id):
    session = database.DbSession()
    req = session.query(database.Request).filter_by(request_id=request_id).first()
    session.close()
    return req


def delete_request(request_id):
    session = database.DbSession()
    req = session.query(database.Request).filter_by(request_id=request_id).first()
    if not req:
        raise RegisterNotFound("Could not delete request " + request_id + ". Not found")
    session.delete(req)
    session.commit()
    session.close()


class RegisterNotFound(Exception):
    def __init__(self, message):
        self.message = message
