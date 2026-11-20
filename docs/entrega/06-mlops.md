# 6. MLOps: dataset, experimentos y configuración ganadora (IA-06, IA-07)

El código está en [ml/](../../ml) y los resultados completos en `ml/results/` y en MLflow (`ml/mlflow.db`, experimento `rednexus-emparejamiento`).

## 6.1 Dataset sintético (IA-06)

| Conjunto | Tamaño | Contenido |
| --- | --- | --- |
| Perfiles | 50 | Ayudantes ficticios de 15 áreas (bases de datos, programación, matemáticas, redes, cloud, inglés, física, química, electrónica, sistemas operativos, ingeniería de software, IA, seguridad, investigación). Incluye los 20 del seed original |
| Solicitudes | 100 | Escritas como las escribiría un estudiante, cada una con el o los ayudantes correctos marcados |
| Fuera de tema | 10 | Dudas que nadie del dataset puede resolver (cocina, guitarra, gimnasio…) para calibrar el umbral |

Reglas de construcción: varios perfiles comparten área pero no tema (SQL básico frente a PostgreSQL avanzado, cálculo de una variable frente a cálculo vectorial) para que el ranking tenga que distinguir, y las solicitudes evitan repetir las palabras del perfil ("unir tres tablas con una intermedia" para un perfil que dice "joins muchos a muchos"). Los 50 ayudantes aparecen como respuesta correcta al menos una vez. Ningún dato es de una persona real (Ley 1581). El mismo dataset alimenta el seed del backend (`ml/scripts/export_seed.py`), así la demo y los experimentos usan los mismos perfiles.

**Limitación:** el dataset lo escribió el equipo; mide bien las diferencias entre configuraciones, pero las cifras absolutas deben confirmarse con usuarios reales en el piloto.

## 6.2 Diseño de los experimentos (IA-07)

El script replica el ranking del backend (`ranking.ts`): los 10 perfiles más cercanos por coseno (como pgvector), puntaje = *w* · similitud + (1 − *w*) · calificación/5 y el top 3. Cada configuración es un run de MLflow con sus parámetros, métricas y predicciones.

| Métrica | Qué mide |
| --- | --- |
| precision@3 | El ayudante correcto aparece entre los 3 propuestos (la métrica de la propuesta) |
| hit@1 y MRR | Qué tan arriba queda el correcto |
| Cobertura | Solicitudes que reciben al menos un candidato |
| Fuera de tema rechazadas | Dudas sin ayudante posible que **no** reciben candidatos |
| Acierto del área | La clasificación del LLM coincide con el área etiquetada |
| Afirmaciones no soportadas | Explicaciones que atribuyen al ayudante algo que su perfil no dice (juez `qwen2.5:7b`) |

## 6.3 Resultados

### Modelo de embeddings (solo similitud)

| Run | precision@3 | hit@1 | MRR |
| --- | --- | --- | --- |
| Respaldo por etiquetas (sin IA) | 0,84 | 0,69 | 0,755 |
| `nomic-embed-text` (el que usaba el backend) | 0,75 | 0,56 | 0,645 |
| `nomic-embed-text` con prefijos `search_query`/`search_document` | 0,68 | 0,51 | 0,588 |
| `all-minilm` (384 dimensiones, solo inglés) | 0,66 | 0,50 | 0,573 |
| **`paraphrase-multilingual`** (768 dimensiones) | **0,83** | 0,65 | 0,732 |

`nomic-embed-text` se entrenó sobre todo en inglés y en español rinde menos que el modelo multilingüe; los prefijos recomendados para nomic empeoran el resultado en este dataset. `paraphrase-multilingual` tiene 768 dimensiones como nomic, así que **el cambio no exige migrar la columna `vector(768)`**.

### Clasificación previa y búsqueda híbrida

| Run | Acierto del área | precision@3 | hit@1 | MRR |
| --- | --- | --- | --- | --- |
| Sin clasificación | – | 0,83 | 0,65 | 0,732 |
| Prompt v1 (8 áreas, el del backend), área y temas en la consulta | 64 % | 0,89 | 0,73 | 0,802 |
| **Prompt v2 (15 áreas con pistas)**, área y temas en la consulta | **75 %** | 0,93 | 0,73 | 0,822 |
| Prompt v2, +0,05 si el área está en las etiquetas | 75 % | 0,87 | 0,67 | 0,758 |
| Híbrido α = 0,8 (embedding + coincidencia de palabras) | 75 % | 0,93 | 0,80 | 0,862 |
| Híbrido α = 0,7 | 75 % | 0,95 | 0,82 | 0,880 |
| **Híbrido α = 0,6** | 75 % | **0,97** | **0,82** | **0,887** |
| Híbrido α = 0,5 | 75 % | 0,96 | 0,80 | 0,870 |

La clasificación aporta porque el área y los temas se agregan al texto que se convierte en embedding. El prompt v1 solo admitía 8 áreas y el dataset tiene 15; el v2 sube el acierto del 64 % al 75 %. La búsqueda híbrida combina lo mejor de los dos mundos: el embedding entiende sinónimos y la coincidencia de palabras premia los términos técnicos exactos (SQL, VLAN, Karnaugh).

### Peso de la calificación y umbral

| Peso de la similitud *w* | 1,0 | 0,9 | **0,8** | 0,7 | 0,6 | 0,5 |
| --- | --- | --- | --- | --- | --- | --- |
| precision@3 | 0,97 | 0,97 | **0,97** | 0,96 | 0,95 | 0,89 |

Se elige el peso más bajo que no pierde precisión (0,8): así las calificaciones sí influyen en el orden sin sacrificar acierto. Con *w* ≤ 0,6 la calificación empieza a imponerse sobre el tema.

| Umbral de similitud | 0,15 (el del backend) | 0,20 | **0,25** | 0,30 | 0,35 |
| --- | --- | --- | --- | --- | --- |
| precision@3 | 0,97 | 0,97 | **0,94** | 0,91 | 0,82 |
| Cobertura | 1,00 | 1,00 | **0,98** | 0,95 | 0,86 |

Con el híbrido, la similitud del ayudante correcto tiene percentil 10 de 0,31 y mediana de 0,46, mientras que la duda fuera de tema más parecida llega a 0,25. Con 0,25 se deja de proponer candidatos arbitrarios para dudas sin relación a cambio de 3 puntos de precisión.

### Explicaciones

| Prompt de explicación | Afirmaciones no soportadas | Observación |
| --- | --- | --- |
| v1 (el del backend) | 30 % | Errores típicos: "como experta en SQL", "como monitora de…" cuando el perfil no lo dice |
| v2 (reglas estrictas y una frase de escape) | 100 % | Demasiado rígido: el modelo de 3B responde siempre la frase de escape, aunque el perfil sí cubra el tema |
| **v3** (v1 + una regla contra adjetivos y cargos) | **17 %** | Quedan casos como "Ana, como monitora de Bases de Datos I…" cuando la duda es de otro tema: el modelo de 3B no siempre obedece. Se elige v3 |

El juez es `qwen2.5:7b` con criterios explícitos (usar el nombre o resumir el perfil no cuenta como inventar). Se revisaron las explicaciones a mano para calibrar el juez: la primera versión marcaba el nombre de la persona como inventado. También se encontró que el modelo a veces repetía la etiqueta `</perfil>`; el backend ahora la limpia.

## 6.4 Configuración ganadora y despliegue

| Parámetro | Antes | Ahora (`rednexus-matching` v1) |
| --- | --- | --- |
| Embeddings | `nomic-embed-text` | `paraphrase-multilingual` |
| LLM | `llama3.2:3b` | `qwen2.5:3b` |
| Clasificación | Prompt v1, solo metadatos | Prompt v2, área y temas en la consulta |
| Búsqueda | Solo embedding | Híbrida, α = 0,6 |
| Peso de la similitud | 0,8 | 0,8 |
| Umbral | 0,15 | 0,25 |
| Explicación | Prompt v1 (30 % no soportadas) | Prompt v3 (17 %) |

| Métrica | Configuración anterior | Ganadora |
| --- | --- | --- |
| precision@3 | 0,81 | **0,94** |
| hit@1 | 0,67 | **0,79** |
| MRR | 0,733 | **0,860** |
| Fuera de tema rechazadas | 10 % | **90 %** |
| Explicaciones con afirmaciones no soportadas | 30 % | **17 %** |
| Cobertura | 100 % | 98 % |

**Cómo se despliega:** la configuración se registró en el Model Registry de MLflow como el modelo `rednexus-matching`, versión 1 (`ml/results/winning-config.json`). El backend la aplica con valores por defecto en `src/modules/matching/matching-config.ts` y variables de entorno (`OLLAMA_EMBED_MODEL`, `MATCH_SIMILARITY_WEIGHT`, `MATCH_MIN_SIMILARITY`, `MATCH_HYBRID_ALPHA`, `MATCH_ENRICH_QUERY`, `MATCH_CONFIG_VERSION`); el log del worker dice qué versión está usando. Volver atrás es cambiar las variables y reiniciar el worker (ADR-010).

**Prueba en vivo:** con Ollama y la base de la demo, "unir tres tablas con una intermedia" propone a Ana y Natalia, "subredes y máscaras" a Daniela y Andrea (13 a 17 s por solicitud) y "cómo preparo una lasaña" no propone a nadie. **Limitación observada:** "mi modelo tiene 99 % en entrenamiento y 60 % en prueba" se clasificó como ingeniería de software (por la palabra "prueba") y el área equivocada arrastró a perfiles de pruebas de software; las explicaciones, al menos, dicen con honestidad que esos perfiles no encajan. Con un acierto del área del 75 %, mejorar la clasificación es la siguiente palanca (por ejemplo, `qwen2.5:7b` si el hardware lo permite).

**Costo:** la clasificación tarda 1,5 s (mediana) y la explicación 2 s por candidato en el Mac M1, dentro del SLO de 30 s por solicitud.
