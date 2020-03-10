import json
import unittest

from lib.dto.Dto import DTO
from lib.dto.AttributeMap import AttributeMap
from lib.dto.Dataset import Dataset


class Phone(DTO):
    def __init__(self):
        self.mobile = Unit()
        self.number = str


class Unit(DTO):
    def __init__(self):
        self.model = str
        self.serial = str


class Person(DTO):
    def __init__(self):
        self.name = str
        self.hometown = Hometown()
        self.phones = [Phone()]


class Hometown(DTO):
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


class DtoTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(DtoTest, self).__init__(*args, **kwargs)
        # logging.basicConfig(level=logging.INFO)
        self.init_tests()

    def init_tests(self):
        self.dataset1 = json.loads(data)
        self.dataset = json.loads(data2)

    def test_unmarshalling_1(self):
        p1 = Person()
        p1.unmarshall(self.dataset1)

        self.assertEqual(self.dataset1['name'], p1.name)
        self.assertEqual(self.dataset1['hometown']['name'], p1.hometown.name)
        self.assertEqual(self.dataset1['hometown']['id'], p1.hometown.id)
        self.assertEqual(2, len(p1.phones))
        self.assertEqual(self.dataset1['phones'][0]['number'], p1.phones[0].number)
        self.assertEqual(self.dataset1['phones'][1]['mobile']['model'], p1.phones[1].mobile.model)

    def test_unmarshalling_2(self):
        p = Person()
        p.unmarshall(self.dataset)

        self.assertEqual(self.dataset['name'], p.name)
        self.assertEqual(self.dataset['hometown']['name'], p.hometown.name)
        self.assertEqual(self.dataset['hometown']['id'], p.hometown.id)
        self.assertEqual(3, len(p.phones))
        self.assertEqual(self.dataset['phones'][0]['number'], p.phones[0].number)
        self.assertEqual(self.dataset['phones'][1]['mobile']['model'], p.phones[1].mobile.model)
        self.assertEqual(self.dataset['phones'][2]['mobile']['serial'], p.phones[2].mobile.serial)

    def test_unmarshalling_edit(self):
        p = Person()
        p.unmarshall(self.dataset)

        p.name = "NAME"
        p.hometown.name = "TOWN"
        p.phones[0].number = "NUMBER"
        p.phones[1].mobile.model = "PHONE"

        self.assertNotEqual(self.dataset['name'], p.name)
        self.assertEqual("NAME", p.name)
        self.assertNotEqual(self.dataset['hometown']['name'], p.hometown.name)
        self.assertEqual("TOWN", p.hometown.name)
        self.assertEqual(self.dataset['hometown']['id'], p.hometown.id)
        self.assertEqual(3, len(p.phones))
        self.assertNotEqual(self.dataset['phones'][0]['number'], p.phones[0].number)
        self.assertEqual("NUMBER", p.phones[0].number)
        self.assertNotEqual(self.dataset['phones'][1]['mobile']['model'], p.phones[1].mobile.model)
        self.assertEqual("PHONE", p.phones[1].mobile.model)
        self.assertEqual(self.dataset['phones'][2]['mobile']['serial'], p.phones[2].mobile.serial)

    def test_marshalling(self):
        expected_str = '{"name": "John Doe", "hometown": {"name": "New Haven", "id": 456}, "phones": [{"mobile": {' \
                       '"model": "A1", "serial": "sbb1234"}, "number": "bb1234"}, {"mobile": {"model": "A2", ' \
                       '"serial": "sbb5678"}, "number": "bb5678"}, {"mobile": {"model": "A3", "serial": "sbb8900"}, ' \
                       '"number": "bb8900"}]}'
        p = Person()
        p.unmarshall(self.dataset)

        res_dict = p.marshall()
        res_str = json.dumps(res_dict)
        self.assertEqual(expected_str, res_str)

    def test_marshalling_edit(self):
        expected_str = '{"name": "NAME", "hometown": {"name": "TOWN", "id": 456}, "phones": [{"mobile": {' \
                       '"model": "A1", "serial": "sbb1234"}, "number": "NUMBER"}, {"mobile": {"model": "PHONE", ' \
                       '"serial": "sbb5678"}, "number": "bb5678"}, {"mobile": {"model": "A3", "serial": "sbb8900"}, ' \
                       '"number": "bb8900"}]}'
        p = Person()
        p.unmarshall(self.dataset)
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

        self.assertEqual(d.properties['test'], datasets[0]['properties']['test'])


if __name__ == '__main__':
    unittest.main()
