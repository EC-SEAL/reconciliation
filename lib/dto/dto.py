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
                if isinstance(val, list):
                    arr = []
                    item_cls = cls[0]
                    for item in val:
                        logging.debug("Item:", item)
                        if not hasattr(item, '__dict__') \
                                and not isinstance(item, dict):
                            arr.append(item)
                        else:
                            obj = item_cls.__class__()
                            logging.debug("Instantiated ", item_cls)
                            # We store the type of the list items as the zero and only element
                            arr.append(self.unmarshall_item(attr, item, obj))
                    self.__dict__[attr] = arr
                else:
                    self.__dict__[attr] = self.unmarshall_item(attr, val, self.__dict__[attr])
        return self

    def unmarshall_item(self, attr, val, cls):
        logging.debug("Called unmarshall_item in ", self.__class__)

        if isinstance(val, dict):
            logging.debug("value:", val)
            try:
                return cls.unmarshall(val)
            except:
                # If no class is defined, we add it as a dictionary
                return val
        else:
            return val

    # From an object hierarchy, build a dictionary
    def marshall(self):
        dic = {}
        for attr, val in self.__dict__.items():
            logging.debug("Attribute:", attr)
            logging.debug("Value:", val)
            if isinstance(val, list):
                logging.debug("is a List")
                arr = []
                for item in val:
                    arr.append(self.marshall_item(item, item.__class__))
                logging.debug("finished array: ", arr)
                dic[attr] = arr
            else:
                dic[attr] = self.marshall_item(val, val.__class__)
        return dic

    def marshall_item(self, element, cls):
        logging.debug("Element: ", element, "Class:", cls)
        # If it is a list, recursively marshall each
        # element (which may be primitive or not)

        # If primitive other than list, return it
        if not hasattr(element, '__dict__')\
                and not isinstance(element, dict):
            logging.debug("is primitive")
            return element
        # If data object, marshall and return
        else:
            logging.debug("is class")
            return element.marshall()

    def json_marshall(self):
        return json.dumps(self.marshall())

    def json_unmarshall(self, data_string):
        data_dict = json.loads(data_string)
        self.unmarshall(data_dict)

# def json_unmarshall(json_string):
#     return json.loads(json_string,
#                            object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
