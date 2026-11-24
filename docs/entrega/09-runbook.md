# 9. Runbook de operación (PL-09)

Qué hacer cuando algo falla. Los comandos de Kubernetes sirven igual en k3d y minikube (namespace `rednexus`); en Docker Compose se usa `docker compose logs <servicio>`.

## 9.1 Diagnóstico rápido

| Pregunta | Comando |
| --- | --- |
| ¿Responde la API? | `curl -s <host>/api/health` → `{"status":"ok"}` |
| ¿Qué pods hay y en qué estado? | `kubectl -n rednexus get pods` |
| ¿Por qué no arranca un pod? | `kubectl -n rednexus describe pod <pod>` y `kubectl -n rednexus logs <pod> --previous` |
| ¿Qué está haciendo el worker? | `kubectl -n rednexus logs deploy/worker -f` (cada emparejamiento dice estrategia, candidatos y ms) |
| ¿Cuánta memoria usa cada uno? | `kubectl -n rednexus top pods` o `docker stats` |
| ¿Está vivo Ollama? | `curl -s http://<nodo-ia>:11434/api/tags` |
| ¿Está vivo whisper.cpp? | `curl -s -o /dev/null -w "%{http_code}" http://<nodo-ia>:8178/` |

## 9.2 Fallas comunes

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| Las solicitudes se quedan en Pendiente | El worker no corre o no llega a Redis | `kubectl -n rednexus rollout restart deploy/worker`; al arrancar vuelve a encolar las pendientes |
| Candidatos de baja calidad y el log dice `por tags` | Ollama apagado o modelo no descargado | Encender Ollama en el nodo de IA y `ollama pull paraphrase-multilingual qwen2.5:3b`; el sistema sigue funcionando mientras tanto |
| Después de cambiar de modelo de embeddings nadie aparece | Los vectores viejos no son comparables con los nuevos | `npm run db:seed` (borra los embeddings de los perfiles sintéticos) y reiniciar el worker para reindexar |
| La nota de voz se queda en "(nota de voz en transcripción)" | whisper.cpp apagado o sin `--convert` | Levantar `whisper-server ... --convert`; BullMQ reintenta 3 veces. Con `TRANSCRIBE_PROVIDER=mock` la demo no depende de whisper |
| `api` en `CrashLoopBackOff` | Falta una variable (`JWT_SECRET`, `DATABASE_URL`) o falló la migración | Revisar los logs del initContainer `migrate` y las variables del Secret |
| El asistente responde siempre el mismo texto | Open WebUI apagado o API key inválida (usa el respaldo) | Levantar Open WebUI y revisar `OPENWEBUI_API_KEY`; ver `asistente-rag/README.md` |
| Argo CD no aplica la versión nueva | El PR de *Promover imágenes* no llegó a `main`, o Kyverno rechazó la imagen (sin firma) | Revisar la app en Argo CD (*Sync status* y *Events*); `kubectl -n rednexus get events --sort-by=.lastTimestamp`; forzar con *Refresh* y *Sync* |
| `no space left on device` al levantar Postgres | Disco de la VM de Docker lleno (Colima tiene 40 GB) | `docker system df`; borrar imágenes que no se usan (`docker image prune -a` borra todas las no usadas: revisar antes) |
| El pod se reinicia con `OOMKilled` | Límite de memoria bajo | Subir `resources.limits.memory` en el overlay o liberar RAM (apagar el otro clúster) |

## 9.3 Respaldo y restauración de PostgreSQL

```bash
# respaldo (k8s)
kubectl -n rednexus exec statefulset/postgres -- pg_dump -U rednexus -Fc rednexus > respaldo-$(date +%F).dump
# restauración
kubectl -n rednexus exec -i statefulset/postgres -- pg_restore -U rednexus -d rednexus --clean --if-exists < respaldo-AAAA-MM-DD.dump
# Docker Compose: lo mismo con  docker compose exec -T postgres ...
```

Los embeddings se guardan en la misma base (pgvector), así que el respaldo los incluye.

## 9.4 Simulacros

Se automatizaron en [`scripts/simulacros.sh`](../../scripts/simulacros.sh) sobre el stack de Docker Compose de la demo (`scripts/demo-local.sh`), que usa las mismas imágenes que Kubernetes. Resultados del 24/11/2026 en el Mac M1 de 8 GB:

| Simulacro | Pasos | Resultado esperado | Resultado obtenido |
| --- | --- | --- | --- |
| Caída del nodo de IA | Se detiene Ollama y se publica una duda de cálculo | Candidatos por etiquetas en segundos; log `por tags` | `MATCHED` en **1,2 s**; el log del worker dice `por tags`. Al encender Ollama, la siguiente solicitud vuelve a usar la IA |
| Caída del worker con trabajos en cola | Se detiene el worker, se publica una duda y se vuelve a encender | La solicitud espera en *Pendiente* y se empareja al volver | Con el worker caído: `PENDING`. Al volver: `MATCHED` en **11 s** (incluye cargar los modelos) |
| Caída de la API | `docker compose kill api` y `docker compose start api` | La web vuelve en segundos, sin perder datos | Durante la caída `/api/health` no responde; `/api/health/ready` (base y Redis arriba) vuelve **4,5 s** después del arranque |
| Respaldo y restauración | `pg_dump -Fc` y `pg_restore` en una base nueva | Los conteos coinciden | Respaldo de 48 KB en **0,5 s**; usuarios/solicitudes/perfiles con embedding: 51/12/0 en la original y en la restaurada |
| Reconstrucción desde cero | Clon limpio de Platform y `docker compose -f compose.yaml -f compose.ghcr.yaml up -d` en un proyecto nuevo | El sistema completo vuelve con datos sintéticos | Clon en **2 s** y aplicación lista en **10 s** con las imágenes ya descargadas (migraciones y 50 perfiles); con IA real, primera solicitud emparejada en 16 s |
| Reconstrucción del clúster GitOps | Workflow *GitOps (kind)* en `main`: clúster nuevo, OpenTofu y Argo CD | Apps *Synced/Healthy* y una solicitud emparejada | OpenTofu **52 s**, Argo CD sincronizado en **86 s**, solicitud en 1 s; 4 min de punta a punta |

**Lecciones del simulacro:** (1) recrear un servicio con `docker compose up` sin las variables de la demo lo deja con la IA de respaldo (`mock`); para reiniciar se usa `start`/`restart` o se vuelve a correr `scripts/demo-local.sh`. (2) Los embeddings de los perfiles se recalculan bajo demanda después de un `seed`, por eso el conteo de perfiles con embedding puede ser 0 justo después de reconstruir. (3) El disco de la VM de Docker se llenó al descargar Grafana durante el ensayo; se agregó la falla a la tabla 9.2.

**En Kubernetes (k3d o minikube)** los mismos casos se ejecutan con `kubectl -n rednexus delete pod -l app.kubernetes.io/name=api` (Kubernetes crea otro pod) y `kubectl -n rednexus delete pod -l app.kubernetes.io/name=worker`; el Deployment los recrea y el worker reencola lo pendiente al arrancar. No se cronometraron en esta entrega porque el clúster local y la demo no caben juntos en 8 GB.
