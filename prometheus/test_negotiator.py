import unittest

from formats import TextFormat
from negotiator import Negotiator


class TestNegotiator(unittest.TestCase):

    def test_protobuffer(self):
        headers = ({
            'accept': "proto=io.prometheus.client.MetricFamily;application/vnd.google.protobuf;encoding=delimited",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        }, {
            'Accept': "application/vnd.google.protobuf;proto=io.prometheus.client.MetricFamily;encoding=delimited",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        }, {
            'ACCEPT': "encoding=delimited;application/vnd.google.protobuf;proto=io.prometheus.client.MetricFamily",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        })

        for i in headers:
            with self.assertRaises(NotImplementedError):
                Negotiator.negotiate(i)

    def test_text_004(self):
        headers = ({
            'accept': "text/plain; version=0.0.4",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        }, {
            'Accept': "text/plain;version=0.0.4",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        }, {
            'ACCEPT': " version=0.0.4; text/plain",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        })

        for i in headers:
            self.assertEqual(TextFormat, Negotiator.negotiate(i))

    def test_text_default(self):
        headers = ({
            'Accept': "text/plain;",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        }, {
            'accept': "text/plain",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        })

        for i in headers:
            self.assertEqual(TextFormat, Negotiator.negotiate(i))

    def test_default(self):
        headers = ({
            'accept': "application/json",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        }, {
            'Accept': "*/*",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        }, {
            'ACCEPT': "application/nothing",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "es-ES,es;q=0.8",
        })

        for i in headers:
            self.assertEqual(TextFormat, Negotiator.negotiate(i))
