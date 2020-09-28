#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import uuid
from urllib.parse import urlencode

from flask import Response, request
from datetime import datetime, timedelta
import logging

from config import config
from definitions import DEFAULT_DATA_DIR
from engine import app
from lib.Microservice import session_manager_handler, redirect_return
from lib.SMHandler import SessionManagerError
from lib.Tools import load_json_file, build_store_id, indirect_search, build_store_id_from_req
from lib.dto.Dataset import Dataset
from lib.dto.LinkRequest import LinkRequest
from lib.dto.StatusResponse import StatusResponse, StatusCodes
from lib.reconciliation import Reconciliation
import database

# Config location
data_dir = config.get('Configuration', 'dir', fallback=DEFAULT_DATA_DIR)

# Link Issuer name
issuer = config.get('App', 'issuer', fallback="")

# Link validity in days
validity_days = config.getint('App', 'validity_days', fallback="")

# Request lifetime in seconds
request_lifetime = config.getint('App', 'request_lifetime', fallback="")

# Similarity threshold to consider a request accepted
acceptance_threshold = config.getfloat('App', 'acceptance_threshold', fallback="")

# Which LLoA will have the resulting link if accepted
lloa = config.get('App', 'lloa', fallback="low")

# Type of the generated link dataset
dataset_type = config.get('App', 'dataset_type', fallback="")

# Private RSA key to use
httpsig_private_key = config.get('HTTPSig', 'private_key')

# Identifier of the entity (usually the SHA256 hex-encoded fingerprint of the key)
httpsig_key_id = config.get('HTTPSig', 'key_id', fallback=None)

# As SM sometimes fails to validate signature, we retry the connection for resilience
httpsig_send_retries = config.getint('HTTPSig', 'retries', fallback=1)

# Config Manager ms metadata url (env var overrides)
ms_metadata_url = config.get('CM', 'url', fallback=None)
ms_metadata_url = os.getenv('MSMETADATAURL', ms_metadata_url)

# Config Manager ms metadata url
cm_cache_lifetime = config.getint('CM', 'cache_lifetime', fallback=None)

# Names of microservices
msID = config.get('App', 'msID', fallback="")
apigwID = config.get('App', 'apigwID', fallback="")


def get_session_manager():
    return session_manager_handler(data_dir, ms_metadata_url,
                                   httpsig_private_key, cm_cache_lifetime,
                                   httpsig_send_retries)


# API Endpoints

@app.route('/link/request/submit', methods=['POST'])
def submit_linking_request():
    clean_expired()

    # Check msToken against SM
    if 'msToken' not in request.form:
        return "missing msToken POST parameter or bad content-type", 404
    msToken = request.form['msToken']
    smh = get_session_manager()
    try:
        smh.validateToken(msToken)
    except SessionManagerError as err:
        return "Error validating msToken: " + str(err), 403

    try:
        dest_url = smh.getSessionVar('ClientCallbackAddr')
    except SessionManagerError as err:
        return "Error retrieving ClientCallbackAddr from SM: " + str(err), 403

    # Load mappings to apply
    mappings_dicts = load_json_file(data_dir + 'attributeMaps.json')
    reconciliation = Reconciliation()
    reconciliation.set_mappings(mappings_dicts)

    # Parse input request
    try:
        link_req = smh.getSessionVar('linkRequest')
    except SessionManagerError as err:
        # return "Error retrieving linkRequest from SM: " + str(err), 403
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID,
                               "Error retrieving linkRequest from SM: " + str(err))
    req = LinkRequest()
    req.json_unmarshall(link_req)

    now = datetime.now()

    request_id = str(uuid.uuid4())

    # Create a database row object
    db_req = database.Request(request_id=request_id, request_date=now,
                              status=StatusCodes.PENDING,
                              dataset_a=req.datasetA.json_marshall(),
                              dataset_b=req.datasetB.json_marshall())

    # Store it on DB
    session = database.DbSession()
    session.add(db_req)
    session.commit()

    # Calculate similarity
    similarity = reconciliation.similarity(req.datasetA, req.datasetB)
    db_req.similarity = similarity

    # Update request with the LLoA and the acceptance status
    if similarity >= acceptance_threshold:
        db_req.status = StatusCodes.ACCEPTED
    else:
        db_req.status = StatusCodes.REJECTED

    session.add(db_req)
    session.commit()
    session.close()

    # Fill in the requestID and store the request object in the dataStore
    req.id = request_id
    request_json = req.json_marshall()

    try:
        # Build the unique persistent storeEntry identifier # TODO: parametrise module name (search more incidences)
        entry_id = build_store_id_from_req("seal-autorecon", issuer, req.datasetA, req.datasetB)
        smh.addDatastoreEntry(entry_id, "linkRequest", req.marshall())  # TODO: parametrise type
    except SessionManagerError as err:
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID,
                               "Error writing updated linkRequest to dataStore: " + str(err))

    # We also overwrite it in SM session
    try:
        smh.writeSessionVar(req.marshall(), 'linkRequest')  # TODO: expected variable?
    except SessionManagerError as err:
        # return "Error writing updated linkRequest to SM: " + str(err), 403
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID,
                               "Error writing updated linkRequest to SM: " + str(err))

    # return Response(request_json,
    #                status=200,
    #                mimetype='application/json')
    return redirect_return(smh, dest_url, 'OK', msID, apigwID)


# TODO: SEGUIR:
# TODO: add the response to the datastore as well as to the session var
# TODO: integrate httpsig lib to build a server in flask (try, but if too much, just rely on open access)
# TODO: integrate httpSig (server) in all back-channel calls, if needed
# TODO: add inline signature to response dataset
# TODO: implement unit tests on each api function (see to mockup the SM, try to redefine the lib with a mockup)

# Get request status in DB
@app.route('/link/<request_id>/status', methods=['GET'])
def linking_request_status(request_id):
    clean_expired()

    # TODO: httpsig secured? (do we have httpsig server)?

    req = get_request(request_id)
    if not req:
        return "Request ID not found", 403
    if not req.status:
        return "Request status not found", 404

    if not check_owner(request.args.get('sessionToken'), req.request_owner):
        return "Request does not belong to the authenticated user", 403

    resp = StatusResponse()
    resp.primaryCode = 'OK'
    resp.secondaryCode = req.status
    resp.message = None
    return Response(resp.json_marshall(),
                    status=200,
                    mimetype='application/json')


@app.route('/link/<request_id>/cancel', methods=['POST'])
def cancel_linking_request(request_id):
    clean_expired()

    # Check msToken against SM
    if 'msToken' not in request.form:
        return "missing msToken POST parameter or bad content-type", 404
    msToken = request.form['msToken']
    smh = get_session_manager()
    try:
        smh.validateToken(msToken)
    except SessionManagerError as err:
        return "Error validating msToken: " + str(err), 403

    try:
        dest_url = smh.getSessionVar('ClientCallbackAddr')
    except SessionManagerError as err:
        return "Error retrieving ClientCallbackAddr from SM: " + str(err), 403

    req = get_request(request_id)
    if not req:
        # return "Request ID not found", 403
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID, "Request ID not found")

    if not check_owner(smh.sessId, req.request_owner):
        # return "Request does not belong to the authenticated user", 403
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID,
                               "Request does not belong to the authenticated user")

    # First we delete it from the dataStore by rebuilding the persistent ID
    try:
        entry_id = build_store_id_from_req("seal-autorecon", issuer, req.datasetA, req.datasetB) # TODO: change when the module is parametrised
        smh.deleteDatastoreEntry(entry_id)
    except SessionManagerError as err:
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID,
                               "Error writing updated linkRequest to dataStore: " + str(err))

    try:
        delete_request(request_id)
        # return "Request Deleted", 200
        return redirect_return(smh, dest_url, 'OK', msID, apigwID)

    except RegisterNotFound:
        # return "Request not found", 403
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID, "Request not found")


@app.route('/link/<request_id>/result/get', methods=['POST'])
def linking_request_result(request_id):
    clean_expired()

    # Check msToken against SM
    if 'msToken' not in request.form:
        return "missing msToken POST parameter or bad content-type", 404
    msToken = request.form['msToken']
    smh = get_session_manager()
    try:
        smh.validateToken(msToken)
    except SessionManagerError as err:
        return "Error validating msToken: " + str(err), 403

    try:
        dest_url = smh.getSessionVar('ClientCallbackAddr')
    except SessionManagerError as err:
        return "Error retrieving ClientCallbackAddr from SM: " + str(err), 403

    req = get_request(request_id)
    if not req:
        # return "Request ID not found", 403
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID, "Request ID not found")

    if not check_owner(smh.sessId, req.request_owner):
        # return "Request does not belong to the authenticated user", 403
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID,
                               "Request does not belong to the authenticated user")

    if req.status != "ACCEPTED":
        # return "Linking request was not accepted", 403
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID, "Linking request was not accepted")

    # Calculate expiration date
    expiration = None
    if validity_days > 0:
        expiration = datetime.now() + timedelta(days=validity_days)
        expiration = expiration.isoformat()

    # Build Response object
    datasetA = Dataset()
    datasetA.json_unmarshall(req.dataset_a)
    datasetB = Dataset()
    datasetB.json_unmarshall(req.dataset_b)

    result = LinkRequest()
    result.id = req.request_id
    result.issuer = issuer
    result.type = dataset_type
    result.lloa = lloa
    result.issued = datetime.now().isoformat()
    result.expiration = expiration
    result.datasetA = datasetA
    result.datasetB = datasetB
    result.evidence = None
    result.conversation = None

    result_json = result.json_marshall()
    # TODO: sign the response json string

    # Overwrite the response in the SM session
    try:
        smh.writeSessionVar(result.marshall(), 'linkRequest')
    except SessionManagerError as err:
        # return "Error writing updated linkRequest to SM: " + str(err), 403
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID,
                               "Error writing updated linkRequest to SM: " + str(err))

    try:
        # Build the unique persistent storeEntry identifier # TODO: parametrise module name (search more incidences)
        entry_id = build_store_id_from_req("seal-autorecon", issuer, result.datasetA, result.datasetB)
        smh.addDatastoreEntry(entry_id, "linkRequest", result.marshall())  # TODO: parametrise type
    except SessionManagerError as err:
        return redirect_return(smh, dest_url, 'ERROR', msID, apigwID,
                               "Error writing updated linkRequest to dataStore: " + str(err))

    try:
        delete_request(request_id)
    except RegisterNotFound:
        logging.warning("This should not happen. Can't delete a register I have just read")

    # return Response(result_json,
    #                status=200,
    #                mimetype='application/json')
    return redirect_return(smh, dest_url, 'OK', msID, apigwID)


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


def clean_expired():
    threshold = datetime.now() - timedelta(seconds=request_lifetime)

    session = database.DbSession()
    reqs_to_delete = session.query(database.Request).filter(database.Request.request_date < threshold)
    for req in reqs_to_delete:
        session.delete(req)
    session.commit()
    session.close()


class RegisterNotFound(Exception):
    def __init__(self, message):
        self.message = message
