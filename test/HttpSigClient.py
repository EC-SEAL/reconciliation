#!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import json
import unittest
import logging

from lib.SMHandler import SMHandler
from lib.Tools import sha256_fingerprint
from lib.httpsig.HttpSigClient import HttpSigClient


class HttpSigTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(HttpSigTest, self).__init__(*args, **kwargs)
        logging.basicConfig(level=logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
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

    def test_get(self):
        key = 'data/httpsig_key.pem'
        fingerprint = '58f20aef58f63c28d95a57e5e7dd3e6971122ce35b5448acf36818874a0b2c0c'
        key = 'data/httpsig_key_esmo.pem'
        #fingerprint = '7a9ba747ab5ac50e640a07d90611ce612b7bde775457f2e57b804517a87c813b'
        trusted_keys = {'58f20aef58f63c28d95a57e5e7dd3e6971122ce35b5448acf36818874a0b2c0c':
                            'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDJBbbirvao04+n3R0rvX2Mbq+J' +
                            'JyEl06K6hWf4MarVi6YTuJWWQb3D0mkWLATBchAntTsQsj+TH8VLkVIP3YWuOeT9' +
                            '49AmfGQ1lM5FTzYmyh5wl6n1v/k7CGKqkm/WLRZD94HJE+FDhJ+ERy4/nF54n6ex' +
                            'Z1Fd4eevfzE1QqNJSQIDAQAB'}
        c = HttpSigClient(key, trusted_keys)

        # This works
        body = "aaa=bbb".encode('utf-8')
        hashlib.sha256(body)


        data = {"aaa": "bbb4", "ccc": "ddd ffff"}
        raw_form = b"aaa=bbb1&ccc=ddd"
        c.debug(True)
        c.validateResponse(False)
        # c.get("http://lab9054.inv.uji.es/")
        # c.get("http://stork.uji.es/")
        # c.get("http://lab9054.inv.uji.es/aa.php?jjj=iii")
        # c.postForm("http://lab9054.inv.uji.es/aa.php", raw_form)
        # c.postForm("http://lab9054.inv.uji.es/aa.php?jjj=iii", data)
        # c.postJson("http://lab9054.inv.uji.es/aa.php", data)

        #c.get("https://www.google.com/")
        #data = b'hello=world'
        #c.postForm("http://lab9054.inv.uji.es/aa.php", query=data)
        data = {"hello": "world"}
        #data = None
        #c.postJson("http://lab9054.inv.uji.es/aa.php", data)
        #c.postForm("http://lab9054.inv.uji.es/aa.php")
        # c.postJson("http://esmo.uji.es:8090/sm/startSession", data)
#         print("-------------------start session----------------------")
#         res = c.postForm("http://esmo.uji.es:8090/sm/startSession")
#         print(res.text)
#         res = json.loads(res.text)
#         sessionId = res['sessionData']['sessionId']
#         print("sessionID:" + sessionId)
#         print("------------------------------------------------------")
#
#
# #getsession  "?varName=" + + "varValue=".urlencode($value);
#
#
#         print("-------------------end session----------------------")
#         res = c.get("http://esmo.uji.es:8090/sm/endSession?sessionId=" + sessionId)
#         print(res.status_code)
#         print("------------------------------------------------------")
#
#
#         sm = SMHandler()

        data = {'hello': 'world'}
        #data = None
        c.postJson("http://lab9054.inv.uji.es/aa.php", data)





        # TODO: SEGUIR implement better tests. then implement server part on the api as a decorator
        #  (and the SM mstoken validation, also as a decorator)
        self.assertEqual(1, 1)
