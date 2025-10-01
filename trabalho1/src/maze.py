from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Iterator

Pos = Tuple[int, int]  # (row, col)

VALID_CHARS = {"S", "G", "#", "."}
_NEIGHBOR_DELTAS = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # UP, RIGHT, DOWN, LEFT


class Maze:
	# Representa um labirinto retangular para algoritmos de busca.
	# Mantém grid original e posições de S (start) e G (goal).

	# ---------------------------------------------------------------------
	# Fábrica
	# ---------------------------------------------------------------------
	@classmethod
	def from_file(cls, path: str) -> "Maze":
		# Lê, normaliza e valida um labirinto a partir de um arquivo texto.
		# Retorna uma instância pronta para uso ou lança ValueError.
		p = Path(path)
		if not p.is_file():  # Erro cedo e claro
			raise ValueError(f"Arquivo não encontrado: {path}")
		with p.open("r", encoding="utf-8") as f:
			raw_lines = [ln.rstrip("\n") for ln in f]

		# Remove linhas vazias no início e fim
		while raw_lines and not raw_lines[0].strip():
			raw_lines.pop(0)
		while raw_lines and not raw_lines[-1].strip():
			raw_lines.pop()

		# Normalização: remover whitespace de cauda de cada linha
		processed: List[str] = [ln.rstrip() for ln in raw_lines if ln.strip()]

		if not processed:
			raise ValueError("Labirinto inválido: arquivo vazio ou somente linhas em branco.")

		return cls(processed)

	# ---------------------------------------------------------------------
	# Inicialização / Validação
	# ---------------------------------------------------------------------
	def __init__(self, grid: List[str]):
		# Constrói o Maze a partir de uma lista de linhas já carregadas.
		# Faz cópia defensiva e valida estrutura + caracteres.
		if not grid:
			raise ValueError("Labirinto inválido: grid vazio.")

		# Garantir que não há linhas vazias internas e uniformidade de largura
		width = len(grid[0])
		for idx, line in enumerate(grid):
			if len(line) != width:
				raise ValueError(
					f"Labirinto inválido: linhas com comprimentos diferentes (linha {idx} tem {len(line)}, esperado {width})."
				)
			if not line:
				raise ValueError(f"Labirinto inválido: linha {idx} vazia.")

		self._grid: List[str] = list(grid)  # cópia defensiva
		self._height = len(self._grid)
		self._width = width

		s_count = 0
		g_count = 0
		s_pos: Pos | None = None
		g_pos: Pos | None = None

		for r, line in enumerate(self._grid):
			for c, ch in enumerate(line):
				if ch not in VALID_CHARS:
					raise ValueError(
						f"Labirinto inválido: caractere inválido '{ch}' em (linha {r}, coluna {c})."
					)
				if ch == "S":
					s_count += 1
					if s_pos is None:
						s_pos = (r, c)
				elif ch == "G":
					g_count += 1
					if g_pos is None:
						g_pos = (r, c)

		if s_count != 1 or g_count != 1:
			raise ValueError(
				f"Labirinto inválido: esperado exatamente um 'S' e um 'G'; encontrados S={s_count}, G={g_count}."
			)

		# Atribuição final das posições (não-nulas garantidas pelo check acima)
		self._start: Pos = s_pos
		self._goal: Pos = g_pos

	# ---------------------------------------------------------------------
	# Propriedades básicas
	# ---------------------------------------------------------------------
	def height(self) -> int:
		# Altura total (número de linhas)
		return self._height

	def width(self) -> int:
		# Largura total (número de colunas)
		return self._width

	def start(self) -> Pos:
		# Posição onde está o 'S'
		return self._start

	def goal(self) -> Pos:
		# Posição onde está o 'G'
		return self._goal

	# ---------------------------------------------------------------------
	# Validações de posição / acessibilidade
	# ---------------------------------------------------------------------
	def in_bounds(self, pos: Pos) -> bool:
		# Verifica se (row,col) está dentro dos limites
		r, c = pos
		return 0 <= r < self._height and 0 <= c < self._width

	def passable(self, pos: Pos) -> bool:
		# Retorna True se não for parede '#'
		# Pré-condição: pos já deve estar dentro dos limites
		r, c = pos
		return self._grid[r][c] != "#"

	# ---------------------------------------------------------------------
	# Geração de vizinhos
	# ---------------------------------------------------------------------
	def neighbors(self, pos: Pos) -> Iterator[Pos]:
		# Gera vizinhos livres na ordem: UP, RIGHT, DOWN, LEFT
		# Ignora posições fora ou paredes
		r, c = pos
		for dr, dc in _NEIGHBOR_DELTAS:
			nr, nc = r + dr, c + dc
			npos = (nr, nc)
			if self.in_bounds(npos) and self.passable(npos):
				yield npos

	# ---------------------------------------------------------------------
	# Custo de passo
	# ---------------------------------------------------------------------
	def step_cost(self, from_pos: Pos, to_pos: Pos) -> int:
		# Custo uniforme de um passo
		return 1

	# ---------------------------------------------------------------------
	# Renderização de caminho
	# ---------------------------------------------------------------------
	def render_path(self, path: List[Pos]) -> str:
		# Desenha uma versão do labirinto com o caminho marcado por 'o'
		# Mantém S e G intactos. Valida cada posição do caminho.
		if not path:
			return str(self)

		# Cópia mutável
		matrix = [list(line) for line in self._grid]

		for (r, c) in path:
			if not self.in_bounds((r, c)):
				raise ValueError(f"Path inválido: posição ({r},{c}) fora dos limites.")
			if not self.passable((r, c)) and (r, c) not in (self._start, self._goal):
				raise ValueError(f"Path inválido: posição ({r},{c}) é parede.")
			if (r, c) != self._start and (r, c) != self._goal:
				matrix[r][c] = 'o'

		return "\n".join("".join(row) for row in matrix)

	# ---------------------------------------------------------------------
	# Representações
	# ---------------------------------------------------------------------
	def __repr__(self) -> str:
		# Representação útil para debug/logging
		return f"Maze(height={self._height}, width={self._width}, start={self._start}, goal={self._goal})"

	def __str__(self) -> str:  # Exibe o grid
		return "\n".join(self._grid)


if __name__ == "__main__":  # Demonstração mínima
	demo_path = Path(__file__).resolve().parents[1] / "data" / "labirinto.txt"
	try:
		mz = Maze.from_file(str(demo_path))
		print("[DEMO] Maze carregado:")
		print(mz)
		print("Start:", mz.start(), "Goal:", mz.goal())
		# Exemplo de render sem caminho
		print("\n[DEMO] Render sem caminho:")
		print(mz.render_path([]))
	except ValueError as e:
		print("Erro ao carregar maze de demonstração:", e)
