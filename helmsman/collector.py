"""Coleta de métricas via docker-py (CPU/RAM) e nginx access.log (RPS)."""

import re
import threading
import time
from collections import deque
from typing import Optional, Tuple, List

import docker

from .state import state, ContainerStats

_docker_client: Optional[docker.DockerClient] = None
_client_lock = threading.Lock()

# Timestamps das requisições recentes (para cálculo de RPS)
_rps_deque: deque = deque(maxlen=50_000)
_rps_lock = threading.Lock()

# (timestamp, status_code) para distribuição HTTP
_http_deque: deque = deque(maxlen=50_000)

_LOG_RE = re.compile(r'^\S+ - - \[.*?\] ".*?" (\d{3}) ')


def _client() -> docker.DockerClient:
    global _docker_client
    with _client_lock:
        if _docker_client is None:
            _docker_client = docker.from_env()
        return _docker_client


# ---------------------------------------------------------------------------
# CPU / RAM
# ---------------------------------------------------------------------------

def _host_ram_bytes() -> int:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) * 1024
    except OSError:
        pass
    return 0


def _cpu_pct_from_stats(raw: dict) -> float:
    try:
        cpu_d = (
            raw["cpu_stats"]["cpu_usage"]["total_usage"]
            - raw["precpu_stats"]["cpu_usage"]["total_usage"]
        )
        sys_d = (
            raw["cpu_stats"]["system_cpu_usage"]
            - raw["precpu_stats"]["system_cpu_usage"]
        )
        ncpus = raw["cpu_stats"].get("online_cpus", 1)
        if sys_d > 0:
            return (cpu_d / sys_d) * ncpus * 100.0
    except (KeyError, ZeroDivisionError):
        pass
    return 0.0


def collect_container_stats(
    container_ids: List[str],
) -> Tuple[float, float, List[ContainerStats]]:
    """Retorna (cpu_total_pct, ram_total_pct, lista_por_container)."""
    host_ram = _host_ram_bytes()
    cli = _client()
    total_cpu = 0.0
    total_ram_bytes = 0
    stats_list: List[ContainerStats] = []

    for cid in container_ids:
        try:
            c = cli.containers.get(cid)
            raw = c.stats(stream=False)
            cpu = _cpu_pct_from_stats(raw)
            ram_b = raw["memory_stats"].get("usage", 0)
            ram_pct = (ram_b / host_ram * 100) if host_ram else 0.0
            total_cpu += cpu
            total_ram_bytes += ram_b
            stats_list.append(
                ContainerStats(
                    id=cid[:12],
                    name=c.name,
                    cpu_pct=round(cpu, 2),
                    ram_pct=round(ram_pct, 2),
                    ram_mb=round(ram_b / 1_048_576, 1),
                )
            )
        except Exception:
            pass

    total_ram_pct = (total_ram_bytes / host_ram * 100) if host_ram else 0.0
    return round(total_cpu, 2), round(total_ram_pct, 2), stats_list


# ---------------------------------------------------------------------------
# RPS via nginx access.log
# ---------------------------------------------------------------------------

def record_log_line(line: str) -> None:
    m = _LOG_RE.match(line)
    if m:
        now = time.monotonic()
        with _rps_lock:
            _rps_deque.append(now)
            _http_deque.append((now, int(m.group(1))))


def current_rps(window: float = 10.0) -> float:
    now = time.monotonic()
    cutoff = now - window
    with _rps_lock:
        count = sum(1 for t in _rps_deque if t >= cutoff)
    return count / window


def http_stats(window: float = 300.0) -> dict:
    """Contagem de 2xx/4xx/5xx nos últimos `window` segundos."""
    now = time.monotonic()
    cutoff = now - window
    counts = {"2xx": 0, "4xx": 0, "5xx": 0, "other": 0}
    with _rps_lock:
        for ts, code in _http_deque:
            if ts < cutoff:
                continue
            if 200 <= code < 300:
                counts["2xx"] += 1
            elif 400 <= code < 500:
                counts["4xx"] += 1
            elif 500 <= code < 600:
                counts["5xx"] += 1
            else:
                counts["other"] += 1
    total = sum(counts.values())
    if total == 0:
        return {"2xx": 0, "4xx": 0, "5xx": 0, "total": 0}
    return {
        "2xx": round(counts["2xx"] / total * 100),
        "4xx": round(counts["4xx"] / total * 100),
        "5xx": round(counts["5xx"] / total * 100),
        "total": total,
    }


def follow_nginx_log(log_path: str) -> None:
    """Thread que segue o nginx access.log em modo tail -f."""
    while state.running:
        try:
            with open(log_path) as f:
                f.seek(0, 2)
                while state.running:
                    line = f.readline()
                    if line:
                        record_log_line(line)
                    else:
                        time.sleep(0.05)
        except FileNotFoundError:
            time.sleep(1)
        except Exception:
            time.sleep(1)
