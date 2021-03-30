import drs
import pathlib
import fix
import re
import sys


sys.path.append(str(pathlib.Path(__file__).parent / 'ext' / 'DRS_parsing_3' /
        'evaluation'))
from clf_referee import check_clf, clf_typing, clf_to_box_dict, \
        box_dict_to_subordinate_rel, get_signature
import utils_counter
signature_path = (pathlib.Path(__file__).parent / 'ext' / 'DRS_parsing_3' /
        'evaluation' / 'clf_signature.yaml' )
signature = get_signature(str(signature_path))


LOOP_PATTERN = re.compile(r'Subordinate relation has a loop \|\| (?P<box>b\d+)>b\d+')
NONC_PATTERN = re.compile(r'Boxes are not connected \|\| { (?P<boxes1>b\d+(?:, b\d+)*) } are not connected with { (?P<boxes2>b\d+(?:, b\d+)*) }')


def ensure_nonempty(clauses):
    if not clauses:
        clauses[:] = (tuple(c) for c in utils_counter.dummy_drs())


def check(clauses, i):
    try:
        check_clf(clauses, signature)
    except RuntimeError as e:
        print(f'WARNING: invalid DRS {i}: {e}', file=sys.stderr)


def find_loop(clauses):
    """Checks if the DRS has a loop.

    Returns a box that is in this loop, or None if none.
    """
    if not clauses:
        return None
    try:
        check_clf(clauses, signature)
        return None
    except RuntimeError as e:
        message = str(e)
    match = LOOP_PATTERN.match(message)
    if not match:
        return None # something other than a loop is wrong
    # TODO try to preserve as much structure as possible by removing the
    # smaller box rather than the first?
    return match.group('box')


def fix_loop(clauses, box):
    """Removes the loop by removing box.

    Simply removes all clauses that have box as first element. Subsequently
    adds missing REFs.
    """
    new_clauses = [c for c in clauses if c[0] != box]
    fix.add_missing_concept_refs(new_clauses)
    fix.add_missing_arg0_refs(new_clauses)
    fix.add_missing_arg1_refs(new_clauses)
    if new_clauses == clauses:
        return new_clauses # avoid infinite recursion
    box = find_loop(new_clauses)
    if box is None:
        return new_clauses
    return fix_loop(new_clauses, box)


def ensure_no_loops(clauses):
    """Makes sure the subordination relation is loop-free.

    Inspired by https://github.com/RikVN/Neural_DRS/blob/master/src/postprocess.py.
    """
    box = find_loop(clauses)
    if box is None:
        return clauses
    return fix_loop(clauses, box)


def find_partition(clauses):
    """Checks if the subordination relation of the DRS is not connected.

    If connected, returns None. If not connected, returns a pair of tuples of
    box IDs, the first of which contains the vertices of a graph component, and
    the second of which, the other vertices.
    """
    if not clauses:
        return None
    try:
        check_clf(clauses, signature)
        return None
    except RuntimeError as e:
        message = str(e)
    match = NONC_PATTERN.match(message)
    if not match:
        return None # something other than a nonconnectedness is wrong
    # TODO try to preserve as much structure as possible by removing the
    # smaller box rather than the first?
    boxes1 = tuple(match.group('boxes1').split(', '))
    boxes2 = tuple(match.group('boxes2').split(', '))
    return boxes1, boxes2


def connect(clauses, boxes1, boxes2):
    def box_sortkey(box):
        return int(box[1:])
    box1 = max(boxes1, key=box_sortkey)
    box2 = min(boxes2, key=box_sortkey)
    if box_sortkey(box2) < box_sortkey(box1):
        box1 = max(boxes2, key=box_sortkey)
        box2 = min(boxes1, key=box_sortkey)
    new_clauses = clauses + [(box1, 'CONTINUATION', box2)]
    partition = find_partition(new_clauses)
    if partition is None:
        return new_clauses
    return connect(new_clauses, *partition)


def ensure_connected(clauses):
    """Makes sure the subordination relation is connected.

    Inspired by https://github.com/RikVN/Neural_DRS/blob/master/src/postprocess.py.
    """
    partition = find_partition(clauses)
    if partition is None:
        return clauses
    return connect(clauses, *partition)
