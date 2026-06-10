"""Motor de auto-scaling baseado em Algoritmo Genético — alternativa ao Mamdani fuzzy.

Implementação 100% Python puro: apenas `random` e `math`.

Cromossomo: [n_replicas, sla_threshold]
  n_replicas    — número de réplicas recomendado (int, min_rep .. max_rep)
  sla_threshold — limiar de ocupação a partir do qual considera sobrecarga (int, 70..95)
"""

# uv run helmsman start --host localhost --port 8003 --container helmsman-server-test --rps-per-replica 400 --mode ag
import random
import math  # noqa: F401 — disponível para extensões futuras

_SLA_MIN = 70
_SLA_MAX = 95

Cromossomo = list[int]  # [n_replicas, sla_threshold]


# ---------------------------------------------------------------------------
# Função de aptidão
# ---------------------------------------------------------------------------

def fitness(cromossomo: Cromossomo, estado: dict) -> float:
    """
    Avalia um cromossomo [n_replicas, sla_threshold] dado o estado atual.
    Quanto menor o valor, melhor o indivíduo.

    cromossomo[0] — n_replicas
    cromossomo[1] — sla_threshold (inteiro 70-95)

    Termos:
      custo           — menos réplicas = menor custo operacional
      sobrecarga      — penalidade exponencial acima do threshold (corrige T11/T12)
      rps_absoluto    — pressiona scale up quando rps_real passa de 70% da capacidade (corrige T3)
      ram_risco       — penaliza SUBIR réplica com RAM alta; manter não é penalizado (corrige T5)
      leak            — CPU alta sem demanda = leak, não escala (cobre T6/T7)
      mudanca         — evita variações bruscas desnecessárias
      risco_threshold — penaliza threshold perigosamente alto (acima de 90%)
      conservadorismo — penaliza threshold muito baixo (abaixo de 75%)
    """
    n_replicas    = cromossomo[0]
    sla_threshold = cromossomo[1]  # inteiro 70-95

    capacidade = n_replicas * estado['rps_per_replica']
    rps_pct    = estado['rps_real'] / capacidade if capacidade > 0 else 999.0

    delta_pretendido = n_replicas - estado['replicas_atuais']

    custo = n_replicas * 1.0

    excesso    = max(0.0, rps_pct - sla_threshold / 100)
    sobrecarga = excesso ** 1.5 * 20

    rps_absoluto = max(0.0, estado['rps_real'] - 0.70 * capacidade) * 0.12

    ram_risco = (
        max(0.0, estado['ram_pct'] - 80) / 20
        * max(0, delta_pretendido)
        * 8
    )

    sem_demanda = max(0.0, 0.3 - rps_pct)
    cpu_alta    = max(0.0, estado['cpu_pct'] - 70) / 30
    leak        = cpu_alta * sem_demanda * 20

    mudanca = abs(delta_pretendido) * 0.5

    risco_threshold = max(0.0, sla_threshold - 90) * 0.5

    conservadorismo = max(0.0, 75 - sla_threshold) * 0.3

    return (
        custo
        + sobrecarga
        + rps_absoluto
        + ram_risco
        + leak
        + mudanca
        + risco_threshold
        + conservadorismo
    )


# ---------------------------------------------------------------------------
# Operadores genéticos
# ---------------------------------------------------------------------------

def _inicializar_populacao(tamanho: int, min_rep: int, max_rep: int) -> list[Cromossomo]:
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


def _mutacao(cromossomo: Cromossomo, min_rep: int, max_rep: int, taxa: float = 0.2) -> Cromossomo:
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
    min_rep = estado['min_replicas']
    max_rep = estado['max_replicas']

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
