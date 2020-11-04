#!/usr/bin/env python3


import argparse
import hyper
import json
import math
import random
import sys
import time
import transit
import util
import vocab


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='train the model for one epoch')
    parser.add_argument('lang', choices=('en', 'de', 'it', 'nl'), help='language')
    parser.add_argument('model_oracles', help='path to file with oracles to extract words and action inventories from')
    parser.add_argument('model_in', help='path to file to read model from')
    parser.add_argument('epoch', type=int, help='current epoch')
    parser.add_argument('model_out', help='path to file to write model to')
    parser.add_argument('train_oracles', nargs='+', help='paths to files with oracles to train on (oracles with actions not in model_oracles will be skipped, and all words not in model_oracles will be unknown)')
    args = parser.parse_args()
    # Read model oracles
    sentences = []
    oracles = []
    with open(args.model_oracles) as f:
        for line in f:
            o = util.lst2tup(json.loads(line))
            sentence = o['sentence']
            oracle = o['oracle']
            sentences.append(sentence)
            oracles.append(oracle)
    # Extract inventories
    print('extracting inventories from {} examples'.format(len(oracles)), file=sys.stderr)
    words = [w for s in sentences for w in s]
    random.seed(1337)
    voc = vocab.Vocabulary(words, hyper.UNK_PROB)
    actions_set = set(a for o in oracles for a in o)
    actions = sorted(actions_set)
    # Read training oracles
    sentences = []
    lemmas = []
    oracles = []
    for path in args.train_oracles:
        with open(path) as f:
            for line in f:
                o = util.lst2tup(json.loads(line))
                sentence = o['sentence']
                oracle = o['oracle']
                if any(a not in actions_set for a in oracle):
                    continue
                sentences.append(sentence)
                lemmas.append(o.get('lemmas'))
                oracles.append(oracle)
    print('training on {} examples'.format(len(oracles)), file=sys.stderr)
    # Shuffle training examples
    random.seed(args.epoch)
    shuffled = util.shuffled(zip(sentences, lemmas, oracles))
    # Prepare DyNet
    import dynet_config
    dynet_config.set(random_seed=args.epoch)
    import dynet as dy
    import parser
    # Read previous model
    p = parser.Parser(args.lang, voc, actions)
    p.load_model(args.model_in)
    # Train
    trainer = dy.SimpleSGDTrainer(p.pc, hyper.ETA)
    for i in range(args.epoch - 1):
        trainer.learning_rate *= (1 - hyper.ETA_DECAY)
    monitor_rhythm = math.ceil(100 / hyper.BATCH_SIZE)
    loss_sum = 0
    loss_values_sum = 0
    start_time = time.time()
    for i, batch in enumerate(util.batches(shuffled, hyper.BATCH_SIZE), start=1):
        losses = []
        dy.renew_cg()
        for sentence, lemmas, oracle in batch:
            loss = p.parse(sentence, lemmas=lemmas, gold_actions=oracle)
            loss_values_sum += loss.value() / len(oracle)
            losses.append(loss)
        batch_loss = dy.esum(losses) / len(losses)
        batch_loss.backward()
        trainer.update()
        if i % monitor_rhythm == 0:
            print('epoch {} batches {}-{} avg train loss {} time {}'.format(args.epoch, i - monitor_rhythm + 1, i, loss_values_sum / hyper.BATCH_SIZE / monitor_rhythm, time.time() - start_time), file=sys.stderr)
            start_time = time.time()
            loss_values_sum = 0
    p.save_model(args.model_out)
