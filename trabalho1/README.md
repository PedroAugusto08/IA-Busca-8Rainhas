# Trabalho 1 - Busca em Labirinto (Formato NSLO)

Implementação de um labirinto baseado em máscaras de 4 bits (N, S, L, O) e buscas não informadas (BFS e DFS).

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
- Ao renderizar um caminho, Start aparece como `S`, Goal como `G` e os passos intermediários como `o`.

## Execução Rápida (Teste mínimo do maze)
```bash
python trabalho1/src/maze.py
```

Isso carrega o arquivo `data/labirinto.txt`, imprime estrutura e vizinhos do Start.

## Licença
Uso educacional.