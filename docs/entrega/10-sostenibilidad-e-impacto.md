# 10. Sostenibilidad, impacto y plan de adopción (DOC-03)

Los requisitos de certificación piden un "Plan estratégico de desarrollo sostenible y marketing" con criterios ESG (ambientales, sociales y de gobernanza). Este capítulo lo aterriza a RedNexus.

> Nota: el alcance exacto de este requisito no se confirmó con el coordinador (parece venir de otro programa); se deja como análisis de sostenibilidad del proyecto.

## 10.1 Ambiental (E)

| Práctica | Efecto |
| --- | --- |
| Modelos pequeños (3B parámetros, embeddings de 137 a 277 M) cuantizados (Q4_K_M) | Menos energía por consulta que un modelo de decenas de miles de millones de parámetros |
| IA local en un portátil con Apple Silicon (Metal) en vez de GPU en la nube | Aprovecha hardware que ya existe |
| Todo cabe en 8 GB de RAM con límites de memoria por servicio | Sin servidores sobredimensionados |
| El worker procesa por cola solo cuando hay trabajo | Sin cómputo ocioso |
| La nota de voz no se almacena | Menos almacenamiento |
| Medición de latencia por trabajo (ms en el log) | Base para medir el costo energético (PL-07) |

## 10.2 Social (S)

| Objetivo | Indicador | Meta del piloto |
| --- | --- | --- |
| Reducir el tiempo para resolver una duda | Mediana entre publicar y la primera aceptación | Menos de 24 h |
| Aumentar la ayuda entre pares | Solicitudes aceptadas / publicadas | 60 % o más |
| Calidad de la ayuda | Promedio de calificaciones | 4 de 5 o más |
| Inclusión | Notas de voz para quien escribe con dificultad o va en movimiento; interfaz accesible con teclado | 100 % de las vistas usables con teclado |
| Contribuir a la permanencia | Deserción de los participantes frente a la cohorte (con bienestar universitario) | Seguimiento por semestre |

Alineación con los Objetivos de Desarrollo Sostenible: **ODS 4** (educación de calidad: aprendizaje entre pares), **ODS 10** (reducción de desigualdades: ayuda gratuita sin depender de pagar tutorías) y **ODS 9** (innovación con IA local y abierta).

## 10.3 Gobernanza (G)

- **Datos:** cumplimiento de la Ley 1581 (autorización, acceso, supresión, minimización), datos sintéticos en demos, IA local sin terceros (capítulo 5).
- **IA responsable:** cada recomendación explica su porqué, el estudiante decide, la configuración se elige con experimentos registrados (MLflow) y se puede revertir; riesgos documentados (CONPES 4144).
- **Ingeniería:** PRs revisados, CI obligatorio, imágenes escaneadas, con SBOM y firmadas; decisiones registradas en ADR.
- **Licencias:** inventario de modelos y su licencia; código del proyecto en repositorios públicos.

## 10.4 Plan de adopción y difusión

| Fase | Duración | Acciones | Indicador de éxito |
| --- | --- | --- | --- |
| 1. Piloto | 1 semestre | Con estudiantes del diplomado y un programa de ingeniería; monitores invitados como ayudantes | 50 perfiles reales con habilidades, 100 solicitudes |
| 2. Institucional | 1 año | Acuerdo con bienestar universitario como responsable del tratamiento; política de datos formal; integración con monitorías | 3 programas usando la red |
| 3. Red regional | Después | Abrir a otras instituciones del Cauca (la "minga" académica) | Convenios firmados |

**Canales de difusión:** inducción de primer semestre, monitores de cada asignatura, redes de la universidad y la página de ayuda con el asistente.

**Modelo de sostenibilidad:** costo de infraestructura bajo (un VPS pequeño y un nodo de IA local); el mantenimiento puede quedar en semilleros de investigación o en el diplomado como proyecto vivo. No se cobra a los estudiantes.

**Costo estimado de operación mensual (piloto):** VPS de 4 GB para la aplicación (USD 5 a 20) + un equipo existente como nodo de IA (costo eléctrico). Las APIs comerciales equivalentes costarían por cada consulta y exigirían transferir los datos fuera del país.
