# 7. Pruebas y calidad

## 7.1 Estrategia

| Nivel | Herramienta | Qué cubre | Cuándo corre |
| --- | --- | --- | --- |
| Unitarias del backend | Vitest | Servicios (auth, perfil, solicitudes, emparejamiento, ranking, transcripción, PQRS, soporte, datos personales) y proveedores de IA con dobles de prueba | En cada PR (`build-test`) |
| End-to-end del backend | Vitest + Supertest | Arranque de la aplicación y `/api/health` | En cada PR |
| Componentes del frontend | Vitest + Vue Test Utils | Vistas y componentes: login, registro con autorización, perfil, solicitudes, nota de voz, bandeja del ayudante, estrellas, ayuda, PQRS | En cada PR |
| Calidad estática | oxlint, ESLint, Prettier, `tsc`/`vue-tsc` | Estilo, tipos y errores comunes | En cada PR |
| Imagen | Trivy, Syft, Cosign | Vulnerabilidades, SBOM y firma | En cada PR (sin publicar) y al fusionar |
| Manifiestos | kubeconform, `docker compose config` | Kubernetes y Compose válidos | En cada PR de Platform |
| IA de emparejamiento | `ml/run_experiments.py` (MLflow) | precision@3, MRR, cobertura, fuera de tema, alucinaciones | Al cambiar el ranking o los modelos |
| Asistente RAG | `asistente-rag/evaluate_rag.py` | Golden dataset: fidelidad, completitud, palabras clave, latencia | Al cambiar documentos o el prompt |
| Funcionales de punta a punta | Guion de la demo | El recorrido completo en el navegador | Antes de cada sustentación |

Ningún PR entra a `developer`, `test` o `main` sin el check `build-test` en verde (rulesets de GitHub).

## 7.2 Pruebas funcionales (guion manual)

| # | Caso | Pasos | Resultado esperado |
| --- | --- | --- | --- |
| PF-01 | Registro con autorización | Registrarse sin marcar la casilla; luego marcándola | Primero un mensaje de error; luego entra a la aplicación |
| PF-02 | Solicitud por texto | Publicar "No entiendo cómo unir tres tablas con una intermedia" | Pasa de Pendiente a Con candidatos en menos de 30 s con 3 candidatos y su explicación |
| PF-03 | Solicitud por voz | Grabar la duda, escucharla y publicarla sin texto | La solicitud aparece transcrita y con candidatos |
| PF-04 | Aceptar | Entrar como un candidato, ir a Ayudar, aceptar y confirmar | Se muestra el correo del autor; el autor ve el del ayudante |
| PF-05 | Conflicto | Dos candidatos aceptan la misma solicitud | El segundo ve "Otro compañero aceptó primero" |
| PF-06 | Calificar | El autor califica con 4 estrellas | La calificación queda guardada y el promedio del ayudante cambia |
| PF-07 | Degradación | Apagar Ollama y publicar una duda | Igual recibe candidatos (por etiquetas) y el log dice `por tags` |
| PF-08 | Asistente | Preguntar "¿Cómo califico a quien me ayudó?" en Ayuda | Responde con los pasos y cita la fuente |
| PF-09 | PQRS | Radicar una sugerencia | Aparece con número PQRS-000N y estado Radicada |
| PF-10 | Mis datos | Descargar mis datos y eliminar la cuenta | Baja un JSON; tras eliminar, no se puede volver a entrar |

## 7.3 Validación de la IA generativa e inyección de prompts

| Prueba | Cómo | Resultado |
| --- | --- | --- |
| Clasificación con salida estructurada | Esquema JSON en la llamada a Ollama, validación y un reintento | 100 % de respuestas válidas en las 100 solicitudes del dataset (IA-07) |
| Alucinaciones en las explicaciones | Juez `qwen2.5:7b` revisa si la explicación atribuye algo que no está en el perfil | Ver [MLOps](06-mlops.md#explicaciones) |
| Inyección en la solicitud | El texto va entre `<solicitud>` y el sistema lo trata como dato | Casos de seguridad del golden dataset del asistente (IA-08) |
| Asistente fuera de alcance | Preguntas sobre otros temas o pedir el prompt | El asistente rechaza y no revela el prompt: 100 % en las categorías `fuera_de_alcance`, `fuera_de_base` y `seguridad` de la evaluación final (60 casos, 83,3 % de éxito global) |

## 7.4 Resultados (24/11/2026, rama `developer`)

| Repo | Pruebas automáticas | Resultado |
| --- | --- | --- |
| RedNexus-Backend | 23 archivos con 113 pruebas unitarias (`npm test`) y 5 pruebas e2e (`npm run test:e2e`) | 118 de 118 en verde; lint (oxlint) y `tsc` sin errores |
| RedNexus-Frontend | 24 archivos con 69 pruebas de componentes (`npx vitest run`) | 69 de 69 en verde |
| RedNexus-Platform | CI `validate`: kubeconform con CRD, `tofu validate`, `docker compose config`, shellcheck, pruebas del RAG y del ML | En verde en `developer`, `test` y `main` |
| ml/ | 39 runs comparables en MLflow | Configuración ganadora registrada (`rednexus-matching` v1) |
| asistente-rag/ | Golden dataset de 60 casos con juez `qwen2.5:7b` | 83,3 % de éxito (meta 70 %) |

| Evidencia | Captura |
| --- | --- |
| CI del backend en `main` (lint, tipos, pruebas y build) | [gh-03-ci-backend.png](evidencias/gh-03-ci-backend.png) |
| CI de Platform en `main` | [gh-04-ci-platform.png](evidencias/gh-04-ci-platform.png) |
| Workflow *Imagen* del backend (Trivy, SBOM, firma) | [gh-01-imagen-backend.png](evidencias/gh-01-imagen-backend.png) |
| Workflow *GitOps (kind)* en `main` | [gh-02-gitops-kind.png](evidencias/gh-02-gitops-kind.png) |

## 7.5 Prueba de integración de punta a punta con la IA real

Ejecutada el 24/11/2026 contra la demo local (imágenes de `main`, Ollama, whisper.cpp y Open WebUI), por la API y luego en el navegador (capturas en [evidencias/](evidencias)).

| Caso | Resultado |
| --- | --- |
| PF-02 · Solicitud por texto: *"No entiendo cómo unir tres tablas con una tabla intermedia en SQL…"* | Clasificada como `bases-de-datos`, temas `join, sql, tablas`, nivel intermedio; 3 candidatos (Ana 0,65; Julián 0,48; David 0,44) en **11 s** |
| PF-03 · Nota de voz generada con la voz del sistema (*"…calcular subredes y máscaras en redes de computadores"*) | Transcrita por whisper.cpp ("sobredes y mascaras": error menor de transcripción), área `redes`, 3 candidatos en **13 s** |
| PF-04 · Ana acepta | La API devuelve el correo de la autora |
| PF-05 · Julián acepta después | `409 Conflict`: "La solicitud ya fue aceptada o cerrada" |
| PF-06 · Laura califica con 5 estrellas | Calificación guardada |
| PF-08 · Asistente: *"¿Cómo califico a la persona que me ayudó?"* | Pasos correctos con fuentes `calificaciones.md` y `emparejamiento.md`, en 24,6 s |
| PF-09 · PQRS de sugerencia | Radicado `PQRS-000001`, estado `RADICADA` |
| PF-07 · Ollama apagado | Candidatos por etiquetas en 1,2 s (ver simulacros del capítulo 9) |

**Observaciones:** la explicación del tercer candidato dijo con honestidad que "no domina SQL" (su perfil es NoSQL): el umbral lo dejó pasar con 0,44. En otra corrida, el modelo escribió mal un apellido en la explicación ("Bosen" por "Bolaños"). Ambos casos confirman que la explicación es de apoyo y que la decisión final es del estudiante.
