"""Hill Climbing

Variações implementadas:
- hill_climbing_sideways: permite movimentos laterais (h igual) até um limite.
- hill_climbing_random_restart: reinicia de estados aleatórios até achar solução ou atingir limite de reinícios.

Dependências utilitárias em eight_queens:
- Representação: board[c] = linha da rainha na coluna c
- Funções: conflicts(board), neighbors(board), apply(board, mv), initial_board(n)
"""

from __future__ import annotations
from typing import List, Tuple, Iterable, Optional, Dict, Any
import random
from time import perf_counter

from .eight_queens import conflicts, neighbors, apply, initial_board

Board = List[int]
Move = Tuple[int, int]


def _best_neighbor_moves(board: Board) -> Tuple[int, List[Move]]:
	# Retorna (h_min, lista de movimentos com h_min) dentre todos os vizinhos.
	# h_min: menor conflicts; lista inclui todos os empates.
	h_min = float('inf')
	best: List[Move] = []
	for mv in neighbors(board):
		nb = apply(board, mv)
		h = conflicts(nb)
		if h < h_min:
			h_min = h
			best = [mv]
		elif h == h_min:
			best.append(mv)
	if h_min == float('inf'):
		# sem vizinhos
		h_min = conflicts(board)
	return int(h_min), best

def hill_climbing_basic(
    board0: Board,
    *,
    max_iters: int = 1000,
    rng: Optional[random.Random] = None,
) -> Dict[str, Any]:
    # Hill Climbing tradicional (sem movimentos laterais).
    # Retorna dict: board, success, steps, time_sec, conflicts_final.
    r = rng or random
    cur = list(board0)
    h_cur = conflicts(cur)
    steps = 0
    t0 = perf_counter()

    for _ in range(max_iters):
        if h_cur == 0:
            break
        h_best, moves = _best_neighbor_moves(cur)
        if not moves:
            break
        if h_best < h_cur:
            mv = r.choice(moves)
            cur = apply(cur, mv)
            h_cur = conflicts(cur)
            steps += 1
        else:
            # Nenhum vizinho melhora: chegou em mínimo local
            break

    t1 = perf_counter()
    return {
        "board": cur,
        "success": h_cur == 0,
        "steps": steps,
        "time_sec": t1 - t0,
        "conflicts_final": h_cur,
    }


def hill_climbing_sideways(
	board0: Board,
	*,
	lateral_limit: int = 20,
	max_iters: int = 1000,
	rng: Optional[random.Random] = None,
) -> Dict[str, Any]:
    # Hill Climbing com movimentos laterais (mesmo h) até lateral_limit.
    # Retorna dict: board, success, steps, sideways_used, time_sec, conflicts_final.
	r = rng or random
	cur = list(board0)
	h_cur = conflicts(cur)
	steps = 0
	sideways_used = 0
	t0 = perf_counter()

	for _ in range(max_iters):
		if h_cur == 0:
			break
		h_best, moves = _best_neighbor_moves(cur)
		if not moves:
			break
		if h_best < h_cur:
			mv = r.choice(moves)
			cur = apply(cur, mv)
			h_cur = conflicts(cur)
			steps += 1
			continue
		if h_best == h_cur and sideways_used < lateral_limit:
			mv = r.choice(moves)
			cur = apply(cur, mv)
			h_cur = conflicts(cur)
			steps += 1
			sideways_used += 1
			continue
		# Caso h_best > h_cur (pior) ou sem laterais disponíveis -> para
		break

	t1 = perf_counter()
	return {
		"board": cur,
		"success": h_cur == 0,
		"steps": steps,
		"sideways_used": sideways_used,
		"time_sec": t1 - t0,
		"conflicts_final": h_cur,
	}

def hill_climbing_random_restart(
    n: int = 8,
    *,
    max_restarts: int = 50,
    max_iters_per_restart: int = 1000,
    rng: Optional[random.Random] = None,
    initial_board_override: Optional[Board] = None,
) -> Dict[str, Any]:
    # Random-Restart Hill Climbing: reinicia de estados aleatórios até h==0.
    r = rng or random
    t0 = perf_counter()

    restarts = 0
    steps_total = 0
    best_board: Optional[Board] = None
    best_h = float("inf")
    conflicts_start: Optional[int] = None

    for attempt in range(max_restarts + 1):
        if attempt == 0 and initial_board_override is not None:
            cur = list(initial_board_override)
        else:
            cur = initial_board(n)

        # Armazena h inicial apenas na primeira tentativa
        if conflicts_start is None:
            conflicts_start = conflicts(cur)

        res = hill_climbing_basic(
            cur,
            max_iters=max_iters_per_restart,
            rng=r,
        )

        steps_total += int(res.get("steps", 0))
        # Suporta tanto a chave nova (conflicts_final) quanto a antiga (h_final) por compatibilidade
        h_cur = int(res.get("conflicts_final", res.get("h_final", conflicts(res["board"]))))
        if h_cur < best_h:
            best_h = h_cur
            best_board = list(res["board"])

        if res.get("success"):
            t1 = perf_counter()
            return {
                "board": res["board"],
                "success": True,
                "restarts": restarts,
                "steps_total": steps_total,
                "time_sec": t1 - t0,
                "conflicts_final": h_cur,
                "conflicts_start": int(conflicts_start),
            }

        restarts += 1

    # Não encontrou solução
    t1 = perf_counter()
    final_board = best_board if best_board is not None else initial_board(n)
    return {
        "board": final_board,
        "success": False,
        "restarts": restarts,
        "steps_total": steps_total,
        "time_sec": t1 - t0,
        "conflicts_final": conflicts(final_board),
        "conflicts_start": int(conflicts_start) if conflicts_start is not None else conflicts(final_board),
    }




# Runner simples
if __name__ == "__main__":
    random.seed(42)
    b = initial_board(8)
    print("Inicial:", b, "h=", conflicts(b))
    r1 = hill_climbing_sideways(b, lateral_limit=50)
    print("HC-sideways -> success=", r1["success"], "h=", r1.get("conflicts_final", r1.get("h_final")), "steps=", r1["steps"])  # type: ignore[index]
    r2 = hill_climbing_random_restart(8, max_restarts=50)
    print("RR-HC -> success=", r2["success"], "h=", r2.get("conflicts_final", r2.get("h_final")), "restarts=", r2["restarts"])  # type: ignore[index]

