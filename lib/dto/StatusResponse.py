from lib.dto.Dto import DTO


# primaryCode:
# - PENDING
# - LOCKED
# - ACCEPTED
# - REJECTED
class StatusResponse(DTO):
    def __init__(self):
        self.primaryCode = str
        self.secondaryCode = str
        self.message = str
