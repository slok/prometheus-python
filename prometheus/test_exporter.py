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

    def tearDown(self):
        self.server.shutdown()
        self.server.socket.close()
