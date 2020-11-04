import itertools
import random


def blocks(stream):
    """Splits a text stream by empty lines.

    Reads a file-like object and returns its contents chopped into a sequence
    of blocks terminated by empty lines.
    """
    block = []
    for line in stream:
        block.append(line)
        (chomped,) = line.splitlines()
        if chomped == '':
            yield block
            block = []
    if block: # in case the last block is not terminated
        yield block


def reverse_enumerate(lst):
    """Enumerates a list in reverse order.

    Like enumerate(lst), but with the order reversed.
    """
    for i in range(len(lst) - 1, -1, -1):
        yield i, lst[i]


def lst2tup(data):
    """Converts output of json.loads to have tuples, not lists.
    """
    if isinstance(data, list):
        return tuple(lst2tup(e) for e in data)
    if isinstance(data, dict):
        return {k: lst2tup(v) for k, v in data.items()}
    return data


def shuffled(seq):
    """Returns a list with the elements in seq, shuffled.
    """
    lst = list(seq)
    random.shuffle(lst)
    return lst


def dedup(seq):
    """Returns a list with the elements of seq, duplicates removed.
    """
    seen = set()
    result = []
    for element in seq:
        if element not in seen:
            seen.add(element)
            result.append(element)
    return result


# from https://docs.python.org/3/library/itertools.html#recipes
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s)+1))


def batches(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:min(len(lst), i + size)]
