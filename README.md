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
* Operadores (Fase Futura)
* Manutenções Preventivas e Corretivas
* Falhas Aleatórias
* Eventos de Downtime (Quebras e Ociosidades)
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
* Simular a ociosidade operacional (tempo de linha ligada sem Ordens de Produção ativas);
* Simular o fator humano (probabilidade do operador esquecer de desligar o painel/máquinas ao término de uma OP, gerando desgaste fantasma);
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

Seu status é calculated dinamicamente a partir das máquinas que a compõem e da existência de uma Ordem de Produção ativa.

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

## Production Order (OP) & Ociosidade

Cada Ordem de Produção representa uma missão temporária de fabricação com metas específicas. Porém, a API suporta o funcionamento de uma fábrica real, distinguindo **tempo produtivo** de **tempo ocioso**:

* **Produção Ativa (Com OP):** O simulador monitora o progresso, desvia peças para análise de qualidade (aprovadas vs. rejeitadas) e calcula o OEE focado naquele lote. Quando a quantidade planejada é atingida, a OP é finalizada automaticamente.
* **Ociosidade Operacional (Sem OP):** O motor de simulação permite que a linha continue rodando mesmo sem uma OP ativa. Nesse cenário, o sistema registra automaticamente eventos de **Downtime por Ociosidade (Idle)** para fins de análise de eficiência e desperdício de energia.
* **Simulação de Falha Humana:** Ao término de uma OP, o sistema roda um cálculo probabilístico de erro humano. Há uma chance de o operador esquecer de desligar o painel, fazendo com que as máquinas continuem ligadas no status `PRODUCTION`, gerando desgaste físico desnecessário ("desgaste fantasma") e penalizando o OEE da linha até que a falha seja corrigida.

---

## Fluxo e Desacoplamento da Produção

A simulação física e o software de gestão da produção são completamente desacoplados no sistema:

1. **A Linha Produz:** A cada tick físico da simulação, se todas as máquinas da célula estiverem ativas, a linha gera um volume bruto de peças físicas (independente de ter uma OP ou não) e incrementa seu totalizador de produção acumulada.
2. **A OP Inspeciona:** Caso exista uma OP ativa, os dados físicos de produção do ciclo são transmitidos via passagem de eventos para o simulador de OP, que assume o papel do controle de qualidade, realizando a análise de refugo (separando as peças em aprovadas ou rejeitadas) de forma isolada na memória.

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

## 📊 O Motor de OEE (Tempo Real)
O sistema calcula o OEE da fábrica de forma dinâmica a cada minuto via Celery, dividindo a métrica em três pilares decimais normalizados antes da consolidação:
- **Disponibilidade:** Tempo de produção ativo vs. Tempo de relógio corrido da OP.
- **Performance:** Ritmo real de produção (peças/min) vs. Ciclo ideal planejado.
- **Qualidade:** Índice de peças boas vs. Total de peças produzidas.

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
* Registro de Downtime (Falhas e Ociosidades por linha)
* Simulação de Produção Desacoplada (Física vs. Qualidade)
* Simulação de Desgaste Realista
* Simulação de Falhas e Comportamento de Operadores (Fator Humano)
* Geração de Apontamentos (Snapshots)
* Cálculo Automático de OEE em Tempo Real
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

---

# 🔮 Próximos Passos & Roadmap de Desenvolvimento

O desenvolvimento do Gêmeo Digital está estruturado em marcos de evolução incremental para garantir robustez arquitetural em cada nova mecânica introduzida:

### 📅 Fase 1: Escala Temporal & Relógio de Fábrica (Time Dilation)
* [ ] **Time Dilation Engine:** Implementar um relógio interno virtual onde **1 dia completo de produção simulada equivale a exatamente 30 minutos em tempo real**.
* [ ] **Sincronização do Celery:** Adaptar os ticks físicos e analíticos para responderem a essa nova escala de tempo acelerada, permitindo simular semanas de operação industrial em poucas horas de execução física.

### 📅 Fase 2: Painel de Controle Haptic & Interatividade Avançada
* [ ] **Controles de Simulação (Hot-Swapping):** Permitir pausar, retomar e acelerar/desacelerar o fluxo do tempo da fábrica via chamadas de API.
* [ ] **Ajustes Finos em Tempo Real:** Permitir que o usuário adicione novas máquinas a uma linha ativa, altere parâmetros de velocidade nominal das máquinas e recalibre taxas de falha em pleno funcionamento.

### 📅 Fase 3: Escalas de Trabalho & Alocação de Operadores
* [ ] **Turnos de Trabalho:** Implementação de perfis de operadores trabalhando em turnos dinâmicos baseados no Relógio de Fábrica.
* [ ] **Fadiga & Eficiência Individual:** Operadores terão taxas de atenção e cansaço. Operadores cansados aumentam a taxa de refugo de peças (Qualidade do OEE) e têm maior probabilidade de esquecer as máquinas ligadas ao término de um lote.
* [ ] **Eventos de Setup (Troca de Lote):** O tempo de transição entre uma OP concluída e o início de uma nova dependerá da velocidade e habilidade do operador escalado na linha.

### 📅 Fase 4 (sujeita a alterações): Inteligência Artificial (Reinforcement Learning com Gymnasium)
* [ ] **Ambiente OpenAI Gymnasium (IA):** Envelopar todo o ecossistema consolidado dentro da especificação de ambiente do Gymnasium.
* [ ] **Agente Gestor Autônomo:** Treinar um modelo de Aprendizado por Reforço que consumirá as leituras físicas do simulador (estados das máquinas, metas, tempo de turno) e atuará de forma autônoma decidindo velocidades de linha e paradas preventivas para otimizar o OEE geral e mitigar falhas humanas.
