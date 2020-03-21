from lib.dto.Dto import DTO


class StatusCodes:
    PENDING = "PENDING"
    LOCKED = "LOCKED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class StatusResponse(DTO):
    def __init__(self):
        self.primaryCode = str
        self.secondaryCode = str
        self.message = str
