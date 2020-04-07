import json
import logging
from urllib.parse import urlencode

from lib import Tools
from lib.dto import MsMetadata
from lib.dto.Dto import BadDtoInput
from lib.dto.SessionMngrResponse import SessionMngrCode, SessionMngrResponse
from lib.httpsig.HttpSig import HttpSig, HttpError
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

        self.httpsig.doValidateResponse(validate)

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

    def _parseResponse(self, requests_resp):
        try:
            smres = SessionMngrResponse()
            smres.json_unmarshall(requests_resp.text)
        except BadDtoInput:
            raise SessionManagerError("Bad Response object. Not a SessionMgrResponse")
        return smres

    def startSession(self):
        url = self._getApiUrl('SM', 'startSession')

        res = self.httpsig.postForm(url)
        res = self._parseResponse(res)
        logging.debug('startSession Response: ' + str(res))

        if res.code == SessionMngrCode.ERROR:
            raise SessionManagerError("Session start failed: " + str(res.error))

        if not res.sessionData.sessionId:
            raise SessionManagerError("No sessionID on response")
        self.sessId = res.sessionData.sessionId

        return self.sessId

    def getSession(self, variable, value):
        logging.debug('Requesting session variable (None means whole session object):' + variable)
        url = self._getApiUrl('SM', 'getSession')
        url = url + "?" + urlencode({'varName': variable, 'varValue': value})

        res = self.httpsig.get(url)
        res = self._parseResponse(res)
        logging.debug('getSession Response: ' + str(res))

        if not res.sessionData.sessionId:
            raise SessionManagerError("No sessionID on response")
        self.sessId = res.sessionData.sessionId
        return self.sessId

    def endSession(self):
        url = self._getApiUrl('SM', 'endSession')
        url = url + "?" + urlencode({'sessionId': self.sessId})
        try:
            res = self.httpsig.get(url)
        except HttpError as err:
            logging.debug('endSession Failed: ' + str(err))
            raise SessionManagerError("Session end failed: " + str(err))

    # If name = NULL, get the whole session object
    def getSessionVar(self, name=None):
        logging.debug('Requesting session variable (None means whole session object):' + name)
        queryParams = {'sessionId': self.sessId}
        if name is not None and isinstance(name, str):
            queryParams["variableName"] = name
        url = self._getApiUrl('SM', 'getSessionData') + "?" + urlencode(queryParams)

        res = self.httpsig.get(url)
        res = self._parseResponse(res)
        logging.debug('Received response:' + str(res))

        if res.code != SessionMngrCode.OK:
            raise SessionManagerError("Variable fetch failed: " + str(res.error))

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
                      + name + ' with value: ' + str(value))

        json_value = value
        if isinstance(value, dict):
            json_value = json.dumps(value)
        if not json_value:
            raise SessionManagerError("Error encoding value of var name in json: " + value)

        body = {
            'sessionId': self.sessId,
            'variableName': name,
            'dataObject': json_value,
        }

        url = self._getApiUrl('SM', 'updateSessionData')

        logging.debug('Body sent:' + str(body))
        res = self.httpsig.postJson(url, body)
        res = self._parseResponse(res)
        logging.debug('Received response:' + str(res))

        if res.code == SessionMngrCode.ERROR:
            raise SessionManagerError("Variable -" + name + "- write failed: " + str(res.error))

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
        res = self._parseResponse(res)
        logging.debug('Received response:' + str(res))

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
        res = self._parseResponse(res)
        logging.debug('Received response:' + str(res))

        if res.code != SessionMngrCode.OK:
            raise SessionManagerError("Token validation failed: " + res.error)

        if not res.sessionData.sessionId:
            raise SessionManagerError("No sessionID on response")
        self.sessId = res.sessionData.sessionId

        logging.debug('sessionID retrieved from token: ' + res.sessionData.sessionId)
        if res.additionalData:
            logging.debug('it had additionalData: ' + res.additionalData)

        return res.additionalData
