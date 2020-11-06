import logging

from lib import Tools
from lib.processors.base.processor import Processor


class NumberProcessor(Processor):
    # Allowed: ,.-+e
    unwanted_chars = "a-df-zA-DF-Z;:_·<>\\/'\\|#@()\"\t\n\r!%&=\\\\?¡¿"

    def __init__(self):
        pass

    def process(self, input_string):

        # Trim spaces and remove unwanted chars:
        final_str = Tools.clean_string(input_string, NumberProcessor.unwanted_chars)
        final_str = Tools.clean_spaces(final_str)

        try:
            # Parse the number to the most general one (float)
            number = float(final_str)

            # Turn the number to a string again (to homogenise representation)
            final_str = str(number)
        except ValueError:
            logging.warning("Number string could not be parsed: "
                            + input_string + " (original)"
                            + final_str + " (after cleaning)")
            # If number cannot be parsed, return original string
            final_str = input_string

        return final_str

    def best(self, item_a, item_b):
        if item_a >= item_b:
            return item_a
        return item_b
