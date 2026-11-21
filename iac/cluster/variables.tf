variable "kubeconfig" {
  description = "Ruta del kubeconfig"
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "Contexto del clúster (k3d crea k3d-<nombre>)"
  type        = string
  default     = "k3d-rednexus-demo"
}

variable "repo_url" {
  description = "Repositorio que sincroniza Argo CD"
  type        = string
  default     = "https://github.com/juanjosegl/RedNexus-Platform.git"
}

variable "git_revision" {
  description = "Rama, etiqueta o commit que despliega Argo CD (main en la demo)"
  type        = string
  default     = "main"
}

variable "sealed_secrets_key" {
  description = <<-EOT
    Llave privada de Sealed Secrets (PEM). Nunca va en Git: se guarda en el equipo del líder
    (~/.config/rednexus/sealed-secrets/tls.key) y en el secreto SEALED_SECRETS_KEY del repo.
  EOT
  type        = string
  default     = "~/.config/rednexus/sealed-secrets/tls.key"
}

variable "observabilidad" {
  description = "Instalar Grafana, Tempo y Prometheus en el clúster (unos 700 MB de RAM)"
  type        = bool
  default     = false
}
