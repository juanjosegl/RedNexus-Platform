# 8. DevSecOps, CI/CD y despliegue

## 8.1 Pipeline

```text
rama feature/* ──PR──► developer ──PR──► test ──PR──► main
        │                  │                 │            │
        ▼                  ▼                 ▼            ▼
   CI build-test      Imagen: buildx amd64+arm64 → GHCR (sha-xxxxxxx y rama)
   (lint, tipos,      → Trivy (falla con críticas con arreglo) → SBOM (Syft, SPDX)
   pruebas, build)    → Cosign sign + attest (keyless, OIDC de GitHub)
   Imagen (PR):                         │
   build + Trivy + SBOM                 ▼
                     Promover imágenes: cosign verify → PR que cambia newTag
                     en deploy/overlays/demo → developer → test → main
                                        │
                                        ▼
                     Argo CD sincroniza; Kyverno admite solo imágenes firmadas
```

| Etapa | Herramienta | Dónde | Evidencia |
| --- | --- | --- | --- |
| Integración continua | GitHub Actions `build-test` / `validate` | `.github/workflows/ci.yml` en los 3 repos | Check obligatorio en los rulesets ([captura](evidencias/gh-03-ci-backend.png)) |
| Construcción multiarquitectura | docker buildx + QEMU | `.github/workflows/image.yml` | Imagen `linux/amd64` y `linux/arm64` en GHCR ([captura](evidencias/gh-07-paquetes-ghcr.png)) |
| Escaneo de vulnerabilidades | Trivy | `image.yml` | Resumen del job; falla con críticas que tengan arreglo |
| SBOM | Syft (SPDX JSON) | `image.yml` | Artefacto del run y atestación en la imagen (523 paquetes en el backend, 71 en el frontend) |
| Firma | Cosign keyless (OIDC de GitHub) | `image.yml` | `cosign verify` (sección 8.5) |
| Promoción | *Promover imágenes* | `promover.yml` en Platform | PR que cambia `newTag` tras verificar las firmas |
| Despliegue continuo | Argo CD con *selfHeal* | `iac/cluster`, `deploy/overlays/demo` | 3 apps *Synced/Healthy* en el run de *GitOps (kind)* |
| Política de admisión | Kyverno 1.20 | `deploy/policies` | Rechaza `nginx:alpine` (registro no permitido) y una etiqueta sin firma |
| Prueba de punta a punta | *GitOps (kind)* | `gitops-e2e.yml` | OpenTofu 52 s, Argo CD 86 s, solicitud emparejada en 1 s, métrica del SLI y 1 traza ([captura](evidencias/gh-02-gitops-kind.png)) |

## 8.2 Ambientes

| Ambiente | Para qué | Cómo se levanta |
| --- | --- | --- |
| Desarrollo | Programar | `docker compose up -d` (Postgres y Redis) + `npm run start:dev` / `npm run dev` |
| Sistema completo con imágenes firmadas | Evaluar o hacer la demo | `docker compose -f compose.yaml -f compose.ghcr.yaml up -d` (web en :8088); con IA real, `.env` de `ia.env.example` o `bash scripts/demo-local.sh` |
| Sistema completo compilado | Probar código sin publicar | `docker compose up -d --build` en RedNexus-Platform |
| Kubernetes local | Probar la orquestación | `bash scripts/k8s-up.sh` (k3d) o `bash scripts/k8s-up.sh minikube` (Ingress en :8080) |
| Demo GitOps | Argo CD, Kyverno, Sealed Secrets | `bash scripts/gitops-up.sh` (k3d, :8090) o el workflow *GitOps (kind)* en Actions |
| Alternativas preparadas | Si hay servidor | `docker-compose.dokploy.yml` (Dokploy, no disponible para el equipo) y `render.yaml` (Render + Neon) |

## 8.3 Seguridad de la plataforma

- Contenedores sin root, sin escalada de privilegios y con *capabilities* eliminadas; la API con sistema de archivos de solo lectura (`deploy/base`).
- Límites de memoria en todos los servicios, pensados para 8 GB.
- Servidor compartido: sin puertos publicados ni `container_name`; dominios por Traefik.
- Secretos: en desarrollo, valores de prueba en `deploy/components/dev`; en la demo GitOps, `SealedSecret` cifrados con el certificado del repositorio (la llave privada nunca está en Git).
- Rulesets: nadie fusiona sin PR y CI en verde, ni siquiera el administrador.

## 8.4 Bitácora de hallazgos de seguridad

| Fecha | Hallazgo | Fuente | Tratamiento |
| --- | --- | --- | --- |
| 2026-11-20 | Backend (`node:24-alpine`): sin vulnerabilidades críticas con arreglo | Trivy, workflow "Imagen" (RedNexus-Backend#41) | Pasa |
| 2026-11-20 | Frontend (`nginx-unprivileged:1.29-alpine`): vulnerabilidades **críticas** con arreglo en paquetes de Alpine; el pipeline se detuvo | Trivy, workflow "Imagen" (RedNexus-Frontend#37) | Corregido: `apk upgrade --no-cache` en la etapa final del `Dockerfile`, sin dejar de correr como usuario 101. El escaneo siguiente pasa |
| 2026-11-20 | `qwen2.5:3b` tiene licencia de investigación (no comercial) | Ficha de modelos | Aceptado para el uso académico; documentado cómo cambiarlo |
| 2026-11-20 | El JWT no se puede revocar antes de expirar | Revisión de diseño | Aceptado (ADR-008); al eliminar la cuenta, las rutas responden 401/404 |
| 2026-11-24 | Backend `main` (`sha-6a2ee94`): 0 críticas, **11 altas** con arreglo en dependencias de Node: `undici` (4 CVE), `brace-expansion` (2), `body-parser`, `multer`, `mysql2`, `effect` y `deepmerge-ts` (dependencias del CLI de Prisma); 0 en el sistema operativo (Alpine 3.24) | Trivy 0.76 local sobre la imagen publicada ([detalle](evidencias/seguridad/trivy-backend-altas.md)) | Corregido en BE-24: `npm audit fix` y `overrides` de `effect` ≥ 3.22.1; `npm audit --omit=dev` queda en 0, las 118 pruebas pasan y `prisma migrate status` funciona |
| 2026-11-24 | Frontend `main`: 0 críticas y 0 altas; 6 medias y 4 bajas en `libcrypto3` y `libssl3` (OpenSSL de Alpine 3.23.4), todas con arreglo | Trivy 0.76 local | Aceptado por severidad; el `apk upgrade` del `Dockerfile` las corrige en la próxima construcción de la imagen |

## 8.5 Verificación de firmas

El 24/11/2026 se verificaron las imágenes publicadas en `main` desde un equipo externo al pipeline:

```text
$ cosign verify ghcr.io/juanjosegl/rednexus-backend:main \
    --certificate-identity-regexp "https://github.com/juanjosegl/RedNexus-.*/.github/workflows/image.yml@.*" \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com
Verification for ghcr.io/juanjosegl/rednexus-backend:main --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - Existence of the claims in the transparency log was verified offline
  - The code-signing certificate was verified using trusted certificate authority certificates
```

Resultado igual para `rednexus-frontend:main`. La salida completa ([evidencias/seguridad](evidencias/seguridad)) incluye dos entradas por imagen sobre el mismo *digest*: la firma (`https://sigstore.dev/cosign/sign/v1`) y la atestación del SBOM (`https://spdx.dev/Document`).
