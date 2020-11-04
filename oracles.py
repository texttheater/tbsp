#!/usr/bin/env python3


# FIXME imperfect reconstruction of DRSs; 94% for German silver data. What gives?


import argparse
import clf
import json
import prep
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
        fragments = prep.realign_pronouns(sentence, fragments, args.lang)
        masked = [prep.mask_fragment(f) for f in fragments]
        fragments, symbols = zip(*masked)
        strings.update(a for f in fragments for c in f for a in c)
        binding_targets = transit.make_binding_targets(fragments)
        fragments = [prep.unbind(f) for f in fragments]
        oracle = transit.make_oracle(fragments, binding_targets)
        for action in oracle:
            actions.add(action)
        example = {}
        example['sentence'] = sentence
        example['symbols'] = symbols
        example['oracle'] = oracle
        if lemmass:
            assert len(lemmass[i]) == len(sentence)
            example['lemmas'] = lemmass[i]
        results.append(example)
    # Aggregate and log inventories
    print('strings:', strings, file=sys.stderr)
    print('# actions:', len(actions), file=sys.stderr)
    print('∅ oracle length:', sum(len(r['oracle']) for r in results) / len(results), file=sys.stderr)
    print('∅ number of swap actions:', sum(1 for r in results for a in r['oracle'] if a == ('swap',)) / len(results), file=sys.stderr)
    # Output
    for d in results:
        json.dump(d, sys.stdout)
        print()
