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
| Dokploy no despliega tras fusionar en `main` | Falta el secreto `DOKPLOY_WEBHOOK_URL` o falló el CI | Revisar el job `deploy`; redeploy manual desde la interfaz de Dokploy |
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

| Simulacro | Pasos | Resultado esperado | Resultado obtenido |
| --- | --- | --- | --- |
| Caída del nodo de IA | `brew services stop ollama` (o cerrar Ollama) y publicar una duda | Candidatos por etiquetas en segundos; log `por tags` | Probado en pruebas automáticas (`matching.service.spec.ts`); repetir en vivo antes de la sustentación |
| Caída de una réplica | `kubectl -n rednexus delete pod -l app.kubernetes.io/name=api` | Kubernetes crea otro pod; la web vuelve en segundos | Por registrar (issue PL-11) |
| Caída del worker con trabajos en cola | Borrar el pod del worker con solicitudes pendientes | Al volver, reencola y empareja las pendientes | Por registrar (issue PL-11) |
| Reconstrucción desde cero | `k3d cluster delete rednexus && bash scripts/k8s-up.sh` y cronometrar | El sistema completo vuelve con datos sintéticos | Por registrar con el tiempo (issue PL-11) |
