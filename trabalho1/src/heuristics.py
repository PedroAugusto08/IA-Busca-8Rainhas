"""Heurísticas para busca informada em grade 4-direções (NSLO).

Funções:
- manhattan(a, b) -> int: |r1 - r2| + |c1 - c2|.
- euclidean(a, b) -> float: sqrt((r1 - r2)^2 + (c1 - c2)^2).

Notas:
- Em grid com custo de passo = 1, ambas são admissíveis e consistentes.
- Pos = tuple[int, int].
"""
from __future__ import annotations
from math import sqrt
from typing import Tuple

Pos = Tuple[int, int]


def manhattan(a: Pos, b: Pos) -> int:
    # Distância Manhattan entre duas posições da grade.
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a: Pos, b: Pos) -> float:
    # Distância Euclidiana entre duas posições da grade.
    dr = a[0] - b[0]
    dc = a[1] - b[1]
    return sqrt(dr * dr + dc * dc)


__all__ = ["manhattan", "euclidean"]
