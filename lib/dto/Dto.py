import json
import logging


class DTO:

    # From a dictionary, build a DTO derived object hierarchy
    def unmarshall(self, data_dict):
        if type(data_dict) is not dict:
            raise BadDtoInput("data_dict must be a dictionary")

        for attr, cls in self.__dict__.items():
            if attr in data_dict:
                val = data_dict[attr]
                if isinstance(val, list):
                    arr = []
                    item_cls = cls[0]
                    for item in val:
                        if not hasattr(item, '__dict__') \
                                and not isinstance(item, dict):
                            arr.append(item)
                        else:
                            obj = item_cls.__class__()
                            # We store the type of the list items as the zero and only element
                            arr.append(self.unmarshall_item(attr, item, obj))
                    self.__dict__[attr] = arr
                else:
                    self.__dict__[attr] = self.unmarshall_item(attr, val, self.__dict__[attr])
        return self

    def unmarshall_item(self, attr, val, cls):

        if isinstance(val, dict):
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
            if isinstance(val, list):
                arr = []
                for item in val:
                    arr.append(self.marshall_item(item))
                dic[attr] = arr
            else:
                dic[attr] = self.marshall_item(val)
        return dic

    def marshall_item(self, element):
        try:
            return element.marshall()
        except:
            return element
        # # If primitive other than list, return it
        # if not hasattr(element, '__dict__') \
        #         and not isinstance(element, dict):
        #     logging.debug("is primitive")
        #     return element
        # # If data object, marshall and return
        # else:
        #     logging.debug("is class")
        #     return element.marshall()

    def json_marshall(self):
        return json.dumps(self.marshall())

    def json_unmarshall(self, data_string):
        data_dict = json.loads(data_string)
        self.unmarshall(data_dict)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)


def cast_from_dict(dict_object, cast_class):
    ob = cast_class()
    try:
        return ob.unmarshall(dict_object)
    except:
        raise NotDtoClass("Casting class can't be marshalled. It must extend DTO")


class NotDtoClass(BaseException):
    def __init__(self, message):
        self.message = message

class BadDtoInput(BaseException):
    def __init__(self, message):
        self.message = message


# def json_unmarshall(json_string):
#     return json.loads(json_string,
#                            object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
