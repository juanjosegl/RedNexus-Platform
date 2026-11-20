# Entrega final de RedNexus (Diplomado CloudForge AI 5.0)

Fuente de todos los documentos que se entregan. Se escriben aquí en Markdown (versionados y revisables por PR) y se compilan al documento en formato APA 7 y a las diapositivas.

## Documento principal

| # | Capítulo | Archivo | Estado |
| --- | --- | --- | --- |
| – | Informe ejecutivo (resumen de 2 páginas) | [informe-ejecutivo.md](informe-ejecutivo.md) | Borrador |
| 1 | Contexto y problema, por qué IA local y cloud native | [01-contexto-y-problema.md](01-contexto-y-problema.md) | Borrador (faltan cifras actualizadas de SPADIES) |
| 2 | Alcance, partes interesadas y marco normativo | [02-alcance-y-partes-interesadas.md](02-alcance-y-partes-interesadas.md) | Listo para revisión |
| 3 | Requisitos funcionales, no funcionales (ISO/IEC 25010), historias de usuario y trazabilidad | [03-requisitos.md](03-requisitos.md) | Listo para revisión |
| 4 | Arquitectura y ADR | [04-decisiones-de-arquitectura.md](04-decisiones-de-arquitectura.md) + [diagramas](../arquitectura/diagramas.md) | Listo para revisión |
| 5 | Privacidad, licencias y riesgos de la IA (DOC-02) | [05-privacidad-y-riesgos-ia.md](05-privacidad-y-riesgos-ia.md) | Listo para revisión |
| 6 | MLOps: dataset, experimentos y configuración ganadora | [06-mlops.md](06-mlops.md) | Listo para revisión |
| 7 | Pruebas y calidad | [07-pruebas-y-calidad.md](07-pruebas-y-calidad.md) | Faltan números finales y capturas |
| 8 | DevSecOps, CI/CD y despliegue | [08-devsecops-y-despliegue.md](08-devsecops-y-despliegue.md) | Falta la bitácora de Trivy |
| 9 | Runbook de operación (PL-09) | [09-runbook.md](09-runbook.md) | Faltan resultados de simulacros |
| 10 | Sostenibilidad, impacto y plan de adopción (DOC-03) | [10-sostenibilidad-e-impacto.md](10-sostenibilidad-e-impacto.md) | Confirmar alcance con el coordinador |
| 11 | Glosario y referencias | [11-glosario-y-referencias.md](11-glosario-y-referencias.md) | Listo para revisión |
| Anexo | Diccionario de datos y modelo ER | [../arquitectura/diccionario-de-datos.md](../arquitectura/diccionario-de-datos.md) | Hecho |
| Anexo | Informe del asistente RAG (actividad 2, módulo 6) | [../../asistente-rag/docs/informe](../../asistente-rag/docs/informe) | En curso (IA-08) |

## Otras entregas

| Entrega | Archivo | Estado |
| --- | --- | --- |
| Guion de la demo y la sustentación (DOC-04) | [guion-demo.md](guion-demo.md) | Borrador; falta el ensayo cronometrado |
| Diapositivas con la plantilla institucional | (Drive del equipo) | Por hacer: pedir la plantilla a comunicaciones |
| Documento en Word APA 7 (portada, tablas y figuras autogeneradas) | Se genera desde estos archivos | Por compilar al cierre |

## Cómo aportar

Cada integrante revisa o completa un capítulo con su issue (`DOC-*`, `PL-*`), en una rama `docs/...` desde `developer`, y abre PR. Las cifras y afirmaciones nuevas van con su fuente en el capítulo 11.
