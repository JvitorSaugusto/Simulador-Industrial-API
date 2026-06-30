# Especificação Técnica: Motor de Cálculo do OEE em Tempo Real

Este documento detalha a arquitetura lógica e matemática utilizada pelo sistema para calcular o **OEE (Overall Equipment Effectiveness)** em tempo real (Nível 1). O motor opera de forma dinâmica, adaptando-se ao comportamento do chão de fábrica minuto a minuto através de processamento assíncrono.

---

## 🎯 Filosofia do Cálculo (Tempo Real vs. Tradicional)

Diferente do OEE tradicional, que utiliza turnos fixos e planejamentos estáticos, este sistema adota uma abordagem **dinâmica de linha do tempo**. Os indicadores são calculados com base no tempo de relógio decorrido desde o início real da Ordem de Produção ($actual\_start$).

* **Escala de Processamento:** Para garantir a consistência matemática e evitar distorções, todos os três pilares (Disponibilidade, Desempenho e Qualidade) são calculados internamente em **escala decimal** ($0.0$ a $1.0$). 
* **Consolidação:** A conversão para base percentual ($0\%$ a $100\%$) ocorre exclusivamente na consolidação do OEE final.

---

## 📊 Os Três Pilares do OEE

### 1. Disponibilidade (Availability)
Mede a eficiência de tempo da linha de produção. Indica a fração de tempo em que a linha passou efetivamente produzindo em relação ao tempo total decorrido desde o início da operação.

#### Variáveis:
* **Total Run Time ($T_{total}$):** Tempo total em minutos desde o início real da OP até o momento atual.
  $$T_{total} = \frac{\text{Agora} - \text{Data de Início Real}}{60 \text{ segundos}}$$
* **Current Stop Time ($T_{stop}$):** Somatória das durações (em minutos) de todos os eventos de parada não-programada ($DownTimeEvents$) registrados para a OP ativa.
* **Runtime ($Runtime$):** Tempo operacional líquido.
  $$Runtime = T_{total} - T_{stop}$$

#### Fórmula:
$$Disponibilidade = \frac{Runtime}{T_{total}}$$

> 📌 *Nota de Segurança:* Se $T_{total} \le 0$ (exatamente no milissegundo de início da OP), o sistema assume o valor padrão de $1.0$ ($100\%$).

---

### 2. Desempenho (Performance)
Mede o ritmo de produção da linha, comparando a velocidade atual do simulador com a velocidade ideal planejada na criação da Ordem de Produção.

#### Variáveis:
* **Ciclo Ideal ($C_{ideal}$):** Ritmo esperado de produção configurado na OP (produtos por minuto).
  $$C_{ideal} = \frac{\text{Quantidade Planejada}}{\text{Tempo Planejado em Minutos}}$$
* **Ciclo Real ($C_{real}$):** Ritmo de produção executado pela linha até o momento atual (produtos por minuto).
  $$C_{real} = \frac{\text{Quantidade Produzida Atual}}{Runtime}$$

#### Fórmula:
$$Desempenho = \frac{C_{real}}{C_{ideal}}$$

> 💡 *Comportamento Industrial:* Caso as máquinas operem em uma velocidade superior à meta planejada, o $C_{real}$ superará o $C_{ideal}$. Portanto, **o pilar de Desempenho pode legitimamente ultrapassar $1.0$ ($100\%$)** em tempo real.

---

### 3. Qualidade (Quality)
Mede a eficiência de conformidade dos produtos que passaram pela linha, avaliando o índice de peças boas em relação ao total produzido.

#### Variáveis:
* **Quantidade de Peças Boas ($Q_{good}$):** Total de produtos aceitáveis acumulados na OP.
* **Quantidade Total Produzida ($Q_{total}$):** Somatória de todas as peças que passaram pela linha (Boas + Refugos/Defeituosas).

#### Fórmula:
$$Qualidade = \frac{Q_{good}}{Q_{total}}$$

> 📌 *Nota de Segurança:* Se $Q_{total} == 0$ (nenhuma peça produzida ainda), o sistema assume o valor padrão de $1.0$ ($100\%$) para evitar divisões por zero.

---

## 🏁 Consolidação do OEE Final

O OEE final é o produto matemático dos três pilares fundamentais. A fórmula multiplica os valores decimais e aplica a conversão percentual na última etapa:

$$OEE = (Disponibilidade \times Desempenho \times Qualidade) \times 100$$

---

## 🛠️ Arquitetura de Código (Design Pattern)

O sistema implementa o padrão de **Orquestrador Centralizado** dentro da camada de serviços (`OeeRecordService`). 

1. **Minimização de I/O:** O método orquestrador realiza as consultas de banco de dados (busca da OP ativa e somatória de paradas) de forma assíncrona uma **única vez**.
2. **Funções Puras:** Os tempos extraídos são distribuídos para funções matemáticas puras, síncronas e isoladas. Isso garante isolamento lógico, facilidade para testes unitários e consistência temporal (todas as fórmulas utilizam exatamente o mesmo milissegundo de referência).