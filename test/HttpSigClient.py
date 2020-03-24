#!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import unittest
import logging

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
        trusted_keys = ['MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDJBbbirvao04+n3R0rvX2Mbq+J' +
                        'JyEl06K6hWf4MarVi6YTuJWWQb3D0mkWLATBchAntTsQsj+TH8VLkVIP3YWuOeT9' +
                        '49AmfGQ1lM5FTzYmyh5wl6n1v/k7CGKqkm/WLRZD94HJE+FDhJ+ERy4/nF54n6ex' +
                        'Z1Fd4eevfzE1QqNJSQIDAQAB']
        c = HttpSigClient(key, trusted_keys)


        body = "aaa=bbb".encode('utf-8')
        hashlib.sha256(body)

        # c.get("http://lab9054.inv.uji.es/")
        c.get("http://stork.uji.es/")
