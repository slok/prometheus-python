from collections import OrderedDict
import unittest

from prometheus import utils


class TestUnifyLabels(unittest.TestCase):

    def test_no_const_labels(self):

        labels = {'a': 'b', 'c': 'd'}
        result = utils.unify_labels(labels, None)

        self.assertEqual(labels, result)

    def test_no_labels(self):

        const_labels = {'a': 'b', 'c': 'd'}
        result = utils.unify_labels(None, const_labels)

        self.assertEqual(const_labels, result)

    def test_union(self):

        const_labels = {'a': 'b', 'c': 'd'}
        labels = {'e': 'f', 'g': 'h'}
        result = utils.unify_labels(labels, const_labels)

        valid_result = {'g': 'h', 'c': 'd', 'e': 'f', 'a': 'b'}

        self.assertEqual(valid_result, result)

    def test_union_order(self):

        const_labels = {'a': 'b', 'c': 'd'}
        labels = {'e': 'f', 'g': 'h'}
        result = utils.unify_labels(labels, const_labels, True)

        valid_result = OrderedDict([('a', 'b'), ('c', 'd'), ('e', 'f'), ('g', 'h')])

        self.assertEqual(valid_result, result)