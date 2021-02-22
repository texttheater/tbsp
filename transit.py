"""Functions related to the transition system.
"""


import clf
import collections
import itertools
import networkx as nx
import networkx.algorithms.cycles as cycles
import prep
import sys
import util


from typing import Dict, List, NewType, Sequence, Tuple


### TYPES #####################################################################


Action = NewType('Action', Tuple)
Binding = Tuple[str, int, str, int] # type and index of the left and right variable
StackElement = Tuple[int, Sequence[clf.Clause], bool]


### HELPERS ###################################################################


def refs(fragment: Tuple[clf.Clause]) -> Dict[str, str]:
    """Returns all referents in a fragment, keyed by type.
    """
    result = collections.defaultdict(list)
    for clause in fragment:
        for arg in clause:
            if clf.is_ref(arg):
                if arg not in result[arg[0]]:
                    result[arg[0]].append(arg)
    return result


def list_variables(fragment):
    variables = collections.defaultdict(list)
    for clause in fragment:
        for arg in clf.args(clause):
            if isinstance(arg, clf.Var) and arg not in variables[arg.letter]:
                variables[arg.letter].append(arg)
    return variables


def apply_bind(pairs, fragment1, fragment2):
    vars1 = list_variables(fragment1)
    vars2 = list_variables(fragment2)
    for letter1, number1, letter2, number2 in pairs:
        var1 = vars1[letter1][number1 - 1]
        var2 = vars2[letter2][number2 - 1]
        var1.bind(var2)


def force_decode(gold_actions, sentence):
    """Parses a sentence with known gold actions (for testing).
    """
    stack = []
    actions = []
    buf = [(i, None, False) for i in reversed(range(len(sentence)))]
    fragments = []
    for action in gold_actions:
        if not is_action_allowed(action, stack, actions, buf):
            raise Exception('{} not allowed'.format(action))
        apply_action(action, stack, actions, buf, fragments)
    assert len(stack) == 0
    assert len(buf) == 0
    return fragments


### ORACLE TIME ###############################################################


def find_cycle(binding_targets: List[List[List[Binding]]]) -> List[int]:
    G = nx.Graph()
    for i, bindingss in enumerate(binding_targets):
        for j, bindings in enumerate(bindingss, start=i + 1):
            if bindings:
                G.add_edge(i, j)
    try:
        return cycles.find_cycle(G)
    except nx.NetworkXNoCycle:
        return []


def make_binding_targets(fragments: List[Sequence[clf.Clause]]) -> List[List[List[Binding]]]:
    """Returns the required bindings for each pair of fragments.

    For 0 <= i < j < len(fragments), result[i][j - i - 1] contains the list of
    bindings required between fragments[i] and fragments[j].
    """
    refss = [refs(f) for f in fragments]
    refs_set = sorted(set(r for d in refss for v in d.values() for r in v))
    l = len(fragments)
    result = [[[] for _ in range(l - i - 1)] for i, _ in enumerate(fragments)]
    for ref in refs_set:
        indexes = [i for i in range(l)
                   if ref in refss[i][ref[0]]]
        for i, j in zip(indexes, indexes[1:]):
            left_index = refss[i][ref[0]].index(ref) + 1
            right_index = refss[j][ref[0]].index(ref) + 1
            result[i][j - i - 1].append((ref[0], left_index, ref[0], right_index))
    return result


def needs_bindings(stack_element: StackElement, binding_targets: List[List[List[Binding]]]):
    #print(stack_element[0], file=sys.stderr)
    #print(binding_targets, file=sys.stderr)
    # Forward binding needed?
    i = stack_element[0]
    if any(b for b in binding_targets[i]):
        return True
    # Backward binding needed?
    j = stack_element[0]
    if any(binding_targets[i][j - i - 1] for i in range(j)):
        return True
    # No binding needed.
    return False


def bind(l: StackElement, r: StackElement, binding_targets: List[List[List[Binding]]]):
    i, j = sorted((l[0], r[0]))
    pairs = binding_targets[i][j - i - 1]
    binding_targets[i][j - i - 1] = []
    if l[0] > r[0]:
        pairs = [(c, d, a, b) for a, b, c, d in pairs]
    apply_bind(pairs, l[1], r[1])
    return pairs


def choose_action(stack, buf, binding_targets):
    # If stack[-1] is unconfirmed, confirm it
    if len(stack) > 0:
        pos, fragment, confirmed = stack[-1]
        if not confirmed:
            stack[-1] = pos, fragment, True
            return ('confirm', clf.fragment_key(fragment))
    # If stack[-1] has all bindings it needs, reduce
    if len(stack) > 0 and not needs_bindings(stack[-1], binding_targets):
        stack.pop()
        return ('reduce',)
    # If stack[-2], stack[-1] need bindings, bind
    if len(stack) > 1:
        pairs = bind(stack[-2], stack[-1], binding_targets)
        if len(pairs) > 0:
            return ('bind', tuple(pairs))
    # If we can't reduce or bind and we haven't swapped yet, swap
    # TODO Look for opportunities to shift and not swap?
    if len(stack) > 1 and stack[-2][0] < stack[-1][0]:
        buf.append(stack.pop(-2))
        return ('swap',)
    # Otherwise, shift
    stack.append(buf.pop())
    return ('shift',)


def make_oracle(fragments: List[Sequence[clf.Clause]], binding_targets: List[List[List[Binding]]]) -> List[Action]:
    stack = []
    buf = [(i, c, False) for i, c in util.reverse_enumerate(fragments)]
    actions = []
    while len(stack) > 0 or len(buf) > 0:
        #print(stack)
        #print(buf)
        #print(binding_targets)
        action = choose_action(stack, buf, binding_targets)
        #print(action, file=sys.stderr)
        actions.append(action)
    return actions


### TEST TIME #################################################################


def is_bind_allowed(pairs, fragment1, fragment2):
    vars1 = list_variables(fragment1)
    vars2 = list_variables(fragment2)
    for letter1, number1, letter2, number2 in pairs:
        if len(vars1[letter1]) < number1:
            return False
        if len(vars2[letter2]) < number2:
            return False
        var1 = vars1[letter1][number1 - 1]
        var2 = vars2[letter2][number2 - 1]
        # TODO Should we allow double-binding?
        if var1.equals(var2):
            return False
    return True


def is_action_allowed(action, stack, actions, buf):
    if action[0] == 'confirm':
        return len(stack) > 0 and stack[-1][2] == False
    if action[0] == 'reduce':
        return len(stack) > 0 and stack[-1][2] == True and actions[-1][0] != 'swap'
    if action[0] == 'bind':
        return len(stack) > 1 and stack[-1][2] == True and actions[-1][0] != 'bind' and is_bind_allowed(action[1], stack[-2][1], stack[-1][1])
    if action[0] == 'swap':
        return len(stack) > 1 and stack[-1][2] == True and stack[-1][0] > stack[-2][0]
    if action[0] == 'shift':
        return (len(stack) == 0 or stack[-1][2] == True) and len(buf) > 0
    raise Exception('unknown action type: ' + action[0])


def apply_action(action, stack, actions, buf, fragments):
    if action[0] == 'confirm':
        fragment = prep.unbind(action[1])
        stack[-1] = stack[-1][0], fragment, True
        fragments.append(fragment)
    elif action[0] == 'reduce':
        stack.pop()
    elif action[0] == 'bind':
        apply_bind(action[1], stack[-2][1], stack[-1][1])
    elif action[0] == 'swap':
        buf.append(stack.pop(-2))
    elif action[0] == 'shift':
        stack.append(buf.pop())
    else:
        raise Exception('unknown action type: ' + action[0])
    actions.append(action)
