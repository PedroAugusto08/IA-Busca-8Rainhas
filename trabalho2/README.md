# Trabalho 2 - Problema das 8 Rainhas

## Estrutura do Projeto
```
src/                                # Representação e algoritmo (eight_queens, hill_climbing)
    eight_queens.py                 # Implementações gerais do problema das 8 rainhas
    hill_climbing.py                # Implementações dos algoritmos usados no Hill Climbing

tests/                              # Testes
    test.py                         # Gera os tabuleiros iniciais, roda os algoritmos e gera as médias

metrics/                            # Valores gerados no teste
    metrics.txt                     # Exemplo de tabuleiro e tabelas com os resultados
    laterais_box.png                # Boxplot da distribuição de laterais
    passos_box.png                  # Boxplot compartivo da distribuição de passos
    passos_mean_bar.png             # Gráfico comparativo da média de passos
    reinícios_box.png               # Boxplot da distribuição de reinícios
    sucesso_bar.png                 # Gráfico comparativo da taxa de sucesso
    tempo_box.png                   # Boxplot comparativo da distribuição de tempo
    tempo_mean_bar.png              # Gráfico comparativo dos tempos médios

read_me/                            # Pasta com o PDF do relatório da atividade
    trabalho2_ Pedro e Samuel.pdf   # PDF do relatório da atividade
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
- Executa os dois tipos de Hill Climbing (sideaways e Random-Restart) e salva as execuções e médias na tabela de métricas
```bash
python trabalho2/tests/test.py
```

## Reprodução dos gráficos
- Se `matplotlib` estiver instalado, os gráficos são gerados automaticamente após a execução do runner.
- Arquivos PNG são salvos em `trabalho1/metrics/` com nomes por métrica.

## Observações
- Pequenas diferenças de tempo entre execuções são normais, mesmo com o mesmo código e entrada. Os principais fatores são:
	- Agendador do sistema operacional e carga de outros processos.
	- Variações de frequência (turbo/thermal) da CPU e política de energia.
	- Efeitos de cache.
	- Coletor de lixo (GC) e sobrecustos internos do Python.