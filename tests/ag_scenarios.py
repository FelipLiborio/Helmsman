"""Cenários de teste para o motor AG do Helmsman.

Os valores de rps são req/s absolutos. rps_per_replica=50 é usado nos testes para que
os valores de rps representem percentuais de utilização equivalentes aos cenários fuzzy
(ex.: rps=92 com capacidade=100 → 92% de utilização).

Execução:
    python tests/ag_scenarios.py          # a partir da raiz do projeto
    python -m tests.ag_scenarios
"""

import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helmsman.ag_engine import evoluir

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


def rodar_cenarios(seed: int) -> tuple[int, int]:
    random.seed(seed)
    passed = failed = 0
    for _, cpu, ram, rps, rep, exp_delta in SCENARIOS:
        estado = _estado(cpu, ram, rps, rep)
        cromossomo, _ = evoluir(estado)
        delta = cromossomo[0] - rep
        ok = delta == exp_delta
        if ok:
            passed += 1
        else:
            failed += 1
    return passed, failed


def run_all() -> bool:
    print(f"\n{'=' * 80}")
    print(f"{'Cenário':<{W}} {'Seed':>6} {'Δ got':>6} {'Δ exp':>6} {'SLA':>5} {'':>4}")
    print(f"{'-' * 80}")

    total_pass = total_fail = 0

    for seed in SEEDS:
        random.seed(seed)
        seed_pass = seed_fail = 0
        rows = []
        for name, cpu, ram, rps, rep, exp_delta in SCENARIOS:
            estado = _estado(cpu, ram, rps, rep)
            cromossomo, _ = evoluir(estado)
            delta = cromossomo[0] - rep
            sla  = cromossomo[1]
            ok = delta == exp_delta
            mark = "✓" if ok else "✗"
            if ok:
                seed_pass += 1
            else:
                seed_fail += 1
            rows.append((name, seed, delta, exp_delta, sla, mark))

        for name, s, got, exp, sla, mark in rows:
            print(f"{name:<{W}} {s:>6} {got:>+6d} {exp:>+6d} {sla:>5}% {mark:>4}")

        print(f"{'':>{W}} {'seed ' + str(seed):<10} {seed_pass}/{len(SCENARIOS)} passou")
        print(f"{'-' * 80}")
        total_pass += seed_pass
        total_fail += seed_fail

    total = len(SCENARIOS) * len(SEEDS)
    print(f"\nTotal: {total_pass}/{total} ({100*total_pass//total}%) — "
          f"{total_fail} falha(s) em {len(SEEDS)} execuções\n")
    return total_fail == 0


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
