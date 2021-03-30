import drs
import fix
import pathlib
import re
import sys


sys.path.append(str(pathlib.Path(__file__).parent / 'ext' / 'DRS_parsing' /
        'evaluation'))
from clf_referee import check_clf, clf_typing, clf_to_box_dict, \
        box_dict_to_subordinate_rel, get_signature
import utils_counter


signature_path = (pathlib.Path(__file__).parent / 'ext' / 'DRS_parsing' /
        'evaluation' / 'clf_signature.yaml' )
signature = get_signature(str(signature_path))
checker = drs.Checker(2)
LOOP_PATTERN = re.compile(r'Subordinate relation has a loop \|\| (?P<box>b\d+)>b\d+')


def ensure_nonempty(clauses):
    if not clauses:
        clauses[:] = (tuple(c) for c in utils_counter.dummy_drs())


def check(clauses, i):
    try:
        check_clf(clauses, signature)
    except RuntimeError as e:
        print(f'WARNING: invalid DRS {i}: {e}', file=sys.stderr)


def ensure_main_box(clauses):
    # based on code from clf_referee.py
    op_types, arg_typing = clf_typing(clauses, signature)
    box_dict = clf_to_box_dict(clauses, op_types, arg_typing)
    try:
        sub_rel = box_dict_to_subordinate_rel(box_dict)
    except RuntimeError as e:
        print('WARNING: could not ensure main box: {}'.format(e), file=sys.stderr)
        return
    # get a set of boxes that are not sitting inside other boxes
    # e.g., presuppositions will be such boxes  
    independent_boxes = set() 
    for b0 in box_dict:
        # there is no b1 that contains b0 in relations or conditions
        if not next(( b1 for b1 in box_dict if b0 in box_dict[b1].subs or b0 in box_dict[b1].rel_boxes ), False):
            independent_boxes.add(b0)
    #print('%%% independent boxes: {}'.format(independent_boxes))
    # find independent boxes that do not subordinate any other independent boxes
    nonsubordinators = [
        b for b in independent_boxes
        if not any(b1 == b
                   and b2 in independent_boxes
                   for b1, b2 in sub_rel)
    ]
    #print('%%% nunsubordinators: {}'.format(nonsubordinators))
    # ensure there is exactly 1 nonsubordinator
    boxes = sorted(box_dict, key=lambda x: int(x[1:]))
    nonsubordinators.sort(key=lambda x: int(x[1:]))
    if len(box_dict[nonsubordinators[0]].rels) > 0:
        # first nonsubordinator already contains discourse relations,
        # subordinate all other nonsubordinators to it
        last_box = max(box_dict[nonsubordinators[0]].rels,
                       key=lambda b: int(b[-1][1:]))[-1]
        for b in nonsubordinators[1:]:
            clauses.append((nonsubordinators[0], 'DRS', b))
            clauses.append((nonsubordinators[0], 'CONTINUATION', last_box, b))
            last_box = b
    else:
        # first nonsubordinator contains no discourse relations, make a new box
        # and subordinate all nonsubordinators to it
        if len(boxes) == 0:
            new_box_label = 'b1'
        else:
            new_box_label = 'b' + str(int(boxes[-1][1:]) + 1)
        for b1, b2 in zip(nonsubordinators, nonsubordinators[1:]):
            clauses.append((new_box_label, 'DRS', b1))
            clauses.append((new_box_label, 'DRS', b2))
            clauses.append((new_box_label, 'CONTINUATION', b1, b2))
