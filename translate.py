#!/usr/bin/env python3


import argparse
import clf
import guess
import sys
import util
import vertical


if __name__ == '__main__':
    try:
        _, clf_path, lemma_path = sys.argv
    except ValueError:
        print('USAGE: python3 translate.py data.clf data.lemma', file=sys.stderr)
        sys.exit(1)
    with open(clf_path) as f:
        examples = clf.read(f)
    with open(lemma_path) as f:
        lemmass = vertical.read(f)
    assert len(examples) == len(lemmass)
    for (sentence, fragments), lemmas in zip(examples, lemmass):
        assert len(sentence) == len(lemmas)
        masked = [mask.mask_fragment(f) for f in fragments]
        fragments, _ = zip(*masked)
        fragments = list(fragments)
        for i in range(len(fragments)):
            fragments[i] = guess.guess_concept_from_lemma(fragments[i], lemmas[i])
        print('%%%', ' '.join(sentence))
        clf.write((fragments,), sys.stdout)

