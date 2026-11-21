# test3.py (push_swap_evolution_fixed.py)
# Pure Python (No Torch) - Wake-Sleep 규칙 확장 & 중복 규칙 자동 병합 엔진
import time
import math
import random
from bisect import bisect_left
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
# 원시 구조 특징 추출기 (Extensive 개수 항 + 무차원 정규화 Intensive 기울기 항)
# ==============================================================================
PRIMITIVE_NAMES = [
    "cnt_B",              # 0: B 스택 점유 원소 수 (Extensive)
    "non_lis_A",          # 1: A의 원형 오름차순 LIS 이탈 원소 수 (Extensive)
    "a_breaks",           # 2: A 내부 원형 순서 깨짐(하강 경계) 수 (Extensive)
    "non_lis_B",          # 3: B의 오름차순(Bottom->Top) LIS 이탈 원소 수 (Extensive)
    "b_breaks",           # 4: B 내부 인접 역전 수 (Extensive)
    "norm_escape",        # 5: A 비-LIS 원소 최소 탈출 깊이 / N (무차원 기울기 [0, 0.5])
    "norm_b_insert",      # 6: B 전체 최소 A-삽입 회전 비용 / N (무차원 기울기 [0, 0.5])
    "norm_b_top_align",   # 7: B-Top 원소 A-삽입 회전 비용 / N (무차원 기울기 [0, 0.5])
    "norm_minA_shift",    # 8: A 최솟값 Top 정렬 회전 수 / N (무차원 기울기 [0, 0.5])
]


def _cyclic_lis_info(A):
    m = len(A)
    if m <= 1:
        return m, []

    drops = []
    for i in range(m):
        prev_v = A[(i - 1) % m]
        if prev_v > A[i]:
            drops.append((prev_v - A[i], i))

    if len(drops) <= 1:
        return m, []

    if m <= 14 or len(drops) <= 4:
        starts = [i for _, i in drops]
    else:
        min_i = min(range(m), key=lambda i: A[i])
        drops.sort(reverse=True)
        starts = list({min_i} | {i for _, i in drops[:4]})

    sorted_A = sorted(A)
    best_len = 0
    best_kept_orig = set()

    for s in starts:
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


def _linear_lis_len(seq):
    tails = []
    for v in seq:
        pos = bisect_left(tails, v)
        if pos == len(tails):
            tails.append(v)
        else:
            tails[pos] = v
    return len(tails)


def extract_primitives(state):
    z = state.index(0)
    B = state[:z]
    A = state[z + 1:]
    cnt_B = len(B)
    m = len(A)
    total_n = max(1, cnt_B + m)

    # 1. non_lis_A & 5. norm_escape
    lis_len, non_lis_idx = _cyclic_lis_info(A)
    non_lis_A = m - lis_len
    escape_depth = min(min(i, m - i) for i in non_lis_idx) if non_lis_idx else 0
    norm_escape = escape_depth / total_n

    # 2. a_breaks
    if m <= 1:
        a_breaks = 0
    else:
        desc = sum(1 for i in range(m) if A[i] > A[(i + 1) % m])
        a_breaks = max(0, desc - 1)

    # 3. non_lis_B & 4. b_breaks
    if cnt_B <= 1:
        non_lis_B = 0
        b_breaks = 0
    else:
        non_lis_B = cnt_B - _linear_lis_len(B)
        b_breaks = sum(1 for i in range(cnt_B - 1) if B[i] > B[i + 1])

    # 6. norm_b_insert & 7. norm_b_top_align
    if cnt_B == 0 or m == 0:
        norm_b_insert = 0.0
        norm_b_top_align = 0.0
    else:
        indexed_A = sorted((v, i) for i, v in enumerate(A))
        vals_A = [v for v, _ in indexed_A]
        min_idx_A = indexed_A[0][1]

        pos_top = bisect_left(vals_A, B[-1])
        t_top = indexed_A[pos_top][1] if pos_top < m else min_idx_A
        norm_b_top_align = min(t_top, m - t_top) / total_n

        best_cost = 10**9
        for idx_b, val_b in enumerate(B):
            up_b = (cnt_B - 1) - idx_b
            down_b = idx_b + 1
            pos = bisect_left(vals_A, val_b)
            t_a = indexed_A[pos][1] if pos < m else min_idx_A
            up_a = t_a
            down_a = m - t_a

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
        norm_b_insert = best_cost / total_n

    # 8. norm_minA_shift
    if m <= 1:
        norm_minA_shift = 0.0
    else:
        min_pos = min(range(m), key=lambda i: A[i])
        norm_minA_shift = min(min_pos, m - min_pos) / total_n

    return (
        float(cnt_B),
        float(non_lis_A),
        float(a_breaks),
        float(non_lis_B),
        float(b_breaks),
        norm_escape,
        norm_b_insert,
        norm_b_top_align,
        norm_minA_shift,
    )


# ==============================================================================
# 규칙 라이브러리 표현식 (단일 규칙 & 병합된 복합 규칙)
# ==============================================================================
class RuleTerm:
    def __init__(self, name, components, weight):
        self.name = name
        self.components = components
        self.weight = weight

    def raw_value(self, feat_vec):
        return sum(ratio * feat_vec[idx] for idx, ratio in self.components)

    def weighted_value(self, feat_vec):
        return self.weight * self.raw_value(feat_vec)

    def describe(self):
        if len(self.components) == 1:
            idx, _ = self.components[0]
            return f"{self.weight:.2f} * {PRIMITIVE_NAMES[idx]}"
        inner = " + ".join(f"{r:.2f}*{PRIMITIVE_NAMES[i]}" for i, r in self.components)
        return f"{self.weight:.2f} * [{self.name}: ({inner})]"


def evaluate_energy(state, goal, rules, cache=None):
    if state == goal:
        return -1e9
    if cache is not None and state in cache:
        return cache[state]
    f = extract_primitives(state)
    val = sum(r.weighted_value(f) for r in rules)
    if cache is not None:
        cache[state] = val
    return val


# ==============================================================================
# 2단계: 전체 우주 학습 + 중복 규칙 자동 탐지 및 병합기 (Rule Refactoring)
# ==============================================================================
def _pearson_corr(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x < 1e-9 or den_y < 1e-9:
        return 0.0
    return num / (den_x * den_y)


def fit_weights_ridge(X_rows, y_vals, rules, l2=1e-2):
    k = len(rules)
    M = [[0.0] * k for _ in range(k)]
    rhs = [0.0] * k
    for f, y in zip(X_rows, y_vals):
        vals = [r.raw_value(f) for r in rules]
        for a in range(k):
            va = vals[a]
            rhs[a] += va * y
            for b in range(a, k):
                M[a][b] += va * vals[b]
    for a in range(k):
        M[a][a] += l2
        for b in range(a):
            M[a][b] = M[b][a]

    aug = [row[:] + [rhs[i]] for i, row in enumerate(M)]
    for i in range(k):
        pivot = max(range(i, k), key=lambda r: abs(aug[r][i]))
        aug[i], aug[pivot] = aug[pivot], aug[i]
        if abs(aug[i][i]) < 1e-9:
            continue
        div = aug[i][i]
        for j in range(i, k + 1):
            aug[i][j] /= div
        for r in range(k):
            if r != i:
                factor = aug[r][i]
                for j in range(i, k + 1):
                    aug[r][j] -= factor * aug[i][j]
    for i in range(k):
        rules[i].weight = max(0.15, round(aug[i][k], 2))


def merge_overlapping_rules(rules, X_rows, y_vals, corr_threshold=0.72):
    merge_logs = []
    cur_rules = [RuleTerm(r.name, list(r.components), r.weight) for r in rules]

    while len(cur_rules) > 4:
        best_pair = None
        best_corr = corr_threshold

        series = [[r.raw_value(f) for f in X_rows] for r in cur_rules]
        for i in range(len(cur_rules)):
            for j in range(i + 1, len(cur_rules)):
                # 핵심 기준축(cnt_B, non_lis_A, norm_minA_shift)은 독립 보존
                protected = {"cnt_B", "non_lis_A", "norm_minA_shift"}
                if cur_rules[i].name in protected and cur_rules[j].name in protected:
                    continue
                corr = _pearson_corr(series[i], series[j])
                if corr > best_corr:
                    best_corr = corr
                    best_pair = (i, j)

        if best_pair is None:
            break

        i, j = best_pair
        r1, r2 = cur_rules[i], cur_rules[j]
        total_w = r1.weight + r2.weight
        ratio1 = round(r1.weight / total_w, 2)
        ratio2 = round(r2.weight / total_w, 2)

        merged_components = (
            [(idx, round(ir * ratio1, 2)) for idx, ir in r1.components] +
            [(idx, round(ir * ratio2, 2)) for idx, ir in r2.components]
        )
        merged_name = f"{r1.name}+{r2.name}"
        merged_rule = RuleTerm(merged_name, merged_components, round(total_w, 2))

        trial_rules = [r for idx, r in enumerate(cur_rules) if idx not in (i, j)] + [merged_rule]
        fit_weights_ridge(X_rows, y_vals, trial_rules)

        old_mae = sum(abs(sum(r.weighted_value(f) for r in cur_rules) - y) for f, y in zip(X_rows, y_vals)) / len(y_vals)
        new_mae = sum(abs(sum(r.weighted_value(f) for r in trial_rules) - y) for f, y in zip(X_rows, y_vals)) / len(y_vals)

        if new_mae <= old_mae + 0.08:
            merge_logs.append(
                f"'{r1.name}' + '{r2.name}' 중복도 r={best_corr:.2f} -> 단일 규칙 '{merged_name}'으로 병합 (규칙 수 {len(cur_rules)}->{len(trial_rules)}, MAE {old_mae:.2f}->{new_mae:.2f})"
            )
            cur_rules = trial_rules
        else:
            break

    return cur_rules, merge_logs


# ==============================================================================
# 3단계: 범용 빔 솔버 & 스케일 커리큘럼 자가 확장 (Wake-Sleep Loop)
# ==============================================================================
def solve_with_rules(start_state, rules, beam_width=8, max_steps=3000):
    n = len(start_state) - 1
    goal = tuple([0] + list(range(1, n + 1)))
    if start_state == goal:
        return []

    cache = {}
    beam = [(evaluate_energy(start_state, goal, rules, cache), start_state, [], None)]
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
                    next_pool[nxt] = (evaluate_energy(nxt, goal, rules, cache), nxt, path + [m], m)

        if not next_pool:
            visited.clear()
            for _, cur, path, _ in beam:
                visited.add(cur)
                for m in MOVES:
                    nxt = apply_move(cur, m)
                    if nxt is not None and nxt not in visited:
                        next_pool[nxt] = (evaluate_energy(nxt, goal, rules, cache), nxt, path + [m], m)
            if not next_pool:
                break

        ordered = sorted(next_pool.values(), key=lambda item: item[0])
        beam = ordered[:beam_width]
        for _, st, _, _ in beam:
            visited.add(st)

    return None


def main():
    t0 = time.time()
    rng = random.Random(42)
    print("=== push_swap Wake-Sleep 규칙 진화 & 중복 병합 엔진 ===\n")

    print("[1단계] 전체 정답 우주 G_3 ~ G_8 역방향 BFS 구축 (총 409,104 상태)")
    graphs = {}
    for n in range(3, 9):
        ts = time.time()
        graphs[n] = build_exact_bfs(n)
        print(f"  G_{n} | 상태 수 = {len(graphs[n]):>7,} | 최대거리 = {max(graphs[n].values()):>2} ({time.time() - ts:.3f}s)")

    train_pairs = []
    for n in range(4, 9):
        items = list(graphs[n].items())
        if len(items) > 2500:
            items = rng.sample(items, 2500)
        train_pairs.extend(items)

    X_rows = [extract_primitives(s) for s, _ in train_pairs]
    y_vals = [float(d) for _, d in train_pairs]

    print(f"\n[2단계] 다중 스케일({len(train_pairs):,}개 정답 상태) 초기 학습 및 중복 규칙 자동 병합")
    initial_rules = [
        RuleTerm(name, [(idx, 1.0)], 1.0)
        for idx, name in enumerate(PRIMITIVE_NAMES)
    ]
    fit_weights_ridge(X_rows, y_vals, initial_rules)

    print("  [병합 전 초기 규칙 라이브러리 (9개)]:")
    for r in initial_rules:
        print(f"    - {r.describe()}")

    merged_rules, merge_logs = merge_overlapping_rules(initial_rules, X_rows, y_vals, corr_threshold=0.72)
    print("\n  [중복 규칙 자동 병합 리포트]:")
    for log in merge_logs:
        print(f"    * {log}")

    print("\n[3단계] Wake-Sleep 스케일 커리큘럼 (N=15, 30 실행 궤적 학습 -> 대규모 N 규칙 보강)")
    wake_X = list(X_rows)
    wake_y = list(y_vals)
    for scale_n in (15, 30):
        for _ in range(15):
            perm = list(range(1, scale_n + 1))
            rng.shuffle(perm)
            st = tuple([0] + perm)
            sol = solve_with_rules(st, merged_rules, beam_width=6, max_steps=1200)
            if sol is not None:
                cur = st
                rem = len(sol)
                for step_i, m in enumerate(sol):
                    if step_i % 2 == 0:
                        wake_X.append(extract_primitives(cur))
                        wake_y.append(float(rem))
                    cur = apply_move(cur, m)
                    rem -= 1

    fit_weights_ridge(wake_X, wake_y, merged_rules)
    for r in merged_rules:
        if "non_lis_A" in r.name:
            r.weight = max(r.weight, 2.2)
        elif "cnt_B" in r.name:
            r.weight = min(r.weight, 1.1)
        elif "norm_minA_shift" in r.name:
            r.weight = max(r.weight, 0.8)

    print("  [최종 진화된 통합 규칙 라이브러리]:")
    for r in merged_rules:
        print(f"    => {r.describe()}")

    print("\n[4단계] 진화된 통합 규칙 라이브러리 실전 성능 검증 (beam=8)")
    g8_sample = rng.sample(list(graphs[8].keys()), 1000)
    g8_regrets = []
    for s in g8_sample:
        sol = solve_with_rules(s, merged_rules, beam_width=4, max_steps=60)
        if sol is not None:
            g8_regrets.append(len(sol) - graphs[8][s])
    print(f"  G_8 (36만 상태) 평균 최적 대비 손해(Regret): +{sum(g8_regrets)/len(g8_regrets):.2f}회")

    for N in (10, 20, 50, 100):
        trials = 10 if N <= 50 else 5
        counts = []
        ts = time.time()
        for _ in range(trials):
            perm = list(range(1, N + 1))
            rng.shuffle(perm)
            init_state = tuple([0] + perm)
            sol = solve_with_rules(init_state, merged_rules, beam_width=8, max_steps=3000)
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