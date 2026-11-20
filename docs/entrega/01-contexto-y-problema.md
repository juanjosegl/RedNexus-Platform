# 1. Contexto y problema

## 1.1 El problema

En la universidad, cuando un estudiante se atasca con un tema (un join en SQL, una integral por partes, un ejercicio de subredes) tiene tres caminos: esperar la monitoría o la asesoría del docente, preguntar en un grupo de WhatsApp del curso o buscar solo en internet. Los tres fallan en lo mismo: **la duda no llega a la persona que sabe resolverla**. En el grupo la pregunta se pierde entre mensajes y la ve quien esté conectado, no quien sabe; la monitoría tiene horario y cupo; y el buscador no conoce el contexto del curso.

Al mismo tiempo, en cada cohorte hay estudiantes de semestres avanzados, monitores y egresados que dominan esos temas y estarían dispuestos a ayudar, pero nadie sabe quiénes son ni qué saben. La ayuda entre compañeros existe, pero es informal y depende de la suerte.

Esto importa porque las dificultades académicas no resueltas se acumulan y terminan en deserción. En Colombia, el Sistema para la Prevención de la Deserción en la Educación Superior (SPADIES) del Ministerio de Educación Nacional reportó para el nivel universitario una **deserción por cohorte del 46,1 %** (estudiantes que no llegan al décimo semestre) y una deserción anual por periodo cercana al **9,3 %** en 2015 (Ministerio de Educación Nacional [MEN], 2016). La misma fuente señala que las áreas de ingeniería, arquitectura y urbanismo tienen de las tasas de graduación más bajas.

> **Pendiente del equipo (issue DOC-09):** actualizar estas cifras con la consulta más reciente de SPADIES filtrada por Unicomfacauca y por los programas de ingeniería, y, si es posible, aplicar una encuesta corta a estudiantes del diplomado (5 preguntas: cómo resuelven dudas hoy, cuánto tardan, si ayudarían a otros).

## 1.2 Por qué la ayuda entre pares

La evidencia muestra que acompañar a los estudiantes con pares funciona. Machado (2022) evaluó el programa Tutorías Entre Pares de la Universidad de la República (Uruguay) con métodos de emparejamiento estadístico y encontró que participar **reduce entre 8 % y 11 % la probabilidad de deserción**, además de mejorar el desempeño académico. El cuello de botella no es la voluntad de ayudar, sino **encontrar rápido al compañero adecuado**.

## 1.3 Cómo lo resuelve RedNexus

RedNexus es una red de apoyo académico en la que cada estudiante describe lo que sabe (texto libre y etiquetas) y publica sus dudas por texto o por nota de voz. En lugar de esperar a que alguien vea la pregunta, **el sistema la lee, entiende de qué trata y se la lleva a los tres compañeros que mejor pueden resolverla**, con una frase que explica por qué cada uno encaja. El ayudante acepta o rechaza; si acepta, los dos reciben el correo del otro, y al final el autor califica la ayuda, lo que mejora las recomendaciones siguientes.

La IA hace tres cosas:

1. **Clasifica** la duda (área, temas y nivel) con un modelo de lenguaje (LLM).
2. **La compara por significado** con los perfiles usando *embeddings*: "unir tres tablas con una intermedia" queda cerca de "joins muchos a muchos" aunque no compartan palabras.
3. **Explica** por qué recomienda a cada ayudante usando solo los datos del perfil recuperado (un patrón RAG, *retrieval-augmented generation*), para no inventar habilidades.

Además, un **asistente de soporte** con RAG responde dudas sobre cómo usar la plataforma con base en la documentación del proyecto, y remite a la PQRS lo que no puede resolver.

## 1.4 Por qué IA local

Toda la IA corre en la infraestructura del proyecto con modelos abiertos (Ollama y whisper.cpp), no en APIs externas. Las dudas y los perfiles de los estudiantes son datos personales según la Ley 1581 de 2012; procesarlos localmente evita transferirlos a terceros fuera del país, elimina costos por uso y permite que el sistema funcione en equipos de 8 GB de RAM. Si el nodo de IA se apaga, el sistema no se cae: empareja por etiquetas y explica con una plantilla (degradación controlada, ADR-006).

## 1.5 Por qué cloud native

El diplomado evalúa cómo se construye, despliega y opera la aplicación. RedNexus se diseñó para ser **pequeño, reconstruible y observable**: contenedores con una sola imagen para la API, el worker y las migraciones; manifiestos de Kubernetes con Kustomize que corren igual en k3d (Mac) y minikube (Windows); CI obligatorio en cada PR; imágenes multiarquitectura firmadas y con SBOM; y despliegue continuo en el servidor compartido del diplomado (Dokploy). Ver los ADR 001, 002 y 009.

## Referencias de la sección

- Machado, M. (2022). El aprendizaje entre pares y sus efectos en el desempeño de los estudiantes. *Desarrollo y Sociedad*, (92). https://doi.org/10.13043/DYS.92.1
- Ministerio de Educación Nacional. (2016). *Deserción en educación superior: informe de seguimiento* [SPADIES]. https://www.mineducacion.gov.co/sistemasinfo/spadies/
