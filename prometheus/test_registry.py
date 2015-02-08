import unittest

from prometheus.collectors import Collector, Counter, Gauge, Summary
from prometheus.registry import Registry


class TestRegistry(unittest.TestCase):

    def setUp(self):
        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': {"app": "my_app"},
        }

    def test_register(self):

        q = 100
        collectors = [Collector('test'+str(i), 'Test'+str(i)) for i in range(q)]

        r = Registry()

        for i in collectors:
            r.register(i)

        self.assertEqual(q, len(r.collectors))

    def test_register_sames(self):
        r = Registry()

        r.register(Collector(**self.data))

        with self.assertRaises(ValueError) as context:
            r.register(Collector(**self.data))

        self.assertEqual("Collector already exists or name colision",
                         str(context.exception))

    def test_register_counter(self):
        r = Registry()
        r.register(Counter(**self.data))

        self.assertEqual(1, len(r.collectors))

    def test_register_gauge(self):
        r = Registry()
        r.register(Gauge(**self.data))

        self.assertEqual(1, len(r.collectors))

    def test_register_summary(self):
        r = Registry()
        r.register(Summary(**self.data))

        self.assertEqual(1, len(r.collectors))

    def test_register_wrong_type(self):
        r = Registry()

        with self.assertRaises(TypeError) as context:
            r.register("This will fail")
            self.assertEqual("Can't register instance, not a valid type of collector",
                             str(context.exception))

    def test_deregister(self):
        r = Registry()
        r.register(Collector(**self.data))

        r.deregister(self.data['name'])

        self.assertEqual(0, len(r.collectors))

    def test_get(self):
        r = Registry()
        c = Collector(**self.data)
        r.register(c)

        self.assertEqual(c, r.get(c.name))

    def test_get_all(self):
        q = 100
        collectors = [Collector('test'+str(i), 'Test'+str(i)) for i in range(q)]

        r = Registry()

        for i in collectors:
            r.register(i)

        result = r.get_all()

        self.assertTrue(isinstance(result, list))
        self.assertEqual(q, len(result))
