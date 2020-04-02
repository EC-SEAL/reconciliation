#!/usr/bin/python
# -*- coding: UTF-8 -*-
import base64
import hashlib
import json
import logging
import urllib
import uuid

import requests
from requests import Timeout
# This implementation is not compatible with the SessionManager (at least as is), it
# does not lowercase the names of the headers to calculate the string to sign
# from requests_http_signature import HTTPSignatureAuth
from httpsig.requests_auth import HTTPSignatureAuth
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

    def __init__(self, private_key, trusted_keys: {}, key_id=None, retries=1):
        self.do_debug = False
        self.validate_response = True
        self.algorithm = self.Algorithm.RSA_SHA256
        self.digest_algorithm = self.Algorithm.SHA256

        # Private RSA key PEM
        with open(private_key, 'rb') as keyfile:
            self.privkey = keyfile.read()

        # Dictionary of trusted public keys, key_id:public_key_b64
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

    def debug(self, debug):
        self.do_debug = debug

    def validateResponse(self, validate):
        self.validate_response = validate

    # We need this because the requests httpsig auth module fails to encode
    # properly the data dict when hashing (works fine for json), so we need to
    # build the form body byte string and pass it like that (also, we need to
    # establish the content-type)
    def urlencode(self, post_params: dict):
        print(post_params)
        if not post_params:
            return None
        if not isinstance(post_params, dict):
            return post_params
        return urllib.parse.urlencode(post_params).encode('utf-8')

    def get(self, url, timeout=None):
        return self.send_retry(self.Method.GET, url, timeout)

    def postForm(self, url, query=None, timeout=None):

        # TODO: EWP implementation of HTTPSig is a bit lame. It always requires
        #  the digest header to be there, even if there is no body. Let's first try
        #  to digest the empty string, or else, send always a dummy. Also test sending a json body, as it is a dict. maybe i
        #  have to urlencode to calculate
        # if not body:
        #     body = '{"hello": "world"}'.encode('utf-8')
        body = self.urlencode(query)
        return self.send_retry(self.Method.POST, url, body, self.ContentType.FORM, timeout)

    def postJson(self, url, body=None, timeout=None):
        json_str = None
        if body:
            json_str = json.dumps(body).encode('utf-8')
        return self.send_retry(self.Method.POST, url, json_str, self.ContentType.JSON, timeout)

    def _base64_digest(self, content):
        hash_alg = None
        if self.digest_algorithm == self.Algorithm.SHA256:
            hash_alg = hashlib.sha256
        digest = hash_alg(content).digest()

        return base64.b64encode(digest).decode()

    def send_retry(self, method, url, body=None, content_type=None, timeout=None):
        if not timeout:
            timeout = 3.0
        for i in range(0, self.retries):
            return self.send(method, url, body, content_type, timeout)
            # try:
            #    return self.send(method, url, body, content_type, timeout)
            # except Exception as ex:
            #    logging.warning('HTTPSig client returned error (retries left: '
            #                    + str(self.retries - i) + '): ' + str(ex))
            #    raise ex

    def send(self, method, url, body=None, content_type=None, timeout=None):
        request_id = str(uuid.uuid4())
        now = gmt_time()

        # Headers to send
        headers = {
            'Accept': '*/*',
            'Date': now,
            'Original-Date': now,
            'X-Request-Id': request_id,
            'Accept-Signature': self.algorithm,
        }

        # Which headers will be signed (Digest will be added by the lib if there is a body)
        sign_headers = ['(request-target)', 'Host', 'Date', 'Original-Date', 'Digest', 'X-Request-Id']  # TODO maybe tolower?

        if not body:
            body = "".encode('utf-8')

        # Calculate body digest, if any body is passed
        #if body:
        if "Digest" not in sign_headers:
            sign_headers.append("Digest")
        #digest = self._base64_digest(b"\r\n"+body)
        digest = self._base64_digest(body)
        print(digest)
        headers["Digest"] = "SHA-256=" + digest

        print(headers)
        print(sign_headers)

        # Create the signature handler
        auth = HTTPSignatureAuth(key_id=self.key_id,
                                 #key=self.privkey,
                                 secret=self.privkey,
                                 algorithm=self.algorithm,
                                 headers=sign_headers)

        args = {
            'method': method,
            'url': url,
            'auth': auth,
            'headers': headers,
        }

        if timeout:
            if not self.do_debug:
                args['timeout'] = timeout
        if method == self.Method.POST: # and body:  # TODO: see if we bring this back for something else
            # Set the content type
            headers['Content-Type'] = content_type
            args['data'] = body

        http_resp = None
        try:
            http_resp = self.request(**args)
        except ValueError as e:
            logging.warning(f'HTTPSig client error: {e}')
            raise HttpConnectError(f'HTTPSig client error: {e}')
        except Timeout:
            logging.warning(f'HTTPSig request to {url} timed out')
            raise HttpConnectError(f'HTTPSig client timed out')

        # TODO: I guess the same validation function can be used over responses.
        #  Try to check with a server signing the responses. Maybe I need the other lib
        #  to do the raw signing of the response? In that case, maybe I need another lib
        #  to implement the digest (or DIY)
        if self.validate_response:
            HTTPSignatureAuth.verify(http_resp, key_resolver=self.trusted_keys_resolver)

        if not http_resp:
            raise HttpError(f"Received error code {http_resp.status_code} when connecting to {url}")

        # # Get response body, as a dict if json, as text if otherwise
        # try:
        #     ret = http_resp.json()  # Returns the parsed json, if any
        # except ValueError:  # Not JSON
        #     # ret = http_resp.content  # Returns bytes of the content
        #     ret = http_resp.text  # Returns string of the content (in the incoming encoding)
        #
        # return ret
        return http_resp

    def request(self, **kwargs):
        # Production requests
        if not self.do_debug:
            return requests.request(**kwargs)
        # Debug requests
        raw = requests.Request(**kwargs)
        prepared = raw.prepare()
        self.pretty_print_post(prepared)
        s = requests.Session()
        res = s.send(prepared)
        s.close()
        return res

    # log the raw HTTP Request
    def pretty_print_post(self, req):
        req_row = req.method + ' ' + req.url
        headers = '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items())
        body = req.body or ""
        logging.debug('-------HTTP REQUEST-------\n' + f'{req_row}\n{headers}\n\n{body}')

    # for a given key_id, returns the public key that must be used to verify a signature
    def trusted_keys_resolver(self, key_id, algorithm):
        if key_id not in self.trusted_keys:
            return None
        return self.trusted_keys[key_id]
