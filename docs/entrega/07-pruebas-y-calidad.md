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
| Asistente fuera de alcance | Preguntas sobre otros temas o pedir el prompt | El asistente rechaza y no revela el prompt (v2.2: 88,9 % de éxito en los 18 casos difíciles) |

## 7.4 Resultados

| Repo | Pruebas automáticas |
| --- | --- |
| RedNexus-Backend | 16+ archivos, unas 75 pruebas unitarias y e2e (con BE-04, BE-05, DOC-02 e IA-07 fusionados) |
| RedNexus-Frontend | 21 archivos, unas 60 pruebas de componentes (con FE-05 a FE-07 y DOC-02 fusionados) |
| ml/ | 30 runs comparables en MLflow |
| asistente-rag/ | Golden dataset de 50 casos (meta 70 % de éxito) |

> **Pendiente (issue DOC-10):** al cierre, pegar aquí el número exacto que muestra `npm test` en cada repo y una captura del CI en verde.
