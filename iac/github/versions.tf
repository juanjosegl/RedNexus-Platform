# PL-06: configuración de los 3 repos como código (reglas de ramas). Ver iac/README.md.
# El token sale de GITHUB_TOKEN (por ejemplo: export GITHUB_TOKEN=$(gh auth token)).
terraform {
  required_version = ">= 1.8"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.13"
    }
  }
}

provider "github" {
  owner = "juanjosegl"
}
