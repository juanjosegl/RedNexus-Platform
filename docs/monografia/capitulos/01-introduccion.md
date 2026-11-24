# Capítulo 1. Introducción

## 1.1 Planteamiento, descripción y formulación del problema

### 1.1.1 Planteamiento

En la vida universitaria es frecuente que un estudiante se bloquee con un tema y no sepa a quién acudir. En los programas de ingeniería, donde las asignaturas se apoyan unas en otras, una duda sin resolver a tiempo afecta el avance en las materias siguientes: un *join* mal entendido en Bases de Datos I reaparece en el proyecto de Ingeniería de Software, y una regla de la cadena que no quedó clara reaparece en Física y en Cálculo Vectorial. Ante esa situación, el estudiante suele tener tres caminos: esperar la monitoría o la asesoría del docente, que tienen horario y cupo; preguntar en el grupo de mensajería del curso, donde la pregunta la ve quien esté conectado y no necesariamente quien sabe; o buscar solo en internet, sin el contexto del curso.

Al mismo tiempo, en cada cohorte hay estudiantes de semestres avanzados, monitores, docentes y egresados que dominan esos temas y que estarían dispuestos a orientar a otros. La ayuda entre pares existe, pero es informal: depende de conocer a la persona indicada o de coincidir con ella. La información sobre quién sabe qué está dispersa, no se actualiza y no se puede consultar.

### 1.1.2 Descripción del problema y su contexto

El problema importa porque las dificultades académicas no resueltas se acumulan y contribuyen al abandono de los estudios. El Sistema para la Prevención de la Deserción en la Educación Superior (SPADIES) del Ministerio de Educación Nacional reporta una tasa de deserción anual en educación superior de 9,03 % en 2022, 8,97 % en 2023 y 9,78 % en 2024 (Infobae, 2026; El Tiempo, 2025), y una deserción por cohorte a décimo semestre en el nivel universitario cercana al 45 % (Ministerio de Educación Nacional, 2016). Las áreas de ingeniería, arquitectura y urbanismo están entre las de menor graduación. Desde 2020 SPADIES no publica cifras por área de conocimiento (Universidad Icesi, 2025), por lo que no fue posible obtener un dato reciente específico para los programas de ingeniería de Unicomfacauca.

La evidencia sobre el acompañamiento entre pares es favorable: Topping (1996) documentó sus efectos positivos en educación superior, y Machado (2022) encontró que participar en un programa de tutorías entre pares en la Universidad de la República (Uruguay) reduce entre 8 % y 11 % la probabilidad de deserción. El cuello de botella no parece ser la disposición a ayudar, sino **encontrar rápido a la persona adecuada**.

A esa dificultad organizativa se suma una técnica. Las búsquedas por palabras exactas no relacionan expresiones distintas de una misma necesidad: un estudiante escribe "no entiendo cómo unir tres tablas con una intermedia" y un posible colaborador describe su experiencia como "*joins* muchos a muchos y modelado entidad-relación". Ambos hablan de lo mismo, pero un buscador literal no los conecta. Los modelos de lenguaje y de *embeddings* resuelven esa brecha semántica, pero su uso habitual mediante servicios comerciales implica enviar a terceros, fuera del país, datos personales de estudiantes (perfiles, dudas y datos de contacto), cuyo tratamiento está regulado en Colombia por la Ley 1581 de 2012, además de un costo por consumo que una institución o un equipo académico no siempre puede asumir.

El proyecto se sitúa espacial y temporalmente en la comunidad académica de Unicomfacauca, en Popayán (Cauca), durante el segundo semestre de 2026, en el marco del Diplomado CloudForge AI 5.0. El equipo dispone de computadores personales de 8 GB de memoria (uno con procesador Apple M1 y cuatro con Windows) y de herramientas de código abierto, lo que condiciona el tamaño de los modelos y de la infraestructura.

### 1.1.3 Formulación del problema

Con base en lo anterior, el proyecto busca responder la siguiente pregunta:

> **¿Cómo diseñar, construir y operar una plataforma web de apoyo académico entre pares que, mediante modelos de inteligencia artificial ejecutados en infraestructura propia y prácticas nativas de la nube, recomiende a cada estudiante los compañeros más adecuados para resolver su duda, de forma medible, reproducible y respetuosa con la protección de sus datos personales?**

De la pregunta se desprenden tres preguntas operativas que orientan la evaluación: (1) ¿qué tan bien acierta el emparejamiento con modelos pequeños que caben en 8 GB, y qué configuración funciona mejor en español?; (2) ¿es posible ofrecer un asistente de soporte con RAG que responda con fidelidad a la documentación sin depender de servicios externos?; y (3) ¿puede un equipo académico construir, asegurar y operar la solución con las prácticas de la industria (CI/CD, cadena de suministro segura, GitOps, observabilidad) con recursos gratuitos?

## 1.2 Justificación

**En lo académico.** El apoyo entre pares es una de las formas más naturales de aprender y tiene evidencia de impacto en el desempeño y la permanencia (Topping, 1996; Machado, 2022). RedNexus no sustituye a docentes ni a monitores: aprovecha los conocimientos que ya existen en la comunidad y acorta el tiempo entre tener una duda y encontrar a alguien que pueda ayudar. Cada persona puede pedir ayuda en un tema y ofrecerla en otro desde la misma cuenta, lo que evita dividir a la comunidad entre quienes preguntan y quienes responden.

**En lo social.** La plataforma es gratuita para los estudiantes, admite notas de voz para quienes escriben con dificultad o van en movimiento y reconoce, mediante las calificaciones, el trabajo de quienes acompañan a otros. Se alinea con los Objetivos de Desarrollo Sostenible 4 (educación de calidad), 9 (innovación) y 10 (reducción de desigualdades), porque ofrece acompañamiento sin depender de pagar tutorías.

**En lo técnico y profesional.** El proyecto integra en un caso real las prácticas que hoy exige la industria del software: arquitectura documentada con decisiones explícitas, contenedores, Kubernetes, integración y entrega continuas, seguridad de la cadena de suministro, GitOps, infraestructura como código, observabilidad, MLOps y LLMOps. Para el equipo es la oportunidad de construir un producto completo y de documentar con evidencia cada decisión, que es lo que se espera de un ingeniero de sistemas.

**En lo ético y legal.** Ejecutar los modelos en infraestructura propia evita transferir datos personales a terceros y elimina el costo por consumo. Esa ventaja se acompaña de los controles que exige la Ley 1581 de 2012 (autorización previa, finalidad, acceso, supresión y circulación restringida), porque el procesamiento local, por sí solo, no garantiza el cumplimiento. La recomendación se presenta como apoyo a la decisión, con explicación y supervisión humana, en línea con el CONPES 4144 de 2025 sobre inteligencia artificial.

**En lo regional.** Una solución pensada desde y para una institución de Popayán puede ampliarse a otros programas e instituciones del Cauca, y demuestra que es posible ofrecer servicios de IA útiles sin infraestructura costosa ni dependencia de proveedores externos, algo pertinente para regiones con menos recursos.

## 1.3 Objetivos

### 1.3.1 Objetivo general

Desarrollar una plataforma web de apoyo académico entre pares que recomiende colaboradores mediante inteligencia artificial ejecutada en infraestructura propia, construida y operada con prácticas nativas de la nube, DevSecOps y MLOps, y validada con métricas reproducibles.

### 1.3.2 Objetivos específicos

1. Definir los requisitos, las restricciones y la arquitectura de la solución, documentando las decisiones con registros ADR y diagramas C4 y 4+1.
2. Implementar la aplicación web y sus servicios: cuenta y perfil únicos, solicitudes por texto y por nota de voz, bandeja del colaborador, aceptación con asignación única, calificación, asistente de ayuda, PQRS y derechos sobre los datos personales.
3. Construir el emparejamiento con modelos locales de lenguaje y de *embeddings* y seleccionar su configuración mediante experimentos registrados en MLflow.
4. Implementar un servicio de soporte con generación aumentada por recuperación (RAG) y evaluarlo con un conjunto de casos de referencia.
5. Automatizar la construcción, la verificación de seguridad y el despliegue reproducible de la solución mediante CI/CD, SBOM, firma de imágenes, Kubernetes, GitOps e infraestructura como código.
6. Validar la calidad y la operación del sistema mediante pruebas automatizadas, observabilidad con un SLI/SLO definido, un *runbook* y simulacros de falla.

## 1.4 Marco de referencia

### 1.4.1 Marco contextual

Unicomfacauca es una institución de educación superior de Popayán con programas de ingeniería en los que el acompañamiento académico se apoya en monitorías y asesorías docentes. El Diplomado CloudForge AI 5.0, iniciado el 14 de septiembre de 2026, es una modalidad de grado que exige un proyecto integrador con quince entregables mínimos, desde el documento de contexto hasta la sustentación ante jurado, pasando por Kubernetes, CI/CD, GitOps, observabilidad, MLOps, un servicio de IA local con RAG y un flujo multimodal. RedNexus responde a esos entregables con un problema real del entorno del equipo.

En el ámbito internacional existen plataformas de preguntas y respuestas entre estudiantes y sistemas experimentales de recomendación de tutores; en el nacional, programas institucionales de acompañamiento entre pares y de monitorías; y en el regional, estrategias de tutorías y monitorías en las universidades de Popayán. El capítulo 2 presenta ese estado del arte en detalle. Ninguna de las soluciones revisadas combina recomendación semántica en español, explicación de la recomendación, ejecución local de los modelos y cumplimiento explícito de la Ley 1581.

### 1.4.2 Marco legal y normativo

Tabla: Marco legal y normativo aplicable a RedNexus
| Referencia | Aplicación en RedNexus | Naturaleza |
| --- | --- | --- |
| Ley Estatutaria 1581 de 2012 | Autorización previa, finalidad, acceso, supresión, circulación restringida y seguridad de los datos personales | Obligación legal |
| Decreto 1377 de 2013 (compilado en el Decreto 1074 de 2015) | Forma de obtener y probar la autorización; políticas de tratamiento | Reglamentaria |
| CONPES 4144 de 2025, Política Nacional de IA | Uso responsable, transparencia y gestión de riesgos de la IA | Política pública orientadora |
| ISO/IEC 25010:2023 | Modelo de calidad para organizar los requisitos no funcionales | Estándar voluntario |
| ISO/IEC 27001:2022 e ISO/IEC 42001:2023 | Referencia para controles de seguridad y gobernanza de sistemas de IA | Estándar voluntario (sin certificación) |
| NIST AI RMF 1.0 | Identificación y tratamiento de riesgos de IA (alucinación, sesgo, inyección de *prompts*) | Marco voluntario |
| NIST SP 800-218 (SSDF) | Prácticas de desarrollo seguro: revisión por PR, escaneo, SBOM y firma | Marco voluntario |
| Licencias de los modelos | Qwen Research License (`qwen2.5:3b`, uso no comercial), Apache 2.0 y MIT | Condición contractual |
Nota: Elaboración propia. La mención de estándares ISO y marcos NIST no implica certificación ni conformidad formal.

La Ley 1581 es la referencia central, porque la plataforma trata nombres, correos, perfiles académicos, dudas y, de forma transitoria, notas de voz. Su cumplimiento se concreta en el diseño: el registro exige aceptar el tratamiento y guarda la fecha de autorización; el usuario puede descargar todos sus datos y eliminar su cuenta con todo lo asociado; el correo solo se comparte entre las dos personas cuando un colaborador acepta; y las notas de voz se transcriben y se descartan sin almacenarse. El capítulo 3 detalla estas decisiones.

### 1.4.3 Marco teórico (síntesis)

El proyecto se apoya en cinco cuerpos de conocimiento, desarrollados en el capítulo 2: el aprendizaje entre pares como estrategia pedagógica; los sistemas de recomendación basados en contenido y la búsqueda semántica con *embeddings* (Reimers y Gurevych, 2019, 2020); los modelos de lenguaje pequeños y la generación aumentada por recuperación (Lewis et al., 2020); la ingeniería nativa de la nube, que incluye contenedores, Kubernetes, GitOps y seguridad de la cadena de suministro (Burns et al., 2016; Newman et al., 2022); y la ingeniería de confiabilidad y MLOps (Beyer et al., 2016; Zaharia et al., 2018).

## 1.5 Metodología

### 1.5.1 Tipo de investigación

El proyecto corresponde a una **investigación aplicada de desarrollo tecnológico** con enfoque **cuantitativo experimental** en los componentes de inteligencia artificial. Es aplicada porque busca resolver un problema concreto mediante un artefacto de software; es de desarrollo tecnológico porque su resultado es un producto funcional y reproducible; y es experimental en la IA porque las configuraciones del emparejamiento y del asistente se compararon con variables controladas (modelo, *prompt*, pesos, umbral, tamaño de fragmento) y métricas definidas de antemano sobre conjuntos etiquetados.

El desarrollo siguió un proceso **iterativo e incremental** con tablero Kanban: cada tarea es un *issue* con identificador (`BE-`, `FE-`, `IA-`, `PL-`, `DOC-`), se trabaja en una rama temporal y entra a la rama `developer` mediante *pull request* con integración continua obligatoria; luego se promueve a `test` y a `main`.

### 1.5.2 Procedimientos para la recolección, el análisis y la sistematización de la información

- **Recolección:** revisión de literatura y de fuentes oficiales (SPADIES, normativa); revisión de soluciones similares; construcción de un conjunto sintético de 50 perfiles, 100 solicitudes con su colaborador correcto y 10 dudas fuera de tema; un *golden dataset* de 60 preguntas con su respuesta esperada para el asistente; y mediciones automáticas de pruebas, escaneos, latencias y simulacros.
- **Análisis:** métricas de recuperación (precision@3, *hit@1*, MRR, cobertura y rechazo de dudas fuera de tema) y de generación (tasa de afirmaciones no soportadas, fidelidad y completitud con un modelo juez, TTFT y TPS); comparación entre configuraciones; y verificación de cada requisito funcional contra la aplicación desplegada.
- **Sistematización:** experimentos y modelos en MLflow; resultados de evaluación en archivos versionados; decisiones en ADR; evidencias (capturas, salidas de Trivy y Cosign) en el repositorio; y documentación por capítulos en Markdown, revisada mediante *pull requests*.

### 1.5.3 Actividades y resultados

Tabla: Relación entre objetivos, actividades, instrumentos y productos
| Objetivo | Actividad | Instrumento | Producto a obtener |
| --- | --- | --- | --- |
| 1. Requisitos y arquitectura | Análisis del problema, partes interesadas, requisitos y decisiones | Historias de usuario, ISO/IEC 25010, plantilla ADR, PlantUML | Documento de contexto, 17 RF, RNF, 12 ADR y 11 diagramas |
| 2. Aplicación web | Desarrollo por *issues* en Backend y Frontend | NestJS, Prisma, Vue 3, Vitest, Swagger | API y aplicación web con 193 pruebas automatizadas |
| 3. Emparejamiento con IA | Dataset sintético y 39 experimentos | Ollama, Python, MLflow | Configuración `rednexus-matching` v1 registrada y desplegada |
| 4. Asistente RAG | Base de conocimiento, modelo personalizado y evaluación | Open WebUI, `evaluate_rag.py`, juez `qwen2.5:7b` | Asistente con 83,3 % de éxito en 60 casos e informe |
| 5. Automatización y despliegue | CI/CD, imágenes firmadas, Kubernetes, GitOps e IaC | GitHub Actions, Trivy, Syft, Cosign, Kustomize, Argo CD, Kyverno, OpenTofu | Pipelines, manifiestos, repositorio GitOps y evidencia de firma |
| 6. Calidad y operación | Pruebas, observabilidad, *runbook* y simulacros | Vitest, OpenTelemetry, Grafana, `simulacros.sh` | SLI/SLO, tablero, *runbook* y resultados cronometrados |
Nota: Elaboración propia.

Las fases del proyecto fueron: (1) preparación y análisis, del 14 de septiembre al 25 de octubre de 2026, con la propuesta, los requisitos, la arquitectura y la estructura base de los tres repositorios; (2) construcción del producto mínimo viable, del 26 de octubre al 15 de noviembre, con un calendario de cuatro semanas y congelamiento de código el 15 de noviembre; (3) MLOps, LLMOps y plataforma, del 16 al 23 de noviembre, con los experimentos, el asistente RAG, GitOps, IaC y observabilidad; y (4) validación y documentación, del 23 al 24 de noviembre, con la verificación de requisitos, los simulacros, las evidencias y esta monografía.

## 1.6 Condiciones de entrega

Tabla: Entregables y productos del proyecto
| Producto | Ubicación | Descripción |
| --- | --- | --- |
| Código fuente | github.com/juanjosegl/RedNexus-Backend, RedNexus-Frontend y RedNexus-Platform | Tres repositorios públicos con ramas `developer`, `test` y `main`, *issues*, README y guía de contribución |
| Imágenes de contenedor | ghcr.io/juanjosegl/rednexus-backend y rednexus-frontend | Imágenes `linux/amd64` y `linux/arm64`, escaneadas, con SBOM y firmadas |
| Manifiestos y GitOps | `deploy/` y `iac/` en RedNexus-Platform | Kustomize (k3d, minikube y demo), políticas de Kyverno, Sealed Secrets y OpenTofu |
| Experimentos y modelo | `ml/` en RedNexus-Platform | Dataset sintético, 39 *runs* y el modelo `rednexus-matching` v1 en MLflow |
| Asistente RAG | `asistente-rag/` en RedNexus-Platform | Base de conocimiento, modelo, *golden dataset*, evaluaciones e informe en PDF |
| Documentación | `docs/entrega/` en RedNexus-Platform | Capítulos de entrega, matriz de los 15 entregables, *runbook*, guion de la demo y del video |
| Guía de instalación | README de RedNexus-Platform | Instalación en dos niveles (sin IA y con IA local), probada desde un clon limpio |
| Monografía | Este documento | Informe formal para la dirección del programa |
| Video y sustentación | Enlace en el README | Instalación siguiendo el README, demostración técnica y exposición ante jurado |
Nota: Elaboración propia. El anexo A relaciona cada uno de los 15 entregables del diplomado con su evidencia.

## 1.7 Alcance y limitaciones

**Alcance logrado.** A la fecha de entrega se cumplen los quince entregables mínimos del diplomado (anexo A). El producto mínimo viable es funcional de punta a punta con la IA real: registro con autorización, perfil, solicitudes por texto y voz, clasificación, emparejamiento con explicación, bandeja del colaborador, aceptación con asignación única, calificación, asistente con RAG, PQRS y exportación y eliminación de datos. Los diecisiete requisitos funcionales se verificaron contra la aplicación funcionando el 24 de noviembre de 2026.

**Limitaciones.**

- **Despliegue público.** El servidor compartido del diplomado (Dokploy) no quedó disponible para el equipo y no se contó con presupuesto para un clúster en la nube. Por eso no existe una URL pública permanente: la demostración se ejecuta en el equipo del líder con las mismas imágenes firmadas (con una URL temporal opcional mediante Cloudflare), y el flujo GitOps completo se valida en GitHub Actions con un clúster efímero (kind).
- **Hardware.** Los equipos tienen 8 GB de memoria. Esto obliga a usar modelos pequeños (3 mil millones de parámetros, cuantizados a 4 bits), un clúster de un solo nodo (sin alta disponibilidad real) y a no ejecutar a la vez el clúster local y la demo.
- **Conectividad.** La red doméstica del equipo es lenta para descargar modelos e imágenes de varios gigabytes, lo que condicionó qué componentes se probaron en vivo.
- **Datos.** Todas las métricas de IA se obtuvieron con datos sintéticos escritos por el equipo. Miden bien las diferencias entre configuraciones, pero sus valores absolutos deben confirmarse en un piloto con estudiantes reales, que no se realizó.
- **Licencia.** `qwen2.5:3b` se distribuye con una licencia de investigación que no permite uso comercial; una adopción institucional debe cambiar de modelo.
- **Calidad de los modelos pequeños.** El acierto del área de la clasificación es del 75 % y la explicación aún contiene afirmaciones no soportadas en el 17 % de los casos; el asistente acierta el 83,3 %. Son suficientes como apoyo, no como fuente de verdad.
- **Seguridad.** Los JWT no se pueden revocar antes de expirar y no hay moderación automática de contenido ofensivo.

## 1.8 Estructura del documento

El **capítulo 1** presenta el problema, la justificación, los objetivos, el marco de referencia, la metodología, las condiciones de entrega y el alcance. El **capítulo 2** desarrolla los fundamentos conceptuales (aprendizaje entre pares, recomendación semántica, modelos de lenguaje, RAG, nativo de la nube, DevSecOps, SRE y MLOps), el glosario, el estado del arte internacional, nacional y regional, y las brechas que aborda RedNexus. El **capítulo 3** describe el diseño: requisitos e historias de usuario, arquitectura y decisiones, Kubernetes y GitOps, DevSecOps y cadena de suministro, infraestructura como código, observabilidad y operación. El **capítulo 4** reporta la apropiación de MLOps y LLMOps: el tipo de aprendizaje automático, los experimentos y la selección de la configuración, el uso del LLM, el asistente RAG con su evaluación y las métricas TTFT y TPS. El **capítulo 5** muestra el desarrollo por módulo, con evidencias de interfaces, pipelines y despliegues. El **capítulo 6** reporta las pruebas y la validación: pruebas automatizadas, verificación de requisitos, integración con la IA real, seguridad, observabilidad y simulacros. El **capítulo 7** presenta las conclusiones generales y los trabajos futuros. Al final se incluyen las referencias y los anexos.
