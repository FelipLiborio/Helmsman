"""Motor de auto-scaling baseado em Algoritmo Genético — alternativa ao Mamdani fuzzy.

Implementação 100% Python puro: apenas `random` e `math`.

Cromossomo: [n_replicas, sla_threshold]
  n_replicas    — número de réplicas recomendado (int, min_rep .. max_rep)
  sla_threshold — limiar de ocupação a partir do qual considera sobrecarga (int, 70..95)
"""

# uv run helmsman start --host localhost --port 8003 --container helmsman-server-test --rps-per-replica 400 --mode ag
import random
import math  # noqa: F401 — disponível para extensões futuras

from .engine import infer

_SLA_MIN = 70
_SLA_MAX = 95

Cromossomo = list[int]  # [n_replicas, sla_threshold]


# ---------------------------------------------------------------------------
# Função de aptidão
# ---------------------------------------------------------------------------


def fitness(cromossomo: Cromossomo, estado: dict) -> float:
    """
    Avalia um cromossomo [n_replicas, sla_threshold] dado o estado atual,
    usando o motor fuzzy Mamdani para estimar o risco da configuração proposta.
    Quanto menor o valor, melhor o indivíduo.

    cromossomo[0] — n_replicas
    cromossomo[1] — sla_threshold (inteiro 70-95)

    Termos:
      custo                  — menos réplicas = menor custo operacional
      penalidade_fuzzy       — risco estimado pelo motor Mamdani para o cenário simulado
      penalidade_sla         — penaliza ultrapassar o sla_threshold proposto
      instabilidade          — evita variações bruscas desnecessárias
      conservadorismo_sla    — penaliza thresholds extremos (muito altos ou muito baixos)
    """
    n_replicas = cromossomo[0]
    sla_threshold = cromossomo[1]  # inteiro 70-95

    capacidade = n_replicas * estado["rps_per_replica"]
    sim_rps_pct = (estado["rps_real"] / capacidade * 100) if capacidade > 0 else 100.0
    sim_rps_pct = max(0.0, min(100.0, sim_rps_pct))

    resultado_fuzzy = infer(estado["cpu_pct"], estado["ram_pct"], sim_rps_pct)

    custo = n_replicas * 1.1

    penalidade_fuzzy = resultado_fuzzy.alert_score * 1.4

    penalidade_sla = max(0.0, sim_rps_pct - sla_threshold) * 10.0

    instabilidade = abs(n_replicas - estado["replicas_atuais"]) * 0.8

    conservadorismo_sla = 0.0
    if sla_threshold > 90:
        conservadorismo_sla += (sla_threshold - 90) * 2.0
    if sla_threshold < 75:
        conservadorismo_sla += (75 - sla_threshold) * 1.5

    return (
        custo
        + penalidade_fuzzy
        + penalidade_sla
        + instabilidade
        + conservadorismo_sla
    )


# ---------------------------------------------------------------------------
# Operadores genéticos
# ---------------------------------------------------------------------------


def _inicializar_populacao(
    tamanho: int, min_rep: int, max_rep: int
) -> list[Cromossomo]:
    return [
        [random.randint(min_rep, max_rep), random.randint(_SLA_MIN, _SLA_MAX)]
        for _ in range(tamanho)
    ]


def _selecao_torneio(
    populacao: list[Cromossomo],
    fitnesses: list[float],
    k: int = 3,
) -> Cromossomo:
    candidatos = random.sample(range(len(populacao)), k)
    melhor = min(candidatos, key=lambda i: fitnesses[i])
    return populacao[melhor]


def _crossover(pai1: Cromossomo, pai2: Cromossomo) -> Cromossomo:
    return [
        round((pai1[0] + pai2[0]) / 2),
        round((pai1[1] + pai2[1]) / 2),
    ]


def _mutacao(
    cromossomo: Cromossomo, min_rep: int, max_rep: int, taxa: float = 0.2
) -> Cromossomo:
    novo = list(cromossomo)
    if random.random() < taxa:
        novo[0] = max(min_rep, min(max_rep, novo[0] + random.choice([-1, 1])))
    if random.random() < taxa:
        novo[1] = max(_SLA_MIN, min(_SLA_MAX, novo[1] + random.choice([-1, 1])))
    return novo


# ---------------------------------------------------------------------------
# Loop evolutivo principal
# ---------------------------------------------------------------------------


def evoluir(
    estado: dict,
    populacao_size: int = 20,
    geracoes: int = 50,
) -> tuple[Cromossomo, list[float]]:
    """Executa o AG e retorna (cromossomo_otimo, historico_fitness_por_geracao).

    cromossomo_otimo[0] = replicas_alvo
    cromossomo_otimo[1] = sla_threshold descoberto (inteiro 70-95)
    """
    min_rep = estado["min_replicas"]
    max_rep = estado["max_replicas"]

    populacao = _inicializar_populacao(populacao_size, min_rep, max_rep)
    historico: list[float] = []

    for _ in range(geracoes):
        fitnesses = [fitness(ind, estado) for ind in populacao]
        historico.append(min(fitnesses))

        nova: list[Cromossomo] = []
        for _ in range(populacao_size):
            pai1 = _selecao_torneio(populacao, fitnesses)
            pai2 = _selecao_torneio(populacao, fitnesses)
            filho = _crossover(pai1, pai2)
            filho = _mutacao(filho, min_rep, max_rep)
            nova.append(filho)

        populacao = nova

    fitnesses_finais = [fitness(ind, estado) for ind in populacao]
    melhor_idx = fitnesses_finais.index(min(fitnesses_finais))
    melhor = populacao[melhor_idx]
    historico.append(fitnesses_finais[melhor_idx])

    return melhor, historico


# ---------------------------------------------------------------------------
# Alert simples para uso fora do motor fuzzy
# ---------------------------------------------------------------------------


def compute_alert(cpu_pct: float, ram_pct: float, rps_pct: float) -> tuple[float, str]:
    """Retorna (score, level) com a mesma escala de thresholds do motor fuzzy."""
    score = max(cpu_pct, ram_pct, rps_pct)
    if score > 66:
        return score, "critical"
    if score > 33:
        return score, "warning"
    return score, "none"
