# 2. Alcance, partes interesadas y marco normativo

## 2.1 Alcance del MVP

| Módulo | Qué incluye | Estado | Dónde está |
| --- | --- | --- | --- |
| Cuentas | Registro, inicio de sesión con JWT, sesión persistente | Hecho | BE-01, FE-02 |
| Perfil | Bio en texto libre, etiquetas, calificación promedio, perfil público sin correo | Hecho | BE-02, FE-03 |
| Solicitudes | Publicar una duda por texto o por **nota de voz**, ver su estado, cerrarla | Hecho | BE-03, BE-04, FE-04, FE-05 |
| IA de emparejamiento | Clasificación con LLM, embeddings con pgvector, top 3 con explicación, respaldo por etiquetas | Hecho | IA-01 a IA-04 |
| Multimodal | Transcripción de notas de voz con whisper.cpp | Hecho | IA-05 |
| Ayudante | Bandeja con las solicitudes propuestas, aceptar o rechazar, contacto al aceptar | Hecho | BE-05, FE-06 |
| Calificación | 1 a 5 estrellas, una por solicitud aceptada, alimenta el ranking | Hecho | BE-06, FE-07 |
| Asistente de soporte | Chat con RAG en Open WebUI sobre la documentación de la plataforma | Hecho | BE-07, FE-08, IA-08 |
| PQRS | Radicar y consultar peticiones, quejas, reclamos y sugerencias | Hecho | BE-12, FE-13 |
| MLOps | Dataset sintético, experimentos en MLflow, configuración ganadora registrada y aplicada | Hecho | IA-06, IA-07 |
| DevSecOps | CI obligatorio, imágenes multiarquitectura en GHCR, Trivy, SBOM y firma con Cosign | Hecho | PL-01, PL-02 |
| Despliegue | Docker Compose, Kubernetes (k3d y minikube), Dokploy con CD desde `main`, Render + Neon | Hecho | Platform, PL |
| Privacidad | Autorización de tratamiento, exportar y eliminar mis datos, nota de voz que no se guarda | Hecho | DOC-02 |

### Previsto (evolución)

| Tema | Qué falta | Tarea |
| --- | --- | --- |
| GitOps | Argo CD sincronizando un overlay de demo con las imágenes de GHCR | PL-03 |
| Secretos | Sealed Secrets para el overlay de demo | PL-04 |
| Admisión | Kyverno exigiendo imágenes firmadas | PL-05 |
| IaC | OpenTofu para namespaces, Argo CD y reglas de los repos | PL-06 |
| Observabilidad | OpenTelemetry, Grafana y el SLO de 30 s medido con trazas | PL-07 |
| Catálogo | `catalog-info.yaml` y TechDocs | PL-08 |

### Fuera de alcance

Chat en tiempo real, aplicación móvil nativa, pagos, videollamadas y roles diferenciados (docente, administrador). Cualquier usuario puede pedir y dar ayuda. Recortar es parte de la ingeniería: la rúbrica del diplomado valora una solución pequeña, reconstruible y bien observada.

## 2.2 Partes interesadas

| Parte interesada | Interés | Cómo participa |
| --- | --- | --- |
| Estudiantes que piden ayuda | Resolver dudas rápido y con alguien que sepa | Publican solicitudes, califican |
| Estudiantes ayudantes (semestres avanzados, monitores, egresados) | Ayudar, ganar reputación, reforzar lo que saben | Completan su perfil, aceptan o rechazan |
| Docentes del Diplomado CloudForge AI 5.0 | Evaluar arquitectura, operación, IA y documentación | Revisan entregas y sustentación |
| Unicomfacauca (bienestar y dirección de programas) | Reducir la deserción, posible adopción institucional | Futuro patrocinador y responsable del tratamiento de datos |
| Equipo de desarrollo (5 integrantes) | Construir, operar y graduarse | Desarrollo, pruebas, documentación |
| Oficina de protección de datos (futura) | Cumplimiento de la Ley 1581 | Aprobar la política de tratamiento y los plazos de conservación |

## 2.3 Marco normativo

| Norma | Qué exige | Cómo la atiende RedNexus |
| --- | --- | --- |
| **Ley 1581 de 2012** (protección de datos personales) y Decreto 1377 de 2013 | Autorización previa e informada, finalidad, acceso, rectificación y supresión, seguridad | Casilla de autorización con fecha (`consentAt`); `GET /api/users/me/export` y `DELETE /api/users/me`; correos visibles solo tras aceptar; notas de voz que no se guardan; datos sintéticos en la demo. Detalle en [privacidad y riesgos](05-privacidad-y-riesgos-ia.md) |
| **CONPES 4144 de 2025** (Política Nacional de Inteligencia Artificial) | Uso ético, confiable y responsable de la IA, capacidades nacionales | IA local con modelos abiertos, explicación de cada recomendación, degradación controlada, ficha de cada modelo y evaluación documentada |
| **Guía de ética de IA del DNP (2025)** y lineamientos de MinTIC | Transparencia, supervisión humana, seguridad digital | El estudiante decide (la IA solo propone), explicaciones visibles, CI con escaneo de vulnerabilidades y firma de imágenes |
| **Ley 1915 de 2018** y Decisión Andina 351 (derecho de autor) | Respeto de licencias | Inventario de licencias de modelos y software en la ficha de modelos |
