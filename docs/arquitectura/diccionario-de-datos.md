# Diccionario de datos de RedNexus

Acompaña al [modelo entidad-relación](diagramas.md#6-modelo-entidad-relación). Fuente: `RedNexus-Backend/prisma/schema.prisma` y sus migraciones.

**Clasificación** (Ley 1581 de 2012):
- **Público**: no identifica a nadie.
- **Personal**: identifica o hace identificable a una persona (art. 3).
- **Sensible**: su mal uso puede afectar la intimidad o generar discriminación (art. 5). La voz entra aquí si se usa para identificar a alguien (dato biométrico).
- **Credencial**: no es dato personal en sí, pero da acceso a la cuenta.

Los **plazos de conservación** son una propuesta: el equipo debe aprobarlos y la política de privacidad debe publicarlos.

## User (usuario)

| Campo | Tipo | Nulo | Restricción | Descripción | Clasificación | Protección | Conservación propuesta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | No | PK | Identificador interno | Público | No revela orden ni cantidad de usuarios | Mientras exista la cuenta |
| email | text | No | Único | Correo de acceso; se entrega al autor solo cuando un colaborador acepta | Personal | No se expone en `GET /users/:id`; solo viaja en `POST /matches/:id/accept` | Mientras exista la cuenta |
| passwordHash | text | No | – | Hash bcrypt de la contraseña (8 a 72 caracteres) | Credencial | bcrypt con sal; nunca sale de la API | Mientras exista la cuenta |
| name | text | No | – | Nombre visible | Personal | Visible solo para usuarios con sesión | Mientras exista la cuenta |
| bio | text | Sí | – | Habilidades y experiencia en texto libre | Personal | Se procesa solo con IA local (Ollama), sin enviarla a terceros | Mientras exista la cuenta |
| tags | text[] | No | – | Materias y nivel | Personal (perfil académico) | Igual que bio | Mientras exista la cuenta |
| embedding | vector(768) | Sí | – | Vector de bio + tags (nomic-embed-text) | Personal derivado | Se recalcula al editar el perfil; no se expone por la API | Se borra con la cuenta |
| createdAt | timestamp | No | default now() | Fecha de registro | Personal (metadato) | – | Mientras exista la cuenta |

## HelpRequest (solicitud de ayuda)

| Campo | Tipo | Nulo | Restricción | Descripción | Clasificación | Protección | Conservación propuesta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | No | PK | Identificador | Público | – | Igual que la solicitud |
| authorId | uuid | No | FK → User | Quién pide ayuda | Personal | Solo el autor ve el detalle completo | Igual que la solicitud |
| text | text | No | – | Duda académica en texto (o transcrita) | Personal; puede contener datos sensibles que el usuario escriba | Procesada solo con IA local; advertir al usuario que no incluya datos sensibles | 12 meses después de cerrada, luego anonimizar |
| audioPath | text | Sí | – | Ruta de la nota de voz original (previsto, BE-04) | **Sensible** (voz) | Volumen interno, sin URL pública | Borrar el audio al transcribir o a los 30 días |
| area | text | Sí | – | Área asignada por el LLM | Público | – | Igual que la solicitud |
| topics | text[] | No | – | Temas detectados por el LLM | Público | – | Igual que la solicitud |
| level | text | Sí | básico, intermedio, avanzado | Nivel estimado por el LLM | Público | – | Igual que la solicitud |
| embedding | vector(768) | Sí | – | Vector del texto | Personal derivado | No se expone por la API | Se borra con la solicitud |
| status | enum | No | PENDING, MATCHED, ACCEPTED, CLOSED | Estado ([diagrama 11](diagramas.md#11-estados-de-la-solicitud-y-del-candidato)) | Público | – | Igual que la solicitud |
| createdAt | timestamp | No | default now() | Fecha de creación | Público | – | Igual que la solicitud |

## Match (candidato)

| Campo | Tipo | Nulo | Restricción | Descripción | Clasificación | Protección | Conservación propuesta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | No | PK | Identificador | Público | – | Igual que la solicitud |
| requestId | uuid | No | FK → HelpRequest; único con helperId | Solicitud | Público | – | Igual que la solicitud |
| helperId | uuid | No | FK → User | Colaborador propuesto | Personal | Solo él ve la bandeja; solo él acepta o rechaza | Igual que la solicitud |
| score | float | No | 0 a 1 | 0,8 × similitud + 0,2 × calificación | Personal derivado (perfilamiento) | Se explica al usuario (transparencia de la IA) | Igual que la solicitud |
| explanation | text | Sí | – | Frase del LLM de por qué encaja | Personal derivado | Generada con IA local; respaldo por plantilla | Igual que la solicitud |
| status | enum | No | PROPOSED, ACCEPTED, REJECTED | Respuesta del colaborador | Público | – | Igual que la solicitud |
| createdAt | timestamp | No | default now() | – | Público | – | Igual que la solicitud |

## Rating (calificación)

| Campo | Tipo | Nulo | Restricción | Descripción | Clasificación | Protección | Conservación propuesta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | uuid | No | PK | Identificador | Público | – | Mientras exista la cuenta del colaborador |
| requestId | uuid | No | FK → HelpRequest; **único** | Una calificación por solicitud | Público | Índice único en la base | Igual |
| authorId | uuid | No | FK → User | Quién califica (solo el autor de la solicitud) | Personal | La API no expone las calificaciones individuales | Igual |
| helperId | uuid | No | FK → User | Colaborador calificado | Personal | Solo se publica el promedio | Igual |
| stars | int | No | 1 a 5 | Estrellas | Personal (evaluación) | Validado en la API | Igual |
| createdAt | timestamp | No | default now() | – | Público | – | Igual |

## Embeddings e índice vectorial (RAG)

- **Qué se vectoriza:** el perfil (`bio` + `tags`) y el texto de cada solicitud. No hay documentos aparte: los "documentos" del RAG son los perfiles de los colaboradores.
- **Dónde se guarda:** en la misma tabla, columna `embedding vector(768)` de pgvector, así se borran junto con el dato de origen.
- **Modelo:** `nomic-embed-text` en Ollama, local. Ningún dato sale a una API externa.
- **Búsqueda:** distancia coseno (`<=>`), los 10 más cercanos, y luego `ranking.ts` deja el top 3. El texto de esos 3 perfiles es el contexto que recibe `llama3.2:3b` para escribir la explicación.
- **Índice:** hoy **no hay índice vectorial** (búsqueda secuencial), suficiente para el volumen del MVP (cientos de perfiles). Con más volumen se agrega `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)`.

## Brechas frente a la Ley 1581 (para DOC-02)

| Brecha | Artículo relacionado | Propuesta |
| --- | --- | --- |
| El registro no pide **autorización** del tratamiento ni enlaza una política de privacidad | Arts. 9 y 12 | Casilla obligatoria y campo `consentAt` en User |
| No hay forma de **eliminar la cuenta** ni de descargar los datos | Art. 8 (derecho de supresión, acceso) | `DELETE /users/me` en cascada y `GET /users/me/export` |
| No hay plazos de conservación aplicados | Art. 4 (principio de finalidad y temporalidad) | Tarea programada que anonimice solicitudes cerradas hace más de 12 meses |
| El JWT dura 7 días y no se puede revocar | Lineamientos de seguridad MinTIC | Bajar a 1 día o agregar refresh token |
| Secretos de desarrollo en texto plano en Git | Lineamientos de seguridad MinTIC | Sealed Secrets en el ambiente de demo (PL-04) |
