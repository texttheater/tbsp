#!/usr/bin/env python3


import argparse
import clf
import constants
import drs
import fix
import horizontal
import hyper
import json
import random
import srl
import sys
import util
import vertical
import vocab


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
    ap.add_argument('--roles', help='input roles in JSON format')
    ap.add_argument('--gold-roles', action='store_true',
            help='use gold instead of predicted roles')
    ap.add_argument('--exp-key', help='experiment key (for excluding specific roles)')
    ap.add_argument('--mode', required=True, type=int, choices=(2, 3), help='PMB major version')
    args = ap.parse_args()
    if args.gold_roles and not args.roles:
        ap.error('--gold-roles requires --roles')
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
    # Read roles
    if args.roles:
        with open(args.roles) as f:
            roler = srl.Roler(
                (json.loads(l) for l in f),
                drs.Checker(args.mode),
                gold=args.gold_roles,
                exp_key=args.exp_key,
            )
    # Create checker
    checker = drs.Checker(args.mode)
    # Parse:
    for i, sentence in enumerate(sentences):
        if lemmass:
            lemmas = lemmass[i]
            assert len(sentence) == len(lemmas)
        else:
            lemmas = None
        dy.renew_cg()
        actions, fragments = p.parse(sentence, lemmas=lemmas)
        # Replace Var objects with DRs
        fragments = clf.fragments_key(fragments)
        # SRL
        if args.roles:
            fragments = roler.overwrite_roles(fragments, sentence)
        # Postprocess
        fragments = constants.replace_constants_rev(fragments)
        fragments = constants.remove_constant_clauses(fragments)
        # Fix
        clauses = [c for f in fragments for c in f]
        if args.mode == 2:
            fix.add_missing_box_refs(clauses, checker)
        fix.add_missing_concept_refs(clauses)
        fix.add_missing_arg0_refs(clauses)
        fix.add_missing_arg1_refs(clauses)
        if args.mode == 2:
            import fix2
            fix2.ensure_nonempty(clauses)
            fix2.ensure_main_box(clauses)
        elif args.mode == 3:
            import fix3
            clauses = fix3.ensure_no_loops(clauses)
            clauses = fix3.ensure_connected(clauses)
            fix3.ensure_nonempty(clauses)
        fix.dedup(clauses)
        if args.mode == 2:
            fix2.check(clauses, i)
        elif args.mode == 3:
            fix3.check(clauses, i)
        # Output
        print('%%%', ' '.join(sentence))
        clf.write(((clauses,),), sys.stdout)
