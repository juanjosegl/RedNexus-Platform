# Tareas de RedNexus

Todo lo que falta para el MVP y para las evidencias del diplomado, dividido en tareas que cada uno puede elegir.

## Cómo usar este documento

1. **Elige una tarea** cuyas dependencias ya estén listas (columna *Depende de*). Asígnate su issue en GitHub o avisa en el grupo.
2. **Crea la rama** con el nombre indicado, desde `developer` (ver la [guía del equipo](guia-del-equipo.md#5-cómo-trabajamos-con-git)).
3. **Haz un commit por cada paso** de la lista *Commits*. Son una guía: si necesitas uno más o uno menos, está bien, pero mantén el formato.
4. **Abre el PR** hacia `developer` cuando cumplas todo lo de *Listo cuando*. El título del PR es el de la tarea.

**Tamaño:** S = 1 día · M = 2 a 3 días · L = 4 a 5 días.

### Calendario

| Semana | Fechas | Meta |
| --- | --- | --- |
| 1 | 8 – 11 oct | Todos con el entorno funcionando. Tareas de la semana 1 iniciadas |
| 2 | 13 – 18 oct | Registro, login, perfiles y solicitudes de punta a punta. Imágenes en GHCR |
| 3 | 20 – 25 oct | Emparejamiento con IA funcionando. Argo CD desplegando desde Git. Trivy, SBOM y firma |
| 4 | 27 oct – 1 nov | Notas de voz, aceptar/rechazar, calificaciones. Observabilidad y SLO |
| 5 | 3 – 8 nov | Experimentos MLflow, evaluación RAG, seguridad (Kyverno, Sealed Secrets), OpenTofu |
| 6 | 10 – 15 nov | Reconstrucción desde cero, runbook, simulacros, documentos finales |
| 7 | 17 – 20 nov | Ensayo de la demo y sustentación |

### Paquetes sugeridos (uno por persona)

| Paquete | Tareas | Perfil |
| --- | --- | --- |
| **Backend** | BE-01 a BE-06 | Le gusta NestJS y las bases de datos |
| **Frontend** | FE-01 a FE-07 | Le gusta Vue y el diseño de interfaces |
| **IA** (líder) | IA-01 a IA-05 | Modelos locales, embeddings, colas |
| **Plataforma y DevSecOps** | PL-01 a PL-05, PL-08 | Docker, Kubernetes, CI/CD y seguridad |
| **SRE, MLOps y documentación** | PL-06, PL-07, PL-09, IA-06, IA-07, DOC-01 a DOC-04 | Observabilidad, datos, métricas y documentos |

Los paquetes son una sugerencia: quien termine antes toma tareas de otro paquete.

---

## Contratos acordados

Para que frontend y backend avancen en paralelo, **primero se escribe el contrato y luego la lógica**. Cada tarea de backend empieza con un commit que crea los DTO y el controlador documentados en Swagger, aunque todavía respondan datos de prueba. Así el frontend ya puede programar contra http://localhost:3000/api/docs.

### Endpoints (todos bajo `/api`)

Todos requieren el encabezado `Authorization: Bearer <token>`, salvo registro, login y health.

| Método y ruta | Cuerpo | Respuesta | Tarea |
| --- | --- | --- | --- |
| `POST /auth/register` | `{ email, password, name }` | `201 { accessToken, user }` | BE-01 |
| `POST /auth/login` | `{ email, password }` | `200 { accessToken, user }` | BE-01 |
| `GET /auth/me` | – | `200 user` | BE-01 |
| `GET /users/me` | – | `200 { id, email, name, bio, tags, rating }` | BE-02 |
| `PATCH /users/me` | `{ name?, bio?, tags? }` | `200` perfil actualizado | BE-02 |
| `GET /users/:id` | – | `200 { id, name, bio, tags, rating }` (sin email) | BE-02 |
| `POST /help-requests` | `{ text }` | `201 { id, status: "PENDING" }` | BE-03 |
| `POST /help-requests/voice` | `multipart: audio` | `201 { id, status: "PENDING" }` | BE-04 |
| `GET /help-requests/mine` | – | `200 [ { id, text, area, topics, level, status, createdAt } ]` | BE-03 |
| `GET /help-requests/:id` | – | `200` solicitud + `matches[]` con ayudante, `score`, `explanation`, `status` y el email del ayudante si aceptó | BE-03 |
| `POST /help-requests/:id/close` | – | `200` | BE-03 |
| `GET /matches/incoming` | – | `200` solicitudes donde soy candidato | BE-05 |
| `POST /matches/:id/accept` | – | `200 { authorEmail }` | BE-05 |
| `POST /matches/:id/reject` | – | `200` | BE-05 |
| `POST /ratings` | `{ requestId, stars }` (1 a 5) | `201` | BE-06 |

### Estados

- Solicitud: `PENDING` (en cola de IA) → `MATCHED` (tiene candidatos) → `ACCEPTED` (un ayudante aceptó) → `CLOSED`
- Candidato (*match*): `PROPOSED` → `ACCEPTED` o `REJECTED`

### Rutas del frontend

`/login`, `/registro`, `/perfil`, `/solicitudes` (mis solicitudes), `/solicitudes/nueva`, `/solicitudes/:id`, `/ayudar` (solicitudes donde soy candidato).

---

## Backend (repo RedNexus-Backend)

### BE-01 · Registro y login con JWT

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/BE-01-auth` | M | 1–2 | – |

**Objetivo:** que un estudiante se registre e inicie sesión, y que las demás rutas puedan exigir sesión.

**Commits:**
1. `chore(auth): agregar @nestjs/jwt y bcryptjs`
2. `feat(auth): dto de registro y login con validación y swagger`
3. `feat(auth): registro con contraseña cifrada y email único`
4. `feat(auth): login que devuelve token jwt`
5. `feat(auth): guard jwt y decorador @CurrentUser`
6. `feat(auth): endpoint /auth/me`
7. `feat(seed): usuarios de prueba con contraseña demo12345`
8. `test(auth): pruebas del servicio de autenticación`

**Listo cuando:** puedo registrarme y hacer login desde Swagger; con el token, `/auth/me` responde mi usuario; sin token responde 401; la contraseña nunca aparece en ninguna respuesta; el `JWT_SECRET` sale de las variables de entorno.

### BE-02 · Perfil con habilidades

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/BE-02-perfil` | M | 2 | BE-01 |

**Objetivo:** que cada usuario describa lo que sabe (texto libre y etiquetas), que es lo que usa la IA para emparejar.

**Commits:**
1. `feat(users): dto y controlador de perfil documentados en swagger`
2. `feat(users): ver y editar mi perfil`
3. `feat(users): perfil público sin datos de contacto`
4. `feat(users): promedio de calificaciones en el perfil`
5. `feat(users): encolar el cálculo del embedding al cambiar bio o etiquetas`
6. `test(users): pruebas del servicio de perfil`

**Listo cuando:** `GET/PATCH /users/me` y `GET /users/:id` funcionan; el perfil público no muestra el email; al editar bio o etiquetas se encola un trabajo `embed-profile` (visible en el log del worker).

### BE-03 · Solicitudes de ayuda por texto

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/BE-03-solicitudes` | M | 2 | BE-01 |

**Objetivo:** que un estudiante publique su duda y siga su estado.

**Commits:**
1. `feat(help-requests): dto y controlador documentados en swagger`
2. `feat(help-requests): crear solicitud y encolar el emparejamiento`
3. `feat(help-requests): listar mis solicitudes`
4. `feat(help-requests): detalle con candidatos y contacto si aceptaron`
5. `feat(help-requests): cerrar solicitud`
6. `test(help-requests): pruebas del servicio`

**Listo cuando:** al crear una solicitud queda en `PENDING` y aparece un trabajo `match` en la cola; solo el autor ve el detalle de su solicitud; el texto tiene un mínimo de 10 y un máximo de 1000 caracteres.

### BE-04 · Solicitud por nota de voz

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/BE-04-nota-de-voz` | S | 4 | BE-03 |

**Objetivo:** recibir el audio y dejarlo listo para que el worker lo transcriba (IA-05).

**Commits:**
1. `feat(help-requests): endpoint multipart para subir audio`
2. `feat(help-requests): guardar el audio y encolar la transcripción`
3. `test(help-requests): rechazar archivos que no son audio o pesan más de 10 MB`

**Listo cuando:** acepta webm, ogg, mp3 o wav de hasta 10 MB; la solicitud se crea con `audioPath` y estado `PENDING`; se encola un trabajo `transcribe`. Coordina con PL-01 dónde se guarda el audio en Kubernetes (volumen compartido entre la API y el worker).

### BE-05 · Aceptar o rechazar como ayudante

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/BE-05-aceptar-rechazar` | M | 3–4 | BE-03 |

**Objetivo:** que el candidato vea las solicitudes donde lo propusieron y responda.

**Commits:**
1. `feat(matching): dto y controlador de candidatos en swagger`
2. `feat(matching): listar solicitudes donde soy candidato`
3. `feat(matching): aceptar candidatura y compartir contacto`
4. `feat(matching): rechazar candidatura`
5. `test(matching): solo el candidato responde y solo una vez`

**Listo cuando:** al aceptar, el match pasa a `ACCEPTED`, la solicitud a `ACCEPTED` y la respuesta trae el email del autor; si la solicitud ya fue aceptada por otro, responde 409; nadie puede aceptar matches ajenos.

### BE-06 · Calificaciones

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/BE-06-calificaciones` | S | 4 | BE-05 |

**Objetivo:** que el autor califique la ayuda recibida, lo cual mejora el ranking futuro.

**Commits:**
1. `feat(ratings): una calificación por solicitud (migración con índice único)`
2. `feat(ratings): calificar de 1 a 5 estrellas`
3. `test(ratings): solo el autor califica y solo solicitudes aceptadas`

**Listo cuando:** solo el autor puede calificar, solo si la solicitud está `ACCEPTED` y una sola vez; el promedio aparece en el perfil (BE-02).

---

## IA (repo RedNexus-Backend, módulos `ai` y `matching`)

### IA-01 · Proveedor de IA con modo de prueba

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/IA-01-proveedor-ia` | M | 1–2 | – |

**Objetivo:** una sola interfaz para la IA con dos implementaciones: Ollama (real) y *mock* (respuestas fijas). Así nadie depende del nodo de IA para programar, y el CI tampoco.

**Commits:**
1. `feat(ai): interfaz AiProvider (embed, classify, explain, transcribe)`
2. `feat(ai): proveedor mock determinístico`
3. `feat(ai): proveedor ollama`
4. `feat(ai): elegir proveedor con AI_PROVIDER (mock por defecto)`
5. `chore(ai): nuevo trabajo embed-profile en la cola`
6. `test(ai): pruebas del proveedor mock`

**Listo cuando:** con `AI_PROVIDER=mock` todo funciona sin Ollama; con `AI_PROVIDER=ollama` y `OLLAMA_URL` apuntando al nodo de IA, se obtienen embeddings de 768 dimensiones.

### IA-02 · Embeddings de perfiles y solicitudes

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/IA-02-embeddings` | S | 2–3 | IA-01 |

**Commits:**
1. `feat(ai): procesar embed-profile y guardar el vector del perfil`
2. `feat(ai): calcular el embedding de cada solicitud`
3. `feat(matching): índice hnsw de pgvector para búsquedas por similitud`

**Listo cuando:** perfiles y solicitudes tienen su columna `embedding` llena después de pasar por el worker.

### IA-03 · Clasificación de la solicitud con el LLM

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/IA-03-clasificacion` | S | 3 | IA-01 |

**Commits:**
1. `feat(ai): prompt de clasificación con salida json (área, temas, nivel)`
2. `feat(ai): validar la salida del modelo y reintentar si no es válida`
3. `test(ai): casos de clasificación con el proveedor mock`

**Listo cuando:** cada solicitud queda con `area`, `topics` y `level`; si el modelo responde algo inválido, se reintenta una vez y luego se sigue sin clasificación.

### IA-04 · Emparejamiento top 3 con explicación (RAG)

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/IA-04-emparejamiento` | L | 3 | IA-02, IA-03, BE-03 |

**Objetivo:** el corazón del producto. Buscar los perfiles más cercanos a la solicitud, ordenarlos por similitud y calificaciones, y explicar con el LLM por qué encaja cada uno, usando solo los datos recuperados del perfil (RAG).

**Commits:**
1. `feat(matching): buscar los 10 perfiles más cercanos con pgvector`
2. `feat(matching): puntaje combinado de similitud y calificaciones`
3. `feat(matching): explicación del llm basada solo en el perfil recuperado`
4. `feat(matching): crear los 3 matches y pasar la solicitud a MATCHED`
5. `feat(matching): respaldo por etiquetas si la ia no responde`
6. `test(matching): ranking y respaldo con el proveedor mock`

**Listo cuando:** una solicitud nueva obtiene 3 candidatos (nunca el propio autor) en menos de 30 segundos; con el nodo de IA apagado, el respaldo por etiquetas igual entrega candidatos.

### IA-05 · Transcripción de notas de voz (multimodal)

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/IA-05-transcripcion` | M | 4 | IA-01, BE-04 |

**Commits:**
1. `docs(ai): instalar whisper.cpp y ffmpeg en el nodo de ia`
2. `feat(ai): transcribir con el servidor de whisper.cpp`
3. `feat(ai): tras transcribir, guardar el texto y encolar el emparejamiento`
4. `test(ai): transcripción con el proveedor mock`

**Listo cuando:** una nota de voz en español termina como solicitud con texto y candidatos.

### IA-06 · Dataset sintético

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/IA-06-dataset-sintetico` | M | 3 | – |

**Repo:** RedNexus-Platform (`ml/data`) y RedNexus-Backend (seed).

**Commits:**
1. `feat(ml): 50 perfiles ficticios de estudiantes`
2. `feat(ml): 100 solicitudes con el ayudante correcto marcado`
3. `feat(seed): cargar el dataset sintético en la base de datos`

**Listo cuando:** `npm run db:seed` carga los 50 perfiles; ningún dato corresponde a una persona real.

### IA-07 · Experimentos MLflow y evaluación RAG

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/IA-07-experimentos-mlflow` | L | 5 | IA-04, IA-06 |

**Repo:** RedNexus-Platform (`ml/`).

**Commits:**
1. `chore(ml): proyecto python con uv y mlflow en docker compose`
2. `feat(ml): métrica precision@3 sobre el dataset`
3. `feat(ml): comparar nomic-embed-text con all-minilm`
4. `feat(ml): comparar con y sin clasificación previa y distintos pesos`
5. `feat(ml): medir afirmaciones no soportadas en las explicaciones`
6. `docs(ml): resultados y configuración ganadora`

**Listo cuando:** MLflow muestra al menos 4 experimentos comparables y la configuración ganadora queda registrada y aplicada en el backend.

---

## Frontend (repo RedNexus-Frontend)

Mientras un endpoint no exista, programa contra datos simulados dentro del `api.ts` de tu feature, siguiendo el contrato, y cámbialo por la llamada real cuando el endpoint aparezca en Swagger.

### FE-01 · Componentes base y layout

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/FE-01-componentes-base` | M | 1 | – |

**Commits:**
1. `feat(ui): botón, campo de texto y tarjeta`
2. `feat(ui): alerta de error y estado de carga`
3. `feat(web): barra de navegación con estado de sesión`
4. `test(ui): pruebas de los componentes base`

**Listo cuando:** los componentes están en `src/components/ui`, se ven bien en celular y escritorio, y el resto de features los usa.

### FE-02 · Login y registro

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/FE-02-login-registro` | M | 2 | FE-01, BE-01 (contrato) |

**Commits:**
1. `feat(auth): vistas de login y registro`
2. `feat(auth): guardar el token en la sesión y en localStorage`
3. `feat(web): enviar el token en cada llamada a la api`
4. `feat(web): proteger rutas y redirigir a /login`
5. `feat(web): cerrar sesión`
6. `test(auth): pruebas de la vista de login`

**Listo cuando:** me registro, inicio sesión, recargo la página y sigo con la sesión; sin sesión, cualquier ruta protegida me lleva a `/login`; los errores del backend se muestran en pantalla.

### FE-03 · Perfil

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/FE-03-perfil` | S | 2–3 | FE-02, BE-02 (contrato) |

**Commits:**
1. `feat(profile): ver mi perfil con calificación`
2. `feat(profile): editar bio y etiquetas`
3. `test(profile): pruebas del formulario`

### FE-04 · Crear y seguir solicitudes

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/FE-04-solicitudes` | M | 2–3 | FE-02, BE-03 (contrato) |

**Commits:**
1. `feat(help-requests): formulario de nueva solicitud`
2. `feat(help-requests): lista de mis solicitudes con su estado`
3. `feat(help-requests): detalle con candidatos y su explicación`
4. `feat(help-requests): actualizar el estado cada 5 segundos mientras está PENDING`
5. `test(help-requests): pruebas del formulario y la lista`

**Listo cuando:** creo una solicitud, la veo en `PENDING` y luego, sin recargar, aparecen sus candidatos con la explicación.

### FE-05 · Nota de voz

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/FE-05-nota-de-voz` | M | 4 | FE-04, BE-04 (contrato) |

**Commits:**
1. `feat(help-requests): grabar audio con el micrófono (MediaRecorder)`
2. `feat(help-requests): escuchar, regrabar y enviar la nota de voz`
3. `feat(help-requests): mensajes si no hay permiso de micrófono`

**Listo cuando:** grabo hasta 60 segundos, la escucho antes de enviar, y la solicitud aparece en mi lista.

### FE-06 · Bandeja del ayudante

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/FE-06-ayudar` | M | 3–4 | FE-02, BE-05 (contrato) |

**Commits:**
1. `feat(matches): lista de solicitudes donde soy candidato`
2. `feat(matches): aceptar o rechazar con confirmación`
3. `feat(matches): mostrar el contacto del autor al aceptar`
4. `test(matches): pruebas de aceptar y rechazar`

### FE-07 · Calificar la ayuda

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/FE-07-calificar` | S | 4 | FE-04, BE-06 (contrato) |

**Commits:**
1. `feat(ratings): componente de 1 a 5 estrellas`
2. `feat(ratings): calificar desde el detalle de una solicitud aceptada`

---

## Plataforma y DevSecOps (repo RedNexus-Platform, salvo que se indique)

### PL-01 · Publicar imágenes en GHCR

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `chore/PL-01-imagenes-ghcr` | M | 2 | – |

**Repos:** RedNexus-Backend y RedNexus-Frontend (`.github/workflows`).

**Commits:**
1. `ci: construir imagen multi-arquitectura (amd64 y arm64) con buildx`
2. `ci: publicar en ghcr con etiquetas sha y rama al fusionar en developer y main`
3. `chore(k8s): volumen compartido para audios entre api y worker` (en Platform)

**Listo cuando:** cada fusión a `developer` publica `ghcr.io/juanjosegl/rednexus-backend` y `rednexus-frontend` con la etiqueta del commit; los PR solo construyen, sin publicar.

### PL-02 · Escaneo, SBOM y firma

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `chore/PL-02-devsecops` | M | 3 | PL-01 |

**Commits:**
1. `ci: escanear la imagen con trivy y fallar con vulnerabilidades críticas`
2. `ci: generar sbom con syft y adjuntarlo`
3. `ci: firmar imagen y sbom con cosign keyless`
4. `docs(security): bitácora de hallazgos y su tratamiento`

**Listo cuando:** el pipeline muestra el reporte de Trivy, el SBOM queda como artefacto, y `cosign verify` valida la imagen publicada.

### PL-03 · GitOps con Argo CD

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/PL-03-argocd` | L | 3 | PL-01 |

**Commits:**
1. `feat(k8s): overlay demo con imágenes de ghcr`
2. `feat(argocd): instalar argo cd con helm y valores livianos`
3. `feat(argocd): aplicación rednexus apuntando a deploy/overlays/demo`
4. `ci: actualizar la etiqueta de imagen del overlay demo al publicar`
5. `docs(argocd): cómo sincronizar, ver drift y hacer rollback`

**Listo cuando:** un cambio fusionado en Git aparece desplegado sin ejecutar `kubectl` a mano, y Argo CD muestra la app *Synced* y *Healthy*.

### PL-04 · Secretos con Sealed Secrets

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/PL-04-sealed-secrets` | S | 5 | PL-03 |

**Commits:**
1. `feat(k8s): instalar sealed-secrets`
2. `feat(k8s): secretos cifrados del overlay demo`
3. `docs(k8s): cómo crear y rotar un secreto`

### PL-05 · Solo imágenes firmadas (Kyverno)

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/PL-05-kyverno` | M | 5 | PL-02, PL-03 |

**Commits:**
1. `feat(k8s): instalar kyverno con recursos mínimos`
2. `feat(k8s): política que exige firma de cosign en imágenes de rednexus`
3. `docs(security): evidencia de que una imagen sin firmar es rechazada`

### PL-06 · Infraestructura como código (OpenTofu)

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/PL-06-opentofu` | M | 5 | PL-03 |

**Commits:**
1. `feat(iac): proveedores de kubernetes, helm y github`
2. `feat(iac): namespaces y release de argo cd`
3. `feat(iac): reglas de ramas y configuración de los repos como código`
4. `docs(iac): plan, apply y manejo del estado`

### PL-07 · Observabilidad y SLO

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `feature/PL-07-observabilidad` | L | 4 | IA-04 |

**Repos:** RedNexus-Backend (instrumentación) y RedNexus-Platform (collector y dashboards).

**Commits:**
1. `feat(otel): trazas y métricas de la api y el worker con opentelemetry`
2. `feat(otel): traza del trabajo de emparejamiento de punta a punta`
3. `feat(k8s): collector y envío a grafana`
4. `feat(grafana): dashboard de solicitudes, latencia y errores`
5. `feat(grafana): slo 95% de solicitudes con candidatos en menos de 30 s`

### PL-08 · Catálogo de servicios

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `docs/PL-08-catalogo` | S | 5 | – |

**Commits:**
1. `docs(catalog): catalog-info.yaml en los tres repos`
2. `docs(catalog): techdocs con mkdocs`

### PL-09 · Runbook y recuperación

| Rama | Tamaño | Semana | Depende de |
| --- | --- | --- | --- |
| `docs/PL-09-runbook` | M | 6 | PL-03, PL-07 |

**Commits:**
1. `feat(k8s): respaldo y restauración de postgres`
2. `docs(runbook): fallas comunes y cómo resolverlas`
3. `docs(runbook): simulacro de caída del nodo de ia y de una réplica`
4. `docs(runbook): reconstrucción desde cero cronometrada`

---

## Documentación (repo RedNexus-Platform, carpeta `docs/`)

| ID | Rama | Tamaño | Semana | Qué entrega |
| --- | --- | --- | --- | --- |
| DOC-01 | `docs/DOC-01-arquitectura` | M | 2 | Contexto, usuarios, requisitos, diagrama de arquitectura y ADRs (k3d/minikube, imagen única, IA local, Grafana) |
| DOC-02 | `docs/DOC-02-privacidad` | M | 5 | Análisis de la Ley 1581, ficha de cada modelo (licencia, tamaño, hash), riesgos de IA y límites del sistema |
| DOC-03 | `docs/DOC-03-informe` | M | 6 | Informe ejecutivo con capítulo de sostenibilidad e impacto (criterios ESG, pendiente de confirmar con el coordinador) |
| DOC-04 | `docs/DOC-04-demo` | S | 7 | Guion de la demo, presentación y ensayo cronometrado |
