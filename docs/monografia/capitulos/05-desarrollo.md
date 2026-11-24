# Capítulo 5. Desarrollo del proyecto

Este capítulo reporta la implementación de lo diseñado en los capítulos 3 y 4, organizada por módulo, con evidencias de las interfaces, de los *pipelines* y de los despliegues. Las capturas de la aplicación se tomaron el 24 de noviembre de 2026 sobre la demo local con las imágenes publicadas en `main` y la IA real (Ollama, whisper.cpp y Open WebUI), con usuarios sintéticos.

## 5.1 Organización del trabajo y del código

El código vive en tres repositorios públicos de GitHub. RedNexus-Backend contiene la API y el *worker*; RedNexus-Frontend, la aplicación web; y RedNexus-Platform, todo lo necesario para construir, desplegar y operar (Docker Compose, Kubernetes, GitOps, OpenTofu, políticas, observabilidad, experimentos de ML, el asistente RAG y la documentación). Los tres deben clonarse en la misma carpeta, porque los *scripts* de Kubernetes construyen las imágenes desde los repositorios hermanos.

El trabajo se repartió en *issues* con identificador por área (`BE-`, `FE-`, `IA-`, `PL-`, `DOC-`) en un tablero Kanban público con las columnas *Por hacer*, *En curso*, *En revisión* y *Hecho*. Cada *issue* se resolvió en una rama temporal y un *pull request* con la integración continua obligatoria; los aportes de los compañeros quedaron como coautores en los *commits*.

Tabla: Actividad en los repositorios al 24/11/2026
| Repositorio | *Issues* | *Pull requests* fusionados | Contenido principal |
| --- | --- | --- | --- |
| RedNexus-Backend | 28 | 52 | NestJS 12, Prisma 7, PostgreSQL 17 con pgvector, BullMQ y Redis, OpenTelemetry |
| RedNexus-Frontend | 16 | 39 | Vue 3, Vite, Pinia, Tailwind CSS y Vitest |
| RedNexus-Platform | 31 | 32 | Compose, Kustomize, Argo CD, Kyverno, Sealed Secrets, OpenTofu, MLflow, Open WebUI y documentación |
Nota: Elaboración propia con datos de GitHub. Los *pull requests* incluyen las promociones `developer → test → main`.

![Tablero del proyecto en GitHub](docs/entrega/evidencias/gh-05-tablero.png)
Nota: Captura del tablero público https://github.com/users/juanjosegl/projects/1.

## 5.2 Backend: API y *worker*

El *backend* es una aplicación NestJS en TypeScript organizada en módulos. Una misma imagen arranca como API (`node dist/main`), como *worker* (`node dist/worker`) o como migración (`prisma migrate deploy` y carga de datos sintéticos).

Tabla: Módulos del backend
| Módulo | Responsabilidad | Rutas principales |
| --- | --- | --- |
| `auth` | Registro con autorización de datos, inicio de sesión y JWT | `POST /api/auth/register`, `/login`, `GET /api/auth/me` |
| `users` | Perfil, perfil público, exportar y eliminar mis datos | `GET/PATCH /api/users/me`, `GET /me/export`, `DELETE /me`, `GET /:id` |
| `help-requests` | Solicitudes por texto y por voz, consulta y cierre | `POST /api/help-requests`, `/voice`, `GET /mine`, `/:id`, `POST /:id/close` |
| `matching` | Ranking, bandeja del colaborador y aceptación atómica | `GET /api/matches/incoming`, `POST /:id/accept`, `/:id/reject` |
| `ai` | Proveedores de IA (Ollama, transcripción con whisper.cpp y dobles de prueba) | Interno |
| `queue` | Colas `match` y `transcribe` de BullMQ con 3 reintentos y espera exponencial | Interno (*worker*) |
| `ratings` | Calificación de 1 a 5 y promedio del colaborador | `POST /api/ratings`, `GET /received` |
| `support` | Asistente de soporte (Open WebUI o respaldo) | `POST /api/support/chat` |
| `pqrs` | Peticiones, quejas, reclamos y sugerencias con radicado | `POST /api/pqrs`, `GET /mine`, `/:id` |
| `stats` | Estadísticas públicas para la página de inicio | `GET /api/stats` |
| `health` | Vida y disponibilidad (base de datos y Redis) | `GET /api/health`, `/health/ready` |
Nota: Elaboración propia. El contrato completo, con ejemplos y respuestas de error, se publica con Swagger en `/api/docs`.

**Aceptación atómica.** Cuando dos colaboradores aceptan la misma solicitud casi al mismo tiempo, solo uno debe quedar asignado. La aceptación cambia el estado de la solicitud de "con candidatos" a "aceptada" en una sola operación condicional dentro de una transacción; si la condición ya no se cumple, responde 409. En la verificación, el segundo colaborador recibió exactamente ese conflicto.

**Emparejamiento.** El *worker* clasifica la duda, construye la consulta enriquecida, calcula su *embedding*, recupera los diez perfiles más cercanos con pgvector, aplica la búsqueda híbrida y el peso de la calificación, filtra por el umbral, guarda el top 3 y genera la explicación de cada candidato. Si cualquier paso de IA falla, empareja por coincidencia de etiquetas y explica con una plantilla. Al arrancar, vuelve a encolar las solicitudes que quedaron pendientes.

## 5.3 Frontend: la aplicación web

La interfaz es una aplicación Vue 3 organizada por funcionalidades (`features/`): autenticación, solicitudes (con el grabador de voz), bandeja de ayuda, calificación, perfil y mis datos, soporte (chat, preguntas sugeridas y preguntas frecuentes) y PQRS. Llama siempre a rutas relativas bajo `/api`: en desarrollo las reenvía Vite y en Docker o Kubernetes, Nginx, de modo que la misma imagen sirve en cualquier ambiente. Es adaptable a celular y navegable con teclado.

![Registro con la autorización de tratamiento de datos](docs/entrega/evidencias/app-02-registro.png)
Nota: Captura de la aplicación. Sin marcar la autorización, el registro responde con un error (Ley 1581, art. 9).

![Formulario de nueva solicitud por texto o nota de voz](docs/entrega/evidencias/app-04-nueva-solicitud.png)
Nota: Captura de la aplicación.

![Detalle de una solicitud aceptada con su clasificación, candidatos y explicaciones](docs/entrega/evidencias/app-05-solicitud-texto.png)
Nota: Captura de la aplicación. La solicitud se clasificó como bases de datos (temas *join*, SQL y tablas; nivel intermedio) y recibió tres candidatos en 11 s. Ana aceptó, su contacto quedó visible para la autora y aparece el recuadro para calificar. La explicación del tercer candidato reconoce que su perfil (NoSQL) no encaja.

![Solicitud creada con una nota de voz](docs/entrega/evidencias/app-06-solicitud-voz.png)
Nota: Captura de la aplicación. whisper.cpp transcribió el audio y el sistema propuso tres colaboradores de redes en 13 s.

![Bandeja del colaborador con las solicitudes en las que fue propuesto](docs/entrega/evidencias/app-07-bandeja-ayudar.png)
Nota: Captura de la aplicación (vista *Ayudar*).

![Asistente de ayuda respondiendo con base en la documentación](docs/entrega/evidencias/app-12-asistente-ayuda.png)
Nota: Captura de la aplicación. La respuesta cita sus fuentes (`preguntas-frecuentes.md` y `solicitudes-de-ayuda.md`). El chat muestra el formato Markdown sin interpretar, una mejora pendiente de la interfaz.

![Perfil con las opciones de descargar y eliminar mis datos](docs/entrega/evidencias/app-10-perfil-mis-datos.png)
Nota: Captura de la aplicación.

![Detalle de una solicitud en un celular](docs/entrega/evidencias/app-11-movil-solicitud.png)
Nota: Captura con un ancho de 390 píxeles.

## 5.4 Inteligencia artificial y asistente

El código de IA del producto está en el módulo `ai` del *backend* (proveedores de Ollama y de transcripción, *prompts* versionados, validación de la salida estructurada y dobles de prueba para el modo sin modelos). Los experimentos están en `ml/` de RedNexus-Platform, con su dataset, el *script* que replica el ranking, el registro en MLflow y el *script* que exporta los perfiles al *seed* del *backend*. El asistente está en `asistente-rag/`: la base de conocimiento en Markdown, el *prompt* de sistema versionado, el *script* que configura Open WebUI por API, el *golden dataset*, el evaluador y sus corridas, y el informe del asistente en PDF. El capítulo 4 detalla sus resultados.

## 5.5 Contenedores y ambientes de ejecución

Tabla: Formas de ejecutar RedNexus
| Para qué | Comando (en RedNexus-Platform) | Resultado |
| --- | --- | --- |
| Evaluar sin compilar ni descargar modelos | `docker compose -f compose.yaml -f compose.ghcr.yaml up -d` | Aplicación en http://localhost:8088 con IA de respaldo |
| Evaluar con IA real | Lo anterior con `cp ia.env.example .env` y Ollama | Emparejamiento con `qwen2.5:3b` y `paraphrase-multilingual` |
| Demo completa en el equipo del líder | `bash scripts/demo-local.sh` (opción `--tunel` para una URL pública temporal) | IA, voz y asistente reales con las imágenes firmadas |
| Probar código sin publicar | `docker compose up -d --build` | Imágenes construidas desde los repositorios hermanos |
| Kubernetes local | `bash scripts/k8s-up.sh` o `bash scripts/k8s-up.sh minikube` | Aplicación en http://localhost:8080 |
| Demo GitOps | `bash scripts/gitops-up.sh` | Argo CD, Kyverno y Sealed Secrets; aplicación en http://localhost:8090 |
Nota: Elaboración propia. Los dos primeros niveles se probaron desde un clon limpio el 24/11/2026 y son los que sigue el video de instalación.

## 5.6 Integración y entrega continuas

Cada repositorio tiene el *workflow* de CI obligatorio y, en Backend y Frontend, el *workflow* *Imagen*. El de Platform valida manifiestos con kubeconform (incluidas las definiciones de Argo CD, Kyverno y Sealed Secrets), OpenTofu, Compose, los *scripts* con shellcheck, el *golden dataset* del asistente y la reproducibilidad del dataset de ML.

![Workflow de integración continua del backend en main](docs/entrega/evidencias/gh-03-ci-backend.png)
Nota: Captura de GitHub Actions.

![Workflow Imagen del backend: construcción multiarquitectura, Trivy, SBOM y firma](docs/entrega/evidencias/gh-01-imagen-backend.png)
Nota: Captura de GitHub Actions del *run* que publicó la imagen `sha-6a2ee94` en `main`.

![Paquete de la imagen del backend en GitHub Container Registry](docs/entrega/evidencias/gh-07-paquetes-ghcr.png)
Nota: Captura de GHCR.

## 5.7 Despliegue GitOps

El *workflow* *GitOps (kind)* reproduce en GitHub Actions el despliegue completo en un clúster efímero: crea el clúster, aplica OpenTofu (Sealed Secrets, Kyverno, Argo CD y sus aplicaciones), espera a que las tres aplicaciones queden *Synced/Healthy*, comprueba que Kyverno rechaza una imagen de un registro no permitido y una sin firma, verifica las firmas de las imágenes en ejecución, publica una solicitud real y mide su latencia, y confirma que la métrica del SLI llega a Prometheus y la traza a Tempo.

Tabla: Resultado del workflow GitOps (kind) en main
| Paso | Resultado |
| --- | --- |
| OpenTofu (instalación de la plataforma) | 52 s |
| Argo CD hasta *Synced/Healthy* | 86 s; `rednexus`, `rednexus-politicas` y `rednexus-observabilidad` sincronizadas |
| Kyverno con `nginx:alpine` | Rechazada: "Imagen no permitida en rednexus" |
| Kyverno con una etiqueta sin firma | Rechazada por `rednexus-imagenes-firmadas` |
| Firmas de las imágenes en ejecución | Válidas para backend y frontend |
| Solicitud de prueba | Emparejada en 1 s (respaldo por etiquetas, sin Ollama en Actions) |
| Observabilidad | 1 observación del SLI en Prometheus y 1 traza en Tempo |
| Duración total | 4 min 4 s |
Nota: Elaboración propia a partir del *log* del *run* del 21/11/2026 sobre `main`.

![Run del workflow GitOps (kind) en main](docs/entrega/evidencias/gh-02-gitops-kind.png)
Nota: Captura de GitHub Actions.

## 5.8 Conclusiones del capítulo

- El producto mínimo viable quedó completo de punta a punta y con un alcance mayor al de la propuesta: voz, asistente, PQRS y derechos de datos.
- La separación en módulos del *backend* y en funcionalidades del *frontend* permitió repartir el trabajo entre cinco personas con *issues* pequeños y verificables; 123 *pull requests* fusionados dejan la trazabilidad del proceso.
- La misma imagen firmada corre en Docker Compose, en Kubernetes local y en el clúster GitOps, lo que hace que lo evaluado sea exactamente lo desplegado.
- La ausencia de un servidor público se compensó con dos mecanismos verificables: una guía de instalación que cualquier evaluador reproduce en minutos y un *workflow* que despliega la plataforma completa desde cero en cada cambio de infraestructura.
