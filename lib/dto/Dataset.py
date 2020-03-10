from lib.dto.Dto import DTO


class Dataset(DTO):
    def __init__(self):
        self.id = str
        self.type = str
        self.categories = [str]
        self.issuerId = str
        self.subjectId = str
        self.loa = str
        self.issued = str
        self.expiration = str
        self.attributes = [Attribute()]
        self.properties = {}

class Attribute(DTO):
    def __init__(self):
        self.name = str
        self.friendlyName = str
        self.encoding = str
        self.language = str
        self.mandatory = bool
        self.values = [str]