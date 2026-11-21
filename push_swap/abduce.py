from itertools import combinations
import time

# =====================================================================
# 1. 기본 상태 우주 생성기 (독립 실행용)
# =====================================================================

def iter_neighbors_with_ops(s: tuple):
    L = len(s)
    z = s.index(0)
    len_b, len_a = z, L - 1 - z

    if len_b >= 1:
        yield "pa", s[:z - 1] + (0, s[z - 1]) + s[z + 1:]
    if len_a >= 1:
        yield "pb", s[:z] + (s[z + 1], 0) + s[z + 2:]
    if len_a >= 2:
        yield "sa", s[:z + 1] + (s[z + 2], s[z + 1]) + s[z + 3:]
        yield "ra", s[:z + 1] + s[z + 2:] + (s[z + 1],)
        yield "rra", s[:z + 1] + (s[-1],) + s[z + 1:-1]
    if len_b >= 2:
        yield "sb", s[:z - 2] + (s[z - 1], s[z - 2]) + s[z:]
        yield "rb", (s[z - 1],) + s[:z - 1] + s[z:]
        yield "rrb", s[1:z] + (s[0],) + s[z:]
    if len_a >= 2 and len_b >= 2:
        yield "ss", s[:z - 2] + (s[z - 1], s[z - 2], 0, s[z + 2], s[z + 1]) + s[z + 3:]
        yield "rr", (s[z - 1],) + s[:z - 1] + (0,) + s[z + 2:] + (s[z + 1],)
        yield "rrr", s[1:z] + (s[0], 0, s[-1]) + s[z + 1:-1]


def build_universe(n: int) -> dict[tuple, int]:
    goal = tuple(range(n + 1))
    dist = {goal: 0}
    frontier = [goal]
    d = 0
    while frontier:
        d += 1
        nxt_f = []
        for s in frontier:
            for _, nxt in iter_neighbors_with_ops(s):
                if nxt not in dist:
                    dist[nxt] = d
                    nxt_f.append(nxt)
        frontier = nxt_f
    return dist


# =====================================================================
# 2. 특이점(병목 상태) 해부 및 무임승차(Piggybacking) 현상 포착
# =====================================================================

def inspect_singularities(universes: dict):
    print("=" * 74)
    print("[1단계] 대칭 공간의 특이점(병목 상태) 정체 해부")
    print("=" * 74)
    print(f"  * G_7 전체 최악 거리(지름) 확인: {max(universes[7].values())}회 (2n-1 = 13 공식 성립 여부 확인!)")

    # G_3 -> G_4 에서 min(Delta) == 1 인 3개 상태
    s3_bottlenecks = []
    for u, d_u in universes[3].items():
        deltas = [universes[4][u[:j] + (4,) + u[j:]] - d_u for j in range(5)]
        if min(deltas) > 0:
            s3_bottlenecks.append((u, d_u, deltas))

    print(f"\n▶ G_3 -> G_4 공짜 확장(Delta=0)이 완전히 막힌 상태 ({len(s3_bottlenecks)}개):")
    for u, d_u, deltas in sorted(s3_bottlenecks):
        print(f"    상태 {u} (d_3={d_u}) -> 슬롯별 Delta={deltas}")

    # G_4 -> G_5 에서 min(Delta) == 2 인 4개 상태
    s4_bottlenecks = []
    for u, d_u in universes[4].items():
        deltas = [universes[5][u[:j] + (5,) + u[j:]] - d_u for j in range(6)]
        if min(deltas) >= 2:
            s4_bottlenecks.append((u, d_u, deltas))

    print(f"\n▶ G_4 -> G_5 최소 추가비용이 +2까지 치솟는 최악 병목 상태 ({len(s4_bottlenecks)}개):")
    for u, d_u, deltas in sorted(s4_bottlenecks):
        print(f"    상태 {u} (d_4={d_u}) -> 슬롯별 Delta={deltas}")


def analyze_piggybacking(n: int, dist_n: dict, dist_n1: dict):
    """
    Delta=0 인 경우를 역추적하여, 새 원소 (n+1)이
    1) 아예 안 건드려지고 가만히 있었는지 (Passive Invariance)
    2) rr, rrr, ss 등 동시 연산에 무임승차(Piggybacking)했는지 분류
    """
    new_max = n + 1
    passive_cnt = 0
    piggyback_cnt = 0
    piggyback_example = None

    for u, d_u in dist_n.items():
        for j in range(n + 2):
            u_j = u[:j] + (new_max,) + u[j:]
            if dist_n1[u_j] != d_u:
                continue

            # u_j가 맨 끝 슬롯(j == n+1)에서 시작해 끝까지 안 움직이는 경로가 있는지 확인
            # 만약 시작 슬롯 자체가 j != n+1 이면, 무조건 도중에 0비용으로 이동(무임승차/연동이동)한 것!
            if j == n + 1:
                passive_cnt += 1
            else:
                piggyback_cnt += 1
                if piggyback_example is None and u.index(0) >= 2:
                    # 실제 최단 경로 하나 추출
                    cur = u_j
                    ops_n1 = []
                    while dist_n1[cur] > 0:
                        for op, nxt in iter_neighbors_with_ops(cur):
                            if dist_n1[nxt] == dist_n1[cur] - 1:
                                ops_n1.append((op, nxt))
                                cur = nxt
                                break
                    piggyback_example = (u, d_u, j, u_j, ops_n1)

    print("\n" + "=" * 74)
    print(f"[2단계] G_{n} -> G_{n+1} 공짜 확장(Delta=0)의 두 가지 물리적 메커니즘")
    print("=" * 74)
    print(f"  - A 맨 바닥 고정형 (끝 슬롯 삽입 & 보존): {passive_cnt:,}건")
    print(f"  - 중간 슬롯 삽입 후 0비용 동반 이동형   : {piggyback_cnt:,}건")

    if piggyback_example:
        u, d_u, j, u_j, ops_n1 = piggyback_example
        print(f"\n  [무임승차 실증 사례] 기본 상태 u = {u} (d_{n} = {d_u})")
        print(f"    '{new_max}'을 슬롯 {j}에 삽입 -> u_j = {u_j} (여전히 d_{n+1} = {d_u}, 추가비용 0!)")
        for step_i, (op, nxt) in enumerate(ops_n1, 1):
            proj = tuple(x for x in nxt if x != new_max)
            print(f"      스텝 {step_i}: {op:>3s} -> {nxt}  (사영 pi -> {proj}, d_{n}={dist_n[proj]})")


# =====================================================================
# 3. CEGIS 루프: 가설 자동 생성 -> 더 큰 n에서 반례(Counterexample)로 기각
# 목표 현상: "언제 A 맨 바닥에 n+1을 꽂아도 비용이 0(백업 불필요)인가?"
# =====================================================================

def extract_relational_atoms(u: tuple, n: int) -> dict[str, bool]:
    """
    연산 시뮬레이션 없이, 순수하게 상태 u의 관계적/대칭적 성질만 추출하는 원시 어휘(DSL)
    """
    z = u.index(0)
    B = u[:z]        # B 바닥 ... B 탑
    A = u[z + 1:]    # A 탑 ... A 바닥

    a_sorted = all(A[i] < A[i + 1] for i in range(len(A) - 1))
    # B가 탑에서 바닥 방향으로 내림차순인가? (즉 pa만 연타하면 정렬되는가: B 바닥 -> 탑이 오름차순)
    b_ready_for_pa = all(B[i] < B[i + 1] for i in range(len(B) - 1))
    # B의 모든 원소가 A의 모든 원소보다 작은가? (A를 건드릴 필요 없이 B만 정리해 올리면 됨)
    b_all_smaller_than_a = (max(B) < min(A)) if (B and A) else True
    # A에서 인접 역전이 맨 위 두 개(sa 대상)에만 국한되어 있는가?
    a_tail_sorted = all(A[i] < A[i + 1] for i in range(1, len(A) - 1)) if len(A) >= 2 else True
    a_top2_only_inv = (len(A) >= 2 and A[0] > A[1] and a_tail_sorted and
                       (len(A) == 2 or A[0] < A[2]))

    atoms = {
        "B_empty": len(B) == 0,
        "A_empty": len(A) == 0,
        "A_sorted": a_sorted,
        "B_ready_pa": b_ready_for_pa,
        "B_lt_A": b_all_smaller_than_a,
        "A_max_at_bottom": (len(A) > 0 and A[-1] == n),
        "A_max_not_at_top": (len(A) == 0 or A[0] != n),
        "A_min_not_at_bottom": (len(A) <= 1 or A[-1] != 1),
        "A_top2_swap_ready": a_top2_only_inv,
    }
    # 부정(Negation) 어휘 자동 포함 (NOPI 스타일)
    neg_atoms = {f"not({k})": (not v) for k, v in atoms.items()}
    atoms.update(neg_atoms)
    return atoms


def run_cegis_abduction(universes: dict):
    print("\n" + "=" * 74)
    print("[3단계] CEGIS 가설 발명 & 반례 기각 실험")
    print("  질문: '어떤 조건 Phi(u)가 보장되면 A 바닥에 n+1을 꽂아도 추가 연산이 0(충분조건)인가?'")
    print("=" * 74)

    # 각 n별 (상태, 원시술어사전, 실제 바닥슬롯 Delta==0 여부) 데이터셋 준비
    datasets = {}
    for n in range(2, 7):
        data_n = []
        for u, d_u in universes[n].items():
            u_bottom = u + (n + 1,)
            is_free = (universes[n + 1][u_bottom] == d_u)
            data_n.append((u, extract_relational_atoms(u, n), is_free))
        datasets[n] = data_n

    atom_names = list(datasets[3][0][1].keys())

    # 길이 1~3인 논리곱(Conjunction) 가설 후보군 생성 (Phi(u) => Delta_bottom == 0)
    candidates = []
    for r in (1, 2, 3):
        for comb in combinations(atom_names, r):
            # 모순 쌍(p 와 not(p) 동시 포함) 제거
            if any(f"not({x})" in comb for x in comb):
                continue
            candidates.append(comb)

    # Step A: n=3 에서 정밀도 100% (반례 0건) 이면서 실제로 참인 사례를 3개 이상 설명하는 가설 수집
    n3_theories = []
    for comb in candidates:
        pos_hits = 0
        falsified = False
        for u, atoms, is_free in datasets[3]:
            if all(atoms[k] for k in comb):
                if not is_free:
                    falsified = True
                    break
                pos_hits += 1
        if not falsified and pos_hits >= 3:
            n3_theories.append(comb)

    print(f"  1) G_3 데이터만 보고 발명된 '100% 무결점' 초기 가설 수: {len(n3_theories)}개")

    # Step B: n=4, 5, 6 으로 올라가며 검증기(Verifier)로 가짜 외삽 가설들을 반례로 파괴!
    surviving = n3_theories
    killed_examples = []

    for test_n in (4, 5, 6):
        next_surviving = []
        killed_count = 0
        for comb in surviving:
            counterexample = None
            for u, atoms, is_free in datasets[test_n]:
                if all(atoms[k] for k in comb) and not is_free:
                    counterexample = u
                    break
            if counterexample is None:
                next_surviving.append(comb)
            else:
                killed_count += 1
                if len(killed_examples) < 4:
                    killed_examples.append((comb, test_n, counterexample))
        surviving = next_surviving
        print(f"  2) G_{test_n} 확장 검증 -> 가짜 가설 {killed_count}개 반례로 기각됨! (생존: {len(surviving)}개)")

    print("\n  [외삽의 함정 실증] G_3에서는 완벽했지만 큰 n에서 박살 난 가짜 가설들과 반례:")
    for comb, broken_n, ce_u in killed_examples:
        formula = " AND ".join(comb)
        d_base = universes[broken_n][ce_u]
        d_ext = universes[broken_n + 1][ce_u + (broken_n + 1,)]
        print(f"    ✘ 기각된 가설: IF [{formula}] THEN Delta_bottom = 0")
        print(f"      -> G_{broken_n} 반례 발견: u = {ce_u} (d_{broken_n}={d_base} 이지만 바닥에 {broken_n+1} 추가 시 d={d_ext}, Delta=+{d_ext-d_base})")

    # Step C: 논리적으로 중복되지 않는 가장 간결한(Minimal) 생존 불변 법칙만 추리기
    minimal_laws = []
    surviving_sorted = sorted(surviving, key=len)
    for comb in surviving_sorted:
        s_comb = set(comb)
        if not any(set(prev).issubset(s_comb) for prev in minimal_laws):
            # G_6에서의 실제 커버리지 계산
            hits_g6 = sum(1 for _, atoms, is_free in datasets[6] if all(atoms[k] for k in comb) and is_free)
            if hits_g6 > 0:
                minimal_laws.append(comb)

    print(f"\n  [최종 생존 보편 법칙] G_2 ~ G_6 전수 검증 통과한 최소 불변 설명 ({len(minimal_laws)}개):")
    for comb in minimal_laws[:8]:
        formula = " AND ".join(comb)
        hits_g6 = sum(1 for _, atoms, _ in datasets[6] if all(atoms[k] for k in comb))
        print(f"    ✔ 보편 법칙: IF [{formula}] THEN 백업/추가연산 불필요 (G_6 상태 {hits_g6}개 설명)")


if __name__ == "__main__":
    t0 = time.perf_counter()
    universes = {n: build_universe(n) for n in range(1, 8)}

    inspect_singularities(universes)
    analyze_piggybacking(4, universes[4], universes[5])
    run_cegis_abduction(universes)

    print(f"\n총 실행 시간: {time.perf_counter() - t0:.2f}초")