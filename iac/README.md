# Infraestructura como código con OpenTofu (PL-06)

Dos configuraciones independientes, cada una con su propio estado:

| Carpeta | Proveedores | Qué declara |
| --- | --- | --- |
| [`cluster/`](cluster) | `hashicorp/kubernetes`, `hashicorp/helm` | La llave de Sealed Secrets, los releases de Helm de Sealed Secrets, Kyverno y Argo CD (versiones fijas) y las aplicaciones de Argo CD |
| [`github/`](github) | `integrations/github` | Las 9 reglas de ramas de los 3 repos (`developer`, `test` y `main`: solo por PR y con el CI en verde) |

El CI de este repo corre `tofu fmt -check` y `tofu validate` en las dos en cada PR.

## Clúster de la demo

Lo normal es no llamarlo a mano: `bash scripts/gitops-up.sh` crea el clúster k3d y aplica esta configuración. A mano:

```bash
cd iac/cluster
tofu init
tofu plan  -var kube_context=k3d-rednexus-demo
tofu apply -var kube_context=k3d-rednexus-demo -var observabilidad=true
tofu output argocd        # cómo entrar a Argo CD
```

| Variable | Por defecto | Qué es |
| --- | --- | --- |
| `kube_context` | `k3d-rednexus-demo` | Contexto de `kubectl` (en kind: `kind-rednexus-demo`) |
| `git_revision` | `main` | Rama o commit que despliega Argo CD |
| `sealed_secrets_key` | `~/.config/rednexus/sealed-secrets/tls.key` | Ruta (o contenido PEM) de la llave privada de Sealed Secrets |
| `observabilidad` | `false` | Agrega la app de Grafana, Tempo y Prometheus |

## Reglas de GitHub

Las reglas ya existían (se crearon a mano en octubre); `imports.tf` las trae al estado sin recrearlas. El plan actual confirma que el código coincide con lo que hay en GitHub:

```text
$ export GITHUB_TOKEN=$(gh auth token)
$ tofu -chdir=iac/github init && tofu -chdir=iac/github plan
Plan: 9 to import, 0 to add, 0 to change, 0 to destroy.
```

`tofu apply` hace la importación. Desde ahí, un cambio en las reglas (por ejemplo, otro check obligatorio) se hace en `github/main.tf` por PR y se aplica con `tofu apply`; si alguien cambia una regla a mano en GitHub, `tofu plan` lo muestra como *drift*.

## Estado

El estado queda en `terraform.tfstate` dentro de cada carpeta y **nunca se sube a Git** (está en `.gitignore`): contiene la llave de Sealed Secrets y datos de los repos. En `cluster/` es desechable: al crear un clúster nuevo `gitops-up.sh` lo borra y lo vuelve a generar. En `github/` lo guarda el líder; si se pierde, `tofu apply` vuelve a importar las reglas.

`.terraform.lock.hcl` sí va en Git: fija las versiones exactas de los proveedores para todos.
