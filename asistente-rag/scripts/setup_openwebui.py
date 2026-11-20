"""Configura Open WebUI como código: RAG, base de conocimiento y modelo `asistente-rednexus`.

Hace por API lo mismo que se haría a mano en la interfaz, para que cualquiera del equipo lo reproduzca:
  1. Embeddings con Ollama (`nomic-embed-text`).
  2. Corte por tokens (CHUNK_SIZE / CHUNK_OVERLAP) y Top K.
  3. Knowledge "Base RedNexus": se vacía y se vuelven a subir todos los .md de knowledge-base/.
  4. Modelo `asistente-rednexus` con el system prompt de model/system-prompt.md y sus parámetros.
  5. Plantilla RAG en español de model/rag-template.md.

Requiere OPENWEBUI_API_KEY de una cuenta administradora en .env (ver .env.example).

Uso (desde asistente-rag/):
  python scripts/setup_openwebui.py                                  # 400 tokens, 60 de solapamiento
  CHUNK_SIZE=300 CHUNK_OVERLAP=30 python scripts/setup_openwebui.py   # configuración alternativa
"""

from __future__ import annotations

import json
import os
import re
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

BASE_URL = os.getenv("OPENWEBUI_BASE_URL", "http://localhost:3001/api").rstrip("/")
API_KEY = os.getenv("OPENWEBUI_API_KEY", "")
OLLAMA_FROM_OPENWEBUI = os.getenv("OLLAMA_FROM_OPENWEBUI", "http://host.docker.internal:11434")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "60"))
TOP_K = int(os.getenv("TOP_K", "4"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
BASE_MODEL = os.getenv("BASE_MODEL", "qwen2.5:3b")
MODEL_ID = os.getenv("TARGET_MODEL", "asistente-rednexus")
# Open WebUI puede pedirle al modelo que reescriba la pregunta antes de buscar (una llamada extra al LLM)
QUERY_GENERATION = os.getenv("RETRIEVAL_QUERY_GENERATION", "true").lower() == "true"
KNOWLEDGE_NAME = "Base RedNexus"

PARAMS = {"temperature": 0.2, "num_ctx": 4096, "max_tokens": 400}


def call(method: str, path: str, body: dict | None = None, raw: bytes | None = None, ctype: str = "") -> dict:
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", ctype or "application/json")
    try:
        with urllib.request.urlopen(req, timeout=600) as res:
            text = res.read().decode()
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"{method} {path} respondió {exc.code}: {exc.read().decode()[:300]}") from exc
    return json.loads(text) if text else {}


def upload(path: Path) -> dict:
    boundary = uuid.uuid4().hex
    content = path.read_bytes()
    raw = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\n"
        f"Content-Type: text/markdown\r\n\r\n"
    ).encode() + content + f"\r\n--{boundary}--\r\n".encode()
    return call("POST", "/v1/files/", raw=raw, ctype=f"multipart/form-data; boundary={boundary}")


def text_block(name: str) -> str:
    """El bloque ```text de un archivo de model/ (así el prompt vive versionado en Markdown)."""
    text = (ROOT / "model" / name).read_text(encoding="utf-8")
    match = re.search(r"```text\n(.*?)\n```", text, re.DOTALL)
    if not match:
        raise SystemExit(f"No encontré el bloque ```text en model/{name}")
    return match.group(1).strip()


def configure_rag() -> None:
    call("POST", "/v1/retrieval/embedding/update", {
        "embedding_engine": "ollama",
        "embedding_model": EMBED_MODEL,
        "ollama_config": {"url": OLLAMA_FROM_OPENWEBUI, "key": ""},
    })
    call("POST", "/v1/retrieval/config/update", {
        "chunk": {"text_splitter": "token", "chunk_size": CHUNK_SIZE, "chunk_overlap": CHUNK_OVERLAP},
    })
    # Sin "template", Open WebUI deja la plantilla RAG en None y falla el chat: siempre se envía
    call("POST", "/v1/retrieval/query/settings/update", {
        "k": TOP_K, "hybrid": False, "template": text_block("rag-template.md"),
    })
    tasks = call("GET", "/v1/tasks/config")
    tasks["ENABLE_RETRIEVAL_QUERY_GENERATION"] = QUERY_GENERATION
    call("POST", "/v1/tasks/config/update", tasks)
    config = call("GET", "/v1/retrieval/config")
    chunk = config.get("chunk", {})
    print(f"RAG: {EMBED_MODEL}, splitter={chunk.get('text_splitter')}, "
          f"chunk={chunk.get('chunk_size')}, overlap={chunk.get('chunk_overlap')}, top_k={TOP_K}, "
          f"query_generation={QUERY_GENERATION}")


def build_knowledge() -> dict:
    existing = next((k for k in call("GET", "/v1/knowledge/list") if k["name"] == KNOWLEDGE_NAME), None)
    if existing:
        knowledge = call("POST", f"/v1/knowledge/{existing['id']}/reset")
    else:
        knowledge = call("POST", "/v1/knowledge/create", {
            "name": KNOWLEDGE_NAME,
            "description": "Documentación de uso de RedNexus para el asistente de soporte",
        })
    docs = sorted(p for p in (ROOT / "knowledge-base").glob("*.md") if not p.name.startswith("_"))
    # Borra las copias que dejaron corridas anteriores, para no acumular archivos repetidos
    names = {d.name for d in docs}
    for old in call("GET", "/v1/files/"):
        if old.get("filename") in names:
            call("DELETE", f"/v1/files/{old['id']}")
    for doc in docs:
        file = upload(doc)
        knowledge = call("POST", f"/v1/knowledge/{knowledge['id']}/file/add", {"file_id": file["id"]})
        print(f"  + {doc.name}")
    print(f"Knowledge '{KNOWLEDGE_NAME}': {len(docs)} documentos")
    return knowledge


def upsert_model(knowledge: dict) -> None:
    knowledge_ref = {k: knowledge[k] for k in ("id", "name", "description") if k in knowledge}
    knowledge_ref["type"] = "collection"
    form = {
        "id": MODEL_ID,
        "base_model_id": BASE_MODEL,
        "name": "Asistente RedNexus",
        "meta": {
            "description": "Soporte de RedNexus con RAG sobre la documentación del proyecto",
            "knowledge": [knowledge_ref],
            "capabilities": {"vision": False, "citations": True},
        },
        "params": {**PARAMS, "system": text_block("system-prompt.md")},
        "access_control": None,
        "is_active": True,
    }
    try:
        call("GET", f"/v1/models/model?id={MODEL_ID}")
        call("POST", f"/v1/models/model/update?id={MODEL_ID}", form)
        action = "actualizado"
    except SystemExit:
        call("POST", "/v1/models/create", form)
        action = "creado"
    call("GET", "/models")  # refresca la caché de modelos; sin esto el chat responde "Model not found"
    print(f"Modelo '{MODEL_ID}' {action} sobre {BASE_MODEL} con {PARAMS}")


def main() -> int:
    if not API_KEY:
        print("Falta OPENWEBUI_API_KEY en .env (Open WebUI → Settings → Account → API keys).")
        return 1
    configure_rag()
    upsert_model(build_knowledge())
    return 0


if __name__ == "__main__":
    sys.exit(main())
