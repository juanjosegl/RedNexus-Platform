# Capítulo 4. Apropiación de MLOps y LLMOps

Este capítulo reporta cómo se diseñaron, ejecutaron y desplegaron los componentes de inteligencia artificial de RedNexus: el emparejamiento (un problema de recuperación y ordenamiento), el uso del modelo de lenguaje para clasificar y explicar, el asistente de soporte con RAG y el flujo multimodal de voz. El principio que guió el trabajo fue **medir antes de decidir**: cada cambio de modelo, de *prompt* o de parámetro se comparó con métricas definidas sobre un conjunto etiquetado, se registró y se volvió reversible.

## 4.1 Tipo de aprendizaje automático y herramientas

### 4.1.1 Formulación del problema

El emparejamiento de RedNexus es un problema de **recuperación de información y ordenamiento** (*ranking*) basado en contenido: dada una duda en texto libre, ordenar los perfiles de los colaboradores y proponer los tres más adecuados. No se entrenó un modelo desde cero, porque no existen datos históricos de solicitudes y aceptaciones y porque el hardware no lo permite. En su lugar se usan **modelos preentrenados** (de *embeddings* y de lenguaje) como extractores de representación y como clasificadores en modo *zero-shot*, y se **ajustan los hiperparámetros del sistema** que los combina: el modelo de *embeddings*, el uso de prefijos, la clasificación previa, el peso de la búsqueda híbrida, el peso de la calificación, el umbral de afinidad y el *prompt* de la explicación. El aprendizaje es, por tanto, de selección de configuración por experimentación, con métricas supervisadas sobre un conjunto etiquetado.

### 4.1.2 Herramientas

Tabla: Herramientas de MLOps y LLMOps
| Herramienta | Uso en RedNexus |
| --- | --- |
| Ollama | Servir los modelos de lenguaje y de *embeddings* en el equipo anfitrión (Metal) |
| `qwen2.5:3b` (Q4_K_M) | Clasificar la duda, explicar al candidato y responder en el asistente |
| `qwen2.5:7b` (Q4_K_M) | Juez de las evaluaciones |
| `paraphrase-multilingual`, `nomic-embed-text`, `all-minilm` | Modelos de *embeddings* comparados |
| whisper.cpp con `ggml-base` | Transcripción de notas de voz |
| Python, NumPy y `uv` | Experimentos reproducibles (`ml/`), con caché de *embeddings* |
| MLflow (con SQLite) | Registro de *runs*, parámetros, métricas, artefactos y el Model Registry |
| Open WebUI | Base de conocimiento, fragmentación, recuperación y modelo personalizado del asistente |
| `evaluate_rag.py` | Evaluación del asistente con *golden dataset* y juez |
Nota: Elaboración propia. La ficha completa de modelos, con tamaño, cuantización, identificador y licencia, está en `docs/entrega/05-privacidad-y-riesgos-ia.md`.

### 4.1.3 Dataset sintético

Para medir sin usar datos personales se construyó un conjunto sintético (`ml/data/build_dataset.py`): **50 perfiles** de colaboradores ficticios en 15 áreas (bases de datos, programación, matemáticas, redes, nube, inglés, física, química, electrónica, sistemas operativos, ingeniería de software, inteligencia artificial, seguridad e investigación, entre otras), **100 solicitudes** escritas como las escribiría un estudiante, cada una con su colaborador o colaboradores correctos marcados, y **10 dudas fuera de tema** (cocina, guitarra, gimnasio) que nadie del conjunto puede resolver. Dos reglas lo hacen exigente: varios perfiles comparten área pero no tema (SQL básico frente a PostgreSQL avanzado; cálculo de una variable frente a cálculo vectorial), y las solicitudes evitan repetir las palabras del perfil ("unir tres tablas con una intermedia" para un perfil que dice "*joins* muchos a muchos"). El mismo conjunto alimenta los datos de prueba del *backend*, de modo que la demo y los experimentos usan los mismos perfiles.

## 4.2 Experimentos realizados y elección del mejor modelo

### 4.2.1 Diseño experimental

El *script* de experimentos replica exactamente el ordenamiento del *backend* (`ranking.ts`): recupera los 10 perfiles más cercanos por coseno, como lo haría pgvector, calcula el puntaje combinado con la calificación y toma el top 3. Cada configuración es un *run* de MLflow con sus parámetros, métricas y predicciones; en total se registraron **39 runs** en el experimento `rednexus-emparejamiento`, organizados en ocho grupos que varían un factor a la vez.

Tabla: Métricas de los experimentos de emparejamiento
| Métrica | Qué mide |
| --- | --- |
| precision@3 | El colaborador correcto aparece entre los 3 propuestos (métrica principal, meta ≥ 0,80) |
| hit@1 y MRR | Qué tan arriba queda el correcto |
| Cobertura | Solicitudes que reciben al menos un candidato |
| Fuera de tema rechazadas | Dudas sin colaborador posible que no reciben candidatos |
| Acierto del área | La clasificación del LLM coincide con el área etiquetada |
| Afirmaciones no soportadas | Explicaciones que atribuyen al colaborador algo que su perfil no dice (juez `qwen2.5:7b`) |
Nota: Elaboración propia.

### 4.2.2 Resultados

**Modelo de *embeddings*.** El modelo que usaba el *backend* al inicio, `nomic-embed-text`, obtuvo una precision@3 de 0,75, por debajo incluso del respaldo por etiquetas (0,84). Los prefijos recomendados para ese modelo empeoraron el resultado (0,68) y `all-minilm`, de 384 dimensiones y entrenado en inglés, obtuvo 0,66. El modelo multilingüe `paraphrase-multilingual` alcanzó 0,83 y, al tener también 768 dimensiones, se pudo adoptar sin migrar la columna `vector(768)` de la base de datos. El hallazgo es relevante: el modelo elegido "por defecto" era el peor en español, y solo se descubrió midiendo.

**Clasificación previa y búsqueda híbrida.** Agregar el área y los temas que extrae el LLM al texto de la consulta subió la precision@3 a 0,89 con el *prompt* original (8 áreas, 64 % de acierto del área) y a 0,93 con un *prompt* v2 de 15 áreas con pistas (75 % de acierto). La búsqueda híbrida, que combina el coseno de los *embeddings* con la coincidencia de palabras, mejoró de nuevo: con α = 0,6 la precision@3 llegó a 0,97, el *hit@1* a 0,82 y el MRR a 0,887.

**Peso de la calificación y umbral.** Con el peso de la similitud entre 1,0 y 0,8 la precision@3 se mantuvo en 0,97; con 0,6 o menos la calificación empezó a imponerse sobre el tema. Se eligió *w* = 0,8, el menor peso que no pierde acierto, para que las calificaciones sí influyan. El umbral de afinidad pasó de 0,15 a 0,25: el percentil 10 de la similitud de los colaboradores correctos es 0,31 y la duda fuera de tema más parecida llega a 0,25, de modo que con 0,25 se dejan de proponer candidatos arbitrarios para dudas sin relación a cambio de 3 puntos de precision@3 y 2 de cobertura.

**Explicaciones.** Con el *prompt* original, el 30 % de las explicaciones contenía afirmaciones no soportadas por el perfil ("como experta en SQL", "como monitora de…"). Un *prompt* v2 con reglas estrictas y una frase de escape fue demasiado rígido para un modelo de 3B: respondió siempre la frase de escape (100 % de fallo según el criterio). El *prompt* v3, que agrega al original una regla contra adjetivos y cargos, bajó la tasa al 17 %. Para calibrar al juez se revisaron explicaciones a mano: la primera versión del juez marcaba como invención el simple uso del nombre de la persona.

![precision@3 de las configuraciones de emparejamiento](docs/monografia/img/experimentos-precision.png)
Nota: Elaboración propia a partir de `ml/results/resumen.json`. Las barras de clasificación e híbrido acumulan las mejoras anteriores; la ganadora aplica además el umbral de 0,25, que sacrifica 3 puntos de precisión para rechazar el 90 % de las dudas fuera de tema.

### 4.2.3 Configuración ganadora y su despliegue

Tabla: Configuración inicial frente a la ganadora (rednexus-matching v1)
| Métrica | Configuración inicial | Ganadora |
| --- | --- | --- |
| precision@3 | 0,81 | **0,94** |
| hit@1 | 0,67 | **0,79** |
| MRR | 0,733 | **0,860** |
| Dudas fuera de tema rechazadas | 10 % | **90 %** |
| Explicaciones con afirmaciones no soportadas | 30 % | **17 %** |
| Cobertura | 100 % | 98 % |
Nota: Elaboración propia. La ganadora usa `paraphrase-multilingual`, clasificación con el *prompt* v2 en la consulta, búsqueda híbrida con α = 0,6, peso de la similitud 0,8, umbral 0,25, explicación con el *prompt* v3 y `qwen2.5:3b`.

La configuración ganadora se registró en el **Model Registry** de MLflow como el modelo `rednexus-matching`, versión 1, creada desde el *run* `08-configuracion-ganadora` (archivo `ml/results/winning-config.json`). El *backend* la aplica con valores por defecto en `matching-config.ts` y variables de entorno (`OLLAMA_EMBED_MODEL`, `MATCH_SIMILARITY_WEIGHT`, `MATCH_MIN_SIMILARITY`, `MATCH_HYBRID_ALPHA`, `MATCH_ENRICH_QUERY`, `MATCH_CONFIG_VERSION`), y el *log* del *worker* anuncia al arrancar qué versión usa ("Emparejamiento rednexus-matching v1: peso 0.8, umbral 0.25, híbrido 0.6"). Volver a una versión anterior es cambiar las variables y reiniciar el *worker* (ADR-010).

![Runs del experimento rednexus-emparejamiento en MLflow](docs/entrega/evidencias/mlflow-01-experimentos.png)
Nota: Captura de la interfaz de MLflow 3.18 tomada el 24/11/2026.

![Versión 1 del modelo rednexus-matching en el Model Registry](docs/entrega/evidencias/mlflow-03-version-1.png)
Nota: Captura de la interfaz de MLflow. La versión registra la métrica `precision_at_3 = 0.94` y el *run* de origen.

**Limitación observada.** En la prueba en vivo, "mi modelo tiene 99 % en entrenamiento y 60 % en prueba" se clasificó como ingeniería de software por la palabra "prueba", y el área equivocada arrastró a perfiles de pruebas de software; las explicaciones, al menos, dijeron con honestidad que esos perfiles no encajaban. Con un acierto del área del 75 %, la siguiente palanca de mejora es la clasificación (por ejemplo, con `qwen2.5:7b` si el hardware lo permite).

## 4.3 Uso de LLM, RAG, evaluación y métricas de rendimiento

### 4.3.1 El LLM en el flujo del emparejamiento

El modelo `qwen2.5:3b` cumple dos funciones en el *worker*:

- **Clasificar** la duda en área, temas y nivel. La llamada a Ollama usa un esquema JSON como formato de salida; la respuesta se valida y, si es inválida, se reintenta una vez. En las 100 solicitudes del dataset se obtuvo el 100 % de respuestas válidas.
- **Explicar** cada recomendación con una frase. Es un uso de RAG: el contexto recuperado es el perfil del candidato y el *prompt* exige no atribuirle nada que no esté en él.

En ambos casos el texto del usuario se delimita con etiquetas (`<solicitud>`) y el sistema lo trata como dato, no como instrucción, para mitigar la **inyección de *prompts***. La salida se limpia de etiquetas repetidas por el modelo.

### 4.3.2 Asistente de soporte con RAG

El asistente responde dudas sobre cómo usar la plataforma. Se construyó en **Open WebUI** sobre Ollama y se integró a la aplicación por el *endpoint* `POST /api/support/chat`, que reenvía la pregunta al modelo personalizado y, si Open WebUI no responde, usa un respaldo por palabras clave.

Tabla: Configuración del asistente RAG
| Parámetro | Valor |
| --- | --- |
| Base de conocimiento | 8 documentos: registro y perfil, solicitudes de ayuda, emparejamiento, calificaciones, normas, privacidad, PQRS y preguntas frecuentes |
| Modelo base / modelo personalizado | `qwen2.5:3b` / `asistente-rednexus` |
| *Embeddings* del RAG | `nomic-embed-text` en Ollama |
| Fragmentación | 400 *tokens* con 60 de solapamiento (separador por *tokens*) |
| Fragmentos recuperados (*top-k*) | 4 |
| Temperatura | 0,2 |
| *Prompt* de sistema | v2.2: reglas de seguridad (contraseñas, no revelar instrucciones, no compartir datos de otros) y de respuesta (fuente única, fuera de alcance, sin información → PQRS, reportes) |
Nota: Elaboración propia. La configuración se aplica por API con `asistente-rag/scripts/setup_openwebui.py`, de modo que el asistente se reconstruye igual en cualquier equipo.

El *prompt* de sistema se versionó y cada versión se evaluó. La versión 1 obtuvo 83,3 % en los 18 casos más difíciles pero filtraba parte de sus instrucciones; la 2.1 endureció las reglas y cayó al 66,7 % por exceso de rechazos; la 2.2 las acotó a disparadores explícitos y llegó al 88,9 %.

### 4.3.3 Evaluación del RAG

El *golden dataset* tiene **60 casos** escritos por el equipo, en 11 categorías, con la respuesta esperada, las palabras clave obligatorias y el comportamiento esperado (responder o rechazar). Un caso es exitoso si el juez (`qwen2.5:7b`) le da 4 o más en promedio de fidelidad y completitud, o si contiene todas las palabras clave y el juez le da al menos 3. La meta del diplomado es 70 %.

Tabla: Evolución de las evaluaciones del asistente
| Corrida | *Prompt* | Fragmentación | Casos | Éxito | Fidelidad | Completitud | Latencia media |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v1 parcial | v1 | 400/60 | 18 | 83,3 % | 4,33 | 3,94 | 18,6 s |
| v2 parcial | v2.1 | 400/60 | 18 | 66,7 % | 3,94 | 3,67 | 22,6 s |
| v2.2 parcial | v2.2 | 400/60 | 18 | 88,9 % | 4,83 | 4,33 | 19,3 s |
| v3 final | v2.2 | **400/60** | 52 | **88,5 %** | 4,67 | 4,44 | 18,7 s |
| v3 comparación | v2.2 | 300/30 | 52 | 80,8 % | 4,69 | 4,19 | 17,7 s |
| v4 final (con el octavo documento) | v2.2 | 400/60 | 60 | **83,3 %** | 4,67 | 4,30 | 17,6 s |
Nota: Elaboración propia a partir de `asistente-rag/runs/`. La comparación de fragmentación eligió 400/60 sobre 300/30 (88,5 % frente a 80,8 %).

![Éxito del asistente RAG por categoría en la evaluación final](docs/monografia/img/rag-por-categoria.png)
Nota: Elaboración propia a partir de `asistente-rag/runs/resumen_v4_final_chunk400_ov60_60casos_*.json`. La línea punteada es la meta de 70 %.

El asistente rechaza correctamente el 100 % de las preguntas fuera de alcance, fuera de la base y de seguridad (pedir el *prompt*, compartir contraseñas o datos de otros). Sus puntos débiles son PQRS (50 %) y emparejamiento (66,7 %), donde a veces omite un paso o agrega información que no está en la documentación (por ejemplo, afirmó que una PQRS se podía editar). La caída del 88,5 % al 83,3 % al pasar de 52 a 60 casos se explica porque el octavo documento y sus casos introdujeron preguntas más específicas; ambos resultados superan la meta.

### 4.3.4 Métricas de rendimiento del LLM: TTFT y TPS

Se midieron el tiempo al primer *token* y la velocidad de generación con `asistente-rag/scripts/medir_tps_ttft.py`, que envía con *streaming* las mismas preguntas que reciben el asistente y el clasificador.

Tabla: TTFT y TPS de qwen2.5:3b en el equipo del líder
| Métrica | Mediana | p90 |
| --- | --- | --- |
| TTFT, tiempo al primer *token* (s) | 0,17 | 0,21 |
| TPS de generación (*tokens*/s) | 24,3 | 24,6 |
| TPS de lectura del *prompt* (*tokens*/s) | 334,6 | 355,8 |
| *Tokens* de salida por respuesta | 190 | 230 |
| Tiempo total por respuesta (s) | 8,1 | 9,7 |
Nota: Medición del 24/11/2026 en un Mac M1 de 8 GB con Ollama nativo y el modelo ya cargado; 12 llamadas (6 preguntas × 2 repeticiones).

Con 24 *tokens* por segundo, una explicación de unos 40 *tokens* tarda menos de 2 s, lo que coincide con el costo medido en los experimentos (clasificación de 1,5 s y explicación de 2 s por candidato en mediana) y deja el emparejamiento completo entre 11 y 17 s, dentro del SLO de 30 s. En el asistente, el primer *token* llega rápido, pero la latencia total (17,6 s de media en la evaluación) la dominan las respuestas largas y la lectura de los cuatro fragmentos recuperados; mostrar la respuesta en *streaming* en la interfaz es la mejora natural.

### 4.3.5 Flujo multimodal: notas de voz

El flujo multimodal adicional es de **audio a texto**. La página de nueva solicitud graba la voz en el navegador; la API recibe el archivo (webm, ogg, mp3, wav o m4a, hasta 10 MB) y encola un trabajo `transcribe` con el audio dentro del trabajo, sin guardarlo en disco; el *worker* lo envía a whisper.cpp (`--language es`), guarda el texto como el de la solicitud, elimina el trabajo de Redis y continúa con el emparejamiento normal. En la prueba del 24/11/2026, una nota de voz de cinco segundos se transcribió y emparejó en 13 s; la transcripción tuvo un error menor ("sobredes" por "subredes") que no impidió clasificarla en el área de redes. Si whisper.cpp no está disponible, BullMQ reintenta tres veces y la demo puede usar un transcriptor de prueba.

## 4.4 Conclusiones del capítulo

- Medir cambió decisiones: el modelo de *embeddings* inicial era el peor en español, y la combinación de modelo multilingüe, clasificación previa y búsqueda híbrida elevó la precision@3 de 0,81 a 0,94 y el rechazo de dudas fuera de tema del 10 % al 90 %.
- MLflow convirtió el ajuste del emparejamiento en un proceso reproducible: 39 *runs* comparables, una versión registrada y un despliegue por variables de entorno que se puede revertir.
- Los modelos pequeños son suficientes como apoyo pero no infalibles: el 17 % de las explicaciones aún contiene afirmaciones no soportadas y el área se acierta en el 75 % de los casos; por eso la recomendación se explica, se limita a tres y la decide una persona.
- El asistente RAG cumple la meta (83,3 % en 60 casos, frente a 70 %), con rechazo perfecto en seguridad y fuera de alcance; el versionado del *prompt* mostró que reglas demasiado estrictas empeoran a un modelo de 3B.
- En un portátil de 8 GB, `qwen2.5:3b` responde su primer *token* en 0,17 s y genera 24 *tokens* por segundo, lo que hace viable la IA local dentro del SLO de 30 s.
