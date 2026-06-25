```markdown
# 🏭 Industrial Simulator & OEE Tracker API

Uma API assíncrona de alta performance desenvolvida em Python para simulação de linhas de produção industrial, monitoramento de status de máquinas em tempo real e rastreamento automatizado de ociosidade (*Idle Time* / *Down Time*).

O core do sistema conta com um motor de simulação dinâmica rodando em segundo plano (via tarefas agendadas), capaz de mimetizar o desgaste de componentes físicos de uma fábrica, calcular a eficiência global dos ativos (**OEE - Overall Equipment Effectiveness**) e expor métricas cruciais para tomadas de decisão gerenciais.

---

## 💡 Origem e Contexto do Projeto

Este projeto não é apenas um exercício teórico. A arquitetura e as regras de negócio aqui implementadas foram diretamente inspiradas na minha **vivência prática no desenvolvimento de sistemas industriais reais** (como o ecossistema SOLVEOEE). 

Trazer as dores reais do chão de fábrica para o código me permitiu desenhar uma solução que resolve problemas complexos de engenharia de software e automação, tais como:
* **Concorrência e Alta Disponibilidade:** Lidando com múltiplos sensores virtuais enviando dados simultaneamente através de rotas assíncronas (`async/await`).
* **Consistência de Estados Complexos:** Rastrear exatamente quando uma linha entra em ociosidade pelo simples fato de não haver nenhuma Ordem de Produção (OP) ativa vinculada a ela.
* **Processamento Assíncrono Pesado:** Desacoplar a lógica da API web das simulações contínuas de desgaste e falha de maquinário utilizando filas de mensageria.

---

## ⚙️ O Motor de Simulação (Background Ecosystem)

Para dar vida ao monitoramento, o projeto implementa um ecossistema robusto baseado em **Celery** e **Redis**, que atua como o "coração pulsante" da fábrica virtual:

1. **Simulação de Desgaste (`Wear Level`):** Workers assíncronos rodam periodicamente incrementando o nível de desgaste das máquinas com base em suas taxas de falha base e tempo em produção.
2. **Geração de Eventos Estocásticos:** O sistema simula paradas imprevistas (quebras ou falhas micro-paradas) de forma automatizada com base na saúde física atual de cada máquina.
3. **Cálculo de Ociosidade em Tempo Real:** Rotinas de background cruzam os horários de funcionamento das máquinas com o status das Ordens de Produção (OP), calculando automaticamente as janelas de *Down Time* e deixando os eventos prontos para serem classificados e justificados pelos operadores na interface.
---

##  Tecnologias Utilizadas

* **Python 3.11+**
* **FastAPI**: Framework web de alta performance para a construção de APIs.
* **SQLAlchemy (Async)**: ORM mapeado para operações assíncronas com o banco de dados.
* **Pydantic V2**: Validação de dados e mapeamento de Schemas (utilizando `model_config`).
* **Celery & Redis**: Orquestração e processamento de tarefas em segundo plano (como incremento de desgaste de máquinas e checagem de ociosidade).
* **PostgreSQL / SQLite**: Banco de dados relacional para persistência dos dados industriais.

---

##  Arquitetura e Padrões de Projeto

A API foi desenhada seguindo as melhores práticas de mercado, priorizando o desacoplamento e a consistência dos dados:

* **Padrão por Feature/Módulo**: Divisão limpa de responsabilidades entre `Models`, `Schemas`, `Services` e `Routers`.
* **Injeção de Dependência Encadeada**: Services injetados via construtor (`__init__`), permitindo alta testabilidade.
* **Gerenciamento de Transação Única (Atomicidade)**: Operações compostas (ex: parar uma máquina e gerar um evento de Down Time) compartilham a mesma sessão e utilizam um único `commit` ao final do fluxo (*princípio do tudo ou nada*).
* **Centralização de Erros**: Tratamento global de exceções customizadas através de Handlers isolados no FastAPI.

---

##  Como Instalar e Rodar o Projeto

### 1. Clonar o Repositório
```bash
git clone [https://github.com/seu-usuario/nome-do-repositorio.git](https://github.com/seu-usuario/nome-do-repositorio.git)
cd nome-do-repositorio

```

### 2. Configurar o Ambiente Virtual (venv)

```bash
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

```

### 3. Instalar as Dependências

```bash
pip install -r requirements.txt

```

### 4. Rodar a API (FastAPI)

```bash
fastapi dev main.py
# Ou usando uvicorn:
uvicorn main:app --reload

```

A documentação interativa da API ficará disponível em: `http://localhost:8000/docs`

### 5. Rodar o Worker do Celery (Background Tasks)

Certifique-se de que o Redis (ou o broker de sua escolha) está rodando e execute:

```bash
celery -A tasks.celery_app worker --loglevel=info

```

---
# 📊 Entidades Principais da Regra de Negócio
#* **Linha de Produção (Production Line):** Agrupa um conjunto de máquinas e gerencia o fluxo de fabricação. É o coração do cálculo de ociosidade (*Idle Time*) do sistema quando não há Ordens de Produção ativas.
* **Máquina (Machine):** Unidade fabril individual. Possui métricas como taxa de falha base, nível de desgaste (`wear_level` incrementado via Celery) e controle estrito de timestamps de atividade (`last_start_time`, `last_stop_time`).
* **Ordem de Produção - OP (Production Order):** Dita o planejamento da fábrica. Controla o status real da produção (Pendente, Em Produção, Finalizado) e armazena os registros cruciais de tempo real de início e fim (`actual_start`, `actual_end`).
* **Eventos de Parada (Down Time Events):** Gerados automaticamente pelo sistema (de forma não classificada) sempre que uma máquina interrompe sua atividade. Permite que operadores entrem no sistema posteriormente para justificar o motivo (*reason*) e adicionar observações (*comments*).
* **Métricas de OEE (Overall Equipment Effectiveness):** O indicador consolidado calculado de forma automatizada pelo sistema, avaliando a Disponibilidade, Performance e Qualidade das linhas de produção com base no histórico de OP e Down Times.

* ```
