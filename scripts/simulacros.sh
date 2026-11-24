#!/usr/bin/env bash
# Simulacros del runbook (PL-11) sobre el stack de Docker Compose (scripts/demo-local.sh).
#
#   bash scripts/simulacros.sh            -> corre los 4 simulacros e imprime una tabla en Markdown
#
# 1. Caída del nodo de IA: se detiene Ollama y se publica una duda (debe emparejar por etiquetas).
# 2. Caída del worker con trabajos en cola: la duda queda Pendiente y se empareja al volver.
# 3. Caída de la API: se mata el contenedor y se cronometra hasta que /api/health/ready responde.
# 4. Respaldo y restauración: pg_dump y pg_restore en una base nueva; se comparan los conteos.
# Usa solo datos sintéticos (laura.demo@rednexus.dev). Ollama se vuelve a encender al final.
set -euo pipefail
cd "$(dirname "$0")/.."

B=http://localhost:8088/api
now() { python3 -c 'import time; print(time.time())'; }
dt() { python3 -c "print(round($(now) - $1, 1))"; }
token() {
  curl -fsS -X POST "$B/auth/login" -H 'Content-Type: application/json' \
    -d "{\"email\":\"$1\",\"password\":\"demo12345\"}" | jq -r .accessToken
}
publicar() { # texto -> id
  curl -fsS -X POST "$B/help-requests" -H "Authorization: Bearer $T" -H 'Content-Type: application/json' \
    -d "{\"text\":\"$1\"}" | jq -r .id
}
esperar_estado() { # id segundos -> estado final
  local s
  for _ in $(seq 1 "$2"); do
    s=$(curl -fsS "$B/help-requests/$1" -H "Authorization: Bearer $T" | jq -r .status)
    [ "$s" != PENDING ] && { echo "$s"; return; }
    sleep 1
  done
  echo PENDING
}

T=$(token laura.demo@rednexus.dev)
FILAS=()

echo "==> 1. Caída del nodo de IA"
OLLAMA_CMD=$(ps -o command= -p "$(pgrep -f 'ollama serve' | head -1)" 2>/dev/null || true)
pkill -f 'ollama serve' || true
sleep 2
t0=$(now)
id=$(publicar "Necesito ayuda con integrales por partes para el parcial de cálculo")
estado=$(esperar_estado "$id" 120)
seg=$(dt "$t0")
estrategia=$(docker compose logs worker --since 3m 2>/dev/null | grep -o 'por tags' | tail -1 || true)
FILAS+=("| Caída del nodo de IA | Ollama detenido; se publica una duda de cálculo | $estado en $seg s; log del worker: \`${estrategia:-sin dato}\` |")
echo "    $estado en $seg s ($estrategia)"
OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_NUM_PARALLEL=1 \
  nohup ollama serve >"${TMPDIR:-/tmp}/rednexus-ollama.log" 2>&1 &
for _ in $(seq 1 30); do curl -fsS -o /dev/null http://localhost:11434/api/tags 2>/dev/null && break; sleep 1; done
echo "    Ollama encendido de nuevo (${OLLAMA_CMD:+antes: $OLLAMA_CMD})"

echo "==> 2. Caída del worker con trabajos en cola"
docker compose stop worker >/dev/null
id=$(publicar "Cómo configuro una VLAN en un switch Cisco para el laboratorio de redes")
sleep 5
antes=$(curl -fsS "$B/help-requests/$id" -H "Authorization: Bearer $T" | jq -r .status)
t0=$(now)
docker compose start worker >/dev/null
estado=$(esperar_estado "$id" 120)
seg=$(dt "$t0")
FILAS+=("| Caída del worker con cola | Worker detenido; se publica una duda; se enciende el worker | Con el worker caído: $antes. Al volver: $estado en $seg s |")
echo "    $antes -> $estado en $seg s"

echo "==> 3. Caída de la API"
docker compose kill api >/dev/null
caida=$(curl -s --max-time 5 -o /dev/null -w '%{http_code}' "$B/health" || true)
t0=$(now)
# start (no up): reusa el mismo contenedor con su imagen y sus variables, como un reinicio tras la caída
docker compose start api >/dev/null
for _ in $(seq 1 120); do curl -fsS -o /dev/null "$B/health/ready" 2>/dev/null && break; sleep 1; done
seg=$(dt "$t0")
FILAS+=("| Caída de la API | \`docker compose kill api\` y \`start api\` | Durante la caída /api/health responde $caida; /api/health/ready vuelve $seg s después del arranque |")
echo "    caída $caida, recuperada en $seg s"

echo "==> 4. Respaldo y restauración de PostgreSQL"
t0=$(now)
docker compose exec -T postgres pg_dump -U rednexus -Fc rednexus >"${TMPDIR:-/tmp}/rednexus-respaldo.dump"
tam=$(du -h "${TMPDIR:-/tmp}/rednexus-respaldo.dump" | cut -f1)
docker compose exec -T postgres psql -U rednexus -qc 'DROP DATABASE IF EXISTS rednexus_restaurada' -c 'CREATE DATABASE rednexus_restaurada' >/dev/null
docker compose exec -T postgres pg_restore -U rednexus -d rednexus_restaurada --no-owner <"${TMPDIR:-/tmp}/rednexus-respaldo.dump"
seg=$(dt "$t0")
contar() { docker compose exec -T postgres psql -U rednexus -d "$1" -tAc \
  'SELECT (SELECT count(*) FROM "User")||'"'"'/'"'"'||(SELECT count(*) FROM "HelpRequest")||'"'"'/'"'"'||(SELECT count(*) FROM "User" WHERE embedding IS NOT NULL)'; }
orig=$(contar rednexus)
rest=$(contar rednexus_restaurada)
docker compose exec -T postgres psql -U rednexus -qc 'DROP DATABASE rednexus_restaurada' >/dev/null
FILAS+=("| Respaldo y restauración | \`pg_dump -Fc\` y \`pg_restore\` en una base nueva | Respaldo de $tam en $seg s; usuarios/solicitudes/perfiles con embedding: original $orig, restaurada $rest |")
echo "    $tam, $seg s, $orig vs $rest"

echo
echo "| Simulacro | Pasos | Resultado ($(date '+%Y-%m-%d %H:%M')) |"
echo "| --- | --- | --- |"
printf '%s\n' "${FILAS[@]}"
