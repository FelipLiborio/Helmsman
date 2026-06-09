"""CLI do Helmsman — helmsman start / stop / status / logs."""

import threading
import time

import typer
import uvicorn

from .state import state, Metrics, Decision
from .engine import infer
from .collector import collect_container_stats, current_rps, follow_nginx_log
from .alerter import emit

app = typer.Typer(
    name="helmsman",
    help="Fuzzy auto-scaler para serviços Docker.",
    no_args_is_help=True,
)

_LOG_DIR = "/tmp/helmsman"
_DEFAULT_API_PORT = 8800


@app.command()
def start(
    host: str = typer.Option(..., help="Host do serviço alvo"),
    port: int = typer.Option(..., help="Porta do serviço alvo"),
    container: str = typer.Option(..., help="Nome ou ID do container alvo"),
    min_replicas: int = typer.Option(1, "--min-replicas"),
    max_replicas: int = typer.Option(5, "--max-replicas"),
    rps_per_replica: float = typer.Option(100.0, "--rps-per-replica"),
    poll_interval: int = typer.Option(5, "--poll-interval"),
    api_port: int = typer.Option(_DEFAULT_API_PORT, "--api-port"),
):
    """Inicia monitoramento e auto-scaling do serviço."""
    import docker as _docker

    cli = _docker.from_env()
    try:
        c = cli.containers.get(container)
        image = c.image.tags[0] if c.image.tags else c.image.id
    except Exception as e:
        typer.echo(f"[erro] Container '{container}' não encontrado: {e}", err=True)
        raise typer.Exit(1)

    state.target_host = host
    state.target_port = port
    state.min_replicas = min_replicas
    state.max_replicas = max_replicas
    state.rps_per_replica = rps_per_replica
    state.poll_interval = poll_interval
    state.service_image = image
    state.service_name = container
    state.running = True
    state.managed_containers = [c.id]

    log_path = f"{_LOG_DIR}/access.log"

    typer.echo(f"[helmsman] monitorando {host}:{port} (imagem: {image})")

    # nginx sidecar
    from .scaler import start_nginx_sidecar
    try:
        nid = start_nginx_sidecar(host, port, _LOG_DIR)
        state.nginx_container = nid
        typer.echo(f"[helmsman] nginx sidecar: {nid[:12]}  →  http://localhost:8080")
    except Exception as e:
        typer.echo(f"[aviso] nginx sidecar não iniciado: {e}", err=True)

    # thread que segue nginx access.log
    threading.Thread(
        target=follow_nginx_log, args=(log_path,), daemon=True
    ).start()

    # thread da API FastAPI
    api_cfg = uvicorn.Config(
        "helmsman.api:app",
        host="0.0.0.0",
        port=api_port,
        log_level="error",
    )
    api_server = uvicorn.Server(api_cfg)
    threading.Thread(target=api_server.run, daemon=True).start()
    typer.echo(f"[helmsman] API em http://localhost:{api_port}")

    typer.echo(f"[helmsman] polling a cada {poll_interval}s — Ctrl+C para parar\n")
    try:
        while True:
            _tick()
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        typer.echo("\n[helmsman] encerrando...")
        state.running = False


def _tick() -> None:
    from .scaler import scale_to

    containers = list(state.managed_containers)
    cpu_pct, ram_pct, cstats = collect_container_stats(containers)
    state.update_container_stats(cstats)

    rps_actual = current_rps(window=float(state.poll_interval))
    capacity = len(containers) * state.rps_per_replica
    rps_pct = min((rps_actual / capacity * 100) if capacity else 0.0, 100.0)

    state.update_metrics(
        Metrics(
            cpu_pct=cpu_pct,
            ram_pct=ram_pct,
            rps_pct=rps_pct,
            rps_actual=rps_actual,
            replicas=len(containers),
        )
    )

    result = infer(cpu_pct, ram_pct, rps_pct)

    target = max(
        state.min_replicas,
        min(state.max_replicas, len(containers) + result.delta_replicas),
    )
    if target != len(containers):
        scale_to(target, state.service_image)

    state.add_decision(
        Decision(
            timestamp=time.time(),
            cpu_pct=cpu_pct,
            ram_pct=ram_pct,
            rps_pct=rps_pct,
            delta_raw=result.delta_raw,
            delta_replicas=result.delta_replicas,
            alert_score=result.alert_score,
            alert_level=result.alert_level,
        )
    )
    emit(result.alert_level, cpu_pct, ram_pct, rps_pct)

    typer.echo(
        f"cpu={cpu_pct:5.1f}%  ram={ram_pct:5.1f}%  rps={rps_pct:5.1f}%  "
        f"replicas={len(containers)}→{target}  delta={result.delta_replicas:+d}  "
        f"alert={result.alert_level}"
    )


@app.command()
def stop():
    """Para todos os containers gerenciados pelo helmsman."""
    from .scaler import stop_all

    stop_all()
    typer.echo("[helmsman] todos os containers removidos.")


@app.command()
def status(
    api_port: int = typer.Option(_DEFAULT_API_PORT, "--api-port"),
):
    """Exibe réplicas ativas, último alerta e última decisão."""
    import httpx

    try:
        r = httpx.get(f"http://localhost:{api_port}/status", timeout=5)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        typer.echo(f"[erro] API indisponível: {e}", err=True)
        raise typer.Exit(1)

    typer.echo(f"réplicas ativas : {data['replicas']}")
    if data.get("last_decision"):
        d = data["last_decision"]
        typer.echo(
            f"última decisão  : delta={d['delta_replicas']:+d}  "
            f"alerta={d['alert_level']}  score={d['alert_score']:.1f}"
        )
    if data.get("last_alert") and data["last_alert"]["level"] != "none":
        a = data["last_alert"]
        typer.echo(f"último alerta   : [{a['level']}] {a['message']}")


@app.command()
def logs(
    limit: int = typer.Option(20, "--limit"),
    api_port: int = typer.Option(_DEFAULT_API_PORT, "--api-port"),
):
    """Histórico de decisões fuzzy."""
    import httpx

    try:
        r = httpx.get(
            f"http://localhost:{api_port}/decisions", params={"limit": limit}, timeout=5
        )
        r.raise_for_status()
        decisions = r.json()
    except Exception as e:
        typer.echo(f"[erro] API indisponível: {e}", err=True)
        raise typer.Exit(1)

    for d in decisions:
        ts = time.strftime("%H:%M:%S", time.localtime(d["timestamp"]))
        typer.echo(
            f"[{ts}]  cpu={d['cpu_pct']:5.1f}%  ram={d['ram_pct']:5.1f}%  "
            f"rps={d['rps_pct']:5.1f}%  "
            f"delta={d['delta_replicas']:+d}  alert={d['alert_level']}"
            f"  (score={d['alert_score']:.1f})"
        )
