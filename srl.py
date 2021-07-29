import collections
import drs
import sys
import util


class Roler:

    def __init__(self, records, checker, gold=False, exp_key=None):
        self.records = []
        for record in records:
            self.records.append(record)
        self.checker = checker
        self.gold = gold
        self.never_replace_roles = {'Name', 'Time'}
        self.never_insert_roles = set()
        if exp_key:
            sys.path.append('ext/SRL-DRS/src')
            import drs_config
            self.never_insert_roles.update(drs_config.never_insert_roles[exp_key])

    def lookup(self, doc):
        doc = list(doc)
        for i in range(0, len(self.records)):
            j = i
            potential_doc = list(self.records[j]['sentences'][0])
            while j + 1 < len(self.records) and len(potential_doc) < len(doc) and potential_doc == doc[:len(potential_doc)]:
                j += 1
                for sentence in self.records[j]['sentences']:
                    potential_doc.extend(sentence)
            if potential_doc == doc:
                roles = []
                offset = 0
                for k in range(i, j + 1):
                    sentences = self.records[k]['sentences']
                    if self.gold:
                        tupss = self.records[k]['srl']
                    else:
                        tupss = self.records[k]['predicted_srl']
                        # Work around inconsistent formats:
                        if tupss == []:
                            tupss = [[]]
                        elif len(tupss[0]) > 0 and type(tupss[0][0]) != list:
                            pred, arg_from, arg_to, role = tupss[0]
                            assert type(arg_from) == int
                            assert type(arg_to) == int
                            tupss = [tupss]
                    assert len(tupss) == len(sentences)
                    for tups, sentence in zip(tupss, sentences):
                        for pred, arg_from, arg_to, role in tups:
                            roles.append((
                                pred + offset,
                                arg_from + offset,
                                arg_to + offset,
                                role
                            ))
                        offset += len(sentence)
                return roles
        raise KeyError(f'document {doc} not found')

    def overwrite_roles(self, fragments, doc):
        try:
            roles = self.lookup(doc)
        except KeyError:
            print(f'WARNING: document {doc} not found', file=sys.stderr)
            return fragments
        fragments = tuple(tuple(list(c) for c in f) for f in fragments)
        # map boxes to the set of roles present in them
        box_roles_map = collections.defaultdict(set)
        for f in fragments:
            for c in f:
                if self.checker.is_event_role(c[1]):
                    box_roles_map[c[0]].add(c[1])
        # map boxes to propositions they introduce
        box_prop_map = {
            c[0]: c[3]
            for f in fragments
            for c in f
            if len(c) == 4
            and c[3].startswith('p')
        }
        # map boxes to the first event they introduce
        box_event_map = {}
        for f in fragments:
            for c in f:
                if len(c) == 3 and c[1] == 'REF' and c[2].startswith('e') and c[0] not in box_event_map:
                    box_event_map[c[0]] = c[2]
        # enrich box_event_map with modal relations
        for f in fragments:
            for c in f:
                if len(c) == 3 and c[1] in ('NECESSITY', 'POSSIBILITY') and c[2] in box_event_map:
                    box_event_map[c[0]] = box_event_map[c[2]]
        # map events to propositions
        event_prop_map = {}
        for f in fragments:
            for c in f:
                if len(c) == 3 and c[1] == 'ATTRIBUTION' and c[0] in box_prop_map and c[2] in box_event_map:
                    event_prop_map[box_event_map[c[2]]] = box_prop_map[c[0]]
        # overwrite roles
        for pred, arg_from, arg_to, role in roles:
            if role == 'V':
                continue
            if role in self.never_insert_roles:
                continue
            assert arg_from == arg_to
            # collect referents corresponding to the predicate
            pred_frag = fragments[pred]
            pred_refs = set(
                c[3]
                for c in pred_frag
                if len(c) == 4
                and drs.is_sense(c[2])
            )
            # collect referents corresponding to the filler
            arg_frag = fragments[arg_from]
            arg_refs = set(
                c[3]
                for c in arg_frag
                if len(c) == 4
                and drs.is_sense(c[2])
            )
            # enrich with propositions corresponding to fillers that are events
            for arg_ref in tuple(arg_refs):
                if arg_ref in event_prop_map:
                    arg_refs.add(event_prop_map[arg_ref])
            # overwrite
            for frag in fragments:
                role_clauses = []
                for clause in frag:
                    if self.checker.is_event_role(clause[1]) \
                            and clause[2] in pred_refs \
                            and clause[3] in arg_refs \
                            and clause[1] not in self.never_replace_roles \
                            and role not in box_roles_map[clause[0]]:
                        print(f'INFO: replacing {clause[1]} with {role}', file=sys.stderr)
                        clause[1] = role
        return tuple(tuple(tuple(c) for c in f) for f in fragments)
