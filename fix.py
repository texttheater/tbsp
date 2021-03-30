"""Postprocessing tricks to make invalid DRSs valid."""


import drs


def add_missing_box_refs(clauses, checker):
    problematic_clauses = [
        c for c in clauses
        if checker.is_discourse_relation(c[1])
        and not any(d[1] == 'DRS'
                    and d[2] == c[2]
                    for d in clauses
                   )
        and not any(d[1] == 'DRS'
                    and d[2] == c[3]
                    for d in clauses
                   )
    ]
    for c in problematic_clauses:
        clauses.append((c[0], 'DRS', c[2]))
        clauses.append((c[0], 'DRS', c[3]))


def add_missing_concept_refs(clauses):
    problems = {
        c[3]: c[0]
        for c in clauses
        if len(c) == 4
        and drs.is_ref(c[3])
        and drs.is_sense(c[2])
        and not any (
            d[1] == 'REF'
            and c[2] == c[3]
            for d in clauses
        )
    }
    for ref, box in problems.items():
        clauses.append((box, 'REF', ref))


def add_missing_arg0_refs(clauses):
    problems = {
        c[2]: c[0]
        for c in clauses
        if len(c) == 4
        and drs.is_ref(c[2])
        and (not c[2].startswith('b'))
        and not any(
            d[1] == 'REF'
            and d[2] == c[2]
            for d in clauses
        )
    }
    for ref, box in problems.items():
        clauses.append((box, 'REF', ref))


def add_missing_arg1_refs(clauses):
    problems = {
        c[3]: c[0]
        for c in clauses
        if len(c) == 4
        and drs.is_ref(c[3])
        and (not c[3].startswith('b'))
        and not any(
            d[1] == 'REF'
            and d[2] == c[3]
            for d in clauses
        )
    }
    for ref, box in problems.items():
        clauses.append((box, 'REF', ref))


def dedup(clauses):
    seen = set()
    def seen_before(c):
        if c in seen:
            return True
        seen.add(c)
        return False
    clauses[:] = (c for c in clauses if not seen_before(c))
