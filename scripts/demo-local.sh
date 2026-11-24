#!/usr/bin/env bash
# Demo de RedNexus en el equipo del líder (Mac M1), con la IA real y sin servidor en la nube.
#
#   bash scripts/demo-local.sh                 -> app en http://localhost:8088
#   bash scripts/demo-local.sh --tunel         -> además una URL pública https://*.trycloudflare.com
#   bash scripts/demo-local.sh --observabilidad -> además Grafana con el SLO en http://localhost:3002
#   bash scripts/demo-local.sh --apagar        -> apaga todo (los datos se conservan)
#
# Qué levanta:
#   - Ollama nativo (GPU del Mac con Metal): qwen2.5:3b y paraphrase-multilingual
#   - whisper.cpp (notas de voz) en :8178, si encuentra el modelo ggml-base.bin
#   - Open WebUI con el asistente RAG en :3001 (asistente-rag/), si está creado
#   - Postgres, Redis, API, worker y web con las imágenes FIRMADAS de GHCR (no compila nada)
#
# Sin argumentos no publica nada en internet. Con --tunel, Cloudflare da una URL temporal y
# gratuita (sin cuenta) mientras el script siga corriendo; Ctrl+C la cierra.
set -euo pipefail

cd "$(dirname "$0")/.."
export TAG="${TAG:-main}"
COMPOSE=(docker compose -f compose.yaml -f compose.ghcr.yaml)
WHISPER_MODEL="${WHISPER_MODEL:-$HOME/.cache/rednexus/whisper/ggml-base.bin}"
LOGS="${TMPDIR:-/tmp}/rednexus-demo"
mkdir -p "$LOGS"

TUNEL=false
OBSERVABILIDAD=false
for arg in "$@"; do
  case "$arg" in
    --tunel) TUNEL=true ;;
    --observabilidad) OBSERVABILIDAD=true ;;
    --apagar)
      "${COMPOSE[@]}" down
      docker compose -f observabilidad/compose.yaml down 2>/dev/null || true
      pkill -f "whisper-server.*8178" 2>/dev/null || true
      echo "Apagado. Ollama y Open WebUI siguen corriendo (ollama stop / docker compose -f asistente-rag/docker-compose.yml down)."
      exit 0
      ;;
    *)
      echo "Uso: bash scripts/demo-local.sh [--tunel] [--observabilidad] [--apagar]" >&2
      exit 1
      ;;
  esac
done

wait_http() { # url segundos
  for _ in $(seq 1 "$2"); do
    curl -fsS -o /dev/null "$1" 2>/dev/null && return 0
    sleep 1
  done
  return 1
}

echo "==> Ollama (IA local)"
if ! curl -fsS -o /dev/null http://localhost:11434/api/tags 2>/dev/null; then
  command -v ollama >/dev/null || { echo "Falta Ollama: brew install ollama" >&2; exit 1; }
  nohup ollama serve >"$LOGS/ollama.log" 2>&1 &
  wait_http http://localhost:11434/api/tags 30 || { echo "Ollama no arrancó (ver $LOGS/ollama.log)" >&2; exit 1; }
fi
for model in qwen2.5:3b paraphrase-multilingual; do
  ollama list | grep -q "^$model" || ollama pull "$model"
done
export AI_PROVIDER=ollama

echo "==> whisper.cpp (notas de voz)"
if curl -fsS -o /dev/null http://localhost:8178 2>/dev/null; then
  export TRANSCRIBE_PROVIDER=whisper
elif command -v whisper-server >/dev/null && [ -f "$WHISPER_MODEL" ]; then
  nohup whisper-server -m "$WHISPER_MODEL" --convert --language es --host 0.0.0.0 --port 8178 \
    >"$LOGS/whisper.log" 2>&1 &
  wait_http http://localhost:8178 30 && export TRANSCRIBE_PROVIDER=whisper
else
  echo "    Sin whisper-server o sin $WHISPER_MODEL: las notas de voz usan el modo de prueba."
  echo "    Para la voz real: brew install whisper-cpp y descarga ggml-base.bin (ver docs/demo-local.md)."
fi

echo "==> Asistente de soporte (Open WebUI)"
if [ -f asistente-rag/.env ] && grep -q '^OPENWEBUI_API_KEY=.\+' asistente-rag/.env; then
  docker compose -f asistente-rag/docker-compose.yml up -d >/dev/null
  if wait_http http://localhost:3001/health 120; then
    OPENWEBUI_API_KEY=$(grep '^OPENWEBUI_API_KEY=' asistente-rag/.env | cut -d= -f2-)
    export OPENWEBUI_API_KEY SUPPORT_PROVIDER=openwebui
  fi
fi
[ "${SUPPORT_PROVIDER:-mock}" = openwebui ] || echo "    Sin Open WebUI listo: el chat de /ayuda usa las respuestas de respaldo."

if [ "$OBSERVABILIDAD" = true ]; then
  echo "==> Observabilidad (Grafana, Tempo y Prometheus)"
  docker compose -f observabilidad/compose.yaml up -d
  export OTEL_EXPORTER_OTLP_ENDPOINT=http://host.docker.internal:4318
fi

echo "==> RedNexus con las imágenes firmadas de GHCR ($TAG)"
"${COMPOSE[@]}" pull -q migrate web
"${COMPOSE[@]}" up -d --force-recreate
wait_http http://localhost:8088/api/health 180 || { "${COMPOSE[@]}" ps; echo "La app no respondió" >&2; exit 1; }

echo
echo "Listo:"
echo "  App:      http://localhost:8088   (usuario de prueba ana.demo@rednexus.dev / demo12345)"
echo "  Swagger:  http://localhost:3000/api/docs"
echo "  IA: $AI_PROVIDER · voz: ${TRANSCRIBE_PROVIDER:-mock} · asistente: ${SUPPORT_PROVIDER:-mock}"
[ "$OBSERVABILIDAD" = true ] && echo "  Grafana:  http://localhost:3002   (tablero RedNexus · SLO y operación)"

if [ "$TUNEL" = true ]; then
  command -v cloudflared >/dev/null || { echo "Falta cloudflared: brew install cloudflared" >&2; exit 1; }
  echo
  echo "==> URL pública temporal (Cloudflare). Deja esta terminal abierta; Ctrl+C la cierra."
  cloudflared tunnel --no-autoupdate --url http://localhost:8088 2>&1 \
    | grep --line-buffered -oE 'https://[a-z0-9-]+\.trycloudflare\.com' \
    | while read -r url; do echo "  Pública:  $url"; done
fi
