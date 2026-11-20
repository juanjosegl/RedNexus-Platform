"""Une las secciones A a G del informe en docs/Informe-modelo-rag-RedNexus.pdf.

Convierte cada archivo de docs/informe/ de Markdown a HTML y lo imprime a PDF con Google Chrome sin interfaz.

Uso (desde asistente-rag/):
    pip install markdown
    python scripts/build_informe.py [--chrome RUTA_A_CHROME] [--html-only]
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INFORME = ROOT / "docs" / "informe"
OUTPUT = ROOT / "docs" / "Informe-modelo-rag-RedNexus.pdf"
SECTIONS = [
    "C-introduccion.md",
    "D-problema.md",
    "E-definicion-modelo.md",
    "F-pruebas.md",
    "G-conclusiones.md",
]
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium",
    "chromium-browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]

CSS = """
@page { size: Letter; margin: 2.54cm; @top-right { content: counter(page); font: 10pt 'Times New Roman', serif; } }
@page :first { @top-right { content: none; } }
body { font-family: 'Times New Roman', Times, serif; font-size: 12pt; line-height: 1.5; color: #111; }
h1 { font-size: 15pt; text-align: center; margin: 0 0 14pt; break-before: page; }
h2 { font-size: 13pt; margin: 16pt 0 6pt; break-after: avoid; }
h3 { font-size: 12pt; font-style: italic; margin: 12pt 0 4pt; break-after: avoid; }
p { margin: 0 0 8pt; text-align: justify; }
ul, ol { margin: 0 0 8pt; padding-left: 22pt; }
li { margin-bottom: 2pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 12pt; font-size: 9.5pt; line-height: 1.3; break-inside: avoid; }
th, td { border-top: 1px solid #444; border-bottom: 1px solid #444; padding: 4pt 5pt; text-align: left; vertical-align: top; }
th { font-weight: bold; }
code { font-family: Menlo, Consolas, monospace; font-size: 9pt; }
pre { background: #f5f5f5; padding: 8pt; font-size: 8pt; line-height: 1.25; white-space: pre; overflow: hidden; break-inside: avoid; }
pre code { font-size: 8pt; }
img { display: block; max-width: 100%; max-height: 9cm; margin: 8pt auto 4pt; border: 1px solid #ccc; }
p:has(> img) { text-align: center; margin-bottom: 2pt; }
p:has(> img) + p > em:only-child { display: block; text-align: center; font-size: 10pt; }
.portada { text-align: center; padding-top: 4cm; }
.portada .titulo { font-size: 18pt; font-weight: bold; margin-bottom: 18pt; }
.portada p { text-align: center; margin: 0 0 6pt; }
.portada .bloque { margin-top: 28pt; }
.indice h1 { break-before: page; }
.indice ol { list-style: none; padding-left: 0; font-size: 12pt; }
.indice li { margin-bottom: 6pt; }
.indice a { color: #111; text-decoration: none; }
"""


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def portada() -> str:
    """Construye la portada desde A-portada.md (lista de campos)."""
    text = strip_comments((INFORME / "A-portada.md").read_text(encoding="utf-8"))
    fields: dict[str, str] = {}
    members: list[str] = []
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("- ") and ":" in line and not raw.startswith("  "):
            key, value = line[2:].split(":", 1)
            fields[key.strip().lower()] = value.strip()
        elif raw.startswith("  - "):
            members.append(line[2:].strip())
        elif line.startswith("- "):
            lines.append(line[2:].strip())
    esc = html.escape
    parts = [
        '<section class="portada">',
        f'<p class="titulo">{esc(fields.get("título", "Informe del modelo RAG"))}</p>',
        *[f"<p>{esc(line)}</p>" for line in lines],
        '<div class="bloque">',
        f'<p><strong>Docente:</strong> {esc(fields.get("docente", ""))}</p>',
        "<p><strong>Integrantes:</strong></p>",
        *[f"<p>{esc(m)}</p>" for m in members],
        "</div>",
        f'<p class="bloque">{esc(fields.get("ciudad y fecha", ""))}</p>',
        "</section>",
    ]
    return "\n".join(parts)


def indice(titles: list[tuple[str, str]]) -> str:
    items = "".join(f'<li><a href="#{anchor}">{html.escape(title)}</a></li>' for anchor, title in titles)
    return f'<section class="indice"><h1>Índice</h1><ol>{items}</ol></section>'


def render_sections() -> tuple[str, list[tuple[str, str]]]:
    import markdown

    body: list[str] = []
    titles: list[tuple[str, str]] = []
    for name in SECTIONS:
        text = strip_comments((INFORME / name).read_text(encoding="utf-8"))
        anchor = name.split("-", 1)[0].lower()
        first = next((l for l in text.splitlines() if l.startswith("# ")), name)
        title = first.lstrip("# ").strip()
        titles.append((anchor, title))
        rendered = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
        rendered = rendered.replace("<h1>", f'<h1 id="{anchor}">', 1)
        body.append(f"<section>{rendered}</section>")
    return "\n".join(body), titles


def build_html() -> str:
    sections, titles = render_sections()
    base = INFORME.as_uri() + "/"
    return (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        f"<base href='{base}'><title>Informe del modelo RAG — RedNexus</title>"
        f"<style>{CSS}</style></head><body>"
        f"{portada()}{indice(titles)}{sections}</body></html>"
    )


def find_chrome(explicit: str | None) -> str:
    for candidate in [explicit] if explicit else CHROME_CANDIDATES:
        if candidate and (Path(candidate).exists() or shutil.which(candidate)):
            return candidate
    sys.exit("No se encontró Google Chrome; pasa la ruta con --chrome.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--chrome", help="ruta al ejecutable de Chrome o Chromium")
    parser.add_argument("--html-only", action="store_true", help="solo escribe el HTML intermedio")
    args = parser.parse_args()

    page = build_html()
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "informe.html"
        html_path.write_text(page, encoding="utf-8")
        if args.html_only:
            target = OUTPUT.with_suffix(".html")
            target.write_text(page, encoding="utf-8")
            print(f"HTML: {target}")
            return
        chrome = find_chrome(args.chrome)
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--user-data-dir={Path(tmp) / 'perfil'}",
                "--allow-file-access-from-files",
                f"--print-to-pdf={OUTPUT}",
                html_path.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    print(f"PDF: {OUTPUT}")


if __name__ == "__main__":
    main()
