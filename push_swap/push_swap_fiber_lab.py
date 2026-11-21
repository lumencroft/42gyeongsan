from __future__ import annotations

from itertools import permutations
import math
import time

# =====================================================================
# 실험 설정: MAX_N = 7 이면 G_2 ~ G_8 까지 생성하여 7 -> 8 섬유까지 전수 분석
# 순수 Python 표준 라이브러리만 사용 (PyTorch / 외부 패키지 불필요)
# =====================================================================
MAX_N = 7
UNVISITED = 255

# Lehmer rank 고속 계산용 비트 마스크 popcount 룩업 테이블 (L <= 12 지원)
_POP_LOW = tuple(
    tuple((mask & ((1 << pi) - 1)).bit_count() for pi in range(12))
    for mask in range(1 << 12)
)


def get_factorials(L: int) -> tuple[int, ...]:
  """길이 L 순열의 Lehmer code 가중치 ((L-1)!, (L-2)!, ..., 0!) 반환"""
  return tuple(math.factorial(L - 1 - i) for i in range(L))


def rank_perm(perm: tuple[int, ...] | list[int], fact: tuple[int, ...]) -> int:
  """순열 -> 고유 정수 인덱스 [0 ~ L!-1] 변환 (목표 상태 [0, 1, ..., n] = 0)"""
  rank = 0
  left_mask = 0
  pop = _POP_LOW
  for i in range(len(perm) - 1):
    pi = perm[i]
    rank += (pi - pop[left_mask][pi]) * fact[i]
    left_mask |= 1 << pi
  return rank


def unrank_perm(rank: int, L: int, fact: tuple[int, ...]) -> tuple[int, ...]:
  """고유 정수 인덱스 -> 순열 튜플 역변환"""
  pool = list(range(L))
  res = []
  rem = rank
  for i in range(L):
    q, rem = divmod(rem, fact[i])
    res.append(pool.pop(q))
  return tuple(res)


def build_moves_by_zero_pos(
    L: int,
) -> dict[int, list[tuple[str, tuple[int, ...]]]]:
  """칸막이 '0'의 위치 z(스택 B 크기)가 정해지면, 11개 연산은 순수 인덱스 치환이 됨.

  표현: [b_k, ..., b_1, 0, a_1, ..., a_m]  (목표: [0, 1, ..., n])
  """
  moves_by_z: dict[int, list[tuple[str, tuple[int, ...]]]] = {}
  cols = list(range(L))

  for z in range(L):
    B = cols[:z]  # B[-1] = top(b_1), B[0] = bottom(b_k)
    A = cols[z + 1 :]  # A[0]  = top(a_1), A[-1] = bottom(a_m)
    m = len(A)
    cand: list[tuple[str, list[int]]] = []

    if z >= 1:
      cand.append(("pa", B[:-1] + [z, B[-1]] + A))
    if m >= 1:
      cand.append(("pb", B + [A[0], z] + A[1:]))
    if m >= 2:
      A_sa = [A[1], A[0]] + A[2:]
      A_ra = A[1:] + [A[0]]
      A_rra = [A[-1]] + A[:-1]
      cand.append(("sa", B + [z] + A_sa))
      cand.append(("ra", B + [z] + A_ra))
      cand.append(("rra", B + [z] + A_rra))
    if z >= 2:
      B_sb = B[:-2] + [B[-1], B[-2]]
      B_rb = [B[-1]] + B[:-1]
      B_rrb = B[1:] + [B[0]]
      cand.append(("sb", B_sb + [z] + A))
      cand.append(("rb", B_rb + [z] + A))
      cand.append(("rrb", B_rrb + [z] + A))
    if z >= 2 and m >= 2:
      cand.append(("ss", B_sb + [z] + A_sa))
      cand.append(("rr", B_rb + [z] + A_ra))
      cand.append(("rrr", B_rrb + [z] + A_rra))

    moves_by_z[z] = [(name, tuple(p)) for name, p in cand if p != cols]
  return moves_by_z


def bfs_universe(n: int) -> bytearray:
  """1단계: 목표 상태 (0, 1, ..., n) (rank=0)에서 전체 (n+1)! 우주로 역방향 BFS"""
  L = n + 1
  num_states = math.factorial(L)
  fact = get_factorials(L)
  raw_moves = build_moves_by_zero_pos(L)

  # BFS 탐색용 중복 제거 인덱스 치환표
  unique_moves: dict[int, tuple[tuple[int, ...], ...]] = {}
  for z, pairs in raw_moves.items():
    unique_moves[z] = tuple({idx_map for _, idx_map in pairs})

  dist = bytearray([UNVISITED]) * num_states
  goal = tuple(range(L))
  dist[0] = 0
  frontier = [goal]

  depth = 0
  while frontier:
    nxt_depth = depth + 1
    next_frontier = []
    for perm in frontier:
      z = perm.index(0)
      for idx_map in unique_moves[z]:
        nbr = tuple(perm[k] for k in idx_map)
        r = rank_perm(nbr, fact)
        if dist[r] == UNVISITED:
          dist[r] = nxt_depth
          next_frontier.append(nbr)
    frontier = next_frontier
    depth = nxt_depth

  return dist


def compute_fiber_deltas(
    n: int, dist_n: bytearray, dist_n1: bytearray
) -> list[tuple[int, ...]]:
  """2단계: G_n의 모든 상태 u에 대해 (n+1)을 n+2개 슬롯에 끼워 넣었을 때의 비용 증가량 Delta 계산"""
  L = n + 1
  fact_n1 = get_factorials(L + 1)
  new_val = (n + 1,)

  # permutations(range(L))은 Lehmer rank 0 ~ L!-1 순서와 정확히 일치함
  deltas: list[tuple[int, ...]] = []
  for r, perm in enumerate(permutations(range(L))):
    d_base = dist_n[r]
    row = tuple(
        dist_n1[rank_perm(perm[:j] + new_val + perm[j:], fact_n1)] - d_base
        for j in range(n + 2)
    )
    deltas.append(row)

  return deltas


def format_state(perm: tuple[int, ...] | list[int]) -> str:
  """순열을 직관적인 'B |0| A' 형태로 포맷팅 (화살표 쪽이 각 스택의 Top)"""
  z = perm.index(0)
  b_part = " ".join(map(str, perm[:z]))
  a_part = " ".join(map(str, perm[z + 1 :]))
  return f"[{b_part:>7} |0| {a_part:<11}]"


def trace_optimal_path(
    perm: tuple[int, ...] | list[int], dist: bytearray
) -> list[tuple[str, tuple[int, ...]]]:
  """특정 상태에서 목표 상태까지의 최단 연산 시퀀스 1개 역추적"""
  L = len(perm)
  fact = get_factorials(L)
  moves_by_z = build_moves_by_zero_pos(L)

  cur = tuple(perm)
  d = dist[rank_perm(cur, fact)]

  path: list[tuple[str, tuple[int, ...]]] = []
  while d > 0:
    z = cur.index(0)
    for name, idx_map in moves_by_z[z]:
      nxt = tuple(cur[k] for k in idx_map)
      if dist[rank_perm(nxt, fact)] == d - 1:
        path.append((name, nxt))
        cur = nxt
        d -= 1
        break
  return path


def inspect_concrete_phenomena(
    n: int,
    dist_n: bytearray,
    dist_n1: bytearray,
    deltas: list[tuple[int, ...]],
) -> None:
  """3단계 설계를 위한 핵심 현상(대조 쌍 & 무임승차) 실제 샘플 추출"""
  L = n + 1
  fact_n = get_factorials(L)
  a_only_limit = math.factorial(n)  # rank 0 ~ n!-1 이 정확히 perm[0] == 0 (A-전용 상태)

  # 1) 바닥 슬롯(j = n+1) 불변 안전지대(Delta=0) vs 불변량 파괴(Delta>=2) 대조 쌍
  free_rank = None
  costly_rank = None
  for r in range(a_only_limit):
    if dist_n[r] < 4:
      continue
    if free_rank is None and deltas[r][n + 1] == 0:
      free_rank = r
    if costly_rank is None and deltas[r][n + 1] >= 2:
      costly_rank = r
    if free_rank is not None and costly_rank is not None:
      break

  if free_rank is not None and costly_rank is not None:
    u1 = unrank_perm(free_rank, L, fact_n)
    u2 = unrank_perm(costly_rank, L, fact_n)
    u1_ext = u1 + (n + 1,)
    u2_ext = u2 + (n + 1,)

    p1 = [op for op, _ in trace_optimal_path(u1_ext, dist_n1)]
    p2_base = [op for op, _ in trace_optimal_path(u2, dist_n)]
    p2_ext = [op for op, _ in trace_optimal_path(u2_ext, dist_n1)]

    print(
        f"\n[현상 1: 대조적 가추(Contrastive Pair) 샘플 (n={n} -> {n+1}, 바닥"
        f" 슬롯 j={n+1})]"
    )
    print(
        f"  S1 (안전지대, Delta=0): {format_state(u1)} (d={dist_n[free_rank]})"
        f"  + '{n+1}' 바닥 삽입 -> d={len(p1)} | 해: {p1}"
    )
    print(
        f"  S2 (불변파괴, Delta={deltas[costly_rank][n+1]}): {format_state(u2)}"
        f" (d={dist_n[costly_rank]}, 원해: {p2_base})  + '{n+1}' 바닥 삽입 ->"
        f" d={len(p2_ext)} | 해: {p2_ext}"
    )

  # 2) 제자리가 아닌 슬롯(j != n+1)에 끼웠는데도 Delta=0으로 도착하는 '공생적 무임승차' 샘플
  for j in range(1, n + 1):
    checked = 0
    for r, d_u in enumerate(dist_n):
      if d_u >= 3 and deltas[r][j] == 0:
        u = unrank_perm(r, L, fact_n)
        u_ext = u[:j] + (n + 1,) + u[j:]
        ops_ext = [op for op, _ in trace_optimal_path(u_ext, dist_n1)]
        if any(op in ("rr", "rrr", "ss") for op in ops_ext):
          print(
              f"\n[현상 2: 공생적 무임승차(Piggybacking) 샘플 (n={n} -> {n+1},"
              f" 중간 슬롯 j={j})]"
          )
          print(f"  원래 상태 u     : {format_state(u)} (d_{n} = {d_u})")
          print(
              f"  '{n+1}' 끼운 상태 u_j: {format_state(u_ext)} (d_{n+1} ="
              f" {len(ops_ext)}, 추가비용 Delta = 0!)"
          )
          print(f"  무임승차 궤적   : {ops_ext}")
          return
        checked += 1
        if checked >= 30:
          break


def main() -> None:
  print(
      "=== push_swap 섬유 다발(Fiber Bundle) 실험실 | Pure Python (No Torch) ===\n"
  )

  t0 = time.perf_counter()
  dists: dict[int, bytearray] = {}

  print("[1단계] 전체 상태 우주 G_n 역방향 BFS 구축")
  for n in range(2, MAX_N + 2):
    ts = time.perf_counter()
    dists[n] = bfs_universe(n)
    L = n + 1
    a_only_limit = math.factorial(n)  # rank 0 ~ n!-1 이 정확히 perm[0] == 0
    max_all = max(dists[n])
    max_a_only = max(dists[n][:a_only_limit])
    print(
        f"  G_{n:<2d} | 상태 수 (n+1)! = {math.factorial(L):>9,d} | "
        f"A-전용 최대거리: {max_a_only:>2d} (우주 전체: {max_all:>2d}) | "
        f"{time.perf_counter() - ts:.3f}s"
    )

  print("\n[2단계] n -> n+1 확장 시 슬롯별 추가 비용 벡터 Delta 전수 검증")
  for n in range(2, MAX_N + 1):
    ts = time.perf_counter()
    deltas = compute_fiber_deltas(n, dists[n], dists[n + 1])

    min_d = min(min(row) for row in deltas)
    max_d = max(max(row) for row in deltas)
    assert min_d >= 0, f"이론 모순 발생! 음수 Delta 발견: {min_d}"

    counts: dict[int, int] = {}
    any_free_cnt = 0
    bottom_free_cnt = 0
    for row in deltas:
      if 0 in row:
        any_free_cnt += 1
      if row[n + 1] == 0:
        bottom_free_cnt += 1
      for v in row:
        counts[v] = counts.get(v, 0) + 1

    num_states = len(deltas)
    total_pairs = num_states * (n + 2)
    dist_str = ", ".join(
        f"Δ={v}:{counts[v] / total_pairs * 100:4.1f}%" for v in sorted(counts)
    )
    any_free_pct = any_free_cnt / num_states * 100.0
    bottom_free_pct = bottom_free_cnt / num_states * 100.0

    print(
        f"  G_{n} -> G_{n+1} | 음수위반: 0건 (min Δ={min_d}, max Δ={max_d}) | "
        f"공짜슬롯 보유 상태: {any_free_pct:5.1f}% (A바닥 j={n+1} 공짜: {bottom_free_pct:4.1f}%) | "
        f"[{dist_str}] ({time.perf_counter() - ts:.3f}s)"
    )

    if n == 5:
      slot_free = [
          sum(1 for row in deltas if row[j] == 0) / num_states
          for j in range(n + 2)
      ]
      slot_mean = [
          sum(row[j] for row in deltas) / num_states for j in range(n + 2)
      ]
      print(
          "    └─ [G_5 -> G_6 슬롯별(j=0..6) Δ=0 비율]: "
          + " | ".join(
              f"j={j}:{slot_free[j]*100:4.1f}%(평균+{slot_mean[j]:.2f})"
              for j in range(n + 2)
          )
      )
      inspect_concrete_phenomena(n, dists[n], dists[n + 1], deltas)

  print(f"\n총 소요 시간: {time.perf_counter() - t0:.2f}초")


if __name__ == "__main__":
  main()