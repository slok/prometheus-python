import unittest

from collectors import Collector


class TestCollectorDict(unittest.TestCase):

    def setUp(self):
        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': {"app": "my_app"},
        }

        self.c = Collector(**self.data)

    def test_initialization(self):
        self.assertEqual(self.data['name'], self.c.name)
        self.assertEqual(self.data['help_text'], self.c.help_text)
        self.assertEqual(self.data['const_labels'], self.c.const_labels)

    def test_set_value(self):
        data = (
            ({'country': "sp", "device": "desktop"}, 520),
            ({'country': "us", "device": "mobile"}, 654),
            ({'country': "uk", "device": "desktop"}, 1001),
            ({'country': "de", "device": "desktop"}, 995),
        )

        for m in data:
            self.c.set_value(m[0], m[1])

        self.assertEqual(len(data), len(self.c.values))

    def test_get_value(self):
        data = (
            ({'country': "sp", "device": "desktop"}, 520),
            ({'country': "us", "device": "mobile"}, 654),
            ({'country': "uk", "device": "desktop"}, 1001),
            ({'country': "de", "device": "desktop"}, 995),
        )

        for m in data:
            self.c.set_value(m[0], m[1])

        for m in data:
            self.assertEqual(m[1], self.c.get_value(m[0]))

     #def test_set_value_mutex(self):
     #   # TODO: Check mutex
     #   pass

    def test_worng_labels(self):

        # Normal set
        with self.assertRaises(ValueError) as context:
            self.c.set_value({'job': 1, 'ok': 2}, 1)

        self.assertEqual('Labels not correct', str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.c.set_value({'__not_ok': 1, 'ok': 2}, 1)

        self.assertEqual('Labels not correct', str(context.exception))

        # Constructor set
        with self.assertRaises(ValueError) as context:
            Collector("x", "y", {'job': 1, 'ok': 2})

        self.assertEqual('Labels not correct', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Collector("x", "y", {'__not_ok': 1, 'ok': 2})

        self.assertEqual('Labels not correct', str(context.exception))
