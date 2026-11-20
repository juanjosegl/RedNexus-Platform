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
- **Decisión:** Ollama con `qwen2.5:3b` (clasificar y explicar) y `nomic-embed-text` (embeddings de 768 dimensiones); whisper.cpp para las notas de voz. El Mac M1 actúa como nodo de IA (Metal) fuera del clúster.
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

## ADR-009 · Ambiente de demo y CD: Dokploy y Render, con imágenes firmadas en GHCR

- **Estado:** aceptado.
- **Contexto:** el docente exige la demo desplegada en un VPS con CI/CD; el servidor compartido (Dokploy) lo usan cinco grupos.
- **Decisión:** `docker-compose.dokploy.yml` sin puertos publicados ni `container_name`, con dominio por Traefik; cada push a `main` con el CI en verde llama al webhook de Dokploy. Como respaldo gratuito, Render (Blueprint) + Neon. Las imágenes se publican firmadas en GHCR (PL-01, PL-02) para el futuro overlay de Argo CD (PL-03).
- **Alternativas:** solo Argo CD (no hay clúster público), solo Render (se duerme a los 15 minutos).
- **Consecuencias:** demo accesible desde internet con CD real; Argo CD queda como evolución.

## ADR-010 · Configuración del emparejamiento elegida con experimentos (MLflow)

- **Estado:** aceptado.
- **Contexto:** los pesos y el umbral del ranking se habían fijado a mano con el mock (`SIMILARITY_WEIGHT = 0.8`, `MIN_SIMILARITY = 0.15`).
- **Decisión:** comparar modelos de embeddings, prefijos, clasificación previa, pesos y umbral sobre un dataset sintético etiquetado; registrar la ganadora como modelo `rednexus-matching` en MLflow y aplicarla en el backend por variables de entorno (`MATCH_SIMILARITY_WEIGHT`, `MATCH_MIN_SIMILARITY`, `OLLAMA_EMBED_PREFIXES`, `MATCH_CONFIG_VERSION`).
- **Consecuencias:** cada cambio del ranking queda medido y versionado; volver a una versión anterior es cambiar variables. Ver [MLOps](06-mlops.md).

## ADR-011 · Observabilidad con OpenTelemetry y Grafana Cloud

- **Estado:** propuesto (PL-07).
- **Decisión prevista:** instrumentar la API y el worker con OpenTelemetry y enviar a Grafana Cloud (plan gratuito) para no correr Prometheus y Loki en 8 GB. Mientras tanto, el log del worker registra la estrategia y la duración de cada emparejamiento.
