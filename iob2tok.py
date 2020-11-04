#!/usr/bin/env python3


import sys
import util


if __name__ == '__main__':
    for block in util.blocks(sys.stdin):
        if block[-1].strip() == '':
            block.pop()
        chars = []
        tags = []
        for line in block:
            char, tag = line.split()
            chars.append(chr(int(char)))
            if tag == 'S':
                tag = 'T'
            tags.append(tag)
        line = ''
        in_token = False
        for char, tag in zip(chars, tags):
            if tag == 'T':
                if in_token:
                    line += ' '
                else:
                    in_token = True
            if tag in 'TI':
                if char.isspace():
                    line += '~'
                else:
                    line += char
        print(line)
