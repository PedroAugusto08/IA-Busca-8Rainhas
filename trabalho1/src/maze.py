"""Maze

Formato de entrada (linhas no arquivo):
	[row,col]:NSLO  # Letra

Onde:
	- row, col começam em 0.
	- NSLO são 4 bits (Norte, Sul, Leste, Oeste) com semântica:
				1 = parede (movimento bloqueado naquela direção)
				0 = livre (movimento permitido se célula destino existe)
	- Comentário após '#' define a letra identificadora daquela célula (usada para visualização).
	- Linhas em branco e linhas iniciadas por '#' são ignoradas.
	- Linhas finais opcionais 'Start:[r,c]' e 'Goal:[r,c]' podem existir apenas para documentação;
		as posições de start e goal são FIXAS (Start=(4,0), Goal=(0,4)). Se declaradas e divergirem,
		gera erro.

Movimento:
	- neighbors() considera a máscara da célula de origem e produz vizinhos em ordem N,S,L,O
		somente onde o bit correspondente == 0 (livre) e dentro dos limites.
	- Não exige reciprocidade (se origem permite ir Leste, o destino não precisa permitir Oeste).

Passabilidade:
	- passable() retorna True se a célula possui ao menos um bit == 0 (tem alguma saída possível).

Renderização (render_path):
	- Sem caminho: imprime grade de letras (ou '.' se faltar letra, embora não esperado).
	- Com caminho: 'S' e 'G' sobrescrevem letras nas posições de início e fim, e 'o' nas demais
		posições do path.

Erros: ValueError para qualquer inconsistência (formato, máscara inválida, posição duplicada,
ausência de alguma célula do retângulo deduzido, declaração Start/Goal divergente).
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Iterator, Union, Dict

Pos = Tuple[int, int]


class Maze:
    START_POS: Pos = (4, 0)
    GOAL_POS: Pos = (0, 4)

    @classmethod
    def from_file(cls, path: Union[Path, str]) -> "Maze":
        # Lê o arquivo texto e converte para estruturas internas (máscaras e letras)
        # Valida formato e consistência do grid
        p = Path(path)
        if not p.is_file():
            raise ValueError(f"Arquivo não encontrado: {path}")
        with p.open('r', encoding='utf-8') as f:
            lines = [ln.rstrip('\n') for ln in f]

        body: List[str] = []
        start_decl = None
        goal_decl = None
        for ln in lines:
            stripped = ln.strip()
            if not stripped:
                # Ignora linhas em branco
                continue
            if stripped.startswith('#'):
                # Comentário puro é ignorado
                continue
            if stripped.startswith('Start:'):
                # Armazena declaração (para validar depois)
                start_decl = stripped
                continue
            if stripped.startswith('Goal:'):
                # Armazena declaração (para validar depois)
                goal_decl = stripped
                continue
            body.append(stripped)

        cells: Dict[Pos, Tuple[int,int,int,int]] = {}
        letters: Dict[Pos, str] = {}
        max_r = -1
        max_c = -1

        for line in body:
            try:
                left, *comment = line.split('#', 1)
                left = left.strip()
                letter = comment[0].strip() if comment else '.'
                # Formato esperado da parte principal: [r,c]:NSLO
                if not left.startswith('[') or ']' not in left or ':' not in left:
                    raise ValueError('Formato de célula inválido')
                coord_part, mask_part = left.split(':', 1)
                inside = coord_part[1:coord_part.index(']')]
                r_str, c_str = inside.split(',')
                r = int(r_str)
                c = int(c_str)
                mask_part = mask_part.strip()
                if len(mask_part) != 4 or any(ch not in '01' for ch in mask_part):
                    raise ValueError(f"Máscara inválida '{mask_part}' em {coord_part}")
                n, s, l, o = (int(b) for b in mask_part)
            except ValueError as e:
                raise ValueError(f"Linha inválida: '{line}' ({e})") from None

            pos = (r, c)
            if pos in cells:
                raise ValueError(f"Posição duplicada {pos}.")
            cells[pos] = (n, s, l, o)
            letters[pos] = letter if letter else '.'
            max_r = max(max_r, r)
            max_c = max(max_c, c)

        if max_r < 0:
            raise ValueError('Nenhuma célula encontrada.')

        height = max_r + 1
        width = max_c + 1
        for rr in range(height):
            for cc in range(width):
                if (rr, cc) not in cells:
                    # Se qualquer célula do retângulo deduzido estiver ausente -> erro
                    raise ValueError(f"Posição ausente no grid: ({rr},{cc}).")
                
		# Start e Goal são fixos, mas se declarados devem ser validados
        def parse_decl(decl: str) -> Pos:
            inside = decl.split(':',1)[1].strip()
            if not inside.startswith('[') or not inside.endswith(']'):
                raise ValueError(f"Declaração inválida: {decl}")
            inner = inside[1:-1]
            a,b = inner.split(',')
            return (int(a), int(b))

        if start_decl and parse_decl(start_decl) != cls.START_POS:
            raise ValueError('Start declarado não corresponde à posição fixa.')
        if goal_decl and parse_decl(goal_decl) != cls.GOAL_POS:
            raise ValueError('Goal declarado não corresponde à posição fixa.')

        return cls(height, width, cells, letters)

    def __init__(self, height: int, width: int, cells: Dict[Pos, Tuple[int,int,int,int]], letters: Dict[Pos,str]):
        # Monta matrizes internas de máscaras (bits) e letras indexadas por (r,c)
        self._height = height
        self._width = width
        self._masks: List[List[Tuple[int,int,int,int]]] = [
            [cells[(r,c)] for c in range(width)] for r in range(height)
        ]
        self._letters: List[List[str]] = [
            [letters[(r,c)] for c in range(width)] for r in range(height)
        ]
        self._start: Pos = self.START_POS
        self._goal: Pos = self.GOAL_POS
        if not self.in_bounds(self._start) or not self.in_bounds(self._goal):
            raise ValueError('Start ou Goal fora dos limites.')

    # API pública
    def start(self) -> Pos:
        return self._start

    def goal(self) -> Pos:
        return self._goal

    def in_bounds(self, pos: Pos) -> bool:
        # Verifica se (r,c) está dentro dos limites gerais do grid
        r,c = pos
        return 0 <= r < self._height and 0 <= c < self._width

    def passable(self, pos: Pos) -> bool:
        # Célula é considerada passável se tiver pelo menos uma direção livre (bit 0)
        n,s,l,o = self._masks[pos[0]][pos[1]]
        return (n==0) or (s==0) or (l==0) or (o==0)

    def neighbors(self, pos: Pos) -> Iterator[Pos]:
        # Gera vizinhos em ordem determinística N,S,L,O conforme bits livres
        r,c = pos
        n,s,l,o = self._masks[r][c]
        if n == 0 and r-1 >= 0:
            yield (r-1, c)
        if s == 0 and r+1 < self._height:
            yield (r+1, c)
        if l == 0 and c+1 < self._width:
            yield (r, c+1)
        if o == 0 and c-1 >= 0:
            yield (r, c-1)

    def step_cost(self, from_pos: Pos, to_pos: Pos) -> int:
        return 1

    def render_path(self, path: List[Pos]) -> str:
        # Cria uma cópia da grade de letras e sobrepõe marcações do caminho
        # 'S' e 'G' sobrescrevem suas posições, 'o' para cada passo intermediário
        out = [row[:] for row in self._letters]
        sr,sc = self._start
        gr,gc = self._goal
        out[sr][sc] = 'S'
        out[gr][gc] = 'G'
        for (r,c) in path:
            if not self.in_bounds((r,c)):
                raise ValueError(f"Posição fora dos limites no path: {r},{c}")
            if (r,c) not in (self._start, self._goal):
                out[r][c] = 'o'
        return '\n'.join(' '.join(ch for ch in row) for row in out)

    def __repr__(self) -> str:
        return f"MazeNSLO(height={self._height}, width={self._width}, start={self._start}, goal={self._goal})"

    def __str__(self) -> str:
        # Representação textual: mostra bits e letra (ex.: 1001:A)
        lines = []
        for r in range(self._height):
            parts = []
            for c in range(self._width):
                n,s,l,o = self._masks[r][c]
                letter = self._letters[r][c]
                parts.append(f"{n}{s}{l}{o}:{letter}")
            lines.append(' '.join(parts))
        return '\n'.join(lines)


if __name__ == '__main__': # Teste simples
    demo_file = Path(__file__).resolve().parents[1] / 'data' / 'labirinto.txt'
    try:
        m = Maze.from_file(demo_file)
        print('Maze carregado:')
        print(m)
        print('Start:', m.start(), 'Goal:', m.goal())
        print('Vizinhos Start:', list(m.neighbors(m.start())))
        print('Render vazio:\n' + m.render_path([]))
    except ValueError as e:
        print('Erro ao carregar maze:', e)
