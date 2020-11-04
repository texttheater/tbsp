#!/usr/bin/env python3


"""Converts plain-text input to codepoints.

Input format: one text per line.
Output format: one codepoint per line, texts terminated by empty lines.
"""


import sys


if __name__ == '__main__':
    for line in sys.stdin:
        for char in line:
            print(ord(char))
        print()
