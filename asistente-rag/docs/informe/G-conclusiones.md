# G. Conclusiones y trabajos futuros

## G.1 Conclusiones

- **El asistente cumple la meta.** Con la configuración elegida (400 tokens de fragmento y 60 de solapamiento)
  alcanza un **88,5 % de éxito** en los 52 casos del golden dataset, frente al 70 % que pide la actividad. Las
  categorías de seguridad, fuera de alcance y fuera de la base quedan al 100 %: no reveló su prompt, no pidió ni
  aceptó contraseñas y no inventó precios ni funciones ante preguntas sin respuesta en la documentación.
- **El tamaño del fragmento importa.** Con 300/30 el éxito baja a 80,8 %, sobre todo en los temas cuyas respuestas
  son listas o procedimientos (emparejamiento, normas y PQRS). Para documentos escritos con secciones cortas y
  autocontenidas, un fragmento que contenga la sección completa funciona mejor que uno más pequeño.
- **La evaluación guió el diseño del prompt.** La primera versión del prompt parecía buena por el porcentaje
  (83,3 %), pero filtraba sus instrucciones ante un ataque simple. Solo los casos de seguridad del golden dataset
  lo mostraron. Corregirlo bajó la precisión en otras categorías y obligó a ajustar las reglas hasta la versión
  v2.2. Con un modelo pequeño funcionan mejor las reglas concretas, con disparadores y frases exactas, que las
  instrucciones generales.
- **El juez también necesita evaluación.** El modelo juez calificaba mal los rechazos correctos y aprobaba
  respuestas con hechos errados; hubo que reescribir su prompt para que evaluara el significado y no la redacción.
  Los resultados se revisaron a mano antes de darlos por buenos.
- **RAG con modelos locales es viable para soporte.** Todo corre en un MacBook M1 de 8 GB, sin enviar las
  preguntas a servicios externos y sin costo por uso. Actualizar el asistente es tan simple como editar un archivo
  Markdown y volver a correr `setup_openwebui.py`.

## G.2 Dificultades

- **Hardware:** con 8 GB de RAM no caben el modelo evaluado y el juez a la vez; la evaluación se partió en dos fases
  y hubo que apagar otros contenedores (el clúster de Kubernetes local) mientras corría.
- **Tiempos de respuesta:** cerca de 19 s por respuesta. Es aceptable para un chat de ayuda, pero lejos de lo
  ideal, y hace que cada corrida completa tarde unos 20 minutos.
- **Español y paráfrasis:** el modelo responde bien en español, pero cambia las palabras de la documentación; por
  eso las palabras clave solas (63,5 %) subestiman la calidad real y se combinaron con el juez.
- **Detalles de Open WebUI:** la configuración por API tiene comportamientos poco documentados (la plantilla RAG se
  borra si no se envía, el modelo nuevo no aparece hasta refrescar la caché y las fuentes solo llegan en modo
  *streaming*). Se resolvieron en el script de configuración y en el backend.

## G.3 Trabajos futuros

1. **Probar un modelo más grande** (por ejemplo `qwen2.5:7b` o `llama3.1:8b`) en un servidor con más memoria, para
   reducir las alucinaciones parciales (pqr-04, emp-02) y los rechazos indebidos.
2. **Activar la búsqueda híbrida** (BM25 + vectores) y un *reranker*, para que las preguntas informales encuentren
   los fragmentos aunque usen palabras distintas a las de los documentos.
3. **Medir la latencia sin la reescritura de la consulta** (`RETRIEVAL_QUERY_GENERATION=false`), que ahorra una
   llamada al modelo por pregunta.
4. **Completar la base de conocimiento** con el documento de solicitudes de ayuda y ampliar el golden dataset con
   preguntas reales de los usuarios, tomadas de las PQRS y de las conversaciones del asistente.
5. **Llevar el asistente al despliegue:** hoy la demo desplegada usa el proveedor *mock*. El paso siguiente es
   desplegar Open WebUI y Ollama junto a RedNexus, con un modelo adecuado al servidor, y monitorear las respuestas.
