# Demo de RedNexus sin Dokploy

El Dokploy compartido del diplomado no quedó disponible para el equipo. Estas son las formas de mostrar el sistema funcionando, de la más completa a la de respaldo. Para la sustentación se usan **la 1 y la 2 juntas**.

| # | Opción | IA real | URL pública | Qué demuestra | Costo |
| --- | --- | --- | --- | --- | --- |
| 1 | **Demo local en el Mac** (`scripts/demo-local.sh`) | Sí: Ollama, whisper.cpp y el asistente RAG | Opcional, con `--tunel` (Cloudflare, temporal) | La app completa de punta a punta, con las imágenes firmadas de GHCR | Gratis, sin cuentas |
| 2 | **Demo GitOps en GitHub Actions** (workflow *GitOps (kind)*) | No (respaldo por etiquetas) | No: se muestra el resumen del run | CI/CD: OpenTofu, Argo CD, Sealed Secrets, Kyverno rechazando imágenes, SLO, métrica y traza | Gratis |
| 3 | Demo GitOps en el Mac (`scripts/gitops-up.sh`) | Sí | No | La interfaz de Argo CD en vivo (*Synced*, *drift*, rollback) | Gratis; usa casi toda la RAM, no corre junto con la 1 |
| 4 | Render + Neon (`render.yaml` en RedNexus-Backend) | No (`mock`) | Sí, permanente | Un enlace que funciona sin el Mac encendido | Gratis; se duerme a los 15 minutos sin tráfico y pide crear dos cuentas |

## 1. Demo local en el Mac

Para el jurado o cualquier otro equipo, la forma más simple es la del [README](../README.md#instalar-y-probar-rednexus-guía-para-el-jurado) (`compose.ghcr.yaml`, niveles 1 y 2). Este script es la versión completa del Mac del líder.

Requisitos (ya instalados en el Mac del líder): Colima, Ollama con `qwen2.5:3b` y `paraphrase-multilingual`, `whisper-cpp`, `ffmpeg`, `cloudflared` y el asistente de `asistente-rag/` con su `.env`.

```bash
bash scripts/demo-local.sh                   # http://localhost:8088
bash scripts/demo-local.sh --tunel           # además una URL https://*.trycloudflare.com
bash scripts/demo-local.sh --observabilidad  # además Grafana con el SLO en http://localhost:3002
bash scripts/demo-local.sh --apagar
```

El script enciende Ollama, whisper.cpp (si encuentra `~/.cache/rednexus/whisper/ggml-base.bin`) y Open WebUI. Luego levanta Postgres, Redis, API, worker y web con las imágenes **firmadas** de GHCR (`TAG=main` por defecto), sin compilar nada. Al final imprime qué IA quedó activa:

```text
IA: ollama · voz: whisper · asistente: openwebui
```

Si algo no está, sigue con el respaldo (`mock`) y lo dice; la app nunca se cae por la IA (ADR-006).

**Modelo de voz** (148 MB, una sola vez):

```bash
mkdir -p ~/.cache/rednexus/whisper
curl -L -o ~/.cache/rednexus/whisper/ggml-base.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

**URL pública con `--tunel`.** Cloudflare da una dirección `https://<palabras>.trycloudflare.com` gratis y sin cuenta, que dura mientras la terminal siga abierta. Sirve para que el docente o los compañeros entren desde su celular durante la exposición. Cambia cada vez, así que se comparte en el momento. Al cerrar la terminal (Ctrl+C) deja de existir.

### Resultado del ensayo (21/11/2026, Mac M1 de 8 GB; repetido el 24/11 con resultados equivalentes: texto 11 s, voz 13 s, asistente 25 s)

| Prueba | Resultado |
| --- | --- |
| Solicitud por texto: "derivadas con la regla de la cadena" | Clasificada como matemáticas, nivel intermedio; 3 candidatos por búsqueda semántica con su explicación, en **19 s** (SLO: < 30 s) |
| Nota de voz (audio generado con `say`) | Transcrita por whisper.cpp y emparejada como bases de datos, en **11 s** |
| Asistente de `/ayuda`: "¿Cómo califico a la persona que me ayudó?" | Respuesta paso a paso desde Open WebUI con fuentes `calificaciones.md` y `emparejamiento.md`, en 25 s |
| URL pública con `cloudflared` | `/api/health` respondió 200 desde internet |
| Memoria de los contenedores | Unos 1,1 GB en total (Open WebUI 750 MB); Ollama corre fuera de Docker |

### Antes de la sustentación

1. La noche anterior: `git pull` en Platform, `bash scripts/demo-local.sh` y una solicitud de prueba. La primera llamada a Ollama carga el modelo en memoria y tarda más.
2. Cerrar Chrome, Docker que no se use y la VPN. Con 8 GB, cada aplicación abierta cuenta.
3. Llevar el celular con datos por si la red de la sala falla: la demo local no necesita internet, solo el túnel.
4. Tener abiertos en pestañas el último run verde de **GitOps (kind)** y el de **Imagen** (Trivy, SBOM, firma).

## 2. Demo GitOps en GitHub Actions

En RedNexus-Platform: **Actions → GitOps (kind) → Run workflow** (rama `main`). Tarda unos 8 minutos, así que se lanza al empezar la exposición y se muestra al final. Su resumen trae la tabla con los tiempos, los rechazos de Kyverno, la latencia de la solicitud, la métrica y la traza. Ver [docs/gitops.md](gitops.md).

## 4. Render + Neon (respaldo con enlace permanente)

Los pasos están en el README de RedNexus-Backend (sección *Render + Neon*). Hay que crear la cuenta en Render y en Neon; el resto ya está en `render.yaml`. La IA queda en `mock`, porque Render gratis no puede correr Ollama.
