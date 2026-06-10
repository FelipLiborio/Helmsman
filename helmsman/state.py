import threading
import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ContainerStats:
    id: str
    name: str
    cpu_pct: float
    ram_pct: float
    ram_mb: float


@dataclass
class Metrics:
    timestamp: float = field(default_factory=time.time)
    cpu_pct: float = 0.0
    ram_pct: float = 0.0
    rps_pct: float = 0.0
    rps_actual: float = 0.0
    replicas: int = 0


@dataclass
class Decision:
    timestamp: float
    cpu_pct: float
    ram_pct: float
    rps_pct: float
    delta_raw: float
    delta_replicas: int
    alert_score: float
    alert_level: str  # none | warning | critical


@dataclass
class Alert:
    timestamp: float
    level: str  # warning | critical
    message: str


class HelmsmanState:
    _MAX = 1000

    def __init__(self):
        self._lock = threading.Lock()
        self.running: bool = False

        # parâmetros da sessão
        self.target_host: str = ""
        self.target_port: int = 0
        self.min_replicas: int = 1
        self.max_replicas: int = 5
        self.rps_per_replica: float = 100.0
        self.poll_interval: int = 5
        self.service_image: str = ""
        self.service_name: str = ""
        self.log_dir: str = ""
        self.mode: str = "fuzzy"  # "fuzzy" | "ag"

        # resultado do último ciclo AG (None no modo fuzzy)
        self.ag_last: Optional[dict] = None

        # containers gerenciados
        self.managed_containers: List[str] = []
        self.nginx_container: Optional[str] = None

        # dados em tempo real
        self.current_metrics: Metrics = Metrics()
        self.container_stats: List[ContainerStats] = []
        self.last_decision: Optional[Decision] = None
        self.last_alert: Optional[Alert] = None

        # histórico
        self.history: List[Metrics] = []
        self.decisions: List[Decision] = []
        self.alerts: List[Alert] = []

    def update_metrics(self, m: Metrics) -> None:
        with self._lock:
            self.current_metrics = m
            self.history.append(m)
            if len(self.history) > self._MAX:
                self.history.pop(0)

    def update_container_stats(self, stats: List[ContainerStats]) -> None:
        with self._lock:
            self.container_stats = stats

    def add_decision(self, d: Decision) -> None:
        with self._lock:
            self.last_decision = d
            self.decisions.append(d)
            if len(self.decisions) > self._MAX:
                self.decisions.pop(0)

    def add_alert(self, a: Alert) -> None:
        with self._lock:
            self.last_alert = a
            self.alerts.append(a)
            if len(self.alerts) > self._MAX:
                self.alerts.pop(0)


state = HelmsmanState()
