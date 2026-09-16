"""第 02 章：用枚举、内建运算和格式参照核对 16 个完整解法。"""
from collections import Counter
from itertools import combinations, permutations, product, zip_longest
import copy, hashlib, ipaddress, json, random, re, string
from catalog import ROOT, catalog
from build import load_content


def verify():
    data = load_content(catalog()[1])
    problems = {p['id']: p for p in data['problems']}
    methods = {}
    counts = Counter()
    rng = random.Random(20260908)
    for pid, p in problems.items():
        ns = {}
        exec('from __future__ import annotations\n' + p['code'], ns)
        methods[pid] = getattr(ns['Solution'](), p['tests']['method'])

    def call(pid, *args):
        counts[pid] += 1
        return methods[pid](*args)

    def equal(pid, args, expected):
        result = call(pid, *copy.deepcopy(args))
        assert result == expected, (pid, args, expected, result)

    # 原地题检查原对象内容、返回约定和有效前缀，不只检查打印结果。
    for _ in range(250):
        a = [rng.randrange(-3, 4) for _ in range(rng.randrange(18))]
        b = a.copy()
        assert call(283, b) is None
        assert b == [x for x in a if x != 0] + [0] * a.count(0)
        a = sorted(a or [0])
        b = a.copy()
        size = call(26, b)
        assert size == len(set(a)) and b[:size] == sorted(set(a))
        left = sorted(rng.choices(range(-5, 6), k=rng.randrange(12)))
        right = sorted(rng.choices(range(-5, 6), k=rng.randrange(12)))
        dest, source = left + [0] * len(right), right.copy()
        assert call(88, dest, len(left), source, len(source)) is None
        assert dest == sorted(left + right) and source == right
        colors = rng.choices(range(3), k=rng.randrange(1, 25))
        b = colors.copy()
        assert call(75, b) is None and b == sorted(colors)
        a = [rng.randrange(-5, 6) for _ in range(rng.randrange(1, 20))]
        k = rng.randrange(100)
        shift = k % len(a)
        expected = a[-shift:] + a[:-shift] if shift else a.copy()
        b = a.copy()
        assert call(189, b, k) is None and b == expected

    # 相向指针与去重：完整枚举所有候选，参照不采用正文的指针规则。
    for _ in range(350):
        s = ''.join(rng.choices(string.ascii_letters + string.digits + ' ,.!?:;', k=rng.randrange(30)))
        clean = ''.join(ch.lower() for ch in s if ch.isalnum())
        equal(125, [s], clean == clean[::-1])
        heights = rng.choices(range(11), k=rng.randrange(2, 12))
        expected = max(min(heights[i], heights[j]) * (j-i) for i, j in combinations(range(len(heights)), 2))
        equal(11, [heights], expected)
        a = rng.choices(range(-5, 6), k=rng.randrange(3, 12))
        expected = {tuple(sorted(triple)) for triple in combinations(a, 3) if sum(triple) == 0}
        result = call(15, a.copy())
        assert all(len(triple) == 3 for triple in result)
        actual = [tuple(sorted(triple)) for triple in result]
        assert len(actual) == len(set(actual)) and set(actual) == expected

    # 下一个排列：枚举三种值构成的所有短数组，按全部不同排列的字典序取后继。
    permutation_cache = {}
    for n in range(1, 7):
        for values in product(range(3), repeat=n):
            key = tuple(sorted(values))
            if key not in permutation_cache:
                permutation_cache[key] = sorted(set(permutations(key)))
            choices = permutation_cache[key]
            expected = list(choices[(choices.index(values) + 1) % len(choices)])
            actual = list(values)
            assert call(31, actual) is None and actual == expected, (31, values, actual, expected)

    for _ in range(300):
        words = [''.join(rng.choices('abcd', k=rng.randrange(1, 8))) for _ in range(rng.randrange(1, 8))]
        s = ' ' * rng.randrange(4) + (' ' * rng.randrange(1, 5)).join(words) + ' ' * rng.randrange(4)
        equal(151, [s], ' '.join(s.split()[::-1]))
        prefix = ''.join(rng.choices('ab', k=rng.randrange(6)))
        words = [prefix + ''.join(rng.choices('abcd', k=rng.randrange(8))) for _ in range(rng.randrange(1, 8))]
        shortest = min(words, key=len)
        candidates = [shortest[:i] for i in range(len(shortest)+1)]
        expected = max((p for p in candidates if all(w.startswith(p) for w in words)), key=len)
        equal(14, [words], expected)
        def version():
            return '.'.join('0' * rng.randrange(4) + str(rng.randrange(1000)) for _ in range(rng.randrange(1, 8)))
        a, b = version(), version()
        pairs = list(zip_longest(map(int, a.split('.')), map(int, b.split('.')), fillvalue=0))
        va, vb = tuple(x for x, _ in pairs), tuple(y for _, y in pairs)
        equal(165, [a, b], (va > vb) - (va < vb))
        x, y = rng.randrange(10**30), rng.randrange(10**30)
        equal(415, [str(x), str(y)], str(x + y))
        equal(43, [str(x), str(y)], str(x * y))

    # 题目规模内的大数边界，参考运算只用于验证，不进入可提交解法。
    for n in [1, 2, 9, 50, 199, 200]:
        nine = '9' * n
        equal(43, [nine, nine], str(int(nine)**2))
        equal(43, [nine, '10'], nine + '0')
        equal(43, ['1', nine], nine)
    for n in [1, 20, 200, 10000]:
        equal(415, ['9' * n, '1'], '1' + '0' * n)
        equal(415, ['1' + '0' * (n-1), '0'], '1' + '0' * (n-1))

    # atoi 参照用锚定开头的正则抽取数字前缀，再做数学截断。
    def atoi_ref(s):
        match = re.match(r'^ *([+-]?)([0-9]+)', s)
        if not match:
            return 0
        value = int(match.group(1) + match.group(2))
        return max(-(2**31), min(2**31-1, value))
    samples = ['', ' ', '+', '-', '+-12', '++1', '0-1', '  + 42', '1e9', '12.34']
    for value in [-2**31-1, -2**31, -2**31+1, 2**31-2, 2**31-1, 2**31]:
        samples += [str(value), '   '+str(value)+'abc']
    for _ in range(500):
        samples.append(''.join(rng.choices(' +-.abc0123456789', k=rng.randrange(80))))
        samples.append(' ' * rng.randrange(5) + rng.choice(['', '+', '-']) + '0' * rng.randrange(10)
                       + ''.join(rng.choices(string.digits, k=rng.randrange(1, 60)))
                       + rng.choice(['', 'xyz12', ' 45', '-6']))
    for s in samples:
        equal(8, [s], atoi_ref(s))

    # ipaddress 接受真实网络中的压缩 IPv6；先限定本题的八段完整写法。
    # 正则限定字符/结构，库验证数值。它们与正文逐段早返回的流程独立。
    def ip_ref(s):
        if re.fullmatch(r'(?:[0-9]+\.){3}[0-9]+', s):
            if any(len(part) > 1 and part.startswith('0') for part in s.split('.')):
                return 'Neither'
            try:
                ipaddress.IPv4Address(s)
                return 'IPv4'
            except ipaddress.AddressValueError:
                return 'Neither'
        if re.fullmatch(r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}', s):
            try:
                ipaddress.IPv6Address(s)
                return 'IPv6'
            except ipaddress.AddressValueError:
                return 'Neither'
        return 'Neither'
    samples = ['', '::1', '1:2:3:4:5:6:7:8:', '.1.2.3', '1.2.3.4.',
               '01.2.3.4', '1.2.3.256', '1:2:3:4:5:6:7:abcd0', '1:2:3:4:5:6:7:g']
    for _ in range(250):
        parts = [str(rng.randrange(256)) for _ in range(4)]
        good = '.'.join(parts)
        samples += [good, good+'.', '.'+good, good.replace('.', '..', 1), '0'+good]
        parts[rng.randrange(4)] = str(rng.randrange(256, 10000))
        samples.append('.'.join(parts))
        parts = [format(rng.randrange(65536), rng.choice(['x', 'X'])) for _ in range(8)]
        good = ':'.join(parts)
        samples += [good, good+':', good.replace(':', '::', 1), good+'g']
        parts[rng.randrange(8)] = ''
        samples.append(':'.join(parts))
    for s in samples:
        equal(468, [s], ip_ref(s))

    assert set(counts) == set(problems), ('missing coverage', set(problems)-set(counts))
    report = {'status': 'PASS', 'chapter': 2, 'problems': len(problems),
              'cases': sum(counts.values()),
              'checks': [{'id': pid, 'cases': counts[pid],
                          'code_sha256': hashlib.sha256(problems[pid]['code'].encode()).hexdigest()}
                         for pid in sorted(problems)],
              'note': '随机种子固定；小规模穷举和参考解检查，不声称穷举所有合法输入。'}
    (ROOT/'arrays-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k not in ('checks', 'note')}, ensure_ascii=False))


if __name__ == '__main__':
    verify()
