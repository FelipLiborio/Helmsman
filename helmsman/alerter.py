"""Classifica e registra alertas no estado global."""

import time

from .state import state, Alert


def emit(level: str, cpu: float, ram: float, rps: float) -> None:
    if level == "none":
        return
    msg = _build_message(level, cpu, ram, rps)
    state.add_alert(Alert(timestamp=time.time(), level=level, message=msg))


def _build_message(level: str, cpu: float, ram: float, rps: float) -> str:
    # Anomalias têm mensagens específicas
    if cpu > 88 and ram < 40 and rps < 40:
        return f"CPU crítica ({cpu:.1f}%) sem demanda — possível CPU leak ou processo travado"
    if ram > 88 and cpu < 40 and rps < 40:
        return f"RAM crítica ({ram:.1f}%) sem demanda — memory leak severo detectado"
    if cpu > 55 and ram > 55 and rps < 40:
        return f"CPU {cpu:.1f}% e RAM {ram:.1f}% altas sem demanda — app possivelmente travada"
    if ram > 75 and rps > 55:
        return f"RAM do host crítica ({ram:.1f}%) — scale up bloqueado para proteger o host"
    if cpu > 75 and ram > 75 and rps > 75:
        return (
            f"Saturação total: CPU {cpu:.1f}%, RAM {ram:.1f}%, RPS {rps:.1f}% "
            "— intervenção humana sugerida"
        )
    if level == "warning":
        return f"Pressão crescente: CPU {cpu:.1f}%, RAM {ram:.1f}%, RPS {rps:.1f}%"
    return f"Alerta crítico: CPU {cpu:.1f}%, RAM {ram:.1f}%, RPS {rps:.1f}%"
