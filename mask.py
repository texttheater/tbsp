"""Functions related to masking/unmasking symbols"""


import drs
import collections
import re
import sys


def mask_fragment(fragment):
    symbols = collections.defaultdict(list)
    return tuple(mask_clause(c, symbols) for c in fragment), symbols


def mask_clause(clause, symbols):
    clause = list(clause)
    # Concepts and sense numbers
    if len(clause) == 4 and drs.is_sense(clause[2]) and \
        not drs.is_function_sense(clause[1], clause[2]):
        concept = clause[1]
        sense_string = clause[2]
        pos = sense_string[1:2]
        number = sense_string[3:5]
        masked_sense_string = '"{}.00"'.format(pos)
        symbols['work'].append(concept)
        symbols[masked_sense_string].append(sense_string)
        clause[1] = 'work'
        clause[2] = masked_sense_string
    # Strings
    if drs.is_string(clause[-1]) and not drs.is_constant(clause[-1]):
        symbols['"tom"'].append(clause[-1])
        clause[-1] = '"tom"'
    if drs.is_string(clause[1]) and not drs.is_constant(clause[1]):
        symbols['"tom"'].append(clause[1])
        clause[1] = '"tom"'
    # Return
    return tuple(clause)


def unmask_fragment(clauses, symbols):
    for mask in ('work', '"n.00"', '"v.00"', '"a.00"', '"r.00"', '"tom"',):
        replacements = list(symbols.get(mask, ()))
        clauses = replace(mask, clauses, replacements)
    return clauses


def replace(old, obj, replacements):
    if not replacements:
        return obj
    if old == obj:
        return replacements.pop(0)
    if isinstance(obj, tuple):
        return tuple(replace(old, e, replacements) for e in obj)
    return obj
