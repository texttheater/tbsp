import clf
import collections
import times
import pathlib
import unittest
import util


class TimeTestCase(unittest.TestCase):

    def setUp(self):
        gold_path = (pathlib.Path(__file__).parent.parent / 'data' / 'pmb-2.2.0' /
                    'gold' / 'train.txt')
        silver_path = (pathlib.Path(__file__).parent.parent / 'data' / 'pmb-2.2.0' /
                       'silver' / 'train.txt')
        drss = []
        #for path in (gold_path, silver_path):
        for path in (gold_path,):
            with open(path) as f:
                drss.extend(clf.read(f))
        self.cases = collections.defaultdict(list)
        for drs in drss:
            for word, fragment in zip(*drs):
                for clause in fragment:
                    if clause[1] in clf.SIGNATURE['btt']['TRO']:
                        self.cases[clause[1]].append((word.lower(), clause[3]))

    def test_clock_time(self):
        for word, gold in self.cases['ClockTime']:
            pred_pm = times.quote(times.guess_clock_time(word, assume='pm'))
            pred_am = times.quote(times.guess_clock_time(word, assume='am'))
            self.assertIn(gold, (pred_pm, pred_am))


    def test_day_of_month(self):
        for word, gold in self.cases['DayOfMonth']:
            pred = times.quote(times.guess_day_of_month(word))
            self.assertEqual(pred, gold)


    def test_day_of_week(self):
        for word, gold in self.cases['DayOfWeek']:
            pred = times.quote(times.guess_day_of_week(word))
            self.assertEqual(pred, gold)


    def test_decade(self):
        for word, gold in self.cases['Decade']:
            pred = times.quote(times.guess_decade(word))
            self.assertEqual(pred, gold)


    def test_month_of_year(self):
        for word, gold in self.cases['MonthOfYear']:
            pred = times.quote(times.guess_month_of_year(word))
            self.assertEqual(pred, gold)


    def test_year_of_century(self):
        for word, gold in self.cases['YearOfCentury']:
            pred = times.quote(times.guess_year_of_century(word))
            self.assertEqual(pred, gold)
