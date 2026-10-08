# Cómo contribuir a RedNexus

Aplica a los tres repos: Backend, Frontend y Platform.

## Ramas

| Rama | Para qué | Quién escribe |
| --- | --- | --- |
| `main` | Versión estable, la que se presenta | Solo por PR desde `test` (líder) |
| `test` | Pruebas antes de pasar a `main` | Solo por PR desde `developer` (líder) |
| `developer` | Integración del trabajo del equipo | Solo por PR desde ramas temporales |
| `tipo/RN-N-descripcion` | **Una rama temporal por cada tarea** | Quien hace la tarea |

Nadie hace push directo a `main`, `test` ni `developer`.

**Tipos de rama temporal:** `feature/` (funcionalidad nueva), `fix/` (corrección), `docs/` (documentación), `chore/` (configuración, dependencias, infraestructura), `refactor/` y `test/`. `N` es el número del issue en GitHub.

Ejemplos: `feature/RN-12-login`, `fix/RN-20-error-al-calificar`, `docs/RN-31-runbook`.

### Vida de una rama temporal

```text
developer ──┬───────────────────────●──────────►  (squash merge del PR)
            │                       ▲
            └─ feature/RN-12-login ─┘  ← se crea desde developer y se borra al fusionarse
```

La rama temporal vive **hasta que su PR entra a `developer`** y ahí se borra. No viaja hasta `main`: su cambio llega a `test` y a `main` dentro de las promociones de `developer`, que hace el líder (ver más abajo).

## Ciclo de una tarea

### 1. Partir de `developer` actualizado y crear la rama

```bash
git switch developer
git pull
git switch -c feature/RN-12-login
```

En VS Code: clic en el nombre de la rama (abajo a la izquierda) → *Create new branch from...* → elige `developer` → escribe el nombre.

### 2. Trabajar con commits pequeños

Usamos [Conventional Commits](https://www.conventionalcommits.org/es/): `tipo(alcance): qué cambia`.

```bash
git add .
git commit -m "feat(auth): registro de usuarios con contraseña cifrada"
```

Algunos ejemplos: `feat(matching): top 3 por similitud`, `fix(web): botón de enviar deshabilitado`, `docs: guía de instalación`, `chore(deps): actualizar prisma`.

En VS Code: panel **Source Control** (Ctrl+Shift+G) → `+` para agregar archivos → escribe el mensaje → **Commit**.

Antes de subir, corre `npm run lint`, `npm test` y `npm run build`.

### 3. Subir la rama y abrir el PR hacia `developer`

```bash
git push -u origin feature/RN-12-login
gh pr create --base developer --fill
```

En VS Code: **Publish Branch** y después abre el PR en GitHub. Revisa siempre que la base sea **`developer`**, no `main`.

En la descripción escribe `Closes #12` para que el issue se cierre solo.

### 4. Revisión y fusión

- Un compañero revisa y aprueba, y el CI debe estar en verde.
- Se fusiona con **Squash and merge**: todos los commits de la rama quedan como uno solo en `developer`.
- GitHub **borra la rama remota automáticamente**.

### 5. Limpiar tu copia local

```bash
git switch developer
git pull
git fetch --prune
git branch -D feature/RN-12-login
```

Se usa `-D` (mayúscula) porque, después de un *squash*, Git no reconoce que la rama ya se fusionó. Úsalo solo cuando el PR ya esté fusionado.

### Si `developer` avanzó mientras trabajabas

```bash
git fetch
git merge origin/developer
```

Resuelve los conflictos si los hay, haz commit y push. El PR se actualiza solo.

## Promociones (solo el líder)

Cuando `developer` tiene un conjunto de cambios estable:

1. **PR `developer` → `test`**, fusionado con **Create a merge commit** (no squash). Se prueba en `test`.
2. **PR `test` → `main`**, también con **merge commit**. Después se etiqueta la versión:

```bash
git switch main && git pull
git tag -a v0.1.0 -m "v0.1.0: registro, perfiles y solicitudes"
git push origin v0.1.0
```

Las promociones no usan squash porque si se aplana, `developer`, `test` y `main` dejan de compartir historia y los PR siguientes arrastran cambios viejos.

## Correcciones urgentes en `main`

Una rama `hotfix/RN-N-descripcion` sale de `main` → PR a `main` → después el líder abre un PR de `main` a `developer` para que la corrección no se pierda.

## Reglas

- Nunca subir `.env`, contraseñas, tokens ni datos reales de personas. Solo datos sintéticos (Ley 1581 de 2012).
- Si usas IA para generar código, revísalo, pruébalo y debes poder explicarlo.
- Un PR = una tarea. Si un PR crece mucho, divídelo.
