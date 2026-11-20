# Configuración del modelo y del RAG

Valores con los que se evalúa el asistente. Si cambias uno, vuelve a correr la evaluación con otro `RUN_TAG`
y anota el resultado en la tabla de corridas del README.

## Modelo personalizado (Open WebUI → Workspace → Models)

| Campo | Valor | Por qué |
| --- | --- | --- |
| Nombre / ID | `asistente-rednexus` | Es el `SUPPORT_MODEL` que usa el backend |
| Modelo base | `qwen2.5:3b` | Buen español y buen seguimiento de instrucciones; cabe en 8 GB de RAM (M1) |
| Alternativa evaluada | `llama3.2:3b` | Es el que ya usa RedNexus para el emparejamiento |
| Knowledge | `Base RedNexus` (todos los `.md` de `knowledge-base/`) | Fuente única de las respuestas |
| System prompt | [system-prompt.md](system-prompt.md) | Delimita alcance y políticas |
| Temperature | `0.2` | Respuestas estables y apegadas al contexto |
| Max tokens (num_predict) | `400` | Respuestas cortas para un chat |
| Context length (num_ctx) | `4096` | Alcanza para el prompt, 4 fragmentos y el historial |

## Documentos (Open WebUI → Admin Panel → Settings → Documents)

| Campo | Valor | Por qué |
| --- | --- | --- |
| Embedding engine | Ollama | Corre local, igual que el resto de la IA de RedNexus |
| Embedding model | `nomic-embed-text` | El mismo del emparejamiento; mejor en español que el MiniLM por defecto |
| Text splitter | **Token (tiktoken)** | La actividad pide el corte en tokens (el valor por defecto mide caracteres) |
| Chunk size | **400 tokens** | Cada sección de los documentos cabe en 1 o 2 fragmentos |
| Chunk overlap | **60 tokens** (15 %) | No partir un paso a la mitad entre dos fragmentos |
| Top K | `4` | Suficiente contexto sin llenar los 4096 tokens |
| Hybrid search | Apagado (versión 1) | Se prueba en una segunda corrida si la precisión no alcanza |

Configuración alternativa para comparar en el informe: **300 tokens con 30 de solapamiento** (`RUN_TAG=v2_chunk300_ov30`).

## Modelo juez

| Campo | Valor |
| --- | --- |
| Modelo | `qwen2.5:7b` (con Colima apagado en el Mac de 8 GB) |
| Temperatura | `0.0` |
| Criterios | Fidelidad (1 a 5) y completitud (1 a 5) frente a la respuesta esperada |
