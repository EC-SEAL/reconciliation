#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Here implement the transliteration api and the different transliteration methods (factory and classes?) for a string
import transliterate


# Transliterate a string to
class Transliteration:
    def __init__(self):
        self.engine = transliterate.translit
        self.languages = transliterate.get_available_language_codes()

    def set_engine(self, engine):
        self.engine = engine

    def set_available_languages(self, languages):
        self.languages = languages

    def get_available_languages(self):
        return self.languages

    def to_ascii(self, source, source_language=None):
        if source_language is not None:
            # Auto-detection
            return self.engine(source, source_language, reversed=True)

        try:
            return self.engine(source, reversed=True)
        except transliterate.exceptions.LanguageDetectionError:
            # Auto-detection does not work for Latin1 to ASCII
            return self.engine(source, "l1", reversed=True)

    def to_alphabet(self, source, target_language="l1"):
        return self.engine(source, target_language)




