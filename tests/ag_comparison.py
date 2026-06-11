"""Comparação de três abordagens de decisão de escalonamento:

  1. Heurística simples  — regra fixa baseada em rps_pct, sem otimização nem fuzzy.
  2. AG-puro             — Algoritmo Genético com a função de aptidão original
                            (sem componente fuzzy), usada na Parte 1.
  3. AG-fuzzy            — Algoritmo Genético com fitness híbrida Fuzzy-Evolutiva
                            (Alternativa 2), implementação atual de helmsman/ag_engine.py.

Os mesmos 12 cenários x 5 sementes de tests/ag_scenarios.py são usados para
permitir comparação direta "antes/depois" da integração fuzzy-evolutiva.

Execução:
    python tests/ag_comparison.py          # a partir da raiz do projeto
    python -m tests.ag_comparison
"""

import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helmsman.ag_engine import (
    evoluir as evoluir_fuzzy,
    _inicializar_populacao,
    _selecao_torneio,
    _crossover,
    _mutacao,
    Cromossomo,
)

RPS_PER_REPLICA = 50

SCENARIOS = [
    # name                             cpu   ram   rps   rep_atuais  delta_exp
    ("T1  Idle noturno",                 5,   10,    8,      2,         -1),
    ("T2  RPS alto CPU baixa",           8,   15,   75,      1,         +1),
    ("T3  Carga real crescente",        60,   55,   80,      2,         +1),
    ("T4  Pico de tráfego",             78,   65,   92,      2,         +1),
    ("T5  Host cheio sob carga",        72,   91,   80,      3,          0),
    ("T6  Memory leak suspeito",        12,   82,    9,      2,         -1),
    ("T7  CPU leak confirmado",         94,   18,    6,      2,         -1),
    ("T8  Colapso total",               91,   93,   96,      3,          0),
    ("T9  Recuperação pós-pico",        35,   40,   45,      3,         -1),
    ("T10 Scale down gradual",          18,   22,   30,      2,         -1),
    ("T11 RPS crítico CPU baixa",        8,   10,   95,      1,         +2),
    ("T12 RPS crítico CPU moderada",    40,   20,   95,      2,         +1),
]

SEEDS = [42, 123, 7, 99, 256]
W = 34


def _estado(cpu, ram, rps, rep):
    return {
        "cpu_pct":         float(cpu),
        "ram_pct":         float(ram),
        "rps_real":        float(rps),
        "replicas_atuais": int(rep),
        "rps_per_replica": RPS_PER_REPLICA,
        "min_replicas":    1,
        "max_replicas":    8,
    }


# ---------------------------------------------------------------------------
# 1. Heurística simples — sem otimização, sem fuzzy
# ---------------------------------------------------------------------------


def heuristica_simples(estado: dict) -> int:
    """Regra fixa baseada apenas em rps_pct atual. Retorna delta_replicas."""
    capacidade = estado["replicas_atuais"] * estado["rps_per_replica"]
    rps_pct = (estado["rps_real"] / capacidade * 100) if capacidade > 0 else 999.0

    if rps_pct > 90:
        return +2
    if rps_pct > 75:
        return +1
    if rps_pct < 25 and estado["cpu_pct"] < 30 and estado["ram_pct"] < 30:
        return -1
    return 0


# ---------------------------------------------------------------------------
# 2. AG-puro — fitness original (Parte 1, sem motor fuzzy)
# ---------------------------------------------------------------------------


def fitness_puro(cromossomo: Cromossomo, estado: dict) -> float:
    n_replicas = cromossomo[0]
    sla_threshold = cromossomo[1]

    capacidade = n_replicas * estado["rps_per_replica"]
    rps_pct = estado["rps_real"] / capacidade if capacidade > 0 else 999.0

    delta_pretendido = n_replicas - estado["replicas_atuais"]

    custo = n_replicas * 1.0

    excesso = max(0.0, rps_pct - sla_threshold / 100)
    sobrecarga = excesso**1.5 * 20

    rps_absoluto = max(0.0, estado["rps_real"] - 0.70 * capacidade) * 0.12

    ram_risco = max(0.0, estado["ram_pct"] - 80) / 20 * max(0, delta_pretendido) * 8

    sem_demanda = max(0.0, 0.3 - rps_pct)
    cpu_alta = max(0.0, estado["cpu_pct"] - 70) / 30
    leak = cpu_alta * sem_demanda * 20

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


def _evoluir_generic(
    estado: dict,
    fitness_fn,
    populacao_size: int = 20,
    geracoes: int = 50,
) -> Cromossomo:
    """Mesmo loop evolutivo de ag_engine.evoluir, parametrizado pela fitness."""
    min_rep = estado["min_replicas"]
    max_rep = estado["max_replicas"]

    populacao = _inicializar_populacao(populacao_size, min_rep, max_rep)

    for _ in range(geracoes):
        fitnesses = [fitness_fn(ind, estado) for ind in populacao]

        nova: list[Cromossomo] = []
        for _ in range(populacao_size):
            pai1 = _selecao_torneio(populacao, fitnesses)
            pai2 = _selecao_torneio(populacao, fitnesses)
            filho = _crossover(pai1, pai2)
            filho = _mutacao(filho, min_rep, max_rep)
            nova.append(filho)

        populacao = nova

    fitnesses_finais = [fitness_fn(ind, estado) for ind in populacao]
    melhor_idx = fitnesses_finais.index(min(fitnesses_finais))
    return populacao[melhor_idx]


# ---------------------------------------------------------------------------
# Execução comparativa
# ---------------------------------------------------------------------------


def run_all() -> None:
    metodos = ["Heurística", "AG-puro", "AG-fuzzy"]
    totais = {m: 0 for m in metodos}

    print(f"\n{'=' * 90}")
    print(f"{'Cenário':<{W}} {'Seed':>6} {'Heur':>8} {'AG-puro':>8} {'AG-fuzzy':>9} {'Δ esp':>6}")
    print(f"{'-' * 90}")

    for seed in SEEDS:
        seed_pass = {m: 0 for m in metodos}

        for name, cpu, ram, rps, rep, exp_delta in SCENARIOS:
            estado = _estado(cpu, ram, rps, rep)

            random.seed(seed)
            delta_heur = heuristica_simples(estado)

            random.seed(seed)
            cromo_puro = _evoluir_generic(estado, fitness_puro)
            delta_puro = cromo_puro[0] - rep

            random.seed(seed)
            cromo_fuzzy, _ = evoluir_fuzzy(estado)
            delta_fuzzy = cromo_fuzzy[0] - rep

            ok_heur = delta_heur == exp_delta
            ok_puro = delta_puro == exp_delta
            ok_fuzzy = delta_fuzzy == exp_delta

            for m, ok in zip(metodos, (ok_heur, ok_puro, ok_fuzzy)):
                if ok:
                    seed_pass[m] += 1
                    totais[m] += 1

            marks = (
                "✓" if ok_heur else "✗",
                "✓" if ok_puro else "✗",
                "✓" if ok_fuzzy else "✗",
            )
            print(
                f"{name:<{W}} {seed:>6} "
                f"{delta_heur:>+5d} {marks[0]:>2} "
                f"{delta_puro:>+5d} {marks[1]:>2} "
                f"{delta_fuzzy:>+6d} {marks[2]:>2} "
                f"{exp_delta:>+6d}"
            )

        print(f"{'':>{W}} seed {seed:<5} "
              f"{seed_pass['Heurística']}/12{'':>5} "
              f"{seed_pass['AG-puro']}/12{'':>5} "
              f"{seed_pass['AG-fuzzy']}/12")
        print(f"{'-' * 90}")

    total = len(SCENARIOS) * len(SEEDS)
    print(f"\n{'Resumo final':<{W}}")
    for m in metodos:
        pct = 100 * totais[m] // total
        print(f"  {m:<12} {totais[m]:>3}/{total} ({pct}%)")
    print()


if __name__ == "__main__":
    run_all()
