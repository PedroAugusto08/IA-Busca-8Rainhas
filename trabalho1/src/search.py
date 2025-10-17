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

Campos de métricas: As funções também retornam métricas de desempenho.

Edge cases abordados:
	- Labirinto vazio: Maze.from_file já impede.
	- Start == Goal: retorno imediato.
	- Nenhum caminho: visita esgota fronteira e retorna [].
"""
from __future__ import annotations
from collections import deque
from typing import Dict, List, Tuple, Optional, Callable, TYPE_CHECKING, Union
import heapq
from itertools import count
from time import perf_counter
from dataclasses import dataclass

if TYPE_CHECKING:
	from .maze import Maze
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


class MetricsRecorder:
	#Utilitário para registrar métricas de busca de forma unificada.
	#Mantém a contagem de nós expandidos/gerados e os picos de estruturas (fronteira e explorados) e monta o SearchMetrics no final, preservando exatamente os valores esperados pelos algoritmos atuais.
	def __init__(
		self,
		algorithm: str,
		enabled: bool,
		compute_optimality: bool,
		*,
		initial_frontier: int = 0,
		initial_explored: int = 0,
	):
		self.algorithm = algorithm
		self.enabled = enabled
		self.compute_optimality = compute_optimality
		self.t0 = perf_counter() if enabled else 0.0
		self.expanded = 0
		self.generated = 0
		self.max_frontier = initial_frontier if enabled else 0
		self.max_explored = initial_explored if enabled else 0

	def inc_expanded(self) -> None:
		if self.enabled:
			self.expanded += 1

	def inc_generated(self) -> None:
		if self.enabled:
			self.generated += 1

	def track_frontier(self, size: int) -> None:
		if self.enabled and size > self.max_frontier:
			self.max_frontier = size

	def track_explored(self, size: int) -> None:
		if self.enabled and size > self.max_explored:
			self.max_explored = size

	def finalize(self, maze: "Maze", path: List[Pos]) -> "SearchMetrics":
		assert self.enabled, "finalize() chamado sem métricas habilitadas"
		t1 = perf_counter()
		found = len(path) > 0
		# Computa completude e optimalidade via oráculo BFS
		completeness, optimal = _eval_completeness_and_optimality(maze, path)
		return SearchMetrics(
			algorithm=self.algorithm,
			time_sec=t1 - self.t0,
			expanded=self.expanded,
			generated=self.generated,
			max_frontier=self.max_frontier,
			max_explored=self.max_explored,
			max_structures=self.max_frontier + self.max_explored,
			found=found,
			completeness=completeness,
			optimal=optimal,
			path_cost=max(0, len(path) - 1),
			path_len=len(path),
		)


def bfs(maze: "Maze", with_metrics: bool = False, compute_optimality: bool = False) -> Union[List[Pos], Tuple[List[Pos], "SearchMetrics"]]:
	# BFS (Breadth-First Search): garante menor número de passos.
	# Estruturas: fila (deque), conjunto visited, mapa came_from.
	start = maze.start()
	goal = maze.goal()
	rec = MetricsRecorder("BFS", with_metrics, compute_optimality, initial_frontier=1, initial_explored=1)
	if start == goal:
		path = [start]
		if not with_metrics:
			return path
		# Mantém métricas idênticas ao caso trivial anterior (frontier=1, explored=1)
		return path, rec.finalize(maze, path)

	queue = deque([start])
	visited = {start}
	came_from: Dict[Pos, Pos] = {}

	# Loop principal da BFS: processa a fila, checa objetivo, enfileira vizinhos não visitados e atualiza métricas
	while queue:
		current = queue.popleft()
		rec.inc_expanded()
		if current == goal:
			break
		for nb in maze.neighbors(current):
			if nb in visited:
				continue
			visited.add(nb)
			came_from[nb] = current
			queue.append(nb)
			rec.inc_generated()
			rec.track_frontier(len(queue))
			rec.track_explored(len(visited))

	# Falha ou sucesso: reconstruir
	path = _reconstruct_path(came_from, start, goal)
	if not with_metrics:
		return path
	return path, rec.finalize(maze, path)


def dfs(maze: "Maze", with_metrics: bool = False, compute_optimality: bool = False) -> Union[List[Pos], Tuple[List[Pos], "SearchMetrics"]]:
	# DFS (Depth-First Search) iterativa com pilha.
	# Não garante caminho mínimo; segue profundidade respeitando ordem N,S,L,O.
	# Vizinhos em ordem reversa na pilha para explorar primeiro o Norte.
	start = maze.start()
	goal = maze.goal()
	rec = MetricsRecorder("DFS", with_metrics, compute_optimality, initial_frontier=1, initial_explored=1)
	if start == goal:
		path = [start]
		if not with_metrics:
			return path
		return path, rec.finalize(maze, path)

	stack: List[Pos] = [start]
	visited = {start}
	came_from: Dict[Pos, Pos] = {}

	while stack:
		current = stack.pop()
		rec.inc_expanded()
		if current == goal:
			break
		# Precisa-se listar antes para poder reverter a ordem de push
		neighbors_list = list(maze.neighbors(current))
		# Reverte para que o primeiro da ordem original seja explorado primeiro ao usar pilha
		for nb in reversed(neighbors_list):
			if nb in visited:
				continue
			visited.add(nb)
			came_from[nb] = current
			stack.append(nb)
			rec.inc_generated()
			rec.track_frontier(len(stack))
			rec.track_explored(len(visited))

	# Falha ou sucesso: reconstruir
	path = _reconstruct_path(came_from, start, goal)
	if not with_metrics:
		return path
	return path, rec.finalize(maze, path)


__all__ = ["bfs", "dfs"]


def astar(maze: "Maze", h: Optional[Callable[[Pos, Pos], float]] = None, with_metrics: bool = False, compute_optimality: bool = False) -> Union[List[Pos], Tuple[List[Pos], "SearchMetrics"]]:
	# A* com fila de prioridade por f(n) = g(n) + h(n).
	# h padrão: distância Manhattan até o goal.
	# Retorna caminho do start ao goal; [] se falha.
	start = maze.start()
	goal = maze.goal()
	rec = MetricsRecorder("A*", with_metrics, compute_optimality, initial_frontier=1, initial_explored=0)
	if start == goal:
		path = [start]
		if not with_metrics:
			return path
		return path, rec.finalize(maze, path)

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
	# contadores via recorder; max_frontier inicia em 1, explored em 0

	start_f = heuristic(start, goal)
	heapq.heappush(open_heap, (start_f, next(push_counter), start))

	# Melhor f(n) conhecido para cada nó (para ignorar entradas obsoletas na heap)
	best_f: Dict[Pos, int] = {start: start_f}

	while open_heap:
		f_cur, _, current = heapq.heappop(open_heap)
		# Ignora entradas obsoletas
		if best_f.get(current, float('inf')) < f_cur:
			continue
		rec.inc_expanded()
		if current == goal:
			break
		closed.add(current)
		rec.track_explored(len(closed))

		# Explora vizinhos com base apenas na heurística: se h melhora, atualiza came_from e insere na fronteira (heap)
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
				rec.inc_generated()
				rec.track_frontier(len(open_heap))

	# Falha ou sucesso: reconstruir
	path = _reconstruct_path(came_from, start, goal)
	if not with_metrics:
		return path
	return path, rec.finalize(maze, path)


__all__ = ["bfs", "dfs", "astar"]


def greedy_best_first(maze: "Maze", h: Optional[Callable[[Pos, Pos], float]] = None, with_metrics: bool = False, compute_optimality: bool = False) -> Union[List[Pos], Tuple[List[Pos], "SearchMetrics"]]:
	# Greedy Best-First Search: fronteira ordenada apenas por h(n).
	# Não considera g(n); não garante ótimo e pode ficar preso em becos mais facilmente.
	start = maze.start()
	goal = maze.goal()
	rec = MetricsRecorder("Greedy", with_metrics, compute_optimality, initial_frontier=1, initial_explored=0)
	if start == goal:
		path = [start]
		if not with_metrics:
			return path
		return path, rec.finalize(maze, path)

	# Heurística padrão (Manhattan)
	try:
		from .heuristics import manhattan as default_h
	except Exception:
		def default_h(a: Pos, b: Pos) -> float:
			return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))
	heuristic = h or default_h

	open_heap: List[Tuple[float, int, Pos]] = []  # (h, tie, node)
	came_from: Dict[Pos, Pos] = {}
	visited: set[Pos] = set()
	push_counter = count()
	# contadores via recorder; max_frontier inicia em 1, explored em 0

	start_h = heuristic(start, goal)
	heapq.heappush(open_heap, (start_h, next(push_counter), start))

	best_h: Dict[Pos, float] = {start: start_h}

	while open_heap:
		cur_h, _, current = heapq.heappop(open_heap)
		# Ignora entradas obsoletas
		if best_h.get(current, float('inf')) < cur_h:
			continue
		rec.inc_expanded()
		if current == goal:
			break
		visited.add(current)
		rec.track_explored(len(visited))

		# Explora vizinhos com base apenas na heurística: se h melhora, atualiza came_from e insere na fronteira (heap)
		for nb in maze.neighbors(current):
			if nb in visited:
				continue
			new_h = heuristic(nb, goal)
			if new_h < best_h.get(nb, float('inf')):
				best_h[nb] = new_h
				came_from[nb] = current
				heapq.heappush(open_heap, (new_h, next(push_counter), nb))
				rec.inc_generated()
				rec.track_frontier(len(open_heap))

	# Falha ou sucesso: reconstruir
	path = _reconstruct_path(came_from, start, goal)
	if not with_metrics:
		return path
	return path, rec.finalize(maze, path)


__all__ = ["bfs", "dfs", "astar", "greedy_best_first"]


# ===================== Métricas de desempenho =====================

@dataclass
class SearchMetrics:
	algorithm: str
	time_sec: float
	expanded: int
	generated: int
	max_frontier: int
	max_explored: int
	max_structures: int
	found: bool
	completeness: Optional[bool]
	optimal: Optional[bool]
	path_cost: int
	path_len: int


def _eval_completeness_and_optimality(maze: "Maze", path: List[Pos]) -> Tuple[Optional[bool], Optional[bool]]:
	# Usa BFS como oráculo para verificar se solução existe e se custo é mínimo (custos = 1).
	oracle = bfs(maze)
	solution_exists = len(oracle) > 0
	found = len(path) > 0
	completeness = (not solution_exists and not found) or (solution_exists and found)
	if not solution_exists or not found:
		return completeness, None
	# custo uniforme: custo = len(path) - 1
	return completeness, (len(path) - 1) == (len(oracle) - 1)


__all__ = ["bfs", "dfs", "astar", "greedy_best_first"]

