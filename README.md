# RedNexus Platform

Plataforma de **RedNexus**: todo lo necesario para construir, desplegar y operar la aplicación. El código vive en los otros dos repos:

| Repo | Contenido |
| --- | --- |
| [RedNexus-Backend](https://github.com/juanjosegl/RedNexus-Backend) | API NestJS y worker de IA |
| [RedNexus-Frontend](https://github.com/juanjosegl/RedNexus-Frontend) | Interfaz Vue 3 |
| **RedNexus-Platform** (este) | Docker Compose, Kubernetes, GitOps con Argo CD, IaC con OpenTofu, políticas de Kyverno, observabilidad, ML, el asistente de soporte con RAG y la documentación |

RedNexus es una red de apoyo académico: un estudiante publica una duda (por texto o nota de voz) y una IA que corre en la propia infraestructura la clasifica, la compara por significado con los perfiles y propone a los tres compañeros que mejor pueden ayudar, explicando por qué. Proyecto integrador del Diplomado CloudForge AI 5.0 (Unicomfacauca, 2026).

**Entregables del diplomado:** [docs/entrega/ENTREGABLES.md](docs/entrega/ENTREGABLES.md) relaciona cada uno de los 15 entregables con su evidencia.

## Instalar y probar RedNexus (guía para el jurado)

Dos niveles. El **nivel 1** corre en cualquier computador con Docker y no descarga modelos de IA (usa el respaldo por etiquetas). El **nivel 2** agrega la IA real con Ollama. Ninguno compila código: usan las imágenes ya construidas, escaneadas y **firmadas** en GitHub Container Registry. Se probaron desde un clon limpio el 24/11/2026.

### Requisitos

| | Windows 10/11 | macOS | Linux |
| --- | --- | --- | --- |
| Git | [git-scm.com](https://git-scm.com/downloads) | `xcode-select --install` | `sudo apt install git` |
| Docker | [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Docker Desktop, o `brew install colima docker docker-compose` y `colima start --memory 4` | Docker Engine con el plugin Compose |
| Memoria libre | 4 GB (nivel 1) · 8 GB (nivel 2) | igual | igual |
| Puertos libres | 8088 (app) y 3000 (API) | igual | igual |

### Nivel 1: la aplicación completa en 5 minutos

```bash
git clone https://github.com/juanjosegl/RedNexus-Platform.git
cd RedNexus-Platform
docker compose -f compose.yaml -f compose.ghcr.yaml up -d
```

La primera vez descarga unos 1,2 GB de imágenes. Cuando `docker compose ps` muestre `api`, `worker` y `web` en *running*, abre **http://localhost:8088**.

| Qué | Dónde |
| --- | --- |
| Aplicación | http://localhost:8088 |
| API y su documentación (Swagger) | http://localhost:3000/api/docs |
| Salud de la API, la base y Redis | http://localhost:8088/api/health/ready |
| Usuarios de prueba (datos sintéticos) | `ana.demo@rednexus.dev`, `laura.demo@rednexus.dev`, `daniela.demo@rednexus.dev`… · contraseña `demo12345` |

### Nivel 2: con la IA real (Ollama)

1. Instala [Ollama](https://ollama.com/download) (Windows, macOS o Linux) y descarga los modelos (unos 2,5 GB):

   ```bash
   ollama pull qwen2.5:3b
   ollama pull paraphrase-multilingual
   ```

2. En la carpeta `RedNexus-Platform`, activa la IA y vuelve a levantar:

   ```bash
   cp ia.env.example .env          # en Windows (cmd o PowerShell): copy ia.env.example .env
   docker compose -f compose.yaml -f compose.ghcr.yaml up -d
   ```

3. Comprueba que tomó la IA: `docker compose logs worker | grep -i proveedor` debe decir `Proveedor de IA: ollama` (en PowerShell: `docker compose logs worker | Select-String proveedor`).

Las notas de voz reales (whisper.cpp) y el asistente de `/ayuda` con Open WebUI son opcionales y se activan en el mismo `.env` (ver [ia.env.example](ia.env.example), [docs/demo-local.md](docs/demo-local.md) y [asistente-rag/README.md](asistente-rag/README.md)). Sin ellos, la voz y el asistente usan respuestas de respaldo y la app sigue funcionando. En el Mac del líder todo se enciende con `bash scripts/demo-local.sh`.

### Recorrido de la demo (10 minutos)

| # | Paso | Qué se espera |
| --- | --- | --- |
| 1 | Abrir http://localhost:8088 → **Crear cuenta** sin marcar la autorización de datos; luego marcándola | Primero un error (Ley 1581); luego entra a la aplicación |
| 2 | Entrar como `laura.demo@rednexus.dev` → **Solicitudes → Nueva solicitud** → *"No entiendo cómo unir tres tablas con una tabla intermedia en SQL"* | Pasa de *Pendiente* a *Con candidatos* en menos de 30 s, con 3 compañeros, su puntaje y una frase que explica por qué |
| 3 | En una ventana privada, entrar como el primer candidato (por ejemplo `ana.demo@rednexus.dev`) → **Ayudar** → **Aceptar** | Se muestra el correo de Laura; si otro candidato acepta después, ve "Otro compañero aceptó primero" |
| 4 | Volver a Laura → abrir la solicitud → **Calificar** con 5 estrellas | La calificación queda guardada y mejora el ranking de Ana |
| 5 | **Nueva solicitud → Grabar** (necesita micrófono) y **Publicar** | La duda aparece transcrita y con candidatos |
| 6 | **Ayuda** → *"¿Qué pasa si nadie acepta mi solicitud?"* | Respuesta con pasos y fuentes (respaldo por palabras clave en el nivel 1) |
| 7 | **Ayuda → Radicar una PQRS** | Queda con número `PQRS-000N` y estado *Radicada* |
| 8 | Con la cuenta creada en el paso 1: **Perfil → Descargar mis datos** y **Eliminar mi cuenta** | Baja un JSON con todo lo del titular; después no se puede volver a entrar |
| 9 | Degradación (nivel 2): cerrar Ollama y publicar otra duda | Igual llegan candidatos; el log del worker dice `por tags` |

### Apagar, reiniciar desde cero y problemas comunes

```bash
docker compose -f compose.yaml -f compose.ghcr.yaml down       # apaga; los datos se conservan
docker compose -f compose.yaml -f compose.ghcr.yaml down -v    # apaga y borra la base (vuelve a los datos de prueba)
```

| Síntoma | Solución |
| --- | --- |
| `port is already allocated` (8088 o 3000) | Cierra lo que usa ese puerto o apaga otro stack de Docker |
| La página carga pero no deja entrar | Espera a que `migrate` termine (`docker compose ps -a` lo muestra *Exited (0)*) y recarga |
| La solicitud se queda en *Pendiente* | `docker compose logs worker`; si dice que no llega a Ollama, revisa que Ollama esté abierto o borra el `.env` para volver al nivel 1 |
| `no space left on device` | `docker system df` y libera imágenes que no uses (`docker image prune`) |

Más fallas y cómo resolverlas: [runbook](docs/entrega/09-runbook.md). Kubernetes (k3d o minikube) y la demo GitOps con Argo CD están más abajo.

## Equipo

| Integrante | GitHub | Aportes principales |
| --- | --- | --- |
| Juan José Gutiérrez Lasso (líder) | [@juanjosegl](https://github.com/juanjosegl) | Arquitectura, backend, IA y MLOps, plataforma (Kubernetes, GitOps, DevSecOps, IaC, observabilidad), asistente RAG y documentación |
| Victor Daniel Fernández | [@daniel200231](https://github.com/daniel200231) | Frontend del chat de ayuda (FE-11), documentación y revisión de requisitos |
| José Sebastián Fernández | [@josesfa](https://github.com/josesfa) | Frontend de la ayuda (FE-09, FE-10), pruebas y evidencias de CI |
| María Paula Andrade Muñoz | [@MariPau-dev](https://github.com/MariPau-dev) | Frontend de preguntas frecuentes (FE-12), documento base y diapositivas |
| María Alejandra Guzmán Ruiz | [@alejandraguzman12](https://github.com/alejandraguzman12) | Base de conocimiento y golden dataset del RAG, pruebas manuales y simulacros |

## Empieza aquí

| Documento | Para qué |
| --- | --- |
| **[Guía del equipo](docs/guia-del-equipo.md)** | Instalar todo (Windows), clonar, levantar el sistema y cómo trabajamos con Git |
| [Tareas](docs/tareas.md) | Qué hay que hacer, con ramas y commits por tarea |
| [CONTRIBUTING](CONTRIBUTING.md) | Resumen de las reglas de ramas, commits y PR |
| [Entorno en Mac](docs/entorno-mac.md) | Instalación en macOS (Apple Silicon) |
| [Demo sin Dokploy](docs/demo-local.md) | Cómo mostrar el sistema funcionando: demo local con IA real, URL pública temporal, GitOps en Actions y Render |
| [GitOps](docs/gitops.md) | Demo con Argo CD, Sealed Secrets e imágenes firmadas (Kyverno): desplegar, *drift*, rollback y secretos |
| [OpenTofu](iac/README.md) | Clúster de la demo y reglas de ramas de GitHub como código |
| [Observabilidad](observabilidad/README.md) | OpenTelemetry, Grafana y el SLO de 30 s |
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
| **Hacer la demo con la IA real** (Ollama, voz y asistente) | RedNexus-Platform | `bash scripts/demo-local.sh` (`--tunel` para una URL pública temporal; ver [Demo sin Dokploy](docs/demo-local.md)) | App en http://localhost:8088 con las imágenes firmadas de GHCR |
| **Programar el frontend** | RedNexus-Platform, y luego RedNexus-Frontend | `docker compose up -d --build api worker`, y luego `npm run dev` en el frontend | Backend listo en Docker, con datos de prueba; tu frontend en http://localhost:5173 con recarga automática |
| **Programar el backend** | RedNexus-Backend | `docker compose up -d` (Postgres y Redis) y `npm run start:dev` (ver su README para la primera vez) | Tu API en http://localhost:3000 con recarga automática |
| **Probar en Kubernetes** | RedNexus-Platform | `bash scripts/k8s-up.sh` (k3d) o `bash scripts/k8s-up.sh minikube` | App en http://localhost:8080 |
| **Demo GitOps** (Argo CD, Kyverno, Sealed Secrets) | RedNexus-Platform | `bash scripts/gitops-up.sh` (ver [GitOps](docs/gitops.md)) | App en http://localhost:8090, desplegada por Argo CD con las imágenes firmadas de GHCR |
| **Ver trazas, métricas y el SLO** | RedNexus-Platform | `docker compose -f observabilidad/compose.yaml up -d` | Grafana en http://localhost:3002 |
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
compose.yaml                  # sistema completo o solo backend con Docker Compose
catalog-info.yaml, mkdocs.yml # catálogo de servicios y TechDocs (PL-08)
.github/workflows/
├── ci.yml                    # kubeconform (con CRD), OpenTofu, compose, scripts, RAG y ML en cada PR
├── gitops-e2e.yml            # demo GitOps completa en kind: Argo CD, Kyverno, app y SLO (PL-03 a PL-07)
└── promover.yml              # PR que despliega las últimas imágenes firmadas en la demo
k3d/cluster.yaml, demo.yaml   # clústeres locales como código: desarrollo (:8080) y demo GitOps (:8090)
deploy/
├── base/                     # manifiestos comunes: postgres, redis, api, worker, web, ingress
├── components/dev/           # común a clústeres locales: imágenes :dev y secretos de prueba
├── overlays/
│   ├── k3d/                  # Ingress Traefik, Ollama en host.k3d.internal
│   ├── minikube/             # Ingress NGINX, Ollama en host.minikube.internal
│   └── demo/                 # imágenes de GHCR por commit, Sealed Secrets y seed (Argo CD)
├── policies/                 # Kyverno: solo imágenes firmadas y registros permitidos
├── sealed-secrets/           # certificado público para cifrar secretos
└── observabilidad/           # Grafana + Tempo + Prometheus y el tablero del SLO
iac/                          # OpenTofu: clúster de la demo y reglas de ramas de GitHub
observabilidad/               # stack de observabilidad local con Docker
scripts/
├── k8s-up.sh                 # construir + cargar imágenes + desplegar (k3d o minikube)
├── gitops-up.sh              # demo GitOps desde cero, cronometrada
├── demo-local.sh             # demo en el Mac con la IA real y URL pública opcional
└── seal-secrets.sh           # cifrar los secretos de la demo con kubeseal
docs/                         # guías del equipo, arquitectura, GitOps y la entrega por capítulos
ml/                           # experimentos de emparejamiento con MLflow
asistente-rag/                # asistente de soporte: base de conocimiento, modelo, golden dataset y evaluación
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
- **Secretos:** los de `components/dev` son valores de prueba, solo para desarrollo. La demo GitOps los lleva cifrados con Sealed Secrets (`deploy/overlays/demo/sealed-secrets.yaml`).

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

- **Jose Sebastian Fernandez** ([@josesfa](https://github.com/josesfa)): enlace "Ayuda" en el menú (FE-09) y preguntas sugeridas en la página de ayuda (FE-10), con sus pruebas.

- **Maria Paula Andrade** ([@MariPau-dev](https://github.com/MariPau-dev)): preguntas frecuentes en la página de ayuda y acceso a la ayuda desde el inicio (FE-12), con sus pruebas.

- **Maria Alejandra Guzman** ([@alejandraguzman12](https://github.com/alejandraguzman12)): documentos de la base de
  conocimiento "Registro y perfil" y "Solicitudes de ayuda", 16 casos del golden dataset (8 de registro_perfil y 8 de
  solicitudes), portada e índice del informe.

## Flujo de trabajo

Una rama temporal por tarea, creada desde `developer` → PR a `developer` (y la rama se borra) → el líder promueve `developer` → `test` → `main`. Paso a paso en [CONTRIBUTING.md](CONTRIBUTING.md).
