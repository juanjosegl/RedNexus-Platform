"""Evalúa el asistente de RedNexus contra el golden dataset.

Basado en el evaluate_rag.py del curso (github.com/FerchoRV/ejemplo-rag-openwebui). Cambios:
  - Lee todos los .jsonl de golden-dataset/ (uno por integrante).
  - El juez califica fidelidad y completitud por separado (1 a 5).
  - Calcula el porcentaje de éxito y de error, por categoría y en total.
  - Guarda el detalle (.jsonl) y un resumen en Markdown listo para el informe.

Configuración por variables de entorno o en un .env (ver .env.example):
  OPENWEBUI_BASE_URL  http://localhost:3001/api
  OPENWEBUI_API_KEY   obligatoria (Open WebUI → Settings → Account → API keys)
  TARGET_MODEL        asistente-rednexus
  JUDGE_MODEL         qwen2.5:7b (vacío = sin juez, solo palabras clave)
  RUN_TAG             nombre de la corrida, p. ej. v1_chunk400_ov60
  LIMIT               opcional: evalúa solo los primeros N casos (para probar)

Uso: python3 evaluate_rag.py
"""

from __future__ import annotations

import json
import os
import re
import statistics
import sys
import time
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from validate_dataset import dataset_files, load_cases  # noqa: E402

load_dotenv(ROOT / ".env")

BASE_URL = os.getenv("OPENWEBUI_BASE_URL", "http://localhost:3001/api")
API_KEY = os.getenv("OPENWEBUI_API_KEY", "")
TARGET_MODEL = os.getenv("TARGET_MODEL", "asistente-rednexus")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "")
RUN_TAG = os.getenv("RUN_TAG", "baseline")
LIMIT = int(os.getenv("LIMIT", "0"))

# Un caso es exitoso si el juez da 4 o más en promedio,
# o si tiene todas las palabras clave y el juez da al menos 3.
JUDGE_PASS = 4.0
JUDGE_PASS_WITH_KEYWORDS = 3.0
TARGET_SUCCESS = 70.0

JUDGE_SYSTEM = """Eres un evaluador estricto de un asistente de soporte de la plataforma RedNexus.
Recibes la pregunta del usuario, el comportamiento esperado, la respuesta esperada y la respuesta real.

Califica de 1 a 5:
- fidelidad: la respuesta real no inventa nada que contradiga o no esté en la respuesta esperada
  (5 = todo es correcto, 1 = inventa o contradice).
- completitud: la respuesta real cubre los puntos clave de la respuesta esperada
  (5 = cubre todo, 1 = no cubre nada).

Si el comportamiento esperado es "rechazar", la mejor respuesta declina con amabilidad, no inventa
información y redirige al uso de RedNexus; en ese caso califica qué tan bien rechaza.

Responde SOLO con JSON: {"fidelidad": <1-5>, "completitud": <1-5>, "motivo": "<una frase>"}"""


def normalize(text: str) -> str:
    """Minúsculas y sin tildes, para comparar palabras clave."""
    plain = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in plain if unicodedata.category(ch) != "Mn")


def check_keywords(answer: str, keywords: list[str]) -> dict[str, bool]:
    text = normalize(answer)
    return {k: normalize(k) in text for k in keywords}


def ask_target(client: OpenAI, prompt: str) -> tuple[str, float, Optional[str]]:
    started = time.perf_counter()
    try:
        res = client.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = (res.choices[0].message.content or "").strip()
        return answer, round(time.perf_counter() - started, 3), None
    except Exception as exc:  # noqa: BLE001 - se registra cualquier fallo de la API
        return "", round(time.perf_counter() - started, 3), f"{type(exc).__name__}: {exc}"


def parse_judge(content: str) -> Optional[dict]:
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        fid, comp = int(data["fidelidad"]), int(data["completitud"])
    except (ValueError, KeyError, TypeError):
        return None
    if not (1 <= fid <= 5 and 1 <= comp <= 5):
        return None
    return {"fidelidad": fid, "completitud": comp, "motivo": str(data.get("motivo", ""))}


def ask_judge(client: OpenAI, case: dict, answer: str) -> Optional[dict]:
    user = (
        f"Pregunta: {case['prompt']}\n"
        f"Comportamiento esperado: {case['behavior']}\n"
        f"Respuesta esperada: {case['expected_answer']}\n"
        f"Respuesta real: {answer}"
    )
    for _ in range(2):  # un reintento si no devuelve JSON válido
        try:
            res = client.chat.completions.create(
                model=JUDGE_MODEL,
                temperature=0.0,
                messages=[{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": user}],
            )
        except Exception as exc:  # noqa: BLE001
            return {"fidelidad": None, "completitud": None, "motivo": f"judge_error: {exc}"}
        parsed = parse_judge(res.choices[0].message.content or "")
        if parsed:
            return parsed
    return None


def is_success(keywords_ok: bool, judge_avg: Optional[float]) -> bool:
    if judge_avg is None:
        return keywords_ok
    return judge_avg >= JUDGE_PASS or (keywords_ok and judge_avg >= JUDGE_PASS_WITH_KEYWORDS)


def evaluate(client: OpenAI, case: dict) -> dict:
    answer, latency, error = ask_target(client, case["prompt"])
    keywords = check_keywords(answer, case["required_keywords"])
    keywords_ok = all(keywords.values())
    judge = ask_judge(client, case, answer) if JUDGE_MODEL and answer else None
    scores = [judge.get("fidelidad"), judge.get("completitud")] if judge else []
    judge_avg = statistics.mean(scores) if scores and None not in scores else None
    return {
        "id": case["id"],
        "category": case["category"],
        "behavior": case["behavior"],
        "prompt": case["prompt"],
        "expected_answer": case["expected_answer"],
        "actual_answer": answer,
        "latency_s": latency,
        "error": error,
        "keywords_check": keywords,
        "keywords_passed": keywords_ok,
        "fidelidad": judge.get("fidelidad") if judge else None,
        "completitud": judge.get("completitud") if judge else None,
        "judge_avg": judge_avg,
        "judge_reason": judge.get("motivo") if judge else None,
        "success": error is None and is_success(keywords_ok, judge_avg),
    }


def pct(part: int, total: int) -> float:
    return round(100 * part / total, 1) if total else 0.0


def mean_or_none(values: list) -> Optional[float]:
    values = [v for v in values if v is not None]
    return round(statistics.mean(values), 2) if values else None


def summarize(results: list[dict]) -> dict:
    ok = [r for r in results if r["error"] is None]
    latencies = [r["latency_s"] for r in ok]
    by_category = defaultdict(list)
    for r in results:
        by_category[r["category"]].append(r)
    return {
        "run_tag": RUN_TAG,
        "target_model": TARGET_MODEL,
        "judge_model": JUDGE_MODEL or None,
        "total": len(results),
        "api_errors": len(results) - len(ok),
        "success": sum(r["success"] for r in results),
        "success_pct": pct(sum(r["success"] for r in results), len(results)),
        "error_pct": round(100 - pct(sum(r["success"] for r in results), len(results)), 1),
        "keywords_pct": pct(sum(r["keywords_passed"] for r in ok), len(ok)),
        "latency_mean_s": round(statistics.mean(latencies), 3) if latencies else None,
        "latency_median_s": round(statistics.median(latencies), 3) if latencies else None,
        "latency_p95_s": round(sorted(latencies)[int(0.95 * (len(latencies) - 1))], 3) if latencies else None,
        "fidelidad_mean": mean_or_none([r["fidelidad"] for r in results]),
        "completitud_mean": mean_or_none([r["completitud"] for r in results]),
        "by_category": {
            cat: {
                "total": len(rs),
                "success_pct": pct(sum(r["success"] for r in rs), len(rs)),
                "fidelidad_mean": mean_or_none([r["fidelidad"] for r in rs]),
                "completitud_mean": mean_or_none([r["completitud"] for r in rs]),
                "latency_mean_s": mean_or_none([r["latency_s"] for r in rs if r["error"] is None]),
            }
            for cat, rs in sorted(by_category.items())
        },
    }


def markdown_report(summary: dict, results: list[dict]) -> str:
    verdict = "CUMPLE" if summary["success_pct"] >= TARGET_SUCCESS else "NO CUMPLE"
    lines = [
        f"# Evaluación `{summary['run_tag']}`",
        "",
        f"- Fecha: {datetime.now():%Y-%m-%d %H:%M}",
        f"- Modelo evaluado: `{summary['target_model']}` · Juez: `{summary['judge_model'] or 'sin juez'}`",
        f"- **Éxito: {summary['success_pct']} %** ({summary['success']}/{summary['total']}) · "
        f"**Error: {summary['error_pct']} %** · Meta {TARGET_SUCCESS:.0f} %: **{verdict}**",
        f"- Palabras clave OK: {summary['keywords_pct']} % · Errores de API: {summary['api_errors']}",
        f"- Latencia: media {summary['latency_mean_s']} s · mediana {summary['latency_median_s']} s · "
        f"p95 {summary['latency_p95_s']} s",
        f"- Juez: fidelidad {summary['fidelidad_mean']} / 5 · completitud {summary['completitud_mean']} / 5",
        "",
        "## Por categoría",
        "",
        "| Categoría | Casos | Éxito | Fidelidad | Completitud | Latencia media (s) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cat, s in summary["by_category"].items():
        lines.append(
            f"| {cat} | {s['total']} | {s['success_pct']} % | {s['fidelidad_mean']} | "
            f"{s['completitud_mean']} | {s['latency_mean_s']} |"
        )
    failed = [r for r in results if not r["success"]]
    lines += ["", f"## Casos fallidos ({len(failed)})", ""]
    for r in failed:
        missing = [k for k, ok in r["keywords_check"].items() if not ok]
        reason = r["error"] or r["judge_reason"] or f"faltan palabras clave: {', '.join(missing)}"
        lines.append(f"- **{r['id']}** ({r['category']}): {reason}")
    return "\n".join(lines) + "\n"


def main() -> int:
    if not API_KEY:
        print("Falta OPENWEBUI_API_KEY (cópiala de Open WebUI → Settings → Account → API keys).")
        return 1
    cases, errors = load_cases(dataset_files())
    if errors:
        print("El dataset tiene errores; corre scripts/validate_dataset.py")
        return 1
    if LIMIT:
        cases = cases[:LIMIT]

    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    print(f"Evaluando {len(cases)} casos con {TARGET_MODEL} (juez: {JUDGE_MODEL or 'ninguno'})\n")
    results = []
    for i, case in enumerate(cases, start=1):
        r = evaluate(client, case)
        results.append(r)
        mark = "OK " if r["success"] else "MAL"
        judge = f"juez={r['judge_avg']}" if r["judge_avg"] is not None else "juez=-"
        print(f"[{i:>2}/{len(cases)}] {mark} {r['id']:<10} {r['latency_s']:>6}s  {judge}")

    runs = ROOT / "runs"
    runs.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    detail = runs / f"eval_{RUN_TAG}_{stamp}.jsonl"
    with detail.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    summary = summarize(results)
    (runs / f"resumen_{RUN_TAG}_{stamp}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = markdown_report(summary, results)
    (runs / f"resumen_{RUN_TAG}_{stamp}.md").write_text(report, encoding="utf-8")

    print("\n" + report)
    print(f"Detalle: {detail.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
