from lib.dto.Dto import DTO


class CompareTuple(DTO):
    def __init__(self):
        self.items = []  # If array is of primitive type, don't specify it here
        self.weight = float
        self.length_weight = float
        self.max_length = int
        self.normalised_similarity = float