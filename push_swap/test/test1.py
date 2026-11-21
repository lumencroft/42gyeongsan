# push_swap_rule_discovery.py
# Pure Python (No Torch / No external deps) - 42 Cluster CPU Ready
import time
import random
from bisect import bisect_left
from itertools import combinations
from collections import deque

MOVES = ('sa', 'sb', 'ss', 'pa', 'pb', 'ra', 'rb', 'rr', 'rra', 'rrb', 'rrr')
INV_MOVES = {
    'sa': 'sa', 'sb': 'sb', 'ss': 'ss',
    'pa': 'pb', 'pb': 'pa',
    'ra': 'rra', 'rb': 'rrb', 'rr': 'rrr',
    'rra': 'ra', 'rrb': 'rb', 'rrr': 'rr',
}


def apply_move(state, move):
    """
    상태 표현: (b_bot, ..., b_top, 0, a_top, ..., a_bot)
    z = state.index(0), B = state[:z], A = state[z+1:]
    """
    n = len(state) - 1
    z = state.index(0)
    B = list(state[:z])
    A = list(state[z + 1:])

    if move == 'sa':
        if len(A) < 2:
            return None
        A[0], A[1] = A[1], A[0]
    elif move == 'sb':
        if len(B) < 2:
            return None
        B[-1], B[-2] = B[-2], B[-1]
    elif move == 'ss':
        if len(A) < 2 and len(B) < 2:
            return None
        if len(A) >= 2:
            A[0], A[1] = A[1], A[0]
        if len(B) >= 2:
            B[-1], B[-2] = B[-2], B[-1]
    elif move == 'pa':
        if not B:
            return None
        A.insert(0, B.pop())
    elif move == 'pb':
        if not A:
            return None
        B.append(A.pop(0))
    elif move == 'ra':
        if len(A) < 2:
            return None
        A = A[1:] + [A[0]]
    elif move == 'rb':
        if len(B) < 2:
            return None
        B = [B[-1]] + B[:-1]
    elif move == 'rr':
        if len(A) < 2 and len(B) < 2:
            return None
        if len(A) >= 2:
            A = A[1:] + [A[0]]
        if len(B) >= 2:
            B = [B[-1]] + B[:-1]
    elif move == 'rra':
        if len(A) < 2:
            return None
        A = [A[-1]] + A[:-1]
    elif move == 'rrb':
        if len(B) < 2:
            return None
        B = B[1:] + [B[0]]
    elif move == 'rrr':
        if len(A) < 2 and len(B) < 2:
            return None
        if len(A) >= 2:
            A = [A[-1]] + A[:-1]
        if len(B) >= 2:
            B = B[1:] + [B[0]]

    return tuple(B + [0] + A)


def build_exact_bfs(n):
    """G_n 전체 상태 우주에 대한 정확한 역방향 BFS 거리 테이블 구축"""
    goal = tuple([0] + list(range(1, n + 1)))
    dist = {goal: 0}
    q = deque([goal])
    while q:
        cur = q.popleft()
        d = dist[cur] + 1
        for m in MOVES:
            prev = apply_move(cur, INV_MOVES[m])
            if prev is not None and prev not in dist:
                dist[prev] = d
                q.append(prev)
    return dist


# ==============================================================================
# N-불변 순수 구조 원시 어휘 (Size-Invariant Structural Primitives)
# ==============================================================================
PRIMITIVE_NAMES = [
    "cnt_B",          # 0: 스택 B에 머무는 원소 수 (칸막이 반대편 점유량)
    "non_lis_A",      # 1: A의 최장 원형 증가 부분수열(Cyclic LIS)에서 이탈한 원소 수
    "a_breaks",       # 2: A 내부의 원형 순서 깨짐(하강 경계) 초과 개수
    "b_breaks",       # 3: B 내부의 역순 정렬 깨짐 개수 (B는 Bottom->Top 오름차순이 이상적)
    "minA_shift",     # 4: A의 최솟값을 A-Top으로 가져오기 위한 최소 회전 수
    "escape_depth",   # 5: A의 LIS 이탈 원소 중 경계(Top/Bottom)에 가장 가까운 탈출 깊이
    "b_align_shift",  # 6: B의 Top 원소가 A의 제자리에 들어가기 위해 필요한 A 회전 거리
    "topA_swap",      # 7: A의 Top 두 원소가 즉시 교환(sa) 이득이 있는지 여부 (0/1)
    "topB_swap",      # 8: B의 Top 두 원소가 즉시 교환(sb) 이득이 있는지 여부 (0/1)
    "b_straddle",     # 9: B의 값 범위가 A의 내부 값들과 얽혀 있는지 여부 (0/1)
]


def _cyclic_lis_info(A):
    """A의 최장 원형 증가 부분수열 길이와 이탈 원소들의 원래 인덱스를 O(m log m)으로 계산"""
    m = len(A)
    if m <= 1:
        return m, []

    # 시작 후보: 원형 하강 지점 직후 인덱스들 (없으면 0)
    starts = [i for i in range(m) if A[(i - 1) % m] > A[i]]
    if not starts:
        starts = [0]

    best_len = 0
    best_kept_orig = set()

    for s in starts:
        tails = []
        tail_idx = []
        parent = [-1] * m
        for offset in range(m):
            orig_i = (s + offset) % m
            val = A[orig_i]
            pos = bisect_left(tails, val)
            if pos == len(tails):
                tails.append(val)
                tail_idx.append(orig_i)
            else:
                tails[pos] = val
                tail_idx[pos] = orig_i
            if pos > 0:
                parent[orig_i] = tail_idx[pos - 1]

        if len(tails) > best_len:
            best_len = len(tails)
            kept = set()
            curr = tail_idx[-1]
            while curr != -1:
                kept.add(curr)
                curr = parent[curr]
            best_kept_orig = kept

    non_lis_indices = [i for i in range(m) if i not in best_kept_orig]
    return best_len, non_lis_indices


def extract_primitives(state):
    """임의의 N에 대해 동일한 스케일(O(N))로 작동하는 10개 구조 특징 추출"""
    z = state.index(0)
    B = state[:z]
    A = state[z + 1:]
    cnt_B = len(B)
    m = len(A)

    # 1. non_lis_A & 5. escape_depth
    lis_len, non_lis_idx = _cyclic_lis_info(A)
    non_lis_A = m - lis_len
    if non_lis_idx:
        escape_depth = min(min(i + 1, m - i) for i in non_lis_idx)
    else:
        escape_depth = 0

    # 2. a_breaks
    if m <= 1:
        a_breaks = 0
    else:
        desc = sum(1 for i in range(m) if A[i] > A[(i + 1) % m])
        a_breaks = max(0, desc - 1)

    # 3. b_breaks (B는 Bottom->Top으로 커져야 pa 시 A에 오름차순으로 쌓임)
    if cnt_B <= 1:
        b_breaks = 0
    else:
        b_breaks = sum(1 for i in range(cnt_B - 1) if B[i] > B[i + 1])

    # 4. minA_shift
    if m <= 1:
        minA_shift = 0
    else:
        min_pos = min(range(m), key=lambda i: A[i])
        minA_shift = min(min_pos, m - min_pos)

    # 6. b_align_shift: B의 Top(B[-1])이 A에서 들어갈 자리까지의 최소 회전 거리
    if cnt_B == 0 or m <= 1:
        b_align_shift = 0
    else:
        top_b = B[-1]
        # A에서 top_b보다 큰 원소 중 가장 작은 값(없으면 min(A))이 A[0]에 와야 함
        greater = [i for i, v in enumerate(A) if v > top_b]
        target_pos = min(greater, key=lambda i: A[i]) if greater else min(range(m), key=lambda i: A[i])
        b_align_shift = min(target_pos, m - target_pos)

    # 7. topA_swap & 8. topB_swap
    topA_swap = 1 if (m >= 2 and A[0] > A[1] and not (A[0] == max(A) and A[1] == min(A))) else 0
    topB_swap = 1 if (cnt_B >= 2 and B[-1] < B[-2]) else 0

    # 9. b_straddle
    if cnt_B > 0 and m > 0 and min(B) < max(A) and max(B) > min(A):
        b_straddle = 1
    else:
        b_straddle = 0

    return (
        float(cnt_B),
        float(non_lis_A),
        float(a_breaks),
        float(b_breaks),
        float(minA_shift),
        float(escape_depth),
        float(b_align_shift),
        float(topA_swap),
        float(topB_swap),
        float(b_straddle),
    )


# ==============================================================================
# 2단계: MDL 복잡도 제한 가설 발명기 (Symbolic Rule Discovery)
# ==============================================================================
def _solve_linear_system(M, y):
    """가우스 소거법으로 작은 KxK 선형 연립방정식 해 계산"""
    k = len(y)
    aug = [row[:] + [y[i]] for i, row in enumerate(M)]
    for i in range(k):
        pivot = max(range(i, k), key=lambda r: abs(aug[r][i]))
        aug[i], aug[pivot] = aug[pivot], aug[i]
        if abs(aug[i][i]) < 1e-9:
            return [0.0] * k
        div = aug[i][i]
        for j in range(i, k + 1):
            aug[i][j] /= div
        for r in range(k):
            if r != i:
                factor = aug[r][i]
                for j in range(i, k + 1):
                    aug[r][j] -= factor * aug[i][j]
    return [aug[i][k] for i in range(k)]


def fit_ols_subset(X_rows, y_vals, idxs):
    k = len(idxs)
    M = [[0.0] * k for _ in range(k)]
    rhs = [0.0] * k
    for x, y in zip(X_rows, y_vals):
        for a in range(k):
            xa = x[idxs[a]]
            rhs[a] += xa * y
            for b in range(a, k):
                M[a][b] += xa * x[idxs[b]]
    for a in range(k):
        M[a][a] += 1e-4  # 약한 L2 안정화
        for b in range(a):
            M[a][b] = M[b][a]
    return _solve_linear_system(M, rhs)


def evaluate_policy_regret(states, dist_map, feat_cache, idxs, weights, max_samples=400):
    """
    발명된 수식 E_hat(S)만을 따라 1-step 그리디 하강했을 때
    실제 최적 거리 d*(S) 대비 손해 본 평균 연산 수(Regret) 측정
    """
    sample_states = states if len(states) <= max_samples else states[:max_samples]
    total_regret = 0.0
    unsolved = 0

    for s in sample_states:
        opt_d = dist_map[s]
        if opt_d == 0:
            continue
        cur = s
        visited = {cur}
        steps = 0
        limit = opt_d * 3 + 6
        while dist_map[cur] > 0 and steps < limit:
            best_next = None
            best_score = float('inf')
            for m in MOVES:
                nxt = apply_move(cur, m)
                if nxt is None or nxt in visited:
                    continue
                if dist_map[nxt] == 0:
                    best_next = nxt
                    break
                f = feat_cache[nxt]
                score = sum(w * f[idx] for idx, w in zip(idxs, weights))
                if score < best_score:
                    best_score = score
                    best_next = nxt
            if best_next is None:
                unsolved += 1
                steps = limit
                break
            cur = best_next
            visited.add(cur)
            steps += 1
        if dist_map[cur] != 0:
            unsolved += 1
            total_regret += 15.0
        else:
            total_regret += max(0, steps - opt_d)

    return total_regret / len(sample_states), unsolved


def discover_rules_pareto(train_states, train_dist, max_k=4):
    """항 개수 K=1..max_k별로 최적의 N-불변 에너지 함수 E_hat(S)를 자동 합성"""
    feat_cache = {s: extract_primitives(s) for s in train_states}
    X_rows = [feat_cache[s] for s in train_states]
    y_vals = [float(train_dist[s]) for s in train_states]

    # 이웃 전이(Transition) 쌍 캐시: 다음 상태들의 특징을 미리 계산해 탐색 고속화
    for s in train_states:
        for m in MOVES:
            nxt = apply_move(s, m)
            if nxt is not None and nxt not in feat_cache:
                feat_cache[nxt] = extract_primitives(nxt)

    pareto_models = {}
    num_p = len(PRIMITIVE_NAMES)

    for k in range(1, max_k + 1):
        candidates = []
        for idxs in combinations(range(num_p), k):
            w = fit_ols_subset(X_rows, y_vals, idxs)
            # 가중치를 소수점 첫째 자리로 깔끔하게 양자화 (과적합 방지 & 물리 법칙화)
            w_clean = [round(val, 1) for val in w]
            if any(val <= 0.0 for val in w_clean):
                continue
            mae = sum(
                abs(sum(wt * x[i] for i, wt in zip(idxs, w_clean)) - y)
                for x, y in zip(X_rows, y_vals)
            ) / len(y_vals)
            candidates.append((mae, idxs, w_clean))

        # MAE 상위 12개 후보에 대해 실제 행동 결정 손실(Policy Regret)을 정밀 평가 및 미세조정
        candidates.sort(key=lambda item: item[0])
        best_model = None
        best_obj = float('inf')

        for mae, idxs, w_init in candidates[:12]:
            w_cur = list(w_init)
            regret, unsolved = evaluate_policy_regret(train_states, train_dist, feat_cache, idxs, w_cur, max_samples=350)
            # 1라운드 좌표 미세조정 (그리디 행동 순위를 더 정확히 맞추도록 가중치 조율)
            for dim in range(k):
                for delta in (-0.4, -0.2, 0.2, 0.4):
                    w_try = list(w_cur)
                    w_try[dim] = round(w_try[dim] + delta, 1)
                    if w_try[dim] <= 0.0:
                        continue
                    r_try, u_try = evaluate_policy_regret(train_states, train_dist, feat_cache, idxs, w_try, max_samples=350)
                    if (u_try, r_try) < (unsolved, regret):
                        w_cur, regret, unsolved = w_try, r_try, u_try

            final_mae = sum(
                abs(sum(wt * x[i] for i, wt in zip(idxs, w_cur)) - y)
                for x, y in zip(X_rows, y_vals)
            ) / len(y_vals)
            obj = regret + 0.15 * final_mae + 5.0 * unsolved
            if obj < best_obj:
                best_obj = obj
                best_model = (idxs, w_cur, final_mae, regret, unsolved)

        pareto_models[k] = best_model

    return pareto_models


# ==============================================================================
# 3단계: 임의의 N 실전 솔버 (하드코딩 알고리즘 Zero, 오직 E_hat 빔 탐색)
# ==============================================================================
def solve_with_discovered_rule(start_state, idxs, weights, beam_width=12, max_steps=2500):
    n = len(start_state) - 1
    goal = tuple([0] + list(range(1, n + 1)))
    if start_state == goal:
        return []

    def energy(s):
        if s == goal:
            return -1e9
        f = extract_primitives(s)
        return sum(w * f[i] for i, w in zip(idxs, weights))

    beam = [(energy(start_state), start_state, [])]
    visited = {start_state}

    for _ in range(max_steps):
        next_pool = {}
        for _, cur, path in beam:
            for m in MOVES:
                nxt = apply_move(cur, m)
                if nxt is None:
                    continue
                if nxt == goal:
                    return path + [m]
                if nxt in visited:
                    continue
                if nxt not in next_pool:
                    next_pool[nxt] = (energy(nxt), nxt, path + [m])

        if not next_pool:
            # 로컬 트랩 탈출을 위해 visited 완화 후 재시도
            visited.clear()
            for _, cur, path in beam:
                visited.add(cur)
                for m in MOVES:
                    nxt = apply_move(cur, m)
                    if nxt is not None and nxt not in visited:
                        next_pool[nxt] = (energy(nxt), nxt, path + [m])
            if not next_pool:
                break

        ordered = sorted(next_pool.values(), key=lambda item: item[0])
        beam = ordered[:beam_width]
        for _, st, _ in beam:
            visited.add(st)

    return None


def format_formula(idxs, weights):
    terms = [f"{w:.1f}*{PRIMITIVE_NAMES[i]}" for i, w in zip(idxs, weights)]
    return " + ".join(terms)


def main():
    t0 = time.time()
    print("=== push_swap 3단계: MDL 압축 가설 발명기 & 임의의 N 범용 솔버 ===\n")

    # 1. G_3 ~ G_8 정답 우주 구축
    print("[1단계] 정답 우주 G_3 ~ G_8 역방향 BFS 구축")
    graphs = {}
    for n in range(3, 9):
        ts = time.time()
        graphs[n] = build_exact_bfs(n)
        print(f"  G_{n} | 상태 수 = {len(graphs[n]):>7,} | 최대거리 = {max(graphs[n].values()):>2} ({time.time() - ts:.3f}s)")

    # 2. G_4 U G_5 만으로 MDL 규칙 발명
    print("\n[2단계] 오직 G_4 U G_5 (총 840개 상태)만으로 N-불변 수식 자동 발명")
    train_states = list(graphs[4].keys()) + list(graphs[5].keys())
    train_dist = {}
    train_dist.update(graphs[4])
    train_dist.update(graphs[5])

    ts = time.time()
    pareto_models = discover_rules_pareto(train_states, train_dist, max_k=4)
    print(f"  발명 완료 ({time.time() - ts:.2f}s) - 복잡도 K별 파레토 프론티어:\n")

    for k, (idxs, weights, mae, regret, _) in pareto_models.items():
        print(f"  [K={k}개 항] E_hat(S) = {format_formula(idxs, weights)}")
        print(f"           └─ 학습(G_4~5) 거리MAE: {mae:.2f} | 1-step 그리디 평균 손해(Regret): +{regret:.2f}회")

    # 3. 미지의 우주 G_6, G_7, G_8 제로샷 일반화 검증
    print("\n[3-A단계] 한 번도 보지 못한 큰 우주(G_6, G_7, G_8) 제로샷 일반화 성능 (beam=4)")
    rng = random.Random(42)
    test_sets = {
        6: list(graphs[6].keys()),
        7: rng.sample(list(graphs[7].keys()), 1500),
        8: rng.sample(list(graphs[8].keys()), 1500),
    }

    header = f"  {'규칙 복잡도':<12} | {'G_6 Regret':<12} | {'G_7 Regret':<12} | {'G_8 Regret':<12}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for k, (idxs, weights, _, _, _) in pareto_models.items():
        row_vals = []
        for n in (6, 7, 8):
            regrets = []
            for s in test_sets[n]:
                sol = solve_with_discovered_rule(s, idxs, weights, beam_width=4, max_steps=60)
                if sol is not None:
                    regrets.append(len(sol) - graphs[n][s])
            avg_r = sum(regrets) / len(regrets)
            row_vals.append(f"+{avg_r:.2f}회")
        print(f"  K={k}개 항      | {row_vals[0]:<12} | {row_vals[1]:<12} | {row_vals[2]:<12}")

    # 4. N = 10, 20, 50, 100 실전 정렬 테스트 (Turk/기수정렬 코드 0줄)
    best_k = max(pareto_models.keys())
    best_idxs, best_weights, _, _, _ = pareto_models[best_k]
    print(f"\n[3-B단계] 발명된 K={best_k} 수식 단 하나로 임의의 N 실전 정렬 테스트 (beam=12)")
    print(f"  적용 수식: E_hat(S) = {format_formula(best_idxs, best_weights)}\n")

    for N in (10, 20, 50, 100):
        trials = 10 if N <= 50 else 5
        counts = []
        ts = time.time()
        for _ in range(trials):
            perm = list(range(1, N + 1))
            rng.shuffle(perm)
            init_state = tuple([0] + perm)
            sol = solve_with_discovered_rule(init_state, best_idxs, best_weights, beam_width=12, max_steps=2500)
            assert sol is not None, f"Failed on N={N}"
            # 실제 goal 도달 검증
            cur = init_state
            for m in sol:
                cur = apply_move(cur, m)
            assert cur == tuple([0] + list(range(1, N + 1)))
            counts.append(len(sol))
        avg_moves = sum(counts) / len(counts)
        print(f"  N = {N:>3} | {trials:>2}회 무작위 테스트 100% 정렬 성공 | 평균 연산 수: {avg_moves:>6.1f}회 (min:{min(counts)}, max:{max(counts)}) [{time.time() - ts:.2f}s]")

    print(f"\n총 소요 시간: {time.time() - t0:.2f}초")


if __name__ == "__main__":
    main()