# Entrega — Actividad 2, módulo 6: servicio de IA generativa con RAG

**Proyecto:** RedNexus, red de apoyo académico entre estudiantes
**Diplomado:** CloudForge AI 5.0, Unicomfacauca
**Docente:** Diego Fernando Rivera Vásquez
**Fecha:** 20/11/2026

**Informe:** [Informe-modelo-rag-RedNexus.pdf](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/docs/Informe-modelo-rag-RedNexus.pdf)
(secciones A a G)

## Resumen

Construimos **Nexus**, un asistente de soporte que responde cómo usar RedNexus solo con la documentación del
proyecto. Usa RAG en **Open WebUI** con modelos locales de **Ollama** y está integrado en la aplicación: la página
`/ayuda` del frontend llama a `POST /api/support/chat` del backend, que consulta el modelo personalizado
`asistente-rednexus`.

**Resultado:** **88,5 % de éxito** (46 de 52 casos) en el golden dataset, frente a la meta del 70 %, con una
latencia media de 18,7 s. Las categorías de seguridad, fuera de alcance y fuera de la base quedan al 100 %.

> **Actualización 23/11/2026:** al agregar el octavo documento de la base de conocimiento (solicitudes de ayuda) y sus 8 casos, la evaluación con **60 casos** dio **83,3 %** (`runs/resumen_v4_final_chunk400_ov60_60casos_*`), también por encima de la meta. El PDF entregado conserva los resultados del 20/11.

## Dónde está cada requisito

| Requisito de la actividad | Dónde está |
| --- | --- |
| Documentos de la base de conocimiento | [knowledge-base/](https://github.com/juanjosegl/RedNexus-Platform/tree/main/asistente-rag/knowledge-base): 7 documentos en Markdown (7 201 tokens); tabla en la sección E.2 del informe |
| Tamaño de fragmento y solapamiento en tokens | **400 tokens** de fragmento y **60 de solapamiento** (separador por tokens, tiktoken), Top K 4: [model/configuracion.md](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/model/configuracion.md) y sección E.3 |
| Comparación de configuraciones | 400/60 → 88,5 % y 300/30 → 80,8 %, con los 52 casos: sección F.4 y [runs/](https://github.com/juanjosegl/RedNexus-Platform/tree/main/asistente-rag/runs) |
| Modelo personalizado | `asistente-rednexus` sobre `qwen2.5:3b`, temperatura 0,2, `num_ctx` 4096, máx. 400 tokens: sección E.1 y E.5 |
| System prompt y políticas | [model/system-prompt.md](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/model/system-prompt.md): 3 reglas de seguridad (S1–S3) y 6 de respuesta (R1–R6), con su historial de versiones; [plantilla RAG](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/model/rag-template.md) |
| Golden dataset de 50 casos o más | [golden-dataset/](https://github.com/juanjosegl/RedNexus-Platform/tree/main/asistente-rag/golden-dataset): **52 casos** en 10 categorías (38 para responder y 14 para rechazar), validados en el CI |
| Evaluación: latencia, palabras clave y juez de 1 a 5 | [evaluate_rag.py](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/evaluate_rag.py) (juez `qwen2.5:7b`, fidelidad y completitud) |
| Resultado de 70 % o más | [Resumen de la corrida final](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/runs/resumen_v3_final_chunk400_ov60_20261120_104125.md): **88,5 %** |
| Código | Configuración por API: [scripts/setup_openwebui.py](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/scripts/setup_openwebui.py), [docker-compose.yml](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/docker-compose.yml); integración en [RedNexus-Backend](https://github.com/juanjosegl/RedNexus-Backend/tree/main/src/modules/support) y [RedNexus-Frontend](https://github.com/juanjosegl/RedNexus-Frontend/tree/main/src/features/support) |
| Informe `Informe-modelo-rag-RedNexus.pdf` (A a G) | [docs/Informe-modelo-rag-RedNexus.pdf](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/docs/Informe-modelo-rag-RedNexus.pdf); fuentes de cada sección en [docs/informe/](https://github.com/juanjosegl/RedNexus-Platform/tree/main/asistente-rag/docs/informe) |
| Aportes de cada integrante | [README principal, "Aportes del equipo"](https://github.com/juanjosegl/RedNexus-Platform#aportes-del-equipo) y [tareas del equipo](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/docs/tareas.md) |

## Cómo reproducirlo

Los pasos para levantar Open WebUI, configurar el RAG con un solo comando y correr la evaluación están en el
[README del asistente](https://github.com/juanjosegl/RedNexus-Platform/blob/main/asistente-rag/README.md).

## Equipo

- Juan Jose Gutierrez Lasso ([@juanjosegl](https://github.com/juanjosegl)), líder
- Maria Alejandra Guzman ([@alejandraguzman12](https://github.com/alejandraguzman12))
- Victor Daniel Fernandez ([@daniel200231](https://github.com/daniel200231))
- Jose Sebastian Fernandez ([@josesfa](https://github.com/josesfa))
- Maria Paula Andrade ([@MariPau-dev](https://github.com/MariPau-dev))
