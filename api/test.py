# http://localhost:8080/test/client/submit
# http://localhost:8080/test/client/status/28902ec5-8930-4d03-bea4-6347b6b0a793
# http://localhost:8080/test/client/cancel/c625249b-a662-493d-8825-2626ad94d0ba
# http://localhost:8080/test/client/response/aca89ce0-ac1a-4f58-985d-9c0aad49fc6a

from flask import render_template, Response

from engine import app
from config import config

from lib.CMHandler import CMHandler
from lib.SMHandler import SMHandler
from lib.Tools import load_json_file
from lib.dto.LinkRequest import LinkRequest

# Config location
from lib.httpsig.HttpSigClient import HttpSigClient

data_dir = config.get('Configuration', 'dir')
port = config.get('Server', 'port')


def httpsig_client():
    key = 'test/data/httpsig_key.pem'
    fingerprint = '58f20aef58f63c28d95a57e5e7dd3e6971122ce35b5448acf36818874a0b2c0c'
    trusted_keys = {'58f20aef58f63c28d95a57e5e7dd3e6971122ce35b5448acf36818874a0b2c0c':
                        'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDJBbbirvao04+n3R0rvX2Mbq+J' +
                        'JyEl06K6hWf4MarVi6YTuJWWQb3D0mkWLATBchAntTsQsj+TH8VLkVIP3YWuOeT9' +
                        '49AmfGQ1lM5FTzYmyh5wl6n1v/k7CGKqkm/WLRZD94HJE+FDhJ+ERy4/nF54n6ex' +
                        'Z1Fd4eevfzE1QqNJSQIDAQAB'}
    return HttpSigClient(key, trusted_keys)


def sm_handler():
    # ms_url = "http://esmo.uji.es:8080/cm/metadata/microservices"
    ms_url = "http://lab9054.inv.uji.es/~paco/seal/msmetadata.json"
    cm = CMHandler(data_dir, key='test/data/httpsig_key_esmo.pem', lifetime=30, ms_source_url=ms_url)
    sm = cm.get_microservice_by_api('SM')
    return SMHandler(sm, key='test/data/httpsig_key_esmo.pem', retries=5, validate=False)


# API Endpoints


# Start a linking request
@app.route('/test/client/submit', methods=['GET'])
def test_client_submit_linking_request():
    smh = sm_handler()

    smh.startSession()
    print("Started session: " + smh.sessId + "<br/>\n")

    token = smh.generateToken("SAMLms_0001", "SAMLms_0001")
    print("Generated msToken: " + token + "<br/>\n")

    streq = load_json_file('test/data/testLinkRequest.json')
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


@app.route('/test/client/cancel/<request_id>', methods=['GET'])
def test_client_cancel_linking_request(request_id=None):
    smh = sm_handler()

    # We don't care about the session, and no user is authenticated
    smh.startSession()
    print("Started session (a different one): " + smh.sessId + "<br/>\n")

    token = smh.generateToken("SAMLms_0001", "SAMLms_0001")
    print("Generated msToken: " + token + "<br/>\n")

    template = {
        'url': f'/link/{request_id}/cancel',
        'token': token,
    }

    return render_template('msToken.html', template=template)


@app.route('/test/client/response/<request_id>', methods=['GET'])
def test_client_getresult_linking_request(request_id=None):
    smh = sm_handler()

    # We don't care about the session, and no user is authenticated
    smh.startSession()
    print("Started session (a different one): " + smh.sessId + "<br/>\n")

    token = smh.generateToken("SAMLms_0001", "SAMLms_0001")
    print("Generated msToken: " + token + "<br/>\n")

    template = {
        'url': f'/link/{request_id}/result/get',
        'token': token,
    }

    return render_template('msToken.html', template=template)


# TODO: Write the test req and metadata, tune this with the proper parameters and target ms, and test
# Start a linking request
@app.route('/test/client/sp/<idp>', methods=['GET'])
def test_client_submit_auth_request(idp):
    smh = sm_handler()
    smh.startSession()
    print("Started session: " + smh.sessId + "<br/>\n")
    token = smh.generateToken("SAMLms_0001", "SAMLms_0001")
    print("Generated msToken: " + token + "<br/>\n")

    with open('test/data/testAuthRequest.json', encoding='utf-8') as f:
        authreq = f.read()
    smh.writeSessionVar(authreq, 'spRequest') # TODO: check variable
    with open('test/data/testSPMetadata.json', encoding='utf-8') as f:
        spmeta = f.read()
    smh.writeSessionVar(spmeta, 'spMetadata')  # TODO: check variable
    smh.writeSessionVar(idp, 'apEntityId')  # TODO: check variable

    # Check written vars
    print("spRequest: " + smh.getSessionVar('spRequest') + "<br/>\n")
    print("spMetadata: " + smh.getSessionVar('spMetadata') + "<br/>\n")
    print("apEntityId: " + smh.getSessionVar('apEntityId') + "<br/>\n")

    template = {
        'url': '/link/request/submit',
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
