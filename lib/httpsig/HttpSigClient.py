#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import logging
import time
import urllib
import uuid

import requests
from requests import Timeout
from requests_http_signature import HTTPSignatureAuth
# from httpsig.requests_auth import HTTPSignatureAuth, HeaderSigner
from Crypto.PublicKey import RSA

from lib.Tools import sha256_fingerprint, gmt_time, pretty_print_http


class HttpError(Exception):
    def __init__(self, message):
        self.message = message


class HttpConnectError(Exception):
    def __init__(self, message):
        self.message = message


class HttpSigClient:

    class Method:
        GET = 'GET'
        POST = 'POST'

    class ContentType:
        JSON = "application/json"
        FORM = "application/x-www-form-urlencoded"

    class Algorithm:
        SHA256 = 'sha256'
        RSA_SHA256 = 'rsa-sha256'

    def __init__(self, private_key, trusted_keys: [], key_id=None, retries=1):

        self.algorithm = self.Algorithm.RSA_SHA256

        # Private RSA key PEM
        with open(private_key, 'rb') as keyfile:
            self.privkey = keyfile.read()

        # List of trusted public keys
        self.trusted_keys = trusted_keys

        # HTTP Send retries
        self.retries = retries

        # RSA Public key
        key = RSA.import_key(self.privkey)
        self.pubkey = key.publickey().export_key().decode("utf-8")

        # If no key_id is defined, use sha256 fingerprint
        self.key_id = key_id
        if not self.key_id:
            self.key_id = sha256_fingerprint(self.pubkey)

    # We need this because the requests httpsig auth module fails to encode
    # properly the data dict when hashing (works fine for json), so we need to
    # build the form body byte string and pass it like that (also, we need to
    # establish the content-type)
    def dict_to_form(self, post_params: dict):
        return urllib.parse.urlencode(post_params).encode('utf-8')

    def get(self, url, timeout=None):
        return self.send_retry(self.Method.GET, url, timeout)

    def postForm(self, url, query=None, timeout=None):
        return self.send_retry(self.Method.POST, url, query, self.ContentType.FORM, timeout)

    def postJson(self, url, body=None, timeout=None):
        return self.send_retry(self.Method.POST, url, body, self.ContentType.JSON, timeout)

    def send_retry(self, method, url, body=None, content_type=None, timeout=None):
        if not timeout:
            timeout = 3.0
        for i in range(0, self.retries):
            try:
                return self.send(method, url, body, content_type, timeout)
            except Exception as ex:
                logging.warning('HTTPSig client returned error (retries left: '
                                + str(self.retries - i) + '): ' + str(ex.__traceback__))
                # TODO: add the error message to the log
                raise ex

    def send(self, method, url, body=None, content_type=None, timeout=None):
        request_id = str(uuid.uuid4())
        now = gmt_time()

        # Headers to send
        headers = {
            'Date': now,
            'Original-Date': now,
            'X-Request-Id': request_id,
            'Accept-Signature': self.algorithm,
            # 'Digest': '',
        }

        # Which headers will be signed (Digest will be added by the lib if there is a body)
        sign_headers = ['(request-target)', 'Host', 'Date', 'Original-Date', 'X-Request-Id']

        # Create the signature handler
        auth = HTTPSignatureAuth(key_id=self.key_id,
                                 key=self.privkey,
                                 algorithm=self.algorithm,
                                 headers=sign_headers)

        args = {
            'method': method,
            'url': url,
            'auth': auth,
            'headers': headers,
            'timeout': timeout,
        }

        if timeout:
            args['timeout'] = timeout
        if method == self.Method.POST:
            # Set the content type
            headers['Content-Type'] = content_type

            if content_type == self.ContentType.JSON:
                args['json'] = body
            if content_type == self.ContentType.FORM:
                args['data'] = body  # b"aaa=bbb"  # TODO implement dict to query str

        http_resp = None
        try:
            http_resp = requests.request(**args)

            # TODO: Validate response signature

        except ValueError as e:
            logging.warning(f'HTTPSig client error: {e}')
            raise HttpConnectError(f'HTTPSig client error: {e}')
        except Timeout:
            logging.warning(f'HTTPSig request to {url} timed out')
            raise HttpConnectError(f'HTTPSig client timed out')

        if not http_resp:
            raise HttpError(f"Received error code {http_resp.status_code} when connecting to {url}")

        # Get response body, as a dict if json, as text if otherwise
        try:
            ret = http_resp.json()  # Returns the parsed json, if any
        except ValueError:  # Not JSON
            # ret = http_resp.content  # Returns bytes of the content
            ret = http_resp.text  # Returns string of the content (in the incoming encoding)

        return ret


'''

# sign_headers = ['(request-target)', 'Host', 'Date', 'Original-Date', 'Digest', 'X-Request-Id']

# auth = HTTPSignatureAuth(key_id=self.key_id,
#                          secret=self.privkey,
#                          algorithm=self.algorithm,
#                          headers=sign_headers)
# headers['Content-Type'] = 'application/x-www-form-urlencoded'
# requests.request('POST', "http://lab9054.inv.uji.es/aa.php", data=b"aaa=bbb", headers=headers)

 #hs = HeaderSigner()
 #hs.

 print("*******")

auth = HTTPSignatureAuth(key=self.privkey, key_id=self.key_id, algorithm=self.algorithm, headers=sign_headers)
#authClient = requests.Request(method, url, auth=auth, headers=headers, json={"key": "value"})
#prepared = authClient.prepare()
# authClient = requests.Request('POST', url, auth=auth, headers=headers, json={"key": "value"})
data = {'aaa': 'bbb'}
#authClient = requests.Request('POST', url, auth=auth, headers=headers, data=data)

headers['Content-Type'] = 'application/x-www-form-urlencoded'
authClient = requests.request(method, "http://lab9054.inv.uji.es/aa.php", auth=auth,
                              headers=headers, data=b"aaa=bbb")
#prepared = authClient.prepare()
#pretty_print_http(prepared)
# TODO: seguir. Si le paso el bytestring, no pone el content type form, creo (ver si puedo dump las cabeceras)
#requests.request('POST', "http://lab9054.inv.uji.es/aa.php", data=b"aaa=bbb",
#                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
# TODO esto de arriba funciona con post, pasando una bytestrung y con el content type, ajustar y probar
# TODO: verificado. Como está ahora, en post, me envía el body, firmado, etc. Falta ver que esté bien y valide.
# Implementar validador? probar contra SM? primero param,wtrizar bien, para que se añada el content type y
# se contruya el body como toca. Probar tb con la otra librería a ver si manda el digest o no, Si lo manda, jusar la otra
'''

