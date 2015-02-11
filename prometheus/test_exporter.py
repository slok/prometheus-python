from http.server import HTTPServer
import unittest
import threading
import urllib

import requests

from prometheus.collectors import Collector, Counter, Gauge, Summary
from prometheus.exporter import PrometheusMetricHandler
from prometheus.formats import TextFormat
from prometheus.registry import Registry

TEST_PORT = 61423
TEST_HOST = "127.0.0.1"
TEST_URL = "http://{host}:{port}".format(host=TEST_HOST, port=TEST_PORT)
TEST_METRICS_PATH = PrometheusMetricHandler.METRICS_PATH


class TestPrometheusMetricHandler(PrometheusMetricHandler):
    """Custom handler to not show request messages when running tests"""
    def log_message(self, format, *args):
        pass


class TestTextExporter(unittest.TestCase):

    def setUp(self):
        # Create the registry
        self.registry = Registry()

        # Handler hack
        def handler(*args, **kwargs):
            TestPrometheusMetricHandler(self.registry, *args, **kwargs)

        self.server = HTTPServer(('', TEST_PORT), handler)

        # Start a server
        thread = threading.Thread(target=self.server.serve_forever)
        thread.start()

    def test_counter(self):

        # Add some metrics
        data = (
            ({'data': 1}, 100),
            ({'data': "2"}, 200),
            ({'data': 3}, 300),
            ({'data': 1}, 400),
        )
        c = Counter("test_counter", "Test Counter.", {'test': "test_counter"})
        self.registry.register(c)

        for i in data:
            c.set(i[0], i[1])

        headers = {'accept': 'text/plain; version=0.0.4'}
        url = urllib.parse.urljoin(TEST_URL, TEST_METRICS_PATH[1:])
        r = requests.get(url, headers=headers)

        valid_data = """# HELP test_counter Test Counter.
# TYPE test_counter counter
test_counter{data="1",test="test_counter"} 400
test_counter{data="2",test="test_counter"} 200
test_counter{data="3",test="test_counter"} 300
"""
        self.assertEqual("text/plain; version=0.0.4; charset=utf-8",
                         r.headers['content-type'])
        self.assertEqual(200, r.status_code)
        self.assertEqual(valid_data, r.text)

    def test_gauge(self):

        # Add some metrics
        data = (
            ({'data': 1}, 100),
            ({'data': "2"}, 200),
            ({'data': 3}, 300),
            ({'data': 1}, 400),
        )
        g = Gauge("test_gauge", "Test Gauge.", {'test': "test_gauge"})
        self.registry.register(g)

        for i in data:
            g.set(i[0], i[1])

        headers = {'accept': 'text/plain; version=0.0.4'}
        url = urllib.parse.urljoin(TEST_URL, TEST_METRICS_PATH[1:])
        r = requests.get(url, headers=headers)

        valid_data = """# HELP test_gauge Test Gauge.
# TYPE test_gauge gauge
test_gauge{data="1",test="test_gauge"} 400
test_gauge{data="2",test="test_gauge"} 200
test_gauge{data="3",test="test_gauge"} 300
"""
        self.assertEqual("text/plain; version=0.0.4; charset=utf-8",
                         r.headers['content-type'])
        self.assertEqual(200, r.status_code)
        self.assertEqual(valid_data, r.text)

    def test_summary(self):

        # Add some metrics
        data = [3, 5.2, 13, 4]
        label = {'data': 1}

        s = Summary("test_summary", "Test Summary.", {'test': "test_summary"})
        self.registry.register(s)

        for i in data:
            s.add(label, i)

        headers = {'accept': 'text/plain; version=0.0.4'}
        url = urllib.parse.urljoin(TEST_URL, TEST_METRICS_PATH[1:])
        r = requests.get(url, headers=headers)

        valid_data = """# HELP test_summary Test Summary.
# TYPE test_summary summary
test_summary_count{data="1",test="test_summary"} 4
test_summary_sum{data="1",test="test_summary"} 25.2
test_summary{data="1",quantile="0.5",test="test_summary"} 4.0
test_summary{data="1",quantile="0.9",test="test_summary"} 5.2
test_summary{data="1",quantile="0.99",test="test_summary"} 5.2
"""
        self.assertEqual("text/plain; version=0.0.4; charset=utf-8",
                         r.headers['content-type'])
        self.assertEqual(200, r.status_code)
        self.assertEqual(valid_data, r.text)

    def test_all(self):
        format_times = 10

        counter_data = (
            ({'c_sample': '1'}, 100),
            ({'c_sample': '2'}, 200),
            ({'c_sample': '3'}, 300),
            ({'c_sample': '1', 'c_subsample': 'b'}, 400),
        )

        gauge_data = (
            ({'g_sample': '1'}, 500),
            ({'g_sample': '2'}, 600),
            ({'g_sample': '3'}, 700),
            ({'g_sample': '1', 'g_subsample': 'b'}, 800),
        )

        summary_data = (
            ({'s_sample': '1'}, range(1000, 2000, 4)),
            ({'s_sample': '2'}, range(2000, 3000, 20)),
            ({'s_sample': '3'}, range(3000, 4000, 13)),
            ({'s_sample': '1', 's_subsample': 'b'}, range(4000, 5000, 47)),
        )

        registry = Registry()
        counter = Counter("counter_test", "A counter.", {'type': "counter"})
        gauge = Gauge("gauge_test", "A gauge.", {'type': "gauge"})
        summary = Summary("summary_test", "A summary.", {'type': "summary"})

        self.registry.register(counter)
        self.registry.register(gauge)
        self.registry.register(summary)

        # Add data
        [counter.set(c[0], c[1]) for c in counter_data]
        [gauge.set(g[0], g[1]) for g in gauge_data]
        [summary.add(i[0], s) for i in summary_data for s in i[1]]

        registry.register(counter)
        registry.register(gauge)
        registry.register(summary)

        valid_data = """# HELP counter_test A counter.
# TYPE counter_test counter
counter_test{c_sample="1",c_subsample="b",type="counter"} 400
counter_test{c_sample="1",type="counter"} 100
counter_test{c_sample="2",type="counter"} 200
counter_test{c_sample="3",type="counter"} 300
# HELP gauge_test A gauge.
# TYPE gauge_test gauge
gauge_test{g_sample="1",g_subsample="b",type="gauge"} 800
gauge_test{g_sample="1",type="gauge"} 500
gauge_test{g_sample="2",type="gauge"} 600
gauge_test{g_sample="3",type="gauge"} 700
# HELP summary_test A summary.
# TYPE summary_test summary
summary_test_count{s_sample="1",s_subsample="b",type="summary"} 22
summary_test_count{s_sample="1",type="summary"} 250
summary_test_count{s_sample="2",type="summary"} 50
summary_test_count{s_sample="3",type="summary"} 77
summary_test_sum{s_sample="1",s_subsample="b",type="summary"} 98857.0
summary_test_sum{s_sample="1",type="summary"} 374500.0
summary_test_sum{s_sample="2",type="summary"} 124500.0
summary_test_sum{s_sample="3",type="summary"} 269038.0
summary_test{quantile="0.5",s_sample="1",s_subsample="b",type="summary"} 4235.0
summary_test{quantile="0.5",s_sample="1",type="summary"} 1272.0
summary_test{quantile="0.5",s_sample="2",type="summary"} 2260.0
summary_test{quantile="0.5",s_sample="3",type="summary"} 3260.0
summary_test{quantile="0.9",s_sample="1",s_subsample="b",type="summary"} 4470.0
summary_test{quantile="0.9",s_sample="1",type="summary"} 1452.0
summary_test{quantile="0.9",s_sample="2",type="summary"} 2440.0
summary_test{quantile="0.9",s_sample="3",type="summary"} 3442.0
summary_test{quantile="0.99",s_sample="1",s_subsample="b",type="summary"} 4517.0
summary_test{quantile="0.99",s_sample="1",type="summary"} 1496.0
summary_test{quantile="0.99",s_sample="2",type="summary"} 2500.0
summary_test{quantile="0.99",s_sample="3",type="summary"} 3494.0
"""

        headers = {'accept': 'text/plain; version=0.0.4'}
        url = urllib.parse.urljoin(TEST_URL, TEST_METRICS_PATH[1:])
        r = requests.get(url, headers=headers)

        self.assertEqual("text/plain; version=0.0.4; charset=utf-8",
                             r.headers['content-type'])
        self.assertEqual(200, r.status_code)
        self.assertEqual(valid_data, r.text)

    def tearDown(self):
        self.server.shutdown()
        self.server.socket.close()
