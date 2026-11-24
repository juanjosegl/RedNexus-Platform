# Capítulo 2. Fundamentos conceptuales del proyecto

Este capítulo presenta los conceptos en los que se apoya RedNexus. No pretende resumir cada área del diplomado, sino explicar los elementos que el proyecto usa y por qué: cómo se representa el significado de un texto, cómo se ordenan los candidatos, cómo se evita que el modelo invente, cómo se mide todo ello y con qué prácticas se construye y opera la plataforma.

## 2.1 Marco teórico

### 2.1.1 Aprendizaje entre pares

El aprendizaje entre pares (*peer learning*) es la adquisición de conocimientos mediante la ayuda activa entre personas de condición similar que no son docentes profesionales. Topping (1996) distingue varias modalidades en educación superior (tutoría entre compañeros del mismo nivel, de distinto nivel, uno a uno o en grupo) y reporta beneficios tanto para quien recibe la ayuda como para quien la da, que consolida lo aprendido al explicarlo. Machado (2022) evaluó con métodos de emparejamiento estadístico el programa de Tutorías entre Pares de la Universidad de la República y encontró una reducción de entre 8 % y 11 % en la probabilidad de deserción.

RedNexus adopta la modalidad de tutoría uno a uno entre estudiantes de distinto nivel (o de docentes y egresados) y le agrega lo que los programas institucionales suelen resolver a mano: **identificar al compañero adecuado**. Una misma persona puede solicitar ayuda en un tema y ofrecerla en otro, y las calificaciones reconocen a quienes ayudan.

### 2.1.2 Sistemas de recomendación basados en contenido

Un sistema de recomendación presenta a un usuario los elementos más relevantes para su necesidad. Los sistemas **basados en contenido** comparan las características del elemento con las de la necesidad; los **colaborativos** aprovechan el comportamiento de usuarios parecidos. Cuando lo que se recomienda son personas y ambas partes deben estar de acuerdo, se habla de recomendación **recíproca**, como en las plataformas de empleo o de tutorías.

En RedNexus el elemento recomendado es el perfil de un colaborador (su descripción libre y sus etiquetas) y la necesidad es el texto de la duda. Como no hay historial suficiente para un enfoque colaborativo, el sistema es basado en contenido; la reciprocidad se resuelve con el flujo de aceptación: el colaborador propuesto decide si acepta. Las calificaciones recibidas aportan una señal de calidad que se combina con la afinidad temática:

> puntaje = *w* · similitud + (1 − *w*) · calificación promedio / 5

donde *w* es el peso de la similitud (0,8 en la configuración elegida) y la similitud es el resultado de la búsqueda descrita a continuación. Se proponen los tres puntajes más altos que superen un umbral mínimo.

### 2.1.3 Representación semántica del texto: *embeddings*

Un *embedding* es un vector de números reales que representa el significado de un texto; los textos con significados parecidos quedan cerca en ese espacio aunque no compartan palabras. Sentence-BERT (Reimers y Gurevych, 2019) mostró cómo obtener *embeddings* de oraciones completas con redes siamesas, y la destilación de conocimiento permite extender un modelo entrenado en inglés a decenas de idiomas (Reimers y Gurevych, 2020). El modelo `paraphrase-multilingual` que usa RedNexus pertenece a esa familia y produce vectores de 768 dimensiones; `nomic-embed-text` (Nussbaum et al., 2024), entrenado sobre todo en inglés, se comparó en los experimentos del capítulo 4.

La cercanía entre dos vectores se mide con la **similitud del coseno**, que vale 1 cuando apuntan en la misma dirección y 0 cuando son ortogonales. Para no comparar la duda contra todos los perfiles uno a uno, las bases vectoriales usan índices aproximados como **HNSW** (*Hierarchical Navigable Small World*; Malkov y Yashunin, 2020), que organiza los vectores en un grafo jerárquico y encuentra los vecinos más cercanos en tiempo sublineal. RedNexus guarda los vectores en PostgreSQL con la extensión **pgvector**, que ofrece el tipo `vector(768)`, el operador de distancia coseno `<=>` y el índice HNSW.

### 2.1.4 Búsqueda híbrida y clasificación previa

Los *embeddings* capturan sinónimos y paráfrasis, pero pueden pasar por alto términos técnicos exactos (SQL, VLAN, Karnaugh) que la coincidencia de palabras sí premia. La **búsqueda híbrida** combina ambas señales:

> similitud = α · coseno(*embeddings*) + (1 − α) · coincidencia léxica

Además, una **clasificación previa** con un modelo de lenguaje extrae el área, los temas y el nivel de la duda; agregarlos al texto antes de calcular su *embedding* (consulta enriquecida) acerca la duda a los perfiles del área correcta. El capítulo 4 muestra que ambas técnicas mejoraron el acierto.

### 2.1.5 Modelos de lenguaje pequeños, cuantización y ejecución local

Un modelo de lenguaje de gran tamaño (LLM) genera texto prediciendo el siguiente *token* a partir de los anteriores. Los modelos "pequeños", de 1 a 8 mil millones de parámetros, pueden ejecutarse en un computador personal si se **cuantizan**, es decir, si sus pesos se representan con menos bits (por ejemplo, 4 bits en el formato Q4_K_M), con una pérdida moderada de calidad. Qwen2.5 (Qwen Team, 2024) es una familia de modelos abiertos con buen desempeño en español; RedNexus usa `qwen2.5:3b` (1,9 GB cuantizado) para clasificar dudas, explicar recomendaciones y responder en el asistente, y `qwen2.5:7b` como juez en las evaluaciones.

**Ollama** es un servidor local que descarga, cuantiza y ejecuta estos modelos con una API HTTP; en el Mac M1 aprovecha la GPU integrada mediante Metal. La ejecución local evita enviar datos personales a terceros y elimina el costo por consumo, a cambio de asumir el cómputo, el mantenimiento y una calidad inferior a la de los modelos comerciales más grandes. Para que la aplicación no dependa de un nodo de IA que puede estar apagado, el sistema aplica **degradación controlada**: si los modelos fallan, empareja por etiquetas y explica con una plantilla.

Dos métricas describen la experiencia de un LLM en producción: el **TTFT** (*time to first token*), tiempo desde la petición hasta el primer fragmento de respuesta, que es lo que el usuario percibe como espera; y el **TPS** (*tokens per second*), velocidad de generación, que determina cuánto tarda una respuesta larga.

### 2.1.6 Generación aumentada por recuperación (RAG)

Un LLM responde con lo que aprendió en su entrenamiento y puede **alucinar**, es decir, producir afirmaciones plausibles pero falsas. La generación aumentada por recuperación (Lewis et al., 2020) reduce ese riesgo: antes de generar, se recuperan fragmentos relevantes de una base de conocimiento y se entregan al modelo como contexto, con la instrucción de responder solo con ellos. Un sistema RAG se caracteriza por los documentos, el **tamaño de fragmento** y el **solapamiento** (en *tokens*), el modelo de *embeddings* y el número de fragmentos recuperados (*top-k*).

RedNexus usa RAG en dos lugares. En la **explicación de cada candidato**, el "documento" recuperado es el perfil del colaborador, y el *prompt* exige no atribuirle nada que su perfil no diga. En el **asistente de soporte**, la base de conocimiento son ocho documentos sobre el uso de la plataforma, fragmentados en bloques de 400 *tokens* con 60 de solapamiento y servidos por Open WebUI.

### 2.1.7 Evaluación de sistemas de IA

La recuperación se evalúa con métricas de *ranking* sobre un conjunto en el que se conoce la respuesta correcta: **precision@k** (fracción de consultas con al menos un elemento correcto entre los *k* primeros; en RedNexus, *k* = 3), **hit@1** (el primero es correcto) y **MRR** (*mean reciprocal rank*, promedio de 1/posición del primer correcto). La generación se evalúa con un **conjunto de referencia** (*golden dataset*) de preguntas con su respuesta esperada y con un **LLM como juez** (Zheng et al., 2023), que califica la fidelidad al contexto y la completitud con criterios explícitos, en la línea de marcos como RAGAS (Es et al., 2024). Un juez automático también se equivoca, por lo que sus criterios se calibraron revisando casos a mano.

### 2.1.8 Reconocimiento automático del habla

Whisper (Radford et al., 2023) es un modelo de reconocimiento del habla entrenado con 680 000 horas de audio multilingüe con supervisión débil, robusto al ruido y a los acentos. whisper.cpp es su implementación en C/C++ que corre en CPU y en GPU de Apple; RedNexus usa el modelo `ggml-base` (142 MB) para transcribir las notas de voz, que luego siguen el mismo flujo que una duda escrita.

### 2.1.9 Arquitectura nativa de la nube y Kubernetes

Una aplicación **nativa de la nube** se compone de servicios empaquetados en contenedores, declarados como configuración y gestionados por un orquestador que los arranca, los reinicia cuando fallan y los conecta. **Kubernetes** es el orquestador de referencia, heredero de la experiencia de Google con Borg y Omega (Burns et al., 2016). Sus objetos principales son el *Deployment* (réplicas sin estado, como la API), el *StatefulSet* (servicios con datos, como PostgreSQL), el *Service* y el *Ingress* (enrutamiento), y las sondas de vida y de disponibilidad (*liveness* y *readiness*). **Kustomize** compone los manifiestos con una base común y *overlays* por ambiente. k3d, kind y minikube ejecutan Kubernetes en un solo equipo.

### 2.1.10 GitOps

GitOps es un modelo de operación en el que el estado deseado del sistema se declara en Git, que es la única fuente de verdad, y un agente lo reconcilia continuamente con lo que corre (OpenGitOps, 2021). Sus cuatro principios son: declarativo, versionado e inmutable, extraído automáticamente (*pull*) y reconciliado de forma continua. **Argo CD** implementa ese agente para Kubernetes: compara una carpeta del repositorio con el clúster, aplica las diferencias y, con *selfHeal*, revierte los cambios manuales (*drift*). Los secretos no pueden guardarse en Git en texto plano; **Sealed Secrets** los cifra con una llave pública cuya llave privada solo conoce el controlador del clúster.

### 2.1.11 DevSecOps y seguridad de la cadena de suministro

DevSecOps integra la seguridad en cada etapa del ciclo de entrega en lugar de dejarla al final. En la cadena de suministro de software, los controles clave son: el **escaneo de vulnerabilidades** de imágenes y dependencias (Trivy); el **SBOM** (*Software Bill of Materials*), inventario de los componentes de un artefacto (Syft, formato SPDX); la **firma** de los artefactos para probar su origen, que Sigstore simplifica con certificados efímeros ligados a la identidad OIDC del *pipeline* y un registro de transparencia público (Newman et al., 2022); y las **políticas de admisión** que impiden ejecutar artefactos no firmados (Kyverno). Estas prácticas concretan las del NIST SSDF (NIST, 2022).

### 2.1.12 Infraestructura como código

La infraestructura como código (IaC) describe los recursos en archivos versionados que una herramienta aplica de forma idempotente. **OpenTofu**, bifurcación abierta de Terraform, calcula un plan de cambios y lo aplica; si el plan da cero cambios, la infraestructura coincide con el código. RedNexus usa OpenTofu para instalar las piezas del clúster GitOps y para declarar las reglas de protección de las ramas de los tres repositorios.

### 2.1.13 Observabilidad e ingeniería de confiabilidad

La observabilidad permite entender el estado interno de un sistema a partir de sus **métricas**, **registros** (*logs*) y **trazas**. **OpenTelemetry** es el estándar abierto para emitirlas; una traza sigue una petición a través de varios servicios, incluso cuando pasa por una cola. La ingeniería de confiabilidad (SRE; Beyer et al., 2016) define un **SLI** (indicador medible del servicio), un **SLO** (objetivo para ese indicador) y un **presupuesto de error** (cuánto se puede incumplir). En RedNexus el SLI es la latencia del emparejamiento y el SLO es que el 95 % de las solicitudes reciba candidatos en menos de 30 segundos. Un ***runbook*** documenta cómo diagnosticar y resolver las fallas comunes, y los **simulacros** comprueban que funciona.

### 2.1.14 MLOps y LLMOps

MLOps aplica las prácticas de DevOps al ciclo de vida de los modelos: datos versionados, experimentos comparables, registro de modelos, despliegue reproducible y monitoreo. **MLflow** (Zaharia et al., 2018) registra cada experimento (*run*) con sus parámetros, métricas y artefactos, y ofrece un **Model Registry** con versiones. LLMOps extiende esas prácticas a los modelos de lenguaje: versionado de *prompts*, evaluación con conjuntos de referencia y jueces, seguimiento de latencia (TTFT, TPS) y mitigación de riesgos como la inyección de *prompts*.

### 2.1.15 Glosario de términos y siglas

Tabla: Glosario de términos y siglas
| Término | Definición |
| --- | --- |
| ADR | *Architecture Decision Record*: registro de una decisión de arquitectura con su contexto, alternativas y consecuencias |
| API REST | Interfaz de programación sobre HTTP con recursos y verbos (GET, POST, PATCH, DELETE) |
| Argo CD | Herramienta de GitOps que sincroniza Kubernetes con lo declarado en Git |
| BullMQ | Librería de colas de trabajos sobre Redis |
| C4 | Modelo de diagramas de arquitectura por niveles: contexto, contenedores, componentes y código |
| CI/CD | Integración y entrega continuas |
| Cosign | Herramienta de Sigstore para firmar y verificar imágenes de contenedor |
| Cuantización | Representar los pesos de un modelo con menos bits para reducir memoria y tiempo |
| Degradación controlada | Seguir funcionando con menor calidad cuando falla un componente |
| *Drift* | Diferencia entre lo declarado en Git y lo que corre en el clúster |
| *Embedding* | Vector numérico que representa el significado de un texto |
| GHCR | GitHub Container Registry |
| GitOps | Operación declarada en Git y reconciliada por un agente |
| *Golden dataset* | Conjunto de casos con la respuesta esperada para evaluar un sistema de IA |
| HNSW | Índice aproximado de vecinos cercanos en grafos jerárquicos |
| IaC | Infraestructura como código |
| JWT | *JSON Web Token*, token firmado que prueba la identidad del usuario |
| Kustomize | Composición de manifiestos de Kubernetes con base y *overlays* |
| Kyverno | Motor de políticas de admisión para Kubernetes |
| LLM | Modelo de lenguaje de gran tamaño |
| MLflow | Plataforma de registro de experimentos y modelos |
| MRR | *Mean Reciprocal Rank* |
| Ollama | Servidor local de modelos de lenguaje y de *embeddings* |
| Open WebUI | Interfaz autoalojada para modelos locales con bases de conocimiento para RAG |
| OpenTelemetry | Estándar abierto de trazas, métricas y registros |
| OpenTofu | Herramienta de infraestructura como código |
| pgvector | Extensión de PostgreSQL para vectores y búsqueda por similitud |
| precision@3 | Fracción de solicitudes con el colaborador correcto entre los 3 propuestos |
| PQRS | Peticiones, quejas, reclamos y sugerencias |
| RAG | Generación aumentada por recuperación |
| SBOM | Inventario de componentes de un artefacto de software |
| Sealed Secrets | Secretos de Kubernetes cifrados para guardarlos en Git |
| SLI / SLO | Indicador y objetivo de nivel de servicio |
| TPS / TTFT | *Tokens* por segundo / tiempo al primer *token* |
| Trivy | Escáner de vulnerabilidades |
| whisper.cpp | Implementación local del modelo de reconocimiento de voz Whisper |
| *Worker* | Proceso que atiende la cola de trabajos de IA aparte de la API |
Nota: Elaboración propia. El glosario completo del proyecto está en `docs/entrega/11-glosario-y-referencias.md`.

## 2.2 Estado del arte

La revisión buscó soluciones que conecten a estudiantes que necesitan ayuda con compañeros que pueden darla, en especial las que usan técnicas de recomendación o inteligencia artificial, en tres ámbitos.

### 2.2.1 Ámbito internacional

- **Plataformas comerciales de preguntas y respuestas.** Servicios como Brainly o los foros académicos de curso tipo Piazza permiten publicar una pregunta y que otros respondan. Funcionan como foros: la pregunta queda a la vista de quien entre, no se dirige a una persona concreta y los datos se procesan en servidores del proveedor.
- **RiPPLE (Universidad de Queensland, Australia).** Plataforma de aprendizaje entre pares que recomienda actividades y compañeros a partir de las brechas de conocimiento y los intereses de cada estudiante (Khosravi, 2017; Khosravi et al., 2019). Opera dentro de un curso y se apoya en el desempeño medido en ejercicios.
- **SOS Tutoría UC (Universidad Católica de Asunción, Paraguay).** Aplicación integrada a la plataforma europea WeNet que recomienda tutores combinando la competencia académica con rasgos de personalidad (modelo de los cinco grandes) y criterios de diversidad (Achón et al., 2023). En sus pruebas, el criterio de competencia funcionó bien y el de personalidad requirió ajustes.
- **Sistemas de emparejamiento con aprendizaje automático.** Trabajos recientes proponen asignar tutores con algoritmos de aprendizaje automático a partir de cuestionarios (por ejemplo, TutorTech en Virginia Tech) o con recomendación basada en grafos para emparejar estudiantes en cursos de lectura académica (Universidad de Kioto). La mayoría están en etapa de piloto o prototipo.

### 2.2.2 Ámbito nacional

- **Programas institucionales de acompañamiento entre pares.** Universidades como la del Valle y la Piloto de Colombia sostienen estrategias de acompañamiento y monitorías entre pares orientadas a reducir la deserción, documentadas en los congresos CLABES. La asignación del par suele hacerse por inscripción y por la oficina responsable, no por recomendación automática.
- **Tutoriza.** Plataforma web para formar a los tutores en competencias de acompañamiento, implementada en 2023 en la Universidad de los Andes y en instituciones de Chile y México (Tutoriza, 2023). Su foco es la formación del tutor, no el emparejamiento.
- **Tutorías virtuales entre pares.** La Universidad Nacional documentó tutorías académicas virtuales entre pares en un curso de Matemáticas Básicas, mediadas por videoconferencia.

### 2.2.3 Ámbito regional (Cauca)

En Popayán, la Universidad del Cauca documenta tutorías masivas de matemáticas en las que estudiantes de semestres superiores resuelven dudas de otros, y publica convocatorias de monitorías por facultad con requisitos académicos. En Unicomfacauca el acompañamiento se apoya en monitorías y asesorías docentes. No se encontró, en la revisión realizada, una plataforma digital de emparejamiento entre pares en las instituciones de la región.

### 2.2.4 Comparación

Tabla: Comparación de RedNexus con soluciones similares
| Característica | Foros de preguntas | RiPPLE | SOS Tutoría UC | Programas institucionales | RedNexus |
| --- | --- | --- | --- | --- | --- |
| La duda llega a personas concretas | No | Sí | Sí | Sí (asignación manual) | Sí (top 3 automático) |
| Comprende el significado en español | No aplica | Parcial | No reportado | No aplica | Sí (*embeddings* multilingües y búsqueda híbrida) |
| Explica por qué recomienda | No | Parcial | No | No | Sí (RAG sobre el perfil) |
| IA ejecutada sin terceros | No | No aplica | No | No aplica | Sí (Ollama y whisper.cpp) |
| Nota de voz | No | No | No | No | Sí |
| Funciona si falla la IA | No aplica | No reportado | No reportado | Sí | Sí (respaldo por etiquetas) |
| Derechos de datos implementados (Ley 1581) | No | No aplica | No aplica | Según la institución | Sí (autorización, exportar, suprimir) |
| Código abierto y reproducible | No | Parcial | No | No | Sí (tres repositorios públicos) |
Nota: Elaboración propia a partir de las fuentes citadas en la sección 2.2. "No reportado" indica que la fuente no lo menciona.

## 2.3 Brechas y desafíos

Del estado del arte se desprenden cuatro brechas que orientan el diseño de RedNexus:

1. **Del foro a la recomendación dirigida.** Las soluciones más usadas son foros donde la pregunta espera a que alguien la vea. Las que recomiendan personas existen sobre todo como prototipos en otros países y dependen de datos de desempeño o de personalidad que una institución pequeña no tiene. RedNexus recomienda a partir de lo que cada persona escribe sobre sí misma, sin datos adicionales.
2. **Comprensión del español con recursos modestos.** Los trabajos revisados no reportan cómo se comportan sus modelos en español ni con hardware limitado. RedNexus mide, con un conjunto etiquetado, qué modelo de *embeddings* y qué técnica de búsqueda funcionan mejor en español en un equipo de 8 GB.
3. **Privacidad por diseño.** Ninguna solución revisada procesa los datos sin terceros ni implementa explícitamente los derechos del titular de la legislación colombiana. RedNexus ejecuta toda la IA en infraestructura propia e implementa autorización, acceso, supresión y minimización.
4. **Producto reproducible y operable.** Los prototipos académicos rara vez incluyen la ingeniería necesaria para operarlos: integración continua, imágenes verificables, despliegue declarativo, observabilidad y procedimientos de falla. RedNexus incorpora esas prácticas desde el inicio y documenta su reproducción.

El principal desafío que queda abierto es la validación con usuarios reales: ninguna de las soluciones revisadas, incluida RedNexus, reporta todavía un efecto medido sobre la permanencia de los estudiantes atribuible a la recomendación automática.

## 2.4 Conclusiones del capítulo

- La evidencia sobre el aprendizaje entre pares justifica facilitarlo; el problema práctico es encontrar a la persona adecuada a tiempo, y ese es el espacio de RedNexus.
- La combinación de *embeddings* multilingües, búsqueda híbrida, clasificación previa y calificaciones permite recomendar personas a partir de texto libre sin datos históricos, y RAG permite explicar cada recomendación sin inventar.
- Los modelos pequeños cuantizados hacen viable la IA local en hardware modesto, con una calidad que debe medirse y con un mecanismo de respaldo para cuando no estén disponibles.
- Las prácticas nativas de la nube, GitOps, DevSecOps, SRE y MLOps proveen el marco para que el producto sea reproducible, verificable y operable, no solo funcional.
- El estado del arte muestra soluciones de foro, prototipos internacionales de recomendación y programas institucionales con asignación manual; ninguno reúne recomendación semántica en español, explicación, IA sin terceros y cumplimiento de la Ley 1581, que son las brechas que aborda este proyecto.
