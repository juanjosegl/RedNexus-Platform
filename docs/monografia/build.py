"""Genera la monografía de RedNexus en Word (.docx) desde los capítulos en Markdown.

Uso (desde la raíz de RedNexus-Platform):
    python3 -m pip install python-docx pillow
    python3 docs/monografia/build.py            # -> docs/monografia/Monografia-RedNexus.docx

Formato pedido por el docente (Detalles generales de la monografía):
- Tamaño carta, Arial 12, redacción impersonal, extranjerismos en cursiva.
- Cubierta y portada sin número pero contadas: la numeración empieza en 3 desde el contenido,
  centrada y a 2 cm del borde inferior.
- Índice de contenido hasta nivel 3, lista de tablas y lista de figuras.
Márgenes de la NTC 1486: superior e izquierdo 3 cm, derecho 2 cm, inferior 3 cm; interlineado 1,5.

Markdown que entiende (subconjunto):
    # Título de nivel 1 (empieza en página nueva)      ## nivel 2      ### nivel 3
    párrafos con **negrita**, *cursiva* y `código`
    - viñetas      1. numeradas      > párrafo destacado (sangría)
    Tabla: Título de la tabla          (línea antes de una tabla con |)
    ![Título de la figura](ruta/relativa/a/la/raiz.png)
    Nota: texto                         (después de una tabla o figura)
Al abrir el .docx, Word pregunta si actualiza los campos: responder "Sí" llena los números
de página del índice y de las listas.
"""

from __future__ import annotations

import io
import re
import struct
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "Monografia-RedNexus.docx"
CAPITULOS = sorted((AQUI / "capitulos").glob("*.md"))

FUENTE = "Arial"
ANCHO_UTIL_CM = 21.59 - 3 - 2  # carta menos márgenes izquierdo y derecho

META = {
    "titulo": "REDNEXUS: RED DE APOYO ACADÉMICO ENTRE PARES CON INTELIGENCIA ARTIFICIAL LOCAL Y ARQUITECTURA NATIVA DE LA NUBE",
    "autores": [
        "JUAN JOSÉ GUTIÉRREZ LASSO",
        "VICTOR DANIEL FERNÁNDEZ",
        "JOSÉ SEBASTIÁN FERNÁNDEZ",
        "MARÍA PAULA ANDRADE MUÑOZ",
        "MARÍA ALEJANDRA GUZMÁN RUIZ",
    ],
    "modalidad": "Monografía presentada como trabajo de grado en la modalidad de diplomado\npara optar al título de Ingeniero de Sistemas",
    "diplomado": "Diplomado CloudForge AI 5.0",
    "docente": "Mg. DIEGO FERNANDO RIVERA VÁSQUEZ",
    "institucion": "CORPORACIÓN UNIVERSITARIA COMFACAUCA – UNICOMFACAUCA",
    "facultad": "FACULTAD DE INGENIERÍA",
    "programa": "PROGRAMA DE INGENIERÍA DE SISTEMAS",
    "lugar_fecha": "POPAYÁN, CAUCA\n2026",
}


# ---------------------------------------------------------------- utilidades de formato

def fijar_fuente(run, tam=12, negrita=None, cursiva=None, mono=False):
    nombre = "Courier New" if mono else FUENTE
    run.font.name = nombre
    run.font.size = Pt(tam)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(atributo), nombre)
    if negrita is not None:
        run.bold = negrita
    if cursiva is not None:
        run.italic = cursiva


def formato_parrafo(p, alineacion=WD_ALIGN_PARAGRAPH.JUSTIFY, antes=0, despues=6, sangria=None, interlineado=1.5):
    pf = p.paragraph_format
    pf.alignment = alineacion
    pf.space_before = Pt(antes)
    pf.space_after = Pt(despues)
    pf.line_spacing = interlineado
    if sangria is not None:
        pf.left_indent = Cm(sangria)


INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


def agregar_texto(p, texto, tam=12, negrita_base=False, cursiva_base=False):
    for trozo in INLINE.split(texto):
        if not trozo:
            continue
        if trozo.startswith("**") and trozo.endswith("**"):
            run = p.add_run(trozo[2:-2])
            fijar_fuente(run, tam, negrita=True, cursiva=cursiva_base)
        elif trozo.startswith("`") and trozo.endswith("`"):
            run = p.add_run(trozo[1:-1])
            fijar_fuente(run, tam - 1, negrita=negrita_base, mono=True)
        elif trozo.startswith("*") and trozo.endswith("*") and len(trozo) > 2:
            run = p.add_run(trozo[1:-1])
            fijar_fuente(run, tam, negrita=negrita_base, cursiva=True)
        else:
            run = p.add_run(trozo)
            fijar_fuente(run, tam, negrita=negrita_base, cursiva=cursiva_base)


def plano(texto: str) -> str:
    return re.sub(r"\*\*|\*|`", "", texto)


def campo(p, instruccion, resultado="", tam=12, negrita=False):
    """Inserta un campo de Word (TOC, SEQ, PAGE) con un resultado precalculado."""
    def fld(tipo):
        r = p.add_run()
        fijar_fuente(r, tam, negrita=negrita)
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), tipo)
        r._element.append(el)
        return r

    fld("begin")
    r = p.add_run()
    fijar_fuente(r, tam, negrita=negrita)
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {instruccion} "
    r._element.append(instr)
    fld("separate")
    if resultado:
        r = p.add_run(resultado)
        fijar_fuente(r, tam, negrita=negrita)
    fld("end")


def sombrear(celda, color="D9E2F3"):
    tcpr = celda._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcpr.append(shd)


def tam_png(ruta: Path):
    with open(ruta, "rb") as f:
        cabecera = f.read(24)
    return struct.unpack(">II", cabecera[16:24])


def comprimir(ruta: Path):
    """Reduce el peso de las imágenes (python3 -m pip install pillow); sin Pillow usa el original.
    Capturas de pantalla a JPEG de 1280 px; diagramas y gráficas a PNG de 1600 px."""
    try:
        from PIL import Image
    except ImportError:
        return str(ruta)
    img = Image.open(ruta)
    captura = "evidencias" in ruta.parts
    maximo = 1280 if captura else 1600
    if captura and img.height > img.width * 1.3:
        img = img.crop((0, 0, img.width, round(img.width * 1.3)))  # se conserva la parte de arriba
    if img.width > maximo:
        img = img.resize((maximo, round(img.height * maximo / img.width)), Image.LANCZOS)
    salida = io.BytesIO()
    if captura:
        img.convert("RGB").save(salida, "JPEG", quality=72, optimize=True)
    else:
        img.save(salida, "PNG", optimize=True)
    salida.seek(0)
    return salida


# ---------------------------------------------------------------- documento

class Monografia:
    def __init__(self):
        self.doc = Document()
        self.n_tabla = 0
        self.n_figura = 0
        self.titulos: list[tuple[int, str]] = []
        self.tablas: list[str] = []
        self.figuras: list[str] = []
        self._estilos()

    def _estilos(self):
        estilos = self.doc.styles
        normal = estilos["Normal"]
        normal.font.name = FUENTE
        normal.font.size = Pt(12)
        normal.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
        normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        for nivel, tam in ((1, 12), (2, 12), (3, 12)):
            e = estilos[f"Heading {nivel}"]
            e.font.name = FUENTE
            e.font.size = Pt(tam)
            e.font.bold = True
            e.font.italic = False
            e.font.color.rgb = RGBColor(0, 0, 0)
            rpr = e.element.get_or_add_rPr()
            rfonts = rpr.find(qn("w:rFonts"))
            if rfonts is None:
                rfonts = OxmlElement("w:rFonts")
                rpr.insert(0, rfonts)
            for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
                rfonts.set(qn(atributo), FUENTE)
            for tema in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
                if rfonts.get(qn(tema)) is not None:
                    del rfonts.attrib[qn(tema)]
            pf = e.paragraph_format
            pf.space_before = Pt(18 if nivel == 1 else 12)
            pf.space_after = Pt(12 if nivel == 1 else 6)
            pf.keep_with_next = True
            pf.line_spacing = 1.5
            pf.alignment = WD_ALIGN_PARAGRAPH.CENTER if nivel == 1 else WD_ALIGN_PARAGRAPH.LEFT
        cap = estilos["Caption"]
        cap.font.name = FUENTE
        cap.font.size = Pt(11)
        cap.font.color.rgb = RGBColor(0, 0, 0)
        cap.font.bold = False
        cap.font.italic = False

        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
        sec.top_margin = Cm(3)
        sec.bottom_margin = Cm(3)
        sec.left_margin = Cm(3)
        sec.right_margin = Cm(2)
        sec.footer_distance = Cm(2)
        sec.header_distance = Cm(1.5)

        # Word actualiza índice, listas y números al abrir el archivo
        ajustes = self.doc.settings.element
        actualizar = OxmlElement("w:updateFields")
        actualizar.set(qn("w:val"), "true")
        ajustes.append(actualizar)

    # ---- páginas iniciales
    def centrado(self, texto, negrita=False, antes=0, despues=0, tam=12):
        for i, linea in enumerate(texto.split("\n")):
            p = self.doc.add_paragraph()
            formato_parrafo(p, WD_ALIGN_PARAGRAPH.CENTER, antes if i == 0 else 0, despues, interlineado=1.15)
            run = p.add_run(linea)
            fijar_fuente(run, tam, negrita=negrita)
        return p

    def salto(self):
        p = self.doc.add_paragraph()
        p.add_run().add_break(WD_BREAK.PAGE)
        formato_parrafo(p, despues=0)

    def cubierta(self):
        m = META
        self.centrado(m["titulo"], negrita=True, antes=24, despues=0)
        self.centrado("\n".join(m["autores"]), antes=150, despues=0)
        self.centrado(f"{m['institucion']}\n{m['facultad']}\n{m['programa']}\n{m['lugar_fecha']}", negrita=True, antes=180)
        self.salto()

    def portada(self):
        m = META
        self.centrado(m["titulo"], negrita=True, antes=24)
        self.centrado("\n".join(m["autores"]), antes=72)
        self.centrado(m["modalidad"], antes=72)
        self.centrado(f"{m['diplomado']}\nDocente:\n{m['docente']}", antes=48)
        self.centrado(f"{m['institucion']}\n{m['facultad']}\n{m['programa']}\n{m['lugar_fecha']}", negrita=True, antes=96)

    def nueva_seccion_numerada(self):
        # La cubierta y la portada no muestran número; desde aquí, número centrado (continúa en 3)
        primera = self.doc.sections[0]
        nueva = self.doc.add_section(WD_SECTION.NEW_PAGE)
        nueva.footer.is_linked_to_previous = False
        primera.footer.is_linked_to_previous = False
        for p in primera.footer.paragraphs:
            p.text = ""
        pie = nueva.footer.paragraphs[0]
        formato_parrafo(pie, WD_ALIGN_PARAGRAPH.CENTER, despues=0, interlineado=1.0)
        campo(pie, "PAGE", "3")

    def titulo_preliminar(self, texto, nueva_pagina=False):
        p = self.doc.add_paragraph()
        formato_parrafo(p, WD_ALIGN_PARAGRAPH.CENTER, 0, 12)
        p.paragraph_format.page_break_before = nueva_pagina
        run = p.add_run(texto)
        fijar_fuente(run, 12, negrita=True)

    def indices(self):
        self.titulo_preliminar("CONTENIDO")
        p = self.doc.add_paragraph()
        resultado = "\n".join(("    " * (n - 1)) + plano(t) for n, t in self.titulos)
        campo(p, 'TOC \\o "1-3" \\h \\z \\u', resultado or "Actualice el campo para ver el contenido")
        self.titulo_preliminar("LISTA DE TABLAS", nueva_pagina=True)
        p = self.doc.add_paragraph()
        campo(p, 'TOC \\h \\z \\c "Tabla"', "\n".join(plano(t) for t in self.tablas))
        self.titulo_preliminar("LISTA DE FIGURAS", nueva_pagina=True)
        p = self.doc.add_paragraph()
        campo(p, 'TOC \\h \\z \\c "Figura"', "\n".join(plano(t) for t in self.figuras))

    # ---- contenido
    def titulo(self, nivel, texto, primera=False):
        h = self.doc.add_heading(level=nivel)
        h.paragraph_format.page_break_before = nivel == 1
        agregar_texto(h, texto.upper() if nivel == 1 else texto, negrita_base=True)
        self.titulos.append((nivel, texto.upper() if nivel == 1 else texto))

    def parrafo(self, texto, sangria=None, cursiva=False):
        p = self.doc.add_paragraph()
        formato_parrafo(p, sangria=sangria)
        agregar_texto(p, texto, cursiva_base=cursiva)

    def lista(self, items, numerada=False):
        for n, item in enumerate(items, start=1):
            if numerada:
                p = self.doc.add_paragraph()
                formato_parrafo(p, despues=3)
                p.paragraph_format.left_indent = Cm(0.9)
                p.paragraph_format.first_line_indent = Cm(-0.6)
                agregar_texto(p, f"{n}. {item}")
            else:
                p = self.doc.add_paragraph(style="List Bullet")
                formato_parrafo(p, despues=3)
                agregar_texto(p, item)

    def leyenda(self, tipo, titulo):
        if tipo == "Tabla":
            self.n_tabla += 1
            n = self.n_tabla
            self.tablas.append(f"Tabla {n}. {titulo}")
        else:
            self.n_figura += 1
            n = self.n_figura
            self.figuras.append(f"Figura {n}. {titulo}")
        p = self.doc.add_paragraph(style="Caption")
        formato_parrafo(p, WD_ALIGN_PARAGRAPH.LEFT, 6, 4, interlineado=1.0)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(f"{tipo} ")
        fijar_fuente(r, 11, negrita=True)
        campo(p, f"SEQ {tipo} \\* ARABIC", str(n), tam=11, negrita=True)
        r = p.add_run(". ")
        fijar_fuente(r, 11, negrita=True)
        agregar_texto(p, titulo, tam=11, cursiva_base=True)

    def nota(self, texto):
        p = self.doc.add_paragraph()
        formato_parrafo(p, WD_ALIGN_PARAGRAPH.LEFT, 2, 10, interlineado=1.0)
        r = p.add_run("Nota. ")
        fijar_fuente(r, 10, cursiva=True)
        agregar_texto(p, texto, tam=10)

    def tabla(self, titulo, filas):
        self.leyenda("Tabla", titulo)
        cab, cuerpo = filas[0], filas[1:]
        t = self.doc.add_table(rows=1, cols=len(cab))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        tam = 10 if len(cab) <= 4 else 9
        for i, texto in enumerate(cab):
            c = t.rows[0].cells[i]
            sombrear(c)
            c.paragraphs[0].text = ""
            agregar_texto(c.paragraphs[0], texto, tam=tam, negrita_base=True)
            formato_parrafo(c.paragraphs[0], WD_ALIGN_PARAGRAPH.LEFT, 0, 0, interlineado=1.0)
        # repetir el encabezado si la tabla pasa de página
        trpr = t.rows[0]._tr.get_or_add_trPr()
        rep = OxmlElement("w:tblHeader")
        rep.set(qn("w:val"), "true")
        trpr.append(rep)
        for fila in cuerpo:
            celdas = t.add_row().cells
            for i in range(len(cab)):
                texto = fila[i] if i < len(fila) else ""
                celdas[i].paragraphs[0].text = ""
                agregar_texto(celdas[i].paragraphs[0], texto, tam=tam)
                formato_parrafo(celdas[i].paragraphs[0], WD_ALIGN_PARAGRAPH.LEFT, 0, 0, interlineado=1.0)

    def figura(self, titulo, ruta: Path):
        self.leyenda("Figura", titulo)
        ancho, alto = tam_png(ruta)
        if "evidencias" in ruta.parts:
            alto = min(alto, round(ancho * 1.3))
        ancho_cm = ANCHO_UTIL_CM
        alto_cm = ancho_cm * alto / ancho
        if alto_cm > 18:
            alto_cm = 18
            ancho_cm = alto_cm * ancho / alto
        p = self.doc.add_paragraph()
        formato_parrafo(p, WD_ALIGN_PARAGRAPH.CENTER, 0, 2, interlineado=1.0)
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(comprimir(ruta), width=Cm(ancho_cm))

    # ---- lectura del Markdown
    def procesar(self, md: str, primera_vez: bool, recolectar: bool):
        lineas = md.splitlines()
        i = 0
        primera_h1 = True
        pendiente_tabla = None
        while i < len(lineas):
            linea = lineas[i].rstrip()
            if not linea.strip():
                i += 1
                continue
            m = re.match(r"^(#{1,3}) (.+)$", linea)
            if m:
                nivel = len(m.group(1))
                if recolectar:
                    self.titulos.append((nivel, m.group(2).upper() if nivel == 1 else m.group(2)))
                else:
                    self.titulo(nivel, m.group(2), primera=primera_vez and primera_h1)
                primera_h1 = False
                i += 1
                continue
            if linea.startswith("Tabla: "):
                pendiente_tabla = linea[len("Tabla: "):]
                i += 1
                continue
            if linea.startswith("|"):
                filas = []
                while i < len(lineas) and lineas[i].startswith("|"):
                    celdas = [c.strip() for c in lineas[i].strip().strip("|").split("|")]
                    if not all(re.fullmatch(r":?-{3,}:?", c) for c in celdas):
                        filas.append(celdas)
                    i += 1
                if recolectar:
                    self.n_tabla += 1
                    self.tablas.append(f"Tabla {self.n_tabla}. {pendiente_tabla}")
                else:
                    self.tabla(pendiente_tabla or "Sin título", filas)
                pendiente_tabla = None
                continue
            m = re.match(r"^!\[(.+)\]\((.+)\)$", linea)
            if m:
                if recolectar:
                    self.n_figura += 1
                    self.figuras.append(f"Figura {self.n_figura}. {m.group(1)}")
                else:
                    self.figura(m.group(1), RAIZ / m.group(2))
                i += 1
                continue
            if linea.startswith("Nota: "):
                if not recolectar:
                    self.nota(linea[len("Nota: "):])
                i += 1
                continue
            if re.match(r"^- ", linea):
                items = []
                while i < len(lineas) and lineas[i].startswith("- "):
                    items.append(lineas[i][2:].strip())
                    i += 1
                if not recolectar:
                    self.lista(items)
                continue
            if re.match(r"^\d+\. ", linea):
                items = []
                while i < len(lineas) and re.match(r"^\d+\. ", lineas[i]):
                    items.append(re.sub(r"^\d+\. ", "", lineas[i]).strip())
                    i += 1
                if not recolectar:
                    self.lista(items, numerada=True)
                continue
            if linea.startswith("> "):
                if not recolectar:
                    self.parrafo(linea[2:], sangria=1.5, cursiva=False)
                i += 1
                continue
            # párrafo: une líneas seguidas
            texto = [linea.strip()]
            i += 1
            while i < len(lineas) and lineas[i].strip() and not re.match(r"^(#|\||- |\d+\. |> |!\[|Tabla: |Nota: )", lineas[i]):
                texto.append(lineas[i].strip())
                i += 1
            if not recolectar:
                self.parrafo(" ".join(texto))


def main():
    textos = [c.read_text(encoding="utf-8") for c in CAPITULOS]

    # 1) primera pasada: títulos, tablas y figuras para el resultado inicial de los índices
    previa = Monografia()
    for t in textos:
        previa.procesar(t, False, recolectar=True)

    m = Monografia()
    m.cubierta()
    m.portada()
    m.nueva_seccion_numerada()
    m.titulos, m.tablas, m.figuras = previa.titulos, previa.tablas, previa.figuras
    m.indices()
    m.titulos, m.tablas, m.figuras = [], [], []
    m.n_tabla = m.n_figura = 0
    for t in textos:
        m.procesar(t, False, recolectar=False)
    m.doc.core_properties.title = "RedNexus: monografía"
    m.doc.core_properties.author = "Equipo RedNexus"
    m.doc.save(SALIDA)
    print(f"{SALIDA.relative_to(RAIZ)}: {len(CAPITULOS)} archivos, {m.n_tabla} tablas, {m.n_figura} figuras")


if __name__ == "__main__":
    main()
