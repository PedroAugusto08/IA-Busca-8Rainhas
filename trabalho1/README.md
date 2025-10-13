# Trabalho 1 - Busca em Labirinto (Formato NSLO)

Implementação de um labirinto baseado em máscaras de 4 bits (N, S, L, O) com buscas:
- Não informadas: BFS e DFS
- Informadas: A* e Gulosa (Greedy Best-First)

## Estrutura
```
src/            # Código fonte (maze, search, heuristics)
data/           # Arquivos de labirinto no formato NSLO
tests/          # (a ajustar para o formato atual)
```

## Requisitos
Python 3.10+

## Formato do Labirinto (NSLO)
Cada célula é descrita em uma linha:

```
[row,col]:NSLO  # LetraOpcional
```

Onde:
- `row,col` começam em 0.
- `NSLO` são 4 dígitos (0 ou 1) indicando (Norte, Sul, Leste, Oeste).
	- 1 = parede (movimento bloqueado naquela direção)
	- 0 = livre (movimento permitido se a célula destino existir)
- Após `#` pode haver uma letra (apenas para visualização). Se omitida, `.` é usado internamente.
- Linhas em branco ou iniciadas por `#` são ignoradas.
- Opcionalmente podem existir ao final do arquivo as linhas documentais:
	- `Start:[r,c]`
	- `Goal:[r,c]`
	Elas são apenas verificadas: o código fixa Start=(4,0) e Goal=(0,4). Se divergirem, gera erro.

O arquivo deve formar um retângulo completo: todas as posições de (0,0) até (max_row,max_col) precisam estar presentes.

### Exemplo mínimo
```
[0,0]:1110  # A
[0,1]:1100  # B
[0,2]:1101  # C
[1,0]:1010  # D
[1,1]:0011  # E
[1,2]:1011  # F
[2,0]:0110  # G
[2,1]:0010  # H
[2,2]:0111  # I
```

### Interpretação dos bits
Para a célula `[r,c]:abcd`:
- `a` (1º dígito) => Norte
- `b` (2º) => Sul
- `c` (3º) => Leste
- `d` (4º) => Oeste

Se o bit for 0, você pode tentar mover naquela direção (desde que o destino exista). Não é exigida reciprocidade: mover de X para Y não implica que o movimento inverso seja permitido.

### Start e Goal
- Fixos no código: Start = (4,0) e Goal = (0,4).
- Renderização do caminho:
	- Start e Goal aparecem com as letras originais coloridas (verde/vermelho) no terminal.
	- Passos intermediários são marcados com `.`.

## Funções disponíveis (APIs)

- `def bfs(maze: "Maze") -> List[Pos]`
	- Busca em largura. Retorna caminho de Start até Goal (incluindo ambos). Ótimo em número de passos.
- `def dfs(maze: "Maze") -> List[Pos]`
	- Busca em profundidade. Não garante caminho mínimo.
- `def astar(maze: "Maze", h: Optional[Callable[[Pos, Pos], float]] = None) -> List[Pos]`
	- A* com `f(n) = g(n) + h(n)`. Padrão `h`: Manhattan. Aceita qualquer heurística `Callable[[Pos, Pos], float]`.
	- Ótimo em custo quando `h` é admissível (ex.: Manhattan em grid 4-direções com custo 1).
- `def greedy_best_first(maze: "Maze", h: Optional[Callable[[Pos, Pos], float]] = None) -> List[Pos]`
	- Gulosa: fronteira ordenada apenas por `h(n)`. Rápida, mas não ótima.
- `def manhattan(a: Pos, b: Pos) -> int` e `def euclidean(a: Pos, b: Pos) -> float`
	- Heurísticas prontas para uso em A* e Gulosa.
- `class Maze`
	- `@classmethod def from_file(path: Union[Path, str]) -> "Maze"`
	- `def start(self) -> Pos`
	- `def goal(self) -> Pos`
	- `def neighbors(self, pos: Pos) -> Iterator[Pos]`
	- `def step_cost(self, from_pos: Pos, to_pos: Pos) -> int`
	- `def label_at(self, pos: Pos) -> str`
	- `def render_path(self, path: List[Pos]) -> str`

Observações:
- As buscas retornam `[]` quando não há caminho.
- `Pos` é uma tupla `(row, col)`.

## Como rodar

O repositório inclui um runner CLI simples que funciona sem configuração extra. Execute os comandos a partir da raiz do repositório:

```bash
# A* (Manhattan — padrão)
python trabalho1/tests/test.py --algo astar

# A* com Euclidiana
python trabalho1/tests/test.py --algo astar --heuristic euclidean

# Gulosa (Greedy) com Euclidiana
python trabalho1/tests/test.py --algo greedy --heuristic euclidean

# BFS e DFS
python trabalho1/tests/test.py --algo bfs
python trabalho1/tests/test.py --algo dfs

# Especificar outro arquivo de labirinto
python trabalho1/tests/test.py --maze trabalho1/data/labirinto.txt
```

### Rodar todos os algoritmos e gerar tabela de métricas

Agora é possível (e padrão) executar todos os algoritmos em sequência e salvar uma tabela consolidada com as métricas:

```bash
# Executa BFS, DFS, A* e Gulosa usando a heurística escolhida para A* e Gulosa
python trabalho1/tests/test.py --algo all --heuristic manhattan --stats

```

Detalhes do modo "all":
- A tabela é salva em arquivo (não é impressa no terminal) no caminho informado por `--out` ou, por padrão, em `trabalho1/metrics/metrics.txt`.
- A saída inclui linhas nas seguintes ordens:
	- BFS
	- DFS
	- A* (Manhattan)
	- A* (Euclidiana)
	- Greedy (Manhattan)
	- Greedy (Euclidiana)
- Colunas: Algoritmo, Heurística, Tempo(ms), Expandidos, Gerados, Pico (máximo de estruturas), Fronteira, Explorados, Completo, Ótimo, Custo, Tam, Caminho (sequência de letras U(S) -> ... -> E(G)).
- Não há renderização visual no modo `all` (apenas a coluna do caminho por letras).

### Métricas disponíveis (SearchMetrics)

Quando `--stats` é usado (ou ao chamar as funções com `with_metrics=True`), são coletados e reportados:
- `time_sec`: tempo total de execução do algoritmo (segundos)
- `expanded`: nós expandidos
- `generated`: nós gerados
- `max_frontier`: pico de elementos na fronteira (fila/pilha/heap)
- `max_explored`: pico de elementos no conjunto explorado/visitado/fechado
- `max_structures`: `max_frontier + max_explored`
- `found`: se encontrou solução
- `completeness`: se o algoritmo é completo para o problema (avaliado via oráculo BFS quando solicitado)
- `optimal`: se o caminho retornado é ótimo (avaliado via oráculo BFS quando solicitado)
- `path_cost`: custo do caminho (custos uniformes = número de passos)
- `path_len`: tamanho do caminho (número de estados)

Observação: Completeness/Optimality só são avaliadas quando explicitamente solicitado (`--stats` no CLI, `compute_optimality=True` no código). Para A* e Gulosa no modo `all`, as métricas são registradas para Manhattan e Euclidiana.

### API com métricas (uso programático)

As funções também suportam coleta de métricas diretamente:

```
path = bfs(maze)
path, metrics = bfs(maze, with_metrics=True, compute_optimality=True)

path = astar(maze, h=manhattan)
path, metrics = astar(maze, h=euclidean, with_metrics=True)
```

`metrics` é uma instância de `SearchMetrics` com os campos descritos acima.

### Reprodutibilidade

O runner fixa `random.seed(42)` para execuções determinísticas. Para evitar qualquer variação de hashing do Python em iterações de conjuntos, você pode opcionalmente definir `PYTHONHASHSEED=0` ao executar o script.

Execução mínima do `Maze` (sanidade check):
```bash
python trabalho1/src/maze.py
```
Isso carrega `data/labirinto.txt`, imprime a estrutura e os vizinhos do Start.

## Licença
Uso educacional.