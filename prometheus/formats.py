from abc import ABCMeta, abstractmethod
import collections
from datetime import datetime, timezone
import re

from prometheus import collectors


class PrometheusFormat(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_headers(self):
        """ Returns the headers of the communication format"""
        pass

    @abstractmethod
    def _format_counter(self, counter, name):
        """ Returns a representation of a counter value in the implemented
            format. Receives a tuple with the labels (a dict) as first element
            and the value as a second element
        """
        pass

    @abstractmethod
    def _format_gauge(self, gauge, name):
        """ Returns a representation of a gauge value in the implemented
            format. Receives a tuple with the labels (a dict) as first element
            and the value as a second element
        """
        pass

    @abstractmethod
    def _format_sumary(self, summary, name):
        """ Returns a representation of a summary value in the implemented
            format. Receives a tuple with the labels (a dict) as first element
            and the value as a second element
        """
        pass

    @abstractmethod
    def marshall(self, registry):
        """ Marshalls a registry and returns the storage/transfer format """
        pass


class TextFormat(PrometheusFormat):
    # Header information
    CONTENT = 'text/plain'
    VERSION = '0.0.4'

    # Formats for values
    HELP_FMT = "# HELP {name} {help_text}"
    TYPE_FMT = "# TYPE {name} {value_type}"
    COMMENT_FMT = "# {comment}"
    LABEL_FMT = "{key}=\"{value}\""
    LABEL_SEPARATOR_FMT = ","
    LINE_SEPARATOR_FMT = "\n"
    COUNTER_FMT = "{name}{labels} {value} {timestamp}"
    GAUGE_FMT = COUNTER_FMT
    SUMMARY_FMTS = {
        'quantile': "{name}{labels} {value} {timestamp}",
        'sum': "{name}_sum{labels} {value} {timestamp}",
        'count': "{name}_count{labels} {value} {timestamp}",
    }

    def __init__(self, timestamp=False):
        """timestamp is a boolean, if you want timestamp in each metric"""
        self.timestamp = timestamp

    def get_headers(self):
        headers = {
            'Content-Type': "{0}; version={1}; charset=utf-8".format(
                TextFormat.CONTENT,
                TextFormat.VERSION),
        }

        return headers

    def _format_line(self, name, labels, value, const_labels=None):
        labels_str = ""
        ts = ""
        # Unify the const_labels and labels
        # Consta labels have lower priority than labels
        if const_labels:
            const_labels = const_labels.copy()
            # Add labels to const labels
            for k, v in labels.items():
                const_labels[k] = v

            # Do we need the order?
            labels = collections.OrderedDict(sorted(const_labels.items(),
                                             key=lambda t: t[0]))

        # Create the label string
        if labels:
            labels_str = [TextFormat.LABEL_FMT.format(key=k, value=v)
                          for k, v in labels.items()]
            labels_str = TextFormat.LABEL_SEPARATOR_FMT.join(labels_str)
            labels_str = "{{{labels}}}".format(labels=labels_str)

        # Python 3.3>
        if self.timestamp:
            ts = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()

        result = TextFormat.COUNTER_FMT.format(name=name, labels=labels_str,
                                               value=value, timestamp=ts)

        return result.strip()

    def _format_counter(self, counter, name, const_labels):
        return self._format_line(name, counter[0], counter[1], const_labels)

    def _format_gauge(self, gauge, name, const_labels):
        return self._format_line(name, gauge[0], gauge[1], const_labels)

    def _format_summary(self, summary, name, const_labels):
        results = []

        for k, v in summary[1].items():
            # Stat from a fresh dict for the labels (new or with preset data)
            if summary[0]:
                labels = summary[0].copy()
            else:
                labels = {}

            # Quantiles need labels and not special name (like sum and count)
            if type(k) is not float:
                name_str = "{0}_{1}".format(name, k)
            else:
                labels['quantile'] = k
                name_str = name
            results.append(self._format_line(name_str, labels, v,
                                             const_labels))

        return results

    def marshall_lines(self, collector):
        """ Marshalls a collector and returns the storage/transfer format in
            a tuple, this tuple has reprensentation format per element.
        """

        if isinstance(collector, collectors.Counter):
            exec_method = self._format_counter
        elif isinstance(collector, collectors.Gauge):
            exec_method = self._format_gauge
        elif isinstance(collector, collectors.Summary):
            exec_method = self._format_summary
        else:
            raise TypeError("Not a valid object format")

        # create headers
        help_header = TextFormat.HELP_FMT.format(name=collector.name,
                                                 help_text=collector.help_text)

        type_header = TextFormat.TYPE_FMT.format(name=collector.name,
                                                 value_type=collector.REPR_STR)

        # Prepare start headers
        lines = [help_header, type_header]

        for i in collector.get_all():
            r = exec_method(i, collector.name, collector.const_labels)

            # Check if it returns one or multiple lines
            if not isinstance(r, str) and isinstance(r, collections.Iterable):
                lines.extend(r)
            else:
                lines.append(r)

        return lines

    def marshall_collector(self, collector):
        # need sort?
        result = sorted(self.marshall_lines(collector))
        return self.__class__.LINE_SEPARATOR_FMT.join(result)

    def marshall(self, registry):
        """Marshalls a full registry (various collectors)"""

        blocks = []
        for i in registry.get_all():
            blocks.append(self.marshall_collector(i))

        # Sort? used in tests
        blocks = sorted(blocks)

        # Needs EOF
        blocks.append("")

        return self.__class__.LINE_SEPARATOR_FMT.join(blocks)
