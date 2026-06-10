# Helmsman

Auto-scaler fuzzy para serviços web rodando em Docker. Em vez de limiares binários ("se CPU > 80%, escala"), o Helmsman lê três sinais ao mesmo tempo — CPU, RAM e requisições por segundo — e toma decisões graduais usando lógica fuzzy Mamdani.

---

## Por que fuzzy?

Auto-scalers baseados em limiares rígidos tomam decisões sem contexto: se CPU > 80%, escala. Isso ignora que 80% de CPU com zero requisições é um leak, não demanda — e escalar nesse caso não resolve nada.

A lógica fuzzy combina os três sinais antes de agir, permitindo expressar conhecimento de domínio diretamente em regras linguísticas:

| Situação | Limiar rígido | Helmsman |
|---|---|---|
| CPU 85% com zero requisições | Escala (errado) | Detecta anomalia, alerta, não escala |
| RAM crítica com demanda alta | Escala (pode derrubar o host) | Bloqueia scale up, emite alerta crítico |
| RPS alto com CPU baixa | Escala sem contexto | Escala e redistribui tráfego entre réplicas |
| CPU em 79% vs 81% | Decisões completamente diferentes | Transição suave e gradual |

### Simplicidade como princípio

Ferramentas como o HPA do Kubernetes exigem cluster, kubeconfig, manifestos YAML e permissões de API. O Helmsman é uma biblioteca Python que funciona com qualquer serviço já rodando em Docker:

```bash
pip install helmsman
helmsman start --host localhost --port 8000 --container meu-servico
```

Sem arquivos de configuração. Sem infraestrutura adicional. O usuário define apenas o que o seu serviço aguenta (`--rps-per-replica`) e o Helmsman cuida do resto — inclusive subindo um proxy nginx transparente na frente do serviço para coletar métricas sem modificar nada no app existente.

---

## Como funciona

```
helmsman start [params]
      │
      ▼
Sobe nginx sidecar na frente do serviço
(proxy transparente — conta req/s pelo access.log)
      │
      ▼
Loop a cada N segundos:
  coleta CPU e RAM via docker stats
  coleta RPS via leitura do nginx access.log
      │
      ▼
Motor Fuzzy Mamdani:
  fuzzificação → 22 regras → agregação → defuzzificação
      │
      ▼
Ação:
  scale up / scale down via docker-py
  atualiza upstream do nginx → distribui tráfego entre todas as réplicas
  emissão de alerta (warning / critical)
      │
      ▼
Dashboard em http://localhost:8800
```

O serviço do usuário **não é modificado**. O nginx sobe na frente dele como sidecar, conta as requisições e repassa o tráfego de forma transparente.

Quando o motor decide escalar, o nginx é reconfigurado automaticamente: cada nova réplica entra no bloco `upstream` e passa a receber tráfego por round-robin. O reload é gracioso — sem derrubar conexões em andamento. No scale down, as réplicas removidas saem do upstream antes de serem desligadas.

---

## Motor Fuzzy

### Entradas — universo 0–100%

| Variável | O que mede | Como é calculado |
|---|---|---|
| `cpu_pct` | Uso de CPU dos containers em relação ao host | `cpu_containers / cpu_host × 100` |
| `ram_pct` | Uso de RAM dos containers em relação ao host | `ram_containers / ram_host × 100` |
| `rps_pct` | Requisições atuais em relação à capacidade configurada | `rps_atual / (réplicas × rps_per_replica) × 100` |

O `rps_per_replica` é definido pelo usuário na CLI — é ele quem decide o que é "cheio" para o seu serviço.

### Saídas

| Variável | Universo | Decisão concreta |
|---|---|---|
| `delta_replicas` | −3 a +5 | Arredondado para inteiro; aplicado dentro dos limites min/max |
| `alerta` | 0–100 | 0–33 → none · 34–66 → warning · 67–100 → critical |

### Funções de pertinência (entradas)

As três entradas compartilham os mesmos quatro termos:

```
Baixo    ████▓░░░░░░░░░░░░░░░░  trapmf [0, 0, 20, 40]
Moderado ░░░░▓████▓░░░░░░░░░░░  trimf  [20, 45, 70]
Alto     ░░░░░░░░░▓████▓░░░░░░  trimf  [55, 72, 88]
Crítico  ░░░░░░░░░░░░░▓████████  trapmf [75, 88, 100, 100]
         0   20   40   60   80  100
```

A sobreposição entre os termos é intencional — na faixa 55–70% o sistema pondera Alto e Moderado ao mesmo tempo, gerando decisões graduais em vez de saltos abruptos.

### Base de regras (22 regras)

#### Grupo 1 — Sistema ocioso, scale down

| cpu | ram | rps | delta | alerta | Lógica |
|---|---|---|---|---|---|
| Baixo | Baixo | Baixo | Derrubar forte | Nenhum | Completamente ocioso |
| Baixo | Baixo | Moderado | Manter | Nenhum | Ainda tem tráfego, não derruba |
| Moderado | Baixo | Baixo | Derrubar | Nenhum | CPU moderada sem demanda |

#### Grupo 2 — RPS alto respeita o limite configurado

| cpu | ram | rps | delta | alerta | Lógica |
|---|---|---|---|---|---|
| Baixo | Baixo | Alto | Subir | Nenhum | Atingiu o limite do rps_per_replica |
| Baixo | Moderado | Alto | Subir | Nenhum | Idem, RAM crescendo |

#### Grupo 3 — Carga real, scale up normal

| cpu | ram | rps | delta | alerta | Lógica |
|---|---|---|---|---|---|
| Moderado | Moderado | Alto | Subir | Nenhum | Pressão confirmada nos três sinais |
| Alto | Moderado | Alto | Subir | Nenhum | CPU alta com demanda alta |
| Moderado | Alto | Alto | Subir | Warning | RAM alta com demanda crescente |

#### Grupo 4 — Carga crítica, scale up urgente

| cpu | ram | rps | delta | alerta | Lógica |
|---|---|---|---|---|---|
| Alto | Alto | Alto | Subir forte | Warning | Saturação generalizada |
| Crítico | Moderado | Alto | Subir forte | Warning | CPU crítica com demanda alta |
| Alto | Moderado | Crítico | Subir forte | Critical | Demanda crítica no limite da capacidade |

#### Grupo 5 — Host cheio, bloqueia scale up

| cpu | ram | rps | delta | alerta | Lógica |
|---|---|---|---|---|---|
| Alto | Crítico | Alto | Manter | Critical | Subir container derrubaria o host |
| Crítico | Crítico | Crítico | Manter | Critical | Colapso iminente — intervenção humana |

#### Grupo 6 — Anomalias (possíveis leaks)

| cpu | ram | rps | delta | alerta | Lógica |
|---|---|---|---|---|---|
| Alto | Baixo | Baixo | Manter | Warning | Suspeita de CPU leak |
| Crítico | Baixo | Baixo | Derrubar | Critical | CPU crítica sem demanda — processo travado |
| Baixo | Alto | Baixo | Derrubar | Warning | Suspeita de memory leak |
| Baixo | Crítico | Baixo | Derrubar forte | Critical | Memory leak severo |
| Alto | Alto | Baixo | Derrubar | Critical | CPU e RAM altas sem demanda |

#### Grupo 7 — RPS crítico com recursos livres

| cpu | ram | rps | delta | alerta | Lógica |
|---|---|---|---|---|---|
| Baixo | Baixo | Crítico | Subir | Warning | Capacidade esgotada, recursos livres |
| Moderado | Baixo | Crítico | Subir forte | Warning | CPU crescendo + capacidade no limite |
| Baixo | Moderado | Crítico | Subir | Warning | RAM crescendo + capacidade no limite |
| Moderado | Moderado | Crítico | Subir forte | Warning | Tudo crescendo, escala agressiva |

### Mecanismo de inferência

- **AND entre antecedentes:** mínimo — `μ_AND = min(μ_A, μ_B, μ_C)`
- **Implicação:** mínimo (truncamento do consequente)
- **Agregação:** máximo entre todas as regras ativas
- **Defuzzificação:** centróide — `z* = ∫ z·μ(z)dz / ∫ μ(z)dz`

O valor contínuo de `delta_replicas` é arredondado para o inteiro mais próximo e aplicado respeitando os limites `min_replicas` e `max_replicas`.

---

## Motor Algoritmo Genético (`--mode ag`)

Como alternativa ao motor fuzzy, o Helmsman implementa um Algoritmo Genético do zero (apenas `random` da stdlib) que evolui, a cada ciclo de monitoramento, um cromossomo:

```text
[n_replicas, sla_threshold]
  n_replicas    — número de réplicas candidato (min_replicas .. max_replicas)
  sla_threshold — limiar de ocupação (%) a partir do qual há sobrecarga (70..95)
```

| Parâmetro | Valor |
|---|---|
| Tamanho da população | 20 |
| Gerações | 50 |
| Seleção | Torneio (k=3) |
| Crossover | Média dos genes dos pais |
| Mutação | 20% por gene |

A função de aptidão (a minimizar) combina: custo por réplica, risco de sobrecarga simulado pelo motor fuzzy Mamdani (`alert_score` de `engine.infer`), penalidade de SLA, instabilidade (mudança brusca de réplicas) e conservadorismo do `sla_threshold`. Detalhes e a comparação contra um AG sem componente fuzzy e contra uma heurística simples estão em `docs/relatorio.tex`.

Para usar:

```bash
helmsman start --host localhost --port 8000 --container meu-servico --mode ag
```

---

## Instalação

```bash
git clone <repo>
cd Helmsman

pip install -e .
```

Para incluir o dashboard buildado no pacote:

```bash
./scripts/build_frontend.sh
pip install -e .
```

---

## Como usar

O serviço alvo precisa estar rodando como container Docker antes de iniciar o Helmsman.

```bash
# uso básico
helmsman start --host localhost --port 8000 --container nome-do-container

# com parâmetros completos
helmsman start \
  --host localhost \
  --port 8000 \
  --container nome-do-container \
  --min-replicas 1 \
  --max-replicas 5 \
  --rps-per-replica 30 \
  --poll-interval 5 \
  --mode fuzzy
```

`--rps-per-replica` define o limite de requisições por segundo que um container aguenta. É o parâmetro mais importante para calibrar o sistema ao seu serviço.

`--mode` seleciona o motor de decisão: `fuzzy` (padrão, lógica Mamdani) ou `ag` (Algoritmo Genético — ver seção [Motor Algoritmo Genético](#motor-algoritmo-genético---mode-ag)).

```bash
helmsman status   # réplicas ativas, última decisão e alerta
helmsman logs     # histórico de decisões
helmsman stop     # encerra containers gerenciados
```

### Dashboard

Acessível em `http://localhost:8800` enquanto o Helmsman estiver rodando. Atualiza automaticamente a cada 3 segundos.

### Modo desenvolvimento (front com hot reload)

```bash
# terminal 1
helmsman start --host localhost --port 8000 --container meu-servico

# terminal 2
cd frontend && npm install && npm run dev
# http://localhost:5173
```

---

## Teste de carga

Com [k6](https://k6.io) instalado:

```bash
# perfil completo (~6 min) — exercita todos os grupos de regras
k6 run tests/k6/load.js

# teste rápido
k6 run --vus 50 --duration 30s tests/k6/load.js
```

O tráfego deve passar pelo nginx sidecar (`http://localhost:8080`), não direto no serviço, para ser contado no RPS.

## Cenários de teste

```bash
python tests/scenarios.py        # 12 cenários — motor fuzzy
python tests/ag_scenarios.py     # 12 cenários x 5 seeds — motor AG
python tests/ag_comparison.py    # heurística simples vs AG-puro vs AG-fuzzy
```

`scenarios.py` roda os 12 cenários definidos na base teórica e verifica se o motor fuzzy produz os deltas e alertas esperados. `ag_scenarios.py` roda os mesmos cenários com o motor AG em 5 sementes distintas. `ag_comparison.py` compara as três abordagens de decisão lado a lado.
