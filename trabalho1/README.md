# Trabalho 1 - Busca em Labirinto (Formato NSLO)

Implementação de um labirinto baseado em máscaras de 4 bits (N, S, L, O) com buscas:
- Não informadas: BFS e DFS
- Informadas: A* e Gulosa (Greedy Best-First)

## Estrutura do projeto
```
trabalho1/
	src/                    # Código-fonte
		maze.py              # Parser NSLO e API do Maze (start, goal, neighbors, step_cost, label_at)
		search.py            # Algoritmos (BFS, DFS, A*, Greedy) + coleta de métricas (SearchMetrics)
		heuristics.py        # Heurísticas: manhattan, euclidean

	data/                   # Labirintos no formato NSLO
		labirinto.txt       # Arquivo de labirinto padrão (usado pelo runner)

	tests/                  # Runner (executa tudo de uma vez)
		test.py             # Roda BFS/DFS/A*/Greedy (Manhattan/Euclidiana), gera metrics.txt e gráficos

	metrics/                # Saídas geradas pelo runner
		metrics.txt         # Tabela consolidada de métricas
		01_tempo_ms.png     # Gráfico: Tempo (ms)
		02_expandidos.png   # Gráfico: Expandidos
		03_gerados.png      # Gráfico: Gerados
		04_pico_memoria.png # Gráfico: Pico Memória (pico simultâneo)
		05_custo.png        # Gráfico: Custo do caminho
```

## Dependências
- Python 3.10+
- Bibliotecas:
	- matplotlib

Instalação:
```bash
pip install matplotlib
```

## Como executar
- Executa todos os algoritmos (BFS, DFS, A* com Manhattan/Euclidiana e Greedy com Manhattan/Euclidiana) e salva a tabela de métricas.

```bash
python trabalho1/tests/test.py
```

Saídas:
- Tabela: `trabalho1/metrics/metrics.txt`
- O script imprime apenas o caminho do arquivo salvo (a tabela não é exibida no terminal).
- Para alterar o labirinto de entrada:
	```bash
	python trabalho1/tests/test.py --maze trabalho1/data/labirinto.txt
	```

Reprodutibilidade:
- O runner fixa a semente: `random.seed(42)`.

## Como reproduzir os gráficos
- Se `matplotlib` estiver instalado, os gráficos são gerados automaticamente após a execução do runner.
- Arquivos PNG são salvos em `trabalho1/metrics/` com nomes por métrica (tempo_ms, expandidos, gerados, pico_memoria, custo).
- Caso `matplotlib` não esteja instalado, os gráficos são pulados; um arquivo de aviso é salvo em `trabalho1/metrics/PLOTTING_DISABLED.txt` com instruções de instalação.