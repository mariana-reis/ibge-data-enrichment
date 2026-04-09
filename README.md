# IBGE Data Enrichment

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-2.33-FF6F00?logo=python&logoColor=white)
![TheFuzz](https://img.shields.io/badge/TheFuzz-0.22-4CAF50?logo=python&logoColor=white)
![UV](https://img.shields.io/badge/uv-Package%20Manager-DE5FE9?logo=uv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue)

Pipeline de enriquecimento de dados municipais brasileiros. Recebe um CSV com nomes de municípios (com possíveis erros de digitação), cruza com a API oficial do IBGE usando fuzzy matching inteligente e gera um CSV enriquecido com UF, região, código IBGE e estatísticas agregadas.

## Arquitetura

```
main.py                 ← Orquestrador do fluxo
ibge/
├── config.py           ← Constantes e URLs
├── models.py           ← Dataclasses tipadas (MunicipioIBGE, LinhaResultado, Estatisticas)
├── text.py             ← Normalização de texto (remoção de acentos, lowercase)
├── api.py              ← Cliente IBGE com cache em memória
├── matching.py         ← Matching exato + fuzzy com validação por palavra
├── processing.py       ← Enriquecimento e detecção de duplicatas
├── csv_io.py           ← Leitura/escrita de CSV
├── statistics.py       ← Cálculo de métricas agregadas
└── submission.py       ← Envio de resultados via JWT
```

## Pré-requisitos

- **Python** 3.11+
- **uv** (gerenciador de pacotes)

## Instalação

```bash
git clone https://github.com/mariana-reis/ibge-data-enrichment.git
cd ibge-data-enrichment

uv sync
```

## Como Executar

```bash

uv run main.py

```

Configurar o token via arquivo `.env`:

```env
ACCESS_TOKEN=seu_token_aqui
```

## Fluxo de Execução

```
input.csv → API IBGE → Matching → resultado.csv → Estatísticas → POST
```

1. **Carrega municípios do IBGE** — chamada única à API, cache em memória
2. **Lê `input.csv`** — municípios com população
3. **Matching em dois passes**:
   - Match exato por normalização (sem acentos, lowercase)
   - Fuzzy matching (Levenshtein) com validação granular por palavra
4. **Gera `resultado.csv`** — dados enriquecidos com UF, região, código IBGE e status
5. **Calcula estatísticas** — totais, população e médias por região
6. **Submete resultados** — POST autenticado via Bearer token

## Exemplo de Entrada e Saída

### `input.csv`

| municipio       | populacao |
|-----------------|-----------|
| Niteroi         | 515317    |
| Belo Horzionte  | 2530701   |
| Santoo Andre    | 700000    |

### `resultado.csv`

| municipio_input | populacao_input | municipio_ibge  | uf | regiao      | id_ibge | status          |
|-----------------|-----------------|-----------------|-----|-------------|---------|-----------------|
| Niteroi         | 515317          | Niterói         | RJ  | Sudeste     | 3303302 | OK              |
| Belo Horzionte  | 2530701         | Belo Horizonte  | MG  | Sudeste     | 3106200 | OK              |
| Santoo Andre    | 700000          |                 |     |             |         | NAO_ENCONTRADO  |

### Status

| Status           | Descrição                                              |
|------------------|--------------------------------------------------------|
| `OK`             | Município encontrado com confiança                     |
| `NAO_ENCONTRADO` | Sem match acima do threshold de similaridade           |
| `AMBIGUO`        | Nome duplicado no input (mesmo nome normalizado)       |
| `ERRO_API`       | Falha na comunicação com a API do IBGE                 |

## Estratégia de Matching

O matching combina normalização determinística com fuzzy probabilístico:

- **Normalização**: remoção de acentos via NFKD + lowercase + trim
- **Threshold**: score Levenshtein ≥ 88
- **Validação por palavra**: cada palavra é avaliada individualmente
  - Palavras curtas (≤ 5 chars): tolera apenas 1 substituição, rejeita inserção/deleção
  - Palavras longas: tolera até 2 operações totais

Isso permite aceitar `Horzionte → Horizonte` (substituição em palavra longa) mas rejeitar `Santoo → Santo` (deleção em palavra curta).

## Stack

| Tecnologia         | Uso                                        |
|--------------------|--------------------------------------------|
| Python 3.12        | Tipagem nativa com union types e generics  |
| requests           | Chamadas HTTP (IBGE + submissão)           |
| thefuzz            | Fuzzy matching baseado em Levenshtein      |
| python-levenshtein | Backend C para performance no matching     |
| python-dotenv      | Carregamento de variáveis via `.env`       |
| uv                 | Gerenciamento de dependências e execução   |
| dataclasses        | Modelos imutáveis com `frozen` e `slots`   |
