# Runner CLI simples para BFS/DFS/A*/Gulosa no labirinto NSLO.
# Ajusta sys.path para permitir execução direta sem configurar pacotes.

import sys
from pathlib import Path

# Garante que a raiz do repositório esteja no sys.path
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
    base = Path(__file__).resolve().parents[1]
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
    # Parser de argumentos CLI
    parser = argparse.ArgumentParser(description="Runner CLI - executa BFS, DFS, A* (Manhattan/Euclidiana) e Greedy (Manhattan/Euclidiana) e salva métricas em tabela.")
    parser.add_argument("--maze", type=str, default=None, help="Caminho do labirinto (padrão: trabalho1/data/labirinto.txt)")
    parser.add_argument("--out", type=str, default=None, help="Arquivo .txt para salvar a tabela (padrão: trabalho1/metrics/metrics.txt)")
    args = parser.parse_args()

    # Carrega o labirinto do arquivo especificado ou padrão
    maze_path = Path(args.maze) if args.maze else _load_default_maze_path()
    mz = Maze.from_file(maze_path)

    path: List[Pos]

    # Função auxiliar para formatar booleanos como strings
    def _bool_str(v: bool | None) -> str:
        return "sim" if v is True else ("não" if v is False else "-")

    # Função para formatar a tabela de métricas dos algoritmos
    def _format_table(rows: List[dict]) -> str:
        headers = [
            "Algoritmo", "Heurística", "Tempo(ms)", "Expandidos", "Gerados",
            "Explorados", "Fronteira", "Pico Memória", "Completo", "Ótimo", "Custo", "Caminho"
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
                f"{m.max_explored}",
                f"{m.max_frontier}",
                f"{m.max_structures}",
                _bool_str(m.completeness),
                _bool_str(m.optimal),
                f"{m.path_cost}",
                r.get("path_str", "-"),
            ])
        # Calcula larguras das colunas
        widths = [len(h) for h in headers]
        for row in data:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))
        # Monta tabela formatada
        def fmt_row(cols: List[str]) -> str:
            return " | ".join(c.ljust(widths[i]) for i, c in enumerate(cols))
        sep = "-+-".join("-" * w for w in widths)
        lines = [fmt_row(headers), sep]
        for row in data:
            lines.append(fmt_row(row))
        return "\n".join(lines)

    # Função para mostrar sequência de letras do caminho encontrado
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

    # Executa todos os algoritmos e gera tabela de métricas
    rows: List[dict] = []

    # Executa BFS
    p_bfs, m_bfs = bfs(mz, with_metrics=True, compute_optimality=True)
    rows.append({"name": "BFS", "heur": "-", "metrics": m_bfs, "path_str": _labels_sequence(mz, p_bfs)})

    # Executa DFS
    p_dfs, m_dfs = dfs(mz, with_metrics=True, compute_optimality=True)
    rows.append({"name": "DFS", "heur": "-", "metrics": m_dfs, "path_str": _labels_sequence(mz, p_dfs)})

    # Executa A* e Greedy com múltiplas heurísticas
    heur_list = [
        ("Manhattan", _get_heuristic("manhattan")),
        ("Euclidiana", _get_heuristic("euclidean")),
    ]
    # Executa A* para cada heurística
    for heur_name, h in heur_list:
        p_as, m_as = astar(mz, h=h, with_metrics=True, compute_optimality=True)
        rows.append({"name": "A*", "heur": heur_name, "metrics": m_as, "path_str": _labels_sequence(mz, p_as)})
    # Executa Greedy para cada heurística
    for heur_name, h in heur_list:
        p_gr, m_gr = greedy_best_first(mz, h=h, with_metrics=True, compute_optimality=True)
        rows.append({"name": "Greedy", "heur": heur_name, "metrics": m_gr, "path_str": _labels_sequence(mz, p_gr)})

    # Formata e salva tabela de métricas em arquivo
    table = _format_table(rows)
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
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
