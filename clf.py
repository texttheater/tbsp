"""Functions for handling clauses.

As in the PMB CLF format.
"""


import collections
import itertools
import pathlib
import re
import sys
import util
import yaml


from typing import List, NewType, Sequence, TextIO, Tuple


Clause = NewType('Clause', Tuple)


SEP_PATTERN = re.compile(r' *% ?')
TOK_PATTERN = re.compile(r'([^ ]+ \[(?P<fr>\d+)\.\.\.(?P<to>\d+)\])')


signature_path = (pathlib.Path(__file__).parent / 'ext' / 'DRS_parsing' /
        'evaluation' / 'clf_signature.yaml')
with open(signature_path) as f:
    SIGNATURE = yaml.load(f)


def token_sortkey(token):
    match = TOK_PATTERN.match(token)
    return int(match.group('fr'))


def read(flo: TextIO) -> List[Tuple[str, List[Sequence[Clause]]]]:
    entries = []
    for block in util.blocks(flo):
        assert block[0].startswith('%%% ')
        assert block[1].startswith('%%% ')
        assert block[2].startswith('%%% ')
        assert block[-1].rstrip() == ''
        sentence = tuple(t for t in block[2].rstrip()[4:].split(' ') if t != 'ø')
        token_fragment_map = collections.defaultdict(list)
        for line in block[3:-1]:
            clause, tokens = SEP_PATTERN.split(line, 1)
            clause = tuple(clause.split(' '))
            if clause == ('',):
                clause = ()
            else:
                assert 3 <= len(clause) <= 4
            tokens = TOK_PATTERN.findall(tokens)
            for token in tokens:
                token_fragment_map[token[0]].append(clause)
                if not clause:
                    token_fragment_map[token[0]].pop(-1)
        fragment_list = [tuple(token_fragment_map[k])
            for k in sorted(token_fragment_map, key=token_sortkey)]
        entries.append((sentence, fragment_list))
    return entries


def write(drss, flo):
    for drs in drss:
        for token in drs:
            for clause in token:
                print(' '.join(clause), file=flo)
        print(file=flo)


def is_ref(arg):
    if not isinstance(arg, str):
        return False
    if arg[0] not in 'benpstx':
        return False
    try:
        int(arg[1:])
    except ValueError:
        return False
    return True


def is_concept(symbol):
    return (not is_ref(symbol)) and symbol[0].islower()


def is_event_role(symbol):
    return symbol in SIGNATURE['btt']['ERO']


def is_concept_role(symbol):
    return symbol in SIGNATURE['btt']['CRO']


def is_time_role(symbol):
    return symbol in SIGNATURE['btt']['TRO']


def is_other_role(symbol):
    return symbol in SIGNATURE['btt']['ORO']


def is_discourse_relation(symbol):
    return symbol in SIGNATURE['bbb']['DRL']


def is_string(string):
    return isinstance(string, str) and string.startswith('"') and string.startswith('"')


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


class Var:

    def __init__(self, letter):
        self.letter = letter
        self.bound_to = None

    def bind(self, other):
        if self.letter != other.letter:
            raise Exception('variable type mismatch')
        while self.bound_to is not None:
            self = self.bound_to
        while other.bound_to is not None:
            other = other.bound_to
        if self == other:
            return
        other.bound_to = self

    def equals(self, other):
        while self.bound_to is not None:
            self = self.bound_to
        while other.bound_to is not None:
            other = other.bound_to
        return self == other


def args(clause):
    return itertools.chain((clause[0],), clause[2:])


def fragments_key(fragments):
    counter = collections.Counter()
    var_str_map = {}
    return tuple(
        tuple(
            clause_key(c, counter, var_str_map)
            for c in f
        )
        for f in fragments
    )


def fragment_key(fragment):
    counter = collections.Counter()
    var_str_map = {}
    return tuple(clause_key(c, counter, var_str_map) for c in fragment)


def clause_key(clause, counter, var_str_map):
    return tuple(arg_key(arg, counter, var_str_map) for arg in clause)


def arg_key(arg, counter, var_str_map):
    if isinstance(arg, Var):
        while arg.bound_to is not None:
            arg = arg.bound_to
        if arg in var_str_map:
            return var_str_map[arg]
        counter[arg.letter] += 1
        string = arg.letter + str(counter[arg.letter])
        var_str_map[arg] = string
        return string
    return arg


def replace(old, new, obj):
    if obj == old:
        return new
    if isinstance(obj, tuple):
        return tuple(replace(old, new, e) for e in obj)
    if isinstance(obj, list):
        return list(replace(old, new, e) for e in obj)
    return obj


def unbind_clause(clause, bindings):
    clause = list(clause)
    clause[0] = bindings.get(clause[0], clause[0])
    clause[2] = bindings.get(clause[2], clause[2])
    if len(clause) > 3:
        clause[3] = bindings.get(clause[3], clause[3])
    return tuple(clause)


def unbind(fragment: Tuple[Clause]) -> Tuple[Clause]:
    """Replaces referents in a fragment by variables.
    """
    bindings = {}
    for clause in fragment:
        for arg in args(clause):
            if is_ref(arg) and not arg in bindings:
                bindings[arg] = Var(arg[0])
    fragment = tuple(unbind_clause(c, bindings) for c in fragment)
    return fragment
