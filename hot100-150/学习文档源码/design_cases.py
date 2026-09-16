"""逐条调用设计题对象，验证返回值及传入操作参数不被修改。"""
import copy


def run_design_case(namespace,tests,case,after_step=None):
    constructor=copy.deepcopy(case['constructor'])
    obj=namespace[tests['class']](*constructor)
    assert constructor==case['constructor'],'constructor mutated input'
    assert len(case['operations'])==len(case['expected']),'operation result count mismatch'
    if after_step:after_step(obj,None,None)
    for i,(operation,expected) in enumerate(zip(case['operations'],case['expected'])):
        args=copy.deepcopy(operation['args'])
        actual=getattr(obj,operation['method'])(*args)
        assert actual==expected,(tests['class'],i,operation,actual,expected)
        if expected is None:assert actual is None
        if isinstance(expected,bool):assert isinstance(actual,bool)
        assert args==operation['args'],'operation mutated input'
        if after_step:after_step(obj,operation,actual)
    return obj
