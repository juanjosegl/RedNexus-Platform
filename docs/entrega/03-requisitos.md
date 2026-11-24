# 3. Requisitos

## 3.1 Requisitos funcionales

Cada requisito se verifica con las pruebas automáticas indicadas y con el guion de la demo. El 24/11/2026 los 17 se verificaron contra la aplicación funcionando: ver [verificacion-requisitos.md](verificacion-requisitos.md) (todos ✅).

| ID | Requisito | Criterio de aceptación | Endpoint / ruta | Prueba |
| --- | --- | --- | --- | --- |
| RF-01 | Registrarse con nombre, correo y contraseña, aceptando el tratamiento de datos | El correo es único; la contraseña se guarda cifrada (bcrypt) y nunca se devuelve; sin aceptar la autorización responde 400 | `POST /api/auth/register`, `/register` | `auth.service.spec.ts` |
| RF-02 | Iniciar sesión | Con credenciales válidas devuelve un JWT; con inválidas, 401 | `POST /api/auth/login`, `/login` | `auth.service.spec.ts`, `LoginView` |
| RF-03 | Ver y editar mi perfil (bio y etiquetas) | Al cambiar bio o etiquetas se encola el cálculo del embedding | `GET/PATCH /api/users/me`, `/perfil` | `users.service.spec.ts`, `ProfileForm.spec.ts` |
| RF-04 | Ver el perfil público de otro usuario | No muestra el correo | `GET /api/users/:id` | `users.service.spec.ts` |
| RF-05 | Publicar una duda por texto | Entre 10 y 1000 caracteres; queda en `PENDING` y se encola el emparejamiento | `POST /api/help-requests` | `help-requests.service.spec.ts` |
| RF-06 | Publicar una duda por nota de voz | webm, ogg, mp3, wav o m4a de hasta 10 MB; se transcribe y sigue el flujo normal; el audio no se guarda | `POST /api/help-requests/voice` | `transcription.service.spec.ts` |
| RF-07 | Clasificar la duda con IA | Cada solicitud queda con área, temas y nivel; si el modelo responde algo inválido se reintenta una vez | worker `match` | `ollama.provider.spec.ts`, `mock.provider.spec.ts` |
| RF-08 | Proponer los 3 mejores ayudantes con una explicación | Nunca el propio autor; con la IA apagada igual hay candidatos por etiquetas | worker `match` | `matching.service.spec.ts`, `ranking.spec.ts` |
| RF-09 | Seguir el estado de mis solicitudes | La vista se actualiza sola cada 5 s mientras está `PENDING` | `GET /api/help-requests/mine`, `/:id` | `HelpRequestDetailView.spec.ts` |
| RF-10 | Ver las solicitudes en las que me propusieron | Lista por responder y respondidas | `GET /api/matches/incoming`, `/ayudar` | `IncomingMatchesView.spec.ts` |
| RF-11 | Aceptar o rechazar una solicitud | Solo el candidato responde, una sola vez; si otro ya aceptó, 409; al aceptar se comparten los correos | `POST /api/matches/:id/accept`, `/reject` | `matches.service.spec.ts` |
| RF-12 | Calificar la ayuda recibida | De 1 a 5, solo el autor, solo si fue aceptada y una vez; el promedio sube o baja el puntaje del ayudante | `POST /api/ratings` | `ratings.service.spec.ts`, `StarRating.spec.ts` |
| RF-13 | Cerrar una solicitud | Solo el autor | `POST /api/help-requests/:id/close` | `help-requests.service.spec.ts` |
| RF-14 | Preguntar al asistente de soporte | Responde con la documentación y cita sus fuentes; si Open WebUI falla, responde el respaldo | `POST /api/support/chat`, `/ayuda` | `support.service.spec.ts`, `evaluate_rag.py` |
| RF-15 | Radicar y consultar PQRS | Número de radicado legible (PQRS-000001); solo el autor ve las suyas | `POST/GET /api/pqrs`, `/pqrs` | `pqrs.service.spec.ts`, `PqrsView.spec.ts` |
| RF-16 | Descargar mis datos | Devuelve perfil, solicitudes, candidaturas, calificaciones y PQRS en JSON | `GET /api/users/me/export` | `users.service.spec.ts` |
| RF-17 | Eliminar mi cuenta | Borra la cuenta y todo lo asociado; la sesión deja de funcionar | `DELETE /api/users/me` | `users.service.spec.ts` |

## 3.2 Requisitos no funcionales (ISO/IEC 25010)

| Característica | ID | Requisito | Cómo se mide |
| --- | --- | --- | --- |
| Eficiencia de desempeño | RNF-01 | El 95 % de las solicitudes recibe candidatos en menos de 30 s | Log del worker (`... candidatos por semantic en N ms`); trazas en PL-07 |
| | RNF-02 | Todo el sistema cabe en un equipo de 8 GB de RAM | Límites de memoria en Compose y Kubernetes |
| Adecuación funcional | RNF-03 | El ayudante correcto aparece en el top 3 en al menos el 80 % de los casos del dataset sintético | `precision_at_3` en MLflow (IA-07) |
| | RNF-04 | El asistente de soporte acierta en al menos el 70 % del golden dataset | `evaluate_rag.py` (IA-08) |
| Fiabilidad | RNF-05 | Si la IA no responde, el emparejamiento sigue (respaldo por etiquetas y explicación por plantilla) | `matching.service.spec.ts`, simulacro del runbook |
| | RNF-06 | Los trabajos de IA se reintentan 3 veces con espera exponencial y se recuperan al reiniciar el worker | `queue.constants.ts`, `ai.processor.ts` |
| Seguridad | RNF-07 | Contraseñas con bcrypt, rutas protegidas con JWT, validación de toda entrada | Pruebas de auth y `ValidationPipe` |
| | RNF-08 | El texto del usuario va delimitado en los prompts para mitigar la inyección de prompts | Prompts de `ollama.provider.ts`, casos de seguridad del golden dataset |
| | RNF-09 | Imágenes sin vulnerabilidades críticas con arreglo, con SBOM y firmadas | Workflow "Imagen" (Trivy, Syft, Cosign) |
| | RNF-10 | Contenedores sin root, sin escalada de privilegios, API con sistema de archivos de solo lectura | `deploy/base` |
| Compatibilidad | RNF-11 | La misma imagen corre en linux/amd64 (Windows) y linux/arm64 (Mac M1) | buildx multiplataforma |
| Mantenibilidad | RNF-12 | Todo PR pasa lint, tipos, pruebas y build antes de fusionar | Rulesets con `build-test` obligatorio |
| Portabilidad | RNF-13 | El sistema se reconstruye desde cero con un comando | `docker compose up -d --build`, `scripts/k8s-up.sh` |
| Usabilidad | RNF-14 | La interfaz funciona en celular y escritorio y se puede usar con teclado | Componentes base y pruebas de accesibilidad |

## 3.3 Historias de usuario

| ID | Historia | Criterios de aceptación | RF |
| --- | --- | --- | --- |
| HU-01 | Como **estudiante**, quiero registrarme y autorizar el uso de mis datos, para usar la red sabiendo qué se hace con ellos | Veo la política, debo marcar la casilla, y luego entro con mi sesión | RF-01, RF-02 |
| HU-02 | Como **ayudante**, quiero describir lo que sé con mis palabras y etiquetas, para que la IA me encuentre cuando alguien lo necesite | Edito bio y etiquetas; mi perfil público no muestra mi correo | RF-03, RF-04 |
| HU-03 | Como **estudiante con una duda**, quiero escribirla como me salga, para recibir a quien mejor me pueda ayudar | Recibo 3 candidatos con una explicación de por qué cada uno | RF-05, RF-07, RF-08, RF-09 |
| HU-04 | Como **estudiante que va caminando**, quiero dejar mi duda en una nota de voz, para no tener que escribir | Grabo hasta 60 s, la escucho y la publico; aparece transcrita con candidatos | RF-06 |
| HU-05 | Como **ayudante**, quiero ver las dudas donde me propusieron y decidir, para ayudar solo cuando puedo | Acepto o rechazo con confirmación; si acepto veo el correo del autor | RF-10, RF-11 |
| HU-06 | Como **estudiante ayudado**, quiero calificar la ayuda, para que la red recomiende mejor a los demás | Califico una vez de 1 a 5 y veo mi calificación | RF-12 |
| HU-07 | Como **usuario nuevo**, quiero preguntarle a un asistente cómo funciona la plataforma, para no depender de otra persona | El asistente responde con la documentación y me remite a PQRS si no sabe | RF-14, RF-15 |
| HU-08 | Como **titular de mis datos**, quiero descargarlos o borrar mi cuenta, para ejercer mis derechos de la Ley 1581 | Descargo un JSON con todo; al borrar, no puedo volver a entrar | RF-16, RF-17 |
| HU-09 | Como **operador**, quiero que el sistema siga funcionando si la IA se cae, para que la demo y los usuarios no se queden sin respuesta | Con Ollama apagado, las solicitudes igual reciben candidatos | RNF-05 |

## 3.4 Matriz de trazabilidad

| HU | RF | Código backend | Código frontend | Pruebas | Issue |
| --- | --- | --- | --- | --- | --- |
| HU-01 | RF-01, RF-02 | `modules/auth` | `features/auth` | `auth.service.spec.ts`, `LoginView` | BE-01, FE-02 |
| HU-02 | RF-03, RF-04 | `modules/users` | `features/profile` | `users.service.spec.ts`, `ProfileForm.spec.ts` | BE-02, FE-03 |
| HU-03 | RF-05, RF-07 a RF-09 | `modules/help-requests`, `modules/matching`, `modules/ai` | `features/help-requests` | `matching.service.spec.ts`, `ranking.spec.ts`, `HelpRequest*.spec.ts` | BE-03, IA-01 a IA-04, FE-04 |
| HU-04 | RF-06 | `modules/ai/transcription*` | `VoiceNoteRecorder.vue` | `transcription.service.spec.ts`, `HelpRequestCreateView.spec.ts` | BE-04, IA-05, FE-05 |
| HU-05 | RF-10, RF-11 | `modules/matching/matches*` | `features/matches` | `matches.service.spec.ts`, `IncomingMatchesView.spec.ts` | BE-05, FE-06 |
| HU-06 | RF-12 | `modules/ratings` | `features/ratings` | `ratings.service.spec.ts`, `StarRating.spec.ts` | BE-06, FE-07 |
| HU-07 | RF-14, RF-15 | `modules/support`, `modules/pqrs` | `features/support`, `features/pqrs` | `support.service.spec.ts`, `evaluate_rag.py` | BE-07, BE-12, FE-08, FE-13, IA-08 |
| HU-08 | RF-16, RF-17 | `modules/users` | `features/profile` | `users.service.spec.ts` | DOC-02 |
| HU-09 | RNF-05 | `matching.service.ts` (respaldo) | – | `matching.service.spec.ts`, runbook | IA-04 |
