"""Functions for preprocessing.

From complete meaning representations to general fragments.
"""


import clf
import re
import collections


from typing import Dict, Tuple


SENSE_STRING_PATTERN = re.compile(r'"(?P<pos>[nvar])\.(?P<number>\d\d?)"')


PRONOUNS1 = {
        'en': {'i', 'we', 'me', 'us', 'myself', 'ourselves', 'mine', 'ours'},
        'de': {'ich', 'meiner', 'mir', 'mich', 'wir', 'unser', 'uns', 'mein', 'meines', 'meinem', 'meinen', 'meine', 'meins', 'unserer', 'unseres', 'unserem', 'unseren', 'unsere', 'unsers'},
        'it': {'io', 'me', 'mi', 'mia', 'mio', 'miei', 'mie', 'noi', 'ci', 'nostro', 'nostra', 'nostri', 'nostre'},
        'nl': {'ik', 'mij', 'me', 'mijne', 'wij', 'we', 'ons', 'onze'},
        }


PRONOUNS2 = {
        'en': {'you', 'yourself', 'yours'},
        'de': {'du', 'deiner', 'dir', 'dich', 'ihr', 'euer', 'euch', 'dein', 'deines', 'deinem', 'deinen', 'deine', 'deins', 'eurer', 'eures', 'eurem', 'euren', 'eure'},
        'it': {'tu', 'te', 'ti', 'tuo', 'tua', 'tuoi', 'tue', 'voi', 'vi', 'vostro', 'vostra', 'vostri', 'vostre'},
        'nl': {'jij', 'je', 'jou', 'jouwe', 'u', 'uwe', 'jullie'},
        }


def replace(clause, bindings):
    clause = list(clause)
    clause[0] = bindings.get(clause[0], clause[0])
    clause[2] = bindings.get(clause[2], clause[2])
    if len(clause) > 3:
        clause[3] = bindings.get(clause[3], clause[3])
    return tuple(clause)


def unbind(fragment: Tuple[clf.Clause]) -> Tuple[clf.Clause]:
    """Replaces referents in a fragment by variables.
    """
    bindings = {}
    for clause in fragment:
        for arg in clf.args(clause):
            if clf.is_ref(arg) and not arg in bindings:
                bindings[arg] = clf.Var(arg[0])
    fragment = tuple(replace(c, bindings) for c in fragment)
    return fragment


def mask_fragment(fragment):
    symbols = collections.defaultdict(list)
    return tuple(mask_clause(c, symbols) for c in fragment), symbols


def mask_clause(clause, symbols):
    clause = list(clause)
    # Concepts and sense numbers
    if len(clause) == 4 and clf.is_concept(clause[1]) and \
        not clf.is_function_sense(clause[1], clause[2]):
        concept = clause[1]
        sense_string = clause[2]
        match = SENSE_STRING_PATTERN.match(sense_string)
        pos = match.group('pos')
        number = match.group('number')
        masked_sense_string = '"{}.00"'.format(pos)
        symbols['work'].append(concept)
        symbols[masked_sense_string].append(sense_string)
        clause[1] = 'work'
        clause[2] = masked_sense_string
    # Strings
    if clf.is_string(clause[-1]) and not clf.is_constant(clause[-1]):
        symbols['"tom"'].append(clause[-1])
        clause[-1] = '"tom"'
    # Return
    return tuple(clause)


def realign_pronouns(sentence, fragments, lang):
    refs = set(a for f in fragments for c in f for a in clf.args(c) if clf.is_ref(a))
    bs = set(r for r in refs if r.startswith('b'))
    xs = set(r for r in refs if r.startswith('x'))
    if bs:
        bmax = max(int(r[1:]) for r in bs)
    else:
        bmax = 0
    if xs:
        xmax = max(int(r[1:]) for r in refs if r.startswith('x'))
    else:
        xmax = 0
    bspeaker = 'b' + str(bmax + 1)
    xspeaker = 'x' + str(xmax + 1)
    bhearer = 'b' + str(bmax + 2)
    xhearer = 'x' + str(bmax + 2)
    new_fragments = []
    for word, fragment in zip(sentence, fragments):
        if word.lower() in PRONOUNS1[lang] and fragment == ():
            fragment = ((bspeaker, '"speaker"', xspeaker),)
        elif word.lower() in PRONOUNS2[lang] and fragment == ():
            fragment = ((bhearer, '"hearer"', xhearer),)
        else:
            temp = []
            for clause in fragment:
                if clf.is_event_role(clause[1]) and clause[3] == '"hearer"':
                    clause = (clause[0], clause[1], clause[2], xhearer)
                elif clf.is_event_role(clause[1]) and clause[3] == '"speaker"':
                    clause = (clause[0], clause[1], clause[2], xspeaker)
                temp.append(clause)
            fragment = tuple(temp)
        new_fragments.append(fragment)
    return tuple(new_fragments)
