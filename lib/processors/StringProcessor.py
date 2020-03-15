from lib import Tools
from lib.processors.base.processor import Processor
from lib.transliteration import Transliteration


class StringProcessor(Processor):

    unwanted_chars = "-.,;:_·<>+\\/'\\|#@()\"\t\n\r!%&=\\\\?¡¿"

    def __init__(self):
        self.trans = Transliteration()
        # List of characters to purge from compare strings

    def process(self, input_string):
        # Transliterate to ascii
        final_str = self.trans.to_ascii(input_string)

        # Clean useless chars and trim spaces:
        final_str = Tools.clean_string(final_str, StringProcessor.unwanted_chars)
        final_str = Tools.clean_spaces(final_str)

        # Uppercase the string
        final_str = final_str.upper()
        return final_str
