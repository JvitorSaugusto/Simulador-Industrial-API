# 🏭 Industrial Digital Twin API

Uma API assíncrona de alta performance desenvolvida em **Python** para simulação de ambientes industriais, gerenciamento de linhas de produção, monitoramento de máquinas e cálculo automatizado de indicadores de eficiência (**OEE - Overall Equipment Effectiveness**).

O projeto implementa um **Digital Twin** (gêmeo digital) de uma fábrica, reproduzindo virtualmente o comportamento de uma linha de produção através de um motor de simulação executado em segundo plano. Durante a execução da simulação, o sistema é capaz de produzir peças, gerar falhas, realizar manutenções, calcular indicadores industriais e disponibilizar informações para dashboards e análises gerenciais.

---

# 💡 Origem e Contexto do Projeto

Este projeto foi inspirado na minha experiência prática desenvolvendo sistemas para ambientes industriais.

Diversas regras de negócio, comportamentos e conceitos implementados aqui foram baseados em situações reais encontradas durante o desenvolvimento de soluções para monitoramento de produção, rastreamento de eventos industriais e cálculo de indicadores de desempenho.

O objetivo é criar uma arquitetura próxima à encontrada em sistemas industriais modernos, utilizando boas práticas de engenharia de software e processamento assíncrono.

---

# 🏭 O que a API Simula

A fábrica virtual é composta por diversos elementos que interagem continuamente.

Durante a simulação o sistema é capaz de representar:

* Linhas de Produção
* Máquinas Industriais
* Ordens de Produção (Production Orders)
* Operadores
* Manutenções Preventivas e Corretivas
* Falhas Aleatórias
* Eventos de Downtime
* Apontamentos de Produção
* Indicadores OEE
* Relatórios Gerenciais

---

# ⚙️ Motor de Simulação

O coração da aplicação é um ecossistema executado em segundo plano utilizando **Celery** e **Redis**.

As tarefas assíncronas simulam continuamente o funcionamento da fábrica, sendo responsáveis por:

* Simular produção das linhas;
* Atualizar velocidade atual de produção;
* Incrementar desgaste das máquinas;
* Gerar falhas probabilísticas;
* Atualizar tempos de operação;
* Executar manutenções;
* Criar apontamentos de produção;
* Calcular automaticamente indicadores de OEE;
* Atualizar métricas utilizadas pelos dashboards.

Toda a simulação utiliza regras probabilísticas baseadas em **Random**, fazendo com que cada execução da fábrica seja diferente da anterior.

---

# 🏭 Modelo da Produção

A arquitetura foi baseada em um ambiente industrial onde as **Ordens de Produção são executadas por Linhas de Produção**, e não diretamente por máquinas individuais.

## Production Line

Cada linha representa uma célula produtiva composta por diversas máquinas.

A linha mantém informações relacionadas ao seu estado atual, como:

* Meta de OEE
* Capacidade ideal de produção
* Velocidade atual de produção
* Tempo atual de operação
* Tempo total de operação

Seu status é calculado dinamicamente a partir das máquinas que a compõem e da existência de uma Ordem de Produção ativa.

---

## Machine

Cada linha possui diversas máquinas.

As máquinas são responsáveis por:

* Produzir peças;
* Sofrer desgaste gradual;
* Gerar falhas;
* Entrar em manutenção.

Caso qualquer máquina apresente uma falha crítica, toda a linha de produção é interrompida automaticamente.

---

## Production Order (OP)

Cada Ordem de Produção representa uma missão temporária de fabricação.

Ela contém informações como:

* Produto
* Quantidade planejada
* Quantidade produzida
* Quantidade aprovada
* Quantidade rejeitada
* Linha responsável pela execução

Quando a quantidade planejada é atingida, a OP é finalizada automaticamente e a linha retorna ao estado **Idle**.

---

## Simulação da Produção

Durante a execução de uma OP, o simulador reproduz a passagem de peças pela linha de produção.

A cada ciclo de simulação o sistema pode:

* Produzir novas peças;
* Classificar peças como aprovadas ou rejeitadas;
* Variar a velocidade de produção;
* Atualizar o desgaste das máquinas;
* Verificar ocorrência de falhas;
* Atualizar indicadores da OP.

Esses eventos são executados continuamente enquanto existir uma Ordem de Produção ativa.

---

## Production Records

O sistema gera apontamentos periódicos da produção.

Esses registros representam snapshots da execução da fábrica e serão utilizados para:

* Auditoria;
* Histórico da produção;
* Dashboards;
* Relatórios;
* Cálculo dos indicadores de desempenho.

---

# 📊 Cálculo do OEE

Durante toda a execução da Ordem de Produção o sistema calcula automaticamente os três pilares do OEE:

* Availability
* Performance
* Quality

A partir desses indicadores é obtido o OEE global da produção.

---

# 🏛️ Arquitetura

O projeto foi desenvolvido utilizando uma arquitetura modular baseada em responsabilidades.

Cada domínio possui sua própria estrutura contendo:

* Models
* Schemas
* Services
* Routers
* Enums
* Validators
* Exceptions
* Background Tasks
* Tests

A lógica de negócio permanece centralizada na camada de **Services**, enquanto os **Routers** são responsáveis apenas pela comunicação HTTP e os **Schemas** pela validação dos dados.

Entre as práticas adotadas destacam-se:

* Arquitetura modular por domínio;
* Injeção de dependências;
* Separação entre Schemas de Request e Response;
* Enumeração utilizando `TextChoices`/Enums;
* Processamento assíncrono com Celery;
* Gerenciamento transacional;
* Validação centralizada;
* Tratamento global de exceções.
* Testes Unitários

---

# 🚀 Tecnologias Utilizadas

* Python 3.13+
* FastAPI
* SQLAlchemy (Async)
* Pydantic V2
* PostgreSQL
* Alembic
* Celery
* Redis
* Docker
* Docker Compose
* Ruff
* Pytest
* Faker

---

# 📈 Funcionalidades

* CRUD de Linhas de Produção
* CRUD de Máquinas
* CRUD de Operadores
* CRUD de Ordens de Produção
* CRUD de Manutenções
* Registro de Falhas
* Registro de Downtime
* Simulação de Produção
* Simulação de Desgaste
* Simulação de Falhas
* Geração de Apontamentos
* Cálculo Automático de OEE
* Dashboard Industrial
* Relatórios Gerenciais
* API REST Documentada

---

# 🎯 Objetivos do Projeto

Este projeto tem como objetivo aprofundar conhecimentos em:

* Arquitetura de Software
* FastAPI
* SQLAlchemy Assíncrono
* Celery
* Redis
* Sistemas Distribuídos
* Processamento Assíncrono
* Simulação Baseada em Eventos
* Engenharia de Software
* Modelagem de Sistemas Industriais
* APIs REST de Alta Performance
* Boas Práticas de Desenvolvimento Backend

