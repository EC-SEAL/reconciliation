from lib.dto.Dto import DTO


class AttributeMap(DTO):
    def __init__(self):
        self.description = str
        self.weight = float
        # Value must match the name of a preprocessor module
        self.processor = str
        self.pairings = [Pairing()]


class Pairing(DTO):
    def __init__(self):
        self.profile = str
        self.issuer = str
        self.categories = [str]
        self.attributes = [str]
        self.regexp = str
        self.replace = str
