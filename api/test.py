from flask import render_template

from engine import app
from config import config

from lib.CMHandler import CMHandler
from lib.SMHandler import SMHandler


from lib.Tools import load_json_file
from lib.dto.LinkRequest import LinkRequest


# Config location
from lib.httpsig.HttpSigClient import HttpSigClient

data_dir = config.get('Configuration', 'dir')

# API Endpoints

# Start a linking request
@app.route('/test/client/submit', methods=['GET'])
def test_client_submit_linking_request():
    ms_url = "http://esmo.uji.es:8080/cm/metadata/microservices" # TODO: SEGUIR: colgare n otra url y probar
    cm = CMHandler(data_dir, key='test/data/httpsig_key_esmo.pem', lifetime=30, ms_source_url=ms_url)
    sm = cm.get_microservice_by_api('SM')
    smh = SMHandler(sm, key='test/data/httpsig_key_esmo.pem', retries=5, validate=False)

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


# TODO: add test calls for:
#  status (httpsig?)
#  cancel (msToken)


def httpsig_client():
    key = 'test/data/httpsig_key.pem'
    fingerprint = '58f20aef58f63c28d95a57e5e7dd3e6971122ce35b5448acf36818874a0b2c0c'
    trusted_keys = {'58f20aef58f63c28d95a57e5e7dd3e6971122ce35b5448acf36818874a0b2c0c':
                        'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDJBbbirvao04+n3R0rvX2Mbq+J' +
                        'JyEl06K6hWf4MarVi6YTuJWWQb3D0mkWLATBchAntTsQsj+TH8VLkVIP3YWuOeT9' +
                        '49AmfGQ1lM5FTzYmyh5wl6n1v/k7CGKqkm/WLRZD94HJE+FDhJ+ERy4/nF54n6ex' +
                        'Z1Fd4eevfzE1QqNJSQIDAQAB'}
    return HttpSigClient(key, trusted_keys)


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
