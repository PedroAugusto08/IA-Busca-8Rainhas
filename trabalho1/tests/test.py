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

    # Gera gráficos de barras das métricas usando os mesmos dados da tabela
    def _generate_bar_charts(rows: List[dict], out_dir: Path) -> None:
        try:
            import matplotlib.pyplot as plt
            from matplotlib.ticker import FuncFormatter, MaxNLocator
            # Estilo legível com grade
            try:
                plt.style.use("seaborn-v0_8-whitegrid")
            except Exception:
                try:
                    plt.style.use("seaborn-whitegrid")
                except Exception:
                    plt.style.use("ggplot")
        except Exception as e:
            # Se matplotlib não estiver disponível, registra uma dica e segue sem falhar o runner
            try:
                (out_dir / "PLOTING_DISABLED.txt").write_text(
                    "matplotlib não encontrado. Para habilitar gráficos, instale com:\n\n"
                    "pip install matplotlib\n\n"
                    "Os gráficos são gerados automaticamente na próxima execução.",
                    encoding="utf-8",
                )
            except Exception:
                pass
            return

        labels = [
            r["name"] if r["heur"] == "-" else f"{r['name']} ({r['heur']})"
            for r in rows
        ]

        # Paleta consistente por algoritmo/heurística
        color_map = {
            "BFS": "#1f77b4",
            "DFS": "#ff7f0e",
            "A* (Manhattan)": "#2ca02c",
            "A* (Euclidiana)": "#98df8a",
            "Greedy (Manhattan)": "#d62728",
            "Greedy (Euclidiana)": "#ff9896",
        }
        hatch_map = {
            "BFS": "",
            "DFS": "",
            "A* (Manhattan)": "",
            "A* (Euclidiana)": "///",
            "Greedy (Manhattan)": "",
            "Greedy (Euclidiana)": "///",
        }

        # Extratores das mesmas métricas usadas na tabela
        metric_specs = [
            ("tempo_ms", "Tempo (ms)", lambda m: m.time_sec * 1000.0, False),
            ("expandidos", "Nós expandidos", lambda m: m.expanded, True),
            ("gerados", "Nós gerados", lambda m: m.generated, True),
            ("explorados", "Explorados (pico)", lambda m: m.max_explored, True),
            ("fronteira", "Fronteira (pico)", lambda m: m.max_frontier, True),
            ("pico_memoria", "Pico de memória (estruturas)", lambda m: m.max_structures, True),
            ("custo", "Custo do caminho", lambda m: m.path_cost, True),
        ]

        for idx, (key, ylabel, fn, is_int) in enumerate(metric_specs, start=1):
            values = [fn(r["metrics"]) for r in rows]
            fig_h = 5 if len(labels) <= 6 else 6
            fig, ax = plt.subplots(figsize=(10, fig_h))

            # Cores e hachuras por algoritmo/heurística
            full_labels = labels
            colors = [color_map.get(lbl, "#4C78A8") for lbl in full_labels]
            hatches = [hatch_map.get(lbl, "") for lbl in full_labels]

            bars = ax.bar(full_labels, values, color=colors, edgecolor="#222", linewidth=0.6)
            for bar, hatch in zip(bars, hatches):
                bar.set_hatch(hatch)

            ax.set_title(f"Comparação de métricas - {ylabel}")
            ax.set_ylabel(ylabel)
            ax.set_xlabel("Algoritmos")
            ax.set_xticklabels(full_labels, rotation=15, ha="right")

            # Grade e formatação do eixo Y
            ax.grid(True, axis="y", linestyle="--", linewidth=0.6, alpha=0.6)
            if key == "tempo_ms":
                ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:.3f}"))
            elif is_int:
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))

            # Espaço no topo para os rótulos
            vmax = max(values) if values else 0
            ax.set_ylim(0, vmax * 1.12 if vmax > 0 else 1)

            # Rótulos nas barras (3 casas no tempo; inteiros nos demais)
            for rect, val in zip(bars, values):
                label = f"{val:.3f}" if key == "tempo_ms" else f"{int(val)}"
                ax.annotate(
                    label,
                    xy=(rect.get_x() + rect.get_width() / 2, rect.get_height()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    color="#111",
                )

            fig.tight_layout()
            png = out_dir / f"{idx:02d}_{key}.png"
            try:
                fig.savefig(png, dpi=200)
            finally:
                plt.close(fig)

    _generate_bar_charts(rows, metrics_dir)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
