# Informe ejecutivo: RedNexus

**Proyecto integrador · Diplomado CloudForge AI 5.0 · Unicomfacauca · Noviembre de 2026**
Equipo: Juan José Gutiérrez Lasso (líder, @juanjosegl), Victor Daniel Fernández (@daniel200231), José Sebastián Fernández (@josesfa), María Paula Andrade Muñoz (@MariPau-dev) y María Alejandra Guzmán Ruiz (@alejandraguzman12).

## El problema

Casi la mitad de los estudiantes universitarios en Colombia no termina su carrera (deserción por cohorte del 46,1 % según SPADIES), y las dificultades académicas no resueltas son parte del camino hacia el abandono. Mientras tanto, la ayuda entre compañeros, que reduce la deserción entre un 8 % y un 11 % según la evidencia (Machado, 2022), sigue siendo informal: la duda se pierde en un grupo de WhatsApp y no llega a quien sabe resolverla.

## La solución

RedNexus es una red de apoyo académico en la que cada estudiante describe lo que sabe y publica sus dudas por texto o por nota de voz. Una IA que corre en la propia infraestructura clasifica la duda, la compara por significado con los perfiles y propone a los tres compañeros que mejor pueden ayudar, explicando por qué. El ayudante acepta o rechaza; al aceptar se comparten los contactos, y al final la ayuda se califica. Un asistente con RAG resuelve dudas sobre el uso de la plataforma y remite a PQRS lo que no puede responder.

## Resultados

| Área | Resultado |
| --- | --- |
| Producto | MVP completo: registro con autorización de datos, perfil, solicitudes por texto y voz, emparejamiento con IA, bandeja del ayudante, calificación, asistente de soporte, PQRS, exportar y borrar mis datos |
| IA | En 100 solicitudes sintéticas con la respuesta correcta conocida, el ayudante correcto aparece entre los tres propuestos en el 94 % de los casos, frente al 81 % de la configuración inicial; se rechaza el 90 % de las dudas fuera de tema. El asistente con RAG acierta en el 83,3 % de 60 casos (meta 70 %). El LLM responde su primer token en 0,17 s y genera 24 tokens/s en un portátil de 8 GB |
| MLOps | 39 runs comparables en MLflow; la configuración ganadora está registrada como versión del modelo `rednexus-matching` y se aplica por variables de entorno |
| Plataforma | Contenedores, Kubernetes local (k3d y minikube), CI obligatorio en tres repositorios, imágenes multiarquitectura escaneadas, con SBOM y firmadas, GitOps con Argo CD, Kyverno y Sealed Secrets instalado con OpenTofu, y observabilidad con OpenTelemetry y Grafana (SLO de 30 s) |
| Privacidad | Cumplimiento de la Ley 1581: autorización, acceso, supresión y minimización; IA local sin transferir datos a terceros |

## Limitaciones

El servidor compartido del diplomado (Dokploy) no quedó disponible, así que no hay una URL pública permanente: la demo corre en el equipo del líder con las mismas imágenes firmadas y el flujo GitOps se prueba de punta a punta en GitHub Actions. Las métricas de IA salen de datos sintéticos y los modelos son pequeños (3B) por el hardware de 8 GB.

## Lo que sigue

Un piloto de un semestre con estudiantes reales y bienestar universitario como responsable del tratamiento de los datos; un servidor con GPU o un clúster público para la demo permanente; cambiar `qwen2.5:3b` por un modelo con licencia comercial si se adopta institucionalmente; y medir con usuarios reales el tiempo hasta la primera ayuda y su efecto en la permanencia.
