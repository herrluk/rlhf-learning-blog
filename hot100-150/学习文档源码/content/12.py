from textwrap import dedent

CHAPTER = {
 'lead':'把网格的邻接关系看成边，把访问标记看成已安排的工作。连通块搜索、同步传播和依赖消除都需要遍历图，但它们维护的状态与结束条件不同。',
 'intro':['学习顺序：200 岛屿数量 → 695 最大面积 → 994 腐烂传播 → 133 克隆图 → 207 课程可行性 → 210 输出课程顺序。先认识四邻接，再处理显式节点和有向依赖。','网格坐标统一写为 (行,列)，行向下增加、列向右增加。上下左右可连通，对角线不算边；必须先验证坐标范围，才能读取格子。','本章网格主解会修改 grid：岛屿题将已发现陆地改为水，腐烂题将新鲜橘子改为腐烂。若业务要求保留地图，应先逐行复制或使用独立 visited；不要误以为给参数换个变量名就复制了矩阵。'],
 'sections':[
  {'title':'DFS 与 BFS：搜索目标决定队列含义','body':['找连通块时，DFS 栈与 BFS 队列都可以；不要求最短时间，只需完整发现同一块中的节点。','边的代价都为一步时，BFS 的层数等于最短距离。多个起点在时刻 0 同时出发，就应全部进入初始队列，不能逐个传播后相加。','处理可能很大的连通网格时，用显式栈或队列避免 Python 递归深度限制。'], 'diagram':'连通块：从一个入口完整搜索 → 标记整块\n最短传播：距离0全部起点 → 距离1 → 距离2 → …\n有向依赖：所有前置已完成 → 当前课程才能进入队列'},
  {'title':'发现时标记，避免同一节点重复入队','body':['一个格子可能被多个已访问邻居同时发现。如果等到弹出时才标记，它可能已被重复放入队列；在安排搜索的那一刻标记，能保证每个格子只安排一次。','克隆图也遵循相同顺序：先把旧节点对应的新对象放进映射，再搜索邻居。这样遇到返回旧节点的边时，可以直接使用已有副本。'], 'diagram':'检查尚未发现 → 立即标记/建立副本 → 加入待处理集合\n                              ↓\n                    其他入口再次遇到时直接复用'},
  {'title':'图遍历标记与回溯标记不要混用','body':['200 的 visited 表示这个格子所属连通块已被全局处理，之后永远无需重新计数，所以不撤销。','下一章 79 单词搜索中的 visited 只约束当前一条拼词路径；换一个路径时，同一格子可能再次参与，因此退出分支必须撤销。','先说明标记的生命周期，再决定离开节点时是否恢复。只背“访问后置一、结束后置零”会把两类问题混在一起。']},
  {'title':'课程依赖的箭头从前置课程出发','body':['prerequisites 中 [a,b] 表示先学 b 才能学 a，因此画 b→a。indegree[a] 表示还有几门前置课未完成。','完成 b 后只减少它的后续课程的入度；入度从 1 降到 0 才能安排这门课。队列不是“已经访问过的任意节点”，而是“现在已满足全部前置条件的节点”。'], 'diagram':'[课程a, 前置b]  ⇒  b → a\n完成 b：indegree[a] -= 1\n若 indegree[a] == 0：a 可以进入队列'}
 ],
 'apis':[
  {'signature':'deque(iterable=())；append(x)；popleft() -> 队首元素','description':['从 collections 导入 deque。append 在右端加入，popleft 从左端取出，端点操作均为 O(1)。多源 BFS 用所有初始源构造队列。','DFS 可用 list.append 与 list.pop() 在末端操作；不要用 list.pop(0) 实现大规模 BFS。']},
  {'signature':'[row[:] for row in grid] -> 新的二维列表','description':['外层推导创建新的行列表，各 row[:] 复制该行。这里元素是整数或字符串，不可变元素可安全共享。','仅 grid[:] 只复制最外层，内部行仍与原矩阵相同，写 copied[r][c] 仍会影响原图。']},
  {'signature':'copies[old_node] = new_node','description':['字典保存原节点对象到副本对象的映射；默认 Node 按身份区分键。该映射同时承担访问标记和引用翻译，不只是“访问过”的布尔状态。','neighbors 是节点引用列表。克隆时必须把每个原邻居翻译成对应副本，再连接到副本的 neighbors。']}
 ],
 'problems':[]
}

MAP = [['1','1','0','0'],['0','1','0','1'],['1','0','1','1']]
CHAPTER['problems'].append({
 'id':200,'slug':'number-of-islands',
 'summary':'字符矩阵中 "1" 表示陆地、"0" 表示水。上下左右相连的陆地属于同一个岛，返回岛屿数量。主解把发现的陆地原地标记成 "0"。',
 'baseline':'仅数 "1" 得到的是陆地面积，不能区分它们是否连成一块。从每个 "1" 都独立搜索却不保留标记，又会重复统计同一个岛。必须让一次搜索覆盖整块，并让后续扫描知道它已经计数。',
 'insight':'按行扫描，只有遇到尚未发现的陆地才把岛数加一，并从这里搜索完整连通块。搜索发现一格就把它改成水，之后无论通过邻居还是外层扫描再遇到，都不会重复处理。',
 'steps':['建立四个方向，答案初始 0。','扫描每一格；水直接跳过，未发现陆地使答案加一。','把入口标记为水并压栈。','不断弹出位置，检查四邻居；合法陆地先标记，再压栈。','栈空表示本岛全部发现，继续外层扫描。'],
 'invariant':'每次新搜索开始时，入口尚未属于任何已处理连通块。搜索只沿陆地邻接边扩展，因此不会越入其他岛；同一连通块的所有陆地都可从入口到达，最终全部标记。于是每个岛恰好触发一次答案加一。',
 'examples':[{'label':'对角线不把岛连起来','input':'grid=["1100","0101","1011"]（每行实际是字符列表）','output':'3','frames':[
  {'title':'首次发现左上连通块','note':'(0,0)、(0,1)、(1,1) 属于同一个岛，只增加一次岛数。','grid':MAP,'active_cells':[[0,0],[0,1],[1,1]],'metrics':[['岛数',1]]},
  {'title':'同一块标记完毕','note':'外层扫描遇到这三格时都已是水；随后在 (1,3) 发现下一块。','grid':[['0','0','0','0'],['0','0','0','1'],['1','0','1','1']],'active_cells':[[1,3],[2,3],[2,2]],'metrics':[['岛数',2]]},
  {'title':'左下角是第三个独立岛','note':'(2,0) 与原来的 (1,1) 只是对角相邻，不存在四邻接路径。','grid':[['0','0','0','0'],['0','0','0','0'],['1','0','0','0']],'active_cells':[[2,0]],'metrics':[['岛数',3]]},
  {'title':'全部陆地被标记','note':'返回 3；原矩阵的所有陆地已经被改成水，数值变化是访问标记。','grid':[['0']*4 for _ in range(3)],'metrics':[['答案',3]]}
 ]}],
 'walkthrough':['一次栈搜索可能处理很多格子，但只有启动这次搜索时才增加岛数。','必须在入栈之前就改为 "0"。例如一个 2×2 陆地块，同一个角可能被两条不同路线同时发现。','坐标检查写在读取 grid[nr][nc] 之前；Python 负下标会从末尾读取，不会自动报错，因此漏掉 nr>=0 会产生跨边界连接。'],
 'code':'''
class Solution:
    def numIslands(self, grid: list[list[str]]) -> int:
        if not grid or not grid[0]:
            return 0
        rows, cols = len(grid), len(grid[0])
        # 只允许上下左右连接，对角线不算同一个岛屿。
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        islands = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != '1':
                    continue
                # 扫描到尚未访问的陆地，说明发现了一个新的连通块。
                islands += 1
                # 入栈前就标记为水，避免同一格被多个邻居重复加入。
                grid[r][c] = '0'
                stack = [(r, c)]
                while stack:
                    x, y = stack.pop()
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        # 先检查边界，再读取相邻格；Python 负下标会绕到末尾，不能漏掉下界。
                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == '1':
                            # 搜索会把整座岛全部标记，之后外层循环就不会重复计数。
                            grid[nx][ny] = '0'
                            stack.append((nx, ny))
        return islands
'''.strip(),
 'code_notes':['本题是字符 "1"，与 695 的整数 1 不同，比较和标记必须对应输入类型。','栈保存坐标元组，当前格子的原数值不需要额外记录。','没有递归调用，连通块很深时也不依赖 Python 调用栈。'],
 'pitfalls':['把八个方向都当邻接。','每弹一个陆地格就把岛数加一。','只复制外层列表就以为已保护原矩阵。','忽略负下标的有效性，导致边缘错误连通。'],
 'complexity':'时间 O(mn)，每格扫描一次、每个陆地至多入栈一次并检查四个方向。栈最坏 O(mn)，原地标记省去独立 visited，但不能因此把总辅助空间写成 O(1)。',
 'quiz':{'question':'[["1","0"],["0","1"]] 有几个岛？','answer':'两个。两块陆地仅对角相邻，不能通过上下左右直接连接。'},
 'tests':{'method':'numIslands','cases':[{'args':[MAP],'expected':3},{'args':[[['1','0'],['0','1']]],'expected':2},{'args':[[['1','1'],['1','1']]],'expected':1},{'args':[[['0']]],'expected':0},{'args':[[['1']]],'expected':1}]}
})

CHAPTER['problems'].append({
 'id':695,'slug':'max-area-of-island',
 'summary':'整数网格中 1 表示陆地，求最大四邻接岛屿的格子数量。没有陆地返回 0；主解将访问过的 1 原地改成 0。',
 'baseline':'先用 200 统计岛屿数量无法得到最大面积：两个地图可能都有三个岛，但每个岛大小不同。搜索过程仍可复用，只需把“每岛一次计数”改成“每个格子计入本岛面积”。',
 'insight':'每次从未标记陆地启动 DFS，建立 area=0。由于入栈前已经标记，每个出栈位置只会出现一次，出栈时 area 加一。整块搜索结束后再用 area 更新全局 best。',
 'steps':['best=0，外层扫描所有格子。','遇到未标记陆地，标记入口、入栈并重置 area。','每弹出一格 area 加一，四邻居中尚未发现的陆地先标记再入栈。','本块结束后 best=max(best,area)。','返回 best。'],
 'invariant':'当前 area 是本次搜索已经弹出的不同陆地格数量，栈保存同一岛已发现但尚未计入的格子。栈空时本岛所有格子恰好计入一次。best 在每次整块结束后等于已处理岛屿的最大面积。',
 'examples':[{'label':'面积是格子数，不是外接矩形','input':'grid=[[1,1,0,0],[0,1,0,1],[1,0,1,1]]','output':'3','frames':[
  {'title':'左上岛不是实心矩形','note':'高亮的三格相连，包围它的 2×2 矩形还包含一格水，所以面积是 3。','grid':[[1,1,0,0],[0,1,0,1],[1,0,1,1]],'active_cells':[[0,0],[0,1],[1,1]],'metrics':[['area',3],['best',3]]},
  {'title':'分别计算每个岛','note':'右下岛也有 3 格，左下孤岛只有 1 格。每开启新岛都重置 area。','table':{'headers':['搜索入口','本岛面积','best'],'rows':[['(0,0)',3,3],['(1,3)',3,3],['(2,0)',1,3]]}},
  {'title':'取最大值而不是求总和','note':'全部陆地总面积为 7，但最大单岛面积为 3。','array':[3,3,1],'active':[0,1],'array_label':'三个岛的面积'}
 ]}],
 'walkthrough':['标记表示“已经安排搜索”，area 表示“已经处理并计数”，二者时机可以不同，只要保证每个位置唯一入栈即可。','如果 area 不在每次新岛开始时归零，最终得到的是累计陆地数，而不是各岛面积。','最大面积允许多个岛并列，题目只要求返回整数面积，不必记录岛的位置。'],
 'code':'''
class Solution:
    def maxAreaOfIsland(self, grid: list[list[int]]) -> int:
        if not grid or not grid[0]:
            return 0
        rows, cols = len(grid), len(grid[0])
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        best = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != 1:
                    continue
                # 发现新岛屿时立即标记起点，开始一次独立的连通块遍历。
                grid[r][c] = 0
                stack = [(r, c)]
                # area 只累计当前这座岛，不与上一座岛混在一起。
                area = 0
                while stack:
                    x, y = stack.pop()
                    # 每个格子只入栈一次，所以每弹出一格恰好增加一单位面积。
                    area += 1
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 1:
                            grid[nx][ny] = 0
                            stack.append((nx, ny))
                # 整座岛遍历完毕后，再与历史最大面积比较。
                best = max(best, area)
        return best
'''.strip(),
 'code_notes':['area 属于一次连通块搜索，best 属于整张地图，初始化层级不同。','比较整数 1，不要复制 200 的字符比较。','外层双循环与内部搜索的总成本是线性叠加，不是对每个格子再完整遍历地图。'],
 'pitfalls':['把岛的包围矩形面积当成陆地面积。','把所有岛的面积累加。','重复入栈导致一个位置被多次计入 area。'],
 'complexity':'时间 O(mn)，显式栈最坏 O(mn)，原矩阵被修改。',
 'quiz':{'question':'两个对角相邻的单格陆地，最大面积是 1 还是 2？','answer':'是 1。它们分属两个岛，分别搜索后得到两个面积 1。'},
 'tests':{'method':'maxAreaOfIsland','cases':[{'args':[[[1,1,0,0],[0,1,0,1],[1,0,1,1]]],'expected':3},{'args':[[[1,0],[0,1]]],'expected':1},{'args':[[[1,1],[1,1]]],'expected':4},{'args':[[[0]]],'expected':0},{'args':[[[1,1,1]]],'expected':3}]}
})

CHAPTER['problems'].append({
 'id':994,'slug':'rotting-oranges',
 'summary':'网格中 0 为空地、1 为新鲜橘子、2 为腐烂橘子。所有腐烂橘子每分钟同时感染四邻接新鲜橘子，返回全部腐烂所需最少分钟数，不能全部感染则 -1。',
 'baseline':'每分钟扫描整张网格也能模拟，但必须将本轮变化延后统一生效，否则一条长链可能在一次扫描里连续传染。多源 BFS 只处理这一分钟真正能向外传播的边界，避免反复扫描不变格子。',
 'insight':'把全部初始腐烂位置作为距离 0 的源同时入队。冻结本轮队列长度，处理它们能感染的格子；这些新格子立刻改为 2 防止重复发现，但留到下一轮才继续传播。BFS 层数对应离最近源的最短感染时间。',
 'steps':['扫描网格，收集全部 2 并统计 fresh 数量。','minutes=0，只要 queue 非空且 fresh>0，就处理一层。','每个可感染邻居立刻改成 2、fresh 减一并入队。','整层结束 minutes 加一。','fresh 为 0 返回 minutes，否则返回 -1。'],
 'invariant':'每轮开始的队列是同一感染时刻的传播源；本轮新发现的邻居距离最近源多一步，不会提前处理。fresh 始终等于尚未感染的格子数，每个新鲜格只在 1→2 的唯一转变时减一。',
 'examples':[{'label':'一轮就是一分钟','input':'grid=[[2,1,1],[1,1,0],[0,1,1]]','output':'4','frames':[
  {'title':'第 0 分钟：只有初始源','note':'新鲜橘子 6 个，队列只包含 (0,0)。','grid':[[2,1,1],[1,1,0],[0,1,1]],'active_cells':[[0,0]],'metrics':[['minutes',0],['fresh',6]]},
  {'title':'第 1 分钟','note':'新感染 (0,1)、(1,0)，它们要等下一分钟才继续扩散。','grid':[[2,2,1],[2,1,0],[0,1,1]],'active_cells':[[0,1],[1,0]],'metrics':[['fresh',4]]},
  {'title':'第 2 分钟','note':'两条路线都可能遇到 (1,1)，首次发现就标成 2，因此 fresh 只减一次。','grid':[[2,2,2],[2,2,0],[0,1,1]],'active_cells':[[0,2],[1,1]],'metrics':[['fresh',2]]},
  {'title':'第 3 分钟','note':'只能新感染 (2,1)，空格不能充当传播媒介。','grid':[[2,2,2],[2,2,0],[0,2,1]],'active_cells':[[2,1]],'metrics':[['fresh',1]]},
  {'title':'第 4 分钟结束','note':'最后的 (2,2) 被感染，fresh=0，返回 4。','grid':[[2,2,2],[2,2,0],[0,2,2]],'active_cells':[[2,2]],'metrics':[['fresh',0],['答案',4]]}
 ]},{'label':'所有源同时出发','input':'grid=[[2,1,1,1,2]]','output':'2','frames':[
  {'title':'两个源都在初始队列','note':'第 1 分钟两端分别感染相邻格，不是先完成左源再处理右源。','grid':[[2,2,1,2,2]],'active_cells':[[0,1],[0,3]]},
  {'title':'中间格第 2 分钟感染','note':'两侧到中间的距离都是 2，只需两分钟。','grid':[[2,2,2,2,2]],'active_cells':[[0,2]]}
 ]}],
 'walkthrough':['初始没有新鲜橘子时，答案就是 0；while 的 fresh 条件避免多处理一层。','队列耗尽但 fresh>0 表示剩余新鲜橘子与所有腐烂源不连通，不能因为“搜索结束”就返回经过的分钟数。','修改 grid 的时刻是发现新感染时，传播的时刻是下一轮；用冻结的 size 明确区分这两个概念。'],
 'code':'''
from collections import deque

class Solution:
    def orangesRotting(self, grid: list[list[int]]) -> int:
        rows, cols = len(grid), len(grid[0])
        # 所有初始腐烂橘子同时入队，它们都是第 0 分钟的传播源。
        queue = deque()
        # 只统计剩余新鲜橘子，便于判断是否仍有无法到达的格子。
        fresh = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 2:
                    queue.append((r, c))
                elif grid[r][c] == 1:
                    fresh += 1
        minutes = 0
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        while queue and fresh:
            # 固定当前分钟的传播源数量，本轮新感染的橘子下一分钟才能继续传播。
            size = len(queue)
            for _ in range(size):
                r, c = queue.popleft()
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                        # 入队时立刻标记感染，避免一颗橘子被多次计数。
                        grid[nr][nc] = 2
                        fresh -= 1
                        queue.append((nr, nc))
            minutes += 1
        # 仍有新鲜橘子说明有区域无法被感染，按题意返回 -1。
        return minutes if fresh == 0 else -1
'''.strip(),
 'code_notes':['队列初始可有多个源，也可能完全为空；两种情况都由同一循环处理。','每个 fresh 格子只入队一次，避免多个腐烂邻居重复减少 fresh。','题目保证网格非空，所以可以直接读取 grid[0]。'],
 'pitfalls':['只放一个初始腐烂橘子。','不冻结一层，让新感染格在同一分钟继续传播。','全新鲜且没有源时返回 0，正确答案应为 -1。'],
 'complexity':'时间 O(mn)，队列空间最坏 O(mn)。输入网格中的可达新鲜橘子被原地改成 2，空地保持 0。',
 'quiz':{'question':'[[2,0,1]] 最终需要几分钟？','answer':'返回 -1。中间空地不传播感染，右侧新鲜橘子永远无法从左源到达。'},
 'tests':{'method':'orangesRotting','cases':[{'args':[[[2,1,1],[1,1,0],[0,1,1]]],'expected':4},{'args':[[[2,1,1,1,2]]],'expected':2},{'args':[[[2,0,1]]],'expected':-1},{'args':[[[0,2]]],'expected':0},{'args':[[[1]]],'expected':-1},{'args':[[[0]]],'expected':0}]}
})

CHAPTER['problems'].append({
 'id':133,'slug':'clone-graph',
 'summary':'给定连通无向图中的一个节点，深拷贝整个可达图并返回对应的新节点。空图返回 None；每个副本节点和它的 neighbors 列表都应独立于原图。',
 'baseline':'只复制入口节点的 val 和 neighbors 列表，里面仍然是原邻居引用，属于浅拷贝。沿每条边都无条件创建新节点，又会在环中无限重复，并把共享邻居复制成多个不同对象。',
 'insight':'维护 copies：旧节点→唯一副本。首次发现一个旧节点时，先建立空副本并登记，再安排搜索；处理它的每条邻边时，把旧邻居翻译成已登记的副本后连接。这样环和多条路线最终指向同一副本。',
 'steps':['入口为空则 None；创建入口副本并放入 copies。','BFS 弹出旧节点 current，遍历其原 neighbors。','尚未登记的邻居先创建副本、登记并入队。','把 copies[neighbor] 追加到 copies[current].neighbors。','完成所有节点后返回 copies[node]。'],
 'invariant':'copies 为每个已发现旧节点恰好保存一个新对象，且对象值相同。处理旧节点的每条边时，副本中加入对应的新对象边；发现时先登记保证回边不会再创建对象。全部边处理完，原图与副本图存在保持值和邻接关系的一一映射。',
 'examples':[{'label':'环中的节点必须只有一个副本','input':'adjList=[[2,3],[1,3],[1,2]]','output':'同样的邻接关系，全部节点为新对象','frames':[
  {'title':'三个节点形成环','note':'撇号表示新对象；先创建 1′，此时还没有连接它的邻边。','diagram':'原图：  1\n       / \\\n      2 — 3\n副本： 1′（neighbors 暂为空）'},
  {'title':'处理 1，创建 2′ 与 3′','note':'登记副本后才入队。副本 1′ 的邻居为 [2′,3′]。','table':{'headers':['旧节点','唯一副本','已填邻居'],'rows':[[1,'1′','[2′,3′]'],[2,'2′','[]'],[3,'3′','[]']]}},
  {'title':'处理 2、3，复用已登记的副本','note':'2、3 的邻居都已登记，依次填完它们的邻接表，不再次创建。3′ 被 1′、2′ 共同引用，这是正确的共享结构。','diagram':'副本：  1′\n       / \\\n      2′— 3′\n所有边都只连接副本，不能指回原图'},
  {'title':'检查深拷贝隔离','note':'改变 1′ 的 val 或清空其 neighbors，不应影响原节点 1 的值与连接。','table':{'headers':['对象','身份是否相同','值/邻接是否对应'],'rows':[['1 与 1′','否','是'],['2 与 2′','否','是'],['3 与 3′','否','是']]}}
 ]}],
 'walkthrough':['visited 集合只能告诉你有没有见过邻居，不能告诉你应该连向哪个副本；因此这里需要映射。','无向边在邻接表中通常出现两次，例如 1→2 和 2→1；应分别复制各节点自己的邻居列表，不要无条件再补一条反向边导致重复。','题目保证节点值唯一，但用对象作键更直接表达身份，也能避免把“值相等”与“同一个节点”混淆。'],
 'code':'''
from collections import deque
from typing import Optional

class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        # 每个节点创建自己的邻居列表，不能把可变列表作为默认参数。
        self.neighbors = neighbors if neighbors is not None else []

class Solution:
    def cloneGraph(self, node: Optional[Node]) -> Optional[Node]:
        if node is None:
            return None
        # 旧节点身份映射到新节点，既用于深拷贝，也用于判定是否已经访问。
        copies = {node: Node(node.val)}
        queue = deque([node])
        while queue:
            current = queue.popleft()
            for neighbor in current.neighbors:
                # 先登记副本再入队，环和自连接不会造成无限遍历。
                if neighbor not in copies:
                    copies[neighbor] = Node(neighbor.val)
                    queue.append(neighbor)
                # 连边时只连接副本节点，不能把原图节点接到新图里。
                copies[current].neighbors.append(copies[neighbor])
        return copies[node]
'''.strip(),
 'code_notes':['neighbors 默认参数用 None，函数内部再创建 []，避免不同节点共享同一个默认列表。','代码只读原节点，通过 copies[current] 修改副本邻居。','每个节点首次发现时入队一次，但每条邻接关系仍要复制，不能只复制 BFS 树边。'],
 'pitfalls':['把原 neighbor 直接加入副本列表。','首次发现时没有立即登记，环与共享邻居会重复创建。','只记录搜索树边，丢掉图中的回边。'],
 'complexity':'时间 O(V+E)，E 按无向边数计时邻接项为 2E，数量级不变。映射与队列辅助空间 O(V)，输出节点和邻接列表占 O(V+E)。',
 'quiz':{'question':'原节点 1、2 都连接节点 3，副本里应该建两个 3′ 吗？','answer':'不应该。两条边必须指向同一个 3′，才能保持原图的共享邻居关系。'},
 'tests':{'adapter':'graph','method':'cloneGraph','cases':[{'args':[[[2,3],[1,3],[1,2]]],'expected':[[2,3],[1,3],[1,2]]},{'args':[[[2,4],[1,3],[2,4],[1,3]]],'expected':[[2,4],[1,3],[2,4],[1,3]]},{'args':[[[]]],'expected':[[]]},{'args':[[]],'expected':[]},{'args':[[[2],[1]]],'expected':[[2],[1]]}]}
})

CHAPTER['problems'].append({
 'id':207,'slug':'course-schedule',
 'summary':'课程编号为 0..numCourses-1，[a,b] 表示先完成 b 才能学 a。判断能否完成全部课程，本质是判断有向依赖中是否存在环。',
 'baseline':'尝试所有课程排列再检查前置条件，最多需要枚举 V! 种顺序。实际上，任何当前没有未完成前置的课程都可以先学，不必猜测整个排列。',
 'insight':'Kahn 拓扑算法维护剩余入度。把所有入度为零的课入队，完成一门就从依赖图中消去它的出边。若能完成 V 门则可行；如果还有课程却没有零入度入口，剩余部分必然含环。',
 'steps':['为每门课建立独立邻接列表，依赖 [a,b] 加边 b→a，并增加 indegree[a]。','把所有入度零的课程同时入队，finished=0。','弹出一门课，finished 加一，将每个后续课入度减一。','某门后续课入度降为零时入队。','返回 finished==numCourses。'],
 'invariant':'indegree[v] 恰好等于尚未完成的前置课数量，队列只包含已经满足全部前置的课。因此每次完成课程都是合法选择。若非空剩余图每个节点入度均大于零，不断沿前驱走最终会重复节点，形成环；反之有向无环图一定存在零入度节点，消除可持续到全部完成。',
 'examples':[{'label':'两个前置必须都完成','input':'numCourses=4，prerequisites=[[1,0],[2,0],[3,1],[3,2]]','output':'True','frames':[
  {'title':'依赖图是一处分叉再汇合','note':'3 需要 1 与 2，因此其入度为 2。','diagram':'    0\n   / \\\n  ↓   ↓\n  1   2\n   \\ /\n    ↓\n    3','metrics':[['入度','[0,1,1,2]'],['队列','[0]']]},
  {'title':'完成 0，解锁 1 与 2','note':'只减少 0 的两条出边；3 的两门直接前置还没完成。','table':{'headers':['完成课程','入度','新可学'],'rows':[[0,'[0,0,0,2]','1、2'],[1,'[0,0,0,1]','暂无'],[2,'[0,0,0,0]','3']]}},
  {'title':'最终完成全部 4 门','note':'3 出队后 finished=4，返回 True。','array':[0,1,2,3],'active':[0,1,2,3],'array_label':'一种完成顺序'}
 ]},{'label':'环使剩余课程互相等待','input':'numCourses=3，prerequisites=[[1,0],[0,1]]','output':'False','frames':[
  {'title':'孤立课程 2 可以完成','note':'0、1 构成环，入度都为 1；只有 2 入度为零。','diagram':'0 ⇄ 1       2（独立）','metrics':[['初始队列','[2]']]},
  {'title':'队列空，但没有完成全部课程','note':'finished=1<3，局部完成并不代表整张图无环。','table':{'headers':['课程','状态'],'rows':[[0,'等待1'],[1,'等待0'],[2,'已完成']]}}
 ]}],
 'walkthrough':['没有依赖的孤立课程也必须加入初始队列，不能只遍历 prerequisites 中出现的编号。','入度从 2 变成 1 时仍不可学，必须等全部前置完成，不能只因访问过一个前置就入队。','DFS 三色法也是另一条判环路线：遇到正在当前搜索路径中的节点才是回边；遇到已完成节点本身不意味着有环。这里用入度法同时为 210 的顺序输出做准备。'],
 'code':'''
from collections import deque

class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        # graph[p] 保存学完 p 后能解锁的课程，每门课有独立邻接列表。
        graph = [[] for _ in range(numCourses)]
        # 入度是该课程尚未完成的先修课数量。
        indegree = [0] * numCourses
        for course, prerequisite in prerequisites:
            # 依赖 [course,prerequisite] 对应边 prerequisite→course，方向不能反。
            graph[prerequisite].append(course)
            indegree[course] += 1
        # 先安排全部零入度课程；没有依赖的孤立课程也要包括在内。
        queue = deque(i for i in range(numCourses) if indegree[i] == 0)
        finished = 0
        while queue:
            course = queue.popleft()
            finished += 1
            for following in graph[course]:
                indegree[following] -= 1
                # 只在最后一个前置要求完成时，把课程加入队列。
                if indegree[following] == 0:
                    queue.append(following)
        # 处理不完说明剩余课程互相等待，依赖图存在环。
        return finished == numCourses
'''.strip(),
 'code_notes':['graph=[[] for _ in range(V)] 为每门课创建不同列表；[[]]*V 会共享列表。','输入 prerequisites 不被修改，变化发生在新建的 indegree 中。','队列出队次序可以有多种，本题只返回是否存在一种合法顺序。'],
 'pitfalls':['把依赖方向画反；虽然整体反向仍保持有无环，却会让 210 的课程顺序错误。','只检查是否完成过至少一门课。','把所有被访问过的节点都当成已经满足前置。'],
 'complexity':'时间 O(V+E)，空间 O(V+E)，包括邻接表、入度数组和队列。',
 'quiz':{'question':'没有任何依赖、共 5 门课时，初始队列应该放几门？','answer':'全部 5 门。每门课的未完成前置数量都是零，任意顺序都可完成。'},
 'tests':{'method':'canFinish','preserve_args':[1],'cases':[{'args':[4,[[1,0],[2,0],[3,1],[3,2]]],'expected':True},{'args':[3,[[1,0],[0,1]]],'expected':False},{'args':[5,[]],'expected':True},{'args':[1,[[0,0]]],'expected':False},{'args':[1,[]],'expected':True}]}
})

CHAPTER['problems'].append({
 'id':210,'slug':'course-schedule-ii',
 'summary':'在相同课程依赖下返回一个完整合法学习顺序；有多个答案时任意一个都可，存在环无法完成时返回 []。',
 'baseline':'207 只记录完成数量，丢掉了具体次序。无须重新设计搜索，只要把每次合法出队的课程保存到 order，就得到一个拓扑序。',
 'insight':'节点出队时全部前置都已经完成，所以将它追加到结果末尾总是合法。最终长度必须等于课程总数；有环时即使已生成部分合法前缀，也不能把这个不完整前缀作为答案。',
 'steps':['依照 b→a 建图并统计入度。','初始队列包含全部零入度课程。','出队时追加 course 到 order，再删除其出边贡献。','新变成零入度的课程加入队列。','order 长度为 V 时返回它，否则返回 []。'],
 'invariant':'order 是一个不违反任何已放入课程前置条件的合法前缀：每门课出队前，所有入边来源都已经更早进入 order。若最终包含每门课一次，则对每条边 b→a 都有 position[b]<position[a]，正好满足拓扑序。',
 'examples':[{'label':'同一依赖允许多个顺序','input':'numCourses=4，prerequisites=[[1,0],[2,0],[3,1],[3,2]]','output':'[0,1,2,3] 或 [0,2,1,3] 均合法','frames':[
  {'title':'0 必须最先，3 必须最后','note':'1 与 2 之间没有依赖，它们的相对顺序可交换。','diagram':'0 → 1 → 3\n \\→ 2 ↗'},
  {'title':'本实现的一次队列过程','note':'按输入邻接顺序先解锁 1，再解锁 2，得到 [0,1,2,3]。','table':{'headers':['出队','order','剩余队列'],'rows':[[0,'[0]','[1,2]'],[1,'[0,1]','[2]'],[2,'[0,1,2]','[3]'],[3,'[0,1,2,3]','[]']]}},
  {'title':'验证每条边的先后关系','note':'不应只与一种固定答案比较；完整覆盖课程并满足四条依赖即可。','table':{'headers':['依赖','顺序中的位置'],'rows':[['0→1','0<1'],['0→2','0<2'],['1→3','1<3'],['2→3','2<3']]}}
 ]}],
 'walkthrough':['若课程 0、1 构成环，独立课程 2 可以先进入 order=[2]，但最终必须返回 []，因为任务是完成全部课程。','FIFO 队列不保证字典序最小，只保证满足依赖。如果变体要求字典序最小，应把可选课程放入最小堆，并计入额外的对数开销。','依赖数组的行顺序可能改变两个同时可学课程的先后，只要所有边方向被尊重，答案仍然正确。'],
 'code':'''
from collections import deque

class Solution:
    def findOrder(self, numCourses: int, prerequisites: list[list[int]]) -> list[int]:
        # 从先修课向后续课连边，入度记录未完成的先修数量。
        graph = [[] for _ in range(numCourses)]
        indegree = [0] * numCourses
        for course, prerequisite in prerequisites:
            graph[prerequisite].append(course)
            indegree[course] += 1
        # 所有零入度节点都可作为拓扑序的下一门课。
        queue = deque(i for i in range(numCourses) if indegree[i] == 0)
        order = []
        while queue:
            course = queue.popleft()
            # 按实际解锁顺序保存课程；合法拓扑序不一定唯一。
            order.append(course)
            for following in graph[course]:
                # 学完一门课，就移除它对所有后续课的一条依赖。
                indegree[following] -= 1
                if indegree[following] == 0:
                    queue.append(following)
        # 只有收集到全部课程才返回序列，否则有环，返回空列表。
        return order if len(order) == numCourses else []
'''.strip(),
 'code_notes':['返回列表中的元素是课程编号，不是依赖边的下标。','每门课只有在入度变成零时入队一次，order 不会重复课程。','完整长度检查同时检测未被消除的环。'],
 'pitfalls':['反着建边，得到反向学习顺序。','有环时返回已经完成的部分课程。','误以为题目要求唯一答案或字典序最小。'],
 'complexity':'时间 O(V+E)，辅助空间 O(V+E)，输出顺序另占 O(V)。',
 'quiz':{'question':'怎样验证 [0,2,1,3] 合法，而不与代码输出 [0,1,2,3] 作相等比较？','answer':'先确认它包含所有课程且无重复，再建立编号到位置的映射，逐条检查每个前置 b 的位置小于课程 a。'},
 'tests':{'adapter':'topological','method':'findOrder','cases':[{'args':[4,[[1,0],[2,0],[3,1],[3,2]]],'expected':True},{'args':[3,[[1,0],[0,1]]],'expected':False},{'args':[3,[]],'expected':True},{'args':[1,[]],'expected':True},{'args':[2,[[0,1]]],'expected':True}]}
})
