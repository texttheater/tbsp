#!/usr/bin/env python3


import argparse
import clf
import finish
import horizontal
import hyper
import json
import random
import vocab
import sys
import util
import vertical


random.seed(1337)


if __name__ == '__main__':
    # Parse command line
    ap = argparse.ArgumentParser(description='''Run the parser in decoding
            mode.''')
    ap.add_argument('lang', choices=('en', 'de', 'it', 'nl'), help='language')
    ap.add_argument('oracles', help='oracles the model was trained on')
    ap.add_argument('model', help='the trained model')
    ap.add_argument('tok', help='tokenized input sentences in horizontal format')
    ap.add_argument('lemmas', nargs='?', help='input lemmas in vertical format')
    args = ap.parse_args()
    # Read training examples
    sentences = []
    oracles = []
    with open(args.oracles) as f:
        for line in f:
            o = util.lst2tup(json.loads(line))
            sentence = o['sentence']
            oracle = o['oracle']
            sentences.append(sentence)
            oracles.append(oracle)
    # Aggregate inventories
    words = [w for s in sentences for w in s]
    voc = vocab.Vocabulary(words, hyper.UNK_PROB)
    actions = sorted(set(a for o in oracles for a in o))
    # Decode
    import dynet_config
    dynet_config.set(random_seed=1337)
    import dynet as dy
    import parser
    p = parser.Parser(args.lang, voc, actions)
    p.load_model(args.model)
    # Read sentences:
    with open(args.tok) as f:
        sentences = horizontal.read(f)
    # Read lemmas
    if args.lemmas:
        with open(args.lemmas) as f:
            lemmass = vertical.read(f)
        assert len(sentences) == len(lemmass)
    else:
        lemmass = None
    # Parse:
    for i, sentence in enumerate(sentences):
        if lemmass:
            lemmas = lemmass[i]
            assert len(sentence) == len(lemmas)
        else:
            lemmas = None
        dy.renew_cg()
        actions, drs = p.parse(sentence, lemmas=lemmas)
        drs = list(clf.fragment_key(drs))
        drs = finish.realign_pronouns(drs)
        finish.add_missing_refs_from_discourse_relations(drs)
        finish.add_missing_refs_from_roles(drs)
        finish.ensure_main_box(drs)
        drs = finish.replace_empty_with_dummy_drs(drs)
        print('%%%', ' '.join(sentence))
        clf.write(((drs,),), sys.stdout)
