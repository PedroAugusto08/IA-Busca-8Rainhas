"""Algoritmos de busca não informada (BFS e DFS) para o Maze NSLO.

Contrato das funções:
	- bfs(maze) -> list[Pos]
	- dfs(maze) -> list[Pos]

Onde Pos = tuple[int,int].

Regras/Assunções:
	- Usa API do Maze: maze.start(), maze.goal(), maze.neighbors(pos) e maze.step_cost(from,to) (fixo 1).
	- Retorna a sequência de posições do START até o GOAL (inclusivos). Se start == goal, lista com apenas essa posição.
	- Se não houver caminho, retorna lista vazia [].
	- BFS garante caminho mais curto em número de passos; DFS não garante otimalidade.
	- A ordem de vizinhos (N,S,L,O) já é determinada pelo Maze, garantindo determinismo.

Campos de métricas (opcional): As funções também retornam (por enquanto comentado) possibilidade de métricas se desejado futuramente.

Edge cases abordados:
	- Labirinto vazio: Maze.from_file já impede.
	- Start == Goal: retorno imediato.
	- Nenhum caminho: visita esgota fronteira e retorna [].
"""
from __future__ import annotations
from collections import deque
from typing import Dict, List, Tuple, Optional, Callable, TYPE_CHECKING
import heapq
from itertools import count

if TYPE_CHECKING:
	# Import apenas para análise estática, evitando acoplamento em tempo de execução
	from .maze import Maze
	# Heurísticas para type hint (opcional)
	from .heuristics import manhattan as _manhattan_hint, euclidean as _euclidean_hint

Pos = Tuple[int,int]

def _reconstruct_path(came_from: Dict[Pos, Pos], start: Pos, goal: Pos) -> List[Pos]:
	# Reconstrói caminho usando o dicionário de predecessores.
	# Se goal não foi alcançado, devolve [].
	if start == goal:
		return [start]
	if goal not in came_from:
		return []
	cur = goal
	rev: List[Pos] = [cur]
	while cur != start:
		cur = came_from[cur]
		rev.append(cur)
	rev.reverse()
	return rev


def bfs(maze: "Maze") -> List[Pos]:
	# BFS (Breadth-First Search): garante menor número de passos.
	# Estruturas: fila (deque), conjunto visited, mapa came_from.
	start = maze.start()
	goal = maze.goal()
	if start == goal:
		return [start]

	queue = deque([start])
	visited = {start}
	came_from: Dict[Pos, Pos] = {}

	while queue:
		current = queue.popleft()
		if current == goal:
			break
		for nb in maze.neighbors(current):
			if nb in visited:
				continue
			visited.add(nb)
			came_from[nb] = current
			queue.append(nb)

	return _reconstruct_path(came_from, start, goal)


def dfs(maze: "Maze") -> List[Pos]:
	# DFS (Depth-First Search) iterativa com pilha.
	# Não garante caminho mínimo; segue profundidade respeitando ordem N,S,L,O.
	# Inserimos vizinhos em ordem reversa na pilha para explorar primeiro o Norte.
	start = maze.start()
	goal = maze.goal()
	if start == goal:
		return [start]

	stack: List[Pos] = [start]
	visited = {start}
	came_from: Dict[Pos, Pos] = {}

	while stack:
		current = stack.pop()
		if current == goal:
			break
		# Precisamos listar antes para poder reverter a ordem de push
		neighbors_list = list(maze.neighbors(current))
		# Reverte para que o primeiro da ordem original seja explorado primeiro ao usar pilha
		for nb in reversed(neighbors_list):
			if nb in visited:
				continue
			visited.add(nb)
			came_from[nb] = current
			stack.append(nb)

	return _reconstruct_path(came_from, start, goal)


__all__ = ["bfs", "dfs"]


def astar(maze: "Maze", h: Optional[Callable[[Pos, Pos], float]] = None) -> List[Pos]:
	# A* com fila de prioridade por f(n) = g(n) + h(n).
	# h padrão: distância Manhattan até o goal.
	# Retorna caminho do start ao goal; [] se falha.
	start = maze.start()
	goal = maze.goal()
	if start == goal:
		return [start]

	# Heurística (Manhattan) padrão
	try:
		from .heuristics import manhattan as default_h
	except Exception:
		# Fallback local se o import falhar por algum motivo
		def default_h(a: Pos, b: Pos) -> float:
			return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))
	heuristic = h or default_h

	# Estruturas
	open_heap: List[Tuple[int, int, Pos]] = []  # (f, tie, node)
	g_score: Dict[Pos, int] = {start: 0}
	came_from: Dict[Pos, Pos] = {}
	closed: set[Pos] = set()
	push_counter = count()

	start_f = heuristic(start, goal)
	heapq.heappush(open_heap, (start_f, next(push_counter), start))

	# Melhor f(n) conhecido para cada nó (para ignorar entradas obsoletas na heap)
	best_f: Dict[Pos, int] = {start: start_f}

	while open_heap:
		f_cur, _, current = heapq.heappop(open_heap)
		# Ignora entradas obsoletas
		if best_f.get(current, float('inf')) < f_cur:
			continue
		if current == goal:
			return _reconstruct_path(came_from, start, goal)
		closed.add(current)

		for nb in maze.neighbors(current):
			if nb in closed:
				continue
			step = maze.step_cost(current, nb)
			cand_g = g_score[current] + step
			if cand_g < g_score.get(nb, float('inf')):
				came_from[nb] = current
				g_score[nb] = cand_g
				f_nb = cand_g + heuristic(nb, goal)
				best_f[nb] = f_nb
				heapq.heappush(open_heap, (f_nb, next(push_counter), nb))

	# Falha: sem caminho
	return []


__all__ = ["bfs", "dfs", "astar"]

