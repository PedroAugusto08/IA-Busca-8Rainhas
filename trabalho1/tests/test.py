# Runner CLI simples para BFS/DFS/A*/Gulosa no labirinto NSLO.
# Ajusta sys.path para permitir execução direta sem configurar pacotes.

import sys
from pathlib import Path

# Garante que a raiz do repositório esteja no sys.path (2 níveis acima de trabalho1/tests/)
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse
import random
from typing import Callable, List, Tuple
# Fixar semente para reprodutibilidade em execuções de teste
random.seed(42)

from trabalho1.src.maze import Maze
from trabalho1.src.search import (
    bfs,
    dfs,
    astar,
    greedy_best_first,
)
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
    parser.add_argument("--algo", type=str, default="all", choices=["all", "bfs", "dfs", "astar", "greedy"],
                        help="Algoritmo de busca (padrão: all)")
    parser.add_argument("--heuristic", type=str, default="manhattan",
                        help="Heurística (manhattan | euclidean | zero). Usada em A* e Gulosa.")
    parser.add_argument("--no-render", action="store_true", help="Não imprimir o labirinto renderizado com o caminho.")
    parser.add_argument("--print-coords", action="store_true", help="Imprimir a lista de coordenadas do caminho.")
    parser.add_argument("--stats", action="store_true", help="Imprimir métricas de desempenho (tempo, memória, nós, etc.).")
    parser.add_argument("--out", type=str, default=None, help="Arquivo .txt para salvar a tabela quando --algo=all (padrão: tests/metrics.txt)")
    args = parser.parse_args()

    maze_path = Path(args.maze) if args.maze else _load_default_maze_path()
    mz = Maze.from_file(maze_path)

    algo = args.algo.lower()
    path: List[Pos]

    def _bool_str(v: bool | None) -> str:
        return "sim" if v is True else ("não" if v is False else "-")

    def _format_table(rows: List[dict]) -> str:
        headers = [
            "Algoritmo", "Heurística", "Tempo(ms)", "Expandidos", "Gerados",
            "Pico", "Fronteira", "Explorados", "Completo", "Ótimo", "Custo", "Tam", "Caminho"
        ]
        data = []
        for r in rows:
            m = r["metrics"]
            data.append([
                r["name"],
                r["heur"],
                f"{m.time_sec*1000:.3f}",
                f"{m.expanded}",
                f"{m.generated}",
                f"{m.max_structures}",
                f"{m.max_frontier}",
                f"{m.max_explored}",
                _bool_str(m.completeness),
                _bool_str(m.optimal),
                f"{m.path_cost}",
                f"{m.path_len}",
                r.get("path_str", "-"),
            ])
        # calcular larguras
        widths = [len(h) for h in headers]
        for row in data:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))
        # montar
        def fmt_row(cols: List[str]) -> str:
            return " | ".join(c.ljust(widths[i]) for i, c in enumerate(cols))
        sep = "-+-".join("-" * w for w in widths)
        lines = [fmt_row(headers), sep]
        for row in data:
            lines.append(fmt_row(row))
        return "\n".join(lines)

    def _labels_sequence(mz: Maze, path: List[Pos]) -> str:
        if not path:
            return "-"
        labels: List[str] = []
        s, g = mz.start(), mz.goal()
        for pos in path:
            ch = mz.label_at(pos)
            if pos == s:
                labels.append(f"{ch}(S)")
            elif pos == g:
                labels.append(f"{ch}(G)")
            else:
                labels.append(ch)
        return " -> ".join(labels)

    if algo == "all":
        # Executa todos os algoritmos e gera tabela
        rows: List[dict] = []

        # BFS
        p_bfs, m_bfs = bfs(mz, with_metrics=True, compute_optimality=args.stats)
        rows.append({"name": "BFS", "heur": "-", "metrics": m_bfs, "path_str": _labels_sequence(mz, p_bfs)})

        # DFS
        p_dfs, m_dfs = dfs(mz, with_metrics=True, compute_optimality=args.stats)
        rows.append({"name": "DFS", "heur": "-", "metrics": m_dfs, "path_str": _labels_sequence(mz, p_dfs)})

        # A* e Greedy com múltiplas heurísticas (ordem pedida)
        heur_list = [
            ("Manhattan", _get_heuristic("manhattan")),
            ("Euclidiana", _get_heuristic("euclidean")),
        ]
        # Primeiro todas as linhas de A*
        for heur_name, h in heur_list:
            p_as, m_as = astar(mz, h=h, with_metrics=True, compute_optimality=args.stats)
            rows.append({"name": "A*", "heur": heur_name, "metrics": m_as, "path_str": _labels_sequence(mz, p_as)})
        # Depois todas as linhas de Greedy
        for heur_name, h in heur_list:
            p_gr, m_gr = greedy_best_first(mz, h=h, with_metrics=True, compute_optimality=args.stats)
            rows.append({"name": "Greedy", "heur": heur_name, "metrics": m_gr, "path_str": _labels_sequence(mz, p_gr)})

        table = _format_table(rows)
        # caminho padrão do arquivo: trabalho1/metrics/metrics.txt
        metrics_dir = Path(__file__).resolve().parents[1] / "metrics"
        try:
            metrics_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        out_path = Path(args.out) if args.out else (metrics_dir / "metrics.txt")
        try:
            out_path.write_text(table + "\n", encoding="utf-8")
            print(f"Tabela de métricas salva em: {out_path}")
        except Exception as e:
            print("Falha ao salvar a tabela:", e)
        # Não imprime a tabela no stdout quando --algo=all (apenas salva em arquivo)
        return 0

    metrics = None
    if algo == "bfs":
        path, metrics = bfs(mz, with_metrics=True, compute_optimality=args.stats) if args.stats else (bfs(mz), None)
        heur_name = "-"
    elif algo == "dfs":
        path, metrics = dfs(mz, with_metrics=True, compute_optimality=args.stats) if args.stats else (dfs(mz), None)
        heur_name = "-"
    elif algo == "astar":
        h = _get_heuristic(args.heuristic)
        path, metrics = astar(mz, h=h, with_metrics=True, compute_optimality=args.stats) if args.stats else (astar(mz, h=h), None)
        heur_name = args.heuristic
    else:  # greedy
        h = _get_heuristic(args.heuristic)
        path, metrics = greedy_best_first(mz, h=h, with_metrics=True, compute_optimality=args.stats) if args.stats else (greedy_best_first(mz, h=h), None)
        heur_name = args.heuristic

    print(f"Arquivo: {maze_path}")
    print(f"Algoritmo: {algo.upper()}  |  Heurística: {heur_name}")
    if path:
        custo = len(path) - 1  # custo uniforme (step_cost=1 por passo)
        print(f"Caminho encontrado com {len(path)} estados, custo = {custo}")
        if metrics is not None:
            print("-" * 60)
            print("Métricas:")
            print(f"  Tempo:            {metrics.time_sec*1000:.3f} ms")
            print(f"  Nós expandidos:   {metrics.expanded}")
            print(f"  Nós gerados:      {metrics.generated}")
            print(f"  Memória (pico):   {metrics.max_structures}  "
                  f"(fronteira={metrics.max_frontier}, explorados={metrics.max_explored})")
            comp = "sim" if metrics.completeness is True else ("não" if metrics.completeness is False else "-")
            opt = "sim" if metrics.optimal is True else ("não" if metrics.optimal is False else "-")
            print(f"  Completude:       {comp}")
            print(f"  Optimalidade:     {opt}")
            print(f"  Custo do caminho: {metrics.path_cost}")
            print(f"  Tamanho caminho:  {metrics.path_len}")
            print("-" * 60)
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