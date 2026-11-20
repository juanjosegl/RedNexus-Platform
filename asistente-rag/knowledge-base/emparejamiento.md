# Emparejamiento con IA en RedNexus

El emparejamiento es la función que, cuando publicas una solicitud de ayuda, busca entre los perfiles de la
comunidad a los compañeros que mejor pueden ayudarte y te propone hasta 3 candidatos, cada uno con una frase que
explica por qué encaja contigo.

## ¿Cómo funciona el emparejamiento?

1. Publicas una solicitud de ayuda con tu duda. La solicitud queda en estado **Pendiente** mientras la IA trabaja.
2. La IA lee tu duda y la clasifica: el área (por ejemplo bases de datos, programación, matemáticas, redes,
   cloud y DevOps, inglés o física), los temas concretos y el nivel (básico, intermedio o avanzado).
3. La IA convierte tu duda en un vector numérico que representa su significado y lo compara con los perfiles de
   los demás estudiantes, que también están convertidos en vectores a partir de su descripción y sus etiquetas.
4. Toma los 10 perfiles más parecidos y les da un puntaje: el 80 % viene de qué tan parecido es el perfil a tu duda
   y el 20 % de su calificación promedio como ayudante.
5. Te propone los 3 candidatos con mejor puntaje y la solicitud pasa a estado **Con candidatos**.

Todo el emparejamiento corre con modelos de IA locales, dentro de la infraestructura de RedNexus; tu duda no se
envía a servicios externos de IA.

## ¿Qué significa la explicación de cada candidato?

Cada candidato trae una frase corta generada por la IA que explica por qué puede ayudarte. Esa frase se escribe
usando solo la información del perfil del candidato (su descripción y sus etiquetas): la IA no inventa títulos,
habilidades ni experiencia. Si el perfil tiene poca información, la explicación también será corta.

## Reglas del emparejamiento

- Nunca se te propone a ti mismo como candidato.
- Un perfil muy poco parecido a tu duda no se propone, aunque tenga buenas calificaciones.
- Un ayudante sin calificaciones cuenta como si tuviera 3 de 5 estrellas, para no castigar a los nuevos.
- Se proponen como máximo 3 candidatos por solicitud.
- La meta es que los candidatos aparezcan en menos de 30 segundos.

## ¿Qué pasa si la IA no está disponible?

Si la IA no responde, RedNexus usa un respaldo por etiquetas: compara las palabras de tu duda con las
descripciones y etiquetas de los perfiles. Así siempre recibes candidatos, aunque pueden ser menos precisos.

## ¿Qué pasa después del emparejamiento?

1. Cada candidato ve tu solicitud y puede **aceptarla** o **rechazarla**.
2. El primer candidato que acepta queda como tu ayudante y la solicitud pasa a estado **Aceptada**. Los demás ya
   no pueden aceptarla.
3. Al aceptar, el ayudante recibe tu correo para ponerse en contacto contigo.
4. Cuando terminas, cierras la solicitud y puedes calificar la ayuda de 1 a 5 estrellas.

## Cómo mejorar tus resultados de emparejamiento

- **Describe bien tu duda.** "No entiendo los joins en SQL" funciona mejor que "ayuda con base de datos".
- **Completa tu perfil.** Si quieres ayudar a otros, escribe en tu descripción qué sabes y agrega etiquetas con
  tus materias. La IA solo te puede proponer como candidato si tu perfil dice en qué eres bueno.
- **Califica a quien te ayudó.** Las calificaciones mejoran el puntaje de los buenos ayudantes.

## Problemas comunes con el emparejamiento

### Mi solicitud sigue en Pendiente

La IA está procesando la solicitud. La página se actualiza sola cada pocos segundos. Si pasan varios minutos,
recarga la página; si sigue igual, reporta el problema con una PQRS.

### Los candidatos no tienen relación con mi duda

Suele pasar cuando la duda es muy corta o muy general, o cuando todavía hay pocos perfiles sobre ese tema.
Publica una nueva solicitud con más detalle.

### Nadie acepta mi solicitud

Los candidatos deciden si tienen tiempo para ayudar. Puedes cerrar la solicitud y publicar una nueva con más
detalle para recibir otros candidatos.

## Preguntas frecuentes sobre el emparejamiento

**¿Puedo elegir yo a mi ayudante?**
No directamente: la IA propone 3 candidatos y el primero que acepta queda como tu ayudante.

**¿La IA lee mis datos personales?**
La IA solo usa el texto de tu duda y, de los candidatos, su descripción y sus etiquetas.

**¿Por qué no aparezco como candidato para ayudar?**
Porque tu perfil no tiene descripción ni etiquetas, o porque no se parece a las dudas publicadas. Complétalo en
**Perfil**.
