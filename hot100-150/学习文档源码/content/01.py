from textwrap import dedent

CHAPTER = {
 'lead':'哈希表不是一种固定套路。先判断要存“位置”“次数”还是“分组”，再解释查表如何替代重复枚举。',
 'intro':[
  '这四题的共同点是反复询问“某个值是否出现过”。两数之和要找搭档，异位词要比较频次，最长连续序列要判断前驱与后继。把已经得到的信息放入字典或集合，后续查询就不必重新扫描整个输入。',
  'Python 的 dict 保存键到值的映射，set 只保存不同的元素。选哪一种取决于下一步需要什么：只判断存在用 set；需要下标、次数或分组列表就用 dict。通常按平均 O(1) 分析哈希查询，不把它误写成无条件的最坏 O(1)。',
  '本章先学 1 的位置映射，再学 242 的频次相等，把相等判定推广为 49 的分组，最后用 128 训练“如何避免重复扩展”。不要只因为都出现了哈希表，就忽略它们存储信息的区别。'
 ],
 'sections':[
  {'title':'从查询目标决定状态','body':['每次读到新元素，先写出你想快速查询的问题。若需要返回原下标，字典的值就不能只存 True；若重复次数有意义，集合会丢失必要信息。','让键表示“怎样才算同类”。第 49 题中，eat 与 tea 虽然原字符串不同，但排好序后都是 aet。这个共同表示就是分组键。'], 'diagram':'需要原位置 → dict[值] = 下标\n需要出现次数 → dict[元素] = 次数\n需要所有同类对象 → dict[特征] = 列表\n只需要是否存在 → set[元素]'},
  {'title':'复杂度要数完整的工作量','body':['查表快，不等于整个算法一定 O(n)。如果每个单词都要排序，还要加上排序的成本；如果从每个数都向后扩展，仍可能重复走过相同连续段。','第 128 题把“只从没有前驱的元素开始”作为规则，才使一个连续段只展开一次。这个避免重复工作的证明比背诵 O(n) 更重要。']}
 ],
 'apis':[
  {'signature':'dict.get(key, default=None) -> value','description':['按 key 读取值，缺失时返回 default，不会自动插入键。freq[x] = freq.get(x, 0) + 1 同时处理第一次出现和后续重复。Go 的 map 缺失键读取有零值；Python 的普通 dict 直接读取缺失键会抛 KeyError，所以这里明确给默认值。']},
  {'signature':'set(iterable) -> set\nsorted(iterable) -> list','description':['set 根据可哈希元素去重，不保证按输入顺序遍历。sorted 返回一个新的有序列表，不修改原输入；sorted("tea") 得到 ["a", "e", "t"]，再用 "".join(...) 得到字符串键 "aet"。']}
 ],
 'problems':[]
}

CHAPTER['problems'].append({
 'id':1,'slug':'two-sum',
 'summary':'给定整数数组 nums 和 target，找到两个不同下标，使对应元素之和等于 target，返回这两个下标。原题保证有且仅有一个有效答案，同一位置不能用两次。',
 'baseline':'最直接的做法是枚举第一个下标 i，再枚举后面的 j，检查 nums[i]+nums[j]。这样不会漏解，但每个元素都要向后重复查找，总共需要 O(n²) 次比较。',
 'insight':'如果当前数是 x，需要的另一个数已经唯一确定为 target-x。我们不必枚举所有搭档，只要知道这个补数此前有没有出现，以及它出现的下标。于是把此前元素存成“值 → 下标”的字典。',
 'steps':[
  '建立空字典 seen。它只保存当前下标之前见过的元素，不包含当前元素。',
  '遍历到下标 i、值 x 时，计算 complement = target - x。先查询 complement 是否在 seen。',
  '若存在，返回 [seen[complement], i]。字典中的位置一定在 i 之前，所以两个下标天然不同。',
  '若不存在，再把 seen[x] = i 存进去，让后面的元素可以使用 x。',
  '重复值也能正确处理。例如 [3,3]、target=6，第一个 3 先存下标 0，第二个 3 查到它，再返回 [0,1]。'
 ],
 'invariant':'处理下标 i 之前，seen 中每个记录都来自区间 [0,i)。任何有效答案若右端下标是 i，它的左端值一定是 target-nums[i]，并且已经可以查到。因为每个右端点都会被检查，所以不会漏掉唯一答案；先查后存也排除了使用自身两次的错误。',
 'examples':[{'label':'补数查找：target=9','input':'nums=[2,7,11,15], target=9','output':'[0,1]','frames':[
  {'title':'开始：还没有历史元素','note':'seen 为空。我们需要两个不同下标，因此还不能用当前元素填补自己的搭档。','array':[2,7,11,15],'active':[],'metrics':[['seen','{}']]},
  {'title':'读取下标 0 的 2','note':'补数是 9−2=7；历史字典中没有 7。这轮没有答案。','array':[2,7,11,15],'active':[0],'pointers':{'i':0},'metrics':[['补数',7],['seen','{}']]},
  {'title':'把 2 留给后面的元素使用','note':'记录 seen[2]=0。字典值是原下标，不能只保存“存在”。','array':[2,7,11,15],'active':[0],'table':{'headers':['值','原下标'],'rows':[[2,0]]}},
  {'title':'读取下标 1 的 7，查到搭档','note':'补数是 9−7=2，seen[2]=0。两个下标分别是 0 和 1，返回 [0,1]。后面的 11、15 不必再扫描。','array':[2,7,11,15],'active':[0,1],'pointers':{'旧':0,'i':1},'metrics':[['对应数值','2+7=9'],['返回','[0,1]']]}
 ]}],
 'walkthrough':['第一轮查询 7 失败，不表示 2 永远没用，只是它的搭档尚未出现。因此记录 2 的位置。','第二轮查询的是 2，而不是继续尝试 11、15。哈希表把“向前枚举所有搭档”压缩成一次查询。','若 target=4 且首个元素是 2，先存再查会错误地把下标 0 使用两次；本解法的操作顺序防止了这种情况。'],
 'code':'''
class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        # seen 保存“已遍历的值 → 原下标”，用于寻找当前数的搭档。
        seen: dict[int, int] = {}
        for i, x in enumerate(nums):
            # 当前值是 x，只需查找唯一需要的补数 target-x。
            complement = target - x
            # 先查后存：这样字典里不含当前下标，避免一个元素用两次。
            if complement in seen:
                return [seen[complement], i]
            # 没有找到搭档，就把当前位置留给后面的元素使用。
            seen[x] = i
        # 原题保证有解；这里仅作没有答案时的兜底。
        return []
'''.strip(),
 'code_notes':['enumerate 同时给出下标和值，对应 Go 中常见的 range 遍历；返回的是下标，不能返回补数本身。','if complement in seen 放在 seen[x]=i 前面，是正确性的组成部分，不是可以随意调换的风格选择。','末尾 return [] 是没有找到答案时的兜底返回；原题保证有解，合法测试通常会在循环内返回。'],
 'pitfalls':['把 set 用作唯一状态会失去下标，还得额外扫描定位，无法直接完成题目要求。','不要先排序再直接返回排序后下标，那已经不是原数组的位置。','有重复值时仍必须使用两个位置；用 [3,3]、target=6 检查这个条件。'],
 'complexity':'平均时间 O(n)，每个元素最多一次查询和一次写入；额外空间 O(n)。哈希操作按平均 O(1) 计。',
 'quiz':{'question':'seen 中同一个值被较晚下标覆盖，会漏掉答案吗？','answer':'不会。需要这个值作为搭档时，只要保留其中一个更早位置就能组成答案。原题只要求返回一个答案；若要求枚举全部下标对，才需要保存每个值对应的所有位置。'},
 'tests':{'method':'twoSum','cases':[{'args':[[2,7,11,15],9],'expected':[0,1]},{'args':[[3,2,4],6],'expected':[1,2]},{'args':[[3,3],6],'expected':[0,1]},{'args':[[-3,4,3,90],0],'expected':[0,2]}]}
})

CHAPTER['problems'].append({
 'id':242,'slug':'valid-anagram',
 'summary':'判断字符串 s 和 t 是否由完全相同的字符及次数组成。字符顺序可以不同，但少一个、多一个，或者某种字符次数不同，都不算异位词。',
 'baseline':'把两个字符串排序后比较，是容易想到的正确做法，时间 O(n log n)。如果只想知道字符次数是否一致，排序所恢复的整体顺序其实是多余的信息。',
 'insight':'把 s 的每个字符看作一张待匹配的票，扫描 t 时消耗相同字符的票。缺少某张票就立即失败；两串等长且每个字符都成功匹配时，最终应没有剩余票。',
 'steps':['若两串长度不同，直接返回 False；频次完全相同必然要求总长度相同。','扫描 s，记录 freq[ch] 的出现次数。','扫描 t。若 ch 不在 freq 中，说明 t 需要的这个字符已无余量，返回 False。','否则把该字符次数减一。减到 0 时删除键，保持字典只记录尚未消耗完的字符。','扫描完成后返回字典是否为空。这个状态也能帮助你解释为什么集合比较不足以解决题目。'],
 'invariant':'处理 t 的前 i 个字符后，freq 精确保存 s 中尚未被这段前缀匹配掉的字符多重集合。一次消耗只减少对应字符的一个实例，不影响别的字符。出现缺货就不可能匹配；全部消耗完成后字典为空，说明每种次数都一致。',
 'examples':[{'label':'相同集合，却不是异位词','input':'s="aab", t="abb"','output':'False','frames':[
  {'title':'先统计 s','note':'a 有两张票，b 有一张票。单看字符集合 {a,b} 会丢失这个区别。','diagram':'s: a a b\nt: a b b','table':{'headers':['字符','剩余次数'],'rows':[['a',2],['b',1]]}},
  {'title':'消耗 t 的第一个 a','note':'a 从 2 减到 1，还不能删除 a 的键。','array':['a','b','b'],'active':[0],'pointers':{'i':0},'table':{'headers':['字符','剩余次数'],'rows':[['a',1],['b',1]]}},
  {'title':'消耗第一个 b','note':'b 从 1 减到 0，删除键；a 仍有一张票未消耗。','array':['a','b','b'],'active':[1],'pointers':{'i':1},'table':{'headers':['字符','剩余次数'],'rows':[['a',1]]}},
  {'title':'第二个 b 没有票可用','note':'字典中已没有 b。立即返回 False，不会因为两串字符集合相同而误判。','array':['a','b','b'],'active':[2],'pointers':{'i':2},'metrics':[['b 剩余',0],['结果','False']]}
 ]}],
 'walkthrough':['aab 和 abb 等长，也包含相同的字符种类，所以“长度相等 + 集合相等”仍不足以判定异位词。','消耗第一轮 a、b 后，只剩一个 a，而 t 最后需要的是 b；这正是逐字符频次匹配发现的矛盾。','对成功例子 anagram 与 nagaram，每轮都能消耗票，最后所有键消失，返回 True。'],
 'code':'''
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        # 总字符数不同，不可能逐个配对。
        if len(s) != len(t):
            return False
        # freq[ch] 表示 s 中还没有被 t 匹配掉的字符个数。
        freq: dict[str, int] = {}
        # 先给 s 的每个字符登记一份可用数量。
        for ch in s:
            freq[ch] = freq.get(ch, 0) + 1
        for ch in t:
            # t 需要的字符已无余量，立即判定失败。
            if ch not in freq:
                return False
            freq[ch] -= 1
            # 零次数必须删除，否则最后的空字典判断会失效。
            if freq[ch] == 0:
                del freq[ch]
        # 所有数量恰好耗尽，才说明字符种类和次数完全相同。
        return not freq
'''.strip(),
 'code_notes':['not freq 在字典为空时为 True。这里空字典不是“没有做过统计”，而是所有票都已经匹配完的状态。','del freq[ch] 真正移除键；把值留为 0 会使 not freq 仍为 False，因此这段代码的返回条件依赖删除零次数键。','字典方案能自然处理更一般的字符。若使用 26 位数组，必须先确认输入仅含小写英文字母。'],
 'pitfalls':['set(s)==set(t) 不保留重复次数，会把 aab 和 abb 误判为相同。','直接 freq[ch]-=1 前要确认 ch 存在，否则 Python 会抛 KeyError。','若选择比较两个计数字典，应让零次数键的处理方式一致。'],
 'complexity':'时间 O(n+m)，其中 n、m 是两串长度；额外空间 O(|Σ|)，Σ 为出现的字符集合。固定小写英文字母表时可视为 O(1)。',
 'alternative':'排序比较也正确，更适合从直觉快速得到基线解法。计数法则把“排列后的具体顺序”压缩成“每种元素的数量”，这会直接引出下一题的分组特征。',
 'quiz':{'question':'这个判定能直接用来把一万个单词分组吗？','answer':'可以两两比较，但比较次数可能达到 O(n²)。更好的做法是为每个单词计算一个可作为字典键的统一特征，把同一特征的单词直接追加进同一组，见第 49 题。'},
 'tests':{'method':'isAnagram','cases':[{'args':['anagram','nagaram'],'expected':True},{'args':['aab','abb'],'expected':False},{'args':['a','aa'],'expected':False},{'args':['中a','a中'],'expected':True}]}
})

CHAPTER['problems'].append({
 'id':49,'slug':'group-anagrams',
 'summary':'把字符串数组中的单词按异位词关系分组。每组中的单词字符种类和出现次数完全相同，输出组的顺序与组内顺序不作要求。',
 'baseline':'为每个新单词遍历已有组，逐一判断它与组代表是否为异位词。即使单次判断已经用计数优化，组数很多时仍会重复做大量比较。问题真正需要改进的是“如何定位属于哪个组”。',
 'insight':'异位词排序后会得到同一个字符串，非异位词不会得到相同结果。因此可以把排序后的字符串当作规范化特征：不同原单词经过转换后，相同特征就直接对应同一组。',
 'steps':['准备字典 groups，键是单词排序后的字符串，值是这一组的原单词列表。','对每个 word，先计算 key = "".join(sorted(word))。这里只改变用来查表的特征，不改变要输出的原单词。','若 key 尚不存在，创建一个空列表；然后把 word 追加进去。','所有单词处理完后，返回 groups.values() 中的各个列表，用 list(...) 把字典视图转换为题目需要的列表结果。','原数组中相同单词出现多次时，要追加多次。题目是分组，不是去重。'],
 'invariant':'处理完前 i 个单词后，字典里每个键对应的列表恰好收集了这段前缀中具有该排序特征的所有原单词。字符排序后的序列完全确定每种字符的次数，因此“特征相同”与“互为异位词”等价，不会把不同类错误合并。',
 'examples':[{'label':'六个单词分成三组','input':'["eat","tea","tan","ate","nat","bat"]','output':'[["eat","tea","ate"],["tan","nat"],["bat"]]（顺序可不同）','frames':[
  {'title':'eat 创建 aet 组','note':'排序只用来得到键 aet，输出中保留 eat 的原始顺序。','array':['eat','tea','tan','ate','nat','bat'],'active':[0],'table':{'headers':['特征键','原单词列表'],'rows':[['aet','[eat]']]}},
  {'title':'tea 直接进入已有组','note':'tea 的特征同样是 aet，一次字典查询即可定位，无需逐一比较组内单词。','array':['eat','tea','tan','ate','nat','bat'],'active':[0,1],'table':{'headers':['特征键','原单词列表'],'rows':[['aet','[eat, tea]']]}},
  {'title':'tan 创建 ant 组','note':'ant 与 aet 不同，所以需要一个新组。','array':['eat','tea','tan','ate','nat','bat'],'active':[2],'table':{'headers':['特征键','原单词列表'],'rows':[['aet','[eat, tea]'],['ant','[tan]']]}},
  {'title':'ate 与 nat 各自追加','note':'ate → aet；nat → ant。字典将两个不同的组分别维护。','array':['eat','tea','tan','ate','nat','bat'],'active':[3,4],'table':{'headers':['特征键','原单词列表'],'rows':[['aet','[eat, tea, ate]'],['ant','[tan, nat]']]}},
  {'title':'bat 创建第三组，收集所有列表','note':'bat → abt。最终返回三个列表，字典中的特征键不需要放进答案。','array':['eat','tea','tan','ate','nat','bat'],'active':[5],'table':{'headers':['特征键','原单词列表'],'rows':[['aet','[eat, tea, ate]'],['ant','[tan, nat]'],['abt','[bat]']]}}
 ]}],
 'walkthrough':['前三个单词形成两个组，说明原字符串相同并非必要条件：eat 与 tea 不同，但规范化结果相同。','后面的 ate、nat 都能复用已有键；不会创建重复组。','bat 需要新键 abt。最后 list(groups.values()) 只取分组结果，得到题目要求的二维列表。'],
 'code':'''
class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        # 原题仅含小写英文字母，用 26 位次数代替逐词排序。
        groups: dict[tuple[int, ...], list[str]] = {}
        for word in strs:
            counts = [0] * 26
            for char in word:
                # 第 0 位对应 a，第 25 位对应 z；重复字母逐次累计。
                counts[ord(char) - ord('a')] += 1
            # 列表不可哈希，转成不可变元组后才能用作字典键。
            key = tuple(counts)
            if key not in groups:
                groups[key] = []
            # 输出保存原单词，不改它内部的顺序，也不删除重复单词。
            groups[key].append(word)
        return list(groups.values())
'''.strip(),
 'api':{'signature':'str.join(iterable_of_strings) -> str\ndict.values() -> dict_values','description':['连接符调用 join，把字符串序列连接为一个新字符串；空连接符不会插入额外字符。values() 返回随字典变化的值视图，不是普通列表，list(...) 才把这些值收集成列表。']},
 'code_notes':['计数位的顺序固定为 a 到 z，不能只保存出现过的次数而丢掉字母位置。', 'tuple(counts) 才能作为字典键；groups[key] 保存原单词列表。', '默认方法依赖原题的小写英文字母限制；若推广到任意 Unicode 字符，应改用排序特征或稀疏计数特征。'],
 'pitfalls':['把 key 追加进组会把原始单词全部变为排序结果，丢失题目要求的原字符串。','同一个单词出现两次也要保留两份，不要把组值定义成 set。','不能只用“字符集合”作为特征，aab 和 abb 会发生误合并。'],
 'complexity':'设总字符数为 S、单词数为 n、不同分组数为 g。固定 26 字母表，平均时间 O(S+26n)，辅助空间 O(26g)，输出引用空间 O(n)。',
 'alternative':'若输入只含 26 个小写英文字母，可把每个单词转成 26 位计数元组 tuple(counts)。构造特征无需排序，时间变为 O(所有单词总长度 + 26n)。必须转换成元组，因为 list 不能作为键；计数元组中每一位对应固定字母，不能省掉为零的位置。',
 'quiz':{'question':'把特征改成所有字符码点的总和，可不可以？','answer':'不可以。不同字符组合可能有相同总和，例如 ad 与 bc 的码点和相同，却并非异位词。分组特征必须保留足够信息，保证相等特征不会把不同频次分布混在一起。'},
 'tests':{'method':'groupAnagrams','compare':'groups','cases':[{'args':[['eat','tea','tan','ate','nat','bat']],'expected':[['eat','tea','ate'],['tan','nat'],['bat']]},{'args':[['']],'expected':[['']]},{'args':[['aab','abb','aab']],'expected':[['aab','aab'],['abb']]},{'args':[['a']],'expected':[['a']]}]}
,
 'submission': {'name': '26 位计数元组分组', 'why': '原题限定小写英文字母，计数特征可以消除逐词排序。前面 aet/ant 的规范化例子展示分组原则，提交代码用等价的频次特征。', 'steps': ['每个单词创建 26 个计数位。', '统计每个字母出现次数，将列表转为元组作为键。', '把原单词追加到对应键的列表，最后返回所有分组。'], 'diagram': 'eat / tea / ate → a:1, e:1, t:1 → 同一个计数元组\ntan / nat → a:1, n:1, t:1 → 另一个计数元组'},
})

CHAPTER['problems'].append({
 'id':128,'slug':'longest-consecutive-sequence',
 'summary':'给定未排序整数数组，求其中数值连续的最长序列长度。数值可以从不同下标取出，原数组中不必相邻；重复数字不增加连续长度。目标是 O(n) 时间。',
 'baseline':'排序去重后逐个检查相邻差是否为 1，可以正确求解，但排序需要 O(n log n)。另一种看似更快的写法是把数放进集合，再从每个数不断查 x+1；它会反复扫描同一个长连续段，最坏仍是 O(n²)。',
 'insight':'一段连续数字只有最小的那个数没有前驱。若 x−1 在集合里，x 就处在某个连续段内部，没必要从它再次向后扩展。只从不存在前驱的数开始扫描，整段便只会走一次。',
 'steps':['把 nums 转成集合 values，去掉重复数字并获得快速存在性查询。','遍历集合中的每个 x；若 x−1 存在，跳过，因为更小的起点会负责覆盖这个连续段。','否则 x 是一个段的起点，设置 current=x、length=1。','只要 current+1 存在，就向后走一步并增加长度。','段结束时更新 best。扫描其他起点，最终得到各段长度的最大值；空数组保留初始答案 0。'],
 'invariant':'每个不同数字恰好属于一个连续段，而每段恰好有一个没有前驱的起点。从该起点不断查询后继会遍历完整的段。内部元素不会再次触发扩展，因此所有内层 while 的成功步数相加不超过不同元素数，外层查询也只有线性次。',
 'examples':[{'label':'定位连续段的真正起点','input':'nums=[100,4,200,1,3,2]','output':'4，对应数值序列 [1,2,3,4]','frames':[
  {'title':'集合只关心数值是否存在','note':'下标顺序不决定连续关系。这里关注会产生最长答案的起点 1；集合实际遍历顺序不保证与画面顺序相同。','array':[100,4,200,1,3,2],'active':[],'metrics':[['不同值','{1,2,3,4,100,200}'] ]},
  {'title':'4 不是起点','note':'因为 3 存在，不能从 4 再扩展一次。2、3 也有前驱，因此都不是起点。','array':[100,4,200,1,3,2],'active':[1,4],'metrics':[['检测','4−1=3，存在'],['动作','跳过']]},
  {'title':'1 没有前驱，可以开始','note':'0 不在集合中，1 是本段最小值。初始化 current=1、length=1。','array':[100,4,200,1,3,2],'active':[3],'metrics':[['current',1],['length',1]]},
  {'title':'沿数值后继走到 2、3','note':'查询的是数值 2、3 是否存在，不是下一个数组位置是什么。长度增加到 3。','array':[100,4,200,1,3,2],'active':[3,4,5],'metrics':[['current',3],['length',3]]},
  {'title':'找到 4，找不到 5','note':'本段长度为 4。100 与 200 都是长度为 1 的孤立段，不能超过它，最终答案是 4。','array':[100,4,200,1,3,2],'active':[1,3,4,5],'metrics':[['连续段','1 → 2 → 3 → 4'],['best',4]]}
 ]}],
 'walkthrough':['原输入中的 1、2、3、4 位于不同下标，仍构成连续数值序列；这和要求连续区间的滑动窗口题不同。','如果从 1 扫到 4，又从 2 扫到 4、从 3 扫到 4，就会重复工作。起点规则正是用来消除这些重复。','空数组返回 0；[1,2,2,3] 去重后仍是 [1,2,3]，所以长度是 3。负数也可以用完全相同的前驱后继规则处理。'],
 'code':'''
class Solution:
    def longestConsecutive(self, nums: list[int]) -> int:
        # 集合去重，避免重复起点让同一连续段被反复扫描。
        values = set(nums)
        best = 0
        for x in values:
            # 只有没有前驱的数才是连续段起点。
            if x - 1 in values:
                continue
            current = x
            length = 1
            # 从起点向后扩展，每个数只属于一个被扫描的连续段。
            while current + 1 in values:
                current += 1
                length += 1
            best = max(best, length)
        # 返回最长段的长度，不要求这些数在原数组里相邻。
        return best
'''.strip(),
 'code_notes':['外层遍历 values 而非 nums，避免某个起点在原数组里重复出现多次，从而反复扫描长连续段。','continue 提前跳过段内部元素，内层 while 只在真正起点执行。','不能边遍历这个 set 边向它添加或删除元素；本解法始终只查询，不修改集合。'],
 'pitfalls':['“两个嵌套循环就是 O(n²)”和“用了 set 就是 O(n)”都不可靠，要数实际成功扩展次数。','忘记前驱判断会重复扩展同一段；用原数组作外层循环又可能因重复起点导致重复扩展。','本题不是最长递增子序列，也不是最长连续子数组，不受原下标顺序限制。'],
 'complexity':'平均时间 O(n)，建立集合与所有段扩展合计线性；额外空间 O(n)。哈希集合的存在性查询按平均 O(1) 计。',
 'quiz':{'question':'如果 nums=[1,1,1,2,3,4]，外层遍历 nums 而不遍历 set(nums) 会怎样？','answer':'三个 1 都没有前驱 0，会各自把 1→4 扫一遍。若重复起点与连续段都很长，就会失去线性保证。因此外层也必须去重。'},
 'tests':{'method':'longestConsecutive','cases':[{'args':[[100,4,200,1,3,2]],'expected':4},{'args':[[1,1,1,2,3,4]],'expected':4},{'args':[[]],'expected':0},{'args':[[-2,-1,0,2]],'expected':3},{'args':[[0,3,7,2,5,8,4,6,0,1]],'expected':9}]}
})
