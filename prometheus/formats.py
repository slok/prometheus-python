from abc import ABCMeta, abstractmethod
from datetime import datetime, timezone
import collectors


class PrometheusFormat(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_headers(self):
        """ Returns the headers of the communication format"""
        pass

    @abstractmethod
    def _format_counter(self, counter):
        """ Returns a representation of a counter value in the implemented
            format. Receives a tuple with the labels (a dict) as first element
            and the value as a second element
        """
        pass

    @abstractmethod
    def _format_gauge(self, gauge):
        """ Returns a representation of a gauge value in the implemented
            format. Receives a tuple with the labels (a dict) as first element
            and the value as a second element
        """
        pass

    @abstractmethod
    def _format_sumary(self, summary):
        """ Returns a representation of a summary value in the implemented
            format. Receives a tuple with the labels (a dict) as first element
            and the value as a second element
        """
        pass

    @abstractmethod
    def marshall(self, collector):
        """ Marshalls a collector and returns the storage/transfer format in
            a tuple, this tuple has reprensentation format per element.
        """
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
    LABEL_SEPARATOR_FMT = ", "
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
        return "'Content-Type': '{1}; version={1}'".format(TextFormat.CONTENT,
                                                           TextFormat.VERSION)

    def _format_counter(self, counter, name):
        # Create the label string
        labels = ""
        ts = ""
        if counter[0]:
            labels = [TextFormat.LABEL_FMT.format(key=k, value=v)
                      for k, v in counter[0].items()]
            labels = TextFormat.LABEL_SEPARATOR_FMT.join(labels)
            labels = "{{{labels}}}".format(labels=labels)

        if self.timestamp:
            ts = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()

        result = TextFormat.COUNTER_FMT.format(name=name, labels=labels,
                                               value=counter[1], timestamp=ts)

        return result.strip()

#    def _format_gauge(self, gauge):
#        pass
#

#    def _format_sumary(self, summary):
#        pass
#

#    def marshall(self, values):
#        pass

    def marshall(self, collector):

        if isinstance(collector, collectors.Counter):
            exec_method = self._format_counter
        else:
            raise TypeError("Not a valid object format")

        # create headers
        help_header = TextFormat.HELP_FMT.format(name=collector.name,
                                                 help_text=collector.help_text)

        type_header = TextFormat.TYPE_FMT.format(name=collector.name,
                                                 value_type=collector.REPR_STR)

        # Prepare start
        lines = [help_header, type_header]

        for i in collector.get_all():
            lines.append(exec_method(counter=i, name=collector.name))

        #[print(i) for i in lines]

        return lines
