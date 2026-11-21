locals {
  # Versiones fijas: un cambio de versión es un PR, igual que el código
  charts = {
    sealed_secrets = "2.22.0"  # controlador 0.41.2
    kyverno        = "3.10.0"  # Kyverno 1.20.0
    argo_cd        = "10.18.2" # Argo CD 3.6.2
    argocd_apps    = "2.0.8"
  }

  sync_policy = {
    automated   = { prune = true, selfHeal = true }
    syncOptions = ["CreateNamespace=true"]
    retry = {
      limit   = 5
      backoff = { duration = "10s", factor = 2, maxDuration = "3m" }
    }
  }

  applications = merge(
    {
      # Políticas de Kyverno antes que la app (sync-wave menor)
      rednexus-politicas = {
        namespace             = "argocd"
        project               = "default"
        additionalAnnotations = { "argocd.argoproj.io/sync-wave" = "-1" }
        source                = { repoURL = var.repo_url, targetRevision = var.git_revision, path = "deploy/policies" }
        destination           = { server = "https://kubernetes.default.svc" }
        syncPolicy            = local.sync_policy
      }
      rednexus = {
        namespace   = "argocd"
        project     = "default"
        source      = { repoURL = var.repo_url, targetRevision = var.git_revision, path = "deploy/overlays/demo" }
        destination = { server = "https://kubernetes.default.svc", namespace = "rednexus" }
        syncPolicy  = local.sync_policy
      }
    },
    var.observabilidad ? {
      rednexus-observabilidad = {
        namespace   = "argocd"
        project     = "default"
        source      = { repoURL = var.repo_url, targetRevision = var.git_revision, path = "deploy/observabilidad" }
        destination = { server = "https://kubernetes.default.svc", namespace = "observabilidad" }
        syncPolicy  = local.sync_policy
      }
    } : {}
  )
}

# --- PL-04: Sealed Secrets con llave propia -------------------------------------------
# El controlador usa esta llave en vez de generar una nueva, así los SealedSecret del repo
# (cifrados con deploy/sealed-secrets/pub-cert.pem) sirven en cualquier clúster que se
# reconstruya desde cero.
resource "kubernetes_secret_v1" "sealed_secrets_key" {
  metadata {
    name      = "sealed-secrets-key-rednexus"
    namespace = "kube-system"
    labels = {
      "sealedsecrets.bitnami.com/sealed-secrets-key" = "active"
    }
  }
  type = "kubernetes.io/tls"
  data = {
    "tls.crt" = file("${path.module}/../../deploy/sealed-secrets/pub-cert.pem")
    "tls.key" = startswith(var.sealed_secrets_key, "-----BEGIN") ? var.sealed_secrets_key : file(pathexpand(var.sealed_secrets_key))
  }
}

resource "helm_release" "sealed_secrets" {
  name       = "sealed-secrets"
  repository = "https://bitnami.github.io/sealed-secrets"
  chart      = "sealed-secrets"
  version    = local.charts.sealed_secrets
  namespace  = "kube-system"
  wait       = true

  values = [yamlencode({
    # nombre que kubeseal busca por defecto
    fullnameOverride = "sealed-secrets-controller"
    # sin rotación automática: la llave activa es siempre la del repo
    keyrenewperiod = "0"
    resources = {
      requests = { cpu = "10m", memory = "32Mi" }
      limits   = { memory = "128Mi" }
    }
  })]

  depends_on = [kubernetes_secret_v1.sealed_secrets_key]
}

# --- PL-05: Kyverno, solo el controlador de admisión (cabe en 8 GB) --------------------
resource "helm_release" "kyverno" {
  name             = "kyverno"
  repository       = "https://kyverno.github.io/kyverno/"
  chart            = "kyverno"
  version          = local.charts.kyverno
  namespace        = "kyverno"
  create_namespace = true
  wait             = true
  timeout          = 600

  values = [yamlencode({
    admissionController = {
      replicas = 1
      container = {
        resources = {
          requests = { cpu = "100m", memory = "128Mi" }
          limits   = { memory = "512Mi" }
        }
      }
    }
    backgroundController = { enabled = false }
    cleanupController    = { enabled = false }
    reportsController    = { enabled = false }
  })]
}

# --- PL-03: Argo CD liviano ------------------------------------------------------------
resource "helm_release" "argo_cd" {
  name             = "argo-cd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = local.charts.argo_cd
  namespace        = "argocd"
  create_namespace = true
  wait             = true
  timeout          = 600

  values = [yamlencode({
    dex           = { enabled = false }
    notifications = { enabled = false }
    configs = {
      # HTTP dentro del clúster; se entra con port-forward (ver docs/gitops.md)
      params = { "server.insecure" = true }
      # revisar Git cada minuto (por defecto son 3)
      cm = { "timeout.reconciliation" = "60s" }
    }
    controller     = { resources = { requests = { cpu = "100m", memory = "256Mi" }, limits = { memory = "768Mi" } } }
    repoServer     = { resources = { requests = { cpu = "50m", memory = "128Mi" }, limits = { memory = "512Mi" } } }
    server         = { resources = { requests = { cpu = "20m", memory = "64Mi" }, limits = { memory = "256Mi" } } }
    redis          = { resources = { requests = { cpu = "10m", memory = "32Mi" }, limits = { memory = "128Mi" } } }
    applicationSet = { resources = { requests = { cpu = "10m", memory = "32Mi" }, limits = { memory = "128Mi" } } }
  })]
}

# Las aplicaciones van en su propio release: así el plan no necesita los CRD de Argo CD
resource "helm_release" "argocd_apps" {
  name       = "rednexus-apps"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argocd-apps"
  version    = local.charts.argocd_apps
  namespace  = "argocd"

  values = [yamlencode({ applications = local.applications })]

  depends_on = [helm_release.argo_cd, helm_release.kyverno, helm_release.sealed_secrets]
}
