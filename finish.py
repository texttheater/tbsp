import clf
import collections
import pathlib
import sys
import util


sys.path.append(str(pathlib.Path(__file__).parent / 'ext' / 'DRS_parsing' /
        'evaluation'))
from clf_referee import get_signature, clf_typing, clf_to_box_dict, \
        box_dict_to_subordinate_rel, detect_main_box
import utils_counter
signature_path = (pathlib.Path(__file__).parent / 'ext' / 'DRS_parsing' /
        'evaluation' / 'clf_signature.yaml' )
signature = get_signature(str(signature_path))


# FIXME use better fixing strategies, compatible with new versions of Counter


def ensure_main_box(drs):
    # based on code from clf_referee.py
    op_types, arg_typing = clf_typing(drs, signature)
    box_dict = clf_to_box_dict(drs, op_types, arg_typing)
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
    if len(boxes) == 0:
        nex_box_label = 'b1'
    else:
        new_box_label = 'b' + str(int(boxes[-1][1:]) + 1)
    for b1, b2 in zip(nonsubordinators, nonsubordinators[1:]):
        drs.append((new_box_label, 'DRS', b1))
        drs.append((new_box_label, 'DRS', b2))
        drs.append((new_box_label, 'CONTINUATION', b1, b2))


def add_missing_refs_from_discourse_relations(drs):
    problematic_clauses = [
        c for c in drs
        if clf.is_discourse_relation(c[1])
        and not any(d[1] == 'DRS'
                    and d[2] == c[2]
                    for d in drs
                   )
        and not any(d[1] == 'DRS'
                    and d[2] == c[3]
                    for d in drs
                   )
    ]
    for c in problematic_clauses:
        drs.append((c[0], 'DRS', c[2]))
        drs.append((c[0], 'DRS', c[3]))


def add_missing_refs_from_roles(drs):
    problems = [
        (c[0], ref)
        for c in drs
        for ref in c[2:]
        if clf.is_ref(ref)
        and (clf.is_event_role(c[1])
             or clf.is_concept_role(c[1])
             or clf.is_time_role(c[1])
             or clf.is_other_role(c[1])
            )
        and not any(d[1] == 'REF'
                    and d[2] == ref
                    for d in drs
                   )
    ]
    boxes = [c[0] for c in drs if c[0].startswith('b')]
    boxes = sorted(boxes, key=lambda x: int(x[1:]))
    if len(boxes) == 0:
        nex_box_label = 'b1'
    else:
        new_box_label = 'b' + str(int(boxes[-1][1:]) + 1)
    for box, ref in problems:
        drs.append((new_box_label, 'REF', ref))


def replace_empty_with_dummy_drs(drs):
    if len(drs) == 0:
        return utils_counter.dummy_drs()
    return drs


def unmask(clauses, symbols):
    for mask in ('work', '"n.00"', '"v.00"', '"a.00"', '"r.00"', '"tom"',):
        replacements = list(symbols.get(mask, ()))
        clauses = replace(mask, clauses, replacements)
    return clauses


def replace(old, obj, replacements):
    if not replacements:
        return obj
    if old == obj:
        return replacements.pop(0)
    if isinstance(obj, tuple):
        return tuple(replace(old, e, replacements) for e in obj)
    return obj


def realign_pronouns(drs):
    speaker_labels = set()
    hearer_labels = set()
    for clause in drs:
        if clause[1] == '"speaker"':
            speaker_labels.add(clause[2])
        elif clause[1] == '"hearer"':
            hearer_labels.add(clause[2])
    new_drs = []
    for clause in drs:
        if clause[1] == '"speaker"':
            pass
        elif clause[1] == '"hearer"':
            pass
        else:
            if clf.is_event_role(clause[1]):
                for label in speaker_labels:
                    clause = clf.replace(label, '"speaker"', clause)
                for label in hearer_labels:
                    clause = clf.replace(label, '"hearer"', clause)
            new_drs.append(clause)
    return new_drs
