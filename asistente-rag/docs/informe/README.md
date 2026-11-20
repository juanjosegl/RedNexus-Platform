# Informe del modelo RAG

Cada sección es un archivo para que cada integrante escriba la suya sin conflictos. Al final se unen en
`docs/Informe-modelo-rag-RedNexus.pdf` (formato institucional de Unicomfacauca, APA 7).

| Archivo | Sección | Responsable |
| --- | --- | --- |
| [A-portada.md](A-portada.md) | A. Portada | Maria Alejandra Guzman |
| [B-indice.md](B-indice.md) | B. Índice | Maria Alejandra Guzman |
| [C-introduccion.md](C-introduccion.md) | C. Introducción | Juanjo |
| [D-problema.md](D-problema.md) | D. Problema que resuelve | Juanjo |
| [E-definicion-modelo.md](E-definicion-modelo.md) | E. Definición del modelo | Juanjo |
| [F-pruebas.md](F-pruebas.md) | F. Implementación y análisis de pruebas | Juanjo |
| [G-conclusiones.md](G-conclusiones.md) | G. Conclusiones y trabajos futuros | Juanjo |

Las imágenes van en `docs/informe/img/` con nombres descriptivos (`f-chat-respuesta-calificaciones.png`).

Para regenerar el PDF después de cambiar una sección (necesita Google Chrome instalado):

```bash
pip install markdown
python scripts/build_informe.py
```
