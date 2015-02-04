
class Collector(object):
    """Collector is the base class for all the collectors/metrics"""

    def __init__(self, name, help_text, const_labels):

        if name is None:
            raise Exception("Name is required")

        if help_text is None:
            raise Exception("Help text is required")

        self.name = name
        self.help_text = help_text
        self.const_labels = const_labels

        # This is a map that contains all the metrics for this type con
        # collector
        self.values = {}

        return self


class Gauge(Collector):
    """ Gauge is a Metric that represents a single numerical value that can
        arbitrarily go up and down.
    """

    def set(self, labels, value):
        """ Set sets the Gauge to an arbitrary value."""
        pass

    def get(self, labels):
        """ Get gets the Gauge of an arbitrary group of labels"""
        pass

    def inc(self, labels):
        """ Inc increments the Gauge by 1."""
        pass

    def dec(self, labels):
        """ Dec decrements the Gauge by 1."""
        pass

    def add(self, labels, value):
        """ Add adds the given value to the Gauge. (The value can be
            negative, resulting in a decrease of the Gauge.)
        """
        pass

    def sub(self, labels, value):
        """ Sub subtracts the given value from the Gauge. (The value can be
            negative, resulting in an increase of the Gauge.)
        """
        pass


class Counter(Collector):
    """ Counter is a Metric that represents a single numerical value that only
        ever goes up.
    """

    def set(self, labels, value):
        """ Set is used to set the Counter to an arbitrary value. """
        pass

    def get(self, labels):
        """ Get gets the counter of an arbitrary group of labels"""
        pass

    def inc(self, labels):
        """ Inc increments the counter by 1."""
        pass

    def add(self, labels, value):
        """ Add adds the given value to the counter. It panics if the value
            is < 0.
        """
        pass


class Summary(Collector):
    """ A Summary captures individual observations from an event or sample
        stream and summarizes them in a manner similar to traditional summary
        statistics: 1. sum of observations, 2. observation count,
        3. rank estimations.
    """

    def observe(self, labels, value):
        """Observe adds a single observation to the summary."""
        pass
