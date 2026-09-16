"""按 LeetCode 层序格式建立真实树，核对输出结构、身份和只读约定。"""
from collections import deque
import copy


def make_tree(cls, values):
    if not values or values[0] is None:
        assert not any(value is not None for value in values)
        return None, [], {}
    root=cls(values[0]);nodes=[root];slots={0:root};queue=deque([root]);i=1
    while queue and i<len(values):
        node=queue.popleft()
        for side in ['left','right']:
            if i>=len(values):break
            if values[i] is not None:
                child=cls(values[i]);setattr(node,side,child)
                nodes.append(child);slots[i]=child;queue.append(child)
            i+=1
    assert all(value is None for value in values[i:]),'unreachable nonempty input slot'
    return root,nodes,slots


def tree_values(root):
    output=[];queue=deque([root]);seen=set()
    while queue:
        node=queue.popleft()
        if node is None:output.append(None);continue
        assert id(node) not in seen,'output contains a cycle or shared child'
        seen.add(id(node));output.append(node.val)
        queue.extend([node.left,node.right])
    while output and output[-1] is None:output.pop()
    return output,seen


def run_tree_case(namespace, tests, case):
    args=copy.deepcopy(case['args']);nodes=[];slots={}
    for index in tests.get('tree_args',[0]):
        args[index],created,by_slot=make_tree(namespace['TreeNode'],args[index])
        nodes+=created
        if index==0:slots=by_slot
    for index in tests.get('node_args',[]):args[index]=slots[args[index]]
    snapshot=[(node,node.val,node.left,node.right) for node in nodes]
    mode=tests.get('result','value')
    original_preorder=[]
    if mode=='flatten':
        pending=[args[0]] if args[0] is not None else []
        while pending:
            node=pending.pop();original_preorder.append(node)
            if node.right is not None:pending.append(node.right)
            if node.left is not None:pending.append(node.left)
    result=getattr(namespace[tests.get('class','Solution')](),tests['method'])(*args)
    if mode=='codec':
        assert isinstance(result,str),'serialization must be a string'
        fresh=namespace[tests.get('class','Codec')]()
        restored=fresh.deserialize(result)
        actual,identities=tree_values(restored)
        assert identities.isdisjoint(id(node) for node in nodes),'deserializer reused input nodes'
        assert fresh.serialize(restored)==result,'round trip changed the encoded representation'
        if 'serialized' in case:assert result==case['serialized'],(result,case)
        if restored is not None:
            restored.val+=123456
            assert all(node.val==value for node,value,_,_ in snapshot),'copy mutation leaked into source'
    elif mode=='flatten':
        assert result is None,'flatten must return None'
        cur=args[0];output=[];seen=set()
        while cur is not None:
            assert id(cur) not in seen,'flattened chain contains a cycle'
            assert cur.left is None,'flattened node still has a left child'
            seen.add(id(cur));output.append(cur);cur=cur.right
        assert len(output)==len(original_preorder) and all(a is b for a,b in zip(output,original_preorder)),'flatten changed original preorder identities'
        assert all(node.val==value for node,value,_,_ in snapshot),'flatten changed node values'
        actual=[node.val for node in output]
    elif mode=='tree':
        actual,identities=tree_values(result)
        if tests.get('reuse_nodes'):
            assert identities=={id(node) for node in nodes},'tree transform lost or replaced nodes'
            assert all(node.val==value for node,value,_,_ in snapshot),'node values changed'
    elif mode=='node':
        actual=None if result is None else next((slot for slot,node in slots.items() if node is result),'foreign_node')
    else:actual=result
    if tests.get('compare')=='sorted':assert sorted(actual)==sorted(case['expected']),(tests['method'],case,actual)
    else:assert actual==case['expected'],(tests['method'],case,actual)
    if tests.get('preserve_tree'):
        assert all(node.val==value and node.left is left and node.right is right for node,value,left,right in snapshot),'input tree changed'
    for index in tests.get('preserve_args',[]):
        assert args[index]==case['args'][index],'input array changed'
    return actual
