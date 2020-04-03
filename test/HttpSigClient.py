#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# These tests will most probably fail for you, as they rely on a specific service being up and you
# having a RSA private key that is not on the repository.  # TODO: try to make them self-sustainable

import hashlib
import json
import unittest
import logging

from lib.SMHandler import SMHandler
from lib.Tools import sha256_fingerprint
from lib.dto.SessionMngrResponse import SessionMngrCode, SessionMngrResponse
from lib.httpsig.HttpSigClient import HttpSigClient, HttpError


class HttpSigTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(HttpSigTest, self).__init__(*args, **kwargs)
        # logging.basicConfig(level=logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True
        self.init_tests()

    def init_tests(self):
        pass

    def test_calculate_fingerprint(self):
        # TODO generate a new test key
        key = 'data/httpsig_key.pem'
        fingerprint = '58f20aef58f63c28d95a57e5e7dd3e6971122ce35b5448acf36818874a0b2c0c'
        trusted_keys = ['MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDJBbbirvao04+n3R0rvX2Mbq+J' +
                        'JyEl06K6hWf4MarVi6YTuJWWQb3D0mkWLATBchAntTsQsj+TH8VLkVIP3YWuOeT9' +
                        '49AmfGQ1lM5FTzYmyh5wl6n1v/k7CGKqkm/WLRZD94HJE+FDhJ+ERy4/nF54n6ex' +
                        'Z1Fd4eevfzE1QqNJSQIDAQAB']
        c = HttpSigClient(key, trusted_keys)
        self.assertEqual(c.key_id, fingerprint)
        self.assertEqual(sha256_fingerprint(c.trusted_keys[0]), fingerprint)

    def test_https_calls(self):
        key = 'data/httpsig_key.pem'
        fingerprint = '58f20aef58f63c28d95a57e5e7dd3e6971122ce35b5448acf36818874a0b2c0c'
        key = 'data/httpsig_key_esmo.pem'
        trusted_keys = {'58f20aef58f63c28d95a57e5e7dd3e6971122ce35b5448acf36818874a0b2c0c':
                            'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDJBbbirvao04+n3R0rvX2Mbq+J' +
                            'JyEl06K6hWf4MarVi6YTuJWWQb3D0mkWLATBchAntTsQsj+TH8VLkVIP3YWuOeT9' +
                            '49AmfGQ1lM5FTzYmyh5wl6n1v/k7CGKqkm/WLRZD94HJE+FDhJ+ERy4/nF54n6ex' +
                            'Z1Fd4eevfzE1QqNJSQIDAQAB'}
        c = HttpSigClient(key, trusted_keys)

        c.debug(True)
        c.validateResponse(False)

        res = c.postForm("http://esmo.uji.es:8090/sm/startSession")
        res = json.loads(res.text)
        sessionId = res['sessionData']['sessionId']
        self.assertIsNotNone(sessionId)
        self.assertNotEqual(sessionId, "")

        body = {
            'sessionId': sessionId,
            'variableName': 'testvar',
            'dataObject': 'testvalue',
        }
        res = c.postJson('http://esmo.uji.es:8090/sm/updateSessionData', body)
        smres = SessionMngrResponse()
        smres.json_unmarshall(res.text)
        self.assertNotEqual(smres.code, SessionMngrCode.ERROR)

        try:
            res = c.get("http://esmo.uji.es:8090/sm/endSession?sessionId=" + sessionId)
        except HttpError as err:
            self.assertEqual(True, False)
