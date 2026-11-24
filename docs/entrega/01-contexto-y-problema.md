# 1. Contexto y problema

## 1.1 El problema

En la universidad, cuando un estudiante se atasca con un tema (un join en SQL, una integral por partes, un ejercicio de subredes) tiene tres caminos: esperar la monitoría o la asesoría del docente, preguntar en un grupo de WhatsApp del curso o buscar solo en internet. Los tres fallan en lo mismo: **la duda no llega a la persona que sabe resolverla**. En el grupo la pregunta se pierde entre mensajes y la ve quien esté conectado, no quien sabe; la monitoría tiene horario y cupo; y el buscador no conoce el contexto del curso.

Al mismo tiempo, en cada cohorte hay estudiantes de semestres avanzados, monitores y egresados que dominan esos temas y estarían dispuestos a ayudar, pero nadie sabe quiénes son ni qué saben. La ayuda entre compañeros existe, pero es informal y depende de la suerte.

Esto importa porque las dificultades académicas no resueltas se acumulan y terminan en deserción. En Colombia, el Sistema para la Prevención de la Deserción en la Educación Superior (SPADIES) del Ministerio de Educación Nacional mide dos indicadores:

| Indicador (SPADIES) | Valor | Año | Fuente |
| --- | --- | --- | --- |
| Tasa de deserción anual (TDA), educación superior | 9,03 % | 2022 | MEN, citado por Infobae (2026) |
| Tasa de deserción anual (TDA), educación superior | 8,97 % | 2023 | MEN, citado por Infobae (2026) y La República (2026) |
| Tasa de deserción anual (TDA), educación superior | 9,78 % | 2024 | MEN, citado por El Tiempo (2025) |
| Deserción por cohorte a décimo semestre, nivel universitario | entre 34 % y 45 % según el perfil del estudiante (≈ 45 % en promedio) | Cohortes hasta 2015 | Ministerio de Educación Nacional (2016) |

Es decir, cada año cerca de uno de cada diez estudiantes abandona, y casi la mitad de una cohorte universitaria no llega al décimo semestre. Las áreas de ingeniería, arquitectura y urbanismo están entre las de menor graduación (Ministerio de Educación Nacional, 2016). Desde 2020 SPADIES no publica cifras por área de conocimiento (Universidad Icesi, 2025), por lo que no fue posible obtener un dato reciente específico de ingeniería ni de Unicomfacauca; ese dato queda como tarea del piloto con bienestar universitario.

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

El diplomado evalúa cómo se construye, despliega y opera la aplicación. RedNexus se diseñó para ser **pequeño, reconstruible y observable**: contenedores con una sola imagen para la API, el worker y las migraciones; manifiestos de Kubernetes con Kustomize que corren igual en k3d (Mac) y minikube (Windows); CI obligatorio en cada PR; imágenes multiarquitectura firmadas y con SBOM; y entrega continua con GitOps (Argo CD) sobre un clúster reconstruible con OpenTofu. Ver los ADR 001, 002 y 009.

## Referencias de la sección

- Machado, M. (2022). El aprendizaje entre pares y sus efectos en el desempeño de los estudiantes. *Desarrollo y Sociedad*, (92). https://doi.org/10.13043/DYS.92.1
- El Tiempo. (2025). *Deserción universitaria: las instituciones de Colombia donde más estudiantes abandonan y cómo les va a las mejores en Saber Pro*. https://www.eltiempo.com/vida/educacion/desercion-universitaria-las-instituciones-de-colombia-donde-mas-estudiantes-abandonan-y-como-les-va-a-las-mejores-en-saber-pro-3599723
- Infobae. (2026, 12 de febrero). *Estas son las reconocidas universidades acreditadas en Colombia de las que se están saliendo los estudiantes: subió la deserción, según el Ministerio de Educación*. https://www.infobae.com/colombia/2026/02/12/estas-son-las-universidades-acreditadas-con-mayor-desercion-en-colombia-comparacion-con-las-mejor-posicionadas-en-rankings-internacionales/
- La República. (2026). *Estas son las 10 universidades acreditadas que exhiben la mayor tasa de deserción*. https://www.larepublica.co/empresas/estas-son-las-10-universidades-acreditadas-que-exhiben-la-mayor-tasa-de-desercion-4325366
- Ministerio de Educación Nacional. (2016). *Deserción en educación superior: informe de seguimiento* [SPADIES]. https://www.mineducacion.gov.co/sistemasinfo/spadies/
- Ministerio de Educación Nacional. (s. f.). *SPADIES: estadísticas de deserción*. https://www.mineducacion.gov.co/sistemasinfo/spadies/secciones/Estadisticas-de-desercion/
- Universidad Icesi. (2025). *Informe de educación superior en Colombia* (agosto de 2025). https://www.icesi.edu.co/wp-content/uploads/2025/08/informe-educacion-superior-082025.pdf
