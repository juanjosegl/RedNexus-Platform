"""Genera el dataset sintético de RedNexus (IA-06).

Escribe profiles.json (50 ayudantes ficticios), requests.json (100 solicitudes con el o los
ayudantes correctos marcados) y off_topic.json (10 dudas que nadie del dataset puede resolver). Ningún dato corresponde a una persona real (Ley 1581): los nombres
son inventados y los correos usan el dominio rednexus.dev.

Reglas con las que se escribió:
- Los 20 perfiles con habilidades del seed del backend están incluidos tal cual (mismo correo),
  así la base de la demo y la de los experimentos son la misma.
- Varios perfiles comparten área pero no tema (SQL básico vs. PostgreSQL avanzado, cálculo de una
  variable vs. cálculo vectorial) para que el ranking tenga que distinguir.
- Las solicitudes están escritas como las escribiría un estudiante y casi nunca repiten las
  palabras del perfil (por ejemplo "unir tres tablas con una intermedia" para un perfil que dice
  "joins muchos a muchos"). Así se mide significado y no coincidencia de palabras.
- `relevant` lista los ayudantes que pueden resolver la duda, del más al menos indicado.
- `avgRating` simula el promedio de calificaciones (None = sin calificaciones todavía).

Uso: python ml/data/build_dataset.py
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

# (id, nombre, bio, etiquetas, avgRating)
PROFILES = [
    # --- los 20 del seed del backend ---
    ("ana", "Ana Gómez", "Sé SQL, joins entre tablas, relaciones muchos a muchos y modelado entidad-relación. Fui monitora de Bases de Datos I.", ["bases-de-datos", "sql", "modelado", "intermedio"], 4.8),
    ("carlos", "Carlos Muñoz", "PostgreSQL avanzado: índices, optimización de consultas lentas, transacciones y procedimientos almacenados.", ["bases-de-datos", "postgresql", "optimizacion", "avanzado"], 4.5),
    ("laura", "Laura Ordóñez", "Programo en Python desde el colegio. Puedo explicar funciones, bucles, listas, diccionarios y recursión desde cero.", ["programacion", "python", "basico"], 4.9),
    ("andres", "Andrés Caicedo", "Programación orientada a objetos en Java: clases, herencia, interfaces, polimorfismo y patrones de diseño.", ["programacion", "java", "poo", "intermedio"], 4.2),
    ("valentina", "Valentina Ruiz", "Desarrollo web con JavaScript, TypeScript y Vue 3. También ayudo con HTML, CSS y consumo de APIs REST.", ["programacion", "javascript", "vue", "web"], 4.6),
    ("juan", "Juan Pablo Torres", "Backend con Node.js y NestJS, APIs REST, autenticación con JWT y pruebas unitarias.", ["programacion", "nestjs", "backend", "avanzado"], 4.4),
    ("sofia", "Sofía Paz", "Cálculo diferencial e integral: límites, derivadas, regla de la cadena e integrales por partes.", ["matematicas", "calculo", "derivadas", "integrales"], 4.7),
    ("mateo", "Mateo Hurtado", "Álgebra lineal: matrices, determinantes, sistemas de ecuaciones, vectores y valores propios.", ["matematicas", "algebra-lineal", "matrices"], 4.1),
    ("isabella", "Isabella Castro", "Estadística y probabilidad: distribuciones, pruebas de hipótesis, regresión lineal. Uso Excel y R.", ["matematicas", "estadistica", "probabilidad"], 4.6),
    ("santiago", "Santiago Bolaños", "Matemáticas discretas y lógica: conjuntos, grafos, inducción matemática y combinatoria.", ["matematicas", "discretas", "grafos", "logica"], 3.9),
    ("daniela", "Daniela Velasco", "Redes de computadores: modelo OSI, TCP/IP, subredes, máscaras, DNS y configuración de routers Cisco.", ["redes", "tcp-ip", "subredes", "cisco"], 4.8),
    ("felipe", "Felipe Rengifo", "Docker, contenedores, Kubernetes y despliegue continuo con GitHub Actions. Administro servidores Linux.", ["cloud-devops", "docker", "kubernetes", "linux"], 4.5),
    ("camila", "Camila Mosquera", "Git y GitHub: ramas, merge, rebase, resolver conflictos y flujo de pull requests en equipo.", ["programacion", "git", "colaboracion"], 4.3),
    ("nicolas", "Nicolás Erazo", "Estructuras de datos y algoritmos: listas enlazadas, árboles, pilas, colas, ordenamiento y complejidad Big O.", ["programacion", "algoritmos", "estructuras-de-datos"], 4.0),
    ("mariana", "Mariana López", "Inglés nivel B2: gramática, tiempos verbales, redacción de ensayos y preparación para exámenes de inglés.", ["ingles", "gramatica", "writing"], 4.7),
    ("sebastian", "Sebastián Chicangana", "Física mecánica: cinemática, leyes de Newton, fuerza, trabajo y energía. También circuitos eléctricos básicos.", ["fisica", "mecanica", "circuitos"], 4.2),
    ("paula", "Paula Fernández", "Machine learning con Python: pandas, scikit-learn, regresión, clasificación y evaluación de modelos.", ["programacion", "python", "machine-learning", "datos"], 4.8),
    ("david", "David Imbachí", "Bases de datos NoSQL con MongoDB, diseño de documentos y consultas de agregación.", ["bases-de-datos", "mongodb", "nosql"], None),
    ("alejandra", "Alejandra Rivera", "Ingeniería de software: requisitos, historias de usuario, diagramas UML, casos de uso y Scrum.", ["ingenieria-de-software", "uml", "requisitos", "scrum"], 4.4),
    ("tomas", "Tomás Guerrero", "Seguridad informática: OWASP Top 10, inyección SQL, XSS, cifrado y buenas prácticas de contraseñas.", ["seguridad", "owasp", "cifrado"], 4.1),
    # --- 30 nuevos (IA-06) ---
    ("julian", "Julián Ceballos", "Consultas SQL desde lo básico: SELECT, filtros con WHERE, GROUP BY, HAVING y subconsultas. Monitor de Bases de Datos.", ["bases-de-datos", "sql", "basico"], 4.3),
    ("natalia", "Natalia Quintero", "Modelado de datos: diagramas entidad-relación, cardinalidades y normalización hasta tercera forma normal.", ["bases-de-datos", "modelado", "normalizacion"], 4.6),
    ("esteban", "Esteban Muñoz", "MySQL en producción: procedimientos almacenados, triggers, vistas, usuarios y copias de seguridad.", ["bases-de-datos", "mysql", "administracion"], 3.8),
    ("gabriela", "Gabriela Ospina", "Python intermedio: clases y objetos en Python, manejo de excepciones, lectura de archivos, módulos y entornos virtuales con venv.", ["programacion", "python", "intermedio"], 4.5),
    ("kevin", "Kevin Anacona", "C y C++: punteros, memoria dinámica con malloc y new, structs, compilación con gcc y make.", ["programacion", "c", "cpp"], 4.0),
    ("luisa", "Luisa Fernanda Rojas", "Maquetación web: HTML semántico, CSS, Flexbox, Grid, diseño responsive y accesibilidad.", ["programacion", "web", "css", "frontend"], 4.7),
    ("cristian", "Cristian Yalanda", "Desarrollo móvil Android con Kotlin y Jetpack Compose: pantallas, listas, navegación y ciclo de vida.", ["programacion", "kotlin", "android", "movil"], 4.2),
    ("manuela", "Manuela Arboleda", "JavaScript asíncrono: callbacks, promesas, async/await, fetch y el event loop del navegador.", ["programacion", "javascript", "asincronia"], 4.4),
    ("jhon", "Jhon Fredy Palechor", "Backend en Java con Spring Boot: controladores REST, JPA, Hibernate y conexión a bases de datos.", ["programacion", "java", "spring-boot", "backend"], 4.1),
    ("diana", "Diana Marcela Solarte", "Ecuaciones diferenciales ordinarias: separables, lineales, de segundo orden y transformada de Laplace.", ["matematicas", "ecuaciones-diferenciales", "laplace"], 4.5),
    ("ricardo", "Ricardo Benavides", "Cálculo multivariable: derivadas parciales, gradiente, integrales dobles y triples, coordenadas polares y esféricas.", ["matematicas", "calculo-vectorial", "multivariable"], 3.9),
    ("valeria", "Valeria Muñoz", "Precálculo y álgebra básica: factorización, fracciones algebraicas, funciones, trigonometría y logaritmos.", ["matematicas", "precalculo", "algebra", "basico"], 4.9),
    ("carolina", "Carolina Idrobo", "Probabilidad: técnicas de conteo, permutaciones, combinaciones, teorema de Bayes y variables aleatorias.", ["matematicas", "probabilidad", "conteo"], 4.3),
    ("andrea", "Andrea Collazos", "Redes conmutadas e inalámbricas: VLAN, enrutamiento entre VLAN, firewalls, WiFi y prácticas en Packet Tracer.", ["redes", "vlan", "packet-tracer", "firewall"], 4.0),
    ("oscar", "Óscar Mosquera", "Administración de Linux: terminal, scripts en bash, permisos, procesos, ssh, cron y firewall con ufw.", ["cloud-devops", "linux", "bash"], 4.6),
    ("melissa", "Melissa Burbano", "Nube en AWS: EC2, S3, IAM, redes VPC e infraestructura como código con Terraform.", ["cloud-devops", "aws", "terraform"], 4.2),
    ("brayan", "Brayan Ijají", "Integración y entrega continua: pipelines en GitHub Actions y Jenkins, pruebas automáticas y despliegues.", ["cloud-devops", "ci-cd", "github-actions", "jenkins"], 3.7),
    ("juliana", "Juliana Cerón", "Inglés conversacional: speaking, pronunciación, listening y preparación de entrevistas de trabajo en inglés.", ["ingles", "speaking", "pronunciacion"], 4.8),
    ("alexander", "Alexander Lasso", "Inglés técnico para ingeniería: leer documentación, artículos científicos y vocabulario de software en inglés.", ["ingles", "ingles-tecnico", "lectura"], 4.0),
    ("lorena", "Lorena Calambás", "Física de electricidad y magnetismo: ley de Coulomb, campo eléctrico, ley de Gauss, ley de Ohm, inducción y ley de Faraday.", ["fisica", "electromagnetismo", "electricidad"], 4.4),
    ("hector", "Héctor Mueses", "Física de ondas, óptica y termodinámica: interferencia, calor, gases ideales y leyes de la termodinámica.", ["fisica", "ondas", "termodinamica"], 3.6),
    ("ximena", "Ximena Vidal", "Química general: estequiometría, balanceo de ecuaciones, óxido-reducción, reactivo límite y tabla periódica.", ["quimica", "estequiometria"], 4.5),
    ("mauricio", "Mauricio Dorado", "Electrónica digital: compuertas lógicas, álgebra de Boole, mapas de Karnaugh, flip-flops y proyectos con Arduino.", ["electronica", "digital", "arduino"], 4.3),
    ("veronica", "Verónica Paredes", "Sistemas operativos: procesos e hilos, planificación de CPU, concurrencia, semáforos, interbloqueos y memoria virtual.", ["sistemas-operativos", "concurrencia", "hilos"], 4.1),
    ("fernando", "Fernando Ordóñez", "Arquitectura y diseño de software: principios SOLID, código limpio, patrones de diseño, MVC y microservicios.", ["ingenieria-de-software", "arquitectura", "solid", "patrones"], 4.6),
    ("lina", "Lina Marcela Gaviria", "Pruebas de software: pruebas unitarias, mocks, TDD, pruebas de integración con Jest y JUnit.", ["ingenieria-de-software", "testing", "tdd"], 4.2),
    ("pablo", "Pablo Andrés Chávez", "Deep learning con PyTorch y TensorFlow: redes neuronales, redes convolucionales y visión por computador.", ["ia", "deep-learning", "vision"], 4.7),
    ("adriana", "Adriana Montenegro", "Procesamiento de lenguaje natural y LLM: embeddings, búsqueda semántica, RAG, prompts y Hugging Face.", ["ia", "nlp", "llm", "rag"], 4.9),
    ("ivan", "Iván Darío Pino", "Hacking ético: pentesting, Kali Linux, escaneo con nmap, análisis de vulnerabilidades y retos CTF.", ["seguridad", "pentesting", "kali"], 3.9),
    ("monica", "Mónica Sandoval", "Redacción académica y metodología de investigación: normas APA 7, anteproyectos, planteamiento del problema y objetivos.", ["investigacion", "apa", "redaccion"], 4.8),
]

# (texto, área esperada, nivel, ayudantes correctos en orden)
REQUESTS = [
    # bases de datos
    ("No entiendo cómo unir tres tablas cuando hay una tabla intermedia entre estudiantes y cursos", "bases-de-datos", "intermedio", ["ana", "julian"]),
    ("Mi consulta en PostgreSQL tarda 40 segundos con una tabla de un millón de filas, ¿cómo la acelero?", "bases-de-datos", "avanzado", ["carlos"]),
    ("¿Qué diferencia hay entre WHERE y HAVING cuando agrupo resultados?", "bases-de-datos", "basico", ["julian", "ana"]),
    ("Tengo que pasar una tabla con datos repetidos a tercera forma normal y no sé por dónde empezar", "bases-de-datos", "intermedio", ["natalia", "ana"]),
    ("Cómo diseño el diagrama entidad relación de una biblioteca con préstamos de libros", "bases-de-datos", "intermedio", ["natalia", "ana"]),
    ("Necesito que cada vez que se actualice un registro en MySQL se guarde automáticamente un historial", "bases-de-datos", "intermedio", ["esteban"]),
    ("¿Cuándo conviene una base de documentos en vez de una relacional para un catálogo de productos?", "bases-de-datos", "intermedio", ["david"]),
    ("No sé armar un pipeline de agregación con $group y $lookup", "bases-de-datos", "avanzado", ["david"]),
    ("¿Qué es un interbloqueo entre transacciones y cómo evito que pase en mi base de datos?", "bases-de-datos", "avanzado", ["carlos", "veronica"]),
    ("Subconsultas correlacionadas: no entiendo cuándo se ejecuta la consulta de adentro", "bases-de-datos", "intermedio", ["julian"]),
    # python
    ("Empiezo a programar y no entiendo para qué sirven los ciclos for y while", "programacion", "basico", ["laura"]),
    ("Mi función que se llama a sí misma para el factorial nunca termina y se desborda", "programacion", "basico", ["laura", "nicolas"]),
    ("¿Cómo leo un archivo CSV línea por línea y controlo el error si el archivo no existe?", "programacion", "intermedio", ["gabriela"]),
    ("No entiendo la herencia ni el método __init__ en las clases de Python", "programacion", "intermedio", ["gabriela"]),
    ("Diferencia entre lista, tupla y diccionario y cuándo usar cada uno", "programacion", "basico", ["laura", "gabriela"]),
    # java
    ("No entiendo la diferencia entre una clase abstracta y una interfaz en Java", "programacion", "intermedio", ["andres"]),
    ("¿Qué es el polimorfismo? El profesor lo explicó con figuras geométricas y no me quedó claro", "programacion", "intermedio", ["andres"]),
    ("Cómo hago una API REST con Spring Boot que guarde los datos con JPA", "programacion", "intermedio", ["jhon"]),
    ("Me sale LazyInitializationException en Hibernate al traer una relación", "programacion", "avanzado", ["jhon"]),
    ("Qué patrón uso para crear objetos sin acoplarme a la clase concreta", "programacion", "avanzado", ["andres", "fernando"]),
    # web
    ("Mi componente de Vue no se actualiza en pantalla cuando cambio un dato dentro de un objeto", "programacion", "intermedio", ["valentina"]),
    ("No entiendo async await, mi función devuelve una promesa pendiente en vez del dato", "programacion", "intermedio", ["manuela", "valentina"]),
    ("Cómo pido datos a una API desde el navegador y los muestro en una tabla", "programacion", "basico", ["valentina", "manuela"]),
    ("Quiero que mi página se vea bien en el celular, los elementos se salen de la pantalla", "programacion", "basico", ["luisa"]),
    ("No logro centrar un div vertical y horizontalmente", "programacion", "basico", ["luisa"]),
    ("¿Qué significa que JavaScript tenga un solo hilo y cómo funciona el event loop?", "programacion", "intermedio", ["manuela"]),
    # backend node
    ("Cómo protejo las rutas de mi API con tokens para que solo entren usuarios con sesión", "programacion", "intermedio", ["juan"]),
    ("Estoy armando un backend con NestJS y no entiendo módulos, providers e inyección de dependencias", "programacion", "intermedio", ["juan"]),
    ("Cómo pruebo un servicio que usa la base de datos sin conectarme a la base real", "ingenieria-de-software", "intermedio", ["lina", "juan"]),
    # c / c++
    ("No entiendo los punteros: cuando paso un arreglo a una función se modifica el original", "programacion", "intermedio", ["kevin"]),
    ("Mi programa en C da segmentation fault cuando reservo memoria", "programacion", "intermedio", ["kevin"]),
    # móvil
    ("Quiero hacer mi primera aplicación para celular Android que muestre una lista", "programacion", "basico", ["cristian"]),
    ("En Jetpack Compose el estado se pierde al girar el celular", "programacion", "intermedio", ["cristian"]),
    # algoritmos
    ("Cómo calculo la complejidad de un algoritmo con dos ciclos anidados", "programacion", "intermedio", ["nicolas"]),
    ("Implementar un árbol binario de búsqueda e insertar y eliminar nodos", "programacion", "intermedio", ["nicolas"]),
    ("Qué método de ordenamiento es más rápido y por qué quicksort es n log n", "programacion", "intermedio", ["nicolas"]),
    ("Encontrar el camino más corto entre dos ciudades en un mapa con distancias", "matematicas", "avanzado", ["santiago", "nicolas"]),
    # git
    ("Hice merge y me salieron marcas <<<<<<< HEAD en el código, no sé qué borrar", "programacion", "basico", ["camila"]),
    ("¿Cuál es la diferencia entre rebase y merge? Mi equipo pide un historial limpio", "programacion", "intermedio", ["camila"]),
    ("Subí por error un archivo con contraseñas al repositorio, cómo lo saco del historial", "programacion", "intermedio", ["camila", "tomas"]),
    # cálculo
    ("No entiendo cómo derivar una función que está dentro de otra función", "matematicas", "basico", ["sofia"]),
    ("Integración por partes: nunca sé qué escoger como u y qué como dv", "matematicas", "intermedio", ["sofia"]),
    ("Cómo calculo un límite que me da cero sobre cero", "matematicas", "basico", ["sofia", "valeria"]),
    ("Integrales dobles en coordenadas polares para calcular el área de una región", "matematicas", "avanzado", ["ricardo"]),
    ("Qué representa el gradiente y la derivada direccional de una función de dos variables", "matematicas", "avanzado", ["ricardo"]),
    ("Resolver la ecuación de un tanque que se vacía, me dijeron que es una ecuación diferencial de primer orden", "matematicas", "intermedio", ["diana"]),
    ("Usar la transformada de Laplace para resolver un circuito RC", "matematicas", "avanzado", ["diana", "lorena"]),
    ("No sé factorizar trinomios ni simplificar fracciones con letras", "matematicas", "basico", ["valeria"]),
    ("Identidades trigonométricas para el examen de admisión", "matematicas", "basico", ["valeria"]),
    # álgebra lineal
    ("Cómo saco los valores y vectores propios de una matriz de 3x3", "matematicas", "intermedio", ["mateo"]),
    ("Resolver un sistema de tres ecuaciones con el método de Gauss-Jordan", "matematicas", "intermedio", ["mateo"]),
    ("Qué significa que unos vectores sean linealmente independientes", "matematicas", "intermedio", ["mateo"]),
    # estadística y probabilidad
    ("Cómo hago una prueba de hipótesis para comparar las medias de dos grupos", "matematicas", "intermedio", ["isabella"]),
    ("Cómo interpreto el R cuadrado de una regresión", "matematicas", "intermedio", ["isabella", "paula"]),
    ("Teorema de Bayes con el ejemplo de una prueba médica con falsos positivos", "matematicas", "intermedio", ["carolina", "isabella"]),
    ("¿De cuántas formas escojo un comité de 3 personas entre 10? No sé si es permutación o combinación", "matematicas", "basico", ["carolina", "santiago"]),
    ("Distribución binomial o de Poisson: cuándo uso cada una", "matematicas", "intermedio", ["carolina", "isabella"]),
    # discretas y numéricos
    ("Demostrar por inducción que la suma de los primeros n impares es n al cuadrado", "matematicas", "intermedio", ["santiago"]),
    ("Tablas de verdad y equivalencias lógicas para simplificar una proposición", "matematicas", "basico", ["santiago", "mauricio"]),
    ("Un resorte con amortiguamiento: cómo resuelvo la ecuación de segundo orden", "matematicas", "avanzado", ["diana"]),
    # redes
    ("Dividir una red /24 en 6 subredes y calcular las máscaras", "redes", "intermedio", ["daniela"]),
    ("Qué capa del modelo OSI se encarga de enrutar los paquetes", "redes", "basico", ["daniela"]),
    ("Configurar VLANs en un switch en Packet Tracer y que se comuniquen entre ellas", "redes", "intermedio", ["andrea", "daniela"]),
    ("La IP responde al ping pero la página no carga por el nombre, ¿será la resolución de nombres?", "redes", "intermedio", ["daniela"]),
    ("Cómo configuro el firewall para dejar pasar solo el puerto 443", "redes", "intermedio", ["andrea", "oscar"]),
    # cloud / devops
    ("Mi contenedor se detiene apenas arranca y no veo el error", "cloud-devops", "intermedio", ["felipe"]),
    ("Qué diferencia hay entre un Deployment y un Service en Kubernetes", "cloud-devops", "intermedio", ["felipe"]),
    ("Quiero que mis pruebas corran solas cada vez que hago push a GitHub", "cloud-devops", "intermedio", ["brayan", "felipe"]),
    ("Cómo escribo un script que haga copias de seguridad todas las noches en un servidor", "cloud-devops", "intermedio", ["oscar"]),
    ("Me sale permission denied al ejecutar un archivo en la terminal de Ubuntu", "cloud-devops", "basico", ["oscar"]),
    ("Subir mi aplicación a una máquina en Amazon y guardar los archivos subidos en un bucket", "cloud-devops", "intermedio", ["melissa"]),
    ("Estoy creando la infraestructura con Terraform y no entiendo qué es el state", "cloud-devops", "avanzado", ["melissa"]),
    ("Configurar un pipeline en Jenkins que construya y despliegue mi aplicación", "cloud-devops", "intermedio", ["brayan"]),
    # inglés
    ("Cuándo uso present perfect y cuándo simple past", "ingles", "intermedio", ["mariana"]),
    ("Tengo una entrevista de trabajo en inglés y me bloqueo al hablar", "ingles", "intermedio", ["juliana"]),
    ("Me cuesta entender la documentación en inglés de las librerías que uso", "ingles", "intermedio", ["alexander"]),
    ("Pronunciación de la th y de los verbos que terminan en ed", "ingles", "basico", ["juliana"]),
    # física
    ("Un bloque baja por un plano inclinado con fricción, cómo saco la aceleración", "fisica", "intermedio", ["sebastian"]),
    ("Calcular el campo eléctrico de una esfera cargada con la ley de Gauss", "fisica", "avanzado", ["lorena"]),
    ("No entiendo la inducción en una espira cuando cambia el flujo magnético", "fisica", "avanzado", ["lorena"]),
    ("Primera ley de la termodinámica en un gas que se expande", "fisica", "intermedio", ["hector"]),
    ("Resistencias en serie y en paralelo con la ley de Ohm", "fisica", "basico", ["sebastian", "lorena", "mauricio"]),
    # química y electrónica
    ("Balancear una ecuación química por el método de óxido reducción", "quimica", "intermedio", ["ximena"]),
    ("Cómo encuentro el reactivo límite en una reacción", "quimica", "basico", ["ximena"]),
    ("Simplificar una función lógica con mapas de Karnaugh", "electronica", "intermedio", ["mauricio"]),
    ("Que un Arduino lea un sensor de temperatura y prenda un LED", "electronica", "basico", ["mauricio"]),
    # sistemas operativos
    ("Diferencia entre proceso e hilo y cuándo usar varios hilos", "sistemas-operativos", "intermedio", ["veronica"]),
    ("Problema del productor y el consumidor con semáforos", "sistemas-operativos", "avanzado", ["veronica"]),
    # ingeniería de software
    ("Cómo escribo historias de usuario con criterios de aceptación para mi proyecto", "ingenieria-de-software", "basico", ["alejandra"]),
    ("Mi código tiene una clase gigante que hace de todo, cómo lo organizo mejor", "ingenieria-de-software", "intermedio", ["fernando"]),
    ("Cómo se hace TDD: escribo la prueba antes, falla, ¿y luego qué?", "ingenieria-de-software", "intermedio", ["lina"]),
    # IA
    ("Mi modelo de clasificación tiene 99 % en entrenamiento y 60 % en prueba", "ia", "intermedio", ["paula", "pablo"]),
    ("Cómo entreno una red neuronal convolucional para clasificar fotos", "ia", "avanzado", ["pablo"]),
    ("Qué es un embedding y cómo lo uso para buscar documentos parecidos", "ia", "intermedio", ["adriana"]),
    ("Cómo armo un chatbot que responda solo con mis propios documentos", "ia", "avanzado", ["adriana"]),
    # seguridad
    ("Cómo evito que me inyecten código en el formulario de inicio de sesión", "seguridad", "intermedio", ["tomas"]),
    ("Qué es XSS y cómo limpio lo que escriben los usuarios", "seguridad", "intermedio", ["tomas"]),
    ("Escanear los puertos abiertos de mi máquina virtual para la práctica de seguridad", "seguridad", "intermedio", ["ivan"]),
    # investigación
    ("Cómo cito un artículo y una página web en normas APA séptima edición", "investigacion", "basico", ["monica"]),
    ("Formular el planteamiento del problema y los objetivos del anteproyecto de grado", "investigacion", "intermedio", ["monica"]),
]

# Dudas que ningún ayudante del dataset puede resolver: sirven para calibrar el umbral de
# similitud (lo correcto es no proponer a nadie y que el respaldo o la PQRS se encarguen).
OFF_TOPIC = [
    "Cómo preparo una lasaña de carne para diez personas",
    "Recomiéndame una serie de televisión para ver el fin de semana",
    "Necesito aprender a tocar la guitarra, acordes básicos",
    "Qué rutina de gimnasio sirve para ganar masa muscular",
    "Cómo cuido una planta de orquídea que tiene las hojas amarillas",
    "Busco a alguien que me explique las reglas del ajedrez",
    "Cómo cambio la llanta pinchada de una bicicleta",
    "Ideas para decorar mi cuarto con poco presupuesto",
    "Quiero aprender a bailar salsa caleña",
    "Cómo saco la licencia de conducción en Popayán",
]


def main() -> None:
    ids = [p[0] for p in PROFILES]
    assert len(PROFILES) == 50, len(PROFILES)
    assert len(set(ids)) == 50, "ids repetidos"
    assert len(REQUESTS) == 100, len(REQUESTS)
    for text, _, level, relevant in REQUESTS:
        assert level in {"basico", "intermedio", "avanzado"}, text
        assert relevant and all(r in ids for r in relevant), (text, relevant)

    profiles = [
        {
            "id": pid,
            "email": f"{pid}.demo@rednexus.dev",
            "name": name,
            "bio": bio,
            "tags": tags,
            "avgRating": rating,
        }
        for pid, name, bio, tags, rating in PROFILES
    ]
    requests = [
        {"id": f"r{i:03d}", "text": text, "area": area, "level": level, "relevant": relevant}
        for i, (text, area, level, relevant) in enumerate(REQUESTS, start=1)
    ]
    (HERE / "profiles.json").write_text(json.dumps(profiles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / "requests.json").write_text(json.dumps(requests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / "off_topic.json").write_text(
        json.dumps([{"id": f"x{i:02d}", "text": t} for i, t in enumerate(OFF_TOPIC, start=1)], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    covered = {r for *_, rel in REQUESTS for r in rel}
    print(f"{len(profiles)} perfiles, {len(requests)} solicitudes; {len(covered)} ayudantes aparecen como correctos")


if __name__ == "__main__":
    main()
