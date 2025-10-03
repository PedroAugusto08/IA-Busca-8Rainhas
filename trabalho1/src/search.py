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
from typing import Dict, List, Tuple, Iterable

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


def bfs(maze) -> List[Pos]:
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


def dfs(maze) -> List[Pos]:
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

