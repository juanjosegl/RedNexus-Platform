# Entorno de desarrollo en macOS (Apple Silicon)

En Mac usamos **Colima** en lugar de Docker Desktop: es gratis, de código abierto y consume menos RAM.

## 1. Homebrew

Si no lo tienes, instálalo desde https://brew.sh. Después asegúrate de que quede primero en el PATH (si no, macOS usa su propio `git` viejo):

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
```

## 2. Herramientas

```bash
brew install git gh colima docker docker-compose docker-buildx kubectl k3d jq
```

```bash
brew install --cask visual-studio-code
```

Conecta los plugins de Docker: `~/.docker/config.json` debe incluir esta línea:

```json
"cliPluginsExtraDirs": ["/opt/homebrew/lib/docker/cli-plugins"]
```

Node.js 24 con [nvm](https://github.com/nvm-sh/nvm) (`nvm install 24`) o [fnm](https://github.com/Schniz/fnm). Ambos leen el `.nvmrc` de cada repo.

## 3. Git y GitHub

```bash
git config --global user.name "Tu Nombre" && git config --global user.email "tu-correo@ejemplo.com" && git config --global core.autocrlf input
```

```bash
gh auth login && gh auth setup-git
```

## 4. Docker con Colima

La primera vez crea la máquina virtual (con 8 GB de RAM, 3 GB es un buen límite):

```bash
colima start --cpu 4 --memory 3 --disk 40 --vm-type vz
```

Los días siguientes basta con `colima start`. Para liberar memoria: `colima stop`.

## 5. Clonar y comprobar

```bash
mkdir -p ~/rednexus && cd ~/rednexus && gh repo clone juanjosegl/RedNexus-Backend && gh repo clone juanjosegl/RedNexus-Frontend && gh repo clone juanjosegl/RedNexus-Platform
```

```bash
cd ~/rednexus/RedNexus-Platform && bash scripts/k8s-up.sh
```

Abre http://localhost:8080: debe decir **API: ok**.

Para programar día a día, mira la tabla "Cómo correr RedNexus según lo que vayas a hacer" en el [README](../README.md).

## Dashboards (opcional)

No hace falta Docker Desktop. Para ver contenedores, usa la extensión Docker de VS Code. Para Kubernetes:

```bash
brew install --cask headlamp && brew install k9s
```

## Nodo de IA (solo el Mac del equipo)

Ollama y whisper.cpp corren **nativos en macOS**, fuera de Docker, para aprovechar la GPU con Metal. Docker en Mac no tiene acceso a la GPU. La guía se agregará al configurar el módulo de IA.
