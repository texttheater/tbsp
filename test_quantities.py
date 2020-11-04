import clf
import pathlib
import quantities
import sys
import unittest


class QuantityTestCase(unittest.TestCase):

    def setUp(self):
        gold_path = (pathlib.Path(__file__).parent.parent / 'data' /
                     'pmb-2.2.0' / 'gold' / 'train.txt')
        silver_path = (pathlib.Path(__file__).parent.parent / 'data' /
                      'pmb-2.2.0' / 'silver' / 'train.txt')
        drss = []
        for path in (gold_path,):
            with open(path) as f:
                drss.extend(clf.read(f))
        self.cases = []
        for drs in drss:
            for word, fragment in zip(*drs):
                for clause in fragment:
                    if (clause[1] in ('Quantity', 'EQU')
                        and not clf.is_constant(clause[3])
                        and not clf.is_ref(clause[3])):
                        self.cases.append((word.lower(), clause[3]))


    def test_quantity(self):
        for word, gold in self.cases:
            print(word, gold)
            pred = quantities.quote(quantities.guess_quantity(word))
            if gold == '"?"':
                self.assertIn(pred, ('"+"', '"?"'))
            elif (word, gold) == ('dozen', '"6"'):
                self.assertEqual(pred, '"12"')
            else:
                self.assertEqual(pred, gold)
