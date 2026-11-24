# Capítulo 6. Pruebas y validación

Este capítulo reporta las pruebas realizadas para determinar la calidad del producto y demostrar su operación: las pruebas automatizadas, la verificación de los requisitos contra la aplicación funcionando, la prueba de integración con la IA real, la validación de seguridad de la cadena de suministro, la observabilidad y los simulacros de falla del *runbook*. Salvo que se indique otra cosa, las mediciones se hicieron el 24 de noviembre de 2026 en el equipo del líder (Mac M1 de 8 GB).

## 6.1 Estrategia de pruebas

Tabla: Niveles de prueba
| Nivel | Herramienta | Qué cubre | Cuándo corre |
| --- | --- | --- | --- |
| Unitarias del backend | Vitest | Servicios (autenticación, perfil, solicitudes, emparejamiento, ranking, transcripción, PQRS, soporte, datos personales) y proveedores de IA con dobles de prueba | Cada PR |
| *End-to-end* del backend | Vitest y Supertest | Arranque de la aplicación y salud | Cada PR |
| Componentes del frontend | Vitest y Vue Test Utils | Vistas y componentes: inicio de sesión, registro con autorización, perfil, solicitudes, nota de voz, bandeja, estrellas, ayuda y PQRS | Cada PR |
| Calidad estática | oxlint, ESLint, Prettier, `tsc` y `vue-tsc` | Estilo, tipos y errores comunes | Cada PR |
| Infraestructura | kubeconform, `tofu validate`, `docker compose config`, shellcheck | Manifiestos, IaC, Compose y *scripts* | Cada PR de Platform |
| Imagen | Trivy, Syft y Cosign | Vulnerabilidades, SBOM y firma | Cada construcción |
| Punta a punta de la plataforma | *GitOps (kind)* | Clúster, Argo CD, Kyverno, solicitud real y SLO | Cambios en `deploy/` o `iac/` |
| IA de emparejamiento | `ml/run_experiments.py` | precision@3, MRR, cobertura, fuera de tema y alucinaciones | Al cambiar el ranking o los modelos |
| Asistente RAG | `asistente-rag/evaluate_rag.py` | Éxito, fidelidad, completitud y latencia | Al cambiar documentos o el *prompt* |
| Funcionales | Guion y verificación de requisitos | Recorrido completo en la aplicación | Antes de cada entrega |
Nota: Elaboración propia. Ningún cambio entra a `developer`, `test` o `main` sin la integración continua en verde.

## 6.2 Resultados de las pruebas automatizadas

Tabla: Resultados de las pruebas automatizadas
| Repositorio | Pruebas | Resultado |
| --- | --- | --- |
| RedNexus-Backend | 23 archivos con 113 pruebas unitarias y 5 *end-to-end* | 118 de 118 aprobadas; lint y tipos sin errores |
| RedNexus-Frontend | 24 archivos con 69 pruebas de componentes | 69 de 69 aprobadas |
| RedNexus-Platform | Validación de manifiestos, OpenTofu, Compose, *scripts*, *golden dataset* y dataset de ML | Aprobada en `developer`, `test` y `main` |
Nota: Ejecución local sobre la rama `developer` el 24/11/2026; los mismos resultados se observan en GitHub Actions.

## 6.3 Verificación de los requisitos funcionales

Cada requisito funcional se verificó contra la aplicación funcionando, por la API y en el navegador, con usuarios sintéticos y una cuenta de prueba que se creó y se eliminó durante la verificación.

Tabla: Verificación de los requisitos funcionales
| ID | Prueba realizada | Resultado | Estado |
| --- | --- | --- | --- |
| RF-01 | Registro sin y con autorización | 400; luego 201 con token | Cumple |
| RF-02 | Inicio de sesión con clave incorrecta y correcta | 401; luego JWT | Cumple |
| RF-03 | Edición de bio y etiquetas | Guardado; *embedding* recalculado | Cumple |
| RF-04 | Perfil público de otra persona | Sin correo | Cumple |
| RF-05 | Duda de 4 caracteres y duda válida | 400; luego emparejada en 11 s | Cumple |
| RF-06 | Nota de voz WAV de 5 s | Transcrita y emparejada en 13 s | Cumple |
| RF-07 | Clasificación | Área, temas y nivel correctos | Cumple |
| RF-08 | Top 3 con explicación; IA apagada | 3 candidatos explicados; por etiquetas en 1,2 s | Cumple |
| RF-09 | Mis solicitudes | Lista con estados | Cumple |
| RF-10 | Bandeja del colaborador | Solicitud por responder | Cumple |
| RF-11 | Dos colaboradores aceptan la misma solicitud | El primero queda asignado; el segundo recibe 409 | Cumple |
| RF-12 | Calificar y calificar de nuevo | Guardada; luego 409 | Cumple |
| RF-13 | Cerrar por otro usuario y por la autora | 403; luego cerrada | Cumple |
| RF-14 | Pregunta al asistente | Respuesta correcta con fuentes en 24,6 s | Cumple |
| RF-15 | Radicar y consultar PQRS | PQRS-000001 radicada | Cumple |
| RF-16 | Exportar mis datos | JSON con perfil, solicitudes, candidaturas, calificaciones y PQRS | Cumple |
| RF-17 | Eliminar mi cuenta | 204; luego el inicio de sesión da 401 y el token viejo, 404 | Cumple |
Nota: Elaboración propia. Detalle en `docs/entrega/verificacion-requisitos.md`.

Los diecisiete requisitos se cumplen. Las rutas protegidas sin token responden 401.

## 6.4 Integración de punta a punta con la IA real

Además de la verificación por requisito, se recorrió el flujo completo como lo haría la demostración: Laura publicó por texto "No entiendo cómo unir tres tablas con una tabla intermedia en SQL para mi proyecto de bases de datos" y por voz "necesito ayuda para calcular subredes y máscaras en redes de computadores"; Ana, la primera candidata, aceptó; Julián intentó aceptar después y recibió el conflicto; Laura calificó con cinco estrellas, preguntó al asistente cómo calificar y radicó una sugerencia como PQRS. Todo el recorrido tomó unos cuatro minutos.

Tabla: Tiempos medidos en el recorrido con la IA real
| Paso | Tiempo |
| --- | --- |
| Solicitud por texto hasta tener candidatos (clasificar, vectorizar, ordenar y explicar) | 11 s |
| Nota de voz hasta tener candidatos (transcribir y emparejar) | 13 s |
| Otras cinco solicitudes con IA real | 11 a 17 s |
| Respuesta del asistente con RAG | 24,6 s |
| Primer *token* del LLM (mediana) | 0,17 s |
Nota: Elaboración propia. Todas las solicitudes cumplen el SLO de 30 s.

Se observaron dos limitaciones de calidad: la explicación de un candidato cuyo perfil es NoSQL dijo con honestidad que no domina SQL (el umbral lo dejó pasar con una similitud de 0,44), y en otra corrida el modelo escribió mal el apellido de un candidato en la explicación. Ambas confirman que la explicación es un apoyo y que la decisión final debe ser humana.

## 6.5 Validación de la seguridad y la cadena de suministro

Tabla: Escaneo de vulnerabilidades de las imágenes publicadas en main
| Imagen | Críticas | Altas | Medias y bajas | Tratamiento |
| --- | --- | --- | --- | --- |
| `rednexus-backend` (`sha-6a2ee94`, Alpine 3.24) | 0 | 11, todas en dependencias de Node con arreglo (`undici`, `brace-expansion`, `body-parser`, `multer`, `mysql2`, `effect`, `deepmerge-ts`); 0 en el sistema operativo | 30 | Corregidas en la tarea BE-24 con `npm audit fix` y una versión mínima de `effect`: la auditoría de producción queda en 0 y las 118 pruebas pasan |
| `rednexus-frontend` (`sha-c3ef50a`, Alpine 3.23) | 0 | 0 | 10, en OpenSSL de Alpine | Aceptadas por severidad; se corrigen en la próxima construcción |
Nota: Trivy 0.76 ejecutado el 24/11/2026 sobre las imágenes publicadas. El *pipeline* bloquea solo las críticas con arreglo; las altas se revisan en la bitácora del capítulo 8 de entrega.

La verificación de firmas desde un equipo ajeno al *pipeline* confirmó, para ambas imágenes, que las afirmaciones de Cosign son válidas, que existen en el registro de transparencia y que el certificado fue emitido para el *workflow* *Imagen* del repositorio por el emisor OIDC de GitHub. Cada imagen tiene dos entradas sobre el mismo *digest*: la firma y la atestación del SBOM en SPDX (523 paquetes en el backend y 71 en el frontend). En el clúster, Kyverno rechazó una imagen de un registro no permitido y una etiqueta sin firma (sección 5.7).

Antes, el 20/11/2026, el *pipeline* detuvo la publicación del frontend por vulnerabilidades críticas en paquetes de Alpine; se corrigieron actualizando los paquetes en la etapa final del `Dockerfile` sin dejar de ejecutar como usuario sin privilegios. Ese episodio mostró el control funcionando como estaba previsto.

## 6.6 Observabilidad

La observabilidad se validó en el *workflow* *GitOps (kind)*: tras publicar una solicitud, la métrica del SLI (`rednexus_match_latency_seconds`) apareció en Prometheus y la traza que une la petición de la API con el trabajo del *worker* apareció en Tempo, ambas consultadas por la API de Grafana. En el equipo local, el *log* del *worker* registra para cada emparejamiento la versión de la configuración, la estrategia (semántica o por etiquetas), los candidatos y la duración, lo que permitió medir los tiempos de este capítulo. Durante el ensayo del 24/11/2026 el disco de la máquina virtual de Docker se llenó al descargar la imagen de Grafana, por lo que el tablero no se capturó en el equipo local; la falla se agregó al *runbook*.

## 6.7 Simulacros del *runbook*

Los simulacros se automatizaron en `scripts/simulacros.sh` y se ejecutaron sobre la demo local, que usa las mismas imágenes que Kubernetes.

Tabla: Resultados de los simulacros de falla
| Simulacro | Resultado esperado | Resultado obtenido |
| --- | --- | --- |
| Caída del nodo de IA (Ollama detenido) | Candidatos por etiquetas | Solicitud emparejada en 1,2 s; el *log* dice `por tags`; al volver Ollama, la IA se reanuda |
| Caída del *worker* con trabajos en cola | La solicitud espera y se empareja al volver | Pendiente mientras el *worker* estuvo caído; emparejada 11 s después de encenderlo |
| Caída de la API | La API vuelve sin perder datos | Lista (`/api/health/ready`) 4,5 s después del arranque |
| Respaldo y restauración de PostgreSQL | Los conteos coinciden | Respaldo en 0,5 s; usuarios, solicitudes y perfiles iguales en la base restaurada |
| Reconstrucción desde cero (clon limpio) | El sistema vuelve con datos sintéticos | Clon en 2 s; aplicación lista en 10 s con las imágenes descargadas; con IA real, primera solicitud en 16 s |
| Reconstrucción del clúster GitOps | Aplicaciones sincronizadas | OpenTofu 52 s y Argo CD 86 s; 4 min de punta a punta |
Nota: Elaboración propia. Los simulacros de borrado de *pods* en Kubernetes no se cronometraron porque el clúster local y la demo no caben juntos en 8 GB.

El simulacro dejó tres lecciones que se incorporaron al *runbook*: recrear un servicio sin las variables de la demo lo deja con la IA de respaldo, por lo que se debe reiniciar con `start` o con el *script* de la demo; después de recargar los datos de prueba, los *embeddings* de los perfiles se recalculan bajo demanda; y el disco de la máquina virtual de Docker es un recurso que puede agotarse.

## 6.8 Sostenibilidad de la solución

Tabla: Uso de memoria de los servicios en la demo con IA real
| Servicio | Memoria en uso | Límite |
| --- | --- | --- |
| API | 84 MB | 384 MB |
| *Worker* | 88 MB | 384 MB |
| Web (Nginx) | 12 MB | 64 MB |
| PostgreSQL | 30 MB | 512 MB |
| Redis | 6 MB | 128 MB |
| Open WebUI (asistente) | 782 MB | Sin límite estricto |
| Ollama (fuera de Docker) | Unos 2 GB con `qwen2.5:3b` cargado | – |
Nota: `docker stats` del 24/11/2026. La aplicación completa, sin el asistente ni los modelos, usa menos de 250 MB.

La aplicación es liviana; el costo dominante es el modelo de lenguaje, que corre en hardware existente sin GPU dedicada. Esto confirma la viabilidad de un piloto con un servidor pequeño para la aplicación y un equipo con GPU integrada como nodo de IA.

## 6.9 Conclusiones del capítulo

- Las 187 pruebas automatizadas y la verificación de los 17 requisitos contra la aplicación funcionando muestran que el producto cumple lo especificado.
- Con la IA real, todas las solicitudes medidas recibieron candidatos entre 11 y 17 s, dentro del SLO de 30 s; sin IA, el respaldo responde en poco más de un segundo.
- La cadena de suministro funciona como control y no solo como documentación: detuvo una publicación con vulnerabilidades críticas, permitió encontrar y corregir 11 vulnerabilidades altas, y sus firmas son verificables por terceros.
- Los simulacros demostraron la degradación controlada, la recuperación de la cola, la restauración de respaldos y la reconstrucción desde cero en segundos, y aportaron lecciones concretas al *runbook*.
- Quedan sin validar con usuarios reales la utilidad percibida y el efecto sobre la permanencia, y sin cronometrar los simulacros en Kubernetes local.
