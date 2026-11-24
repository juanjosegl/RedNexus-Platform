"""Mide TTFT (tiempo al primer token) y TPS (tokens por segundo) de los modelos de Ollama.

Uso:  python asistente-rag/scripts/medir_tps_ttft.py [--modelo qwen2.5:3b] [--repeticiones 3]

Envía las mismas preguntas que recibe el asistente y el clasificador, con streaming, y anota:
- TTFT: segundos desde la petición hasta el primer fragmento de texto (lo que el usuario espera).
- TPS: eval_count / eval_duration que reporta Ollama (velocidad de generación).
- Carga del prompt: prompt_eval_count / prompt_eval_duration.
Escribe un CSV y un resumen en Markdown en asistente-rag/runs/.
"""

import argparse
import csv
import json
import statistics
import time
import urllib.request
from datetime import datetime
from pathlib import Path

OLLAMA = "http://localhost:11434"
PREGUNTAS = [
    "¿Cómo califico a la persona que me ayudó?",
    "¿Qué pasa si nadie acepta mi solicitud?",
    "¿Puedo pedir ayuda con una nota de voz?",
    "Clasifica esta duda en área, temas y nivel: no entiendo cómo unir tres tablas con una intermedia",
    "Explica en una frase por qué Ana, que sabe de joins y modelado relacional, puede ayudar con SQL",
    "¿Cómo descargo o elimino mis datos personales?",
]


def medir(modelo: str, pregunta: str) -> dict:
    cuerpo = json.dumps(
        {"model": modelo, "messages": [{"role": "user", "content": pregunta}], "stream": True}
    ).encode()
    req = urllib.request.Request(
        f"{OLLAMA}/api/chat", data=cuerpo, headers={"Content-Type": "application/json"}
    )
    inicio = time.perf_counter()
    ttft = None
    final = {}
    with urllib.request.urlopen(req, timeout=300) as resp:
        for linea in resp:
            dato = json.loads(linea)
            if ttft is None and dato.get("message", {}).get("content"):
                ttft = time.perf_counter() - inicio
            if dato.get("done"):
                final = dato
    total = time.perf_counter() - inicio
    eval_s = final.get("eval_duration", 0) / 1e9
    prompt_s = final.get("prompt_eval_duration", 0) / 1e9
    return {
        "modelo": modelo,
        "pregunta": pregunta,
        "ttft_s": round(ttft or total, 3),
        "total_s": round(total, 3),
        "tokens_salida": final.get("eval_count", 0),
        "tps": round(final.get("eval_count", 0) / eval_s, 2) if eval_s else 0,
        "tokens_prompt": final.get("prompt_eval_count", 0),
        "tps_prompt": round(final.get("prompt_eval_count", 0) / prompt_s, 2) if prompt_s else 0,
        "carga_modelo_s": round(final.get("load_duration", 0) / 1e9, 3),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="qwen2.5:3b")
    ap.add_argument("--repeticiones", type=int, default=3)
    args = ap.parse_args()

    medir(args.modelo, "Hola")  # calentamiento: carga el modelo en memoria
    filas = [medir(args.modelo, p) for _ in range(args.repeticiones) for p in PREGUNTAS]

    runs = Path(__file__).resolve().parent.parent / "runs"
    runs.mkdir(exist_ok=True)
    sello = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = f"tps_ttft_{args.modelo.replace(':', '-')}_{sello}"
    with open(runs / f"{nombre}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)

    def p(campo: str, q: float) -> float:
        valores = sorted(r[campo] for r in filas)
        return valores[min(len(valores) - 1, int(q * len(valores)))]

    resumen = [
        f"# TTFT y TPS de `{args.modelo}` ({datetime.now():%Y-%m-%d %H:%M})",
        "",
        f"{len(filas)} llamadas ({len(PREGUNTAS)} preguntas × {args.repeticiones}), Ollama local, modelo ya cargado en memoria.",
        "",
        "| Métrica | Mediana | p90 |",
        "| --- | --- | --- |",
        f"| TTFT (s) | {statistics.median(r['ttft_s'] for r in filas):.2f} | {p('ttft_s', 0.9):.2f} |",
        f"| TPS de generación (tokens/s) | {statistics.median(r['tps'] for r in filas):.1f} | {p('tps', 0.9):.1f} |",
        f"| TPS de lectura del prompt (tokens/s) | {statistics.median(r['tps_prompt'] for r in filas):.1f} | {p('tps_prompt', 0.9):.1f} |",
        f"| Tokens de salida | {statistics.median(r['tokens_salida'] for r in filas):.0f} | {p('tokens_salida', 0.9):.0f} |",
        f"| Tiempo total (s) | {statistics.median(r['total_s'] for r in filas):.2f} | {p('total_s', 0.9):.2f} |",
    ]
    (runs / f"{nombre}.md").write_text("\n".join(resumen) + "\n", encoding="utf-8")
    print("\n".join(resumen))


if __name__ == "__main__":
    main()
