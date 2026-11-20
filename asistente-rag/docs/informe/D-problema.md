# D. Problema que resuelve

## D.1 Contexto

RedNexus es una red de apoyo académico entre estudiantes universitarios: quien tiene una duda publica una solicitud
de ayuda y la plataforma, con modelos de IA locales, le propone hasta tres compañeros que pueden ayudarle, con una
explicación de por qué encaja cada uno. Alrededor de ese flujo hay reglas que el estudiante necesita conocer:
cómo funcionan el emparejamiento y las calificaciones, qué se puede pedir y qué no, quién ve sus datos y qué hacer
cuando algo falla.

## D.2 Necesidad

Las dudas sobre **cómo usar la plataforma** son repetitivas y llegan en cualquier momento. Sin un canal de soporte,
el estudiante tiene tres opciones malas: buscar en documentación que no conoce, escribirle al equipo y esperar, o
abandonar. Además, el soporte de un proyecto académico lo atiende un equipo pequeño, sin turnos ni mesa de ayuda.

Usar un chat de IA genérico tiene dos riesgos:

1. **Alucinaciones:** un modelo general inventa funciones, botones, plazos o precios que RedNexus no tiene.
2. **Desvío del propósito:** se usaría para resolver tareas o exámenes, lo que va contra las normas de la
   comunidad (fraude académico).

## D.3 Servicio propuesto

Un **asistente de soporte con IA generativa y RAG** integrado en la página **Ayuda** de RedNexus:

- Responde en lenguaje natural, en español y en segundos, las dudas sobre el uso de la plataforma.
- Responde **solo** con la base de conocimiento del proyecto (documentos escritos por el equipo), y lo dice cuando
  no tiene la información.
- Rechaza lo que está fuera de su alcance (tareas, temas generales) y redirige a publicar una solicitud de ayuda.
- Resiste intentos de manipulación (*prompt injection*) y nunca pide contraseñas ni revela datos de otros usuarios.
- Cuando no puede resolver el caso, remite al **canal de PQRS** (peticiones, quejas, reclamos y sugerencias), que se
  construyó como parte de esta actividad: el estudiante radica la PQRS, recibe un número de radicado y ve la
  respuesta del equipo en la misma página.

## D.4 Alcance

| Dentro del alcance | Fuera del alcance |
| --- | --- |
| Registro, inicio de sesión y perfil | Resolver ejercicios o explicar temas de materias |
| Solicitudes de ayuda y sus estados | Información que no esté en la base de conocimiento |
| Emparejamiento con IA y sus reglas | Datos de otros usuarios |
| Calificaciones | Acciones sobre la cuenta (el asistente orienta, no ejecuta) |
| Normas de la comunidad, privacidad y PQRS | Conversación general |

## D.5 Por qué RAG y modelos locales

- **RAG en lugar de reentrenar:** la documentación cambia con cada versión de RedNexus. Con RAG basta con actualizar
  los documentos de la base de conocimiento; no hay que volver a entrenar el modelo.
- **Modelos locales (Ollama):** las preguntas de los estudiantes no salen a servicios externos de IA, coherente con
  la política de privacidad del proyecto y con la Ley 1581 de 2012, y sin costo por uso.
- **Open WebUI:** permite gestionar la base de conocimiento, el modelo personalizado y el system prompt, y expone una
  API compatible con OpenAI que el backend de RedNexus consume en `POST /api/support/chat`.
