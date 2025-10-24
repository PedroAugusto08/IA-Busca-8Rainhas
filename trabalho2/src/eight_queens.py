"""Problema das 8 Rainhas — representação e utilitários básicos.

Inclui:
- Representação: board[c] = linha (0..n-1) da rainha na coluna c (0..n-1).
- Estado inicial: initial_board(n) -> lista aleatória de linhas (random.seed(42)).
- Conflitos: conflicts(board) retorna número de pares de rainhas em conflito.
    Conflitos ocorrem quando duas rainhas estão na mesma linha ou na mesma diagonal
    (|Δcol| == |Δlin|).
- Vizinhança: neighbors(board) gera movimentos movendo uma única rainha para outra
    linha na mesma coluna; retorna pares (coluna, nova_linha) para linhas 0..n-1
    exceto a linha atual.
- Aplicação de movimento: apply(board, mv) retorna um novo tabuleiro com a rainha
    movida; não altera o original.

Notas:
- Tipos: Move = (coluna, nova_linha); Board = List[int].
- random.seed(42) no runner para reprodutibilidade.
"""

# eight_queens_representation.py
# Representacao: board[c] = linha (0..7) da rainha na coluna c(0..7)
from typing import List, Iterable, Tuple
import random

Move = Tuple[int, int] # (coluna, nova_linha)

Board = List[int]

# Cria um tabuleiro aleatório de tamanho n.
def initial_board(n: int) -> List[int]:
    # random.seed(42) -> não definir seed aqui, fixar no runner
    return [random.randrange(n) for _ in range(n)]

def conflicts(board: List[int]) -> int:
    # Calcula o número de pares de rainhas em conflito.
    # Retorna o número de pares (i < j) em conflito. Solução válida -> 0.
    n = len(board)
    confl = 0
    for c1 in range(n):
        r1 = board[c1]
        for c2 in range(c1 + 1, n):
            r2 = board[c2]
            if r1 == r2 or abs(c1 - c2) == abs(r1 - r2):
                confl += 1
    return confl

def neighbors(board: List[int]) -> Iterable[Move]:
    # Gera movimentos de vizinhança.
    n = len(board)
    for c in range(n):
        current_row = board[c]
        for new_row in range(n):
            if new_row != current_row:
                yield (c, new_row)

def apply(board: List[int], mv: Move) -> List[int]:
    # Aplica o movimento (coluna, nova_linha) e retorna um novo tabuleiro.
    # Não modifica o tabuleiro original.
    c, r = mv
    newb = board.copy()
    newb[c] = r
    return newb

# Runner simples
if __name__ == "__main__":
    n = 8
    random.seed(42)
    board = initial_board(n)
    print("Board inicial:", board, "Conflitos:", conflicts(board))