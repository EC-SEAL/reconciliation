#!/usr/bin/python
# -*- coding: UTF-8 -*-


# Here implement the transformation of the input sets into a list of tuples of strings,
# using the input transformations


# Clean all - _ , . tabs, etc to separate words with just single spaces

class Preprocessor:

    def __init__(self):
        pass

    def transform(self, set_a, set_b, transforms):
        return





'''
def json_validator(data):
    try:
        json.loads(data)
        return True
    except ValueError as error:
        print("invalid json: %s" % error)
        return False
'''


'''


  attributeMap:
    description: Represent semantic equivalence relationships between attribute groups. Groups can be either single attributes or formed by regexp transformation (match and replace) of the result of concatenation of attributes and literal strings.
    type: object
    properties:
      description:
        description: Name or explain the mapping
        type: string
      pairings:
        description: A list of groups that are semantically equivalent
        type: array
        items:
          type: object
          properties:
            profile:
              description: Attribute profile which this group belongs to
              example: eIDAS
              type: string
            issuer:
              description: ID of the entity that emmitted the attributes on this group. If specified, this equivalence will only apply to attributes coming from the correspondign issuer
              example: http://clave.redsara.es/
              type: string
            attributes:
              description: Array of attribute names (can be a single one) and/or string literals that will concatenate to form the group. Items starting with $ will be considered as attribute names, and will be substitutied by its value. Literal strings starting with $ must escape it "\$"
              example:  ["$surname1","#","$surname2"]
              type: array
              items:
                type: string
            regexp:
              description: If set, the result of the concatenation will be matched towards this PERL compatible regexp (no match will return an empty string). Can be used to transform or to ensure a given format.
              example: "^(-,a-zA-Z)+#(-,a-zA-Z)+$"
              type: string
            replace:
              description: If set, this is what will be returned after matching the regexp. Sub-match numeric placeholders can be used as in a PERL compatible regexp.
              example: \1 \2
              type: string


  attributeMapList:
    type: array
    items:
      $ref: '#/definitions/attributeMap'


'''