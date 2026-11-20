# RedNexus — Asistente de soporte con RAG

Asistente de IA generativa que responde dudas sobre **cómo usar RedNexus** (registro, solicitudes de ayuda,
emparejamiento, calificaciones, normas, privacidad y PQRS) usando **solo** la documentación del proyecto, con una
estrategia RAG en Open WebUI y modelos locales en Ollama.

Actividad 2 del módulo 6 del Diplomado CloudForge AI 5.0 (Unicomfacauca). Vive dentro de RedNexus-Platform; la
integración está en [RedNexus-Backend](https://github.com/juanjosegl/RedNexus-Backend) (módulo `support`) y
[RedNexus-Frontend](https://github.com/juanjosegl/RedNexus-Frontend) (página `/ayuda`).

## Cómo encaja en RedNexus

```
Frontend /ayuda  →  POST /api/support/chat (backend)  →  Open WebUI: modelo asistente-rednexus  →  Ollama
                                                           └─ Knowledge "Base RedNexus" (knowledge-base/*.md)
```

Si Open WebUI no está disponible, el backend usa un mock (`SUPPORT_PROVIDER=mock`) y la demo no se cae.

## Contenido

| Carpeta | Qué hay |
| --- | --- |
| [knowledge-base/](knowledge-base) | Documentos de la base de conocimiento (la fuente única del asistente) |
| [model/](model) | [System prompt](model/system-prompt.md), [configuración del RAG e hiperparámetros](model/configuracion.md) y capturas |
| [golden-dataset/](golden-dataset) | Casos de prueba (pregunta → comportamiento esperado), uno por integrante |
| [evaluate_rag.py](evaluate_rag.py) | Evaluación: latencia, palabras clave, juez (fidelidad y completitud) y % de éxito |
| [scripts/setup_openwebui.py](scripts/setup_openwebui.py) | Configura Open WebUI por API: RAG, base de conocimiento y modelo |
| [runs/](runs) | Resultados de cada corrida |
| [docs/](docs) | Informe `Informe-modelo-rag-RedNexus.pdf`, sus secciones y las [tareas del equipo](docs/tareas.md) |

## Estrategia RAG

| Parámetro | Valor |
| --- | --- |
| Modelo base | `qwen2.5:3b` |
| Embeddings | `nomic-embed-text` (Ollama) |
| Corte | **400 tokens**, separador por tokens (tiktoken) |
| Solapamiento | **60 tokens** |
| Top K | 4 |
| Temperatura | 0.2 |

Detalle y justificación en [model/configuracion.md](model/configuracion.md).

## Levantarlo

Todos los comandos se corren dentro de esta carpeta (`cd asistente-rag`).

1. Instala [Ollama](https://ollama.com) y descarga los modelos:
   ```bash
   ollama pull qwen2.5:3b && ollama pull nomic-embed-text && ollama pull qwen2.5:7b
   ```
2. Levanta Open WebUI en http://localhost:3001 y crea la cuenta de administrador:
   ```bash
   docker compose up -d
   ```
3. Crea una API key en **Settings → Account → API keys** y pégala en `.env` (`cp .env.example .env`).
4. Con el entorno de Python de la sección "Evaluar", configura el RAG, sube la base de conocimiento y crea el
   modelo `asistente-rednexus` con un solo comando:
   ```bash
   python scripts/setup_openwebui.py
   ```
   Hace por API lo mismo que se haría a mano: embeddings `nomic-embed-text`, corte por tokens (400/60), Top K 4,
   knowledge `Base RedNexus` con todos los `.md` de `knowledge-base/`, y el modelo con el
   [system prompt](model/system-prompt.md) y los parámetros de [configuracion.md](model/configuracion.md).
   Vuelve a correrlo cada vez que cambie un documento o el prompt.

## Evaluar

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/validate_dataset.py --min-total 50
python evaluate_rag.py
```

Un caso es **exitoso** si el juez le da 4 o más en promedio (fidelidad y completitud), o si contiene todas las
palabras clave y el juez le da al menos 3. Meta: **70 % o más**.

### Corridas

Las tres primeras son corridas parciales con los 18 casos difíciles (seguridad, fuera de alcance, normas,
privacidad, PQRS y emparejamiento), usadas para ajustar el prompt. Las dos últimas son la evaluación final con los
52 casos y la comparación de cortes; la configuración elegida es **400/60**.

| Run | Prompt | Corte | Éxito | Fidelidad | Completitud | Latencia media |
| --- | --- | --- | --- | --- | --- | --- |
| `v1_chunk400_ov60_parcial18` | v1 | 400/60 | 83,3 % | 4,33 | 3,94 | 18,6 s |
| `v2_prompt_chunk400_ov60_parcial18` | v2.1 | 400/60 | 66,7 % | 3,94 | 3,67 | 22,6 s |
| `v2.2_prompt_chunk400_ov60_parcial18` | v2.2 | 400/60 | 88,9 % | 4,83 | 4,33 | 19,3 s |
| `v3_final_chunk400_ov60` (52 casos) | v2.2 | **400/60** | **88,5 %** | 4,67 | 4,44 | 18,7 s |
| `v3_chunk300_ov30` (52 casos) | v2.2 | 300/30 | 80,8 % | 4,69 | 4,19 | 17,7 s |

Detalle y análisis en [docs/informe/F-pruebas.md](docs/informe/F-pruebas.md#f4-resultados-con-el-golden-dataset).

## Cómo aportar

Igual que en el resto de RedNexus-Platform: rama desde `developer` (por ejemplo `docs/DOC-05-registro-y-perfil`),
un commit por paso (`docs(kb): registro y perfil`), `python3 scripts/validate_dataset.py` antes de subir y PR a
`developer` con `Closes #N`. Las tareas están en [docs/tareas.md](docs/tareas.md).

El aporte de cada integrante está en el [README principal](../README.md#asistente-de-soporte-con-rag-actividad-2-del-módulo-6).
