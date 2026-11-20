#!/usr/bin/env bash
# Levanta RedNexus completo en Kubernetes local. Funciona en macOS y en WSL2 (Windows).
#   bash scripts/k8s-up.sh             -> k3d (por defecto)
#   bash scripts/k8s-up.sh minikube    -> minikube (perfil "rednexus")
# Requiere: docker, kubectl y k3d o minikube, y los repos RedNexus-Backend y
# RedNexus-Frontend clonados junto a este. Se puede repetir: reconstruye y redespliega.
set -euo pipefail

cd "$(dirname "$0")/.."
TOOL="${1:-k3d}"
CLUSTER=rednexus
IMAGES=(rednexus-api:dev rednexus-web:dev)

case "$TOOL" in
  k3d | minikube) ;;
  *)
    echo "Uso: bash scripts/k8s-up.sh [k3d|minikube]" >&2
    exit 1
    ;;
esac

for repo in RedNexus-Backend RedNexus-Frontend; do
  if [ ! -d "../$repo" ]; then
    echo "Falta ../$repo. Clona los tres repos en la misma carpeta." >&2
    exit 1
  fi
done

if [ "$TOOL" = k3d ]; then
  if ! k3d cluster list "$CLUSTER" >/dev/null 2>&1; then
    echo "==> Creando el clúster $CLUSTER (k3d)"
    k3d cluster create --config k3d/cluster.yaml
  fi
  kubectl config use-context "k3d-$CLUSTER" >/dev/null
else
  # Perfil propio para no chocar con otro minikube que ya tengas (por ejemplo el de clase)
  if ! minikube status -p "$CLUSTER" >/dev/null 2>&1; then
    echo "==> Iniciando minikube (perfil $CLUSTER)"
    minikube start -p "$CLUSTER" --driver=docker --cpus=2 --memory="${MINIKUBE_MEMORY:-3072}"
  fi
  echo "==> Activando el Ingress de minikube (ingress-nginx)"
  minikube addons enable ingress -p "$CLUSTER" >/dev/null
  kubectl config use-context "$CLUSTER" >/dev/null
  kubectl -n ingress-nginx wait --for=condition=ready pod \
    -l app.kubernetes.io/component=controller --timeout=300s >/dev/null
fi

echo "==> Construyendo imagenes desde los repos hermanos"
docker compose build api web

echo "==> Cargando imagenes en el clúster"
if [ "$TOOL" = k3d ]; then
  k3d image import "${IMAGES[@]}" --cluster "$CLUSTER"
else
  for image in "${IMAGES[@]}"; do
    minikube -p "$CLUSTER" image load "$image"
  done
fi

echo "==> Aplicando manifiestos (deploy/overlays/$TOOL)"
kubectl apply -k "deploy/overlays/$TOOL"

# Las imagenes :dev conservan el nombre al reconstruirse; reiniciar fuerza a usar las nuevas
kubectl -n rednexus rollout restart deployment/api deployment/worker deployment/web >/dev/null

echo "==> Esperando a que todo este listo"
kubectl -n rednexus rollout status statefulset/postgres --timeout=180s
for d in redis api worker web; do
  kubectl -n rednexus rollout status "deployment/$d" --timeout=180s
done

echo
if [ "$TOOL" = k3d ]; then
  echo "Listo: http://localhost:8080 (API en http://localhost:8080/api/health)"
else
  # Con el driver docker la IP de minikube no es accesible desde el navegador de Windows;
  # el port-forward lleva el Ingress a localhost.
  echo "Listo. Para abrir la app deja corriendo esto en otra terminal:"
  echo "  kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80"
  echo "y entra a http://localhost:8080 (API en http://localhost:8080/api/health)"
fi
