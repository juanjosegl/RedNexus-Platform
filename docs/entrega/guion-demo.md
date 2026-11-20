# Guion de la demo y de la sustentación (DOC-04)

**Duración:** 15 minutos de exposición + 10 de preguntas. **Formato:** diapositivas con la plantilla institucional de Unicomfacauca.

## Reparto sugerido

| Minuto | Tema | Quién | Apoyo |
| --- | --- | --- | --- |
| 0:00–2:00 | Problema con datos (SPADIES, tutorías entre pares) y la idea | Integrante 1 | Capítulo 1 |
| 2:00–5:00 | Arquitectura: C4 N2 y N3, despliegue 4+1, 3 ADR clave (IA local, pgvector, degradación) | Juanjo | Diagramas 2, 3, 5 |
| 5:00–10:00 | **Demo de punta a punta** (abajo) | Juanjo + Integrante 2 | Ambiente de Dokploy |
| 10:00–12:00 | MLOps: dataset, experimentos en MLflow, configuración ganadora | Integrante 3 | Capítulo 6 |
| 12:00–13:30 | DevSecOps: CI, GHCR, Trivy, SBOM, Cosign; privacidad (Ley 1581) | Integrante 4 | Capítulos 5 y 8 |
| 13:30–15:00 | Problemas encontrados y lo que sigue | Integrante 5 | Sección final |

## Demo (5 minutos)

Antes de empezar: abrir la API dos minutos antes (Render se duerme), Ollama encendido, cuentas de prueba (`*.demo@rednexus.dev`, contraseña `demo12345`) y una pestaña privada para el segundo usuario.

1. **Registro** de una cuenta nueva: mostrar la autorización de datos (Ley 1581).
2. Como **Estudiante Demo**, publicar: *"No entiendo cómo unir tres tablas cuando hay una tabla intermedia entre estudiantes y cursos"*. Mostrar el estado Pendiente y, en segundos, los 3 candidatos con su explicación.
3. **Nota de voz:** grabar *"Necesito ayuda para dividir una red en subredes"* y publicarla.
4. En la otra pestaña, como **Ana**, abrir **Ayudar**, aceptar y mostrar el correo del autor.
5. Volver al autor: ver el contacto de Ana y **calificar** con 5 estrellas.
6. **Asistente:** en Ayuda, preguntar *"¿Qué pasa con mis datos?"*.
7. **Degradación (opcional, 30 s):** cerrar Ollama, publicar otra duda y mostrar que igual llegan candidatos (log `por tags`).
8. **CI/CD:** mostrar un PR con los checks en verde, el run de "Imagen" (Trivy, SBOM, firma) y el despliegue en Dokploy.

## Problemas encontrados (para contar)

- Equipos de 8 GB: todo en un clúster de un nodo y Ollama fuera del clúster para usar Metal.
- Mac (ARM) y Windows (x86): imágenes multiarquitectura y dos herramientas de Kubernetes.
- Prisma 7 en Docker generaba importaciones `.ts`: se fijó `importFileExtension = "js"`.
- El modelo de embeddings que elegimos al principio (`nomic-embed-text`) resultó peor en español que un modelo multilingüe; **lo descubrimos midiendo**, no suponiendo.
- La licencia de `qwen2.5:3b` no permite uso comercial: lo encontramos al hacer la ficha de modelos.
- Coordinación de 5 personas en 3 repos: contratos en Swagger antes de la lógica y tablero de issues.

## Preguntas probables

| Pregunta | Respuesta corta |
| --- | --- |
| ¿Por qué no usar ChatGPT? | Datos personales (Ley 1581), costo por uso y dependencia; la IA local cabe en 8 GB |
| ¿Qué pasa si la IA se equivoca? | Propone 3, explica por qué, el ayudante puede rechazar y el estudiante decide; medimos precision@3 y alucinaciones |
| ¿Cómo saben que el emparejamiento es bueno? | Dataset sintético de 100 solicitudes con la respuesta correcta: precision@3 en MLflow (capítulo 6) |
| ¿Por qué pgvector y no una base vectorial? | Un solo motor, transacciones y respaldos juntos; el volumen es pequeño |
| ¿Qué pasa si se cae el nodo de IA? | Degradación controlada: etiquetas y plantilla |
| ¿Cómo protegen los datos? | Autorización, exportar y borrar, correo solo al aceptar, notas de voz que no se guardan, IA local |

## Ensayo

| Fecha | Duración total | Qué falló | Ajuste |
| --- | --- | --- | --- |
| | | | |
