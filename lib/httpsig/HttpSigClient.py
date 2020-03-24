#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import logging
import time
import uuid

import requests
from requests_http_signature import HTTPSignatureAuth
#from httpsig.requests_auth import HTTPSignatureAuth, HeaderSigner
from Crypto.PublicKey import RSA

from lib.Tools import sha256_fingerprint, gmt_time, pretty_print_http


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

    def get(self, url):
        return self.send_retry(self.Method.GET, url)

    def postForm(self, url, query=None):
        return self.send_retry(self.Method.POST, url, query, self.ContentType.FORM)

    def postJson(self, url, body=None):
        return self.send_retry(self.Method.POST, url, body, self.ContentType.JSON)

    def send_retry(self, method, url, body=None, content_type=None):
        for i in range(0, self.retries):
            try:
                return self.send(method, url, body, content_type)
            except Exception as ex:
                logging.warning('HTTPSig client returned error (retries left: '
                                + str(self.retries - i) + '): ' + str(ex.__traceback__))
                # TODO: add the error message to the log
                raise ex

    def send(self, method, url, body=None, content_type=None):
        request_id = str(uuid.uuid4())
        now = gmt_time()

        headers = {
            'Date': now,
            'Original-Date': now,
            'X-Request-Id': request_id,
            'Accept-Signature': self.algorithm,
            # 'Digest': '',
        }

        sign_headers = ['(request-target)', 'Host', 'Date', 'Original-Date', 'X-Request-Id']

        '''

         sign_headers = ['(request-target)', 'Host', 'Date', 'Original-Date', 'Digest', 'X-Request-Id']

        auth = HTTPSignatureAuth(key_id='Test',
                                 secret=self.privkey,
                                 algorithm=self.algorithm,
                                 headers=sign_headers)

        #hs = HeaderSigner()
        #hs.

        print("*******")
        '''
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
        $authClient->setRequestMethod($method);

        # To sign the request
        $authClient->setKeyId($this->keyId);
        $authClient->setPrivKeyPem($this->privateKey);

        # To validate the response
        $authClient->setTrustedCertList($this->trustedKeys);

        # Request destination and contents
        $authClient->setRequestUrl($url);
        $authClient->setRequestContentType($contentType);
        if $body != None:
            $authClient->setRequestContent($body);

        $res = $authClient->sendRequest();

        if $res == NULL or $res == False:
            raise SimpleSAML_Error_Exception("Error. No response body")

        SimpleSAML_Logger::debug('Response RAW:'.$res);

        $res = json_decode($res, TRUE);
        if ($res == = False):
            logging.debug('Error parsing JSON string:'.$res);
            raise SimpleSAML_Error_Exception("Bad json");


        if ($res['code'] == = "ERROR")
            throw
            new
            SimpleSAML_Error_Exception("Remote microservice returned error code: ".$res['error']);


            SimpleSAML_Logger::debug('Response JSON:'.print_r($res, true));

            return $res;
        '''
