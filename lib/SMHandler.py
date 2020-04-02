import json
import logging
from urllib.parse import urlencode

from lib import Tools
from lib.dto import MsMetadata
from lib.dto.Dto import BadDtoInput
from lib.dto.SessionMngrResponse import SessionMngrCode, SessionMngrResponse
from lib.httpsig.HttpSigClient import HttpSigClient


class EndpointNotFound(BaseException):
    def __init__(self, message):
        self.message = message


class SessionManagerError(BaseException):
    def __init__(self, message):
        self.message = message


class SMHandler:

    def __init__(self, smMetadata: MsMetadata, key, key_id=None, retries=1, validate=True):
        # Session Identifier
        self.sessId = None
        # Key ID of this client
        self.key_id = key_id
        # Key of this client
        self.key = key
        # Send retries
        self.retries = retries
        # Metadata of the Session Manager microservice
        self.smMetadata = smMetadata

        trusted_keys = {Tools.sha256_fingerprint(smMetadata.rsaPublicKeyBinary): smMetadata.rsaPublicKeyBinary}

        # HTTPSig client instance
        self.httpsig = HttpSigClient(self.key, trusted_keys,
                                     key_id=self.key_id, retries=self.retries)

        self.httpsig.validateResponse(validate)

    def getSessID(self):
        return self.sessId

    def setSessID(self, sessId):
        self.sessId = sessId

    def _getApiUrl(self, apiClass, apiCall):
        for api in self.smMetadata.publishedAPI:
            if api.apiClass == apiClass and api.apiCall == apiCall:
                return api.apiEndpoint
        raise EndpointNotFound("API call " + apiCall + " from class " + apiClass +
                               " not found on any entry in the " +
                               self.smMetadata.msId + " microservice metadata object")

    def startSession(self):
        url = self._getApiUrl('SM', 'startSession')
        print("*****", url)
        res = self.httpsig.postForm(url)
        print("******", res.status_code)
        try:
            res = SessionMngrResponse().unmarshall(res)
        except BadDtoInput:
            raise SessionManagerError("Bad Response object. Not a SessionMgrResponse")

        if res.code == SessionMngrCode.ERROR:
            raise SessionManagerError("Session start failed: " + res.error)

        if not res.sessionData.sessionId:
            raise SessionManagerError("No sessionID on response")
        self.sessId = res.sessionData.sessionId

        return self.sessId

    def getSession(self, variable, value):
        logging.debug('Requesting session variable (None means whole session object):' + variable)
        url = self._getApiUrl('SM', 'getSession')
        url = url + "?" + urlencode({'varName': variable, 'varValue': value})

        res = self.httpsig.get(url)

        if not res.additionalData:
            raise SessionManagerError("No sessionID on response")
        self.sessId = res.additionalData

    def endSession(self):
        url = self._getApiUrl('SM', 'endSession')
        url = url + "?" + urlencode({'sessionId': self.sessId})

        res = self.httpsig.get(url)

        if res.code == SessionMngrCode.ERROR:
            raise SessionManagerError("Session end failed: " + res.error)

    # If name = NULL, get the whole session object
    def getSessionVar(self, name=None):
        logging.debug('Requesting session variable (None means whole session object):' + name)
        queryParams = {'sessionId': self.sessId}
        if name is not None and isinstance(name, str):
            queryParams["variableName"] = name
        url = self._getApiUrl('SM', 'getSessionData') + "?" + urlencode(queryParams)

        res = self.httpsig.get(url)
        logging.debug('Received response:' + res)

        if res.code != SessionMngrCode.OK:
            raise SessionManagerError("Variable fetch failed: " + res.error)

        if not res.sessionData:
            raise SessionManagerError("No sessionData on response")

        if not res.sessionData.sessionVariables:
            raise SessionManagerError("No sessionVariables on response")

        if name:
            if not res.sessionData.sessionVariables[name]:
                # raise SessionManagerError("Variable 'name' not on response")
                return None

            obj = res.sessionData.sessionVariables[name]
        else:
            obj = res.sessionData.sessionVariables

        return obj

    # If name = NULL, write the whole session object public function
    def writeSessionVar(self, value, name=None):

        logging.debug('Writing session variable (null means whole session object):'
                      + name + ' with value: ' + value)

        json_value = json.dumps(value)
        if not json_value:
            raise SessionManagerError("Error encoding value of var name in json: " + value)

        body = '{' + \
               f'"sessionId": "{self.sessId}",' + \
               f'"variableName": "{name}",' + \
               f'"dataObject": {json_value}' + \
               '}'

        url = self._getApiUrl('SM', 'updateSessionData')

        logging.debug('Body sent:' + body)
        res = self.httpsig.postJson(url, body)
        logging.debug('Received response:' + res)

        if res.code == SessionMngrCode.ERROR:
            raise SessionManagerError("Variable -" + name + "- write failed: " + res.error)

    # The msId of the destination microservice
    def generateToken(self, origin: str, destination: str, data=None):

        if not origin or origin == '':
            raise SessionManagerError("origin ms not defined")
        if not destination or destination == '':
            raise SessionManagerError("destination ms not defined")

        queryParams = {'sessionId': self.sessId,
                       'sender': origin,
                       'receiver': destination}
        if data:
            queryParams['data'] = data

        url = self._getApiUrl('SM', 'generateToken') + "?" + urlencode(queryParams)

        logging.debug('Requesting token:' + url)
        res = self.httpsig.get(url)
        logging.debug('Received response:' + res)

        if res.code == SessionMngrCode.ERROR:
            raise SessionManagerError("Token generation failed: " + res.error)

        if not res.additionalData:
            raise SessionManagerError("No token on response")

        return res.additionalData

    # If validated, session token will be returned
    def validateToken(self, token):

        if not token or token == '':
            raise SessionManagerError("token not passed")

        url = self._getApiUrl('SM', 'validateToken') + "?" + urlencode({'token': token})

        res = self.httpsig.get(url)
        if not res:
            raise SessionManagerError("Bad response for validateToken")

        if res.code != SessionMngrCode.OK:
            raise SessionManagerError("Token validation failed: " + res.error)

        if not res.sessionData.sessionId:
            raise SessionManagerError("No sessionID on response")
        self.sessId = res.sessionData.sessionId

        logging.debug('sessionID retrieved from token: ' + res.sessionData.sessionId)
        logging.debug('additionalData: ' + res.additionalData)

        return res.additionalData
