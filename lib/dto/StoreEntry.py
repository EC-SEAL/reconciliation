from lib.dto.Dto import DTO


class StoreEntry(DTO):
    def __init__(self):
        self.id = str
        self.type = str
        self.data = {}


class StoreEntryList(DTO):
    def __init__(self):
        self.entries = [StoreEntry()]
