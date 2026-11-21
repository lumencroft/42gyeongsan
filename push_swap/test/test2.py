# test2.py (push_swap_scale_discovery.py)
# Pure Python (No Torch) - G_4 U G_5 학습만으로 N=50, 100 돌파 실험
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
# N-불변 순수 구조 원시 어휘 (기울기 연속성 & 다중 원소 동시 회전 반영)
# ==============================================================================
PRIMITIVE_NAMES = [
    "cnt_B",              # 0: 스택 B 점유 원소 수
    "non_lis_A",          # 1: A의 최장 원형 증가 부분수열(Cyclic LIS) 이탈 원소 수
    "escape_depth",       # 2: 가장 가까운 A의 비-LIS 원소가 A-Top(index 0)에 도달하는 최소 회전 수
    "min_b_insert_cost",  # 3: B의 모든 원소 중 rr/rrr 동시 회전을 포함해 A 제자리에 꽂는 최소 비용
    "minA_shift",         # 4: A의 최솟값을 A-Top으로 정렬하는 최소 회전 수 (결승선 위상 정렬)
    "a_breaks",           # 5: A 내부 원형 순서 깨짐 초과 개수
    "b_breaks",           # 6: B 내부 역순 정렬 깨짐 개수
    "topA_swap",          # 7: A-Top 두 원소 즉시 교환(sa) 이득 여부
    "topB_swap",          # 8: B-Top 두 원소 즉시 교환(sb) 이득 여부
    "b_straddle",         # 9: B 값 범위가 A 내부와 얽혀 있는지 여부
]


def _cyclic_lis_info(A):
    """상한 가지치기가 적용된 고속 Cyclic LIS 계산"""
    m = len(A)
    if m <= 1:
        return m, []

    starts = [i for i in range(m) if A[(i - 1) % m] > A[i]]
    if not starts:
        return m, []
    if len(starts) == 1:
        return m, []

    sorted_A = sorted(A)
    best_len = 0
    best_kept_orig = set()

    for s in starts:
        # s에서 시작해 만들 수 있는 최대 증가 수열 길이 상한 체크 (가지치기)
        max_possible = m - bisect_left(sorted_A, A[s])
        if max_possible <= best_len:
            continue

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
            if best_len == m - 1:
                break

    non_lis_indices = [i for i in range(m) if i not in best_kept_orig]
    return best_len, non_lis_indices


def extract_primitives(state):
    z = state.index(0)
    B = state[:z]
    A = state[z + 1:]
    cnt_B = len(B)
    m = len(A)

    # 1. non_lis_A & 2. escape_depth (index 0이면 0회전, index 1 또는 m-1이면 1회전)
    lis_len, non_lis_idx = _cyclic_lis_info(A)
    non_lis_A = m - lis_len
    if non_lis_idx:
        escape_depth = min(min(i, m - i) for i in non_lis_idx)
    else:
        escape_depth = 0

    # 3. min_b_insert_cost: B의 모든 원소 중 rr/rrr 동시 회전 포함 최소 A-삽입 비용
    if cnt_B == 0 or m == 0:
        min_b_insert_cost = 0
    else:
        # A에서 삽입 위치 탐색을 O(log m)으로 수행하기 위해 (값, 원래인덱스) 정렬
        indexed_A = sorted((v, i) for i, v in enumerate(A))
        vals_A = [v for v, _ in indexed_A]
        min_idx_A = indexed_A[0][1]

        best_cost = 10**9
        for idx_b, val_b in enumerate(B):
            up_b = (cnt_B - 1) - idx_b   # rb 횟수
            down_b = idx_b + 1           # rrb 횟수
            pos = bisect_left(vals_A, val_b)
            t_a = indexed_A[pos][1] if pos < m else min_idx_A
            up_a = t_a                   # ra 횟수
            down_a = m - t_a             # rra 횟수

            c_up = up_a if up_a > up_b else up_b
            c_dn = down_a if down_a > down_b else down_b
            c_mx = (up_a if up_a < down_a else down_a) + (up_b if up_b < down_b else down_b)
            cost = c_up if c_up < c_dn else c_dn
            if c_mx < cost:
                cost = c_mx
            if cost < best_cost:
                best_cost = cost
                if best_cost == 0:
                    break
        min_b_insert_cost = best_cost

    # 4. minA_shift
    if m <= 1:
        minA_shift = 0
    else:
        min_pos = min(range(m), key=lambda i: A[i])
        minA_shift = min(min_pos, m - min_pos)

    # 5. a_breaks
    if m <= 1:
        a_breaks = 0
    else:
        desc = sum(1 for i in range(m) if A[i] > A[(i + 1) % m])
        a_breaks = max(0, desc - 1)

    # 6. b_breaks
    if cnt_B <= 1:
        b_breaks = 0
    else:
        b_breaks = sum(1 for i in range(cnt_B - 1) if B[i] > B[i + 1])

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
        float(escape_depth),
        float(min_b_insert_cost),
        float(minA_shift),
        float(a_breaks),
        float(b_breaks),
        float(topA_swap),
        float(topB_swap),
        float(b_straddle),
    )


# ==============================================================================
# 2단계: MDL 복잡도 제한 가설 발명기 (G_4 U G_5 전 상태 평가)
# ==============================================================================
def _solve_linear_system(M, y):
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
        M[a][a] += 1e-4
        for b in range(a):
            M[a][b] = M[b][a]
    return _solve_linear_system(M, rhs)


def evaluate_policy_regret(states, dist_map, feat_cache, idxs, weights):
    """G_4 U G_5 전체 840개 상태에 대해 1-step 그리디 하강 Regret 측정"""
    total_regret = 0.0
    unsolved = 0

    for s in states:
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

    return total_regret / len(states), unsolved


def discover_rules_pareto(train_states, train_dist, max_k=5):
    feat_cache = {s: extract_primitives(s) for s in train_states}
    X_rows = [feat_cache[s] for s in train_states]
    y_vals = [float(train_dist[s]) for s in train_states]

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
            w_clean = [round(val, 1) for val in w]
            if any(val <= 0.0 for val in w_clean):
                continue
            mae = sum(
                abs(sum(wt * x[i] for i, wt in zip(idxs, w_clean)) - y)
                for x, y in zip(X_rows, y_vals)
            ) / len(y_vals)
            candidates.append((mae, idxs, w_clean))

        candidates.sort(key=lambda item: item[0])
        best_model = None
        best_obj = float('inf')

        for mae, idxs, w_init in candidates[:15]:
            w_cur = list(w_init)
            regret, unsolved = evaluate_policy_regret(train_states, train_dist, feat_cache, idxs, w_cur)
            for dim in range(k):
                for delta in (-0.4, -0.2, 0.2, 0.4):
                    w_try = list(w_cur)
                    w_try[dim] = round(w_try[dim] + delta, 1)
                    if w_try[dim] <= 0.0:
                        continue
                    r_try, u_try = evaluate_policy_regret(train_states, train_dist, feat_cache, idxs, w_try)
                    if (u_try, r_try) < (unsolved, regret):
                        w_cur, regret, unsolved = w_try, r_try, u_try

            final_mae = sum(
                abs(sum(wt * x[i] for i, wt in zip(idxs, w_cur)) - y)
                for x, y in zip(X_rows, y_vals)
            ) / len(y_vals)
            obj = regret + 0.12 * final_mae + 5.0 * unsolved
            if obj < best_obj:
                best_obj = obj
                best_model = (idxs, w_cur, final_mae, regret, unsolved)

        pareto_models[k] = best_model

    return pareto_models


# ==============================================================================
# 3단계: 임의의 N 실전 솔버 (상태 캐싱 + 역연산 가지치기 적용)
# ==============================================================================
def solve_with_discovered_rule(start_state, idxs, weights, beam_width=12, max_steps=3000):
    n = len(start_state) - 1
    goal = tuple([0] + list(range(1, n + 1)))
    if start_state == goal:
        return []

    score_cache = {}

    def energy(s):
        if s == goal:
            return -1e9
        val = score_cache.get(s)
        if val is None:
            f = extract_primitives(s)
            val = sum(w * f[i] for i, w in zip(idxs, weights))
            score_cache[s] = val
        return val

    beam = [(energy(start_state), start_state, [], None)]
    visited = {start_state}

    for _ in range(max_steps):
        next_pool = {}
        for _, cur, path, last_m in beam:
            inv_last = INV_MOVES[last_m] if last_m else None
            for m in MOVES:
                if m == inv_last:
                    continue
                nxt = apply_move(cur, m)
                if nxt is None:
                    continue
                if nxt == goal:
                    return path + [m]
                if nxt in visited:
                    continue
                if nxt not in next_pool:
                    next_pool[nxt] = (energy(nxt), nxt, path + [m], m)

        if not next_pool:
            visited.clear()
            for _, cur, path, _ in beam:
                visited.add(cur)
                for m in MOVES:
                    nxt = apply_move(cur, m)
                    if nxt is not None and nxt not in visited:
                        next_pool[nxt] = (energy(nxt), nxt, path + [m], m)
            if not next_pool:
                break

        ordered = sorted(next_pool.values(), key=lambda item: item[0])
        beam = ordered[:beam_width]
        for _, st, _, _ in beam:
            visited.add(st)

    return None


def format_formula(idxs, weights):
    return " + ".join(f"{w:.1f}*{PRIMITIVE_NAMES[i]}" for i, w in zip(idxs, weights))


def main():
    t0 = time.time()
    print("=== push_swap 3-2단계: 기울기 연속성 & B 최소삽입 포텐셜 보강 실험 ===\n")

    print("[1단계] 정답 우주 G_3 ~ G_8 역방향 BFS 구축")
    graphs = {}
    for n in range(3, 9):
        ts = time.time()
        graphs[n] = build_exact_bfs(n)
        print(f"  G_{n} | 상태 수 = {len(graphs[n]):>7,} | 최대거리 = {max(graphs[n].values()):>2} ({time.time() - ts:.3f}s)")

    print("\n[2단계] 오직 G_4 U G_5 (840개 상태)만으로 N-불변 수식 자동 발명 (K=1..5)")
    train_states = list(graphs[4].keys()) + list(graphs[5].keys())
    train_dist = {}
    train_dist.update(graphs[4])
    train_dist.update(graphs[5])

    ts = time.time()
    pareto_models = discover_rules_pareto(train_states, train_dist, max_k=5)
    print(f"  발명 완료 ({time.time() - ts:.2f}s) - 복잡도 K별 파레토 프론티어:\n")

    for k, (idxs, weights, mae, regret, _) in pareto_models.items():
        print(f"  [K={k}개 항] E_hat(S) = {format_formula(idxs, weights)}")
        print(f"           └─ 학습(G_4~5) 거리MAE: {mae:.2f} | 1-step 그리디 평균 손해(Regret): +{regret:.2f}회")

    print("\n[3-A단계] 미지의 큰 우주(G_6, G_7, G_8) 제로샷 일반화 성능 (beam=4)")
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
            sol = solve_with_discovered_rule(init_state, best_idxs, best_weights, beam_width=12, max_steps=3000)
            assert sol is not None, f"Failed on N={N}"
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