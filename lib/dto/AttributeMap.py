from lib.dto.dto import DTO


class AttributeMap(DTO):
    def __init__(self):
        self.description = str
        self.pairings = [Pairing()]


class Pairing(DTO):
    def __init__(self):
        self.profile = str
        self.issuer = str
        self.attributes = [str]
        self.regexp = str
        self.replace = str
