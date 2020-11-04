import clf


def extract(fragment_in):
    fragment_out = []
    roleset = []
    for clause in fragment_in:
        if clf.is_event_role(clause[1]) or clause[1] == 'DummyRole': # TODO concept, time, other roles?
            fragment_out.append((clause[0], 'DummyRole', clause[2], clause[3]))
            roleset.append(clause[1])
        else:
            fragment_out.append(clause)
    return tuple(fragment_out), tuple(roleset)


def insert(fragment_in, roleset):
    roleset = list(roleset)
    fragment_out = []
    for clause in fragment_in:
        if clause[1] == 'DummyRole':
            role = roleset.pop(0)
            fragment_out.append((clause[0], role, clause[2], clause[3]))
        else:
            fragment_out.append(clause)
    return tuple(fragment_out)
