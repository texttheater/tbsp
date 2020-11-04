#!/usr/bin/env python3


import sys
import util


if __name__ == '__main__':
    for block in util.blocks(sys.stdin):
        sentence = block[2]
        sentence = sentence.rstrip()
        sentence = sentence.split(' ')[1:]
        sentence = [t for t in sentence if t != 'ø']
        sentence = ' '.join(sentence)
        print(sentence)
