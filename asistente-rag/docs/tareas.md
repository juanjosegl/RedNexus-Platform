# Tareas del asistente de soporte (RAG)

Cada tarea es un issue en el [tablero](https://github.com/users/juanjosegl/projects/1) con la etiqueta
`asistente-rag`. Se trabaja igual que siempre: **Assign yourself** → rama desde `developer` → un commit por paso →
PR a `developer` con `Closes #N`. Las tareas DOC y la IA-08 son en RedNexus-Platform, dentro de la carpeta
`asistente-rag/`.

> **Antes de empezar:** revisa que `git config user.email` sea el correo de tu cuenta de GitHub. Si no, tus
> commits no cuentan como tuyos y el profe no te ve en el repositorio.

## Resumen

| Issue | Tarea | Repo | Asignada a |
| --- | --- | --- | --- |
| [#30](https://github.com/juanjosegl/RedNexus-Backend/issues/30) | BE-07 Módulo `support` | Backend | Juanjo · hecho |
| [#25](https://github.com/juanjosegl/RedNexus-Frontend/issues/25) | FE-08 Página de ayuda | Frontend | Juanjo · hecho |
| [#21](https://github.com/juanjosegl/RedNexus-Platform/issues/21) | IA-08 RAG, modelo y evaluación | Platform | Juanjo · hecho |
| — | BE-12 / FE-13 PQRS (endpoint y página) | Backend y Frontend | Juanjo |
| [#28](https://github.com/juanjosegl/RedNexus-Frontend/issues/28) | FE-11 Burbuja de mensaje | Frontend | Victor Daniel Fernandez · hecho |
| [#22](https://github.com/juanjosegl/RedNexus-Platform/issues/22) | DOC-05 Registro y perfil | Platform | Maria Alejandra Guzman · hecho |
| [#27](https://github.com/juanjosegl/RedNexus-Frontend/issues/27) | FE-10 Preguntas sugeridas | Frontend | Jose Sebastian Fernandez · hecho |
| [#31](https://github.com/juanjosegl/RedNexus-Backend/issues/31) | BE-08 Respuestas del mock | Backend | Juanjo · hecho |
| [#32](https://github.com/juanjosegl/RedNexus-Backend/issues/32) | BE-09 Variables de entorno | Backend | Juanjo · hecho |
| [#33](https://github.com/juanjosegl/RedNexus-Backend/issues/33) | BE-10 Pruebas e2e | Backend | Juanjo · hecho |
| [#34](https://github.com/juanjosegl/RedNexus-Backend/issues/34) | BE-11 Documentación Swagger | Backend | Juanjo · hecho |
| [#26](https://github.com/juanjosegl/RedNexus-Frontend/issues/26) | FE-09 Enlace "Ayuda" en el menú | Frontend | Jose Sebastian Fernandez · hecho |
| [#29](https://github.com/juanjosegl/RedNexus-Frontend/issues/29) | FE-12 Preguntas frecuentes | Frontend | Maria Paula Andrade · hecho |
| [#23](https://github.com/juanjosegl/RedNexus-Platform/issues/23) | DOC-06 Solicitudes de ayuda | Platform | Maria Alejandra Guzman |
| [#24](https://github.com/juanjosegl/RedNexus-Platform/issues/24) | DOC-07 Calificaciones | Platform | Juanjo · hecho |
| [#25](https://github.com/juanjosegl/RedNexus-Platform/issues/25) | DOC-08 Preguntas frecuentes | Platform | Juanjo · hecho |

Las tareas de los integrantes son de tamaño **S** y dependen de BE-07, FE-08 e IA-08, que ya están en `developer`.

---

## Núcleo (Juanjo)

### BE-07 · Módulo `support` del asistente
Rama `feature/BE-07-asistente-soporte` · Backend · L

- `POST /api/support/chat` con `{ message, history? }` → `{ answer, sources, provider, latencyMs }`.
- Proveedor `openwebui` (reenvía al modelo `asistente-rednexus` de Open WebUI) y `mock` (por defecto).
- Si el proveedor falla responde 503 con un mensaje amable.

### FE-08 · Página de ayuda
Rama `feature/FE-08-pagina-ayuda` · Frontend · M

- Ruta `/ayuda` con el chat, historial de hasta 10 turnos, fuentes y estados de carga y error.
- Deja marcados los lugares donde entran FE-10, FE-11 y FE-12.

### BE-12 y FE-13 · PQRS
Ramas `feature/BE-12-pqrs` y `feature/FE-13-pqrs` · M

- `POST /api/pqrs`, `GET /api/pqrs/mine` y `GET /api/pqrs/:id`, con número de radicado (`PQRS-000001`) y estados
  Radicada, En revisión y Respondida.
- Página `/pqrs` con el formulario y "Mis PQRS", enlazada desde la ayuda. Es el canal al que remite el asistente.

### IA-08 · RAG, modelo personalizado y evaluación
Rama `feature/IA-08-asistente-rag` · Platform · L

- Open WebUI con la knowledge `Base RedNexus`, el modelo `asistente-rednexus` y el system prompt.
- Documentos `normas.md`, `privacidad.md`, `pqrs.md` y `emparejamiento.md`, y 18 casos difíciles.
- Corridas con 400/60 y 300/30, ajuste hasta superar el 70 % y secciones D, E y F del informe.
- Validación del golden dataset en el CI de Platform y sección de aportes en el README principal.

---

## Backend

### BE-08 · Respuestas del mock del asistente
Rama `feature/BE-08-respuestas-mock` · S

Hoy el mock siempre responde lo mismo. La idea es que responda algo útil según la pregunta, para que la demo
desplegada (sin Open WebUI) tenga sentido.

Archivos: `src/modules/support/providers/mock.provider.ts` y un nuevo `mock.provider.spec.ts` al lado.

**Commits**
- [ ] `feat(support): respuestas del mock por palabra clave`
- [ ] `test(support): respuestas del mock`

**Cómo**
1. Crea una lista de temas, cada uno con palabras clave y una respuesta corta (1 o 2 frases). Mínimo 5 temas:
   registro, perfil, solicitudes, candidatos/emparejamiento y calificaciones.
   ```ts
   const TOPICS = [
     { keywords: ['registr', 'cuenta'], answer: 'Para registrarte...' },
     // ...
   ];
   ```
2. En `ask`, toma el último mensaje del usuario, pásalo a minúsculas y sin tildes
   (`text.normalize('NFD').replace(/[̀-ͯ]/g, '')`) y devuelve la respuesta del primer tema cuya palabra
   clave aparezca. Si ninguna aparece, devuelve `MOCK_DEFAULT_ANSWER`.
3. Las respuestas deben coincidir con lo que dicen los documentos de `asistente-rag/knowledge-base/` en
   RedNexus-Platform.
4. En el spec, una prueba por tema y una para la respuesta por defecto.

**Listo cuando** `npm test` pasa y, con `SUPPORT_PROVIDER=mock`, "¿cómo me registro?" responde sobre el registro.

### BE-09 · Variables de entorno del asistente
Rama `feature/BE-09-variables-asistente` · S

El código ya lee estas variables (`src/config/configuration.ts`), pero no están documentadas.

| Variable | Valor por defecto | Qué es |
| --- | --- | --- |
| `SUPPORT_PROVIDER` | `mock` | `mock` u `openwebui` |
| `OPENWEBUI_URL` | `http://localhost:3001` | URL de Open WebUI, sin `/api` |
| `OPENWEBUI_API_KEY` | (vacío) | API key de Open WebUI. **Nunca** se sube a GitHub |
| `SUPPORT_MODEL` | `asistente-rednexus` | Modelo personalizado de Open WebUI |
| `SUPPORT_TIMEOUT_MS` | `60000` | Tiempo máximo de espera de la respuesta |

**Commits**
- [ ] `docs(config): variables del asistente en .env.example` → agrégalas a `.env.example` con un comentario, como
  las de Ollama.
- [ ] `chore(deploy): variables del asistente en dokploy y render` → en `docker-compose.dokploy.yml` agrégalas a
  `x-api-env` con `${VARIABLE:-valor}` y documéntalas en el comentario de arriba; en `render.yaml` agrega
  `SUPPORT_PROVIDER` con valor `mock`.
- [ ] `docs(readme): cómo conectar el asistente a open webui` → en el `README.md`, una sección corta con la tabla
  de arriba y los pasos para usar `SUPPORT_PROVIDER=openwebui`.

**Listo cuando** el CI pasa y alguien del equipo puede conectar el backend a Open WebUI leyendo solo el README.

### BE-10 · Pruebas e2e del asistente
Rama `feature/BE-10-e2e-asistente` · S

Archivo nuevo: `test/support.e2e-spec.ts`. Copia la estructura de `test/health.e2e-spec.ts`, pero importando
`ConfigModule.forRoot({ isGlobal: true, load: [configuration] })` y `SupportModule`, y activando
`app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }))` antes de `app.init()`.

**Commits**
- [ ] `test(support): e2e de /support/chat con el mock`

**Casos** (`POST /support/chat`)
1. `{ message: '¿Cómo me registro?' }` → 200 y `provider` es `mock`.
2. `{ message: '' }` → 400.
3. `{ message: 'hola', history: [{ role: 'sistema', content: 'x' }] }` → 400 (rol inválido).
4. `history` con 11 turnos → 400 (máximo 10).

**Listo cuando** `npm run test:e2e` pasa.

### BE-11 · Documentación Swagger del asistente
Rama `feature/BE-11-swagger-asistente` · S

Archivo: `src/modules/support/support.controller.ts`.

**Commits**
- [ ] `docs(support): respuestas de error en swagger`

**Cómo** Agrega al método `chat` los decoradores `@ApiBadRequestResponse`, `@ApiUnauthorizedResponse` y
`@ApiServiceUnavailableResponse` de `@nestjs/swagger`, cada uno con una `description` en español (mira
`ratings.controller.ts` como ejemplo). Borra el comentario que dice "se documentan en BE-11".

**Listo cuando** en `/api/docs` la ruta `POST /api/support/chat` muestra las respuestas 200, 400, 401 y 503.
Toma una captura de esa pantalla: va en el informe.

---

## Frontend

### FE-09 · Enlace "Ayuda" en el menú
Rama `feature/FE-09-enlace-ayuda` · S

Archivos: `src/layouts/DefaultLayout.vue` y `src/layouts/__tests__/DefaultLayout.spec.ts`.

**Commits**
- [ ] `feat(layout): enlace a la ayuda en el menú` → un `RouterLink` a `/ayuda` con el texto "Ayuda", en el bloque
  de usuario con sesión, antes del enlace al perfil (igual que el de "Solicitudes").
- [ ] `test(layout): enlace a la ayuda` → con sesión iniciada aparece "Ayuda"; sin sesión no aparece.

**Listo cuando** `npm test` pasa y el enlace lleva a la página de ayuda.

### FE-10 · Preguntas sugeridas
Rama `feature/FE-10-preguntas-sugeridas` · S

Archivos nuevos en `src/features/support/`: `suggestions.ts`, `SuggestedQuestions.vue` y su prueba en `__tests__/`.

**Commits**
- [ ] `feat(support): preguntas sugeridas` → `suggestions.ts` exporta un arreglo con 5 preguntas frecuentes.
  `SuggestedQuestions.vue` las muestra como botones con las clases `chips` y `chip` (ya existen en
  `rednexus.css`), recibe la prop `disabled` y emite `select` con el texto de la pregunta.
- [ ] `feat(support): mostrar las preguntas sugeridas en la ayuda` → en `SupportView.vue`, reemplaza el comentario
  `FE-10` por `<SuggestedQuestions :disabled="sending" @select="send" />`.
- [ ] `test(support): preguntas sugeridas` → muestra las 5 preguntas y al hacer clic emite `select` con el texto.

**Listo cuando** `npm test` pasa y al hacer clic en una sugerencia el asistente responde.

### FE-11 · Burbuja de mensaje del chat
Rama `feature/FE-11-mensaje-chat` · S

Archivos nuevos: `src/features/support/ChatMessage.vue` y su prueba en `__tests__/`.

**Commits**
- [ ] `feat(support): componente de mensaje del chat` → props `role` (`'user' | 'assistant'`), `content` y
  `sources?`. Muestra arriba "Tú" o "Asistente", el texto y, si hay, "Fuentes: …". Mueve aquí los estilos
  `.bubble` de `SupportView.vue`.
- [ ] `refactor(support): usar ChatMessage en la ayuda` → en `SupportView.vue`, reemplaza el bloque marcado con
  `FE-11` por `<ChatMessage v-for="(entry, index) in messages" :key="index" v-bind="entry" />`.
- [ ] `test(support): mensaje del chat` → muestra "Tú" para el usuario, "Asistente" y las fuentes para el asistente.

**Listo cuando** `npm test` pasa y el chat se ve igual o mejor que antes.

### FE-12 · Preguntas frecuentes y acceso desde el inicio
Rama `feature/FE-12-preguntas-frecuentes` · S

Archivos: nuevo `src/features/support/FaqList.vue` con su prueba, `SupportView.vue` y `src/features/home/HomeView.vue`.

**Commits**
- [ ] `feat(support): preguntas frecuentes en la ayuda` → `FaqList.vue` con 5 preguntas y respuestas sacadas de
  tu documento `preguntas-frecuentes.md` (DOC-08), cada una en un `<details>` con `<summary>`. En
  `SupportView.vue`, reemplaza el comentario `FE-12` por `<FaqList />`.
- [ ] `feat(home): acceso a la ayuda desde el inicio` → en `HomeView.vue`, un tercer botón
  `<BaseButton variant="quiet" :to="{ name: 'support' }">¿Necesitas ayuda?</BaseButton>`.
- [ ] `test(support): preguntas frecuentes` → muestra las 5 preguntas.

**Listo cuando** `npm test` pasa y desde el inicio se llega a la ayuda.

---

## Platform: base de conocimiento, casos e informe

Las cuatro tareas DOC son iguales; cambia el tema. Repo RedNexus-Platform, rama `docs/DOC-0X-<tema>` desde
`developer`. Todas las rutas de esta sección son dentro de `asistente-rag/`.

| Tarea | Documento | Archivo de casos | Categoría | Sección del informe |
| --- | --- | --- | --- | --- |
| DOC-05 | `registro-y-perfil.md` | `golden-dataset/<tu-usuario>.jsonl` | `registro_perfil` | A. Portada y B. Índice |
| DOC-06 | `solicitudes-de-ayuda.md` | `golden-dataset/<tu-usuario>.jsonl` | `solicitudes` | C. Introducción |
| DOC-07 | `calificaciones.md` | `golden-dataset/<tu-usuario>.jsonl` | `calificaciones` | F.2 Capturas de la interfaz |
| DOC-08 | `preguntas-frecuentes.md` | `golden-dataset/<tu-usuario>.jsonl` | `problemas_comunes` | G. Conclusiones |

**Commits**
- [ ] `docs(kb): <tema>` → copia `knowledge-base/_plantilla.md` con el nombre de la tabla y escríbelo (400 a 900
  palabras). Mira `knowledge-base/emparejamiento.md` como ejemplo. Solo lo que la app hace de verdad: pruébala.
- [ ] `test(dataset): casos de <tema>` → 8 casos en tu archivo, con la categoría de la tabla; al menos 1 con
  `"behavior": "rechazar"`. Formato y consejos en `golden-dataset/README.md`.
- [ ] `docs(informe): <sección>` → tu sección en `docs/informe/` (las instrucciones están dentro del archivo).
- [ ] `docs(readme): aporte de <tu nombre>` → en el `README.md` principal de RedNexus-Platform, sección
  "Asistente de soporte con RAG", reemplaza tu línea por tu nombre completo, tu usuario de GitHub y lo que
  aportaste (solo tu línea, para no chocar con los demás).

**Qué tiene que decir cada documento**
- **Registro y perfil:** crear cuenta, iniciar y cerrar sesión, editar descripción y etiquetas, para qué sirve el
  perfil en el emparejamiento, errores comunes (correo ya registrado, contraseña incorrecta, sesión vencida).
- **Solicitudes de ayuda:** crear una solicitud (10 a 1000 caracteres; la nota de voz solo si ya funciona de punta a punta), los estados
  Pendiente, Con candidatos, Aceptada y Cerrada, ver el detalle, cerrar una solicitud.
- **Calificaciones:** cuándo se puede calificar (solicitud aceptada o cerrada), de 1 a 5 estrellas, solo una vez y
  solo el autor, cómo influyen en el emparejamiento, qué pasa si no hay calificaciones.
- **Preguntas frecuentes:** 10 a 15 preguntas cortas de todo un poco y problemas comunes (la página no carga, no
  llegan candidatos, la API dice "sin conexión", etc.).

**Listo cuando** el CI del PR pasa (valida tus casos) y el documento sigue la plantilla.
