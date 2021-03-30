#!/usr/bin/env python3


"""Reconstruct the training DRSs from oracles.

This is a sanity check, making sure that our transition system and oracle
generation work as expected.
"""


import clf
import drs
import constants
import fix
import json
import mask
import sys
import transit
import util


if __name__ == '__main__':
    try:
        _, mode = sys.argv
    except ValueError:
        print('USAGE: cat oracle.jsonl | python3 reconstruct.py MODE', file=sys.stderr)
        sys.exit(1)
    mode = int(mode)
    assert mode in (2, 3)
    checker = drs.Checker(mode)
    for i, line in enumerate(sys.stdin, start=1):
        o = util.lst2tup(json.loads(line))
        sentence = o['sentence']
        symbolss = list(o['symbols'])
        oracle = o['oracle']
        # Unmask the confirm actions
        oracle_unmasked = []
        for action in oracle:
            if action[0] == 'confirm':
                symbols = symbolss.pop(0)
                action = ('confirm', mask.unmask_fragment(action[1], symbols))
            oracle_unmasked.append(action)
        assert len(symbolss) == 0
        # Force decode (sanity check)
        fragments = transit.force_decode(oracle_unmasked, sentence)
        # Postprocess
        fragments = clf.fragments_key(fragments)
        fragments = constants.replace_constants_rev(fragments)
        fragments = constants.remove_constant_clauses(fragments)
        # Fix
        clauses = [c for f in fragments for c in f]
        if mode == 2:
            fix.add_missing_box_refs(clauses, checker)
        fix.add_missing_concept_refs(clauses)
        fix.add_missing_arg0_refs(clauses)
        fix.add_missing_arg1_refs(clauses)
        if mode == 2:
            import fix2
            fix2.ensure_nonempty(clauses)
            fix2.ensure_main_box(clauses)
        elif mode == 3:
            import fix3
            clauses = fix3.ensure_no_loops(clauses)
            clauses = fix3.ensure_connected(clauses)
            fix3.ensure_nonempty(clauses)
        fix.dedup(clauses)
        if mode == 2:
            fix2.check(clauses, i)
        elif mode == 3:
            fix3.check(clauses, i)
        # Output
        print('%%%', ' '.join(sentence))
        clf.write(((clauses,),), sys.stdout)
