import json
import unittest

from lib.dto.dto import DTO
from lib.dto.AttributeMap import AttributeMap
from lib.dto.Dataset import Dataset


class Phone (DTO):
    def __init__(self):
        self.mobile = Unit()
        self.number = str

class Unit(DTO):
    def __init__(self):
        self.model = str
        self.serial = str

class Person (DTO):
    def __init__(self):
        self.name = str
        self.hometown = Hometown()
        self.phones = [Phone()]

class Hometown (DTO):
    def __init__(self):
        self.name = None
        self.id = None


data = '''
{
    "name": "John Smith", 
    "hometown": {
        "name": "New York", 
        "id": 123
    },
    "phones": [
        {"mobile": {"model":"A1", "serial":"s1234"}, 
        "number":"1234"},
        {"mobile": {"model":"A2", "serial":"s5678"}, 
        "number":"5678"}
    ]
}
'''

data2 = '''
{
    "name": "John Doe", 
    "hometown": {
        "name": "New Haven", 
        "id": 456
    },
    "phones": [
        {"mobile": {"model":"A1", "serial":"sbb1234"}, 
        "number":"bb1234"},
        {"mobile": {"model":"A2", "serial":"sbb5678"}, 
        "number":"bb5678"},
        {"mobile": {"model":"A3", "serial":"sbb8900"}, 
        "number":"bb8900"}
    ]
}
'''

class MyTestCase(unittest.TestCase):

    def test_unmarshalling_1(self):
        d = json.loads(data)
        p = Person()
        p.unmarshall(d)

        self.assertEqual(d['name'], p.name)
        self.assertEqual(d['hometown']['name'], p.hometown.name)
        self.assertEqual(d['hometown']['id'], p.hometown.id)
        self.assertEqual(2, len(p.phones))
        self.assertEqual(d['phones'][0]['number'], p.phones[0].number)
        self.assertEqual(d['phones'][1]['mobile']['model'], p.phones[1].mobile.model)

    def test_unmarshalling_2(self):
        d = json.loads(data2)
        p = Person()
        p.unmarshall(d)
        self.assertEqual(d['name'], p.name)
        self.assertEqual(d['hometown']['name'], p.hometown.name)
        self.assertEqual(d['hometown']['id'], p.hometown.id)
        self.assertEqual(3, len(p.phones))
        self.assertEqual(d['phones'][0]['number'], p.phones[0].number)
        self.assertEqual(d['phones'][1]['mobile']['model'], p.phones[1].mobile.model)
        self.assertEqual(d['phones'][2]['mobile']['serial'], p.phones[2].mobile.serial)

    def test_unmarshalling_edit(self):
        d = json.loads(data2)
        p = Person()
        p.unmarshall(d)

        p.name = "NAME"
        p.hometown.name = "TOWN"
        p.phones[0].number = "NUMBER"
        p.phones[1].mobile.model = "PHONE"

        self.assertNotEqual(d['name'], p.name)
        self.assertEqual("NAME", p.name)
        self.assertNotEqual(d['hometown']['name'], p.hometown.name)
        self.assertEqual("TOWN", p.hometown.name)
        self.assertEqual(d['hometown']['id'], p.hometown.id)
        self.assertEqual(3, len(p.phones))
        self.assertNotEqual(d['phones'][0]['number'], p.phones[0].number)
        self.assertEqual("NUMBER", p.phones[0].number)
        self.assertNotEqual(d['phones'][1]['mobile']['model'], p.phones[1].mobile.model)
        self.assertEqual("PHONE", p.phones[1].mobile.model)
        self.assertEqual(d['phones'][2]['mobile']['serial'], p.phones[2].mobile.serial)

    def test_marshalling(self):
        expected_str = '{"name": "John Doe", "hometown": {"name": "New Haven", "id": 456}, "phones": [{"mobile": {' \
                       '"model": "A1", "serial": "sbb1234"}, "number": "bb1234"}, {"mobile": {"model": "A2", ' \
                       '"serial": "sbb5678"}, "number": "bb5678"}, {"mobile": {"model": "A3", "serial": "sbb8900"}, ' \
                       '"number": "bb8900"}]}'
        d = json.loads(data2)
        p = Person()
        p.unmarshall(d)

        res_dict = p.marshall()
        res_str = json.dumps(res_dict)
        self.assertEqual(expected_str, res_str)

    def test_marshalling_edit(self):
        expected_str = '{"name": "NAME", "hometown": {"name": "TOWN", "id": 456}, "phones": [{"mobile": {' \
                       '"model": "A1", "serial": "sbb1234"}, "number": "NUMBER"}, {"mobile": {"model": "PHONE", ' \
                       '"serial": "sbb5678"}, "number": "bb5678"}, {"mobile": {"model": "A3", "serial": "sbb8900"}, ' \
                       '"number": "bb8900"}]}'
        d = json.loads(data2)
        p = Person()
        p.unmarshall(d)
        p.name = "NAME"
        p.hometown.name = "TOWN"
        p.phones[0].number = "NUMBER"
        p.phones[1].mobile.model = "PHONE"

        res_dict = p.marshall()
        res_str = json.dumps(res_dict)
        self.assertEqual(expected_str, res_str)

    def test_AttributeMap(self):
        with open('attributeMaps.json', encoding="utf8") as matchings_file:
            matchings = json.load(matchings_file)

        m = AttributeMap()
        m.unmarshall(matchings[0])

        self.assertEqual(m.pairings[0].attributes, matchings[0]['pairings'][0]['attributes'])

    def test_Dataset(self):
        with open('testDatasets.json', encoding="utf8") as datasets_file:
            datasets = json.load(datasets_file)

        d = Dataset()
        d.unmarshall(datasets[0])

        print(d.properties['test'])
        #self.assertEqual(m.pairings[0].attributes, datasets[0]['pairings'][0]['attributes'])




if __name__ == '__main__':
    unittest.main()
