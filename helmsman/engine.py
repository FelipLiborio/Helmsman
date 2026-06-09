"""Motor fuzzy Mamdani com 3 entradas, 2 saídas e 18 regras."""
# uv run helmsman start --host localhost --port 8003 --container helmsman-server-test --rps-per-replica 400;
from dataclasses import dataclass

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


@dataclass
class FuzzyResult:
    delta_raw: float
    delta_replicas: int
    alert_score: float
    alert_level: str  # none | warning | critical


def _build_system() -> ctrl.ControlSystem:
    u_pct = np.arange(0, 101, 1, dtype=float)
    u_delta = np.arange(-3, 5.1, 0.1)
    u_alert = np.arange(0, 101, 1, dtype=float)

    cpu = ctrl.Antecedent(u_pct, "cpu_pct")
    ram = ctrl.Antecedent(u_pct, "ram_pct")
    rps = ctrl.Antecedent(u_pct, "rps_pct")
    delta = ctrl.Consequent(u_delta, "delta_replicas", defuzzify_method="centroid")
    alerta = ctrl.Consequent(u_alert, "alerta", defuzzify_method="centroid")

    # Funções de pertinência das entradas (idênticas para as 3 variáveis)
    for v in (cpu, ram, rps):
        v["baixo"] = fuzz.trapmf(v.universe, [0, 0, 20, 40])
        v["moderado"] = fuzz.trimf(v.universe, [20, 45, 70])
        v["alto"] = fuzz.trimf(v.universe, [55, 72, 88])
        v["critico"] = fuzz.trapmf(v.universe, [75, 88, 100, 100])

    # Saída: delta_replicas  [-3, 5]
    delta["derrubar_forte"] = fuzz.trimf(delta.universe, [-3, -2, -1])
    delta["derrubar"] = fuzz.trimf(delta.universe, [-2, -1, 0])
    delta["manter"] = fuzz.trimf(delta.universe, [-1, 0, 1])
    delta["subir"] = fuzz.trimf(delta.universe, [0, 1, 2])
    delta["subir_forte"] = fuzz.trimf(delta.universe, [1, 3, 5])

    # Saída: alerta  [0, 100]
    alerta["nenhum"] = fuzz.trapmf(alerta.universe, [0, 0, 20, 40])
    alerta["warning"] = fuzz.trimf(alerta.universe, [20, 50, 80])
    alerta["critical"] = fuzz.trapmf(alerta.universe, [60, 80, 100, 100])

    rules = [
        # Grupo 1 — Idle / scale down
        ctrl.Rule(cpu["baixo"] & ram["baixo"] & rps["baixo"],
                  (delta["derrubar_forte"], alerta["nenhum"])),
        ctrl.Rule(cpu["baixo"] & ram["baixo"] & rps["moderado"],   # R2: tráfego ainda presente — mantém
                  (delta["manter"], alerta["nenhum"])),
        ctrl.Rule(cpu["moderado"] & ram["baixo"] & rps["baixo"],
                  (delta["derrubar"], alerta["nenhum"])),

        # Grupo 2 — RPS alto respeita rps_per_replica → escala
        # (antes "não escala"; agora: o usuário definiu o limite, se chegou em alto é hora de subir)
        ctrl.Rule(cpu["baixo"] & ram["baixo"] & rps["alto"],
                  (delta["subir"], alerta["nenhum"])),
        ctrl.Rule(cpu["baixo"] & ram["moderado"] & rps["alto"],
                  (delta["subir"], alerta["nenhum"])),

        # Grupo 3 — Carga real, scale up normal
        ctrl.Rule(cpu["moderado"] & ram["moderado"] & rps["alto"],
                  (delta["subir"], alerta["nenhum"])),
        ctrl.Rule(cpu["alto"] & ram["moderado"] & rps["alto"],
                  (delta["subir"], alerta["nenhum"])),
        ctrl.Rule(cpu["moderado"] & ram["alto"] & rps["alto"],
                  (delta["subir"], alerta["warning"])),

        # Grupo 4 — Carga crítica, scale up urgente
        ctrl.Rule(cpu["alto"] & ram["alto"] & rps["alto"],
                  (delta["subir_forte"], alerta["warning"])),
        ctrl.Rule(cpu["critico"] & ram["moderado"] & rps["alto"],
                  (delta["subir_forte"], alerta["warning"])),
        ctrl.Rule(cpu["alto"] & ram["moderado"] & rps["critico"],
                  (delta["subir_forte"], alerta["critical"])),

        # Grupo 5 — Host cheio, bloqueia scale up
        ctrl.Rule(cpu["alto"] & ram["critico"] & rps["alto"],
                  (delta["manter"], alerta["critical"])),
        ctrl.Rule(cpu["critico"] & ram["critico"] & rps["critico"],
                  (delta["manter"], alerta["critical"])),

        # Grupo 6 — Anomalias (possível leak)
        ctrl.Rule(cpu["alto"] & ram["baixo"] & rps["baixo"],
                  (delta["manter"], alerta["warning"])),
        ctrl.Rule(cpu["critico"] & ram["baixo"] & rps["baixo"],
                  (delta["derrubar"], alerta["critical"])),
        ctrl.Rule(cpu["baixo"] & ram["alto"] & rps["baixo"],
                  (delta["derrubar"], alerta["warning"])),
        ctrl.Rule(cpu["baixo"] & ram["critico"] & rps["baixo"],
                  (delta["derrubar_forte"], alerta["critical"])),
        ctrl.Rule(cpu["alto"] & ram["alto"] & rps["baixo"],
                  (delta["derrubar"], alerta["critical"])),

        # Grupo 7 — RPS crítico com CPU/RAM baixa ou moderada
        ctrl.Rule(cpu["baixo"] & ram["baixo"] & rps["critico"],
                  (delta["subir"], alerta["warning"])),
        ctrl.Rule(cpu["moderado"] & ram["baixo"] & rps["critico"],
                  (delta["subir_forte"], alerta["warning"])),
        ctrl.Rule(cpu["baixo"] & ram["moderado"] & rps["critico"],
                  (delta["subir"], alerta["warning"])),
        ctrl.Rule(cpu["moderado"] & ram["moderado"] & rps["critico"],
                  (delta["subir_forte"], alerta["warning"])),
    ]

    return ctrl.ControlSystem(rules)


# Sistema construído uma única vez na importação (thread-safe para leitura)
_system = _build_system()


def infer(cpu_pct: float, ram_pct: float, rps_pct: float) -> FuzzyResult:
    """Roda inferência Mamdani e retorna delta_replicas e nível de alerta."""
    sim = ctrl.ControlSystemSimulation(_system)
    # Pequeno offset evita que valores exatos em 0 ou 100 gerem área nula no centróide
    sim.input["cpu_pct"] = float(np.clip(cpu_pct, 0.01, 99.99))
    sim.input["ram_pct"] = float(np.clip(ram_pct, 0.01, 99.99))
    sim.input["rps_pct"] = float(np.clip(rps_pct, 0.01, 99.99))

    try:
        sim.compute()
        delta_raw  = float(sim.output["delta_replicas"])
        alert_score = float(sim.output["alerta"])
    except (KeyError, Exception):
        # Área agregada degenerada — mantém estado atual como decisão segura
        delta_raw  = 0.0
        alert_score = 0.0
    delta_int = int(round(delta_raw))

    if alert_score <= 33:
        level = "none"
    elif alert_score <= 66:
        level = "warning"
    else:
        level = "critical"

    return FuzzyResult(
        delta_raw=delta_raw,
        delta_replicas=delta_int,
        alert_score=alert_score,
        alert_level=level,
    )
