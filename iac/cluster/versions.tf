# PL-06: el clúster de demo declarado con OpenTofu (namespaces, Sealed Secrets, Kyverno,
# Argo CD y las aplicaciones de Argo CD). Lo usa scripts/gitops-up.sh; ver iac/README.md.
terraform {
  required_version = ">= 1.8"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 3.5"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 3.3"
    }
  }
}

provider "kubernetes" {
  config_path    = pathexpand(var.kubeconfig)
  config_context = var.kube_context
}

provider "helm" {
  kubernetes = {
    config_path    = pathexpand(var.kubeconfig)
    config_context = var.kube_context
  }
}
