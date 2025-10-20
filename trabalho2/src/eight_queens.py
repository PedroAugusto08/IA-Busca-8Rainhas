# eight_queens_representation.py
# Representacao: board[c] = linha (0..7) da rainha na coluna c(0..7)
from typing import List, Iterable, Tuple
import random

Move = Tuple[int, int] # (coluna, nova_linha)

# Cria um tabuleiro aleatório com base na seed:
def initial_board(Board, N):
    random.seed(42)
    Board = [random.randint(0, 7) for _ in range(N)]
    print(Board)
    return Board

""""
(AINDA INCOMPLETO)
def conflicts(Board):
    confl = 0
    for i in range(8):
        for j in range(8):
            if Board[i] == Board[j]:
                confl += 1
    print(confl)
"""

# MAIN:
N = 8
Board = List[int]
Board = initial_board(Board, N)