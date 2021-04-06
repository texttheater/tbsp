import drs
import sys
import util


# exclude some substitutions based on
# 210325_srl_confusion_matrix.xslx
DO_NOT_SUBSTITUTE = set((
    'PartOf',
    'Patient',
    'Product',
    'Result',
    'Source',
    'Theme',
    'Topic',
))


class Roler:

    def __init__(self, records, checker, gold=False):
        self.records = []
        for record in records:
            assert len(record['sentences']) == 1
            self.records.append(record)
        self.checker = checker
        self.gold = gold

    def lookup(self, doc):
        doc = list(doc)
        for i in range(0, len(self.records)):
            j = i
            potential_doc = list(self.records[j]['sentences'][0])
            while j + 1 < len(self.records) and len(potential_doc) < len(doc) and potential_doc == doc[:len(potential_doc)]:
                j += 1
                potential_doc.extend(self.records[j]['sentences'][0])
            if potential_doc == doc:
                roles = []
                offset = 0
                for k in range(i, j + 1):
                    if self.gold:
                        assert len(self.records[k]['srl']) == 1
                        tups = self.records[k]['srl'][0]
                    else:
                        tups = self.records[k]['predicted_srl']
                    for pred, arg_from, arg_to, role in tups:
                        roles.append((
                            pred + offset,
                            arg_from + offset,
                            arg_to + offset,
                            role
                        ))
                    offset += len(self.records[k]['sentences'][0])
                return roles
        raise IndexError(f'document {doc} not found')

    def overwrite_roles(self, fragments, doc):
        try:
            roles = self.lookup(doc)
        except IndexError:
            print(f'WARNING: document {doc} not found', file=sys.stderr)
            return fragments
        fragments = tuple(tuple(list(c) for c in f) for f in fragments)
        for pred, arg_from, arg_to, role in roles:
            if role == 'V':
                continue
            if role in DO_NOT_SUBSTITUTE:
                continue
            assert arg_from == arg_to
            pred_frag = fragments[pred]
            pred_refs = set(
                c[2]
                for c in pred_frag
                if c[1] == 'REF'
            )
            arg_frag = fragments[arg_from]
            arg_refs = set(
                c[2]
                for c in arg_frag
                if c[1] == 'REF'
            )
            for frag in fragments:
                for clause in frag:
                    if self.checker.is_event_role(clause[1]) \
                            and clause[2] in pred_refs \
                            and clause[3] in arg_refs:
                        print(f'INFO: replacing {clause[1]} with {role}', file=sys.stderr)
                        clause[1] = role
        return tuple(tuple(tuple(c) for c in f) for f in fragments)
