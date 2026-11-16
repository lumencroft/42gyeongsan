from collections import deque, defaultdict
from graphviz import Graph

# 앞쪽에 있을수록 대표 연산으로 우선 선택됨
OPS = ["sa", "sb", "ss", "pa", "pb", "ra", "rb", "rr", "rra", "rrb", "rrr"]
PRIORITY = {op: i for i, op in enumerate(OPS)}

def step(a, b, op):
    if op == "sa":
        return ((a[1], a[0]) + a[2:], b) if len(a) >= 2 else (a, b)
    if op == "sb":
        return (a, (b[1], b[0]) + b[2:]) if len(b) >= 2 else (a, b)
    if op == "ss":
        a, _ = step(a, b, "sa")
        _, b = step(a, b, "sb")
        return (a, b)
    if op == "pa":
        return ((b[0],) + a, b[1:]) if b else (a, b)
    if op == "pb":
        return (a[1:], (a[0],) + b) if a else (a, b)
    if op == "ra":
        return (a[1:] + (a[0],), b) if len(a) >= 2 else (a, b)
    if op == "rb":
        return (a, b[1:] + (b[0],)) if len(b) >= 2 else (a, b)
    if op == "rr":
        a, _ = step(a, b, "ra")
        _, b = step(a, b, "rb")
        return (a, b)
    if op == "rra":
        return ((a[-1],) + a[:-1], b) if len(a) >= 2 else (a, b)
    if op == "rrb":
        return (a, (b[-1],) + b[:-1]) if len(b) >= 2 else (a, b)
    if op == "rrr":
        a, _ = step(a, b, "rra")
        _, b = step(a, b, "rrb")
        return (a, b)

def fmt_state(a, b):
    a_str = " ".join(map(str, a)) if a else "∅"
    b_str = " ".join(map(str, b)) if b else "∅"
    return f"A:[{a_str}]\nB:[{b_str}]"

def render_clean_graph(n, filename="push_swap_clean"):
    goal = (tuple(range(1, n + 1)), ())
    dist = {goal: 0}
    layers = defaultdict(list)
    layers[0].append(goal)
    q = deque([goal])

    while q:
        curr = q.popleft()
        for op in OPS:
            nxt = step(*curr, op)
            if nxt not in dist:
                dist[nxt] = dist[curr] + 1
                layers[dist[nxt]].append(nxt)
                q.append(nxt)

    # 두 상태 쌍(pair)당 대표 연산 1개만 선택
    edges = {}
    for u in dist:
        for op in OPS:
            v = step(*u, op)
            if u == v:
                continue
            pair = tuple(sorted([u, v]))
            # 정답(위쪽)으로 향하는 방향(dist[u] > dist[v])의 연산을 최우선으로 채택
            is_upward = dist[u] > dist[v]
            score = (0 if is_upward else 1, PRIORITY[op])

            if pair not in edges or score < edges[pair][0]:
                edges[pair] = (score, op)

    g = Graph(format="svg")
    g.attr(rankdir="TB", splines="polyline", nodesep="0.45", ranksep="0.9")
    g.attr("node", shape="box", style="rounded,filled", fontname="Consolas", fontsize="10")
    g.attr("edge", fontname="Consolas", fontsize="9", color="#555555")

    for d, nodes in sorted(layers.items()):
        with g.subgraph() as sub:
            sub.attr(rank="same")
            for st in nodes:
                if st == goal:
                    fill = "#d4edda"   # 정답 상태
                elif len(st[1]) == 0:
                    fill = "#fff3cd"   # B가 비어 있는 초기 상태들
                else:
                    fill = "#f8f9fa"
                sub.node(str(st), label=fmt_state(*st), fillcolor=fill)

    for (u, v), (_, label) in edges.items():
        g.edge(str(u), str(v), label=label)

    output_path = g.render(filename, view=True)
    print(f"생성 완료: {output_path} (상태 {len(dist)}개, 간선 {len(edges)}개)")

render_clean_graph(3, "push_swap_n3_clean")