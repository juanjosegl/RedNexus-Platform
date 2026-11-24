# Anexos

## Anexo A. Entregables mínimos del diplomado y su evidencia

Tabla: Relación de los 15 entregables mínimos del diplomado con la evidencia de RedNexus
| # | Entregable | Evidencia | Estado |
| --- | --- | --- | --- |
| 1 | Documento de contexto, usuarios, requisitos, restricciones y decisiones de arquitectura | Capítulos 1 y 3 de esta monografía; `docs/entrega/01` a `04`; diagramas en `docs/arquitectura/` | Completo |
| 2 | Repositorio Git con estrategia de ramas, *issues*, README y convenciones de contribución | Tres repositorios públicos; ramas `developer → test → main` con reglas como código; `CONTRIBUTING.md`; 75 *issues* y tablero | Completo |
| 3 | Aplicación o servicio contenedorizado con pruebas automatizadas | `Dockerfile` multietapa; `compose.yaml`; 193 pruebas en verde | Completo |
| 4 | Manifiestos de Kubernetes y/o Kustomize para despliegue reproducible | `deploy/base` y overlays `k3d`, `minikube` y `demo`; validación con kubeconform | Completo |
| 5 | Pipeline CI/CD con controles de calidad y seguridad | CI obligatorio, *Imagen*, *Promover imágenes* y *GitOps (kind)* | Completo |
| 6 | SBOM, escaneo de vulnerabilidades y firma/verificación | Syft, Trivy, Cosign, `cosign verify` y política de Kyverno; bitácora de hallazgos | Completo |
| 7 | Repositorio GitOps y sincronización con Argo CD | RedNexus-Platform con tres aplicaciones de Argo CD y Sealed Secrets | Completo (clúster local o efímero en Actions) |
| 8 | Infraestructura como código | OpenTofu en `iac/cluster` e `iac/github`; clústeres k3d como código | Completo |
| 9 | Dashboard de observabilidad con SLI/SLO | OpenTelemetry, tablero de Grafana, SLI `rednexus.match.latency` y SLO de 30 s | Completo |
| 10 | Registro de experimentos y modelos (MLOps) | 39 *runs* en MLflow y modelo `rednexus-matching` v1 | Completo |
| 11 | Servicio de IA local con RAG | Explicación con RAG sobre el perfil y asistente en Open WebUI (83,3 %) | Completo |
| 12 | Workflow multimodal adicional | Notas de voz transcritas con whisper.cpp | Completo |
| 13 | Análisis de privacidad, seguridad, licencias, riesgos de IA y límites | `docs/entrega/05-privacidad-y-riesgos-ia.md`; secciones 3.3 y 1.7 | Completo |
| 14 | *Runbook* de operación, respaldo, recuperación y fallas comunes | `docs/entrega/09-runbook.md` y `scripts/simulacros.sh` | Completo |
| 15 | Informe ejecutivo, demostración técnica y sustentación | Informe ejecutivo, guion de la demo, guion del video, guía de instalación y esta monografía | Diapositivas a cargo del equipo |
Nota: Elaboración propia. Versión navegable con enlaces: `docs/entrega/ENTREGABLES.md` en RedNexus-Platform.

## Anexo B. Enlaces del proyecto

Tabla: Enlaces de los repositorios, artefactos y documentos
| Recurso | Enlace |
| --- | --- |
| Repositorio Backend | https://github.com/juanjosegl/RedNexus-Backend |
| Repositorio Frontend | https://github.com/juanjosegl/RedNexus-Frontend |
| Repositorio Platform (GitOps, ML, RAG y documentación) | https://github.com/juanjosegl/RedNexus-Platform |
| Guía de instalación para el jurado | README de RedNexus-Platform, sección "Instalar y probar RedNexus" |
| Tablero del proyecto | https://github.com/users/juanjosegl/projects/1 |
| Imágenes firmadas | ghcr.io/juanjosegl/rednexus-backend y ghcr.io/juanjosegl/rednexus-frontend |
| Matriz de entregables | `docs/entrega/ENTREGABLES.md` |
| Informe del asistente RAG | `asistente-rag/docs/Informe-modelo-rag-RedNexus.pdf` |
| Video de instalación y demostración | Se agrega al README al publicarse |
Nota: Elaboración propia.

## Anexo C. Equipo y aportes

Tabla: Integrantes del equipo y aportes principales
| Integrante | Usuario de GitHub | Aportes principales |
| --- | --- | --- |
| Juan José Gutiérrez Lasso (líder) | juanjosegl | Arquitectura, backend, IA y MLOps, plataforma (Kubernetes, GitOps, DevSecOps, IaC y observabilidad), asistente RAG y documentación |
| Victor Daniel Fernández | daniel200231 | Componente de mensajes del chat de ayuda (FE-11), documentación y revisión de requisitos |
| José Sebastián Fernández | josesfa | Enlace de ayuda y preguntas sugeridas (FE-09 y FE-10), pruebas y evidencias de CI |
| María Paula Andrade Muñoz | MariPau-dev | Preguntas frecuentes y acceso a la ayuda (FE-12), documento base y diapositivas |
| María Alejandra Guzmán Ruiz | alejandraguzman12 | Documentos de la base de conocimiento, casos del *golden dataset*, pruebas manuales y simulacros |
Nota: Elaboración propia. El detalle de cada aporte está en los *pull requests* y en el README de RedNexus-Platform.

## Anexo D. Evidencias adicionales

![Pantalla de inicio de sesión](docs/entrega/evidencias/app-01-login.png)
Nota: Captura de la aplicación.

![Página de inicio con las estadísticas públicas](docs/entrega/evidencias/app-03-inicio.png)
Nota: Captura de la aplicación.

![Historial de solicitudes de una usuaria](docs/entrega/evidencias/app-08-mis-solicitudes.png)
Nota: Captura de la aplicación.

![PQRS radicada](docs/entrega/evidencias/app-09-pqrs.png)
Nota: Captura de la aplicación.

![Pull requests fusionados del backend](docs/entrega/evidencias/gh-06-prs-backend.png)
Nota: Captura de GitHub.

![Integración continua de Platform en main](docs/entrega/evidencias/gh-04-ci-platform.png)
Nota: Captura de GitHub Actions.

![Modelo rednexus-matching en el Model Registry de MLflow](docs/entrega/evidencias/mlflow-02-modelo-registrado.png)
Nota: Captura de la interfaz de MLflow.
