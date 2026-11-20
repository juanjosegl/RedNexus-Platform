# Informe ejecutivo: RedNexus

**Proyecto integrador · Diplomado CloudForge AI 5.0 · Unicomfacauca · Noviembre de 2026**
Equipo: Juan José Gutiérrez Lasso (líder, @juanjosegl), Daniel Fernández (@daniel200231), José Fernández (@josesfa), María Paula (@MariPau-dev) y Alejandra Guzmán (@alejandraguzman12).

> **Pendiente:** cada integrante confirma su nombre completo tal como debe salir en la portada (issue DOC-11).

## El problema

Casi la mitad de los estudiantes universitarios en Colombia no termina su carrera (deserción por cohorte del 46,1 % según SPADIES), y las dificultades académicas no resueltas son parte del camino hacia el abandono. Mientras tanto, la ayuda entre compañeros, que reduce la deserción entre un 8 % y un 11 % según la evidencia (Machado, 2022), sigue siendo informal: la duda se pierde en un grupo de WhatsApp y no llega a quien sabe resolverla.

## La solución

RedNexus es una red de apoyo académico en la que cada estudiante describe lo que sabe y publica sus dudas por texto o por nota de voz. Una IA que corre en la propia infraestructura clasifica la duda, la compara por significado con los perfiles y propone a los tres compañeros que mejor pueden ayudar, explicando por qué. El ayudante acepta o rechaza; al aceptar se comparten los contactos, y al final la ayuda se califica. Un asistente con RAG resuelve dudas sobre el uso de la plataforma y remite a PQRS lo que no puede responder.

## Resultados

| Área | Resultado |
| --- | --- |
| Producto | MVP completo: registro con autorización de datos, perfil, solicitudes por texto y voz, emparejamiento con IA, bandeja del ayudante, calificación, asistente de soporte, PQRS, exportar y borrar mis datos |
| IA | En 100 solicitudes sintéticas con la respuesta correcta conocida, el ayudante correcto aparece entre los tres propuestos en cerca del 90 % de los casos, frente al 81 % de la configuración inicial; se rechaza el 90 % de las dudas fuera de tema (ver capítulo 6) |
| MLOps | 30 experimentos comparables en MLflow; la configuración ganadora está registrada como versión del modelo `rednexus-matching` y se aplica por variables de entorno |
| Plataforma | Contenedores, Kubernetes local (k3d y minikube), CI obligatorio en tres repositorios, imágenes multiarquitectura escaneadas, con SBOM y firmadas, y despliegue continuo en el servidor del diplomado |
| Privacidad | Cumplimiento de la Ley 1581: autorización, acceso, supresión y minimización; IA local sin transferir datos a terceros |

## Lo que sigue

GitOps con Argo CD, Sealed Secrets, política de imágenes firmadas con Kyverno, infraestructura como código con OpenTofu y observabilidad con OpenTelemetry y Grafana para medir el SLO de 30 segundos. Para la adopción, un piloto de un semestre con bienestar universitario como responsable del tratamiento de los datos.
