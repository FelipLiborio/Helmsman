"""Gerencia containers Docker: nginx sidecar, scale up/down."""

import os
from pathlib import Path
from typing import Optional

import docker
from docker.types import Mount

from .collector import _client
from .nginx_gen import render
from .state import state

NGINX_IMAGE = "nginx:alpine"
_NET = "helmsman_net"


def _net(cli: docker.DockerClient) -> str:
    names = {n.name for n in cli.networks.list()}
    if _NET not in names:
        cli.networks.create(_NET, driver="bridge")
    return _NET


def _kill(cli: docker.DockerClient, name: str) -> None:
    try:
        c = cli.containers.get(name)
        c.stop(timeout=5)
        c.remove(force=True)
    except Exception:
        pass


def start_nginx_sidecar(host: str, port: int, log_dir: str) -> str:
    """Sobe nginx sidecar e retorna o container ID."""
    cli = _client()
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    conf_path = os.path.join(log_dir, "nginx.conf")
    with open(conf_path, "w") as f:
        f.write(render(host, port))

    _kill(cli, "helmsman-nginx")
    extra_hosts = (
        {"host.docker.internal": "host-gateway"}
        if host in ("localhost", "127.0.0.1")
        else {}
    )

    c = cli.containers.run(
        NGINX_IMAGE,
        name="helmsman-nginx",
        detach=True,
        ports={"80/tcp": 8080},
        extra_hosts=extra_hosts,
        mounts=[
            Mount(target="/etc/nginx/nginx.conf", source=conf_path,
                  type="bind", read_only=True),
            Mount(target="/var/log/nginx", source=log_dir, type="bind"),
        ],
        network=_net(cli),
        restart_policy={"Name": "unless-stopped"},
    )
    return c.id


def _reload_nginx() -> None:
    """Regenera nginx.conf com os upstreams atuais e recarrega o sidecar."""
    if not state.nginx_container or not state.log_dir:
        return

    cli = _client()

    # containers escalados (índice 1+) estão na helmsman_net → acessíveis por nome
    extra: list[str] = []
    for cid in state.managed_containers[1:]:
        try:
            c = cli.containers.get(cid)
            extra.append(f"{c.name}:{state.target_port}")
        except Exception:
            pass

    conf_path = os.path.join(state.log_dir, "nginx.conf")
    with open(conf_path, "w") as f:
        f.write(render(state.target_host, state.target_port, extra))

    try:
        nginx = cli.containers.get(state.nginx_container)
        nginx.exec_run("nginx -s reload")
    except Exception:
        pass


def scale_to(target: int, image: str) -> None:
    """Ajusta o número de réplicas gerenciadas para `target`."""
    cli = _client()
    current = list(state.managed_containers)
    diff = target - len(current)

    if diff > 0:
        for i in range(diff):
            idx = len(current) + i + 1
            name = f"helmsman-svc-{idx}"
            _kill(cli, name)
            c = cli.containers.run(
                image,
                name=name,
                detach=True,
                network=_net(cli),
                restart_policy={"Name": "unless-stopped"},
            )
            with state._lock:
                state.managed_containers.append(c.id)

    elif diff < 0:
        to_stop = current[diff:]  # os últimos abs(diff) IDs
        for cid in to_stop:
            try:
                c = cli.containers.get(cid)
                c.stop(timeout=10)
                c.remove(force=True)
            except Exception:
                pass
        with state._lock:
            state.managed_containers = state.managed_containers[:target]

    _reload_nginx()


def stop_all() -> None:
    """Para e remove todos os containers gerenciados pelo helmsman."""
    cli = _client()

    for cid in list(state.managed_containers):
        try:
            c = cli.containers.get(cid)
            c.stop(timeout=5)
            c.remove(force=True)
        except Exception:
            pass
    state.managed_containers.clear()

    if state.nginx_container:
        try:
            c = cli.containers.get(state.nginx_container)
            c.stop(timeout=5)
            c.remove(force=True)
        except Exception:
            pass
        state.nginx_container = None

    try:
        net = cli.networks.get(_NET)
        net.remove()
    except Exception:
        pass
