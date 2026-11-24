# 4. Decisiones de arquitectura (ADR)

Los diagramas C4 (niveles 1, 2 y 3), las vistas física, lógica, de procesos y de escenarios (4+1), el modelo entidad-relación, los casos de uso y las secuencias están en [docs/arquitectura/diagramas.md](../arquitectura/diagramas.md). Cada ADR sigue la plantilla contexto → decisión → alternativas → consecuencias.

## ADR-001 · Kubernetes local con k3d (Mac) y minikube (Windows)

- **Estado:** aceptado.
- **Contexto:** el equipo tiene equipos de 8 GB, uno con Mac M1 y cuatro con Windows. El diplomado exige Kubernetes, pero un clúster en la nube cuesta y depende de una tarjeta.
- **Decisión:** los mismos manifiestos con Kustomize (`deploy/base`) y un overlay por herramienta (`deploy/overlays/k3d` y `minikube`). `scripts/k8s-up.sh` crea el clúster, construye las imágenes y despliega.
- **Alternativas:** solo minikube (pesado en Mac), kind (sin Ingress listo), un clúster gratuito en la nube (Oracle Always Free: capacidad incierta y requiere tarjeta).
- **Consecuencias:** cada integrante reproduce el ambiente en su equipo; los overlays solo cambian el Ingress y la dirección de Ollama. Un clúster de un nodo no prueba alta disponibilidad real.

## ADR-002 · Una sola imagen para la API, el worker y las migraciones

- **Estado:** aceptado.
- **Contexto:** la API, el worker de IA y las migraciones comparten el mismo código y el cliente de Prisma.
- **Decisión:** un `Dockerfile` multi-etapa; el comando decide el rol (`node dist/main`, `node dist/worker`, `prisma migrate deploy` en un initContainer).
- **Alternativas:** tres imágenes separadas.
- **Consecuencias:** se construye, escanea y firma una sola imagen. Prisma, dotenv y tsx quedan como dependencias de producción (más peso, a cambio de simplicidad).

## ADR-003 · IA local con Ollama y whisper.cpp

- **Estado:** aceptado.
- **Contexto:** las dudas y los perfiles son datos personales (Ley 1581); las APIs comerciales cobran por uso y envían los datos fuera del país.
- **Decisión:** Ollama con `qwen2.5:3b` (clasificar y explicar) y `paraphrase-multilingual` (embeddings de 768 dimensiones; reemplazó a `nomic-embed-text` tras los experimentos de ADR-010); whisper.cpp para las notas de voz. El Mac M1 actúa como nodo de IA (Metal) fuera del clúster.
- **Alternativas:** OpenAI o Gemini (costo, privacidad), modelos de 7B o más en el clúster (no caben en 8 GB).
- **Consecuencias:** sin costo por uso y sin transferencia de datos a terceros; la calidad depende de modelos pequeños, por eso se mide (IA-07, IA-08) y se diseñó la degradación (ADR-006). `qwen2.5:3b` tiene una licencia de investigación: sirve para el proyecto académico, pero un uso comercial debe cambiar a `qwen2.5:7b` (Apache 2.0) u otro modelo (ver la ficha de modelos).

## ADR-004 · Emparejamiento asíncrono con BullMQ y Redis

- **Estado:** aceptado.
- **Contexto:** clasificar, calcular embeddings, explicar y transcribir puede tardar de 2 a 30 s.
- **Decisión:** la API guarda la solicitud y encola un trabajo (`match` o `transcribe`); un proceso worker lo consume con 3 reintentos y espera exponencial. El frontend consulta el estado cada 5 s.
- **Alternativas:** procesar dentro de la petición HTTP (tiempos de espera, sin reintentos), un bus de eventos más pesado (Kafka).
- **Consecuencias:** la API responde de inmediato y el worker escala aparte. Al reiniciar, el worker vuelve a encolar lo pendiente.

## ADR-005 · pgvector dentro de PostgreSQL

- **Estado:** aceptado.
- **Contexto:** se necesita búsqueda por similitud de vectores para unos cientos o miles de perfiles.
- **Decisión:** columna `vector(768)` en `User` y `HelpRequest` con índice HNSW de pgvector, consultada con SQL (`ORDER BY embedding <=> $1 LIMIT 10`).
- **Alternativas:** una base vectorial dedicada (Qdrant, Weaviate, Chroma).
- **Consecuencias:** un solo motor que respaldar y operar, transacciones entre datos y vectores. Cambiar a un modelo de otra dimensión (all-minilm, 384) exige una migración; por eso IA-07 compara también un modelo multilingüe de 768.

## ADR-006 · Degradación controlada de la IA

- **Estado:** aceptado.
- **Contexto:** el nodo de IA es un portátil que puede estar apagado o lento.
- **Decisión:** si falla la clasificación o el embedding, se empareja por coincidencia de palabras con bio y etiquetas; si falla la explicación, se usa una plantilla; si falla whisper, BullMQ reintenta. El asistente de soporte tiene un mock de respaldo.
- **Alternativas:** dejar la solicitud en cola hasta que vuelva la IA.
- **Consecuencias:** el usuario siempre recibe candidatos, aunque de menor calidad (en IA-07 el respaldo logra menos `precision_at_3` que los embeddings; ver [MLOps](06-mlops.md)).

## ADR-007 · Tres repositorios y flujo developer → test → main

- **Estado:** aceptado.
- **Contexto:** cinco personas trabajando en frontend, backend y plataforma a la vez.
- **Decisión:** RedNexus-Backend, RedNexus-Frontend y RedNexus-Platform. Ramas temporales con squash a `developer`, y promociones `developer → test → main` con merge commit. Rulesets con CI obligatorio y revisión por PR.
- **Alternativas:** monorepo.
- **Consecuencias:** cada repo tiene su CI y su imagen; Platform orquesta. Hay que coordinar cambios de contrato (se documentan en Swagger antes de la lógica).

## ADR-008 · JWT sin estado

- **Estado:** aceptado.
- **Decisión:** JWT firmado con `JWT_SECRET`, enviado como `Authorization: Bearer`.
- **Alternativas:** sesiones en Redis, un proveedor de identidad (Keycloak).
- **Consecuencias:** sin estado en el servidor; no se puede revocar un token antes de que expire. Al eliminar la cuenta, las rutas que buscan al usuario responden 401/404.

## ADR-009 · Entrega continua con GitOps e imágenes firmadas en GHCR; demo local cuando no hay servidor público

- **Estado:** aceptado (revisado el 24/11/2026; la versión anterior proponía Dokploy como CD principal).
- **Contexto:** el docente pidió la demo desplegada con CI/CD. El servidor compartido del diplomado (Dokploy) no quedó disponible para el equipo y no hay presupuesto para un clúster público.
- **Decisión:** cada push a `developer`, `test` o `main` construye, escanea, documenta (SBOM) y firma las imágenes en GHCR (workflow *Imagen*). El workflow *Promover imágenes* verifica las firmas y abre un PR que cambia la etiqueta del overlay `deploy/overlays/demo`; al fusionarlo, Argo CD lo despliega (ADR-012). La demo se hace en el equipo del líder con las mismas imágenes (`compose.ghcr.yaml` y `scripts/demo-local.sh`, con URL pública temporal opcional por Cloudflare), y el flujo GitOps completo se prueba de punta a punta en GitHub Actions con kind. `docker-compose.dokploy.yml` y `render.yaml` quedan listos como alternativas.
- **Alternativas:** Dokploy (no disponible), Render + Neon (se duerme a los 15 minutos y no corre Ollama), un clúster gestionado en la nube (costo y tarjeta).
- **Consecuencias:** cualquier persona reproduce exactamente lo que corre en la demo, porque las imágenes son las mismas y están firmadas. No hay una URL pública permanente: es la principal limitación de la entrega.

## ADR-010 · Configuración del emparejamiento elegida con experimentos (MLflow)

- **Estado:** aceptado.
- **Contexto:** los pesos y el umbral del ranking se habían fijado a mano con el mock (`SIMILARITY_WEIGHT = 0.8`, `MIN_SIMILARITY = 0.15`).
- **Decisión:** comparar modelos de embeddings, prefijos, clasificación previa, pesos y umbral sobre un dataset sintético etiquetado; registrar la ganadora como modelo `rednexus-matching` en MLflow y aplicarla en el backend por variables de entorno (`MATCH_SIMILARITY_WEIGHT`, `MATCH_MIN_SIMILARITY`, `OLLAMA_EMBED_PREFIXES`, `MATCH_CONFIG_VERSION`).
- **Consecuencias:** cada cambio del ranking queda medido y versionado; volver a una versión anterior es cambiar variables. Ver [MLOps](06-mlops.md).

## ADR-011 · Observabilidad con OpenTelemetry y Grafana (LGTM)

- **Estado:** aceptado (PL-07).
- **Contexto:** se necesita medir el SLO de 30 s y seguir una solicitud desde la API hasta el worker sin correr Prometheus, Loki y Tempo por separado en 8 GB.
- **Decisión:** instrumentar la API y el worker con OpenTelemetry (`src/telemetry/`) y enviar por OTLP a `grafana/otel-lgtm` (Grafana, Tempo, Prometheus y collector en un contenedor), en Docker o como app de Argo CD. La telemetría solo se activa si existe `OTEL_EXPORTER_OTLP_ENDPOINT`. Grafana Cloud (plan gratuito) queda como opción sin consumir RAM local.
- **Consecuencias:** el SLI `rednexus.match.latency`, la latencia por endpoint y la traza API → worker quedan disponibles; el tablero *RedNexus · SLO y operación* se versiona en Git. Sin el endpoint, el log del worker sigue registrando estrategia y duración.

## ADR-012 · GitOps con Argo CD, Sealed Secrets y Kyverno, instalados con OpenTofu

- **Estado:** aceptado (PL-03 a PL-06).
- **Contexto:** el diplomado pide despliegue reproducible y controles de la cadena de suministro; nadie debe aplicar cambios a mano en el clúster.
- **Decisión:** OpenTofu (`iac/cluster`) instala Sealed Secrets, Kyverno, Argo CD y tres aplicaciones (`rednexus`, `rednexus-politicas`, `rednexus-observabilidad`) que sincronizan carpetas de este repositorio con *selfHeal*. Los secretos viajan cifrados (`SealedSecret`) y Kyverno 1.20 (`ImageValidatingPolicy`) solo admite imágenes de RedNexus firmadas por el workflow *Imagen*, más una lista blanca de registros.
- **Alternativas:** Flux (menos interfaz para la demo), `kubectl apply` desde el CI (sin reconciliación ni *drift*), secretos en texto plano o en un gestor externo (costo).
- **Consecuencias:** lo que está en Git es lo que corre; un cambio manual se revierte solo. La llave privada de Sealed Secrets vive fuera de Git (equipo del líder y secreto del repositorio) y es un punto único a custodiar.
