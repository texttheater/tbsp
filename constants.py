"""Utilities for dealing with constants in DRS."""


import drs
import sys


def add_constant_clauses(symbols, fragments):
    """Add "constant clauses" to DRS.
    
    Input: fragments may be empty and associated with constants, e.g.,
    "speaker", "hearer", "3".

    Output: such fragments are no longer empty, instead they contain a
    single "constant clause", e.g. ('b2', '"speaker"', 'x2').
    """
    constant_clause_map = {}
    xmax = drs.max_ref_num('x', (c for f in fragments for c in f))
    bmax = drs.max_ref_num('b', (c for f in fragments for c in f))
    def replace(symbol, fragment):
        nonlocal xmax, bmax
        if fragment == ():
            constant = f'"{symbol}"'
            if constant not in constant_clause_map:
                xmax += 1
                bmax += 1
                x = f'x{xmax}'
                b = f'b{bmax}'
                constant_clause_map[constant] = (b, constant, x)
            fragment = (constant_clause_map[constant],)
        return fragment
    return tuple(replace(s, f) for s, f in zip(symbols, fragments))


def replace_constants(fragments):
    """Replace ARG1 constants with referents introduced by constant clauses."""
    constant_ref_map = {
        c[1]: c[2]
        for f in fragments
        for c in f
        if len(c) == 3
        and c[1].startswith('"')
        and c[1].endswith('"')
        and c[1] not in ('"?"',)
    }
    def replace(clause):
        if len(clause) == 4 and clause[3] in constant_ref_map:
            clause = (clause[0], clause[1], clause[2], constant_ref_map[clause[3]])
        return clause
    return tuple(tuple(replace(c) for c in f) for f in fragments)


def replace_constants_rev(fragments):
    """Replace ARG1 referents introduced by constant clauses by constants."""
    ref_constant_map = {c[2]: c[1] for f in fragments for c in f if drs.is_constant(c[1])}
    def replace(clause):
        if len(clause) == 4 and clause[3] in ref_constant_map:
            clause = (clause[0], clause[1], clause[2], ref_constant_map[clause[3]])
        return clause
    return tuple(tuple(replace(c) for c in f) for f in fragments)


def remove_constant_clauses(fragments):
    return tuple(tuple(c for c in f if not c[1].startswith('"')) for f in fragments)
