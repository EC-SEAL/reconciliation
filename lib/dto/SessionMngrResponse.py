from lib.dto.Dto import DTO


class SessionMngrCode:
    OK = 'OK'
    ERROR = 'ERROR'
    NEW = 'NEW'


class SessionMngrResponse(DTO):
    def __init__(self):
        self.additionalData = str
        self.code = str
        self.error = str
        self.sessionData = MngrSessionTO()


class MngrSessionTO(DTO):
    def __init__(self):
        self.sessionId = str
        self.sessionVariables = {}
