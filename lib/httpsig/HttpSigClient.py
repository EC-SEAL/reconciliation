#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import logging
import urllib

import requests
from requests import Timeout
# This implementation is not compatible with the SessionManager (at least as is), it
# does not lowercase the names of the headers to calculate the string to sign
# from requests_http_signature import HTTPSignatureAuth
from httpsig.requests_auth import HTTPSignatureAuth
from Crypto.PublicKey import RSA

from lib.Tools import sha256_fingerprint, pretty_print_http
from lib.httpsig.HttpSig import HttpError, HttpConnectError, HttpSig


class HttpSigClient:
    class Method:
        GET = 'GET'
        POST = 'POST'

    class ContentType:
        JSON = "application/json"
        FORM = "application/x-www-form-urlencoded"

    def __init__(self, private_key, trusted_keys=None, key_id=None, retries=1):
        self.do_debug = False
        self.validate_response = True

        # Private RSA key PEM
        with open(private_key, 'rb') as keyfile:
            self.privkey = keyfile.read()

        # Dictionary of trusted public keys, key_id:public_key_b64
        if not trusted_keys:
            trusted_keys = {}
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

    def doValidateResponse(self, validate):
        self.validate_response = validate

    # We need this because the requests httpsig auth module fails to encode
    # properly the data dict when hashing (works fine for json), so we need to
    # build the form body byte string and pass it like that (also, we need to
    # establish the content-type)
    def urlencode(self, post_params: dict):
        if not post_params:
            return None
        if not isinstance(post_params, dict):
            return post_params
        return urllib.parse.urlencode(post_params).encode('utf-8')

    def get(self, url, timeout=None):
        return self.send_retry(self.Method.GET, url, timeout)

    def postForm(self, url, query=None, timeout=None):
        body = self.urlencode(query)
        return self.send_retry(self.Method.POST, url, body, self.ContentType.FORM, timeout)

    def postJson(self, url, body=None, timeout=None):
        json_str = None
        if body:
            json_str = json.dumps(body).encode('utf-8')
        return self.send_retry(self.Method.POST, url, json_str, self.ContentType.JSON, timeout)

    def send_retry(self, method, url, body=None, content_type=None, timeout=5.0):
        for i in range(0, self.retries):
            try:
                return self.send(method, url, body, content_type, timeout)
            except Exception as ex:
               logging.warning('HTTPSig client returned error (retries left: '
                               + str(self.retries - i) + '): ' + str(ex))
               if i == self.retries-1:
                   raise ex

    def send(self, method, url, body=None, content_type=None, timeout=None):

        # Headers to send (the HttpSig lib will add more)
        headers = {
            'Accept': '*/*',
        }

        # Not sure if this is required, I think it is not on the draft, but
        # the lib we use from EWP requires a digest even if no body is passed
        if not body:
            body = "".encode('utf-8')

        # Create the signature handler
        httpsig = HttpSig(private_key=self.privkey,
                          trusted_keys=self.trusted_keys,
                          key_id=self.key_id)

        # Sign the body and headers
        res = httpsig.sign(headers, body)
        auth = res['auth']
        headers = res['headers']

        args = {
            'method': method,
            'url': url,
            'auth': auth,
            'headers': headers,
        }

        if timeout:
            if not self.do_debug:
                args['timeout'] = timeout
        if method == self.Method.POST:
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

        if not http_resp:
            raise HttpError(f"Received error code {http_resp.status_code} when connecting to {url}")

        # If we expect responses to be signed, validate it
        if self.validate_response:
            httpsig.verify(http_resp.headers, http_resp.content)
            # TODO: check if I need to pass the response .content or the .text. I guess the raw content

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
