"""Gera nginx.conf via Jinja2 para o sidecar de coleta de RPS."""

from jinja2 import Template

_TEMPLATE = """\
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    log_format helmsman '$remote_addr - $remote_user [$time_local] '
                        '"$request" $status $body_bytes_sent';

    access_log /var/log/nginx/access.log helmsman;
    error_log  /var/log/nginx/error.log  warn;

    upstream backend {
        {% for server in servers %}server {{ server }};
        {% endfor %}
    }

    server {
        listen 80;

        location / {
            proxy_pass         http://backend;
            proxy_set_header   Host              $host;
            proxy_set_header   X-Real-IP         $remote_addr;
            proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_connect_timeout 5s;
            proxy_read_timeout    60s;
        }
    }
}
"""


def render(host: str, port: int, extra_servers: list | None = None) -> str:
    upstream = "host.docker.internal" if host in ("localhost", "127.0.0.1") else host
    servers = [f"{upstream}:{port}"] + (extra_servers or [])
    return Template(_TEMPLATE).render(servers=servers)
