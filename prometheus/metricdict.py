import collections


# http://stackoverflow.com/questions/3387691/python-how-to-perfectly-override-a-dict
class MetricDict(collections.MutableMapping):
    """ MetricDict stores the data based on the labels so we need to generate
        custom hash keys based on the labels
    """

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        if type(key) is not dict:
            raise TypeError("Only accepts dicts as keys")
        return str(key)
