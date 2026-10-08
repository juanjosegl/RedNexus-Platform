# RedNexus Platform

Plataforma de **RedNexus**: todo lo necesario para construir, desplegar y operar la aplicación. El código vive en los otros dos repos:

| Repo | Contenido |
| --- | --- |
| [RedNexus-Backend](https://github.com/juanjosegl/RedNexus-Backend) | API NestJS y worker de IA |
| [RedNexus-Frontend](https://github.com/juanjosegl/RedNexus-Frontend) | Interfaz Vue 3 |
| **RedNexus-Platform** (este) | Docker Compose, Kubernetes, y más adelante GitOps, IaC, observabilidad y documentación |

## Preparar tu equipo

- **Windows:** [docs/entorno-windows.md](docs/entorno-windows.md)
- **macOS:** [docs/entorno-mac.md](docs/entorno-mac.md)

Los tres repos deben quedar **en la misma carpeta**:

```text
rednexus/
├── RedNexus-Backend/
├── RedNexus-Frontend/
└── RedNexus-Platform/
```

## Tres formas de correr RedNexus

| Para qué | Cómo | URL |
| --- | --- | --- |
| **Programar día a día** | Postgres y Redis con el `docker compose` del backend; API y frontend con `npm` (ver README de cada repo) | http://localhost:5173 |
| **Probar las imágenes Docker** | `docker compose up -d --build` en este repo | http://localhost:8088 |
| **Kubernetes local con k3d** | `bash scripts/k8s-up.sh` en este repo | http://localhost:8080 |
| **Kubernetes local con minikube** | `bash scripts/k8s-up.sh minikube` en este repo | http://localhost:8080 (con port-forward, ver abajo) |

La API siempre responde bajo `/api` (por ejemplo `/api/health`). El frontend llama a `/api` y quien la reenvía al backend es Vite en desarrollo, o Nginx en Docker y Kubernetes. Por eso la misma imagen sirve en cualquier ambiente.

### Kubernetes local

Sirven **k3d o minikube**: los manifiestos son los mismos y solo cambia el overlay (`deploy/overlays/k3d` o `deploy/overlays/minikube`). Usa uno a la vez, porque los dos juntos no caben en 8 GB.

```bash
bash scripts/k8s-up.sh              # k3d
bash scripts/k8s-up.sh minikube     # minikube
```

El script hace todo esto:
1. Crea el clúster `rednexus` si no existe. En minikube usa su propio perfil, `rednexus`, para no chocar con otro minikube que tengas.
2. Construye las imágenes desde los repos hermanos y las carga en el clúster.
3. Aplica los manifiestos y espera a que todo esté listo.

Puedes repetirlo cada vez que cambies código. La primera vez tarda varios minutos; después, cerca de uno.

**Con minikube**, para entrar desde el navegador deja corriendo esto en otra terminal y abre http://localhost:8080. Con el driver docker, la IP de minikube no es accesible desde el navegador, y el port-forward lleva el Ingress a localhost:

```bash
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80
```

| | k3d | minikube |
| --- | --- | --- |
| Estado | `kubectl -n rednexus get pods` | igual |
| Logs de la API | `kubectl -n rednexus logs deploy/api` | igual |
| Apagar (libera RAM, no borra datos) | `k3d cluster stop rednexus` | `minikube stop -p rednexus` |
| Encender | `k3d cluster start rednexus` | `minikube start -p rednexus` |
| Borrar todo | `k3d cluster delete rednexus` | `minikube delete -p rednexus` |
| Cambiar `kubectl` a este clúster | `kubectl config use-context k3d-rednexus` | `kubectl config use-context rednexus` |

## Estructura

```text
compose.yaml              # stack completo con Docker Compose
k3d/cluster.yaml          # clúster local declarado como código (1 nodo, Ingress en :8080)
deploy/
├── base/                 # manifiestos comunes: postgres, redis, api, worker, web, ingress
├── components/dev/       # común a clústeres locales: imágenes :dev y secretos de prueba
└── overlays/
    ├── k3d/              # Ingress Traefik, Ollama en host.k3d.internal
    └── minikube/         # Ingress NGINX, Ollama en host.minikube.internal
scripts/k8s-up.sh         # construir + cargar imágenes + desplegar (k3d o minikube)
docs/                     # guías de entorno (más adelante: ADRs, privacidad, runbooks)
```

### Arquitectura en Kubernetes

```text
navegador ──► Ingress (Traefik) ──► web (Nginx) ──/api──► api (NestJS) ──► postgres (pgvector)
                                                            │
                                                            └──► redis ◄── worker ──► Ollama / whisper.cpp
                                                                                       (fuera del clúster)
```

- **api:** antes de arrancar, su `initContainer` aplica las migraciones de Prisma.
- **worker:** usa la misma imagen que la API, pero corre otro proceso (`node dist/worker`).
- **Seguridad:** los contenedores corren sin root, sin escalada de privilegios y con *capabilities* eliminadas, y la API tiene el sistema de archivos en solo lectura. Todos los pods tienen límites de memoria pensados para equipos de 8 GB.
- **Secretos:** los de `components/dev` son valores de prueba, solo para desarrollo. El ambiente de demo usará Sealed Secrets.

## Flujo de trabajo

Una rama temporal por tarea, creada desde `developer` → PR a `developer` (y la rama se borra) → el líder promueve `developer` → `test` → `main`. Paso a paso en [CONTRIBUTING.md](CONTRIBUTING.md).
