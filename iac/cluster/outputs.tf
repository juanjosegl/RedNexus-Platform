output "argocd" {
  description = "Cómo entrar a Argo CD"
  value       = <<-EOT
    kubectl -n argocd port-forward svc/argo-cd-argocd-server 8081:80   -> http://localhost:8081
    usuario: admin
    contraseña: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
  EOT
}

output "aplicaciones" {
  description = "Aplicaciones de Argo CD creadas"
  value       = keys(local.applications)
}
