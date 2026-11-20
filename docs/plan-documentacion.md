# Plan de la documentación y la sustentación

Estado al **4 de noviembre de 2026** frente a lo que pide el docente. Sirve para repartir el trabajo de DOC-01 a DOC-04.

## 1. Cómo vamos

| Área | Hecho | Falta |
| --- | --- | --- |
| **Backend** | BE-01, BE-02, BE-03, BE-05, BE-06 e IA-01 a IA-04 fusionados (PR #13 a #21): registro, perfil, solicitudes, emparejamiento con IA local, aceptar/rechazar y calificaciones | BE-04 e IA-05 (notas de voz) |
| **Frontend** | Estructura base. FE-01 y FE-04 asignados; hay ramas `Aleja` y `Maria` | FE-01 a FE-07: **ningún PR fusionado**. Sin frontend no hay demo de punta a punta |
| **Plataforma** | Compose, k3d/minikube con Kustomize, CI de validación en los 3 repos | PL-01 a PL-09: **ninguna iniciada en GitHub**. Hoy hay **CI pero no CD**: no se publican imágenes ni se despliega en ningún servidor |
| **Documentación** | Guía del equipo, tareas, diagramas, ER y diccionario de datos (`docs/arquitectura`) | Todo el documento formal |

**Riesgo principal para la sustentación:** el docente pide ver CI/CD funcionando "en la plataforma compartida (Dokploy) u otra". El camino más corto es PL-01 (imágenes en GHCR) + desplegar el `compose.yaml` en Dokploy con `AI_PROVIDER=mock` u Ollama en CPU. Argo CD (PL-03) puede quedar como evolución.

## 2. Lo que pide el docente y en qué estado está

### Documento (formato APA 7)

| Requisito | Estado | De dónde sale | Qué falta |
| --- | --- | --- | --- |
| Portada, contraportada, tabla de contenido, lista de tablas y figuras autogeneradas | Falta | Plantilla de Word con estilos de título y "Insertar título" en figuras y tablas | Crear la plantilla una vez y que todos peguen ahí |
| Contexto: problema y cómo se resuelve | Borrador (texto de la compañera) | Ver comentarios en la sección 3 | **Datos de fuentes** (deserción, tutorías, encuestas propias) |
| Por qué cloud native y por qué IA local | Falta | ADR-003 y ADR-004 | Redactar |
| Alcance: construido (módulos 1 a 4) y previsto (5 a 7), y qué queda fuera | Falta | `tareas.md` | **Confirmar qué es cada módulo del diplomado** y rastrear cada ítem a un requisito |
| Marco normativo: Ley 1581, CONPES 4144, lineamientos MinTIC | Falta | [Brechas frente a la Ley 1581](arquitectura/diccionario-de-datos.md#brechas-frente-a-la-ley-1581-para-doc-02) | Una línea por norma sobre cómo nos afecta |
| Partes interesadas (tabla) | Falta | – | Estudiantes, ayudantes, docentes del diplomado, Unicomfacauca, equipo, futura oficina de bienestar |
| Requerimientos funcionales | Implícitos en el código | Endpoints de `tareas.md` | Pasarlos a RF-01... con criterio de aceptación |
| Requerimientos no funcionales (ISO/IEC 25010) | Falta | SLO de 30 s, 8 GB de RAM, multiarquitectura, CI obligatorio | Agruparlos por característica de 25010 |
| Historias de usuario | Implícitas en los issues | Issues de GitHub | Formato "Como... quiero... para..." con criterios |
| ADR | Falta | Lista en la sección 4 | Redactar con plantilla (contexto, decisión, alternativas, consecuencias) |
| Diagramas C4 N1, N2, N3 y despliegue 4+1 | **Hecho** | [diagramas.md](arquitectura/diagramas.md) 1 a 5 | Revisarlos en equipo |
| Modelo ER y diccionario con datos personales, protección y conservación | **Hecho (borrador)** | [diagrama 6](arquitectura/diagramas.md#6-modelo-entidad-relación) y [diccionario](arquitectura/diccionario-de-datos.md) | Aprobar los plazos de conservación |
| Almacenamiento de embeddings e índice vectorial (RAG) | **Hecho** | [Diccionario, sección RAG](arquitectura/diccionario-de-datos.md#embeddings-e-índice-vectorial-rag) | – |
| Secuencia o actividades | **Hecho** | Diagramas 8 a 11 | – |
| Casos de uso | **Hecho** | Diagrama 7 | – |
| Glosario y referencias | Falta | – | Embedding, RAG, LLM, pgvector, GitOps, SLO... |

### A futuro (después de la sustentación)

Pruebas funcionales, validación de IA generativa con inyección de prompts (IA-07), ficha del proyecto, matriz de trazabilidad, análisis de riesgos, pipeline CI/CD (PL-01 a PL-03), IaC (PL-06), SLI/SLO (PL-07) y licencias del software usado.

### Exposición (15 minutos + 10 de preguntas)

| Punto | Estado |
| --- | --- |
| Problema y contexto con datos de fuentes | Falta investigar |
| Arquitectura: C4 N2 y N3, despliegue 4+1 y ADR | Diagramas listos; ADR por escribir |
| Demostración de punta a punta con CI/CD | **Bloqueada por el frontend y por PL-01** |
| Problemas encontrados | Ver sección 5 |
| Módulos pendientes | Tablero |
| Formato institucional | Descargar de la oficina de comunicaciones |

## 3. Comentarios al texto 1.1 propuesto

Es una buena base. Para que cuadre con lo construido y con lo que piden:

1. **"Registro diferenciado de estudiantes y profesionales"**: hoy el sistema tiene **un solo tipo de usuario**; cualquiera puede pedir y dar ayuda. O se ajusta el texto ("cada usuario puede pedir ayuda y ofrecer la suya"), o se agrega un campo de rol al registro (tarea pequeña en BE-01/FE-02). Hay que decidirlo antes de escribir requisitos.
2. **Falta decir que la IA es local** (Ollama en la propia infraestructura): es el argumento de privacidad frente a la Ley 1581 y el CONPES 4144, y lo que nos diferencia de usar una API externa.
3. **Falta el "cómo" de la IA** en una frase: clasifica la duda, la compara por significado (embeddings) con los perfiles y explica por qué recomienda a cada ayudante.
4. **Faltan datos**: cifras de deserción en ingeniería (SPADIES, Ministerio de Educación), uso de monitorías o tutorías, y si es posible una encuesta corta a estudiantes de Unicomfacauca.
5. **"Docentes o profesionales"**: el MVP también incluye a estudiantes de semestres avanzados como ayudantes. Conviene nombrarlos.

## 4. ADR propuestos

| ADR | Decisión | Estado |
| --- | --- | --- |
| 001 | Kubernetes local con k3d (Mac) y minikube (Windows) en vez de un clúster en la nube | Decidido |
| 002 | Una sola imagen para API, worker y migraciones | Decidido |
| 003 | IA local con Ollama (llama3.2:3b, nomic-embed-text) en vez de APIs externas | Decidido |
| 004 | Emparejamiento asíncrono con BullMQ y Redis; la API responde de inmediato | Decidido |
| 005 | pgvector dentro de PostgreSQL en vez de una base vectorial dedicada | Decidido |
| 006 | Degradación controlada: respaldo por etiquetas y explicación por plantilla si la IA falla | Decidido |
| 007 | Tres repositorios (Backend, Frontend, Platform) con flujo developer → test → main | Decidido |
| 008 | JWT sin estado para la autenticación | Decidido |
| 009 | Ambiente de demo y CD: Dokploy, Argo CD o los dos | **Pendiente** |
| 010 | Observabilidad con OpenTelemetry y Grafana | Previsto |

## 5. Problemas encontrados (para la exposición)

- Equipos de 8 GB: todo tuvo que caber en un clúster de un nodo, y Ollama corre fuera del clúster para usar la GPU (Metal) del Mac.
- Mac (ARM) y Windows (x86) en el mismo equipo: imágenes multiarquitectura y dos herramientas de Kubernetes (k3d y minikube).
- Prisma 7 en Docker generaba importaciones `.ts`; se fijó `importFileExtension = "js"`.
- Calibración del umbral de similitud con el modelo de prueba; falta repetirla con `nomic-embed-text` (IA-07).
- Coordinación: el backend avanzó más rápido que el frontend y la plataforma.
