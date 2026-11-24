# Verificación de los requisitos contra la aplicación funcionando (DOC-12)

**Fecha:** 24/11/2026. **Ambiente:** demo local con las imágenes de `main` (`ghcr.io/juanjosegl/rednexus-backend:sha-6a2ee94`, `rednexus-frontend:sha-c3ef50a`), Ollama (`qwen2.5:3b`, `paraphrase-multilingual`), whisper.cpp y Open WebUI. **Método:** cada requisito se probó por la API (http://localhost:8088/api) con usuarios sintéticos y se revisó en el navegador (capturas en [evidencias/](evidencias)). La cuenta de prueba `verificacion.demo@rednexus.dev` se creó y se eliminó durante la verificación.

## Requisitos funcionales

| ID | Requisito | Qué se hizo | Resultado | Verificado |
| --- | --- | --- | --- | --- |
| RF-01 | Registro con autorización de datos | Registro con `acceptsDataPolicy: false` y luego `true` | 400; luego 201 con `accessToken` y `user` | ✅ |
| RF-02 | Iniciar sesión | Contraseña incorrecta y correcta | 401; luego JWT | ✅ |
| RF-03 | Editar perfil | `PATCH /api/users/me` con bio y etiquetas | Guardado; el embedding se recalcula en el worker | ✅ |
| RF-04 | Perfil público sin correo | `GET /api/users/:id` de Ana | Campos `id, name, bio, tags, rating`; sin correo | ✅ |
| RF-05 | Duda por texto | Texto de 4 caracteres; texto válido | 400; luego `PENDING` → `MATCHED` en 11 s | ✅ |
| RF-06 | Duda por nota de voz | WAV de 5 s a `POST /api/help-requests/voice` | Transcrita y emparejada en 13 s ([captura](evidencias/app-06-solicitud-voz.png)) | ✅ |
| RF-07 | Clasificación con IA | Revisión de la solicitud por texto | `bases-de-datos`, temas `join, sql, tablas`, nivel intermedio | ✅ |
| RF-08 | Top 3 con explicación | Revisión de candidatos | 3 candidatos con puntaje y explicación; con Ollama apagado, candidatos por etiquetas en 1,2 s | ✅ |
| RF-09 | Seguir mis solicitudes | `GET /api/help-requests/mine` y la vista de detalle | 8 solicitudes de Laura con su estado ([captura](evidencias/app-08-mis-solicitudes.png)) | ✅ |
| RF-10 | Solicitudes donde me propusieron | `GET /api/matches/incoming` como Daniela | 1 solicitud por responder ([captura](evidencias/app-07-bandeja-ayudar.png)) | ✅ |
| RF-11 | Aceptar o rechazar | Ana acepta; luego Julián acepta la misma solicitud | Ana recibe el correo de la autora; Julián recibe 409 | ✅ |
| RF-12 | Calificar | Laura califica con 5 y luego intenta calificar otra vez | Guardada; la segunda vez, 409 "Ya calificaste esta solicitud" | ✅ |
| RF-13 | Cerrar solicitud | Otro usuario intenta cerrarla; luego la autora | 403; luego `CLOSED` | ✅ |
| RF-14 | Asistente de soporte | Pregunta "¿Cómo califico a la persona que me ayudó?" | Pasos correctos con fuentes, 24,6 s ([captura](evidencias/app-12-asistente-ayuda.png)) | ✅ |
| RF-15 | PQRS | Radicar sugerencia y consultar las mías | `PQRS-000001`, estado `RADICADA` | ✅ |
| RF-16 | Descargar mis datos | `GET /api/users/me/export` | JSON con perfil, solicitudes, candidaturas, calificaciones dadas y recibidas, PQRS y aviso | ✅ |
| RF-17 | Eliminar mi cuenta | `DELETE /api/users/me` | 204; después el login da 401 y el token viejo, 404 | ✅ |

Ningún requisito falló, así que no se abrieron issues. Las rutas protegidas sin token responden 401.

## Requisitos no funcionales con medición

| ID | Requisito | Medición | Resultado |
| --- | --- | --- | --- |
| RNF-01 | 95 % de las solicitudes con candidatos en menos de 30 s | 6 solicitudes con IA real hoy: 11 a 17 s; en *GitOps (kind)*, 1 s con respaldo | ✅ |
| RNF-02 | Todo cabe en 8 GB | `docker stats`: API 84 MB, worker 88 MB, web 12 MB, Postgres 30 MB, Redis 6 MB, Open WebUI 782 MB; Ollama fuera de Docker | ✅ (con poco margen: ver runbook) |
| RNF-03 | precision@3 ≥ 80 % | MLflow, `rednexus-matching` v1 | 0,94 ✅ |
| RNF-04 | Asistente ≥ 70 % en el golden dataset | `evaluate_rag.py`, 60 casos | 83,3 % ✅ |
| RNF-05 | Emparejamiento sin IA | Simulacro con Ollama apagado | ✅ |
| RNF-06 | Reintentos y recuperación del worker | Simulacro con el worker caído | ✅ |
| RNF-09 | Imágenes sin críticas, con SBOM y firmadas | Trivy, Syft y `cosign verify` | ✅ (11 altas del backend corregidas en BE-24) |
