from lib.dto.Dto import DTO


class RequestParameters(DTO):
    def __init__(self):
        self.id = str
        self.type = str
        self.data = str
        self.sessionId = str
