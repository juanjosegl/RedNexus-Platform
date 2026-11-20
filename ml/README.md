# ml/ — Dataset sintético y experimentos de emparejamiento (IA-06, IA-07)

Componente de MLOps de RedNexus: un dataset etiquetado para medir el emparejamiento, experimentos comparables en MLflow y la configuración ganadora registrada como versión del modelo `rednexus-matching`, que es la que usa el backend.

## Contenido

| Archivo | Qué es |
| --- | --- |
| [data/build_dataset.py](data/build_dataset.py) | Genera el dataset: 50 ayudantes ficticios, 100 solicitudes con el ayudante correcto marcado y 10 dudas fuera de tema |
| `data/profiles.json`, `data/requests.json`, `data/off_topic.json` | El dataset (Ley 1581: ningún dato es de una persona real) |
| [rednexus_ml.py](rednexus_ml.py) | Embeddings con Ollama (con caché), el ranking idéntico a `ranking.ts` del backend, métricas y los prompts |
| [run_experiments.py](run_experiments.py) | Corre todos los experimentos, los registra en MLflow y escribe la configuración ganadora |
| [scripts/export_seed.py](scripts/export_seed.py) | Copia los 50 perfiles al seed del backend (`prisma/data/profiles.ts`) |
| `results/winning-config.json` | Configuración ganadora con sus métricas y la versión registrada en MLflow |
| `results/resumen.json` | Una fila por run (parámetros y métricas) |
| `results/explicaciones-v1.json`, `-v2.json` | Las explicaciones evaluadas por el juez |
| `mlflow.db` | Experimentos y Model Registry de MLflow (SQLite) |

## Correrlo

Requisitos: [uv](https://docs.astral.sh/uv/) y Ollama con los modelos:

```bash
ollama pull paraphrase-multilingual && ollama pull nomic-embed-text && ollama pull all-minilm
ollama pull qwen2.5:3b && ollama pull qwen2.5:7b
```

```bash
cd ml
uv sync                                   # mlflow-skinny, numpy y requests
uv run python run_experiments.py          # unos 15 minutos la primera vez; luego usa la caché (.cache/)
uv run python run_experiments.py --skip-judge   # sin el juez de 7B (más rápido)
```

Para ver los experimentos en la interfaz web de MLflow (descarga unos 250 MB):

```bash
uv sync --group ui
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000   # http://localhost:5000
```

Si cambias el dataset: `python3 data/build_dataset.py`, `python3 scripts/export_seed.py` y vuelve a correr los experimentos.

## Qué se mide

| Métrica | Significado |
| --- | --- |
| `precision_at_3` | El ayudante correcto aparece entre los 3 propuestos (la métrica de la propuesta) |
| `hit_at_1` | El primero propuesto es correcto |
| `mrr` | Promedio de 1 / posición del primer correcto |
| `recall_at_3` | Fracción de los ayudantes correctos que quedan en el top 3 |
| `coverage` | Solicitudes que reciben al menos un candidato |
| `off_topic_rejected` | Dudas fuera de tema que **no** reciben candidatos (lo correcto) |
| `classification_area_accuracy` | El LLM acierta el área de la solicitud |
| `explanations_unsupported_rate` | Explicaciones que atribuyen algo que el perfil no dice (juez `qwen2.5:7b`) |

Los resultados y su análisis están en [docs/entrega/06-mlops.md](../docs/entrega/06-mlops.md).

## Cómo se aplica en el backend

La configuración ganadora se despliega por variables de entorno del backend (valores por defecto en `src/modules/matching/matching-config.ts`):

| Variable | Qué controla |
| --- | --- |
| `OLLAMA_EMBED_MODEL` | Modelo de embeddings |
| `OLLAMA_LLM_MODEL` | LLM para clasificar y explicar |
| `MATCH_SIMILARITY_WEIGHT` | Peso de la similitud frente a la calificación |
| `MATCH_MIN_SIMILARITY` | Similitud mínima para proponer a alguien |
| `MATCH_HYBRID_ALPHA` | Peso del embedding en la búsqueda híbrida (1 = solo embedding) |
| `MATCH_ENRICH_QUERY` | Agregar el área y los temas de la clasificación a la consulta |
| `MATCH_CONFIG_VERSION` | Versión de `rednexus-matching` en MLflow (aparece en el log del worker) |

Volver a una versión anterior es cambiar estas variables y reiniciar el worker. Al cambiar de modelo de embeddings hay que reindexar los perfiles (`npm run db:seed` y reiniciar el worker).
