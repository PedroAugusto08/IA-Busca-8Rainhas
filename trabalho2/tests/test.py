"""Runner para o Trabalho 2 — 8 Rainhas com Hill Climbing.

Executa as variantes:
- Hill Climbing com movimentos laterais (sideways)
- Hill Climbing com Random-Restart (rr)

Agrega métricas em múltiplos trials e salva, em trabalho2/metrics/metrics.txt,
um tabuleiro de amostra (seed=42) seguido da tabela consolidada.
"""

from __future__ import annotations
import sys
from pathlib import Path
import argparse
import random
from typing import List, Dict, Any
import statistics

try:
    import matplotlib.pyplot as plt  # type: ignore
except Exception:  # matplotlib opcional
    plt = None  # type: ignore

# Garante que a raiz do repositório esteja no sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from trabalho2.src.eight_queens import initial_board, conflicts, board_to_str
from trabalho2.src.hill_climbing import (
    hill_climbing_sideways,
    hill_climbing_random_restart,
)


def _format_table(headers: List[str], rows: List[List[str]]) -> str:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    def fmt_row(cols: List[str]) -> str:
        return " | ".join(c.ljust(widths[i]) for i, c in enumerate(cols))
    sep = "-+-".join("-" * w for w in widths)
    lines = [fmt_row(headers), sep]
    for row in rows:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Runner - 8 Rainhas com Hill Climbing (sideways e random-restart)")
    parser.add_argument("--n", type=int, default=8, help="Tamanho do tabuleiro (padrão: 8)")
    parser.add_argument("--trials", type=int, default=100, help="Número de execuções por variante (padrão: 10)")
    parser.add_argument("--lateral-limit", type=int, default=100, help="Limite de movimentos laterais (padrão da função: 50)")
    parser.add_argument("--max-iters", type=int, default=1000, help="Máximo de iterações por execução (padrão: 1000)")
    parser.add_argument("--max-restarts", type=int, default=50, help="Máximo de reinícios no Random-Restart (padrão: 100)")
    parser.add_argument("--out", type=str, default=None, help="Arquivo .txt de saída (padrão: trabalho2/metrics/metrics.txt)")
    parser.add_argument("--show-board", action="store_true", help="Imprime um tabuleiro de amostra antes de executar os trials")
    args = parser.parse_args()

    n = args.n
    T = args.trials
    lateral_limit = args.lateral_limit
    max_iters = args.max_iters
    max_restarts = args.max_restarts

    # Reprodutibilidade
    random.seed(42)

    # Gera um tabuleiro de amostra (sem afetar os trials) e prepara texto para o arquivo
    sample = initial_board(n)
    sample_text = (
        "Tabuleiro (amostra, seed=42):\n" + board_to_str(sample) +
        f"\nConflitos: {conflicts(sample)}\n\n"
    )

    if args.show_board:
        print(sample_text)

    # Preparar tabuleiros iniciais idênticos para todos os trials
    random.seed(42)
    initial_boards: List[List[int]] = [initial_board(n) for _ in range(T)]


    # Tabela por-trial: HC-Sideways
    headers_sw = ["Trial", "Sucesso", "Tempo(ms)", "Passos", "Laterais", "conflicts_start", "conflicts_final"]
    rows_sw: List[List[str]] = []
    sum_time = 0.0
    sum_steps = 0
    sum_lats = 0
    sum_h_start = 0
    sum_h_final = 0
    success_cnt = 0
    # coletores para gráficos
    times_sw_ms: List[float] = []
    steps_sw: List[int] = []
    lats_sw: List[int] = []
    succ_sw: List[bool] = []
    for i in range(1, T + 1):
        b0 = list(initial_boards[i - 1])  # mesmo tabuleiro usado pelo RR
        if lateral_limit is None:
            res = hill_climbing_sideways(b0, max_iters=max_iters)
        else:
            res = hill_climbing_sideways(b0, lateral_limit=lateral_limit, max_iters=max_iters)
        t_ms = float(res.get("time_sec", 0.0)) * 1000.0
        steps = int(res.get("steps", 0))
        lats = int(res.get("sideways_used", 0))
        hstart = int(conflicts(b0))
        hfin = int(res.get("conflicts_final", conflicts(res["board"])))  # type: ignore[index]
        succ = "sim" if res.get("success") else "não"
        rows_sw.append([
            str(i),
            succ,
            f"{t_ms:.3f}",
            str(steps),
            str(lats),
            str(hstart),
            str(hfin),
        ])
        sum_time += t_ms
        sum_steps += steps
        sum_lats += lats
        sum_h_start += hstart
        sum_h_final += hfin
        success_cnt += 1 if res.get("success") else 0
        # coleta
        times_sw_ms.append(t_ms)
        steps_sw.append(steps)
        lats_sw.append(lats)
        succ_sw.append(bool(res.get("success")))
    avg_time = sum_time / T if T else 0.0
    avg_steps = sum_steps / T if T else 0.0
    avg_lats = sum_lats / T if T else 0.0
    avg_h_start = sum_h_start / T if T else 0.0
    avg_h_final = sum_h_final / T if T else 0.0
    success_pct = (success_cnt / T) * 100.0 if T else 0.0
    rows_sw.append(["Média", f"{success_pct:.1f}%", f"{avg_time:.3f}", f"{avg_steps:.2f}", f"{avg_lats:.2f}", f"{avg_h_start:.2f}", f"{avg_h_final:.2f}"])
    table_sw = "HC-Sideways" + "\n" + _format_table(headers_sw, rows_sw)

    # Tabela por-trial: HC-RandomRestart
    headers_rr = ["Trial", "Sucesso", "Tempo(ms)", "Passos", "Reinícios", "conflicts_start", "conflicts_final"]
    rows_rr: List[List[str]] = []
    sum_time = 0.0
    sum_steps_total = 0
    sum_restarts = 0
    sum_h_start = 0
    sum_h_final = 0
    success_cnt = 0
    # coletores para gráficos
    times_rr_ms: List[float] = []
    steps_rr: List[int] = []
    restarts_rr: List[int] = []
    succ_rr: List[bool] = []
    for i in range(1, T + 1):
        b0 = list(initial_boards[i - 1])  # mesmo tabuleiro do sideways
        res = hill_climbing_random_restart(
            n,
            max_restarts=max_restarts,
            max_iters_per_restart=max_iters,
            rng=random,
            initial_board_override=b0,  # <- novo parâmetro que vamos adicionar abaixo
        )
        t_ms = float(res.get("time_sec", 0.0)) * 1000.0
        steps = int(res.get("steps_total", 0))
        restarts = int(res.get("restarts", 0))
        hstart = int(res.get("conflicts_start", 0))
        hfin = int(res.get("conflicts_final", conflicts(res["board"])))  # type: ignore[index]
        succ = "sim" if res.get("success") else "não"
        rows_rr.append([
            str(i),
            succ,
            f"{t_ms:.3f}",
            str(steps),
            str(restarts),
            str(hstart),
            str(hfin),
        ])
        sum_time += t_ms
        sum_steps_total += steps
        sum_restarts += restarts
        sum_h_start += hstart
        sum_h_final += hfin
        success_cnt += 1 if res.get("success") else 0
        # coleta
        times_rr_ms.append(t_ms)
        steps_rr.append(steps)
        restarts_rr.append(restarts)
        succ_rr.append(bool(res.get("success")))
    avg_time = sum_time / T if T else 0.0
    avg_steps_total = sum_steps_total / T if T else 0.0
    avg_restarts = sum_restarts / T if T else 0.0
    avg_h_start = sum_h_start / T if T else 0.0
    avg_h_final = sum_h_final / T if T else 0.0
    success_pct = (success_cnt / T) * 100.0 if T else 0.0
    rows_rr.append(["Média", f"{success_pct:.1f}%", f"{avg_time:.3f}", f"{avg_steps_total:.2f}", f"{avg_restarts:.2f}", f"{avg_h_start:.2f}", f"{avg_h_final:.2f}"])
    table_rr = "HC-RandomRestart" + "\n" + _format_table(headers_rr, rows_rr)

    # Salvar tabuleiro de amostra + tabela
    metrics_dir = Path(__file__).resolve().parents[1] / "metrics"
    try:
        metrics_dir.mkdir(parents=True, exist_ok=True) 
    except Exception:
        pass
    out_path = Path(args.out) if args.out else (metrics_dir / "metrics.txt")
    try:
        out_path.write_text(sample_text + table_sw + "\n\n" + table_rr + "\n", encoding="utf-8")
        print(f"Tabela de métricas salva em: {out_path}")
    except Exception as e:
        print("Falha ao salvar a tabela:", e)

    # Geração de gráficos (se matplotlib disponível)
    try:
        if plt is not None:
            _generate_plots(
                metrics_dir,
                times_sw_ms,
                steps_sw,
                lats_sw,
                succ_sw,
                times_rr_ms,
                steps_rr,
                restarts_rr,
                succ_rr,
            )
            print(f"Gráficos salvos em: {metrics_dir}")
        else:
            print("matplotlib não encontrado; gráficos não gerados.")
    except Exception as e:
        print("Falha ao gerar gráficos:", e)

    return 0


def _generate_plots(
    out_dir: Path,
    times_sw_ms: List[float],
    steps_sw: List[int],
    lats_sw: List[int],
    succ_sw: List[bool],
    times_rr_ms: List[float],
    steps_rr: List[int],
    restarts_rr: List[int],
    succ_rr: List[bool],
) -> None:
    if plt is None:
        return

    # Estilo visual agradável
    try:
        plt.style.use("seaborn-v0_8")
    except Exception:
        plt.style.use("ggplot")

    # Utilitários
    def _mean(xs: List[float]) -> float:
        return float(statistics.mean(xs)) if xs else 0.0

    def _stdev(xs: List[float]) -> float:
        return float(statistics.stdev(xs)) if len(xs) > 1 else 0.0

    # 1) Barras: Tempo(ms), Passos, Sucesso(%)
    labels = ["Sideways", "Random-Restart"]

    # Tempo(ms)
    means = [_mean(times_sw_ms), _mean(times_rr_ms)]
    errs = [_stdev(times_sw_ms), _stdev(times_rr_ms)]
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, means, yerr=errs, capsize=6, color=["#4C78A8", "#F58518"])
    ax.set_ylabel("Tempo (ms)")
    ax.set_title("Tempo médio por algoritmo (± desvio)")
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{val:.1f}", ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_dir / "tempo_mean_bar.png", dpi=160)
    plt.close(fig)

    # Passos
    means = [_mean([float(x) for x in steps_sw]), _mean([float(x) for x in steps_rr])]
    errs = [_stdev([float(x) for x in steps_sw]), _stdev([float(x) for x in steps_rr])]
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, means, yerr=errs, capsize=6, color=["#4C78A8", "#F58518"])
    ax.set_ylabel("Passos")
    ax.set_title("Passos médios por algoritmo (± desvio)")
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{val:.1f}", ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_dir / "passos_mean_bar.png", dpi=160)
    plt.close(fig)

    # Sucesso (%)
    def _pct_true(bs: List[bool]) -> float:
        return (sum(1 for b in bs if b) / len(bs) * 100.0) if bs else 0.0
    means = [_pct_true(succ_sw), _pct_true(succ_rr)]
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, means, color=["#4C78A8", "#F58518"])
    ax.set_ylabel("Sucesso (%)")
    ax.set_ylim(0, 100)
    ax.set_title("Taxa de sucesso por algoritmo")
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{val:.1f}%", ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_dir / "sucesso_bar.png", dpi=160)
    plt.close(fig)

    # 2) Boxplots: Tempo(ms), Passos
    # Tempo
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.boxplot([times_sw_ms, times_rr_ms], labels=labels, showfliers=True)
    ax.set_ylabel("Tempo (ms)")
    ax.set_title("Distribuição de tempo (boxplot)")
    fig.tight_layout()
    fig.savefig(out_dir / "tempo_box.png", dpi=160)
    plt.close(fig)

    # Passos
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.boxplot([steps_sw, steps_rr], labels=labels, showfliers=True)
    ax.set_ylabel("Passos")
    ax.set_title("Distribuição de passos (boxplot)")
    fig.tight_layout()
    fig.savefig(out_dir / "passos_box.png", dpi=160)
    plt.close(fig)

    # 3) Boxplots específicos
    # Reinícios (RR)
    if steps_rr:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.boxplot([restarts_rr], labels=["Random-Restart"], showfliers=True)
        ax.set_ylabel("Reinícios")
        ax.set_title("Distribuição de reinícios (RR)")
        fig.tight_layout()
        fig.savefig(out_dir / "reinicios_box.png", dpi=160)
        plt.close(fig)

    # Laterais (Sideways)
    if steps_sw:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.boxplot([lats_sw], labels=["Sideways"], showfliers=True)
        ax.set_ylabel("Laterais")
        ax.set_title("Distribuição de laterais (Sideways)")
        fig.tight_layout()
        fig.savefig(out_dir / "laterais_box.png", dpi=160)
        plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
