# Guía del equipo RedNexus

Esta guía te lleva desde un computador sin nada instalado hasta tener RedNexus corriendo y tu primera rama lista para programar. Síguela **en orden**: cada paso termina con un **✅ Comprueba** para que sepas que vas bien antes de seguir. Si algo no sale como dice ahí, busca el error en [Problemas comunes](#7-problemas-comunes) o escribe en el grupo con una captura.

Tiempo estimado: **1 a 2 horas**, la mayor parte esperando descargas.

---

## 0. Antes de empezar

### Qué es lo que vas a instalar

RedNexus son **tres repositorios** que viven en la misma carpeta:

| Repo | Qué tiene | Quién lo toca más |
| --- | --- | --- |
| `RedNexus-Backend` | La API (NestJS) y el worker de IA | Backend e IA |
| `RedNexus-Frontend` | La interfaz web (Vue 3) | Frontend |
| `RedNexus-Platform` | Docker, Kubernetes, CI/CD, documentación | Plataforma (y esta guía) |

**No necesitas saber Docker ni Kubernetes** para programar: ya está configurado y lo levantas con un comando.

### Lista de verificación

- [ ] Tienes cuenta de GitHub y **aceptaste las 3 invitaciones**. Revisa tu correo o entra a cada enlace y presiona *Accept invitation*:
  - https://github.com/juanjosegl/RedNexus-Backend/invitations
  - https://github.com/juanjosegl/RedNexus-Frontend/invitations
  - https://github.com/juanjosegl/RedNexus-Platform/invitations
- [ ] Windows 10 (versión 22H2) o Windows 11.
- [ ] Al menos 8 GB de RAM y 30 GB libres en disco.
- [ ] **Virtualización activada.** Abre el Administrador de tareas → *Rendimiento* → *CPU* → abajo a la derecha debe decir **Virtualización: Habilitado**. Si dice *Deshabilitado*, hay que activarla en la BIOS (busca "activar virtualización" + la marca de tu computador) o pide ayuda en el grupo.

> **¿Usas Mac?** Sigue [entorno-mac.md](entorno-mac.md) y luego salta a la [parte 2](#2-clonar-los-repos).

---

## 1. Instalar el entorno (Windows)

Trabajamos **dentro de Ubuntu (WSL2)**, un Linux que corre dentro de Windows. Así todos usamos exactamente los mismos comandos, en Windows y en Mac, y evitamos problemas de compatibilidad.

> **Dos terminales distintas:** en esta guía, **PowerShell** es la de Windows y **Ubuntu** es la de Linux. Cada bloque de código dice en cuál va. Si un comando falla, lo primero es revisar que estés en la terminal correcta.

### Paso 1. WSL2 con Ubuntu

Abre **PowerShell como administrador** (menú Inicio → escribe "PowerShell" → clic derecho → *Ejecutar como administrador*):

```powershell
wsl --install -d Ubuntu-24.04
```

**Reinicia el computador.** Al volver se abre una ventana de Ubuntu; si no se abre, búscala en el menú Inicio como "Ubuntu 24.04". La primera vez te pide crear un **usuario y una contraseña de Linux**. Pueden ser distintos a los de Windows, pero **anota la contraseña**, porque la pedirá cada vez que uses `sudo`. Al escribirla no se ven los caracteres; es normal.

✅ **Comprueba** en PowerShell (no hace falta que sea como administrador):

```powershell
wsl -l -v
```

Debe aparecer `Ubuntu-24.04` con **VERSION 2**. Si dice 1, ejecuta `wsl --set-version Ubuntu-24.04 2`.

### Paso 2. Limitar la memoria de Ubuntu

Si no lo limitas, WSL puede tomar casi toda la RAM y dejar el computador lento. En **PowerShell**, copia y pega el bloque completo:

```powershell
@"
[wsl2]
memory=4GB
processors=4
swap=2GB
"@ | Out-File -Encoding ascii "$env:USERPROFILE\.wslconfig"
wsl --shutdown
```

Si tu computador tiene 16 GB de RAM o más, cambia `memory=4GB` por `memory=6GB`.

✅ **Comprueba:** abre Ubuntu de nuevo y ejecuta `free -h`. En la fila `Mem`, el total debe ser cercano a 4 GB (o 6 GB).

### Paso 3. Docker Desktop

Si ya lo tienes instalado (por ejemplo, de clase), no lo reinstales: solo revisa los puntos 3 y 4.

1. Descárgalo de https://www.docker.com/products/docker-desktop/ e instálalo. Es gratis para uso educativo.
2. Ábrelo y espera a que diga *Engine running*.
3. **Settings** (engranaje) → **General** → debe estar marcado *Use the WSL 2 based engine*.
4. **Settings** → **Resources** → **WSL integration** → activa el interruptor de **Ubuntu-24.04** → *Apply & restart*.

✅ **Comprueba** en **Ubuntu**:

```bash
docker run --rm hello-world
```

Debe aparecer `Hello from Docker!`. Docker Desktop tiene que estar abierto siempre que trabajes en el proyecto.

### Paso 4. Herramientas dentro de Ubuntu

Todo lo de este paso va en la terminal de **Ubuntu**.

**Git, GitHub CLI y utilidades:**

```bash
sudo apt update && sudo apt install -y git curl unzip gh
```

**Configura Git** con tu nombre y **el mismo correo de tu cuenta de GitHub** (así tus commits aparecen a tu nombre):

```bash
git config --global user.name "Tu Nombre Apellido"
git config --global user.email "tu-correo-de-github@ejemplo.com"
git config --global core.autocrlf input
git config --global init.defaultBranch main
git config --global pull.rebase false
```

**Node.js 24** con nvm. Primero instala nvm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

**Cierra Ubuntu y ábrelo de nuevo**, y luego instala Node:

```bash
nvm install 24
```

**kubectl** (para hablar con Kubernetes):

```bash
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && sudo install -m 0755 kubectl /usr/local/bin/kubectl && rm kubectl
```

**minikube** (el clúster local; es el mismo que usamos en clase):

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```

> Si ya tienes minikube instalado **en Windows** (desde PowerShell), igual instálalo aquí: el proyecto corre dentro de Ubuntu y no ve el de Windows. Pueden convivir; el proyecto usa su propio perfil (`rednexus`) y no toca el de clase. Eso sí, enciende solo uno a la vez.

✅ **Comprueba:**

```bash
git --version && node -v && kubectl version --client && minikube version
```

Deben salir cuatro versiones sin errores, y la de Node debe empezar por `v24`.

### Paso 5. Iniciar sesión en GitHub

En **Ubuntu**:

```bash
gh auth login
```

Responde así:

| Pregunta | Respuesta |
| --- | --- |
| Where do you use GitHub? | **GitHub.com** |
| Preferred protocol? | **HTTPS** |
| Authenticate Git with your GitHub credentials? | **Yes** |
| How would you like to authenticate? | **Login with a web browser** |

Te mostrará un código de 8 caracteres. Si el navegador no se abre solo, entra a https://github.com/login/device desde Windows, pega el código y autoriza.

✅ **Comprueba:** `gh auth status` debe decir `Logged in to github.com account TU_USUARIO`.

### Paso 6. VS Code

1. Instala VS Code **en Windows**: https://code.visualstudio.com
2. Ábrelo, ve a Extensiones (Ctrl+Shift+X) e instala **WSL** (de Microsoft).
3. Ciérralo. Desde ahora lo abrirás **desde Ubuntu** con `code .` (lo hacemos en la parte 2).

---

## 2. Clonar los repos

En **Ubuntu**, copia y pega el bloque completo:

```bash
mkdir -p ~/rednexus && cd ~/rednexus
gh repo clone juanjosegl/RedNexus-Backend
gh repo clone juanjosegl/RedNexus-Frontend
gh repo clone juanjosegl/RedNexus-Platform
ls
```

> ⚠️ Clona siempre en `~/rednexus`, **nunca** en `C:\` ni en `/mnt/c/...`. Ahí todo es muchísimo más lento y aparecen errores raros de permisos y saltos de línea.

✅ **Comprueba:** `ls` muestra las tres carpetas, y cada repo está en la rama `developer`:

```bash
git -C RedNexus-Backend branch --show-current
```

Debe decir `developer`.

**Abre los repos en VS Code**, uno por ventana:

```bash
cd ~/rednexus/RedNexus-Frontend && code .
```

La primera vez tarda un poco (instala su parte dentro de Ubuntu). Abajo a la izquierda debe decir **WSL: Ubuntu-24.04**. Cuando VS Code ofrezca *instalar las extensiones recomendadas*, acepta. Si no lo ofrece: Extensiones → filtro `@recommended` → instala todas.

---

## 3. Primera prueba: levantar RedNexus completo

En **Ubuntu**:

```bash
cd ~/rednexus/RedNexus-Platform
docker compose up -d --build
```

La primera vez tarda **entre 5 y 10 minutos**, porque construye las imágenes. Al terminar:

✅ **Comprueba:** abre http://localhost:8088 en el navegador de Windows. Debe decir **RedNexus** y **API: ok**.

Si lo ves, **tu entorno está listo** 🎉. Apágalo para liberar memoria:

```bash
docker compose down
```

### Opcional: probarlo en Kubernetes (minikube)

```bash
cd ~/rednexus/RedNexus-Platform && bash scripts/k8s-up.sh minikube
```

La primera vez descarga Kubernetes (10–15 minutos). Cuando diga *Listo*, abre **otra** terminal de Ubuntu y deja corriendo esto:

```bash
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80
```

Entra a http://localhost:8080: debe decir **API: ok**. Para apagarlo: Ctrl+C en esa terminal y `minikube stop -p rednexus`.

---

## 4. Trabajar día a día

Al empezar el día, abre Docker Desktop y elige el caso que te toca. Cada uno es un comando.

### Si programas el **frontend**

```bash
cd ~/rednexus/RedNexus-Platform && docker compose up -d --build api worker
```

Esto levanta el backend completo en Docker, con datos de prueba. Luego, en otra terminal:

```bash
cd ~/rednexus/RedNexus-Frontend
cp -n .env.example .env
npm install
npm run dev
```

- Tu app: http://localhost:5173. Se recarga sola al guardar.
- **Lo que ofrece la API** (endpoints, qué enviar, qué responde): http://localhost:3000/api/docs
- Cuando el backend tenga cambios nuevos: `git -C ~/rednexus/RedNexus-Backend pull` y repite el primer comando.

### Si programas el **backend** o la **IA**

```bash
cd ~/rednexus/RedNexus-Backend
cp -n .env.example .env
docker compose up -d
npm install
npm run db:migrate
npm run db:seed
npm run start:dev
```

- Tu API: http://localhost:3000/api/health, y Swagger en http://localhost:3000/api/docs. Se recarga sola al guardar.
- Worker de IA, en otra terminal: `npm run start:worker:dev`.
- No levantes al mismo tiempo la API de Docker (`docker compose up … api` en Platform), porque las dos usan el puerto 3000.

### Si trabajas en **plataforma**

Lee el [README de Platform](../README.md): ahí están Compose, Kubernetes y el script `k8s-up.sh`.

### Ver lo que está corriendo

- **Contenedores:** el panel de Docker Desktop, o la extensión Docker de VS Code.
- **Kubernetes:** `minikube dashboard -p rednexus`, o instala Headlamp en Windows con `winget install headlamp` (en PowerShell).

### Al terminar el día

```bash
docker compose down
```

Ejecútalo en la carpeta donde hiciste `up`. Cierra Docker Desktop si no lo vas a usar.

---

## 5. Cómo trabajamos con Git

Estas reglas son iguales para todos. Siguiéndolas, nadie pisa el trabajo de otro y el historial queda limpio para el jurado.

### Las 5 reglas de oro

1. **Nunca programes en `developer`, `test` ni `main`.** GitHub no te dejará subir ahí; todo entra por Pull Request (PR).
2. **Una tarea = una rama = un PR.** Las tareas están en [tareas.md](tareas.md), cada una con su ID (por ejemplo `BE-01`).
3. **Antes de crear tu rama, actualiza `developer`.**
4. **Commits pequeños** con el formato de abajo, y un commit por cada paso de la tarea.
5. **Antes de subir:** `npm run lint`, `npm test` y `npm run build` sin errores.

### Nombres de ramas

```text
tipo/ID-descripcion-corta
```

| Tipo | Cuándo | Ejemplo |
| --- | --- | --- |
| `feature/` | Funcionalidad nueva | `feature/BE-01-auth` |
| `fix/` | Corregir un error | `fix/FE-04-estado-solicitud` |
| `docs/` | Solo documentación | `docs/DOC-02-privacidad` |
| `chore/` | Configuración, dependencias, Docker, CI | `chore/PL-01-imagenes-ghcr` |
| `refactor/` | Reorganizar código sin cambiar lo que hace | `refactor/BE-03-servicio-solicitudes` |
| `test/` | Solo pruebas | `test/BE-06-calificaciones` |

Todo en **minúsculas**, con guiones, **sin tildes, eñes ni espacios**. El ID va en mayúsculas, tal como aparece en tareas.md.

### Mensajes de commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/es/):

```text
tipo(alcance): qué hace el cambio
```

- **tipo:** `feat` (funcionalidad), `fix` (corrección), `test`, `docs`, `refactor`, `style` (formato, sin cambiar lógica), `chore` (configuración o dependencias), `ci` (pipelines).
- **alcance:** el módulo que tocas: `auth`, `users`, `help-requests`, `matching`, `ai`, `ratings`, `web`, `k8s`, `ci`…
- **qué hace:** en minúscula, en presente, sin punto final, máximo unos 70 caracteres. Debe responder a "este commit…".

| ✅ Así | ❌ Así no |
| --- | --- |
| `feat(auth): endpoint de registro con contraseña cifrada` | `cambios` |
| `fix(web): mostrar error cuando el login falla` | `arreglé el bug` |
| `test(ratings): validar que solo el autor califica` | `Commit final ya funciona!!!` |
| `docs(users): documentar endpoints en swagger` | `feat: muchas cosas del perfil y el login` |

Cada tarea de [tareas.md](tareas.md) ya trae la lista de commits sugeridos. Úsala como guía.

### El ciclo completo de una tarea

**1. Toma la tarea.** Asígnate su issue en GitHub, o avisa en el grupo, para que nadie más la tome.

**2. Crea tu rama desde `developer` actualizado.** En Ubuntu, dentro del repo:

```bash
git switch developer
git pull
git switch -c feature/BE-01-auth
```

O en VS Code: clic en el nombre de la rama (abajo a la izquierda) → *Create new branch from...* → elige `developer` → escribe el nombre.

**3. Programa y haz commits.** En VS Code:
1. Abre **Source Control** (Ctrl+Shift+G).
2. Revisa los archivos cambiados. Clic en uno te muestra qué cambió.
3. Presiona `+` en los archivos que van en este commit.
4. Escribe el mensaje (formato de arriba) y dale **Commit**.

**4. Sube tu rama.** En VS Code, **Publish Branch** (la primera vez) o **Sync Changes** (las siguientes). En la terminal, `git push -u origin feature/BE-01-auth` la primera vez y `git push` las siguientes.

**5. Abre el Pull Request.** En GitHub aparece un aviso amarillo con **Compare & pull request**.
- **base:** `developer` ← **compare:** tu rama. Revisa que no diga `main`.
- **Título** con el formato de commit + el ID, porque será el mensaje final en `developer`. Por ejemplo: `feat(auth): registro y login con JWT (BE-01)`
- En la descripción, completa la plantilla y escribe `Closes #N` (N = número del issue).

**6. Revisión.** El CI corre solo (2–3 minutos); si sale en rojo, abre el detalle, corrige en tu rama y sube de nuevo. Un compañero o el líder revisa y aprueba. Si te piden cambios, haz nuevos commits en la misma rama y el PR se actualiza solo.

**7. Fusión.** Se usa **Squash and merge**, y GitHub borra la rama automáticamente.

**8. Limpia y vuelve a empezar:**

```bash
git switch developer
git pull
git branch -D feature/BE-01-auth
```

Usamos `-D` porque, después del squash, Git no reconoce la rama como fusionada. Úsalo solo cuando el PR ya esté fusionado.

### Si `developer` avanzó mientras trabajabas

Hazlo seguido, sobre todo antes de abrir el PR:

```bash
git fetch
git merge origin/developer
```

Si hay **conflictos**, VS Code los marca en rojo. En cada archivo elige *Accept Current*, *Accept Incoming* o *Accept Both*, guarda, haz commit y push. Si dudas, pregunta antes de elegir.

### Si cambias la base de datos (`prisma/schema.prisma`)

1. Avisa en el grupo: dos migraciones creadas a la vez chocan.
2. Crea la migración con un nombre claro: `npm run db:migrate -- --name agregar-calificacion-unica`
3. Haz commit de `schema.prisma` **y** de la carpeta nueva en `prisma/migrations/`.
4. Si alguien fusionó otra migración antes que tú: actualiza tu rama (`git merge origin/developer`), borra **tu** carpeta de migración, y vuelve a ejecutar el paso 2.

### Uso de IA (ChatGPT, Copilot, Claude…)

Se permite, y el diplomado lo fomenta, pero **tú respondes por el código**. Revisa, prueba y asegúrate de poder explicarlo en la sustentación. Nunca pegues contraseñas, tokens ni datos reales de personas en un chat de IA.

---

## 6. Qué nunca subir

- El archivo `.env` (ya está en `.gitignore`; no lo saques de ahí).
- Contraseñas, tokens o llaves, ni siquiera "temporalmente".
- **Datos reales de personas.** Solo datos inventados (Ley 1581 de 2012).
- Carpetas `node_modules/` o `dist/`.

---

## 7. Problemas comunes

| Lo que ves | Qué hacer |
| --- | --- |
| `docker: command not found` o `Cannot connect to the Docker daemon` en Ubuntu | Abre Docker Desktop y espera a *Engine running*. Revisa la integración WSL (parte 1, paso 3) |
| `bash\r: No such file or directory` o `$'\r': command not found` | El repo se clonó con saltos de línea de Windows. Ejecuta `git config --global core.autocrlf input`, borra la carpeta y vuelve a clonar |
| Todo va lentísimo | ¿Clonaste en `/mnt/c`? Clona en `~/rednexus` |
| El computador se pone muy lento | Apaga lo que no uses (`docker compose down`, `minikube stop -p rednexus`) y no tengas el minikube de clase encendido a la vez |
| `port is already allocated` o `EADDRINUSE` | Algo ya usa ese puerto. `docker compose down` en Platform y en Backend, y cierra otras terminales con `npm run …` |
| `nvm: command not found` | Cierra y vuelve a abrir Ubuntu. Si sigue, repite la instalación de nvm |
| `node -v` muestra otra versión | Dentro del repo ejecuta `nvm use` (lee el archivo `.nvmrc`) |
| `Permission denied` o `403` al hacer push | Ejecuta `gh auth status`. Revisa que aceptaste la invitación al repo |
| `push declined due to repository rule violations` | Estás intentando subir a `developer` o `main`. Crea tu rama (parte 5) y sube esa |
| El PR dice *Merging is blocked* | Falta la aprobación o el CI está en rojo. Revisa la pestaña *Checks* |
| http://localhost:5173 dice **API: sin conexion** | El backend no está corriendo: levántalo como en la parte 4 |
| minikube: `Exiting due to RSRC_INSUFFICIENT_CONTAINER_MEMORY` | Sube `memory` en `.wslconfig` (parte 1, paso 2), o usa `MINIKUBE_MEMORY=2200 bash scripts/k8s-up.sh minikube` |
| `kubectl` muestra otro clúster | `kubectl config use-context rednexus` |

¿No está tu error? Escribe en el grupo con: qué comando ejecutaste, una captura del error y en qué paso de esta guía ibas.
