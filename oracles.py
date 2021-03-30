#!/usr/bin/env python3


# FIXME imperfect reconstruction of DRSs; 94% for German silver data. What gives?


import argparse
import clf
import constants
import copy
import drs
import json
import mask
import symbols
import sys
import transit
import vertical


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='''generate oracles from training examples''')
    ap.add_argument('lang', choices=('en', 'de', 'it', 'nl'), help='''language''')
    ap.add_argument('clf', help='''training examples in clause format''')
    ap.add_argument('lemma', nargs='?', help='''lemmas of training examples''')
    args = ap.parse_args()
    # Read input
    with open(args.clf) as f:
        examples = clf.read(f)
    if args.lemma:
        with open(args.lemma) as f:
            lemmass = vertical.read(f)
        assert len(examples) == len(lemmass)
    else:
        lemmass = None
    # Initialize data structures
    strings = set()
    actions = set()
    results = []
    # Make oracles
    for i, (sentence, fragments) in enumerate(examples):
        example = {}
        example['sentence'] = sentence
        syms = tuple(symbols.guess_symbol(w, args.lang) for w in sentence)
        fragments = constants.add_constant_clauses(syms, fragments)
        fragments = constants.replace_constants(fragments)
        fragments = tuple(drs.sorted(f) for f in fragments)
        masked = [mask.mask_fragment(f) for f in fragments]
        fragments, syms = zip(*masked)
        example['symbols'] = syms
        strings.update(a for f in fragments for c in f for a in c)
        binding_targets = transit.make_binding_targets(fragments)
        example['binding_targets'] = copy.deepcopy(binding_targets)
        example['cycle'] = transit.find_cycle(binding_targets)
        fragments = [clf.unbind(f) for f in fragments]
        oracle = transit.make_oracle(fragments, binding_targets)
        example['oracle'] = oracle
        for action in oracle:
            actions.add(action)
        if lemmass:
            assert len(lemmass[i]) == len(sentence)
            example['lemmas'] = lemmass[i]
        results.append(example)
    # Aggregate and log inventories
    print('strings:', strings, file=sys.stderr)
    print('# actions:', len(actions), file=sys.stderr)
    for action in sorted(actions):
        print(action, file=sys.stderr)
    print('∅ oracle length:', sum(len(r['oracle']) for r in results) / len(results), file=sys.stderr)
    print('∅ number of swap actions:', sum(1 for r in results for a in r['oracle'] if a == ('swap',)) / len(results), file=sys.stderr)
    # Output
    for d in results:
        json.dump(d, sys.stdout)
        print()
