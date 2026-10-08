# Entorno de desarrollo en Windows

En Windows trabajamos **dentro de WSL2 (Ubuntu)**. Así usamos los mismos comandos `bash` que en Mac, los scripts funcionan igual y Docker corre más rápido.

Requisitos: Windows 10 (22H2) u 11, virtualización activada en la BIOS (casi siempre viene activa), 8 GB de RAM como mínimo (16 GB recomendado) y unos 30 GB libres.

## 1. Instalar WSL2 con Ubuntu

En **PowerShell como administrador**:

```powershell
wsl --install -d Ubuntu-24.04
```

Reinicia el equipo. Al volver se abre Ubuntu y te pide crear un usuario y una contraseña de Linux (no tienen que ser los de Windows).

## 2. Limitar la memoria de WSL

Sin límite, WSL puede tomar casi toda la RAM. Crea el archivo `C:\Users\TU_USUARIO\.wslconfig` con este contenido (con 16 GB puedes usar `memory=6GB`):

```ini
[wsl2]
memory=4GB
processors=4
swap=2GB
```

Aplica el cambio en PowerShell con `wsl --shutdown` y vuelve a abrir Ubuntu.

## 3. Instalar Docker Desktop

1. Descárgalo de https://www.docker.com/products/docker-desktop/ (gratis para uso personal y educativo).
2. En **Settings → General**, deja activado *Use the WSL 2 based engine*.
3. En **Settings → Resources → WSL integration**, activa **Ubuntu-24.04**.
4. Comprueba desde Ubuntu:

```bash
docker version && docker compose version
```

## 4. Herramientas dentro de Ubuntu

Todos estos comandos van en la terminal de **Ubuntu**, no en PowerShell.

```bash
sudo apt update && sudo apt install -y git curl unzip gh
```

Configura Git. `core.autocrlf input` evita que Windows meta saltos de línea CRLF:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
git config --global core.autocrlf input
git config --global init.defaultBranch main
```

Node.js 24 con nvm (cierra y vuelve a abrir la terminal después del primer comando):

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

```bash
nvm install 24 && node -v
```

kubectl:

```bash
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && sudo install -m 0755 kubectl /usr/local/bin/kubectl && rm kubectl
```

Para el clúster local, instala **minikube o k3d**; el proyecto funciona con los dos. Si ya usas minikube en clase, quédate con minikube.

> **Importante:** si instalaste minikube desde PowerShell (en Windows), el script del proyecto no lo ve, porque corre dentro de Ubuntu. Instala minikube **también dentro de Ubuntu** con el comando de abajo. Las dos instalaciones conviven: el proyecto usa su propio perfil, `rednexus`, así que no toca el minikube que usas en clase. Eso sí, enciende solo uno a la vez (en PowerShell: `minikube stop`).

minikube:

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```

k3d (si prefieres k3d, que es más liviano):

```bash
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
```

Inicia sesión en GitHub (elige HTTPS y "Login with a web browser"):

```bash
gh auth login && gh auth setup-git
```

## 5. Clonar los repos

Clona **dentro de Ubuntu** (`~/rednexus`), nunca en `C:\` ni en `/mnt/c`: ahí todo es mucho más lento y aparecen problemas de permisos y saltos de línea.

```bash
mkdir -p ~/rednexus && cd ~/rednexus
gh repo clone juanjosegl/RedNexus-Backend
gh repo clone juanjosegl/RedNexus-Frontend
gh repo clone juanjosegl/RedNexus-Platform
```

## 6. VS Code

1. Instala VS Code **en Windows**: https://code.visualstudio.com
2. Agrégale la extensión **WSL** (`ms-vscode-remote.remote-wsl`).
3. Abre cada repo desde Ubuntu, por ejemplo: `cd ~/rednexus/RedNexus-Backend && code .`
4. Acepta las extensiones recomendadas que te sugiere VS Code.

## 7. Comprobar que todo funciona

Con **minikube** (la primera vez tarda varios minutos, porque descarga Kubernetes):

```bash
cd ~/rednexus/RedNexus-Platform && bash scripts/k8s-up.sh minikube
```

Cuando termine, deja corriendo esto en **otra** terminal de Ubuntu:

```bash
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80
```

Con **k3d**, en cambio, no hace falta el port-forward:

```bash
cd ~/rednexus/RedNexus-Platform && bash scripts/k8s-up.sh
```

Abre http://localhost:8080 en el navegador de Windows: debe decir **API: ok**.

Para programar día a día, sigue el README de cada repo (backend: `docker compose up -d`, `npm install`, `npm run db:migrate`, `npm run start:dev`; frontend: `npm install`, `npm run dev`).

## Problemas comunes

| Síntoma | Solución |
| --- | --- |
| `docker: command not found` en Ubuntu | Docker Desktop debe estar abierto, con la integración WSL activada para Ubuntu-24.04 (paso 3) |
| `bash\r: No such file or directory` | El repo se clonó con CRLF. Configura `core.autocrlf input` y vuelve a clonar |
| Todo va muy lento | ¿Clonaste en `/mnt/c`? Clona en `~/rednexus` |
| El equipo se queda sin memoria | Baja `memory` en `.wslconfig` y ejecuta `wsl --shutdown`. Apaga el clúster cuando no lo uses (`minikube stop -p rednexus` o `k3d cluster stop rednexus`) y no tengas encendidos el minikube de clase y el del proyecto a la vez |
| minikube dice que no hay memoria suficiente | Sube `memory` en `.wslconfig`, o arráncalo con menos memoria: `MINIKUBE_MEMORY=2200 bash scripts/k8s-up.sh minikube` |
| `kubectl` apunta a otro clúster | `kubectl config use-context rednexus` (minikube) o `kubectl config use-context k3d-rednexus` (k3d) |
| Puerto 8080 ocupado | Otro programa lo usa. Ciérralo o cambia el puerto en `k3d/cluster.yaml` (sin subir ese cambio) |
