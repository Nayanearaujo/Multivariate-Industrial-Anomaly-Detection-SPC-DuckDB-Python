# Industrial Anomaly Analytics: Detecção Estatística Multivariada com DuckDB e Python

**Um framework analítico industrial que transforma dados de sensores de alta frequência em um plano de monitoramento estatístico de processos, auditado e pronto para a tomada de decisão operacional.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.10-orange?logo=duckdb)](https://duckdb.org/)
[![SQL](https://img.shields.io/badge/SQL-DuckDB-blue)](https://duckdb.org/)
[![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Power_BI](https://img.shields.io/badge/Power_BI-Executive-yellow?logo=powerbi)](https://powerbi.microsoft.com/)
[![Parquet](https://img.shields.io/badge/Parquet-Data_Lake-blue)](https://parquet.apache.org/)
[![Pytest](https://img.shields.io/badge/Pytest-Integrity_Checks-green?logo=pytest)](https://docs.pytest.org/)

Este projeto analisa o dataset do *Tennessee Eastman Process* utilizando um stack de **Python, SQL, Docker e Power BI**. O escopo cobre desde a auditoria da base de dados física (*raw signals*), validação da consistência estatística da operação normal, detecção de anomalias por modelos multivariados (SPC), até a modelagem dimensional de KPIs e o design de um plano de controle contínuo baseado em DMAIC.

---

### 📊 [CLIQUE AQUI PARA ACESSAR O DASHBOARD INTERATIVO](https://github.com/Nayanearaujo/industrial-anomaly-analytics)

![Dashboard Executivo - Industrial Anomaly Analytics](images/powerbi_executive_overview.png)

---

## 🛠️ Tech Stack e Habilidades
Este repositório é um case de **Analytics Engineering & Industrial Data Science** focado em confiabilidade e integridade de dados operacionais:

- **Python (Pandas, NumPy, Plotly):** Pipelines de ETL para conversão de grandes volumes de séries temporais (formato RData para Parquet), análise exploratória multivariada e modelagem SPC.
- **SQL (DuckDB):** Modelagem e criação de views de KPIs analíticos para consumo no Power BI.
- **Docker & Docker Compose:** Containerização do ambiente completo para execução isolada e reprodutibilidade com um único comando.
- **Estatística Industrial:** Monitoramento multivariado via $T^2$ de Hotelling, resíduos $Q$ (SPE) e regras de persistência de alarme.
- **Business Intelligence (Power BI & Power Query):** Modelagem dimensional star schema, desenvolvimento de medidas em DAX para acompanhamento de faturamento/alarme e design de interface executiva.

> O projeto contendo o modelo estatístico está disponível no repositório. Cada KPI apresentado foi reconciliado com a base higienizada para garantir 100% de integridade dos dados de processo.

## Status do Projeto (Milestones)

| Frente de Trabalho | Status |
|---|---|
| Mapeamento de Sensores e Contexto Físico (Define) | Completo |
| ETL e Engenharia de Parquet (Measure) | Completo |
| Higienização e Auditoria de Qualidade | Completo |
| Validação Estatística de Operação Estável | Completo |
| Containerização com Docker & Docker Compose | Completo |
| Modelagem de Controle Estatístico de Processo (SPC) | Planejado |
| Ingestão e Injeção de Falhas | Planejado |
| Comparação de Modelos de Detecção | Planejado |
| Dashboards de Monitoramento e Controle (Power BI) | Planejado |

## Raio-X do Processo (Resultados de Base)
A base analítica foi validada e auditada, fornecendo a base histórica necessária para o estabelecimento de limites de controle estatístico confiáveis.

| KPI / Métrica | Resultado Auditado | Detalhe Técnico |
|---|---:|---|
| **Amostras Totais** | **730.000** | Leituras de tempo coletadas nas simulações |
| **Simulações de Operação** | **1.000** | Corridas completas de processo para treino e teste |
| **Sinais de Processo** | **52** | 41 variáveis medidas + 11 variáveis manipuladas |
| **Desvio de Distribuição** | **0,019 IQR** | Máximo desvio de mediana entre treino e teste |
| **Integridade de Dados** | **100%** | Zero células vazias, valores infinitos ou chaves duplicadas |

## Indicadores de Processo & Insights
1. **Monitoramento Multivariado:** Como identificar quando o processo sai do seu envelope operacional estável usando métricas unificadas?
2. **Tempo de Detecção:** Quão rápido conseguimos identificar uma falha no sistema após o seu início físico?
3. **Taxa de Alarme Falso:** Como minimizar alertas desnecessários durante a operação normal para não sobrecarregar os operadores?
4. **Isolamento de Causa Raiz:** Quais variáveis (pressão, vazão, temperatura) são as maiores causadoras de um desvio detectado?
5. **Carga de Alarme:** Quantos alarmes confirmados são gerados a cada 100 horas de operação?

## Pipeline de Inteligência (Workflow)

```mermaid
flowchart TD
    A[Dados Brutos - Harvard Dataverse] --> B[Auditoria e Qualidade da Base]
    B --> C[Construção da Linha de Base Estável]
    C --> D[Modelagem SPC - Hotelling T² e Q]
    D --> E[Isolamento de Causa Raiz - Gráficos de Contribuição]
    E --> F[Dashboard de Controle Operacional]
```

## Validação e Higienização de Dados
A consistência dos dados históricos é crítica para o controle estatístico. A auditoria de dados realizou as seguintes verificações automáticas:
- **Integridade de Chave:** Confirmação de que a combinação de `simulationRun` e `sample` é única.
- **Valores Nulos e Infinitos:** Varredura em todas as 52 colunas físicas para assegurar a inexistência de leituras falhas.
- **Comparação de Splits:** Teste estatístico de Kolmogorov-Smirnov para garantir que a partição de teste tem a mesma distribuição da partição de treino (limite de deslocamento máximo de 0,019 IQR respeitado).

## Insights Críticos de Engenharia de Processo
- **Divisão de Normalidade:** Um conjunto independente de testes normais foi mantido exclusivamente para calibrar a taxa de alarmes falsos sob condições não vistas.
- **Variáveis de Processo vs Manipuladas:** Das 52 variáveis, 41 representam sensores diretos de processo (temperaturas, pressões, níveis, composições) e 11 representam as posições de válvulas de controle (manipuladas).
- **Ausência de Dados Financeiros:** A simulação foca puramente em física e controle de processos. Métricas financeiras como economia de matéria-prima ou OEE não serão geradas devido à ausência dessas informações na fonte.

## Arquitetura de Monitoramento (DMAIC)
O projeto é estruturado utilizando a metodologia DMAIC de melhoria contínua:
- **Define:** Mapeamento de problemas operacionais como atrasos de detecção e sobrecarga de alarmes falsos.
- **Measure:** Criação da linha de base de operação normal estável.
- **Analyse:** Identificação das falhas mais críticas e das variáveis físicas correlacionadas com cada desvio.
- **Improve:** Ajuste fino dos limites estatísticos e das regras de persistência (ex: 3 alarmes consecutivos para validar um desvio).
- **Control:** Publicação de views em SQL, dicionários de KPIs e painéis de resposta operacional para a sala de controle.

## Estrutura do Repositório
```text
industrial-anomaly-analytics/
├── config/                  # Paletas visuais e configurações
├── data/                    # Dados locais (raw, interim e processed)
├── docs/                    # Especificação de KPIs, dicionário e charter
├── images/                  # Gráficos exportados para documentação
├── notebooks/               # Análise exploratória e notebooks do leitor
├── powerbi/                 # Arquivo de modelo e layout de dashboard
├── scripts/                 # Scripts Python de download e pipelines
├── sql/                     # Banco DuckDB e views de KPIs
├── src/                     # Módulos Python reutilizáveis
├── tests/                   # Testes unitários e de integridade
├── Dockerfile               # Imagem Docker para execução reprodutível
└── docker-compose.yml       # Orquestração do pipeline analítico e Jupyter
```

## Roteiro de Análise (Notebook Roadmap)

| Ordem | Notebook | Objetivo |
|---|---|---|
| `01` | [01_data_source_and_process_context.ipynb](notebooks/01_data_source_and_process_context.ipynb) | Contextualização do processo químico, definição de variáveis e download. |
| `02` | [02_data_quality_and_operating_baseline.ipynb](notebooks/02_data_quality_and_operating_baseline.ipynb) | Auditoria de integridade física dos dados e validação do baseline estável. |

## Como Reproduzir o Projeto

### Opção A: Execução Containerizada com Docker (Recomendado)

Construa a imagem e execute o pipeline de dados automaticamente:
```bash
# Gerar as tabelas dimensionais e métricas no container
docker compose up analytics --build

# Iniciar o ambiente JupyterLab containerizado (porta 8888)
docker compose up jupyter
```

### Opção B: Execução Local (Python)

```bash
git clone https://github.com/Nayanearaujo/industrial-anomaly-analytics.git
cd industrial-anomaly-analytics
pip install -r requirements.txt

# Download do dataset
python scripts/download_data.py

# Processamento do baseline
python scripts/prepare_normal_baseline.py
```

## Ferramentas Utilizadas
Python · Pandas · NumPy · Plotly · DuckDB · SQL · Docker · Parquet · Jupyter · Pytest · Power BI · GitHub

## Fonte e Licença
- **Dataset:** Tennessee Eastman Process Simulation Data (Harvard Dataverse, DOI: [10.7910/DVN/6C3JR1](https://doi.org/10.7910/DVN/6C3JR1)).
- **Licença:** Código sob [Licença MIT](LICENSE).

Desenvolvido por `Nayane Araujo`