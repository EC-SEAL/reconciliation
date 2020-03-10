import json
import logging


class DTO:

    # From a dictionary, build a DTO derived object hierarchy
    def unmarshall(self, data_dict):
        logging.debug("Called unmarshall in ", self.__class__)
        if type(data_dict) is not dict:
            raise Exception("data_dict must be a dictionary")

        for attr, cls in self.__dict__.items():
            logging.debug("Seeking: ", attr)

            if attr in data_dict:
                logging.debug("Found ", attr)
                val = data_dict[attr]
                logging.debug("Value: ", val)
                self.__dict__[attr] = self.unmarshall_item(attr, val, self.__dict__[attr])
        return self

    def unmarshall_item(self, attr, val, cls):
        logging.debug("Called unmarshall_item in ", self.__class__)
        if isinstance(val, list):
            arr = []
            item_cls = cls[0]
            for item in val:
                logging.debug("Item:", item)
                obj = item_cls.__class__()
                # We store the type of the list items as the zero and only element
                arr.append(self.unmarshall_item(attr, item, obj))
            return arr
        if isinstance(val, dict):
            logging.debug("value:", val)
            return cls.unmarshall(val)
        else:
            return val

    # From an object hierarchy, build a dictionary
    def marshall(self):
        dic = {}
        for attr, val in self.__dict__.items():
            dic[attr] = self.marshall_item(val)
        return dic

    def marshall_item(self, element):
        # If it is a list, recursively marshall each
        # element (which may be primitive or not)
        if isinstance(element, list):
            arr = []
            for item in element:
                arr.append(item.marshall())
            return arr
        # If primitive other than list, return it
        if not hasattr(element, '__dict__'):
            return element
        # If data object, marshall and return
        else:
            return element.marshall()

    def json_marshall(self):
        return json.dumps(self.marshall())

    def json_unmarshall(self, data_string):
        data_dict = json.loads(data_string)
        self.unmarshall(data_dict)

# def json_unmarshall(json_string):
#     return json.loads(json_string,
#                            object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
