"""Convierte a PDF los documentos de entrega que se presentan fuera de GitHub.

Uso (desde la raíz de RedNexus-Platform; necesita Google Chrome):
    python3 -m pip install markdown
    python3 docs/entrega/build_pdfs.py          # -> docs/entrega/pdf/*.pdf
"""

import re
import subprocess
import tempfile
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parents[2]
ENTREGA = Path(__file__).resolve().parent
SALIDA = ENTREGA / "pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
REPO = "https://github.com/juanjosegl/RedNexus-Platform/blob/main/"

DOCUMENTOS = {
    "informe-ejecutivo.md": "RedNexus - Informe ejecutivo.pdf",
    "ENTREGABLES.md": "RedNexus - Matriz de entregables.pdf",
    "guion-video.md": "RedNexus - Guion del video.pdf",
    "guion-demo.md": "RedNexus - Guion de la demo y la sustentacion.pdf",
}

ESTILO = """
@page { size: Letter; margin: 2cm 2cm 2cm 2.5cm; }
body { font-family: Arial, sans-serif; font-size: 11pt; line-height: 1.45; color: #111; }
h1 { font-size: 17pt; margin: 0 0 12pt; }
h2 { font-size: 13pt; margin: 16pt 0 6pt; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9pt; page-break-inside: auto; }
th, td { border: 1px solid #999; padding: 3pt 5pt; vertical-align: top; text-align: left; }
th { background: #dde6f3; }
code { font-family: Menlo, Consolas, monospace; font-size: 8.5pt; background: #f2f2f2; padding: 0 2pt; }
pre { background: #f2f2f2; padding: 6pt; font-size: 8.5pt; white-space: pre-wrap; }
blockquote { border-left: 3px solid #999; margin: 6pt 0; padding: 2pt 8pt; color: #333; }
a { color: #1c5cab; text-decoration: none; }
"""


def enlaces_absolutos(html: str, origen: Path) -> str:
    """Los enlaces relativos del repo apuntan a GitHub, para que funcionen en el PDF."""

    def cambiar(m):
        url = m.group(1)
        if url.startswith(("http", "#", "mailto")):
            return m.group(0)
        destino = (origen.parent / url.split("#")[0]).resolve()
        try:
            ruta = destino.relative_to(RAIZ).as_posix()
        except ValueError:
            return m.group(0)
        ancla = "#" + url.split("#", 1)[1] if "#" in url else ""
        tipo = "tree/main/" if destino.is_dir() else "blob/main/"
        return f'href="{REPO.replace("blob/main/", tipo)}{ruta}{ancla}"'

    return re.sub(r'href="([^"]+)"', cambiar, html)


def main():
    SALIDA.mkdir(exist_ok=True)
    for fuente, nombre in DOCUMENTOS.items():
        ruta = ENTREGA / fuente
        cuerpo = markdown.markdown(ruta.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
        html = f'<!doctype html><html lang="es"><meta charset="utf-8"><style>{ESTILO}</style><body>{enlaces_absolutos(cuerpo, ruta)}</body></html>'
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html)
        destino = SALIDA / nombre
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={destino}", tmp.name],
            check=True,
            capture_output=True,
        )
        print("ok", destino.relative_to(RAIZ))


if __name__ == "__main__":
    main()
