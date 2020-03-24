from lib.dto.Dto import DTO


class ApiConnectionType:
    POST = 'post'
    GET = 'get'


class MsMetadata(DTO):
    def __init__(self):
        self.msId = str
        self.authorisedMicroservices = [str]
        self.rsaPublicKeyBinary = str
        self.publishedAPI = [ApiType()]


class ApiType(DTO):
    def __init__(self):
        self.apiClass = str
        self.apiCall = str
        self.apiConnectionType = str
        self.apiEndpoint = str
