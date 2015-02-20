from http.server import HTTPServer
import unittest
import threading

from prometheus.collectors import Counter
from prometheus.pusher import Pusher
from prometheus.registry import Registry

TEST_PORT = 61423
TEST_HOST = "127.0.0.1"
TEST_URL = "http://{host}:{port}".format(host=TEST_HOST, port=TEST_PORT)


from http.server import BaseHTTPRequestHandler


class PusherTestHandler(BaseHTTPRequestHandler):

    def __init__(self, test_instance, *args, **kwargs):
        self.test_instance = test_instance

        super().__init__(*args, **kwargs)

    # Silence!
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        self.send_response(200)
        self.end_headers()

        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)

        # Set the request data to access from the test
        self.test_instance.request = {
            'path': self.path,
            'headers': self.headers,
            'method': "POST",
            'body': data,
        }
        return

    def do_PUT(self):
        self.send_response(200)
        self.end_headers()

        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)

        # Set the request data to access from the test
        self.test_instance.request = {
            'path': self.path,
            'headers': self.headers,
            'method': "PUT",
            'body': data,
        }

        return

    def do_DELETE(self):
        self.send_response(200)
        self.end_headers()

        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)

        # Set the request data to access from the test
        self.test_instance.request = {
            'path': self.path,
            'headers': self.headers,
            'method': "DELETE",
            'body': data,
        }
        return


class TestPusher(unittest.TestCase):

    def setUp(self):
        # Handler hack
        def handler(*args, **kwargs):
            PusherTestHandler(self, *args, **kwargs)

        self.server = HTTPServer(('', TEST_PORT), handler)

        # Start a server
        thread = threading.Thread(target=self.server.serve_forever)
        thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.socket.close()

    def test_push_job_ping(self):
        job_name = "my-job"
        p = Pusher(job_name, TEST_URL)
        registry = Registry()
        c = Counter("total_requests", "Total requests.", {})
        registry.register(c)

        c.inc({'url': "/p/user", })

        # Push to the pushgateway
        p.replace(registry)

        # Check the objects that setted the server thread
        self.assertEqual(Pusher.PATH.format(job_name), self.request['path'])

    def test_push_instance_ping(self):
        job_name = "my-job"
        instance_name = "my-instance"
        p = Pusher(job_name, TEST_URL, instance_name)
        registry = Registry()
        c = Counter("total_requests", "Total requests.", {})
        registry.register(c)

        c.inc({'url': "/p/user", })

        # Push to the pushgateway
        p.replace(registry)

        # Check the object that setted the server thread
        self.assertEqual(Pusher.INSTANCE_PATH.format(job_name, instance_name),
                         self.request['path'])

    def test_push_add(self):
        job_name = "my-job"
        p = Pusher(job_name, TEST_URL)
        registry = Registry()
        counter = Counter("counter_test", "A counter.", {'type': "counter"})
        registry.register(counter)

        counter_data = (
            ({'c_sample': '1', 'c_subsample': 'b'}, 400),
        )

        [counter.set(c[0], c[1]) for c in counter_data]
        valid_result = b'[\n\x0ccounter_test\x12\nA counter.\x18\x00"=\n\r\n\x08c_sample\x12\x011\n\x10\n\x0bc_subsample\x12\x01b\n\x0f\n\x04type\x12\x07counter\x1a\t\t\x00\x00\x00\x00\x00\x00y@'

        # Push to the pushgateway
        p.add(registry)

        # Check the object that setted the server thread
        self.assertEqual("POST", self.request['method'])
        self.assertEqual(valid_result, self.request['body'])

    def test_push_replace(self):
        job_name = "my-job"
        p = Pusher(job_name, TEST_URL)
        registry = Registry()
        counter = Counter("counter_test", "A counter.", {'type': "counter"})
        registry.register(counter)

        counter_data = (
            ({'c_sample': '1', 'c_subsample': 'b'}, 400),
        )

        [counter.set(c[0], c[1]) for c in counter_data]
        valid_result = b'[\n\x0ccounter_test\x12\nA counter.\x18\x00"=\n\r\n\x08c_sample\x12\x011\n\x10\n\x0bc_subsample\x12\x01b\n\x0f\n\x04type\x12\x07counter\x1a\t\t\x00\x00\x00\x00\x00\x00y@'

        # Push to the pushgateway
        p.replace(registry)

        # Check the object that setted the server thread
        self.assertEqual("PUT", self.request['method'])
        self.assertEqual(valid_result, self.request['body'])

    def test_push_delete(self):
        job_name = "my-job"
        p = Pusher(job_name, TEST_URL)
        registry = Registry()
        counter = Counter("counter_test", "A counter.", {'type': "counter"})
        registry.register(counter)

        counter_data = (
            ({'c_sample': '1', 'c_subsample': 'b'}, 400),
        )

        [counter.set(c[0], c[1]) for c in counter_data]
        valid_result = b'[\n\x0ccounter_test\x12\nA counter.\x18\x00"=\n\r\n\x08c_sample\x12\x011\n\x10\n\x0bc_subsample\x12\x01b\n\x0f\n\x04type\x12\x07counter\x1a\t\t\x00\x00\x00\x00\x00\x00y@'

        # Push to the pushgateway
        p.delete(registry)

        # Check the object that setted the server thread
        self.assertEqual("DELETE", self.request['method'])
        self.assertEqual(valid_result, self.request['body'])
