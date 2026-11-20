# 8. DevSecOps, CI/CD y despliegue

## 8.1 Pipeline

```text
rama feature/* ──PR──► developer ──PR──► test ──PR──► main
        │                  │                            │
        ▼                  ▼                            ▼
   CI build-test      Imagen: buildx amd64+arm64    CD: webhook de Dokploy
   (lint, tipos,      → GHCR (sha-xxxx, developer)   (docker-compose.dokploy.yml)
   pruebas, build)    → Trivy → SBOM (Syft)          Render despliega main
   Imagen (PR):       → Cosign sign + attest
   build + Trivy + SBOM
```

| Etapa | Herramienta | Dónde | Evidencia |
| --- | --- | --- | --- |
| Integración continua | GitHub Actions `build-test` | `.github/workflows/ci.yml` en los 3 repos | Check obligatorio en los rulesets |
| Construcción multiarquitectura | docker buildx + QEMU | `.github/workflows/image.yml` | Imagen `linux/amd64` y `linux/arm64` en GHCR |
| Registro | GitHub Container Registry | `ghcr.io/juanjosegl/rednexus-backend` y `rednexus-frontend` | Etiquetas `sha-xxxxxxx` y de rama |
| Escaneo de vulnerabilidades | Trivy | `image.yml` | Resumen del job; falla con críticas que tengan arreglo |
| SBOM | Syft (SPDX JSON) | `image.yml` | Artefacto del run y atestación en la imagen |
| Firma | Cosign keyless (OIDC de GitHub) | `image.yml` | `cosign verify` (comando en el workflow) |
| Despliegue continuo | Webhook de Dokploy | Job `deploy` del CI del backend en `main` | Despliegue en el servidor del diplomado |
| Demo gratuita | Render Blueprint + Neon | `render.yaml` | API y web en onrender.com |

## 8.2 Ambientes

| Ambiente | Para qué | Cómo se levanta |
| --- | --- | --- |
| Desarrollo | Programar | `docker compose up -d` (Postgres y Redis) + `npm run start:dev` / `npm run dev` |
| Sistema completo local | Probar todo | `docker compose up -d --build` en RedNexus-Platform (web en :8088) |
| Kubernetes local | Probar la orquestación | `bash scripts/k8s-up.sh` (k3d) o `bash scripts/k8s-up.sh minikube` (Ingress en :8080) |
| Demo (VPS del diplomado) | Sustentación | Dokploy en 169.58.151.195 con `docker-compose.dokploy.yml`, dominio por Traefik |
| Demo de respaldo | Si Dokploy falla | Render + Neon (se duerme a los 15 minutos sin tráfico) |

## 8.3 Seguridad de la plataforma

- Contenedores sin root, sin escalada de privilegios y con *capabilities* eliminadas; la API con sistema de archivos de solo lectura (`deploy/base`).
- Límites de memoria en todos los servicios, pensados para 8 GB.
- Servidor compartido: sin puertos publicados ni `container_name`; dominios por Traefik.
- Secretos: en desarrollo, valores de prueba en `deploy/components/dev`; en Dokploy, variables del proyecto (`POSTGRES_PASSWORD`, `JWT_SECRET`); Sealed Secrets previsto (PL-04).
- Rulesets: nadie fusiona sin PR y CI en verde, ni siquiera el administrador.

## 8.4 Bitácora de hallazgos de seguridad

| Fecha | Hallazgo | Fuente | Tratamiento |
| --- | --- | --- | --- |
| 2026-11-20 | Primer escaneo con Trivy de las imágenes de backend y frontend | Workflow "Imagen" | Ver el resumen del job en el PR de PL-01/PL-02; registrar aquí las críticas o altas que aparezcan y si se corrigieron (actualizar la imagen base) o se aceptaron |
| 2026-11-20 | `qwen2.5:3b` tiene licencia de investigación (no comercial) | Ficha de modelos | Aceptado para el uso académico; documentado cómo cambiarlo |
| 2026-11-20 | El JWT no se puede revocar antes de expirar | Revisión de diseño | Aceptado (ADR-008); al eliminar la cuenta, las rutas responden 401/404 |

> **Pendiente (issue PL-10):** cuando corra el workflow en `developer`, copiar a esta tabla lo que reporte Trivy y adjuntar la salida de `cosign verify`.
