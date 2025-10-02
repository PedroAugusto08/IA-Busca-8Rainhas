"""Maze

Cada célula é representada por um token de 4 bits (N,S,E,W) opcionalmente seguido
por 'S' (start) ou 'G' (goal). Ex: 1010, 1111S, 0101G. Apenas este formato é aceito.

Regras:
  - Todas as linhas devem ter o mesmo número de tokens (grid retangular).
  - Bits: '1' significa movimento permitido NAQUELA direção a partir da célula.
  - neighbors() considera apenas a máscara da célula de origem (não checa reciprocidade).
  - passable(): True se houver pelo menos um bit 1 (não totalmente bloqueada).
  - Exatamente um token com S e um token com G devem existir.
  - Erros levantam ValueError com mensagens claras.

Renderização (render_path):
  - '.' para células normais não no caminho
  - 'o' para células no caminho (exceto start/goal)
  - 'S' e 'G' nas posições respectivas

"""
from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Iterator, Union

Pos = Tuple[int, int]

_DIRS = [(-1, 0), (1, 0), (0, 1), (0, -1)]  # N, S, E, W (ordem fixa)


class Maze:
	"""Labirinto baseado em máscaras de adjacência (4 bits N,S,E,W)."""

	@classmethod
	def from_file(cls, path: Union[Path, str]) -> "Maze":
		p = Path(path)
		if not p.is_file():
			raise ValueError(f"Arquivo não encontrado: {path}")

		with p.open("r", encoding="utf-8") as f:
			raw_lines = [ln.rstrip("\n") for ln in f]

		# Remove linhas externas vazias
		while raw_lines and not raw_lines[0].strip():
			raw_lines.pop(0)
		while raw_lines and not raw_lines[-1].strip():
			raw_lines.pop()

		if not raw_lines:
			raise ValueError("Arquivo vazio ou somente linhas em branco.")

		# Tokenização por espaço
		token_lines: List[List[str]] = []
		for line in raw_lines:
			if not line.strip():
				continue
			tokens = line.strip().split()
			token_lines.append(tokens)

		# Valida retangularidade (mesmo número de tokens por linha)
		width_set = {len(tl) for tl in token_lines}
		if len(width_set) != 1:
			raise ValueError("Linhas com número de tokens diferentes (grid não retangular).")

		return cls(token_lines)

	def __init__(self, tokens_grid: List[List[str]]):

		if not tokens_grid:
			raise ValueError("Grid vazio.")

		self._height = len(tokens_grid)
		self._width = len(tokens_grid[0])

		# Estrutura: armazenar uma matriz de listas [n,s,e,w] ints (0/1)
		self._masks: List[List[Tuple[int, int, int, int]]] = []
		start_pos: Pos | None = None
		goal_pos: Pos | None = None
		s_count = 0
		g_count = 0

		for r, row_tokens in enumerate(tokens_grid):
			if len(row_tokens) != self._width:
				raise ValueError("Inconsistência de largura detectada durante parsing.")
			row_masks: List[Tuple[int, int, int, int]] = []
			for c, token in enumerate(row_tokens):
				# Token base: primeiros 4 chars devem ser 0/1
				if len(token) < 4:
					raise ValueError(f"Token inválido (menos de 4 chars) '{token}' em ({r},{c}).")
				base = token[:4]
				if any(ch not in '01' for ch in base):
					raise ValueError(f"Token contém bit inválido '{token}' em ({r},{c}).")
				flags = token[4:]  # sufixo pode estar vazio ou conter S/G

				# Analisa sufixo
				if flags:
					# Não permitir caracteres diferentes de S/G ou repetição
					for ch in flags:
						if ch not in 'SG':
							raise ValueError(f"Sufixo inválido '{flags}' em token '{token}' ({r},{c}).")
					if 'S' in flags:
						s_count += 1
						if start_pos is None:
							start_pos = (r, c)
					if 'G' in flags:
						g_count += 1
						if goal_pos is None:
							goal_pos = (r, c)
					# Impedir múltiplos S ou G no mesmo token (ex: 1111SS)
					if flags.count('S') > 1 or flags.count('G') > 1:
						raise ValueError(f"Sufixo repetido em token '{token}' ({r},{c}).")

				n, s, e, w = (int(b) for b in base)
				row_masks.append((n, s, e, w))
			self._masks.append(row_masks)

		if s_count != 1 or g_count != 1 or start_pos is None or goal_pos is None:
			raise ValueError(f"Esperado exatamente um S e um G; encontrados S={s_count}, G={g_count}.")

		self._start: Pos = start_pos  # type: ignore[assignment]
		self._goal: Pos = goal_pos    # type: ignore[assignment]

	# ------------------- API pública -------------------
	def start(self) -> Pos:
		# Retorna posição start (linha,coluna).
		return self._start

	def goal(self) -> Pos:
		# Retorna posição goal (linha,coluna).
		return self._goal

	def in_bounds(self, pos: Pos) -> bool:
		# True se a posição está dentro dos limites.
		r, c = pos
		return 0 <= r < self._height and 0 <= c < self._width

	def passable(self, pos: Pos) -> bool:
		# True se a célula tem ao menos um movimento permitido (não bloqueada).
		r, c = pos
		n, s, e, w = self._masks[r][c]
		return (n + s + e + w) > 0

	def neighbors(self, pos: Pos) -> Iterator[Pos]:
		# Itera vizinhos permitidos pela máscara da célula de origem na ordem N,S,E,W.
		r, c = pos
		n, s, e, w = self._masks[r][c]
		# N
		if n and r - 1 >= 0:
			yield (r - 1, c)
		# S
		if s and r + 1 < self._height:
			yield (r + 1, c)
		# E
		if e and c + 1 < self._width:
			yield (r, c + 1)
		# W
		if w and c - 1 >= 0:
			yield (r, c - 1)

	def step_cost(self, from_pos: Pos, to_pos: Pos) -> int:
		# Custo uniforme de movimento (sempre 1).
		return 1

	def render_path(self, path: List[Pos]) -> str:
		# Gera string visual com S, G, 'o' no caminho e '.' demais células.
		# Matriz base de '.'
		out = [['.' for _ in range(self._width)] for _ in range(self._height)]
		sr, sc = self._start
		gr, gc = self._goal
		out[sr][sc] = 'S'
		out[gr][gc] = 'G'

		for (r, c) in path:
			if not self.in_bounds((r, c)):
				raise ValueError(f"Path inválido: posição ({r},{c}) fora dos limites.")
			if (r, c) not in (self._start, self._goal):
				out[r][c] = 'o'

		return "\n".join("".join(row) for row in out)

	# ------------------- Representações -------------------
	def __repr__(self) -> str:
		return f"MazeAdj(height={self._height}, width={self._width}, start={self._start}, goal={self._goal})"

	def __str__(self) -> str:
		# Exibe apenas a máscara base (sem S/G) para inspeção rápida
		lines = []
		for r in range(self._height):
			row_parts = []
			for c in range(self._width):
				n, s, e, w = self._masks[r][c]
				base = f"{n}{s}{e}{w}"
				if (r, c) == self._start:
					base += 'S'
				if (r, c) == self._goal:
					base += 'G'
				row_parts.append(base)
			lines.append(" ".join(row_parts))
		return "\n".join(lines)


if __name__ == "__main__":  # Demo simples
	demo_file = Path(__file__).resolve().parents[1] / 'data' / 'labirinto.txt'
	if demo_file.exists():
		try:
			m = Maze.from_file(demo_file)
			print("Labirinto carregado:")
			print(m)
			print("Start:", m.start(), "Goal:", m.goal())
			print("Vizinhos de start:", list(m.neighbors(m.start())))
			print("Render vazio:\n", m.render_path([]))
		except ValueError as e:
			print("Erro:", e)
	else:
		print("Arquivo de demo não encontrado:", demo_file)
