#!/usr/bin/python
# -*- coding: UTF-8 -*-
import base64
import hashlib
import logging
import uuid

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


class HttpSig:

    class Algorithm:
        SHA256 = 'sha256'
        RSA_SHA256 = 'rsa-sha256'

    def __init__(self, private_key, trusted_keys: {}, key_id=None):
        self.do_debug = False
        self.algorithm = self.Algorithm.RSA_SHA256
        self.digest_algorithm = self.Algorithm.SHA256

        # Private RSA key PEM
        try:
            with open(private_key, 'rb') as keyfile:
                self.privkey = keyfile.read()
        except OSError:
            # Maybe it has been passed as a string
            self.privkey = private_key

        # Dictionary of trusted public keys, key_id:public_key_b64
        self.trusted_keys = trusted_keys

        # RSA Public key
        key = RSA.import_key(self.privkey)
        self.pubkey = key.publickey().export_key().decode("utf-8")

        # If no key_id is defined, use sha256 fingerprint
        self.key_id = key_id
        if not self.key_id:
            self.key_id = sha256_fingerprint(self.pubkey)

    def debug(self, debug):
        self.do_debug = debug

    def _base64_digest(self, content):
        hash_alg = None
        if self.digest_algorithm == self.Algorithm.SHA256:
            hash_alg = hashlib.sha256
        digest = hash_alg(content).digest()
        return base64.b64encode(digest).decode()

    # Receive headers, body, headers to sign
    #   return auth object and modified headers
    def sign(self, headers: dict, body=None, more_sign_headers=None):
        now = gmt_time()

        # Add a request ID, if not any
        if 'X-Request-Id' not in headers:
            request_id = str(uuid.uuid4())
            headers['X-Request-Id'] = request_id

        # Add headers needed by HTTPSig
        headers['Date'] = now
        headers['Original-Date'] = now
        headers['Accept-Signature'] = self.algorithm

        # Which headers will be signed
        sign_headers = ['(request-target)', 'Host', 'Date', 'Original-Date', 'Digest', 'X-Request-Id']

        # Add other headers to sign the user might want to add
        if more_sign_headers:
            for h in more_sign_headers:
                if h not in sign_headers:
                    sign_headers.append(h)

        # Not sure if this is required, I think it is not on the draft, but
        # the lib we use from EWP requires a digest even if no body is passed
        if not body:
            body = "".encode('utf-8')

        # Calculate body digest, even if no body is passed
        if "Digest" not in sign_headers:
            sign_headers.append("Digest")
        digest = self._base64_digest(body)
        logging.debug("Digest: " + digest)
        headers["Digest"] = "SHA-256=" + digest

        logging.debug("Headers: " + str(headers))
        logging.debug("Sign-Headers: " + str(sign_headers))

        # Create the signature handler
        auth = HTTPSignatureAuth(key_id=self.key_id,
                                 #key=self.privkey,
                                 secret=self.privkey,
                                 algorithm=self.algorithm,
                                 headers=sign_headers)

        return {'auth': auth, 'headers': headers}

    # for a given key_id, returns the public key that must be used to verify a signature
    def _default_trusted_keys_resolver(self, key_id, algorithm):
        if key_id not in self.trusted_keys:
            return None
        return self.trusted_keys[key_id]

    def verify(self, headers, body=None, key_id=None):
        # TODO: implement
        # from httpsig.verify import Verifier, HeaderVerifier
        # Implement validation of the digest:
        #   get the algorithm from the header,
        #   digest body,
        #   compare with digest in header
        # Validate signature in headers:
        #   HeaderVerifier.__init__(self, headers, secret, required_headers=None, method=None,
        #                  path=None, host=None, sign_header='authorization'):
        #   Then call self.verify(), will return true/false [might raise HttpSigException for unsuported alg]
        # See if I need a trusted key resolver, or if I use it for something,
        #   but in this case, they expect the pubkey (in 'secret' field) to be there,
        #   so, just do the selection by key_id inside here, searching the key_id in
        #   the collection, or defaulting to the fingerprint
        # If validation fails, raise something, handle it at link.py
        #         """
        #         Instantiate a HeaderVerifier object.
        #
        #         :param headers:             A dictionary of headers from the HTTP
        #             request.
        #         :param secret:              The HMAC secret or RSA *public* key.
        #         :param required_headers:    Optional. A list of headers required to
        #             be present to validate, even if the signature is otherwise valid.
        #             Defaults to ['date'].
        #         :param method:              Optional. The HTTP method used in the
        #             request (eg. "GET"). Required for the '(request-target)' header.
        #         :param path:                Optional. The HTTP path requested,
        #             exactly as sent (including query arguments and fragments).
        #             Required for the '(request-target)' header.
        #         :param host:                Optional. The value to use for the Host
        #             header, if not supplied in :param:headers.
        #         :param sign_header:         Optional. The header where the signature is.
        #             Default is 'authorization'.
        #         """
        return False
