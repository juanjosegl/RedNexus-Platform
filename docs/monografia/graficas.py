"""Gráficas de la monografía a partir de los resultados versionados del repo.

Uso: python3 -m pip install matplotlib && python3 docs/monografia/graficas.py
Salida: docs/monografia/img/*.png (se suben al repo; build.py las inserta como figuras)
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

RAIZ = Path(__file__).resolve().parents[2]
IMG = Path(__file__).resolve().parent / "img"
IMG.mkdir(exist_ok=True)

AZUL = "#2a78d6"        # serie
AZUL_OSCURO = "#104281"  # resaltado (la configuración elegida)
TINTA = "#222222"
TINTA_SUAVE = "#666666"
REJILLA = "#e5e5e5"

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 10,
    "axes.edgecolor": TINTA_SUAVE,
    "axes.labelcolor": TINTA,
    "xtick.color": TINTA_SUAVE,
    "ytick.color": TINTA,
})


def barras_h(etiquetas, valores, resaltar, titulo_eje, archivo, formato="{:.2f}", limite=1.0, meta=None):
    fig, ax = plt.subplots(figsize=(7.2, 0.42 * len(etiquetas) + 0.9), dpi=200)
    colores = [AZUL_OSCURO if i in resaltar else AZUL for i in range(len(etiquetas))]
    pos = list(range(len(etiquetas)))[::-1]
    ax.barh(pos, valores, color=colores, height=0.62, edgecolor="white", linewidth=2)
    for y, v in zip(pos, valores):
        ax.text(v + limite * 0.01, y, formato.format(v).replace(".", ","), va="center", fontsize=9, color=TINTA)
    ax.set_yticks(pos)
    ax.set_yticklabels(etiquetas)
    ax.set_xlim(0, limite * 1.08)
    ax.set_xlabel(titulo_eje)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:g}".replace(".", ",")))
    ax.grid(axis="x", color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    if meta is not None:
        ax.axvline(meta, color=TINTA_SUAVE, linestyle="--", linewidth=1)
        ax.text(meta, len(etiquetas) - 0.4, f" meta {formato.format(meta).replace('.', ',')}", fontsize=8, color=TINTA_SUAVE)
    fig.tight_layout()
    fig.savefig(IMG / archivo, facecolor="white")
    plt.close(fig)
    print("ok", archivo)


# 1) precision@3 por configuración del emparejamiento (ml/results/resumen.json)
runs = {r["run"]: r for r in json.loads((RAIZ / "ml/results/resumen.json").read_text())}
ganadora = json.loads((RAIZ / "ml/results/winning-config.json").read_text())
seleccion = [
    ("Respaldo por etiquetas (sin IA)", runs["01-respaldo-etiquetas"]["precision_at_3"]),
    ("nomic-embed-text", runs["02-embedding-nomic-embed-text"]["precision_at_3"]),
    ("all-minilm", runs["02-embedding-all-minilm"]["precision_at_3"]),
    ("paraphrase-multilingual", runs["02-embedding-paraphrase-multilingual"]["precision_at_3"]),
    ("+ clasificación prompt v2", runs["04-clasificacion-prompt-v2-enriquece"]["precision_at_3"]),
    ("+ búsqueda híbrida α = 0,6", runs["04c-hibrido-alpha-0.6"]["precision_at_3"]),
    ("Configuración inicial del backend", ganadora["baseline_backend"]["precision_at_3"]),
    ("Ganadora (umbral 0,25, rednexus-matching v1)", ganadora["metrics"]["precision_at_3"]),
]
barras_h([s[0] for s in seleccion], [s[1] for s in seleccion], {7}, "precision@3 en 100 solicitudes sintéticas", "experimentos-precision.png", meta=0.80)

# 2) asistente RAG: éxito por categoría en la evaluación final (60 casos)
final = next((RAIZ / "asistente-rag/runs").glob("resumen_v4_final_*60casos*.json"))
datos = json.loads(final.read_text())
filas = sorted(((c, v["success_pct"]) for c, v in datos["by_category"].items()), key=lambda x: -x[1])
barras_h([f.replace("_", " ") for f, _ in filas], [v for _, v in filas], set(), "Casos exitosos (%) en la evaluación final (60 casos)", "rag-por-categoria.png", formato="{:.1f}", limite=100, meta=70)
