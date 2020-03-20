from lib.dto.Dataset import Dataset
from lib.dto.Dto import DTO


class LinkRequest(DTO):
    def __init__(self):
        self.id = str
        self.issuer = str
        self.lloa = str
        self.issued = str
        self.expiration = str
        self.datasetA = Dataset()
        self.datasetB = Dataset()
        self.evidence = [FileObject()]
        self.conversation = [ChatMessage()]


class FileObject(DTO):
    def __init__(self):
        self.filename = str
        self.fileID = str
        self.contentType = str
        self.fileSize = int
        self.content = str


class ChatMessage(DTO):
    def __init__(self):
        self.timestamp = int
        self.sender = str
        self.senderType = str
        self.recipient = str
        self.recipientType = str
        self.message = str
