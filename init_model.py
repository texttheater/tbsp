#!/usr/bin/env python3


import argparse
import hyper
import json
import random
import util
import vocab


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='initialize the parser model')
    parser.add_argument('lang', choices=('en', 'de', 'it', 'nl'), help='language')
    parser.add_argument('oracles', help='path to oracles input file')
    parser.add_argument('model_out', help='path to file to write model to')
    args = parser.parse_args()
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
    random.seed(1337)
    voc = vocab.Vocabulary(words, hyper.UNK_PROB)
    actions = sorted(set(a for o in oracles for a in o))
    # Prepare DyNet
    import dynet_config
    dynet_config.set(random_seed=1337)
    import dynet as dy
    import parser
    # Initialize model
    p = parser.Parser(args.lang, voc, actions)
    # Save
    p.save_model(args.model_out)
