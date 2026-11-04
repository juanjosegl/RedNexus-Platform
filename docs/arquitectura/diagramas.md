# Diagramas de arquitectura de RedNexus

Fuente única de los diagramas del documento (DOC-01). Están en [Mermaid](https://mermaid.js.org), así que GitHub los muestra directamente y se pueden editar como texto en los PR.

**Para exportarlos como imagen** (para el documento en Word o la presentación), pega el bloque en https://mermaid.live y descarga PNG o SVG, o desde la raíz de este repo:

```bash
npx -y @mermaid-js/mermaid-cli -i docs/arquitectura/diagramas.md -o salida/diagrama.md -e png -s 2 -b white
```

Genera `salida/diagrama-1.png` a `diagrama-11.png` en el orden de la tabla; cópialos a [img/](img) con el nombre que ya tienen (por ejemplo `01-c4-contexto.png`).

Convenciones C4: azul oscuro = persona, azul = nuestro sistema o contenedor, gris = sistema externo, **línea punteada = previsto, todavía no construido**.

| # | Diagrama | Estado de lo que muestra |
| --- | --- | --- |
| 1 | C4 nivel 1: contexto | Construido, salvo notas de voz |
| 2 | C4 nivel 2: contenedores | Construido, salvo whisper.cpp y el volumen de audios |
| 3 | C4 nivel 3: componentes de la API y el worker | Construido |
| 4 | 4+1 vista física: despliegue local (k3d / minikube) | Construido |
| 5 | 4+1 vista física: despliegue de demo y CI/CD | Previsto (PL-01, PL-03) |
| 6 | Modelo entidad-relación | Construido (migraciones de Prisma) |
| 7 | Casos de uso | Construido, salvo nota de voz |
| 8 | Secuencia: publicar solicitud y emparejar con IA | Construido |
| 9 | Secuencia: aceptar la ayuda y calificar | Construido |
| 10 | Actividades: algoritmo de emparejamiento | Construido |
| 11 | Estados de la solicitud y del candidato | Construido |

---

## 1. C4 nivel 1: contexto del sistema

Quién usa RedNexus y con qué sistemas se relaciona.

```mermaid
flowchart TB
  sol["<b>Estudiante solicitante</b><br/>[Persona]<br/>Publica una duda académica y<br/>recibe ayudantes recomendados"]
  ayu["<b>Ayudante</b><br/>[Persona]<br/>Estudiante avanzado, docente o<br/>profesional que comparte lo que sabe"]
  ops["<b>Equipo de desarrollo y operación</b><br/>[Persona]<br/>Construye, despliega y monitorea"]

  rn["<b>RedNexus</b><br/>[Sistema de software]<br/>Red de apoyo académico que empareja<br/>solicitudes con ayudantes usando IA local"]

  ia["<b>Modelos de IA locales</b><br/>[Sistema externo: Ollama]<br/>llama3.2:3b (clasificar y explicar)<br/>nomic-embed-text (embeddings)"]
  gh["<b>GitHub</b><br/>[Sistema externo]<br/>Repositorios, Actions y GHCR"]

  sol -- "Publica solicitudes, consulta<br/>candidatos y califica [HTTPS]" --> rn
  ayu -- "Mantiene su perfil, acepta o<br/>rechaza solicitudes [HTTPS]" --> rn
  rn -- "Clasifica, vectoriza y explica<br/>[HTTP/JSON, sin salir de la red propia]" --> ia
  ops -- "Sube código y revisa PR" --> gh
  gh -. "Publica imágenes y despliega<br/>(previsto)" .-> rn

  classDef person fill:#08427b,stroke:#052e56,color:#fff
  classDef system fill:#1168bd,stroke:#0b4884,color:#fff
  classDef external fill:#999,stroke:#6b6b6b,color:#fff
  class sol,ayu,ops person
  class rn system
  class ia,gh external
```

## 2. C4 nivel 2: contenedores

Las piezas que se despliegan por separado. La API y el worker usan **la misma imagen** (`rednexus-api`) con distinto comando.

```mermaid
flowchart TB
  sol["<b>Estudiante solicitante</b><br/>[Persona]"]
  ayu["<b>Ayudante</b><br/>[Persona]"]

  subgraph rn["RedNexus [Sistema de software]"]
    direction TB
    web["<b>Aplicación web</b><br/>[Contenedor: Vue 3, Vite, Pinia, Tailwind<br/>servida por Nginx]<br/>Interfaz del estudiante y del ayudante.<br/>Reenvía /api a la API"]
    api["<b>API</b><br/>[Contenedor: NestJS 12, Prisma 7]<br/>REST bajo /api, JWT, Swagger en /api/docs.<br/>Registra solicitudes y encola el trabajo de IA"]
    worker["<b>Worker de IA</b><br/>[Contenedor: NestJS + BullMQ]<br/>Clasifica, genera embeddings,<br/>empareja top 3 y explica"]
    db[("<b>Base de datos</b><br/>[Contenedor: PostgreSQL 17 + pgvector]<br/>Usuarios, solicitudes, candidatos,<br/>calificaciones y vectores de 768 dim.")]
    redis[("<b>Cola</b><br/>[Contenedor: Redis 7]<br/>Trabajos de BullMQ con<br/>3 reintentos y backoff")]
    audio[("<b>Audios</b><br/>[Volumen compartido]<br/>Notas de voz (previsto, PL-01)")]
    whisper["<b>Transcripción</b><br/>[Contenedor: whisper.cpp]<br/>Voz a texto (previsto, IA-05)"]
  end

  ollama["<b>Ollama</b><br/>[Sistema externo, en el equipo anfitrión]<br/>llama3.2:3b y nomic-embed-text"]

  sol -- "Usa [HTTPS]" --> web
  ayu -- "Usa [HTTPS]" --> web
  web -- "Llama a /api [HTTP/JSON]" --> api
  api -- "Lee y escribe [SQL]" --> db
  api -- "Encola trabajos" --> redis
  worker -- "Consume trabajos" --> redis
  worker -- "Candidatos y vectores [SQL]" --> db
  worker -- "embed, classify, explain<br/>[HTTP/JSON :11434]" --> ollama
  api -. "Guarda el audio" .-> audio
  worker -. "Lee el audio" .-> audio
  worker -. "Transcribe" .-> whisper

  classDef person fill:#08427b,stroke:#052e56,color:#fff
  classDef container fill:#438dd5,stroke:#2e6295,color:#fff
  classDef external fill:#999,stroke:#6b6b6b,color:#fff
  classDef planned fill:#eaf2fb,stroke:#438dd5,color:#1d3b5c,stroke-dasharray:5 5
  class sol,ayu person
  class web,api,worker,db,redis container
  class ollama external
  class audio,whisper planned
  style rn fill:none,stroke:#1168bd,stroke-width:2px,stroke-dasharray:8 4
```

## 3. C4 nivel 3: componentes de la API y del worker

Módulos de NestJS del repo RedNexus-Backend (`src/modules`).

```mermaid
flowchart TB
  web["<b>Aplicación web</b><br/>[Contenedor]"]

  subgraph apic["API [Contenedor: NestJS]"]
    direction TB
    auth["<b>AuthModule</b><br/>[Componente]<br/>Registro y login, bcrypt,<br/>JWT de 7 días, JwtAuthGuard"]
    users["<b>UsersModule</b><br/>[Componente]<br/>Perfil: nombre, bio y etiquetas;<br/>promedio de calificaciones"]
    hr["<b>HelpRequestsModule</b><br/>[Componente]<br/>Crear, listar, ver detalle<br/>y cerrar solicitudes"]
    matches["<b>MatchesController / Service</b><br/>[Componente del MatchingModule]<br/>Bandeja del ayudante;<br/>aceptar o rechazar"]
    ratings["<b>RatingsModule</b><br/>[Componente]<br/>Calificar de 1 a 5,<br/>una por solicitud"]
    health["<b>HealthModule</b><br/>[Componente: Terminus]<br/>/api/health para sondas"]
    producer["<b>QueueModule</b><br/>[Componente: BullMQ]<br/>Productor de la cola ai"]
    prisma1["<b>PrismaService</b><br/>[Componente: Prisma 7 + adapter-pg]"]
  end

  subgraph workc["Worker de IA [Contenedor: NestJS sin HTTP]"]
    direction TB
    proc["<b>AiProcessor</b><br/>[Componente: WorkerHost]<br/>Concurrencia 2; al arrancar<br/>reencola lo pendiente"]
    msvc["<b>MatchingService</b><br/>[Componente]<br/>Búsqueda semántica con respaldo<br/>por etiquetas; guarda el top 3"]
    rank["<b>ranking</b><br/>[Componente]<br/>80 % similitud + 20 % calificación,<br/>umbral mínimo 0,15"]
    prov["<b>AiProvider</b><br/>[Interfaz]<br/>OllamaProvider o MockAiProvider<br/>según AI_PROVIDER"]
    prisma2["<b>PrismaService</b>"]
  end

  db[("PostgreSQL + pgvector")]
  redis[("Redis")]
  ollama["Ollama"]

  web --> auth & users & hr & matches & ratings
  users -- "embed-profile" --> producer
  hr -- "match" --> producer
  auth & users & hr & matches & ratings --> prisma1
  producer --> redis
  prisma1 --> db
  redis --> proc
  proc --> msvc
  msvc --> rank
  msvc --> prov
  msvc --> prisma2
  prov --> ollama
  prisma2 --> db

  classDef container fill:#438dd5,stroke:#2e6295,color:#fff
  classDef component fill:#85bbf0,stroke:#5d82a8,color:#0b2a4a
  classDef external fill:#999,stroke:#6b6b6b,color:#fff
  class web,db,redis container
  class auth,users,hr,matches,ratings,health,producer,prisma1,proc,msvc,rank,prov,prisma2 component
  class ollama external
  style apic fill:none,stroke:#438dd5,stroke-width:2px,stroke-dasharray:8 4
  style workc fill:none,stroke:#438dd5,stroke-width:2px,stroke-dasharray:8 4
```

## 4. Vista física (4+1): despliegue local

Lo que hoy levanta `bash scripts/k8s-up.sh [k3d|minikube]`. Ollama corre fuera del clúster para usar la GPU del equipo (Metal en Mac).

```mermaid
flowchart TB
  dev["Navegador del usuario"]

  subgraph host["Equipo de desarrollo [Mac M1 8 GB con Colima, o Windows con WSL2 + Docker]"]
    direction TB
    ollama["<b>Ollama</b> [proceso nativo :11434]<br/>llama3.2:3b, nomic-embed-text"]
    subgraph k8s["Clúster Kubernetes de un nodo [k3d 'rednexus' o minikube perfil 'rednexus']"]
      direction TB
      ing["<b>Ingress</b><br/>Traefik (k3d, localhost:8080)<br/>ingress-nginx (minikube, port-forward)"]
      subgraph ns["namespace rednexus"]
        direction TB
        web["<b>Deployment web</b><br/>rednexus-web: Nginx + SPA"]
        api["<b>Deployment api</b><br/>rednexus-api<br/>initContainer: prisma migrate deploy"]
        worker["<b>Deployment worker</b><br/>rednexus-api: node dist/worker"]
        pg[("<b>StatefulSet postgres</b><br/>pgvector/pgvector:pg17<br/>PVC 1 Gi")]
        redis[("<b>Deployment redis</b><br/>redis:7-alpine")]
        cfg["ConfigMap api-config<br/>Secrets api-secrets, postgres-secrets"]
      end
    end
  end

  dev -- "HTTP" --> ing
  ing --> web
  web -- "/api" --> api
  api --> pg
  api --> redis
  worker --> redis
  worker --> pg
  worker -- "host.k3d.internal:11434" --> ollama
  cfg -. "envFrom" .-> api & worker

  classDef node fill:#438dd5,stroke:#2e6295,color:#fff
  classDef external fill:#999,stroke:#6b6b6b,color:#fff
  classDef cfg fill:#fff7e0,stroke:#c9a227,color:#5a4500
  class ing,web,api,worker,pg,redis node
  class ollama external
  class cfg cfg
```

## 5. Vista física (4+1): despliegue de demo y CI/CD (previsto)

Flujo objetivo de PL-01 a PL-05. **Pendiente decidir** si el ambiente de demo es el clúster con Argo CD o la plataforma compartida Dokploy que pide el docente (ver ADR pendiente).

```mermaid
flowchart TB
  devs["<b>Equipo</b><br/>[5 personas]"]
  subgraph gh["GitHub"]
    direction LR
    repos["Repos Backend, Frontend, Platform<br/>ramas developer → test → main"]
    ci["<b>GitHub Actions</b><br/>lint, typecheck, pruebas, build<br/>buildx amd64 + arm64"]
    sec["Trivy (escaneo), Syft (SBOM),<br/>cosign keyless (firma)"]
    ghcr[("<b>GHCR</b><br/>rednexus-backend<br/>rednexus-frontend")]
  end
  subgraph demo["Ambiente de demo"]
    direction LR
    argo["<b>Argo CD</b> o <b>Dokploy</b><br/>sincroniza deploy/overlays/demo"]
    kyv["Kyverno: solo imágenes firmadas<br/>Sealed Secrets: secretos cifrados"]
    app["Pods de RedNexus<br/>(misma topología del diagrama 4)"]
    obs["OpenTelemetry → Grafana<br/>SLO: 95 % con candidatos en menos de 30 s"]
  end

  devs -- "PR" --> repos
  repos --> ci
  ci --> sec
  sec -- "push con etiqueta sha" --> ghcr
  ci -. "actualiza la etiqueta del overlay" .-> repos
  repos -. "GitOps: pull" .-> argo
  ghcr -. "pull de imágenes" .-> app
  argo -.-> app
  kyv -.-> app
  app -.-> obs

  classDef person fill:#08427b,stroke:#052e56,color:#fff
  classDef built fill:#438dd5,stroke:#2e6295,color:#fff
  classDef planned fill:#eaf2fb,stroke:#438dd5,color:#1d3b5c,stroke-dasharray:5 5
  class devs person
  class repos,ci built
  class sec,ghcr,argo,kyv,app,obs planned
```

## 6. Modelo entidad-relación

Tomado de `RedNexus-Backend/prisma/schema.prisma`. `PII` = dato personal (Ley 1581 de 2012); `SENS` = dato que requiere protección reforzada.

```mermaid
erDiagram
  USER ||--o{ HELP_REQUEST : "publica"
  USER ||--o{ MATCH : "es candidato en"
  HELP_REQUEST ||--o{ MATCH : "genera hasta 3"
  HELP_REQUEST ||--o| RATING : "recibe como máximo 1"
  USER ||--o{ RATING : "otorga (autor)"
  USER ||--o{ RATING : "recibe (ayudante)"

  USER {
    uuid id PK
    string email UK "PII"
    string passwordHash "SENS: hash bcrypt"
    string name "PII"
    string bio "PII: habilidades en texto libre"
    string_array tags "materias y nivel"
    vector_768 embedding "derivado del perfil"
    datetime createdAt
  }
  HELP_REQUEST {
    uuid id PK
    uuid authorId FK
    string text "puede contener PII"
    string audioPath "SENS: voz (previsto)"
    string area "clasificación del LLM"
    string_array topics
    string level "basico, intermedio, avanzado"
    vector_768 embedding "derivado del texto"
    enum status "PENDING, MATCHED, ACCEPTED, CLOSED"
    datetime createdAt
  }
  MATCH {
    uuid id PK
    uuid requestId FK "UK junto con helperId"
    uuid helperId FK
    float score "0 a 1"
    string explanation "frase del LLM"
    enum status "PROPOSED, ACCEPTED, REJECTED"
    datetime createdAt
  }
  RATING {
    uuid id PK
    uuid requestId FK "UK: una por solicitud"
    uuid authorId FK
    uuid helperId FK
    int stars "1 a 5"
    datetime createdAt
  }
```

## 7. Casos de uso

En el MVP un mismo usuario puede ser solicitante y ayudante: los dos son especializaciones de *Usuario registrado* y heredan sus casos de uso.

```mermaid
flowchart LR
  usr(["👤 Usuario registrado"])
  sol(["👤 Estudiante solicitante"])
  ayu(["👤 Ayudante"])
  ia(["⚙ Worker de IA<br/>[actor de sistema]"])

  subgraph rn["Sistema RedNexus"]
    direction TB
    subgraph cuenta["Cuenta"]
      direction TB
      uc1(["Registrarse"])
      uc2(["Iniciar sesión"])
      uc3(["Gestionar perfil y habilidades"])
    end
    subgraph pedir["Pedir ayuda"]
      direction TB
      uc4(["Publicar solicitud por texto"])
      uc5(["Publicar solicitud por nota de voz"])
      uc6(["Ver mis solicitudes y candidatos"])
      uc7(["Cerrar solicitud"])
      uc8(["Calificar la ayuda"])
    end
    subgraph dar["Dar ayuda"]
      direction TB
      uc9(["Ver solicitudes donde soy candidato"])
      uc10(["Aceptar o rechazar solicitud"])
    end
    subgraph ias["Inteligencia artificial local"]
      direction TB
      uc13(["Emparejar top 3 con explicación"])
      uc11(["Clasificar la solicitud"])
      uc12(["Generar embeddings"])
      uc14(["Transcribir nota de voz"])
    end
  end

  sol -- "«es un»" --> usr
  ayu -- "«es un»" --> usr
  usr --- uc1 & uc2 & uc3
  sol --- uc4 & uc5 & uc6 & uc7 & uc8
  ayu --- uc9 & uc10
  uc11 & uc12 & uc13 & uc14 --- ia
  uc4 -. "«include»" .-> uc13
  uc5 -. "«include»" .-> uc14

  classDef actor fill:#08427b,stroke:#052e56,color:#fff
  classDef uc fill:#dbeafe,stroke:#1168bd,color:#0b2a4a
  classDef planned fill:#fff,stroke:#1168bd,color:#1d3b5c,stroke-dasharray:5 5
  class usr,sol,ayu,ia actor
  class uc1,uc2,uc3,uc4,uc6,uc7,uc8,uc9,uc10,uc11,uc12,uc13 uc
  class uc5,uc14 planned
  style rn fill:none,stroke:#1168bd,stroke-width:2px
```

El emparejamiento (uc13) incluye clasificar (uc11) y generar embeddings (uc12); se omiten esas flechas para que el diagrama se lea mejor y se detallan en el diagrama 10.

## 8. Secuencia: publicar una solicitud y emparejar con IA

La API responde de inmediato con `PENDING`; el trabajo pesado ocurre en el worker y el frontend consulta el estado.

```mermaid
sequenceDiagram
  autonumber
  actor S as Estudiante
  participant W as Aplicación web
  participant A as API
  participant DB as PostgreSQL + pgvector
  participant Q as Redis (BullMQ)
  participant K as Worker de IA
  participant O as Ollama

  S->>W: Escribe su duda y envía
  W->>A: POST /api/help-requests { text } + JWT
  A->>A: JwtAuthGuard valida el token
  A->>DB: INSERT HelpRequest (status PENDING)
  A->>Q: add("match", { requestId })
  A-->>W: 201 { id, status: PENDING }
  W-->>S: "Buscando ayudantes..."

  Q->>K: Entrega el trabajo (3 intentos, backoff exponencial)
  K->>DB: Lee la solicitud (si ya no está PENDING, termina)
  K->>O: classify(text) con llama3.2:3b
  O-->>K: { area, topics, level }
  K->>O: embed(text) con nomic-embed-text
  O-->>K: vector de 768 dimensiones
  K->>DB: Top 10 perfiles por distancia coseno (<=>)
  alt Sin IA o sin perfiles indexados
    K->>DB: Respaldo: coincidencia de palabras con bio y etiquetas
  end
  K->>K: rank(): 80 % similitud + 20 % calificación, top 3
  loop Por cada candidato
    K->>O: explain(solicitud, perfil)
    O-->>K: "Te puede ayudar porque..."
  end
  K->>DB: Transacción: INSERT Match x3 y status MATCHED

  loop Cada pocos segundos mientras esté PENDING
    W->>A: GET /api/help-requests/:id
    A->>DB: Solicitud + candidatos
    A-->>W: status MATCHED + matches[]
  end
  W-->>S: Muestra 3 ayudantes con su explicación
```

## 9. Secuencia: aceptar la ayuda y calificar

```mermaid
sequenceDiagram
  autonumber
  actor H as Ayudante
  actor S as Estudiante
  participant W as Aplicación web
  participant A as API
  participant DB as PostgreSQL

  H->>W: Abre "Solicitudes para ayudar"
  W->>A: GET /api/matches/incoming
  A->>DB: Matches donde helperId = yo
  A-->>W: Lista con solicitud, score y explicación
  H->>W: Acepta una solicitud
  W->>A: POST /api/matches/:id/accept
  A->>DB: Transacción: HelpRequest MATCHED → ACCEPTED (solo una vez)
  alt Otro ayudante ya aceptó
    A-->>W: 409 La solicitud ya fue aceptada o cerrada
  else Primero en aceptar
    A->>DB: Match PROPOSED → ACCEPTED
    A-->>W: 200 { authorEmail }
    W-->>H: Correo del estudiante para contactarlo
  end

  Note over H,S: La ayuda ocurre fuera de la plataforma (correo, reunión)

  S->>W: Califica con estrellas
  W->>A: POST /api/ratings { requestId, stars }
  A->>A: Valida: es el autor, la solicitud fue aceptada, 1 ≤ stars ≤ 5
  A->>DB: INSERT Rating (único por solicitud)
  A-->>W: 201
  Note over DB: El promedio de estrellas sube o baja<br/>el puntaje del ayudante en futuros emparejamientos
```

## 10. Actividades: algoritmo de emparejamiento

Lo que hace `MatchingService.matchRequest` en el worker.

```mermaid
flowchart TD
  start((Inicio)) --> read[Leer la solicitud]
  read --> pend{¿Sigue en PENDING?}
  pend -- No --> skip[Terminar sin cambios<br/>reintento idempotente] --> fin((Fin))
  pend -- Sí --> cls[Clasificar con el LLM<br/>área, temas y nivel]
  cls --> emb[Calcular embedding de la solicitud]
  emb --> okemb{¿Hay embedding?}
  okemb -- Sí --> sem[Buscar 10 perfiles más cercanos<br/>por distancia coseno en pgvector]
  okemb -- "No (Ollama caído)" --> tags
  sem --> any{¿Hay candidatos?}
  any -- Sí --> rank
  any -- No --> tags[Respaldo: % de palabras de la solicitud<br/>presentes en bio y etiquetas]
  tags --> rank[Ordenar: 0,8 × similitud + 0,2 × calificación<br/>sin calificaciones cuenta 3/5<br/>descartar similitud menor a 0,15<br/>excluir al autor; tomar top 3]
  rank --> exp[Pedir al LLM una explicación por candidato]
  exp --> okexp{¿El LLM respondió?}
  okexp -- Sí --> save
  okexp -- No --> fb[Explicación de respaldo con plantilla] --> save
  save[Guardar candidatos y pasar a MATCHED<br/>en una sola transacción] --> fin

  classDef decision fill:#fff7e0,stroke:#c9a227,color:#5a4500
  classDef step fill:#dbeafe,stroke:#1168bd,color:#0b2a4a
  class pend,okemb,any,okexp decision
  class read,cls,emb,sem,tags,rank,exp,fb,save,skip step
```

## 11. Estados de la solicitud y del candidato

```mermaid
stateDiagram-v2
  direction LR
  state "Solicitud" as S {
    [*] --> PENDING : El estudiante la publica
    PENDING --> MATCHED : El worker guarda el top 3
    PENDING --> CLOSED : El autor la cierra
    MATCHED --> ACCEPTED : Un ayudante acepta
    MATCHED --> CLOSED : El autor la cierra
    ACCEPTED --> CLOSED : El autor la cierra
    CLOSED --> [*]
  }
  state "Candidato (Match)" as M {
    [*] --> PROPOSED : Creado por el worker
    PROPOSED --> ACCEPTED_M : El ayudante acepta
    PROPOSED --> REJECTED : El ayudante rechaza
    ACCEPTED_M --> [*]
    REJECTED --> [*]
  }
  state "ACCEPTED" as ACCEPTED_M
```
