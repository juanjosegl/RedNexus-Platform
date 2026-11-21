# GitOps, secretos e imágenes firmadas (PL-03 a PL-06)

La demo GitOps corre en un clúster k3d propio (`rednexus-demo`, app en http://localhost:8090). Nadie ejecuta `kubectl apply`: **lo que está en Git es lo que corre**.

```text
PR fusionado ─► GitHub (deploy/overlays/demo, deploy/policies)
                   │  Argo CD revisa Git cada minuto
                   ▼
         Argo CD ─► aplica en el clúster ─► Kyverno revisa cada pod (firma y registro)
                                         └► Sealed Secrets descifra los secretos
```

| Pieza | Dónde | Para qué |
| --- | --- | --- |
| OpenTofu | `iac/cluster` | Instala Sealed Secrets, Kyverno, Argo CD y las aplicaciones de Argo CD (ver [iac/README.md](../iac/README.md)) |
| Argo CD | app `rednexus` → `deploy/overlays/demo` | La app con las imágenes de GHCR fijadas por commit (`sha-xxxxxxx`) |
| Argo CD | app `rednexus-politicas` → `deploy/policies` | Políticas de Kyverno |
| Argo CD | app `rednexus-observabilidad` → `deploy/observabilidad` | Grafana, Tempo y Prometheus (opcional) |
| Sealed Secrets | `deploy/overlays/demo/sealed-secrets.yaml` | Contraseña de Postgres y `JWT_SECRET`, cifrados |
| Kyverno | `deploy/policies` | Solo imágenes de rednexus firmadas por el workflow "Imagen" y solo registros permitidos |

## Levantar la demo desde cero

Necesitas Docker (Colima en Mac), `k3d`, `kubectl`, `tofu` (OpenTofu) y la **llave privada de Sealed Secrets** en `~/.config/rednexus/sealed-secrets/tls.key`. La llave no está en Git: pídesela al líder por un canal privado.

```bash
bash scripts/gitops-up.sh                       # app, Argo CD, Kyverno y Sealed Secrets
OBSERVABILIDAD=true bash scripts/gitops-up.sh   # además Grafana (unos 700 MB más)
```

El script imprime cuánto tardó: es la evidencia de la **reconstrucción desde cero cronometrada** (PL-09). Para borrar todo: `k3d cluster delete rednexus-demo`. El clúster de desarrollo (`bash scripts/k8s-up.sh`) es otro; enciende uno a la vez.

El mismo flujo corre en GitHub Actions con kind en cada PR que toca `deploy/` o `iac/cluster` (workflow **GitOps (kind)**). Su resumen muestra los tiempos, los rechazos de Kyverno, la latencia de una solicitud real y las firmas verificadas.

## Argo CD

```bash
kubectl -n argocd port-forward svc/argo-cd-argocd-server 8081:80     # http://localhost:8081
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
```

Usuario `admin`. Las tres aplicaciones deben estar **Synced** y **Healthy**.

| Quiero… | Cómo |
| --- | --- |
| **Desplegar una versión nueva** | Actions → **Promover imágenes** → *Run workflow*. Verifica las firmas y abre un PR que cambia `newTag` en `deploy/overlays/demo/kustomization.yaml`. Al fusionarlo en `developer` y promoverlo a `main`, Argo CD lo aplica en menos de un minuto |
| **Sincronizar ya, sin esperar** | En la interfaz, *Refresh* y luego *Sync*; o `kubectl -n argocd annotate application rednexus argocd.argoproj.io/refresh=hard --overwrite` |
| **Ver *drift*** (alguien cambió algo a mano) | Prueba: `kubectl -n rednexus scale deploy/web --replicas=0`. Argo CD marca la app *OutOfSync* y, como tiene `selfHeal`, la devuelve a lo que dice Git en segundos. En la interfaz, *App diff* muestra la diferencia |
| **Rollback** | La forma GitOps: `git revert` del PR que cambió la imagen y fusionar. En una emergencia: *History and rollback* en la interfaz (desactiva el auto-sync hasta que Git quede igual) |
| **Ver por qué falló un pod** | Pestaña *Events* del recurso, o `kubectl -n rednexus get events --sort-by=.lastTimestamp` |

## Sealed Secrets: crear y rotar un secreto

Los secretos de la demo se cifran con el certificado público del repo (`deploy/sealed-secrets/pub-cert.pem`) y solo el controlador del clúster, que tiene la llave privada, los puede descifrar. Por eso `sealed-secrets.yaml` sí va en Git y los `Secret` en texto plano nunca.

```bash
brew install kubeseal          # Windows/WSL: binario de github.com/bitnami-labs/sealed-secrets/releases
bash scripts/seal-secrets.sh   # contraseñas nuevas al azar
```

1. El script reescribe `deploy/overlays/demo/sealed-secrets.yaml`. Súbelo con un PR.
2. Al sincronizar, el controlador actualiza los `Secret` y los pods toman los valores al reiniciarse (`kubectl -n rednexus rollout restart deploy/api deploy/worker`).
3. **Contraseña de Postgres:** Postgres solo la lee al crear la base. Si la base ya existe, bórrala antes en la demo (`kubectl -n rednexus delete pvc data-postgres-0` y reinicia `postgres-0`) o cámbiala también con `ALTER USER`.

**Llave del clúster.** OpenTofu carga la llave del equipo como llave activa (`sealed-secrets-key-rednexus` en `kube-system`) y el controlador no la rota (`keyrenewperiod: 0`). Así, los secretos del repo sirven en cualquier clúster reconstruido. Para rotarla: genera un par nuevo con `openssl req -x509 -nodes -newkey rsa:4096 -days 3650 -keyout tls.key -out tls.crt -subj "/CN=sealed-secret/O=rednexus"`, reemplaza `pub-cert.pem` y la llave local, actualiza el secreto `SEALED_SECRETS_KEY` del repo, vuelve a correr `seal-secrets.sh` y sube todo en un PR.

## Kyverno: solo imágenes firmadas

| Política | Qué rechaza |
| --- | --- |
| `rednexus-imagenes-firmadas` (ImageValidatingPolicy) | Imágenes `ghcr.io/juanjosegl/rednexus-*` sin firma de Cosign hecha por `image.yml` de Backend o Frontend en `developer`, `test` o `main` |
| `rednexus-registros-permitidos` (ValidatingPolicy) | Cualquier imagen que no sea de GHCR de rednexus, `pgvector/pgvector` o `redis` |

Evidencia (también la produce el workflow GitOps en cada PR):

```bash
kubectl -n rednexus run intruso --image=nginx:alpine
# Error from server: ... Imagen no permitida en rednexus...
kubectl -n rednexus run sin-firma --image=ghcr.io/juanjosegl/rednexus-backend:sha-0000000
# Error from server: ... rednexus-imagenes-firmadas ...
```

Cosign v3 guarda la firma como *referrer* OCI junto a la imagen (no como etiqueta `.sig`); en Kyverno 1.20 ese formato lo verifica `ImageValidatingPolicy`, por eso no se usa la `ClusterPolicy` clásica.

## Secretos del repositorio

| Secreto | Repo | Para qué | Obligatorio |
| --- | --- | --- | --- |
| `SEALED_SECRETS_KEY` | Platform | Contenido de `tls.key`, para el workflow GitOps (kind) | Sí, para ese workflow |
| `PLATFORM_PR_TOKEN` | Platform | Token personal (*fine-grained*, permisos Contents y Pull requests en Platform) para que el PR de "Promover imágenes" dispare el CI | No: sin él se usa el token de Actions |
| `PLATFORM_DISPATCH_TOKEN` | Backend y Frontend | Token personal con permiso *Contents* en Platform, para que publicar en `main` dispare "Promover imágenes" solo | No: sin él se dispara a mano |
