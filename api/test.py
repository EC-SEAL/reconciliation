# http://localhost:8050/test/client/submit
# http://localhost:8050/test/client/status/28902ec5-8930-4d03-bea4-6347b6b0a793
# http://localhost:8050/test/client/cancel/c625249b-a662-493d-8825-2626ad94d0ba
# http://localhost:8050/test/client/response/aca89ce0-ac1a-4f58-985d-9c0aad49fc6a
import base64
import json
import logging
import os

# TODO: update this script to:
#   - register a callback url
#   - validate the msToken on the callback
#   - get the response status
#   - display the likRequest, etc, by reading the variables from the SM.

# TODO: check if sameSite= None is being set


from flask import render_template, Response, request

from engine import app
from config import config

from lib.CMHandler import CMHandler
from lib.SMHandler import SMHandler, EndpointNotFound
from lib.Tools import load_json_file
from lib.dto.LinkRequest import LinkRequest

# Config location
from lib.httpsig.HttpSigClient import HttpSigClient

data_dir = config.get('Configuration', 'dir')
port = config.get('Server', 'port')
key_file = config.get('HTTPSig', 'private_key')
cm_url = config.get('CM', 'url')
cm_url = os.getenv('MSMETADATAURL', cm_url)

client_key_file = config.get('TestClient', 'cli_key')
trusted_key = config.get('TestClient', 'trusted_key')
fingerprnt = config.get('TestClient', 'fingerprint')
test_link_req = config.get('TestClient', 'test_link_req')

test_auth_req = config.get('TestClient', 'test_auth_req')
test_sp_metadata = config.get('TestClient', 'test_sp_metadata')

cburl = "/test/client/callback"


def httpsig_client():
    key = client_key_file
    fingerprint = fingerprnt
    trusted_keys = {fingerprnt: trusted_key}
    return HttpSigClient(key, trusted_keys)


def cm_handler():
    ms_url = cm_url
    return CMHandler(data_dir, key=key_file, lifetime=30, ms_source_url=ms_url)


def sm_handler():
    cm = cm_handler()
    sm = cm.get_microservice_by_api('SM')
    return SMHandler(sm, key=key_file, retries=5, validate=False)


def get_url(mo, apiClass, apiCall):
    for api in mo.publishedAPI:
        if api.apiClass == apiClass and api.apiCall == apiCall:
            return api.apiEndpoint
    raise EndpointNotFound("API call " + apiCall + " from class " + apiClass +
                           " not found on any entry in the " +
                           mo.smMetadata.msId + " microservice metadata object")


# API Endpoints


# Callback address
@app.route('/test/client/', methods=['GET', 'POST'])
@app.route('/test/client/callback', methods=['GET', 'POST'])
def test_client_callback():
    token = ''
    session = ''
    output = ''
    session_str = ''
    sessid = ''
    datastoreStr = ''
    requestID = None
    if request.form and request.form['msToken']:
        token = request.form['msToken']

        logging.debug("token: " + token)
        token = token.split('.')
        logging.debug("split token: " + str(token))

        # Add padding to the B64 string
        token[1] += "=" * ((4 - len(token[1]) % 4) % 4)
        btoken = bytes(token[1], 'utf-8')
        token = base64.b64decode(btoken)
        json_token = json.loads(token)
        token = json.dumps(json_token, indent=4)

        jwt = json.loads(token)

        sessid = jwt['sessionId']
        smh = sm_handler()
        smh.setSessID(sessid)

        session = smh.getSessionVar()
        session_str = ''
        for sessvar in session:
            value = session[sessvar]
            if value[0] == '{':
                valueunesc = value.replace('\\"', '"')
                jsonvalue = json.loads(valueunesc)
                session[sessvar] = jsonvalue
                indentvalue = json.dumps(jsonvalue, indent=4)
                session_str = session_str + sessvar + ': ' + indentvalue + '\n--------\n'
            else:
                session_str = session_str + sessvar + ': ' + value + '\n--------\n'

        if session['linkRequest']:
            linkRequest = session['linkRequest']
            logging.debug("linkRequest: " + str(linkRequest))
            if linkRequest['id']:
                requestID = linkRequest['id']
                logging.debug("linkRequest.id: " + str(requestID))

        datastore = smh.searchDatastoreEntries()
        for entry in datastore:
            datastoreStr = json.dumps(entry.marshall(), indent=4)

    template = {
        'token': token,
        'datastore': datastoreStr,
        'session': session_str,
        'display': output,
    }
    if requestID:
        template['requestID'] = requestID
    if sessid:
        template['sessionID'] = sessid
    logging.debug("Template vars: " + str(template))
    return render_template('callback.html', template=template)


# Start a linking request
@app.route('/test/client/submit', methods=['GET'])
def test_client_submit_linking_request():
    smh = sm_handler()

    smh.startSession()
    print("Started session: " + smh.sessId + "<br/>\n")

    smh.writeSessionVar(cburl, 'ClientCallbackAddr')

    token = smh.generateToken("SAMLms_0001", "SAMLms_0001")
    print("Generated msToken: " + token + "<br/>\n")

    streq = load_json_file(test_link_req)
    treq = LinkRequest()
    treq.unmarshall(streq)
    smh.writeSessionVar(treq.marshall(), 'linkRequest')
    print("Wrote linkRequest in Session: " + treq.json_marshall() + "<br/>\n")

    template = {
        'url': '/link/request/submit',
        'token': token,
    }

    return render_template('msToken.html', template=template)


# Check status of a linking request
@app.route('/test/client/status/<request_id>', methods=['GET'])
def test_client_status_linking_request(request_id):
    cli = httpsig_client()
    resp = cli.get(f'http://localhost:{port}/link/{request_id}/status')
    return Response(resp.text,
                    status=200,
                    mimetype='application/json')


@app.route('/test/client/cancel/<request_id>/<sess_id>', methods=['GET'])
def test_client_cancel_linking_request(request_id, sess_id):
    smh = sm_handler()

    ## We don't care about the session, and no user is authenticated
    # smh.startSession()
    # print("Started session (a different one): " + smh.sessId + "<br/>\n")

    smh.setSessID(sess_id)

    token = smh.generateToken("SAMLms_0001", "SAMLms_0001")
    print("Generated msToken: " + token + "<br/>\n")

    template = {
        'url': f'/link/{request_id}/cancel',
        'token': token,
    }

    return render_template('msToken.html', template=template)


@app.route('/test/client/response/<request_id>/<sess_id>', methods=['GET'])
def test_client_getresult_linking_request(request_id, sess_id):
    smh = sm_handler()

    ## We don't care about the session, and no user is authenticated
    # smh.startSession()
    # print("Started session (a different one): " + smh.sessId + "<br/>\n")

    smh.setSessID(sess_id)

    token = smh.generateToken("SAMLms_0001", "SAMLms_0001")
    print("Generated msToken: " + token + "<br/>\n")

    template = {
        'url': f'/link/{request_id}/result/get',
        'token': token,
    }

    return render_template('msToken.html', template=template)


# TODO: tune this with the proper parameters and target ms, and test
# Start a linking request
#   to <idp> [Discovery, PDS, uportSSIwallet, eIDAS, eduGAIN]
#   of <type> [auth_request, data_query]
# http://localhost:8050/test/client/sp/eduGAIN/auth_request
@app.route('/test/client/sp/<idp>/<type>', methods=['GET'])
def test_client_submit_auth_request(idp, type):
    # Start session
    smh = sm_handler()
    smh.startSession()
    print("Started session: " + smh.sessId + "<br/>\n")

    # Generate Token
    dest = 'RMms001'
    token = smh.generateToken("SAMLms_0001", dest)
    print(f"Generated msToken addressed to {dest}: {token}<br/>\n")

    # Write session variables
    with open(test_auth_req, encoding='utf-8') as f:
        authreq = f.read()
    smh.writeSessionVar(authreq, 'spRequest')  # TODO: check variable
    with open(test_sp_metadata, encoding='utf-8') as f:
        spmeta = f.read()
    smh.writeSessionVar(spmeta, 'spMetadata')  # TODO: check variable
    smh.writeSessionVar(idp, 'apEntityId')  # TODO: check variable

    smh.writeSessionVar(type, 'spRequestEP')
    smh.writeSessionVar(idp, 'spRequestSource')

    # Check written vars
    print("spRequest: " + smh.getSessionVar('spRequest') + "<br/>\n")
    print("spMetadata: " + smh.getSessionVar('spMetadata') + "<br/>\n")
    print("apEntityId: " + smh.getSessionVar('apEntityId') + "<br/>\n")
    print("spRequestEP: " + smh.getSessionVar('spRequestEP') + "<br/>\n")
    print("spRequestSource: " + smh.getSessionVar('spRequestSource') + "<br/>\n")

    # Now let's get the Request Manager metadata
    cm = cm_handler()
    rm = cm.get_microservice_by_api('RM')

    url = get_url(rm, 'RM', 'rmRequest')
    template = {
        'url': url,
        'token': token,
    }

    return render_template('msToken.html', template=template)


# Tests for HTTPSig server and client  # TODO: implement


# Test HTTPSig server
@app.route('/test/server/httpsig', methods=['GET', 'POST'])
def test_server_httpsig_verify():
    return "AAAAA"


# Test HTTPSig client GET
@app.route('/test/client/httpsig/get', methods=['GET'])
def test_client_submit_httpsig_get():
    c = httpsig_client()
    res = c.get("http://localhost:8080/test/server/httpsig")
    return "Hola", 200


# Test HTTPSig client POST Form  # TODO: implement
@app.route('/test/client/httpsig/post/form', methods=['POST'])
def test_client_submit_httpsig_form():
    pass


# Test HTTPSig client POST Json  # TODO: implement
@app.route('/test/client/httpsig/post/json', methods=['POST'])
def test_client_submit_httpsig_json():
    pass
