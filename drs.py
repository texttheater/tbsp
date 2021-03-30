"""Functions related to DRS clauses."""


import builtins
import itertools
import pathlib
import re
import sys
import yaml


REF_PATTERN = re.compile(r'(?P<letter>[benpstx])(?P<number>\d+)$')
SENSE_STRING_PATTERN = re.compile(r'"(?P<pos>[nvar])\.(?P<number>\d\d?)"')


def args(clause):
    return itertools.chain((clause[0],), clause[2:])


def max_ref_num(letter, clauses):
    def nums():
        for clause in clauses:
            for arg in args(clause):
                match = REF_PATTERN.match(arg)
                if match and match.group('letter') == letter:
                    yield int(match.group('number'))
    return max(nums(), default=0)


def is_ref(arg):
    return bool(REF_PATTERN.match(arg))


def is_sense(arg):
    return bool(SENSE_STRING_PATTERN.match(arg))


class Checker:

    def __init__(self, mode=2):
        self.mode = mode
        if mode == 2:
            signature_path = (
                pathlib.Path(__file__).parent /
                'ext' /
                'DRS_parsing' /
                'evaluation' /
                'clf_signature.yaml'
            )
        elif mode == 3:
            signature_path = (
                pathlib.Path(__file__).parent /
                'ext' /
                'DRS_parsing_3' /
                'evaluation' /
                'clf_signature.yaml'
            )
        with open(signature_path) as f:
            self.signature = yaml.load(f)

    def is_event_role(self, symbol):
        return symbol in self.signature['btt']['ERO']

    def is_concept_role(self, symbol):
        return symbol in self.signature['btt']['CRO']

    def is_time_role(self, symbol):
        return symbol in self.signature['btt']['TRO']

    def is_other_role(self, symbol):
        return symbol in self.signature['btt']['ORO']

    def is_discourse_relation(self, symbol):
        if self.mode == 2:
            return symbol in self.signature['bbb']['DRL']
        elif self.mode == 3:
            return symbol in self.signature['bb']['DRL']


def is_string(string):
    return isinstance(string, str) and string.startswith('"') and string.endswith('"')


def is_constant(string):
   return string in ('"now"', '"speaker"', '"hearer"')


def is_function_sense(concept, sense):
    # TODO this is an ad-hoc set
    return (concept, sense) in (
        ('male', '"n.02"'),
        ('female', '"n.02"'),
        ('time', '"n.08"'),
        ('person', '"n.01"'),
        ('measure', '"n.02"'),
        ('entity', '"n.01"'),
        ('country', '"n.02"'),
        ('city', '"n.01"'),
        ('quantity', '"n.01"'),
        ('name', '"n.01"'),
        ('location', '"n.01"'),
    )


def replace(old, new, obj):
    if obj == old:
        return new
    if isinstance(obj, tuple):
        return tuple(replace(old, new, e) for e in obj)
    if isinstance(obj, list):
        return list(replace(old, new, e) for e in obj)
    return obj


def sorted(fragment):
    return tuple(builtins.sorted(
        fragment,
        key=lambda c: (c[0],) + c[2:] + (c[1],),
    ))
