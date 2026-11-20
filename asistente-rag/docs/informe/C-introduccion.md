# C. Introducción

RedNexus es una red de apoyo académico entre estudiantes universitarios. Quien tiene una duda publica una
solicitud de ayuda y la plataforma, con modelos de inteligencia artificial que corren de forma local, le propone
hasta tres compañeros que pueden ayudarle, cada uno con una explicación de por qué encaja.

Este informe documenta el **asistente de soporte** que se agregó a RedNexus en la actividad 2 del módulo 6. Es un
servicio de IA generativa que responde las dudas sobre **cómo usar la plataforma**: registro, solicitudes,
emparejamiento, calificaciones, normas, privacidad y PQRS. Usa la técnica **RAG** (*Retrieval-Augmented
Generation*, generación aumentada con recuperación). Antes de responder, el asistente busca en una base de
conocimiento escrita por el equipo los fragmentos que más se parecen a la pregunta y se los entrega al modelo de
lenguaje como contexto. Así responde con información real de RedNexus en vez de inventarla. Si la respuesta no
está en la base, lo dice y remite al canal de PQRS.

En la actividad se construyó lo siguiente:

- una base de conocimiento en Markdown, verificada contra el código de la aplicación;
- un modelo personalizado en **Open WebUI** (`asistente-rednexus`, sobre `qwen2.5:3b` en **Ollama**) con un
  system prompt de políticas de seguridad y de alcance;
- un *golden dataset* de 52 casos con un script de evaluación que mide latencia, palabras clave y la calificación
  de un modelo juez;
- la integración con la aplicación: el endpoint `POST /api/support/chat`, la página `/ayuda` y el módulo de PQRS al
  que remite el asistente.

El informe está organizado así:

- **D** describe el problema que resuelve el asistente y por qué un chat genérico no sirve.
- **E** define el modelo: el modelo base, los documentos, la estrategia de corte en tokens, el system prompt y los
  hiperparámetros.
- **F** presenta la implementación, las pruebas desde la interfaz y desde la API, y el análisis de los resultados
  con el golden dataset.
- **G** recoge las conclusiones, las dificultades y los trabajos futuros.
