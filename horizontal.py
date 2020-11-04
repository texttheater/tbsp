from typing import List, TextIO, Tuple


def read(f: TextIO) -> List[Tuple[str]]:
    lines = []
    for line in f:
        line = tuple(line.rstrip().split(' '))
        lines.append(line)
    return lines
