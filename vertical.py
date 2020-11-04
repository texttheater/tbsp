import util


from typing import List, TextIO, Tuple


def read(f: TextIO) -> List[Tuple[str]]:
    blocks = []
    for block in util.blocks(f):
        block = tuple(l.rstrip() for l in block[:-1])
        blocks.append(block)
    return blocks
