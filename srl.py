class Roler:

    def __init__(self, records):
        self. doc_roles_map = {}
        for record in records:
            doc_data = json.reads(line)
            assert len(doc_data['sentences']) == 1
            doc = tuple(doc_data['sentences'][0])
            roles = doc_data['srl']
            self.doc_roles_map[doc] = roles

    def overwrite_roles(fragments, sentence):
        for pred, arg_from, arg_to, role in self.doc_roles_map[sentence]:
            assert arg_from == arg_to
            pred_frag = fragments[pred]
            arg_frag = fragments[arg_from]
            arg_refs = set(
                c[2]
                for c in arg_frag
                if c[1] == 'REF'
            )
            for clause in pred_frag:
                if clf.is_role(clause[1]) and c[3] in arg_refs:
                    clause[1] = role
