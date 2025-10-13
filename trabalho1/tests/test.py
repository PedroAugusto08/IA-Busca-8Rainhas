# Runner CLI simples para BFS/DFS/A*/Gulosa no labirinto NSLO.
# Ajusta sys.path para permitir execução direta sem configurar pacotes.

import sys
from pathlib import Path

# Garante que a raiz do repositório esteja no sys.path (2 níveis acima de trabalho1/tests/)
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse
from typing import Callable, List, Tuple

from trabalho1.src.maze import Maze
from trabalho1.src.search import bfs, dfs, astar, greedy_best_first
from trabalho1.src.heuristics import manhattan as h_manhattan, euclidean as h_euclidean

Pos = Tuple[int, int]

def _load_default_maze_path() -> Path:
    # Resolve trabalho1/data/labirinto.txt a partir deste arquivo
    base = Path(__file__).resolve().parents[1]  # .../trabalho1
    return base / "data" / "labirinto.txt"

def _get_heuristic(name: str) -> Callable[[Pos, Pos], float]:
    name = name.lower()
    if name in ("manhattan", "manh", "m"):
        return h_manhattan
    if name in ("euclidean", "eucl", "e"):
        return h_euclidean
    if name in ("zero", "none"):
        return lambda a, b: 0.0
    raise ValueError(f"Heurística inválida: {name}. Use: manhattan | euclidean | zero")

def main() -> int:
    parser = argparse.ArgumentParser(description="Runner CLI para buscas no labirinto NSLO (BFS/DFS/A*/Gulosa).")
    parser.add_argument("--maze", type=str, default=None, help="Caminho do labirinto (padrão: trabalho1/data/labirinto.txt)")
    parser.add_argument("--algo", type=str, default="astar", choices=["bfs", "dfs", "astar", "greedy"],
                        help="Algoritmo de busca (padrão: astar)")
    parser.add_argument("--heuristic", type=str, default="manhattan",
                        help="Heurística (manhattan | euclidean | zero). Usada em A* e Gulosa.")
    parser.add_argument("--no-render", action="store_true", help="Não imprimir o labirinto renderizado com o caminho.")
    parser.add_argument("--print-coords", action="store_true", help="Imprimir a lista de coordenadas do caminho.")
    args = parser.parse_args()

    maze_path = Path(args.maze) if args.maze else _load_default_maze_path()
    mz = Maze.from_file(maze_path)

    algo = args.algo.lower()
    path: List[Pos]

    if algo == "bfs":
        path = bfs(mz)
        heur_name = "-"
    elif algo == "dfs":
        path = dfs(mz)
        heur_name = "-"
    elif algo == "astar":
        h = _get_heuristic(args.heuristic)
        path = astar(mz, h=h)
        heur_name = args.heuristic
    else:  # greedy
        h = _get_heuristic(args.heuristic)
        path = greedy_best_first(mz, h=h)
        heur_name = args.heuristic

    print(f"Arquivo: {maze_path}")
    print(f"Algoritmo: {algo.upper()}  |  Heurística: {heur_name}")
    if path:
        custo = len(path) - 1  # custo uniforme (step_cost=1 por passo)
        print(f"Caminho encontrado com {len(path)} estados, custo = {custo}")
        # Imprime sequência de letras: U(S) -> V -> Q -> ... -> E(G)
        labels: List[str] = []
        for i, pos in enumerate(path):
            ch = mz.label_at(pos)
            if pos == mz.start():
                labels.append(f"{ch}(S)")
            elif pos == mz.goal():
                labels.append(f"{ch}(G)")
            else:
                labels.append(ch)
        print("Sequência:", " -> ".join(labels))
        if args.print_coords:
            print("Coordenadas:", path)
        if not args.no_render:
            print("\nRenderização:\n")
            print(mz.render_path(path))
    else:
        print("Sem caminho encontrado.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())