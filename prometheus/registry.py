from multiprocessing import Lock

from collectors import Collector

# Used so only one thread can access the values at the same time
mutex = Lock()


class Registry(object):
    """" Registry registers all the collectors"""

    def __init__(self):
        self.collectors = {}

    def register(self, collector):
        """ Registers a collector"""
        if not isinstance(collector, Collector):
            raise TypeError(
                "Can't register instance, not a valid type of collector")

        if collector.name in self.collectors:
            raise ValueError("Collector already exists or name colision")

        with mutex:
            self.collectors[collector.name] = collector

    def deregister(self, name):
        """ eregisters a collector based on the name"""
        with mutex:
            del self.collectors[name]

    def get(self, name):
        """ Get a collector"""

        with mutex:
            return self.collectors[name]

    def get_all(self):
        """Get a list with all the collectors"""
        with mutex:
            return [v for k, v in self.collectors.items()]
