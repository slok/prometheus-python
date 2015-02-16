from abc import ABCMeta, abstractmethod
import collections
from datetime import datetime, timezone

from prometheus import collectors
from prometheus import utils
from prometheus.pb2 import metrics_pb2


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
        labels = utils.unify_labels(labels, const_labels, True)

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


class ProtobufFormat(PrometheusFormat):
    # Header information
    CONTENT = 'application/vnd.google.protobuf'
    PROTO = 'io.prometheus.client.MetricFamily'
    ENCODING = 'delimited'
    VERSION = '0.0.4'

    def __init__(self, timestamp=False):
        """timestamp is a boolean, if you want timestamp in each metric"""
        self.timestamp = timestamp

    def get_headers(self):
        headers = {
            'Content-Type': "{0}; proto={1}; encoding={2}".format(
                self.__class__.CONTENT,
                self.__class__.PROTO,
                self.__class__.ENCODING,
                ),
        }

        return headers

    def _create_pb2_labels(self, labels):
        result = []
        for k, v in labels.items():
            l = metrics_pb2.LabelPair(name=k, value=v)
            result.append(l)
        return result

    def _format_counter(self, counter, name, const_labels):
        labels = utils.unify_labels(counter[0], const_labels)

        # With a counter and labelpairs we do a Metric
        pb2_labels = self._create_pb2_labels(labels)
        counter = metrics_pb2.Counter(value=counter[1])
        # TODO: TIMESTAMP!
        metric = metrics_pb2.Metric(label=pb2_labels, counter=counter)
        return metric

    def _format_gauge(self, gauge, name, const_labels):
        labels = utils.unify_labels(gauge[0], const_labels)

        pb2_labels = self._create_pb2_labels(labels)
        gauge = metrics_pb2.Gauge(value=gauge[1])
        # TODO: TIMESTAMP!
        metric = metrics_pb2.Metric(label=pb2_labels, gauge=gauge)
        return metric

    def _format_summary(self, summary, name, const_labels):
        labels = utils.unify_labels(summary[0], const_labels)

        pb2_labels = self._create_pb2_labels(labels)

        # Create the quantiles
        quantiles = []

        for k, v in summary[1].items():
            if not isinstance(k, str):
                q = metrics_pb2.Quantile(quantile=k, value=v)
                quantiles.append(q)

        summary = metrics_pb2.Summary(sample_count=summary[1]['count'],
                                      sample_sum=summary[1]['sum'],
                                      quantile=quantiles)

        # TODO: TIMESTAMP!
        metric = metrics_pb2.Metric(label=pb2_labels, summary=summary)
        return metric

    def marshall_collector(self, collector):

        if isinstance(collector, collectors.Counter):
            metric_type = metrics_pb2.COUNTER
            exec_method = self._format_counter
        elif isinstance(collector, collectors.Gauge):
            metric_type = metrics_pb2.GAUGE
            exec_method = self._format_gauge
        elif isinstance(collector, collectors.Summary):
            metric_type = metrics_pb2.SUMMARY
            exec_method = self._format_summary
        else:
            raise TypeError("Not a valid object format")

        metrics = []

        for i in collector.get_all():
            r = exec_method(i, collector.name, collector.const_labels)
            metrics.append(r)

        pb2_collector = metrics_pb2.MetricFamily(name=collector.name,
                                                 help=collector.help_text,
                                                 type=metric_type,
                                                 metric=metrics)
        return pb2_collector
#
#    def marshall(self, registry):