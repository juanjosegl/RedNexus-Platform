# Observabilidad y SLO (PL-07)

La API y el worker se instrumentan con OpenTelemetry (`src/telemetry/` en RedNexus-Backend) y envían por OTLP a un stack liviano: **Grafana + Tempo (trazas) + Prometheus (métricas) + collector**, todo en un contenedor (`grafana/otel-lgtm`). El tablero **RedNexus · SLO y operación** (`deploy/observabilidad/dashboards/rednexus-slo.json`) se carga solo.

## SLO

> El **95 %** de las solicitudes de ayuda recibe candidatos en **menos de 30 segundos**.

| | |
| --- | --- |
| **SLI** | `rednexus.match.latency`: tiempo desde que se crea la solicitud hasta que el worker guarda el top 3 (incluye la espera en la cola) |
| **Consulta** | `sum(increase(rednexus_match_latency_seconds_bucket{le=~"30(.0)?"}[$__range])) / sum(increase(rednexus_match_latency_seconds_count[$__range]))` |
| **Presupuesto de error** | 5 % de las solicitudes del periodo. El tablero muestra cuánto queda |
| **Qué hacer si se incumple** | Ver el runbook ([docs/entrega/09-runbook.md](../docs/entrega/09-runbook.md)): casi siempre es el nodo de IA lento o caído (las solicitudes caen al respaldo por etiquetas) o la cola llena |

Además: latencia y errores por endpoint (`http.server.request.duration`), duración y errores de cada trabajo de IA (`rednexus.job.duration`) y la traza completa de cada solicitud: `POST /api/help-requests` (API) → `match process` (worker), unidas porque la API pasa el `traceparent` dentro del trabajo de BullMQ.

## Local con Docker

```bash
docker compose -f observabilidad/compose.yaml up -d     # Grafana en http://localhost:3002
```

En el `.env` del backend agrega `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318` y reinicia la API y el worker. Si usas el `compose.yaml` de este repo, el valor es `http://host.docker.internal:4318`. Crea un par de solicitudes desde la app y abre el tablero (las métricas llegan cada 15 s). Las trazas se buscan en **Explore → Tempo**.

## En Kubernetes (demo GitOps)

`OBSERVABILIDAD=true bash scripts/gitops-up.sh` agrega la app de Argo CD `rednexus-observabilidad`. El overlay demo ya apunta la API y el worker a `http://lgtm.observabilidad:4318`.

```bash
kubectl -n observabilidad port-forward svc/lgtm 3002:3000    # http://localhost:3002
```

## Grafana Cloud (sin gastar RAM)

En el plan gratuito de Grafana Cloud, *Connections → OpenTelemetry (OTLP)* da el endpoint y un token. En Dokploy, Render o el `.env`:

```text
OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp-gateway-prod-<región>.grafana.net/otlp
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Basic <base64 de instancia:token>
```

Luego importa `deploy/observabilidad/dashboards/rednexus-slo.json` en *Dashboards → New → Import*, eligiendo los datasources de Prometheus y Tempo de tu cuenta.
