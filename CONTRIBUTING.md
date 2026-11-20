# Cómo contribuir a RedNexus

Aplica a los tres repos: Backend, Frontend y Platform. La explicación paso a paso, con capturas de qué hacer en VS Code y en GitHub, está en la [guía del equipo, parte 5](docs/guia-del-equipo.md#5-cómo-trabajamos-con-git). Aquí va el resumen.

## Ramas

| Rama | Para qué | Cómo entra el código |
| --- | --- | --- |
| `main` | Versión estable, la que se presenta | Solo por PR desde `test` (líder) |
| `test` | Pruebas antes de pasar a `main` | Solo por PR desde `developer` (líder) |
| `developer` | Integración del trabajo del equipo | Solo por PR desde ramas temporales |
| `tipo/ID-descripcion` | **Una rama temporal por tarea** | La crea quien hace la tarea |

- **Tipos:** `feature/`, `fix/`, `docs/`, `chore/`, `refactor/` y `test/`.
- **ID:** el de la tarea en [docs/tareas.md](docs/tareas.md).
- **Formato:** minúsculas, con guiones, sin tildes ni espacios. Ejemplos: `feature/BE-01-auth`, `fix/FE-04-estado-solicitud`.

```text
developer ──┬──────────────────────●──────►   squash merge del PR
            └─ feature/BE-01-auth ─┘          se crea desde developer y se borra al fusionarse
```

## Commits

Formato [Conventional Commits](https://www.conventionalcommits.org/es/): `tipo(alcance): qué hace el cambio`. Va en minúscula, en presente y sin punto final.

- **tipos:** `feat`, `fix`, `test`, `docs`, `refactor`, `style`, `chore` y `ci`.
- **alcance:** el módulo que tocas (`auth`, `users`, `help-requests`, `matching`, `ai`, `ratings`, `web`, `k8s`…).
- **ejemplo:** `feat(auth): endpoint de registro con contraseña cifrada`.

## Pull Requests

- Siempre hacia **`developer`**.
- **Título:** como un commit, más el ID de la tarea. Por ejemplo: `feat(auth): registro y login con JWT (BE-01)`. Es el mensaje que queda en `developer` al fusionar.
- **Requisitos para fusionar:** CI en verde y 1 aprobación. Se fusiona con **Squash and merge** y GitHub borra la rama.
- **Antes de abrirlo:** corre `npm run lint`, `npm test` y `npm run build`.

## Promociones (solo el líder)

Cuando `developer` tiene un conjunto estable:

1. **PR `developer` → `test`**, fusionado con **Create a merge commit**, no squash. Se prueba en `test`.
2. **PR `test` → `main`**, también con merge commit. Después se etiqueta la versión:

```bash
git switch main && git pull
git tag -a v0.1.0 -m "v0.1.0: registro, perfiles y solicitudes"
git push origin v0.1.0
```

Las promociones no usan squash porque, si se aplanan, `developer`, `test` y `main` dejan de compartir historia y los PR siguientes arrastran cambios viejos.

## Correcciones urgentes en `main`

Una rama `fix/ID-descripcion` sale de `main` → PR a `main` → después el líder abre un PR de `main` a `developer` para que la corrección no se pierda.

## Reglas

- Nunca subir `.env`, contraseñas, tokens ni datos reales de personas. Solo datos sintéticos (Ley 1581 de 2012).
- Si usas IA para generar código, revísalo, pruébalo y debes poder explicarlo.
- Un PR = una tarea. Si un PR crece mucho, divídelo.
