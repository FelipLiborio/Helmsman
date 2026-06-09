"""FastAPI — expõe métricas e histórico de decisões para o dashboard."""

from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .state import state

app = FastAPI(title="Helmsman API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Todos os endpoints da API ficam sob /api para não colidir com o front
api = APIRouter(prefix="/api")


@api.get("/metrics")
def get_metrics():
    m = state.current_metrics
    return {
        "timestamp": m.timestamp,
        "cpu_pct": m.cpu_pct,
        "ram_pct": m.ram_pct,
        "rps_pct": m.rps_pct,
        "rps_actual": m.rps_actual,
        "replicas": m.replicas,
    }


@api.get("/status")
def get_status():
    d = state.last_decision
    a = state.last_alert
    return {
        "replicas": len(state.managed_containers),
        "max_replicas": state.max_replicas,
        "service_name": state.service_name,
        "last_alert": {
            "level": a.level if a else "none",
            "message": a.message if a else "",
            "timestamp": a.timestamp if a else None,
        },
        "last_decision": {
            "delta_replicas": d.delta_replicas,
            "delta_raw": d.delta_raw,
            "alert_level": d.alert_level,
            "alert_score": d.alert_score,
            "timestamp": d.timestamp,
        } if d else None,
    }


@api.get("/history")
def get_history(limit: int = 120):
    with state._lock:
        items = list(state.history[-limit:])
    return [
        {
            "timestamp": m.timestamp,
            "cpu_pct": m.cpu_pct,
            "ram_pct": m.ram_pct,
            "rps_pct": m.rps_pct,
            "rps_actual": m.rps_actual,
            "replicas": m.replicas,
        }
        for m in items
    ]


@api.get("/containers")
def get_containers():
    with state._lock:
        stats = list(state.container_stats)
    return [
        {
            "id": s.id,
            "name": s.name,
            "cpu_pct": s.cpu_pct,
            "ram_pct": s.ram_pct,
            "ram_mb": s.ram_mb,
        }
        for s in stats
    ]


@api.get("/decisions")
def get_decisions(limit: int = 50):
    with state._lock:
        items = list(state.decisions[-limit:])
    return [
        {
            "timestamp": d.timestamp,
            "cpu_pct": d.cpu_pct,
            "ram_pct": d.ram_pct,
            "rps_pct": d.rps_pct,
            "delta_replicas": d.delta_replicas,
            "delta_raw": d.delta_raw,
            "alert_score": d.alert_score,
            "alert_level": d.alert_level,
        }
        for d in items
    ]


@api.get("/host-info")
def get_host_info():
    import os
    ram_total = 0
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    ram_total = int(line.split()[1]) * 1024
                    break
    except OSError:
        pass
    return {
        "ram_total_gb": round(ram_total / (1024 ** 3), 1),
        "cpu_count": os.cpu_count() or 1,
    }


@api.get("/http-stats")
def get_http_stats():
    from .collector import http_stats
    return http_stats()


@api.get("/alerts")
def get_alerts(limit: int = 50):
    with state._lock:
        items = list(state.alerts[-limit:])
    return [
        {"timestamp": a.timestamp, "level": a.level, "message": a.message}
        for a in items
    ]


app.include_router(api)

# Serve o front buildado (helmsman/frontend_dist/) se existir.
# html=True faz fallback para index.html em qualquer rota não encontrada — necessário para SPA.
_DIST = Path(__file__).parent / "frontend_dist"
if _DIST.exists():
    app.mount("/", StaticFiles(directory=_DIST, html=True), name="frontend")
