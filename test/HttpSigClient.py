#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# These tests will most probably fail for you, as they rely on a specific service being up and you
# having a RSA private key that is not on the repository.  # TODO: try to make them self-sustainable

# Before running these tests, you need urls to point to a properly functioning
# SessionManager microservice. Either substitute here the domain in the urls 
# or set sessionManager to be resolved in your /etc/hosts file to the proper domain

import hashlib
import json
import unittest
import logging

from lib.SMHandler import SMHandler
from lib.Tools import sha256_fingerprint
from lib.dto.SessionMngrResponse import SessionMngrCode, SessionMngrResponse
from lib.httpsig.HttpSig import HttpError
from lib.httpsig.HttpSigClient import HttpSigClient


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

        res = c.postForm("http://sessionManager:8090/sm/startSession")
        res = json.loads(res.text)
        sessionId = res['sessionData']['sessionId']
        self.assertIsNotNone(sessionId)
        self.assertNotEqual(sessionId, "")

        body = {
            'sessionId': sessionId,
            'variableName': 'testvar',
            'dataObject': 'testvalue',
        }
        res = c.postJson('http://sessionManager:8090/sm/updateSessionData', body)
        smres = SessionMngrResponse()
        smres.json_unmarshall(res.text)
        self.assertNotEqual(smres.code, SessionMngrCode.ERROR)

        try:
            res = c.get("http://sessionManager:8090/sm/endSession?sessionId=" + sessionId)
        except HttpError as err:
            self.assertEqual(True, False)


# TODO: use below examples to mock HTTP calls here, in SMtests, CMtests and api tests
'''

This is how you can do it (you can run this file as-is):

import requests
import unittest
from unittest import mock

# This is the class we want to test
class MyGreatClass:
    def fetch_json(self, url):
        response = requests.get(url)
        return response.json()

# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://someurl.com/test.json':
        return MockResponse({"key1": "value1"}, 200)
    elif args[0] == 'http://someotherurl.com/anothertest.json':
        return MockResponse({"key2": "value2"}, 200)

    return MockResponse(None, 404)

# Our test case class
class MyGreatClassTestCase(unittest.TestCase):

    # We patch 'requests.get' with our own method. The mock object is passed in to our test case method.
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_fetch(self, mock_get):
        # Assert requests.get calls
        mgc = MyGreatClass()
        json_data = mgc.fetch_json('http://someurl.com/test.json')
        self.assertEqual(json_data, {"key1": "value1"})
        json_data = mgc.fetch_json('http://someotherurl.com/anothertest.json')
        self.assertEqual(json_data, {"key2": "value2"})
        json_data = mgc.fetch_json('http://nonexistenturl.com/cantfindme.json')
        self.assertIsNone(json_data)

        # We can even assert that our mocked method was called with the right parameters
        self.assertIn(mock.call('http://someurl.com/test.json'), mock_get.call_args_list)
        self.assertIn(mock.call('http://someotherurl.com/anothertest.json'), mock_get.call_args_list)

        self.assertEqual(len(mock_get.call_args_list), 3)

if __name__ == '__main__':
    unittest.main()


Important Note: If your MyGreatClass class lives in a different package, say my.great.package, you have to mock my.great.package.requests.get instead of just 'request.get'. In that case your test case would look like this:

import unittest
from unittest import mock
from my.great.package import MyGreatClass

# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    # Same as above


class MyGreatClassTestCase(unittest.TestCase):

    # Now we must patch 'my.great.package.requests.get'
    @mock.patch('my.great.package.requests.get', side_effect=mocked_requests_get)
    def test_fetch(self, mock_get):
        # Same as above

if __name__ == '__main__':
    unittest.main()



'''