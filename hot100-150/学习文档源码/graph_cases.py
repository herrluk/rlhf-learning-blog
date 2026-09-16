"""图深拷贝身份检查；拓扑序按依赖关系验收，允许多种答案。"""
from collections import deque
import copy


def run_graph_case(namespace, tests, case):
    adjacency=case['args'][0]
    nodes=[namespace['Node'](i+1) for i in range(len(adjacency))]
    for node,neighbors in zip(nodes,adjacency):node.neighbors=[nodes[i-1] for i in neighbors]
    snapshots=[(node,node.val,node.neighbors,list(node.neighbors)) for node in nodes]
    result=getattr(namespace['Solution'](),tests['method'])(nodes[0] if nodes else None)
    if not nodes:
        assert result is None,'empty graph must return None'
        assert case['expected']==[]
        return []
    assert result is not None and result.val==1,'must return clone of entry node'
    discovered={};identities=set();queue=deque([result])
    while queue:
        node=queue.popleft()
        if id(node) in identities:continue
        assert node.val not in discovered,'multiple copies of the same original node'
        discovered[node.val]=node;identities.add(id(node));queue.extend(node.neighbors)
    assert set(discovered)==set(range(1,len(nodes)+1)),'clone node coverage mismatch'
    assert identities.isdisjoint(id(node) for node in nodes),'copied graph points to original nodes'
    neighbor_lists={id(node.neighbors) for node in discovered.values()}
    assert len(neighbor_lists)==len(nodes),'clone nodes share mutable neighbor lists'
    assert neighbor_lists.isdisjoint(id(node.neighbors) for node in nodes),'clone reused original neighbor list'
    actual=[sorted(neighbor.val for neighbor in discovered[i].neighbors) for i in range(1,len(nodes)+1)]
    assert actual==[sorted(row) for row in case['expected']],(actual,case)
    def preserved():
        for node,value,original_list,neighbors in snapshots:
            assert node.val==value and node.neighbors is original_list
            assert len(node.neighbors)==len(neighbors) and all(a is b for a,b in zip(node.neighbors,neighbors)),'source graph changed'
    preserved()
    result.val+=1000;result.neighbors.clear();preserved()
    return actual


def run_topological_case(namespace, tests, case):
    args=copy.deepcopy(case['args']);n,edges=args
    order=getattr(namespace['Solution'](),tests['method'])(*args)
    assert args==case['args'],'prerequisite input changed'
    assert isinstance(order,list),'topological order must be a list'
    if not case['expected']:
        assert order==[],('cycle must return an empty result',case,order)
    else:
        assert len(order)==n and set(order)==set(range(n)),('course coverage',case,order)
        position={value:i for i,value in enumerate(order)}
        assert all(position[b]<position[a] for a,b in edges),('dependency direction',case,order)
    return order
