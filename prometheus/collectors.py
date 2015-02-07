import collections
import json
from multiprocessing import Lock

import quantile

from metricdict import MetricDict


# Used so only one thread can access the values at the same time
mutex = Lock()

# Used to return the value ordered (not necessary byt for consistency useful)
decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)

RESTRICTED_LABELS_NAMES = ('job',)
RESTRICTED_LABELS_PREFIXES = ('__',)


class Collector(object):
    """Collector is the base class for all the collectors/metrics"""

    REPR_STR = "untyped"

    def __init__(self, name, help_text, const_labels=None):
        self.name = name
        self.help_text = help_text
        self.const_labels = const_labels

        if const_labels:
            self._label_names_correct(const_labels)
            self.const_labels = const_labels

        # This is a map that contains all the metrics
        # This variable should be syncronized
        self.values = MetricDict()

    def set_value(self, labels, value):
        """ Sets a value in the container"""

        if labels:
            self._label_names_correct(labels)

        with mutex:
            # TODO: Accept null labels
            self.values[labels] = value

    def get_value(self, labels):
        """ Gets a value in the container, exception if isn't present"""

        with mutex:
            return self.values[labels]

    def _label_names_correct(self, labels):
        """Raise exception (ValueError) if labels not correct"""

        for k, v in labels.items():
            # Check reserved labels
            if k in RESTRICTED_LABELS_NAMES:
                raise ValueError("Labels not correct")

            # Check prefixes
            if any(k.startswith(i) for i in RESTRICTED_LABELS_PREFIXES):
                raise ValueError("Labels not correct")

        return True

    def get_all(self):
        """ Returns a list populated by tuples of 2 elements, first one is
            a dict with all the labels and the second elemnt is the value
            of the metric itself
        """
        with mutex:
            result = []
            # Check if is a single value dict (custom empty key)
            for k, v in self.values.items():
                if not k or k == MetricDict.EMPTY_KEY:
                    key = None
                else:
                    key = decoder.decode(k)
                result.append((key, v))

        return result


class Counter(Collector):
    """ Counter is a Metric that represents a single numerical value that only
        ever goes up.
    """

    REPR_STR = "counter"

    def set(self, labels, value):
        """ Set is used to set the Counter to an arbitrary value. """

        self.set_value(labels, value)

    def get(self, labels):
        """ Get gets the counter of an arbitrary group of labels"""

        return self.get_value(labels)

    def inc(self, labels):
        """ Inc increments the counter by 1."""
        self.add(labels, 1)

    def add(self, labels, value):
        """ Add adds the given value to the counter. It panics if the value
            is < 0.
        """

        if value < 0:
            raise ValueError("Counters can't decrease")

        try:
            current = self.get_value(labels)
        except KeyError:
            current = 0

        self.set_value(labels, current + value)


class Gauge(Collector):
    """ Gauge is a Metric that represents a single numerical value that can
        arbitrarily go up and down.
    """

    REPR_STR = "gauge"

    def set(self, labels, value):
        """ Set sets the Gauge to an arbitrary value."""

        self.set_value(labels, value)

    def get(self, labels):
        """ Get gets the Gauge of an arbitrary group of labels"""

        return self.get_value(labels)

    def inc(self, labels):
        """ Inc increments the Gauge by 1."""
        self.add(labels, 1)

    def dec(self, labels):
        """ Dec decrements the Gauge by 1."""
        self.add(labels, -1)

    def add(self, labels, value):
        """ Add adds the given value to the Gauge. (The value can be
            negative, resulting in a decrease of the Gauge.)
        """

        try:
            current = self.get_value(labels)
        except KeyError:
            current = 0

        self.set_value(labels, current + value)

    def sub(self, labels, value):
        """ Sub subtracts the given value from the Gauge. (The value can be
            negative, resulting in an increase of the Gauge.)
        """
        self.add(labels, -value)


class Summary(Collector):
    """ A Summary captures individual observations from an event or sample
        stream and summarizes them in a manner similar to traditional summary
        statistics: 1. sum of observations, 2. observation count,
        3. rank estimations.
    """

    REPR_STR = "summary"
    DEFAULT_INVARIANTS = [(0.50, 0.05), (0.90, 0.01), (0.99, 0.001)]
    SUM_KEY = "sum"
    COUNT_KEY = "count"

    # Reimplement the setter and getter without mutex because we need to use
    # it in a higher level (with the estimator object)
    def get_value(self, labels):
            return self.values[labels]

    def set_value(self, labels, value):
        if labels:
            self._label_names_correct(labels)

        self.values[labels] = value

    def add(self, labels, value):
        """Add adds a single observation to the summary."""

        if type(value) not in (float, int):
            raise TypeError("Summay only works with digits (int, float)")

        # We have already a lock for data but not for the estimator
        with mutex:
            try:
                e = self.get_value(labels)
            except KeyError:
                # Initialize quantile estimator
                e = quantile.Estimator(*self.__class__.DEFAULT_INVARIANTS)
                self.set_value(labels, e)
            e.observe(float(value))

    def get(self, labels):
        """ Get gets the data in the form of 0.5, 0.9 and 0.99 percentiles. Also
            you get sum and count, all in a dict
        """

        return_data = {}

        # We have already a lock for data but not for the estimator
        with mutex:
            e = self.get_value(labels)

            # Set invariants data (default to 0.50, 0.90 and 0.99)
            for i in e._invariants:
                q = i._quantile
                return_data[q] = e.query(q)

            # Set sum and count
            return_data[self.__class__.SUM_KEY] = e._sum
            return_data[self.__class__.COUNT_KEY] = e._observations

        return return_data
