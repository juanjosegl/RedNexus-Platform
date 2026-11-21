#!/usr/bin/env bash
# PL-03 a PL-07: levanta la demo GitOps desde cero y cronometra cuánto tarda.
#
#   bash scripts/gitops-up.sh                      -> k3d (clúster rednexus-demo)
#   OBSERVABILIDAD=true bash scripts/gitops-up.sh  -> además Grafana, Tempo y Prometheus
#   GIT_REVISION=developer bash scripts/gitops-up.sh
#
# 1. Crea el clúster k3d (k3d/demo.yaml) si no existe.
# 2. OpenTofu (iac/cluster) instala Sealed Secrets con la llave del equipo, Kyverno, Argo CD
#    y las aplicaciones de Argo CD.
# 3. Argo CD sincroniza deploy/policies y deploy/overlays/demo desde GitHub: nadie ejecuta
#    kubectl apply. Las imágenes vienen de GHCR, firmadas.
#
# Requiere: docker, k3d, kubectl, tofu y la llave privada de Sealed Secrets en
# ~/.config/rednexus/sealed-secrets/tls.key (o SEALED_SECRETS_KEY_FILE). Pídesela al líder.
set -euo pipefail

cd "$(dirname "$0")/.."
START=$(date +%s)
CLUSTER=rednexus-demo
CONTEXT="k3d-$CLUSTER"
KEY_FILE="${SEALED_SECRETS_KEY_FILE:-$HOME/.config/rednexus/sealed-secrets/tls.key}"

for tool in docker k3d kubectl tofu; do
  command -v "$tool" >/dev/null || { echo "Falta $tool" >&2; exit 1; }
done
if [ ! -f "$KEY_FILE" ]; then
  echo "Falta la llave de Sealed Secrets en $KEY_FILE (ver docs/gitops.md)" >&2
  exit 1
fi

if ! k3d cluster list "$CLUSTER" >/dev/null 2>&1; then
  echo "==> Creando el clúster $CLUSTER"
  k3d cluster create --config k3d/demo.yaml
  # clúster nuevo: el estado de OpenTofu de un clúster anterior ya no sirve
  rm -f iac/cluster/terraform.tfstate iac/cluster/terraform.tfstate.backup
fi
kubectl config use-context "$CONTEXT" >/dev/null

echo "==> OpenTofu: Sealed Secrets, Kyverno, Argo CD y aplicaciones"
tofu -chdir=iac/cluster init -input=false >/dev/null
tofu -chdir=iac/cluster apply -input=false -auto-approve \
  -var "kube_context=$CONTEXT" \
  -var "sealed_secrets_key=$KEY_FILE" \
  -var "git_revision=${GIT_REVISION:-main}" \
  -var "observabilidad=${OBSERVABILIDAD:-false}"

echo "==> Esperando a que Argo CD sincronice (Synced y Healthy)"
for app in rednexus-politicas rednexus; do
  for _ in $(seq 1 90); do
    status=$(kubectl -n argocd get application "$app" \
      -o jsonpath='{.status.sync.status}/{.status.health.status}' 2>/dev/null || true)
    [ "$status" = "Synced/Healthy" ] && break
    sleep 10
  done
  echo "    $app: ${status:-sin estado}"
done

echo
echo "Listo en $(( $(date +%s) - START )) s"
echo "  App:     http://localhost:8090"
echo "  Argo CD: kubectl -n argocd port-forward svc/argo-cd-argocd-server 8081:80  -> http://localhost:8081"
echo "           usuario admin, contraseña:"
echo "           kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
if [ "${OBSERVABILIDAD:-false}" = true ]; then
  echo "  Grafana: kubectl -n observabilidad port-forward svc/lgtm 3002:3000  -> http://localhost:3002"
fi
