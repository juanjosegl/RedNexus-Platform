# Guion de la demo: contenedores y orquestación

Demo de unos 5 minutos sobre cómo RedNexus usa Docker y Kubernetes. No muestra la IA: en el clúster local corre con `AI_PROVIDER=mock`.

Se ensayó el 4 de noviembre de 2026 en el Mac (M1, 8 GB, Colima con 3 GB) con k3d. Con minikube los comandos son los mismos, salvo el port-forward.

## Preparación

### El día anterior

```bash
cd RedNexus-Platform
bash scripts/k8s-up.sh            # o: bash scripts/k8s-up.sh minikube
```

Construye las imágenes, enciende el clúster (lo crea si no existe), despliega todo y carga los perfiles sintéticos con el Job `seed`. Termina con `Listo: http://localhost:8080`.

### 30 minutos antes

1. Cierren todo lo que no sea necesario: Docker y el clúster usan cerca de 3 GB.
2. Liberen el puerto 8080: `docker ps --format '{{.Names}} {{.Ports}}' | grep 8080` no debe mostrar nada más que el balanceador de k3d.
3. Vuelvan a correr `bash scripts/k8s-up.sh`. Tarda cerca de 1 minuto y deja todo limpio.
4. Comprueben que `curl localhost:8080/api/health` responde `{"status":"ok"}`.
5. Abran:
   - **Terminal 1**, con letra grande (`Cmd +`): la de los comandos.
   - **Terminal 2**: `k9s -n rednexus`, la vista en vivo de los pods.
   - **Navegador**: http://localhost:8080 y http://localhost:8080/api/docs.
   - **Editor**: `RedNexus-Backend/Dockerfile` y `RedNexus-Platform/deploy/base/api.yaml`.
6. Graben la demo una vez en video como respaldo.

## Guion (5 minutos)

### 1. Los contenedores: una imagen, tres roles (1 min)

Muestren el `Dockerfile` del backend.

> "Es una imagen multietapa: en la primera etapa se compila TypeScript y en la segunda solo quedan el código compilado y las dependencias de producción. Corre con el usuario `node`, no como root. La **misma imagen** hace tres trabajos: la API, el worker que procesa la cola y las migraciones de la base de datos."

```bash
docker images | grep rednexus
```

```bash
kubectl -n rednexus get deploy,job -o custom-columns='NOMBRE:.metadata.name,IMAGEN:.spec.template.spec.containers[0].image,COMANDO:.spec.template.spec.containers[0].command'
```

Se ve `api`, `worker` y `seed` con `rednexus-api:dev`, cada uno con un comando distinto. `api` muestra `<none>` porque usa el comando por defecto de la imagen (`node dist/main`).

### 2. Qué corre en el clúster (1 min)

```bash
kubectl -n rednexus get pods,svc,ingress,pvc
```

> "Son cinco componentes. **web** es Nginx con el frontend en Vue. **api** es NestJS. **worker** procesa la cola. **redis** sostiene la cola BullMQ. **postgres** con pgvector es un **StatefulSet**, porque guarda datos: tiene su volumen persistente (PVC) de 1 GB. Todo entra por un solo **Ingress**: `/` va al frontend y `/api` a la API."

En el navegador, abran http://localhost:8080 (la app) y `/api/docs` (Swagger).

### 3. Una petición recorre el clúster (1 min)

En la Terminal 1, dejen corriendo los logs del worker:

```bash
kubectl -n rednexus logs -f deploy/worker
```

En Swagger, inicien sesión con `estudiante.demo@rednexus.dev` / `demo12345`, presionen **Authorize** y creen una solicitud con `POST /api/help-requests`. Un texto de ejemplo: "Necesito ayuda para crear un Dockerfile y desplegar contenedores en Kubernetes".

> "La API responde de inmediato con `PENDING` y deja un trabajo en Redis. El worker, que es **otro pod**, lo toma y lo procesa. Aquí está el log: `1 candidatos por semantic en 48 ms`."

Con `GET /api/help-requests/{id}`, la solicitud ya aparece en `MATCHED`. Detengan los logs con `Ctrl+C`.

### 4. Kubernetes trabajando (1,5 min)

**Migraciones antes de arrancar (initContainer):**

```bash
kubectl -n rednexus logs deploy/api -c migrate
```

> "Antes de que arranque la API, un initContainer con la misma imagen aplica las migraciones. Si fallan, la API no arranca."

**Escalar el worker** (mírenlo en k9s):

```bash
kubectl -n rednexus scale deploy/worker --replicas=2
```

```bash
kubectl -n rednexus get pods -l app.kubernetes.io/name=worker
```

> "Si llegan muchas solicitudes, agregamos workers y se reparten la cola. Tarda unos segundos."

**Autorreparación** (borren el pod de la API y miren k9s):

```bash
kubectl -n rednexus delete pod -l app.kubernetes.io/name=api
```

```bash
kubectl -n rednexus get pods -l app.kubernetes.io/name=api
```

> "Kubernetes ve que falta un pod y crea otro. La *readinessProbe* (`/api/health`) evita que reciba tráfico antes de estar lista. En el ensayo tardó 3 segundos."

Vuelvan a dejarlo como estaba:

```bash
kubectl -n rednexus scale deploy/worker --replicas=1
```

### 5. Seguridad y recursos (30 s)

Muestren `deploy/base/api.yaml` en el editor.

> "Todos los contenedores corren **sin root**, sin escalada de privilegios y sin *capabilities*, y la API tiene el **sistema de archivos en solo lectura**. Cada pod tiene límites de memoria (la API, 384 MiB), porque todo debe caber en equipos de 8 GB."

### Cierre (15 s)

> "Los manifiestos usan Kustomize: hay una base común y un overlay por herramienta, k3d en Mac y minikube en Windows. El CI valida cada overlay con kubeconform en cada PR. Esta misma imagen es la que despliega Render en la nube con cada push a `main`."

## Preguntas probables

| Pregunta | Respuesta corta |
| --- | --- |
| ¿Por qué k3d o minikube y no un clúster en la nube? | Costo cero, y cabe en los equipos del equipo (8 GB). Los manifiestos son Kubernetes estándar: cambiar de clúster es cambiar de overlay (ADR-001) |
| ¿Por qué una sola imagen? | Un solo build y un solo escaneo, y la API, el worker y las migraciones siempre tienen la misma versión del código (ADR-002) |
| ¿Por qué Postgres es un StatefulSet? | Necesita identidad estable y su propio volumen. Si se borra el pod, los datos siguen en el PVC |
| ¿Los secretos están en texto plano? | Solo los de desarrollo (`components/dev`), y no tienen valor real. Para el ambiente de demo está prevista Sealed Secrets (PL-04) |
| ¿Hay autoescalado? | Hoy el escalado es manual (`kubectl scale`). Un HPA por CPU o por tamaño de la cola es el siguiente paso |
| ¿Cómo llegan las imágenes al clúster? | `scripts/k8s-up.sh` las construye desde los repos y las importa al clúster. Está previsto publicarlas en GHCR (PL-01) y desplegar con Argo CD (PL-03) |
| ¿Por qué la imagen de la API pesa 845 MB? | Incluye Prisma y tsx para las migraciones y el seed. Optimizarla, con una imagen aparte para el seed, está pendiente |
| ¿Dónde corre la IA? | Fuera del clúster (Ollama nativo, para usar la GPU del Mac). El worker la alcanza en `host.k3d.internal`. En esta demo se usa el modo de prueba |
| ¿Funciona en Windows? | Sí, con minikube: `bash scripts/k8s-up.sh minikube` y el port-forward que indica el script |

## Si algo falla en vivo

| Síntoma | Qué hacer |
| --- | --- |
| `connection refused` al usar kubectl | El clúster está apagado: `k3d cluster start rednexus` |
| La app no abre en el 8080 | Otro programa usa el puerto: `docker ps \| grep 8080` |
| Un pod en `CrashLoopBackOff` | `kubectl -n rednexus logs <pod> --previous` |
| La solicitud no sale de `PENDING` | Revisen el worker: `kubectl -n rednexus logs deploy/worker` |
| Nada funciona | Pongan el video de respaldo |

## Después de la demo

```bash
k3d cluster stop rednexus         # libera la RAM y conserva los datos
```
