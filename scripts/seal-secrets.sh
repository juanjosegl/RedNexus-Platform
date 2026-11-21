#!/usr/bin/env bash
# PL-04: genera deploy/overlays/demo/sealed-secrets.yaml (secretos de la demo cifrados).
#
#   bash scripts/seal-secrets.sh            -> contraseñas nuevas al azar
#   POSTGRES_PASSWORD=... JWT_SECRET=... bash scripts/seal-secrets.sh
#
# Cifra sin conectarse al clúster, con el certificado público del repo
# (deploy/sealed-secrets/pub-cert.pem). Solo el controlador de Sealed Secrets, que tiene la
# llave privada, puede descifrarlos; por eso el archivo resultante sí se sube a Git.
#
# Requiere kubeseal (brew install kubeseal, o el binario de
# https://github.com/bitnami-labs/sealed-secrets/releases en Windows/WSL) y kubectl.
set -euo pipefail

cd "$(dirname "$0")/.."
CERT=deploy/sealed-secrets/pub-cert.pem
OUT=deploy/overlays/demo/sealed-secrets.yaml
NS=rednexus

command -v kubeseal >/dev/null || { echo "Falta kubeseal (brew install kubeseal)" >&2; exit 1; }

# Solo letras y números: la contraseña va dentro de DATABASE_URL
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-$(openssl rand -hex 24)}"
JWT_SECRET="${JWT_SECRET:-$(openssl rand -hex 32)}"

seal() {
  kubeseal --cert "$CERT" --format yaml --scope strict
}

# kubeseal ya separa cada documento con ---
{
  echo "# Generado por scripts/seal-secrets.sh: no editar a mano (PL-04)."
  echo "# Cifrado con deploy/sealed-secrets/pub-cert.pem; solo el controlador del clúster lo descifra."
  kubectl create secret generic postgres-secrets -n "$NS" --dry-run=client -o yaml \
    --from-literal=POSTGRES_USER=rednexus \
    --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    --from-literal=POSTGRES_DB=rednexus | seal
  kubectl create secret generic api-secrets -n "$NS" --dry-run=client -o yaml \
    --from-literal=DATABASE_URL="postgresql://rednexus:${POSTGRES_PASSWORD}@postgres:5432/rednexus" \
    --from-literal=JWT_SECRET="$JWT_SECRET" | seal
} >"$OUT"

echo "Listo: $OUT. Súbelo con un PR; Argo CD lo aplica y el controlador crea los Secret."
echo "Si cambias la contraseña de Postgres con la base ya creada, bórrala antes (ver docs/gitops.md)."
