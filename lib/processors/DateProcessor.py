import logging

from lib import Tools
from lib.processors.base.processor import Processor

import dateparser


# Only for dates. If you need to process DateTime, create another processor
class DateProcessor(Processor):
    # Allowed: \ / , . - '
    unwanted_chars = ";·<>\\|#@()\"\t\n\r!%&=?¡¿"

    def __init__(self):
        pass

    def process(self, input_string):

        # Trim spaces and remove unwanted chars:
        final_str = Tools.clean_string(input_string, DateProcessor.unwanted_chars)
        final_str = Tools.clean_spaces(final_str)

        try:
            # Parse the date with multiple approaches
            date_object = dateparser.parse(final_str)
            if date_object is None:
                raise TypeError

            # Turn the date to a string again (use ISO format)
            final_str = str(date_object.date().isoformat())
        except TypeError:
            logging.warning("Date string could not be parsed: <"
                            + input_string + "> (original) - <"
                            + final_str + "> (after cleaning)")
            # If date cannot be parsed, return original string
            final_str = input_string

        return final_str

    def best(self, item_a, item_b):

        date_a = dateparser.parse(item_a)
        date_b = dateparser.parse(item_b)
        if date_a is None or date_b is None:
            raise TypeError

        # They are two dates. There is no best. Either it parsed or not
        return item_a
