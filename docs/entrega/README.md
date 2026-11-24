# Entrega final de RedNexus (Diplomado CloudForge AI 5.0)

Fuente de todos los documentos que se entregan. Se escriben aquí en Markdown (versionados y revisables por PR) y se compilan al documento en formato APA 7 y a las diapositivas.

## Documento principal

| # | Capítulo | Archivo | Estado |
| --- | --- | --- | --- |
| – | Informe ejecutivo (resumen de 2 páginas) | [informe-ejecutivo.md](informe-ejecutivo.md) | Listo |
| 1 | Contexto y problema, por qué IA local y cloud native | [01-contexto-y-problema.md](01-contexto-y-problema.md) | Listo (cifras SPADIES 2022–2024) |
| 2 | Alcance, partes interesadas y marco normativo | [02-alcance-y-partes-interesadas.md](02-alcance-y-partes-interesadas.md) | Listo para revisión |
| 3 | Requisitos funcionales, no funcionales (ISO/IEC 25010), historias de usuario y trazabilidad | [03-requisitos.md](03-requisitos.md) | Listo para revisión |
| 4 | Arquitectura y ADR | [04-decisiones-de-arquitectura.md](04-decisiones-de-arquitectura.md) + [diagramas](../arquitectura/diagramas.md) | Listo para revisión |
| 5 | Privacidad, licencias y riesgos de la IA (DOC-02) | [05-privacidad-y-riesgos-ia.md](05-privacidad-y-riesgos-ia.md) | Listo para revisión |
| 6 | MLOps: dataset, experimentos y configuración ganadora | [06-mlops.md](06-mlops.md) | Listo para revisión |
| 7 | Pruebas y calidad | [07-pruebas-y-calidad.md](07-pruebas-y-calidad.md) | Listo (118 + 75 pruebas, integración con IA real) |
| 8 | DevSecOps, CI/CD y despliegue | [08-devsecops-y-despliegue.md](08-devsecops-y-despliegue.md) | Listo (bitácora del 24/11 y `cosign verify`) |
| 9 | Runbook de operación (PL-09) | [09-runbook.md](09-runbook.md) | Listo (6 simulacros cronometrados) |
| 10 | Sostenibilidad, impacto y plan de adopción (DOC-03) | [10-sostenibilidad-e-impacto.md](10-sostenibilidad-e-impacto.md) | Listo para revisión |
| 11 | Glosario y referencias | [11-glosario-y-referencias.md](11-glosario-y-referencias.md) | Listo para revisión |
| Anexo | Diccionario de datos y modelo ER | [../arquitectura/diccionario-de-datos.md](../arquitectura/diccionario-de-datos.md) | Hecho |
| Anexo | Informe del asistente RAG (actividad 2, módulo 6) | [../../asistente-rag/docs/informe](../../asistente-rag/docs/informe) | Hecho (60 casos, 83,3 %) |

| – | **Matriz de los 15 entregables del diplomado** | [ENTREGABLES.md](ENTREGABLES.md) | Listo |
| – | Verificación de requisitos contra la app (DOC-12) | [verificacion-requisitos.md](verificacion-requisitos.md) | Listo |
| – | Evidencias (capturas, Trivy, SBOM, firmas) | [evidencias/](evidencias) | Listo |

## Otras entregas

| Entrega | Archivo | Estado |
| --- | --- | --- |
| Guion del video de instalación y demo | [guion-video.md](guion-video.md) | Listo para grabar |
| Guion de la demo y la sustentación (DOC-04) | [guion-demo.md](guion-demo.md) | Ensayo técnico hecho; falta el ensayo con diapositivas |
| Diapositivas con la plantilla institucional | (Drive del equipo) | A cargo de María Paula (DOC-13) |
| Monografía en Word (formato del docente: carta, Arial 12, índices de tablas y figuras) | [../monografia/](../monografia) (`python3 docs/monografia/build.py`) | Monografía generada (ver abajo) |

## Cómo aportar

Cada integrante revisa o completa un capítulo con su issue (`DOC-*`, `PL-*`), en una rama `docs/...` desde `developer`, y abre PR. Las cifras y afirmaciones nuevas van con su fuente en el capítulo 11.
