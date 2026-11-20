"""Experimentos de emparejamiento de RedNexus en MLflow (IA-07).

Compara, sobre el dataset sintético (ml/data), las decisiones del emparejamiento:
  1. Respaldo por etiquetas (lo que usa el backend si la IA no responde): línea base.
  2. Modelo de embeddings: nomic-embed-text, all-minilm y paraphrase-multilingual.
  3. Prefijos de tarea de nomic-embed-text (search_query / search_document).
  4. Con o sin clasificación previa por el LLM (prompt v1 vs. v2, enriquecer la consulta o premiar
     el área) y búsqueda híbrida (embedding + coincidencia de palabras).
  5. Peso entre similitud y calificación (SIMILARITY_WEIGHT del backend).
  6. Umbral de similitud mínima (MIN_SIMILARITY), con 10 dudas fuera de tema.
  7. Afirmaciones no soportadas en las explicaciones del LLM, prompts v1, v2 y v3 (juez qwen2.5:7b).
Al final registra la configuración ganadora como modelo `rednexus-matching` en el registro de
MLflow y la escribe en results/winning-config.json, que es lo que se aplica en el backend.

Uso (desde ml/, con Ollama corriendo):
    uv run python run_experiments.py            # todo
    uv run python run_experiments.py --skip-judge   # sin el juez de explicaciones (más rápido)
    uv sync --group ui && uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000   # ver los runs
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
from datetime import datetime, timezone

import mlflow
import numpy as np
from mlflow.tracking import MlflowClient

from rednexus_ml import (
    EXPLAIN_SYSTEM,
    EXPLAIN_SYSTEM_V1,
    EXPLAIN_SYSTEM_V2,
    CLASSIFY_SYSTEM,
    CLASSIFY_SYSTEM_V1,
    ROOT,
    Profile,
    Request,
    chat,
    classify,
    embed,
    explain,
    load_data,
    metrics,
    rank,
    tag_similarity,
)

EXPERIMENT = "rednexus-emparejamiento"
RESULTS = ROOT / "results"
EMBED_MODELS = ["nomic-embed-text", "all-minilm", "paraphrase-multilingual"]
LLM = "qwen2.5:3b"
JUDGE = "qwen2.5:7b"
# configuración que tiene hoy el backend (src/modules/matching/ranking.ts)
BACKEND_WEIGHT = 0.8
BACKEND_MIN_SIMILARITY = 0.15

summary: list[dict] = []


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "desconocido"


def log_run(name: str, params: dict, results: list[tuple[Request, list[str]]], extra: dict | None = None, tags: dict | None = None) -> dict:
    m = metrics(results)
    m.update(extra or {})
    with mlflow.start_run(run_name=name):
        mlflow.set_tags({"dataset": "sintetico-v1", "git_sha": git_sha(), **(tags or {})})
        mlflow.log_params(params)
        mlflow.log_metrics(m)
        mlflow.log_dict(
            [{"request": r.id, "text": r.text, "relevant": r.relevant, "top3": top, "hit": bool(set(r.relevant) & set(top))} for r, top in results],
            "predicciones.json",
        )
    row = {"run": name, **params, **{k: round(v, 4) for k, v in m.items()}}
    summary.append(row)
    print(f"{name:42s} p@3={m['precision_at_3']:.2f} hit@1={m['hit_at_1']:.2f} mrr={m['mrr']:.3f} cobertura={m['coverage']:.2f}")
    return m


def similarity_matrix(model: str, profiles: list[Profile], texts: list[str], prefix: bool = False) -> tuple[np.ndarray, float]:
    doc = [("search_document: " if prefix else "") + p.text for p in profiles]
    qry = [("search_query: " if prefix else "") + t for t in texts]
    P, _ = embed(model, doc)
    Q, ms = embed(model, qry)
    return Q @ P.T, ms


def evaluate(sims: np.ndarray, profiles, reqs, weight=1.0, min_sim=0.0, boost=None, pool_by=None):
    return [
        (r, rank(sims[i], profiles, weight, min_sim, boost=None if boost is None else boost[i], pool_by=None if pool_by is None else pool_by[i]))
        for i, r in enumerate(reqs)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--judge-sample", type=int, default=30)
    args = parser.parse_args()

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", f"sqlite:///{ROOT / 'mlflow.db'}"))
    mlflow.set_experiment(EXPERIMENT)
    profiles, reqs = load_data()
    off_topic = json.loads((ROOT / "data" / "off_topic.json").read_text(encoding="utf-8"))
    texts = [r.text for r in reqs]
    print(f"Dataset: {len(profiles)} perfiles, {len(reqs)} solicitudes, {len(off_topic)} fuera de tema\n")

    # 1. línea base: respaldo por etiquetas
    tag_sims = np.array([tag_similarity(t, profiles) for t in texts])
    log_run("01-respaldo-etiquetas", {"embedding": "ninguno (etiquetas)", "weight": 1.0, "min_similarity": 0.01, "classification": "no"}, evaluate(tag_sims, profiles, reqs, min_sim=0.01))
    log_run("01b-respaldo-etiquetas-con-calificacion", {"embedding": "ninguno (etiquetas)", "weight": BACKEND_WEIGHT, "min_similarity": 0.01, "classification": "no"}, evaluate(tag_sims, profiles, reqs, BACKEND_WEIGHT, 0.01))

    # 2 y 3. modelos de embeddings (solo similitud) y prefijos de nomic
    candidates: dict[str, tuple[np.ndarray, float, dict]] = {}
    for model in EMBED_MODELS:
        sims, ms = similarity_matrix(model, profiles, texts)
        m = log_run(f"02-embedding-{model}", {"embedding": model, "prefix": "no", "weight": 1.0, "min_similarity": 0.0, "classification": "no"}, evaluate(sims, profiles, reqs), {"embed_ms_per_text": ms})
        candidates[model] = (sims, ms, m)
    sims, ms = similarity_matrix("nomic-embed-text", profiles, texts, prefix=True)
    m = log_run("03-embedding-nomic-con-prefijos", {"embedding": "nomic-embed-text", "prefix": "search_query/search_document", "weight": 1.0, "min_similarity": 0.0, "classification": "no"}, evaluate(sims, profiles, reqs), {"embed_ms_per_text": ms})
    candidates["nomic-embed-text+prefijos"] = (sims, ms, m)

    best_name = max(candidates, key=lambda k: (candidates[k][2]["precision_at_3"], candidates[k][2]["mrr"]))
    best_sims = candidates[best_name][0]
    best_model = best_name.split("+")[0]
    best_prefix = best_name.endswith("+prefijos")
    print(f"\nMejor embedding: {best_name}\n")

    # 4. clasificación previa con el LLM: prompt v1 (8 áreas, el del backend) contra v2 (todas)
    def run_classification(system: str, label: str):
        classes, times = [], []
        for r in reqs:
            c, t = classify(LLM, r.text, system)
            classes.append(c)
            times.append(t)
        acc = sum(1 for r, c in zip(reqs, classes) if c and c["area"] == r.area) / len(reqs)
        print(f"Clasificación {LLM} {label}: área correcta {acc:.0%}, {statistics.median(times):.0f} ms (mediana)")
        enriched = [r.text + (f"\nÁrea: {c['area']}. Temas: {', '.join(c['topics'])}" if c else "") for r, c in zip(reqs, classes)]
        sims, _ = similarity_matrix(best_model, profiles, enriched, prefix=best_prefix)
        extra = {"classification_area_accuracy": acc, "classification_valid": sum(1 for c in classes if c) / len(reqs), "classification_ms_median": statistics.median(times)}
        return classes, enriched, sims, extra

    _, _, sims_v1, extra_v1 = run_classification(CLASSIFY_SYSTEM_V1, "prompt v1")
    log_run("04a-clasificacion-prompt-v1-enriquece", {"embedding": best_name, "weight": 1.0, "min_similarity": 0.0, "classification": f"{LLM} prompt v1 (8 áreas)"}, evaluate(sims_v1, profiles, reqs), extra_v1)
    classes, enriched, sims_cls, cls_extra = run_classification(CLASSIFY_SYSTEM, "prompt v2")
    m_enriched = log_run("04-clasificacion-prompt-v2-enriquece", {"embedding": best_name, "weight": 1.0, "min_similarity": 0.0, "classification": f"{LLM} prompt v2: área y temas en la consulta"}, evaluate(sims_cls, profiles, reqs), cls_extra)
    boost = np.array([[0.05 if c and c["area"] in p.tags else 0.0 for p in profiles] for c in classes])
    m_boost = log_run("04b-clasificacion-premia-area", {"embedding": best_name, "weight": 1.0, "min_similarity": 0.0, "classification": f"{LLM} prompt v2: +0.05 si el área está en las etiquetas"}, evaluate(best_sims, profiles, reqs, boost=boost), cls_extra)
    base_m = candidates[best_name][2]
    use_cls = None
    if max(m_enriched["precision_at_3"], m_boost["precision_at_3"]) > base_m["precision_at_3"]:
        use_cls = "enriquecer" if m_enriched["precision_at_3"] >= m_boost["precision_at_3"] else "premiar-area"
    final_sims = sims_cls if use_cls == "enriquecer" else best_sims
    final_boost = boost if use_cls == "premiar-area" else None
    pool_by = final_sims

    # 4c. búsqueda híbrida: embedding + coincidencia de palabras (la que usa el respaldo), sobre los
    # 10 más cercanos por embedding. alpha = peso del embedding
    lexical = np.array([tag_similarity(t, profiles) for t in (enriched if use_cls == "enriquecer" else texts)])
    best_alpha, best_alpha_m = 1.0, metrics(evaluate(final_sims, profiles, reqs, 1.0, 0.0, final_boost))
    for alpha in [0.8, 0.7, 0.6, 0.5]:
        blend = alpha * final_sims + (1 - alpha) * lexical
        m = log_run(f"04c-hibrido-alpha-{alpha:.1f}", {"embedding": best_name, "hybrid_alpha": alpha, "weight": 1.0, "min_similarity": 0.0, "classification": use_cls or "no"}, evaluate(blend, profiles, reqs, 1.0, 0.0, final_boost, pool_by))
        if (m["precision_at_3"], m["mrr"]) > (best_alpha_m["precision_at_3"], best_alpha_m["mrr"]):
            best_alpha, best_alpha_m = alpha, m
    if best_alpha < 1.0:
        final_sims = best_alpha * final_sims + (1 - best_alpha) * lexical
    print(f"Híbrido: alpha={best_alpha}")

    # 5. peso entre similitud y calificación
    by_weight = {}
    for w in [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]:
        by_weight[w] = log_run(f"05-peso-{w:.1f}", {"embedding": best_name, "weight": w, "min_similarity": 0.0, "classification": use_cls or "no"}, evaluate(final_sims, profiles, reqs, w, 0.0, final_boost, pool_by))
    # el peso más bajo que no pierde precisión frente al mejor (las calificaciones sí cuentan)
    top_p3 = max(v["precision_at_3"] for v in by_weight.values())
    best_weight = min((w for w, v in by_weight.items() if v["precision_at_3"] >= top_p3 - 0.01 and v["mrr"] >= by_weight[1.0]["mrr"] - 0.02), default=1.0)

    # 6. umbral de similitud mínima: distribución de similitudes y dudas fuera de tema
    off_sims, _ = similarity_matrix(best_model, profiles, [o["text"] for o in off_topic], prefix=best_prefix)
    off_max_pure = off_sims.max(axis=1)
    if best_alpha < 1.0:
        off_sims = best_alpha * off_sims + (1 - best_alpha) * np.array([tag_similarity(o["text"], profiles) for o in off_topic])
    best_correct = [max(final_sims[i][[p.id for p in profiles].index(rid)] for rid in r.relevant) for i, r in enumerate(reqs)]
    off_max = off_sims.max(axis=1)
    print(f"Similitud del ayudante correcto: p10={np.percentile(best_correct, 10):.3f} mediana={np.median(best_correct):.3f}; fuera de tema máx={off_max.max():.3f} mediana={np.median(off_max):.3f}")
    thresholds = sorted({0.0, 0.10, BACKEND_MIN_SIMILARITY, 0.20, 0.25, *[round(x, 2) for x in np.arange(0.30, 0.76, 0.05)]})
    best_threshold, best_balance = 0.0, -1.0
    for th in thresholds:
        rejected = float(np.mean(off_max < th))
        res = evaluate(final_sims, profiles, reqs, best_weight, th, final_boost, pool_by)
        m = log_run(f"06-umbral-{th:.2f}", {"embedding": best_name, "weight": best_weight, "min_similarity": th, "classification": use_cls or "no"}, res, {"off_topic_rejected": rejected})
        # se busca rechazar lo fuera de tema sin perder solicitudes válidas
        balance = m["precision_at_3"] * m["coverage"] + 0.5 * rejected
        if m["coverage"] >= 0.97 and balance > best_balance:
            best_threshold, best_balance = th, balance

    # configuración actual del backend con el mejor embedding, para comparar
    backend_now = log_run("07-config-actual-backend", {"embedding": best_name, "weight": BACKEND_WEIGHT, "min_similarity": BACKEND_MIN_SIMILARITY, "classification": "no"}, evaluate(best_sims, profiles, reqs, BACKEND_WEIGHT, BACKEND_MIN_SIMILARITY), {"off_topic_rejected": float(np.mean(off_max_pure < BACKEND_MIN_SIMILARITY))})

    # 7. explicaciones: ¿el LLM inventa habilidades?
    winner_res = evaluate(final_sims, profiles, reqs, best_weight, best_threshold, final_boost, pool_by)
    judge_extra = {}
    explain_prompt = "v2"
    if not args.skip_judge:
        judged = {}
        for label, system in [("v1", EXPLAIN_SYSTEM_V1), ("v2", EXPLAIN_SYSTEM_V2), ("v3", EXPLAIN_SYSTEM)]:
            judged[label] = judge_explanations(winner_res, profiles, args.judge_sample, system, label)
            log_run(f"07-explicaciones-prompt-{label}", {"llm": LLM, "judge": JUDGE, "explain_prompt": label}, winner_res, judged[label])
        explain_prompt = min(judged, key=lambda k: judged[k]["explanations_unsupported_rate"])
        judge_extra = judged[explain_prompt]

    # configuración ganadora
    winner = {
        "version": datetime.now(timezone.utc).strftime("%Y%m%d"),
        "embedding_model": best_model,
        "embedding_prefixes": best_prefix,
        "similarity_weight": best_weight,
        "min_similarity": best_threshold,
        "classification": use_cls or "solo-metadatos",
        "classification_prompt": "v2",
        "hybrid_alpha": best_alpha,
        "explain_prompt": explain_prompt,
        "llm": LLM,
    }
    final_m = log_run("08-configuracion-ganadora", {k: str(v) for k, v in winner.items()}, winner_res, {"off_topic_rejected": float(np.mean(off_max < best_threshold)), **judge_extra}, tags={"ganadora": "si"})
    winner["metrics"] = {k: round(v, 4) for k, v in final_m.items()}
    winner["baseline_backend"] = {k: round(v, 4) for k, v in backend_now.items()}
    version = register_winner(winner)
    winner["mlflow_model"] = f"models:/rednexus-matching/{version}"

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "winning-config.json").write_text(json.dumps(winner, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (RESULTS / "resumen.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\nGanadora:", json.dumps(winner, ensure_ascii=False, indent=2))


def judge_explanations(results, profiles: list[Profile], sample: int, explain_system: str, label: str) -> dict:
    by_id = {p.id: p for p in profiles}
    picked = [(r, top) for r, top in results if top][:sample]
    rows, unsupported, ms = [], 0, []
    judge_system = (
        "Eres un evaluador estricto pero justo. Recibes el PERFIL de un estudiante (con su nombre) y una EXPLICACIÓN "
        "de por qué puede ayudar con una duda. Responde SOLO JSON "
        "{\"inventa\": true|false, \"afirmaciones_no_soportadas\": [\"...\"]}.\n"
        "inventa = true SOLO si la explicación le atribuye una habilidad, un tema, un título, un cargo o una experiencia "
        "concreta que NO aparece en el perfil (por ejemplo, decir que es experta o monitora de algo que el perfil no dice, "
        "o que sabe de un tema que el perfil no menciona).\n"
        "NO es inventar: usar su nombre, decir que puede ayudar con la duda cuando el perfil sí trata ese tema, resumir o "
        "usar sinónimos de lo que el perfil dice, o decir que el perfil no menciona el tema."
    )
    schema = {"type": "object", "properties": {"inventa": {"type": "boolean"}, "afirmaciones_no_soportadas": {"type": "array", "items": {"type": "string"}}}, "required": ["inventa", "afirmaciones_no_soportadas"]}
    # primero todas las explicaciones (3b) y luego todos los juicios (7b): en 8 GB no caben los dos
    # modelos a la vez y alternarlos obliga a recargarlos en cada caso
    explained = []
    for r, top in picked:
        p = by_id[top[0]]
        text, t = explain(LLM, r.text, p, explain_system)
        ms.append(t)
        explained.append((r, p, text))
    for r, p, text in explained:
        verdict, _ = chat(JUDGE, judge_system, f"PERFIL:\nNombre: {p.name}\nDescripción: {p.bio}\nEtiquetas: {', '.join(p.tags)}\n\nEXPLICACIÓN:\n{text}", schema)
        try:
            v = json.loads(verdict)
        except ValueError:
            v = {"inventa": False, "afirmaciones_no_soportadas": ["(el juez no devolvió JSON)"]}
        unsupported += bool(v.get("inventa"))
        rows.append({"request": r.text, "helper": p.name, "explicacion": text, **v})
    rate = unsupported / len(picked)
    print(f"Explicaciones prompt {label}: {unsupported}/{len(picked)} con afirmaciones no soportadas ({rate:.0%}), {statistics.median(ms):.0f} ms (mediana)")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"explicaciones-{label}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"explanations_unsupported_rate": rate, "explanations_judged": float(len(picked)), "explain_ms_median": statistics.median(ms)}


def register_winner(winner: dict) -> str:
    """Registra la configuración ganadora como una versión del modelo `rednexus-matching`.

    La "versión desplegable" del emparejamiento es su configuración (modelo de embeddings, pesos,
    umbral): se guarda como artefacto del run ganador y se registra en el Model Registry, así el
    backend puede decir qué versión usa (MATCH_CONFIG_VERSION) y se puede volver a una anterior.
    """
    client = MlflowClient()
    run = mlflow.search_runs(
        filter_string="tags.ganadora = 'si'",
        order_by=["attributes.start_time DESC"],
        max_results=1,
        output_format="list",
    )[0]
    run_id = run.info.run_id
    with mlflow.start_run(run_id=run_id):
        mlflow.log_dict(winner, "matching-config/winning-config.json")
    try:
        client.create_registered_model("rednexus-matching", description="Configuración del emparejamiento de RedNexus elegida con IA-07")
    except Exception:
        pass  # ya existe
    mv = client.create_model_version("rednexus-matching", source=f"{run.info.artifact_uri}/matching-config", run_id=run_id)
    client.set_model_version_tag("rednexus-matching", mv.version, "precision_at_3", str(winner["metrics"]["precision_at_3"]))
    print(f"Registrado rednexus-matching versión {mv.version}")
    return str(mv.version)


if __name__ == "__main__":
    main()
