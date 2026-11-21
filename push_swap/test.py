from collections import Counter
import time

# =====================================================================
# 1. 상태 표현 및 11개 대칭 연산 정의
# 표현법: (b_k, ..., b_1, 0, a_1, ..., a_m)
#   - 0 바로 왼쪽(z-1)이 B의 Top, 맨 왼쪽(0)이 B의 Bottom
#   - 0 바로 오른쪽(z+1)이 A의 Top, 맨 오른쪽(L-1)이 A의 Bottom
#   - 정렬 완료(목표) 상태: (0, 1, 2, ..., n)
# =====================================================================

def iter_neighbors_with_ops(s: tuple):
    """현재 상태에서 1번의 연산으로 갈 수 있는 (연산이름, 다음상태) 생성"""
    L = len(s)
    z = s.index(0)
    len_b = z
    len_a = L - 1 - z

    # 1) Push 연산: 칸막이 0만 좌우로 한 칸 이동
    if len_b >= 1:  # pa: B Top -> A Top
        yield "pa", s[:z - 1] + (0, s[z - 1]) + s[z + 1:]
    if len_a >= 1:  # pb: A Top -> B Top
        yield "pb", s[:z] + (s[z + 1], 0) + s[z + 2:]

    # 2) Swap 연산: 칸막이 양옆 두 원소 교환
    if len_a >= 2:  # sa
        yield "sa", s[:z + 1] + (s[z + 2], s[z + 1]) + s[z + 3:]
    if len_b >= 2:  # sb
        yield "sb", s[:z - 2] + (s[z - 1], s[z - 2]) + s[z:]
    if len_a >= 2 and len_b >= 2:  # ss
        yield "ss", s[:z - 2] + (s[z - 1], s[z - 2], 0, s[z + 2], s[z + 1]) + s[z + 3:]

    # 3) Rotate 연산 (원심 회전: Top -> Bottom)
    if len_a >= 2:  # ra
        yield "ra", s[:z + 1] + s[z + 2:] + (s[z + 1],)
    if len_b >= 2:  # rb
        yield "rb", (s[z - 1],) + s[:z - 1] + s[z:]
    if len_a >= 2 and len_b >= 2:  # rr
        yield "rr", (s[z - 1],) + s[:z - 1] + (0,) + s[z + 2:] + (s[z + 1],)

    # 4) Reverse Rotate 연산 (구심 회전: Bottom -> Top)
    if len_a >= 2:  # rra
        yield "rra", s[:z + 1] + (s[-1],) + s[z + 1:-1]
    if len_b >= 2:  # rrb
        yield "rrb", s[1:z] + (s[0],) + s[z:]
    if len_a >= 2 and len_b >= 2:  # rrr
        yield "rrr", s[1:z] + (s[0], 0, s[-1]) + s[z + 1:-1]


def iter_neighbors_fast(s: tuple, L: int):
    """역방향 BFS 고속 탐색용 (연산 문자열 생략)"""
    z = s.index(0)
    len_b = z
    len_a = L - 1 - z

    if len_b >= 1:
        yield s[:z - 1] + (0, s[z - 1]) + s[z + 1:]
    if len_a >= 1:
        yield s[:z] + (s[z + 1], 0) + s[z + 2:]
    if len_a >= 2:
        yield s[:z + 1] + (s[z + 2], s[z + 1]) + s[z + 3:]
        yield s[:z + 1] + s[z + 2:] + (s[z + 1],)
        yield s[:z + 1] + (s[-1],) + s[z + 1:-1]
    if len_b >= 2:
        yield s[:z - 2] + (s[z - 1], s[z - 2]) + s[z:]
        yield (s[z - 1],) + s[:z - 1] + s[z:]
        yield s[1:z] + (s[0],) + s[z:]
    if len_a >= 2 and len_b >= 2:
        yield s[:z - 2] + (s[z - 1], s[z - 2], 0, s[z + 2], s[z + 1]) + s[z + 3:]
        yield (s[z - 1],) + s[:z - 1] + (0,) + s[z + 2:] + (s[z + 1],)
        yield s[1:z] + (s[0], 0, s[-1]) + s[z + 1:-1]


# =====================================================================
# 2. 전체 상태 우주 G_n 생성기 (목표 상태에서 단 1회 역방향 BFS)
# =====================================================================

def build_universe(n: int) -> dict[tuple, int]:
    """(n+1)! 개의 모든 상태에 대해 정확한 최단 정렬 거리를 계산"""
    goal = tuple(range(n + 1))  # (0, 1, 2, ..., n)
    L = n + 1
    dist = {goal: 0}
    frontier = [goal]
    d = 0

    # 모든 연산의 역연산이 연산 집합 내에 존재하므로 무방향 대칭 그래프임
    while frontier:
        d += 1
        next_frontier = []
        for s in frontier:
            for nxt in iter_neighbors_fast(s, L):
                if nxt not in dist:
                    dist[nxt] = d
                    next_frontier.append(nxt)
        frontier = next_frontier

    return dist


def shortest_path(s: tuple, dist: dict[tuple, int]) -> list[tuple[str, tuple]]:
    """특정 상태 s에서 정렬 완료까지의 실제 최단 경로 1개 추적"""
    path = []
    cur = s
    while dist[cur] > 0:
        target_d = dist[cur] - 1
        for op, nxt in iter_neighbors_with_ops(cur):
            if dist[nxt] == target_d:
                path.append((op, nxt))
                cur = nxt
                break
    return path


# =====================================================================
# 3. n -> n+1 섬유(Fiber) 확장 및 Delta 벡터 분석기
# =====================================================================

def analyze_fiber_transition(n: int, dist_n: dict, dist_n1: dict):
    """
    G_n의 모든 상태 u에 새 최댓값 (n+1)을 n+2개 빈틈에 꽂아 넣으며
    Delta_j(u) = d_{n+1}(u_j) - d_n(u) 의 대칭성과 불변 조건을 분석
    """
    new_max = n + 1
    num_slots = n + 2

    min_delta_counter = Counter()
    free_in_B = 0          # B스택 쪽에 넣었는데 Delta=0이 나온 횟수
    free_in_A = 0          # A스택 쪽에 넣었는데 Delta=0이 나온 횟수
    free_at_bottom_A = 0   # A스택 맨 바닥(맨 끝 슬롯)에서 Delta=0인 횟수
    total_A_slots = 0

    for u, d_u in dist_n.items():
        z = u.index(0)
        deltas = []

        for j in range(num_slots):
            u_j = u[:j] + (new_max,) + u[j:]
            delta = dist_n1[u_j] - d_u

            # 핵심 수학적 정리 검증: 가정이 절대 흐트러지지 않는가? (Delta >= 0)
            assert delta >= 0, f"단조성 붕괴 발견! {u} -> {u_j}: delta={delta}"
            deltas.append(delta)

            # 칸막이 0 기준 왼쪽(j <= z)은 B스택 삽입, 오른쪽(j > z)은 A스택 삽입
            if j <= z:
                if delta == 0:
                    free_in_B += 1
            else:
                total_A_slots += 1
                if delta == 0:
                    free_in_A += 1
                    if j == num_slots - 1:
                        free_at_bottom_A += 1

        min_delta_counter[min(deltas)] += 1

    total_states = len(dist_n)
    stack_a_only_max = max(d for s, d in dist_n.items() if s[0] == 0)

    print(f"\n[G_{n} -> G_{n+1} 네트워크 확장 분석] (상태 수: {total_states:,}개 -> {len(dist_n1):,}개)")
    print(f"  - G_{n} 전체 최악 거리: {max(dist_n.values())}회 (전통적 A스택 시작 기준 최악: {stack_a_only_max}회)")
    print(f"  - 단조성 검증 (모든 슬롯 Delta >= 0): 100% 통과 (예외 0건)")
    print(f"  - 상태별 최소 추가비용 min_j(Delta) 분포: {dict(sorted(min_delta_counter.items()))}")
    zero_ratio = min_delta_counter[0] / total_states * 100
    print(f"    => 전체 상태의 {zero_ratio:.1f}%는 적어도 한 자리에 '{new_max}'을 공짜(Delta=0)로 끼워 넣을 수 있음!")
    print(f"  - B스택 영역 삽입 시 공짜(Delta=0) 발생 건수: {free_in_B}건 (이론상 무조건 0건이어야 함)")
    print(f"  - A스택 영역 삽입 시 공짜(Delta=0) 비율: {free_in_A:,}/{total_A_slots:,} ({free_in_A/total_A_slots*100:.1f}%)"
          f" | 그중 A 맨 바닥 슬롯: {free_at_bottom_A:,}건")


def show_contrastive_example(dist_3: dict, dist_4: dict):
    """
    AI가 '설명(불변량)'을 발명하게 만들 대조군(Contrastive Pair) 예시 출력
    """
    print("\n" + "=" * 72)
    print("[핵심 관찰] 왜 어떤 상태는 공짜 확장이 되고, 어떤 상태는 안 될까? (n=3 -> 4)")
    print("=" * 72)

    # 둘 다 G_3에서는 단 1번의 회전으로 정렬되는 대칭적인 상태 쌍
    s1 = (0, 2, 3, 1)  # rra 1번이면 정렬됨
    s2 = (0, 3, 1, 2)  # ra  1번이면 정렬됨

    for label, u in [("케이스 1 (구심 회전 rra 해법)", s1), ("케이스 2 (원심 회전 ra 해법)", s2)]:
        d_u = dist_3[u]
        deltas = []
        children = []
        for j in range(5):
            u_j = u[:j] + (4,) + u[j:]
            deltas.append(dist_4[u_j] - d_u)
            children.append(u_j)

        print(f"\n▶ {label}: u = {u} (기본 거리 d_3 = {d_u})")
        print(f"  '4' 삽입 위치별 Delta 벡터: {deltas}")
        for j, (u_j, dt) in enumerate(zip(children, deltas)):
            tag = " <-- [공짜 확장! Delta=0]" if dt == 0 else ""
            ops = [op for op, _ in shortest_path(u_j, dist_4)]
            print(f"    슬롯 {j}: {u_j} -> d_4 = {dist_4[u_j]} (Delta = +{dt}) | 최단해: {ops}{tag}")


if __name__ == "__main__":
    MAX_N = 7  # 순수 파이썬으로 7까지 약 0.5초 소요 (8로 올리면 약 5초 소요)
    t0 = time.perf_counter()

    universes = {}
    print(f"1단계: G_1 ~ G_{MAX_N} 전체 대칭 상태 우주 생성 중...")
    for n in range(1, MAX_N + 1):
        t_start = time.perf_counter()
        universes[n] = build_universe(n)
        elapsed = time.perf_counter() - t_start
        print(f"  - G_{n}: 상태 {len(universes[n]):>7,}개 완료 ({elapsed:.3f}초)")

    print("\n2단계: n -> n+1 섬유(Fiber) 사영 및 Delta 벡터 전수 검증...")
    for n in range(2, MAX_N):
        analyze_fiber_transition(n, universes[n], universes[n + 1])

    show_contrastive_example(universes[3], universes[4])
    print(f"\n총 실행 시간: {time.perf_counter() - t0:.2f}초")