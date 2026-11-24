# Guion del video: instalar RedNexus siguiendo el README y hacer la demo

El docente pidió un video que muestre cómo seguir el `README.md` paso a paso para montar el proyecto y hacer la prueba demo en ese escenario. Este guion sigue al pie de la letra la sección [Instalar y probar RedNexus](../../README.md#instalar-y-probar-rednexus-guía-para-el-jurado).

**Duración objetivo:** 12 a 15 minutos. **Grabación:** pantalla completa a 1080p con micrófono (en Mac, `Cmd+Shift+5`; en Windows, la Barra de juego con `Win+Alt+R` u OBS). **Idioma:** español, en tercera persona o en plural ("se clona", "ahora abrimos").

## Antes de grabar

1. Partir de un escenario limpio, para que se vea la instalación real:
   - Apagar la demo local si está corriendo: `bash scripts/demo-local.sh --apagar`.
   - Clonar en una carpeta nueva, por ejemplo `~/video-rednexus` (no la carpeta de trabajo).
   - Si se quiere mostrar la descarga de imágenes, borrarlas antes: `docker rmi ghcr.io/juanjosegl/rednexus-backend:main ghcr.io/juanjosegl/rednexus-frontend:main` (con internet lento, mejor dejarlas y decirlo).
2. Ollama abierto y con los modelos ya descargados (`ollama list`), para no esperar 2,5 GB en cámara.
3. Cerrar notificaciones, Slack y pestañas personales. Aumentar la letra de la terminal (`Cmd +`).
4. Tener abiertas en pestañas: el README en GitHub, el run verde de **Imagen** (Backend) y el de **GitOps (kind)** (Platform).

## Guion

| Minuto | Se muestra | Se dice (idea) |
| --- | --- | --- |
| 0:00–0:45 | Portada del README en GitHub | Qué es RedNexus, quiénes somos y que el video sigue el README tal cual, en un equipo con Docker y sin compilar nada |
| 0:45–1:30 | Sección **Requisitos** | Git, Docker (Desktop en Windows, Colima en Mac), puertos 8088 y 3000; versiones: `git --version`, `docker compose version` |
| 1:30–3:30 | Terminal: los 3 comandos del **nivel 1** | `git clone`, `cd`, `docker compose -f compose.yaml -f compose.ghcr.yaml up -d`. Explicar que `compose.ghcr.yaml` usa las imágenes firmadas de GHCR y que el contenedor `migrate` aplica las migraciones y carga 50 perfiles sintéticos |
| 3:30–4:00 | `docker compose ps -a` y http://localhost:8088/api/health/ready | Todos arriba; la salud reporta base de datos y Redis |
| 4:00–6:30 | Navegador: pasos 1 a 4 del **recorrido** (registro con autorización, solicitud por texto, aceptar en ventana privada, calificar) | En el nivel 1 no hay modelos: el emparejamiento usa el respaldo por etiquetas (degradación controlada, ADR-006) |
| 6:30–8:00 | Terminal: **nivel 2** (`ollama list`, `cp ia.env.example .env`, `up -d`, `logs worker`) | Ahora la misma app con IA local; el log dice `Proveedor de IA: ollama` y `rednexus-matching v1` |
| 8:00–10:00 | Navegador: nueva solicitud con IA real, nota de voz (si está whisper), asistente de **Ayuda** y PQRS | Clasificación (área, temas, nivel), 3 candidatos con explicación, menos de 30 s (SLO) |
| 10:00–11:00 | Swagger en http://localhost:3000/api/docs | Contrato de la API; `GET /api/users/me/export` y `DELETE /api/users/me` (Ley 1581) |
| 11:00–12:30 | GitHub: run de **Imagen** y de **GitOps (kind)**; `cosign verify` en la terminal | La imagen que acabamos de usar está escaneada (Trivy), con SBOM y firmada; Argo CD la despliega y Kyverno rechaza imágenes sin firma |
| 12:30–13:30 | Terminal: `docker compose ... down -v` | Cómo apagar y volver al estado inicial; dónde está el runbook |
| 13:30–14:00 | [ENTREGABLES.md](ENTREGABLES.md) | Cada entregable del diplomado con su evidencia |

## Comandos exactos (para copiar durante la grabación)

```bash
git --version && docker compose version
git clone https://github.com/juanjosegl/RedNexus-Platform.git
cd RedNexus-Platform
docker compose -f compose.yaml -f compose.ghcr.yaml up -d
docker compose -f compose.yaml -f compose.ghcr.yaml ps -a
curl http://localhost:8088/api/health/ready
ollama list
cp ia.env.example .env
docker compose -f compose.yaml -f compose.ghcr.yaml up -d
docker compose logs worker | grep -iE "proveedor|rednexus-matching"
cosign verify ghcr.io/juanjosegl/rednexus-backend:main \
  --certificate-identity-regexp 'https://github.com/juanjosegl/RedNexus-.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
docker compose -f compose.yaml -f compose.ghcr.yaml down -v
```

## Tiempos medidos en el ensayo (24/11/2026, Mac M1 de 8 GB)

| Paso | Tiempo |
| --- | --- |
| Clonar Platform | 2 s |
| Nivel 1 hasta `/api/health/ready` (imágenes ya descargadas) | 10 s |
| Solicitud con respaldo por etiquetas (nivel 1) | menos de 4 s |
| Nivel 2 (recrear API y worker con Ollama) | 5 s |
| Solicitud con IA real: clasificar, embeddings, top 3 y explicación | 11 a 16 s |
| Nota de voz con whisper.cpp hasta tener candidatos | 13 s |
| Respuesta del asistente de `/ayuda` (Open WebUI con RAG) | 25 s |

## Después de grabar

1. Subir el video a YouTube como **no listado** (o a Drive con enlace de lectura) y poner el enlace en el README y en la monografía (anexo).
2. Volver a encender la demo de trabajo: `bash scripts/demo-local.sh`.
