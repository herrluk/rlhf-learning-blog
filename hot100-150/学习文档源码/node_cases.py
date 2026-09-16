"""链表用例适配：保留真实节点身份，核对复用、连接恢复和环入口。"""
import copy


def make_list(node_class, values):
    nodes = [node_class(value) for value in values]
    for left, right in zip(nodes, nodes[1:]):
        left.next = right
    return (nodes[0] if nodes else None), nodes


def chain_nodes(head):
    result, seen = [], set()
    while head is not None:
        assert id(head) not in seen, 'result unexpectedly contains a cycle'
        seen.add(id(head))
        result.append(head)
        head = head.next
    return result


def run_linked_case(namespace, tests, case):
    cls = namespace['ListNode']
    args = copy.deepcopy(case['args'])
    all_nodes, first_nodes = [], []
    shared = None
    if tests.get('mode') == 'list_of_lists':
        heads = []
        for values in args[0]:
            head, nodes = make_list(cls, values)
            heads.append(head)
            all_nodes += nodes
        args[0] = heads
    elif tests.get('mode') == 'intersection':
        a, an = make_list(cls, args[0])
        b, bn = make_list(cls, args[1])
        shared, sn = make_list(cls, args[2])
        if an:
            an[-1].next = shared
        else:
            a = shared
        if bn:
            bn[-1].next = shared
        else:
            b = shared
        args = [a, b]
        all_nodes = an + bn + sn
    else:
        for index in tests.get('linked_args', [0]):
            args[index], nodes = make_list(cls, args[index])
            if index == 0:
                first_nodes = nodes
            all_nodes += nodes
        if case.get('cycle_pos', -1) >= 0:
            first_nodes[-1].next = first_nodes[case['cycle_pos']]
    snapshot = [(node, node.val, node.next) for node in all_nodes]
    obj = namespace[tests.get('class', 'Solution')]()
    result = getattr(obj, tests['method'])(*args)
    if tests.get('inplace'):
        assert result is None, 'in-place method must return None'
        result = args[0]
    output_mode = tests.get('result', 'values')
    if output_mode == 'values':
        out_nodes = chain_nodes(result)
        actual = [node.val for node in out_nodes]
        if tests.get('reuse_nodes'):
            assert {id(node) for node in out_nodes} <= {id(node) for node in all_nodes}, 'copied values instead of reusing nodes'
            assert all(node.val == value for node, value, _ in snapshot), 'changed input values instead of relinking nodes'
        if 'expected_indices' in case:
            assert [id(node) for node in out_nodes] == [id(all_nodes[i]) for i in case['expected_indices']], 'wrong original-node order'
        if tests.get('new_nodes'):
            assert not ({id(node) for node in out_nodes} & {id(node) for node in all_nodes}), 'result aliases input'
    elif output_mode == 'index':
        actual = None if result is None else next((i for i, node in enumerate(first_nodes) if node is result), 'not_original_node')
    elif output_mode == 'shared':
        actual = None if result is None else ('shared' if result is shared else 'wrong_node')
    else:
        actual = result
    assert actual == case['expected'], (tests['method'], case, actual)
    if tests.get('preserve_links'):
        assert all(node.val == value and node.next is successor for node, value, successor in snapshot), 'input values or links were changed'
    return actual


def run_random_linked_case(namespace, tests, case):
    spec = case['args'][0]
    cls = namespace['Node']
    originals = [cls(value) for value, _ in spec]
    for i, node in enumerate(originals):
        node.next = originals[i+1] if i+1 < len(originals) else None
        target = spec[i][1]
        node.random = originals[target] if target is not None else None
    snapshot = [(node, node.val, node.next, node.random) for node in originals]
    result = getattr(namespace['Solution'](), tests['method'])(originals[0] if originals else None)
    copies = chain_nodes(result)
    old_ids, new_ids = {id(n) for n in originals}, {id(n) for n in copies}
    assert len(copies) == len(originals) and not old_ids & new_ids, 'not a deep copy'
    positions = {id(node): i for i, node in enumerate(copies)}
    actual = []
    for node in copies:
        assert node.random is None or id(node.random) in new_ids, 'random points outside copied chain'
        actual.append([node.val, positions[id(node.random)] if node.random is not None else None])
    assert actual == case['expected'], (tests['method'], case, actual)
    assert all(node.val == value and node.next is nxt and node.random is rand
               for node, value, nxt, rand in snapshot), 'original graph was not preserved'
    if copies:
        copies[0].val += 1
        copies[0].random = copies[0]
        assert all(node.val == value and node.next is nxt and node.random is rand
                   for node, value, nxt, rand in snapshot), 'copy mutation affects original'
    return actual
