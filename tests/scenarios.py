"""10 cenários de teste para o motor fuzzy Mamdani do Helmsman.

Execução:
    python -m tests.scenarios          # a partir da raiz do projeto
    python tests/scenarios.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from helmsman.engine import infer

SCENARIOS = [
    # name                        cpu   ram   rps   exp_delta  exp_alert
    ("T1  Idle noturno",            5,   10,    8,      -2,    "none"),
    ("T2  Carga leve (assets)",      8,   15,   75,       0,    "none"),
    ("T3  Carga real crescente",    60,   55,   80,      +1,    "none"),
    ("T4  Pico de tráfego",         78,   65,   92,      +3,    "warning"),
    ("T5  Host cheio sob carga",    72,   91,   80,       0,    "critical"),
    ("T6  Memory leak suspeito",    12,   82,    9,      -1,    "warning"),
    ("T7  CPU leak confirmado",     94,   18,    6,      -1,    "critical"),
    ("T8  Colapso total",           91,   93,   96,       0,    "critical"),
    ("T9  Recuperação pós-pico",    35,   40,   45,       0,    "none"),
    ("T10 Scale down gradual",      18,   22,   30,      -1,    "none"),
]

W = 32


def run_all() -> bool:
    passed = failed = 0
    print(f"\n{'=' * 72}")
    print(f"{'Cenário':<{W}} {'Δ got':>6} {'Δ exp':>6} {'alert got':<12} {'alert exp':<12} {'':>4}")
    print(f"{'-' * 72}")

    for name, cpu, ram, rps, exp_delta, exp_alert in SCENARIOS:
        r = infer(cpu, ram, rps)
        delta_ok = r.delta_replicas == exp_delta
        alert_ok = r.alert_level == exp_alert
        ok = delta_ok and alert_ok
        mark = "✓" if ok else "✗"
        if ok:
            passed += 1
        else:
            failed += 1
        print(
            f"{name:<{W}} {r.delta_replicas:>+6d} {exp_delta:>+6d} "
            f"{r.alert_level:<12} {exp_alert:<12} {mark:>4}"
        )

    print(f"{'=' * 72}")
    print(f"Resultado: {passed}/{len(SCENARIOS)} passou  —  {failed} falhou\n")
    return failed == 0


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
