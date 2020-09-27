import json
import logging
from urllib.parse import urlencode

from lib import Tools
from lib.dto import MsMetadata
from lib.dto.Dataset import Dataset
from lib.dto.Dto import BadDtoInput
from lib.dto.LinkRequest import LinkRequest
from lib.dto.SessionMngrResponse import SessionMngrCode, SessionMngrResponse
from lib.dto.StoreEntry import StoreEntry, StoreEntryList
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
    # TODO: add something here that parses the domain (and port? just domain I think)
    #  part of the retrieved url, as a kind of pre-dns resolver. This way, we can
    #  change the domain in there for a given domain or ip. Test this by commenting
    #  the etc/hosts stuff, see that fails, then pass this and see it work.
    #  use urllib.parse 
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

# The new dataStore API implemented on the SM

    # Erases all the contents of the datastore if exists and sets it ready for operation
    def resetDatastore(self):
        url = self._getApiUrl('SM', 'datastoreStart')  # TODO: set the proper identifiers on the ms.json

        # We assume the session exists before the dataStore is
        # created, but the call also supports creating a dataStore
        # which is independent from the session, by not passing a sessionID
        queryParams = {'sessionId': self.sessId}

        res = self.httpsig.postForm(url, queryParams)
        res = self._parseResponse(res)
        logging.debug('resetDatastore Response: ' + str(res))

        if res.code == SessionMngrCode.ERROR:
            raise SessionManagerError("Datastore reset failed: " + str(res.error))

        if not res.sessionData.sessionId:
            raise SessionManagerError("No sessionID on response (should be the same)")
        self.sessId = res.sessionData.sessionId

        return self.sessId

    # TODO: SEGUIR

    def addDatastoreEntry(self, id, type, data):

        logging.debug('Writing dataStore entry. id: ' + id + ' type: '
                      + type + ' data: ' + str(data))

        json_value = data
        if isinstance(data, dict):
            json_value = json.dumps(data)
        if not json_value:
            raise SessionManagerError("Error encoding data of entry in json: " + data)

        body = {
            'sessionId': self.sessId,
            'id': id,
            'type': type,
            'data': json_value,
        }

        url = self._getApiUrl('SM', 'datastoreAdd')

        logging.debug('Body sent:' + str(body))
        res = self.httpsig.postForm(url, body)
        res = self._parseResponse(res)
        logging.debug('Received response:' + str(res))

        if res.code == SessionMngrCode.ERROR:
            raise SessionManagerError("storeEntry -" + id + "-" + type + "- write failed: " + str(res.error))

    def deleteDatastoreEntry(self, id):

        logging.debug('Deleting dataStore entry. id: ' + id)

        body = {
            'sessionId': self.sessId,
            'id': id,
        }

        url = self._getApiUrl('SM', 'datastoreDelete')

        logging.debug('Body sent:' + str(body))
        res = self.httpsig.postForm(url, body)
        res = self._parseResponse(res)
        logging.debug('Received response:' + str(res))

        if res.code == SessionMngrCode.ERROR:
            raise SessionManagerError("storeEntry -" + id + "- delete failed: " + str(res.error))

    def getDatastoreEntry(self, id):
        logging.debug('Requesting datastore entry:' + id)
        queryParams = {'sessionId': self.sessId,
                       'id': id,
        }
        url = self._getApiUrl('SM', 'datastoreGet') + "?" + urlencode(queryParams)

        res = self.httpsig.get(url)
        res = self._parseResponse(res)
        logging.debug('Received response:' + str(res))

        if res.code != SessionMngrCode.OK:
            raise SessionManagerError("store entry fetch failed: " + str(res.error))

        if not res.additionalData:
            raise SessionManagerError("No additionalData on response")

        storeObj = StoreEntry()
        storeObj.json_unmarshall(res.additionalData)

        if not storeObj.id:
            raise SessionManagerError("store entry fetch failed: no data id")
        if not storeObj.type:
            raise SessionManagerError("store entry fetch failed: no data type")
        if not storeObj.data:
            raise SessionManagerError("store entry fetch failed: no data object")

        if storeObj.type == "linkRequest":  # TODO: parametrise and check the types of object
            obj = LinkRequest()
        elif storeObj.type == "dataSet":
            obj = Dataset()
        else:
            raise SessionManagerError("Unknown store entry type: " + storeObj.type)

        obj.json_unmarshall(storeObj.data)
        storeObj.data = obj

        return storeObj

    # Return all entries of a type (or all entries if type is none)
    def searchDatastoreEntries(self, type=None):
        if not type:
            logging.debug('Searching all datastore entries')
        else:
            logging.debug('Searching datastore entries of type:' + type)
        queryParams = {'sessionId': self.sessId,
                       'type': type,
                       }
        url = self._getApiUrl('SM', 'datastoreSearch') + "?" + urlencode(queryParams)

        res = self.httpsig.get(url)
        res = self._parseResponse(res)
        logging.debug('Received response:' + str(res))

        if res.code != SessionMngrCode.OK:
            raise SessionManagerError("store entry search failed: " + str(res.error))

        if not res.additionalData:
            raise SessionManagerError("No additionalData on response")

        storeObjList = StoreEntryList()
        storeObjList.json_unmarshall(res.additionalData)

        idx = 0
        for storeObj in storeObjList.entries:
            if not storeObj.id:
                raise SessionManagerError("store entry search failed: no data id at idx " + str(idx))
            if not storeObj.type:
                raise SessionManagerError("store entry search failed: no data type at idx " + str(idx))
            if not storeObj.data:
                raise SessionManagerError("store entry search failed: no data object at idx " + str(idx))

            if storeObj.type == "linkRequest":  # TODO: parametrise and check the types of object
                obj = LinkRequest()
            elif storeObj.type == "dataSet":
                obj = Dataset()
            else:
                raise SessionManagerError("Unknown store entry type: " + storeObj.type + " at idx " + str(idx))

            obj.json_unmarshall(storeObj.data)
            storeObj.data = obj
            idx += 1

        return storeObjList
