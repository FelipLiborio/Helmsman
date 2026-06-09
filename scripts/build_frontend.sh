#!/usr/bin/env bash
# Builda o frontend e copia o dist/ para dentro do pacote Python.
# Rode isso antes de "pip install -e ." ou de gerar o wheel.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "[build] instalando dependências do frontend..."
cd "$ROOT/frontend"
npm install

echo "[build] buildando com vite..."
npm run build

echo "[build] copiando dist/ → helmsman/frontend_dist/..."
DEST="$ROOT/helmsman/frontend_dist"
rm -rf "$DEST"
cp -r "$ROOT/frontend/dist" "$DEST"

echo "[build] pronto — $DEST"
