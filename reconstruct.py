#!/usr/bin/env python3


"""Reconstruct the training DRSs from oracles.

This is a sanity check, making sure that our transition system and oracle
generation work as expected.
"""


import clf
import finish
import json
import sys
import transit
import util


if __name__ == '__main__':
    for line in sys.stdin:
        o = util.lst2tup(json.loads(line))
        sentence = o['sentence']
        symbolss = list(o['symbols'])
        oracle = o['oracle']
        # Unmask the confirm actions
        oracle_unmasked = []
        for action in oracle:
            if action[0] == 'confirm':
                symbols = symbolss.pop(0)
                action = ('confirm', finish.unmask(action[1], symbols))
            oracle_unmasked.append(action)
        assert len(symbolss) == 0
        # Force decode (sanity check)
        drs = transit.force_decode(oracle_unmasked, sentence)
        # Postprocess
        drs = list(clf.fragment_key(drs))
        drs = finish.realign_pronouns(drs)
        finish.add_missing_refs_from_discourse_relations(drs)
        finish.ensure_main_box(drs)
        finish.add_missing_refs_from_roles(drs)
        # Output
        print('%%%', ' '.join(sentence))
        clf.write(((drs,),), sys.stdout)
