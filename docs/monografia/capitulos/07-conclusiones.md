# Capítulo 7. Conclusiones y trabajos futuros

## 7.1 Conclusiones generales

**Sobre la pregunta del proyecto.** Es posible construir y operar, con recursos de un equipo académico, una plataforma web que recomiende a cada estudiante los compañeros más adecuados para su duda usando inteligencia artificial ejecutada en infraestructura propia. RedNexus lo demuestra con un producto mínimo viable funcional de punta a punta, cuyos diecisiete requisitos funcionales se verificaron contra la aplicación en ejecución y cuyo emparejamiento, sobre un conjunto sintético de 100 solicitudes, propone al colaborador correcto entre los tres primeros en el 94 % de los casos.

**Sobre los objetivos específicos.**

1. *Requisitos y arquitectura.* Se documentaron el contexto, las partes interesadas, 17 requisitos funcionales, los no funcionales según ISO/IEC 25010, 19 historias de usuario, 12 decisiones de arquitectura y 11 diagramas C4 y 4+1, actualizados con lo construido.
2. *Aplicación web.* Se implementaron la cuenta y el perfil únicos, las solicitudes por texto y por voz, la bandeja del colaborador, la aceptación con asignación única garantizada por una transacción, la calificación, el asistente de ayuda, las PQRS y la exportación y eliminación de datos, con 187 pruebas automatizadas.
3. *Emparejamiento con IA.* Treinta y nueve experimentos registrados en MLflow llevaron la precision@3 de 0,81 a 0,94 y el rechazo de dudas fuera de tema del 10 % al 90 %, y redujeron las explicaciones con afirmaciones no soportadas del 30 % al 17 %. La configuración quedó registrada como `rednexus-matching` v1 y se aplica por variables de entorno.
4. *Asistente RAG.* El asistente alcanzó un 83,3 % de éxito en 60 casos evaluados con un modelo juez, por encima de la meta del 70 %, con rechazo correcto de todas las preguntas de seguridad y fuera de alcance.
5. *Automatización y despliegue.* Cada imagen se construye para dos arquitecturas, se escanea, se inventaría con un SBOM y se firma; Argo CD la despliega desde Git en un clúster instalado con OpenTofu, Kyverno rechaza lo que no está firmado y los secretos viajan cifrados. Todo se reproduce desde cero en cuatro minutos en GitHub Actions.
6. *Calidad y operación.* Se definió un SLI y un SLO de 30 segundos con su tablero, un *runbook* y seis simulacros cronometrados que confirmaron la degradación controlada, la recuperación de la cola, la restauración de respaldos y la reconstrucción desde cero.

**Sobre la IA local.** Los modelos pequeños cuantizados hacen viable la IA en un portátil de 8 GB: `qwen2.5:3b` responde su primer *token* en 0,17 s y genera 24 *tokens* por segundo, y el emparejamiento completo tarda entre 11 y 17 s. Su calidad es suficiente como apoyo, no como fuente de verdad, por lo que el diseño la rodea de explicación, límite de tres candidatos, decisión humana y un respaldo que funciona sin modelos. El procesamiento local evita transferir datos personales a terceros, pero el cumplimiento de la Ley 1581 se logró con decisiones de diseño explícitas (autorización, acceso, supresión y minimización), no por el solo hecho de ser local.

**Sobre el método.** Medir cambió decisiones que parecían obvias: el modelo de *embeddings* elegido al inicio resultó el peor en español, y un *prompt* más estricto empeoró a un modelo pequeño. Registrar experimentos, versionar *prompts* y evaluar con conjuntos de referencia convirtió el ajuste de la IA en un proceso reproducible.

**Sobre la ingeniería.** La combinación de una imagen firmada para todos los roles, despliegue declarativo y una guía de instalación probada desde un clon limpio hace que lo evaluado sea exactamente lo desplegado. Esa fue también la respuesta a la principal limitación del proyecto, la falta de un servidor público: cualquier evaluador reproduce el sistema en minutos y el despliegue GitOps completo se verifica en cada cambio de infraestructura.

**Sobre el trabajo en equipo.** Organizar el trabajo en *issues* pequeños, ramas por tarea, *pull requests* con integración continua obligatoria y documentación en el mismo repositorio permitió coordinar a cinco personas con equipos distintos y dejó trazabilidad de cada aporte en 123 *pull requests*.

## 7.2 Trabajos futuros

### 7.2.1 Corto plazo (un semestre)

- **Piloto con estudiantes reales** de un programa de ingeniería, con bienestar universitario como responsable del tratamiento de los datos, para medir el tiempo hasta la primera ayuda, la tasa de aceptación y la satisfacción.
- **Despliegue público permanente** en un servidor de la institución o en un VPS pequeño, reutilizando `docker-compose.dokploy.yml` o el overlay `demo` con Argo CD.
- **Mejoras de la interfaz:** mostrar con formato las respuestas del asistente, transmitirlas en *streaming* y notificar por correo al colaborador propuesto.
- **Publicar el video** de instalación y demostración y completar el ensayo cronometrado con las diapositivas institucionales.

### 7.2.2 Mediano plazo (un año)

- **Mejorar la clasificación**, que hoy acierta el área en el 75 % de los casos, con un modelo de 7B o con ejemplos en el *prompt*, y medir el efecto en la precision@3.
- **Recalibrar con datos reales** los pesos y el umbral del emparejamiento usando las aceptaciones y calificaciones del piloto, y monitorear el sesgo de popularidad.
- **Cambiar a modelos con licencia comercial** (por ejemplo, `qwen2.5:7b` con Apache 2.0) si la institución adopta la plataforma.
- **Revocación de sesiones**, moderación de contenido ofensivo y una política formal de tratamiento de datos registrada ante la autoridad cuando aplique.
- **Simulacros en Kubernetes** cronometrados (borrado de *pods*, reconstrucción del clúster local) y alertas sobre el presupuesto de error del SLO.

### 7.2.3 Largo plazo

- **Red regional:** abrir la plataforma a otras instituciones del Cauca con espacios separados por institución, en el espíritu de la "minga" académica que dio origen al proyecto.
- **Nodo de IA compartido** con GPU para varias instituciones, manteniendo el procesamiento dentro de la región.
- **Medir el impacto en la permanencia** de los participantes frente a sus cohortes, en colaboración con las oficinas de bienestar y con los datos de SPADIES.
- **Recomendación grupal**, para conformar grupos de estudio alrededor de un mismo tema, y aplicaciones móviles nativas.
