# RedNexus Platform

Plataforma de **RedNexus**: todo lo necesario para construir, desplegar y operar la aplicación. El código vive en los otros dos repos:

| Repo | Contenido |
| --- | --- |
| [RedNexus-Backend](https://github.com/juanjosegl/RedNexus-Backend) | API NestJS y worker de IA |
| [RedNexus-Frontend](https://github.com/juanjosegl/RedNexus-Frontend) | Interfaz Vue 3 |
| **RedNexus-Platform** (este) | Docker Compose, Kubernetes, documentación, el asistente de soporte con RAG, y más adelante GitOps, IaC y observabilidad |

## Empieza aquí

| Documento | Para qué |
| --- | --- |
| **[Guía del equipo](docs/guia-del-equipo.md)** | Instalar todo (Windows), clonar, levantar el sistema y cómo trabajamos con Git |
| [Tareas](docs/tareas.md) | Qué hay que hacer, con ramas y commits por tarea |
| [CONTRIBUTING](CONTRIBUTING.md) | Resumen de las reglas de ramas, commits y PR |
| [Entorno en Mac](docs/entorno-mac.md) | Instalación en macOS (Apple Silicon) |
| **[Entrega final](docs/entrega/README.md)** | Documento del diplomado por capítulos: problema, requisitos, ADR, privacidad, MLOps, pruebas, DevSecOps, runbook, sostenibilidad y guion de la demo |

Los tres repos deben quedar **en la misma carpeta**:

```text
rednexus/
├── RedNexus-Backend/
├── RedNexus-Frontend/
└── RedNexus-Platform/
```

## Cómo correr RedNexus según lo que vayas a hacer

| Si vas a… | Dónde | Comando | Qué obtienes |
| --- | --- | --- | --- |
| **Ver el sistema completo funcionando** | RedNexus-Platform | `docker compose up -d --build` | App en http://localhost:8088 |
| **Programar el frontend** | RedNexus-Platform, y luego RedNexus-Frontend | `docker compose up -d --build api worker`, y luego `npm run dev` en el frontend | Backend listo en Docker, con datos de prueba; tu frontend en http://localhost:5173 con recarga automática |
| **Programar el backend** | RedNexus-Backend | `docker compose up -d` (Postgres y Redis) y `npm run start:dev` (ver su README para la primera vez) | Tu API en http://localhost:3000 con recarga automática |
| **Probar en Kubernetes** | RedNexus-Platform | `bash scripts/k8s-up.sh` (k3d) o `bash scripts/k8s-up.sh minikube` | App en http://localhost:8080 |
| **Apagar** | Donde lo levantaste | `docker compose down` | Libera memoria; los datos se conservan (con `-v` se borran) |

- **Contrato de la API (Swagger):** http://localhost:3000/api/docs cuando el backend corre en Docker o con `npm run start:dev`. Ahí ves cada endpoint, qué recibe y qué responde.
- **Datos de prueba:** al levantar con este `compose.yaml` se cargan datos sintéticos (por ejemplo `ana.demo@rednexus.dev`).
- **Código nuevo de un compañero:** las imágenes se construyen con el código que tengas en las carpetas hermanas. Haz `git pull` en RedNexus-Backend o RedNexus-Frontend y repite el comando con `--build`.
- **No mezcles en el puerto 3000** la API de Docker (`docker compose up … api`) con `npm run start:dev`: usa una u otra.

La API siempre responde bajo `/api` (por ejemplo `/api/health`). El frontend llama a `/api`, y quien la reenvía al backend es Vite en desarrollo o Nginx en Docker y Kubernetes. Por eso la misma imagen sirve en cualquier ambiente.

### Ver lo que está corriendo (dashboards)

No hace falta Docker Desktop en Mac. Estos son gratuitos y livianos:

| Herramienta | Para qué | Instalación |
| --- | --- | --- |
| Extensión **Docker** de VS Code (`ms-azuretools.vscode-docker`) | Ver contenedores e imágenes, sus logs, y abrir una terminal dentro | Desde VS Code (recomendada en cada repo) |
| **Headlamp** | Dashboard gráfico de Kubernetes (pods, logs, eventos). Sirve con k3d y minikube | Mac: `brew install --cask headlamp`. Windows: `winget install headlamp` |
| **k9s** | Dashboard de Kubernetes en la terminal, muy liviano | Mac: `brew install k9s`. WSL: ver https://k9scli.io |
| `minikube dashboard -p rednexus` | Dashboard web oficial de Kubernetes | Viene con minikube |

En Windows, Docker Desktop ya trae su propio panel de contenedores.

### Kubernetes local

Sirven **k3d o minikube**: los manifiestos son los mismos y solo cambia el overlay (`deploy/overlays/k3d` o `deploy/overlays/minikube`). Usa uno a la vez, porque los dos juntos no caben en 8 GB.

```bash
bash scripts/k8s-up.sh              # k3d
bash scripts/k8s-up.sh minikube     # minikube
```

El script hace todo esto:
1. Crea el clúster `rednexus` si no existe. En minikube usa su propio perfil, `rednexus`, para no chocar con otro minikube que tengas.
2. Construye las imágenes desde los repos hermanos (`rednexus-api`, que sirve para API, worker y migraciones, y `rednexus-web`) y las carga en el clúster.
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
compose.yaml              # sistema completo o solo backend con Docker Compose
.github/workflows/ci.yml  # valida manifiestos (kubeconform), compose y scripts en cada PR
k3d/cluster.yaml          # clúster local declarado como código (1 nodo, Ingress en :8080)
deploy/
├── base/                 # manifiestos comunes: postgres, redis, api, worker, web, ingress
├── components/dev/       # común a clústeres locales: imágenes :dev y secretos de prueba
└── overlays/
    ├── k3d/              # Ingress Traefik, Ollama en host.k3d.internal
    └── minikube/         # Ingress NGINX, Ollama en host.minikube.internal
scripts/k8s-up.sh         # construir + cargar imágenes + desplegar (k3d o minikube)
docs/                     # guías de entorno (más adelante: ADRs, privacidad, runbooks)
asistente-rag/            # asistente de soporte: base de conocimiento, modelo, golden dataset y evaluación
```

### Arquitectura en Kubernetes

```text
navegador ──► Ingress (Traefik) ──► web (Nginx) ──/api──► api (NestJS) ──► postgres (pgvector)
                                                            │
                                                            └──► redis ◄── worker ──► Ollama / whisper.cpp
                                                                                       (fuera del clúster)
```

- **api:** antes de arrancar, su `initContainer` (con la misma imagen) aplica las migraciones de Prisma.
- **worker:** usa la misma imagen que la API, pero corre otro proceso (`node dist/worker`).
- **Seguridad:** los contenedores corren sin root, sin escalada de privilegios y con *capabilities* eliminadas, y la API tiene el sistema de archivos en solo lectura. Todos los pods tienen límites de memoria pensados para equipos de 8 GB.
- **Secretos:** los de `components/dev` son valores de prueba, solo para desarrollo. El ambiente de demo usará Sealed Secrets.

## Asistente de soporte con RAG (actividad 2 del módulo 6)

Chat de ayuda que responde cómo usar RedNexus con **solo** la documentación del proyecto: RAG en Open WebUI con
modelos locales de Ollama, integrado en la página `/ayuda` del frontend a través de `POST /api/support/chat` del
backend. Todo lo de la actividad (base de conocimiento, modelo, golden dataset, evaluación e informe) está en
[asistente-rag/](asistente-rag), y las tareas en [asistente-rag/docs/tareas.md](asistente-rag/docs/tareas.md).

- **Entrega:** [asistente-rag/ENTREGA.md](asistente-rag/ENTREGA.md) (resultado y dónde está cada requisito).
- **Informe:** [Informe-modelo-rag-RedNexus.pdf](asistente-rag/docs/Informe-modelo-rag-RedNexus.pdf) (secciones A a G).
- **Resultado:** 88,5 % de éxito en el golden dataset de 52 casos (meta 70 %), con fragmentos de 400 tokens y 60 de
  solapamiento; detalle en [asistente-rag/runs/](asistente-rag/runs).

### Aportes del equipo

<!-- Cada integrante reemplaza SOLO su propia línea, con su nombre completo y lo que aportó. -->

- **Juan Jose Gutierrez Lasso** ([@juanjosegl](https://github.com/juanjosegl)): arquitectura e integración
  (módulo `support` del backend y página `/ayuda`), PQRS de punta a punta (endpoint y página `/pqrs`),
  configuración del RAG y del modelo en Open WebUI, system prompt, scripts de configuración, evaluación y armado
  del PDF, documentos de emparejamiento, normas, privacidad, PQRS, calificaciones y preguntas frecuentes, 44 casos
  del golden dataset, corridas de evaluación y secciones C a G del informe.

- **Victor Daniel Fernandez** ([@daniel200231](https://github.com/daniel200231)): componente de mensaje del chat de la página de ayuda (FE-11), con sus pruebas.

- **Jose Sebastian Fernandez** ([@josesfa](https://github.com/josesfa)): _pendiente (FE-10)_

- **Maria Paula Andrade** ([@MariPau-dev](https://github.com/MariPau-dev)): preguntas frecuentes en la página de ayuda y acceso a la ayuda desde el inicio (FE-12), con sus pruebas.

- **Maria Alejandra Guzman** ([@alejandraguzman12](https://github.com/alejandraguzman12)): documento de la base de
  conocimiento "Registro y perfil", 8 casos del golden dataset (registro_perfil), portada e índice del informe.

## Flujo de trabajo

Una rama temporal por tarea, creada desde `developer` → PR a `developer` (y la rama se borra) → el líder promueve `developer` → `test` → `main`. Paso a paso en [CONTRIBUTING.md](CONTRIBUTING.md).
