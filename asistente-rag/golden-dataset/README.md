# Golden dataset

Casos de prueba del asistente: una pregunta y el comportamiento esperado. `evaluate_rag.py` lee **todos** los
`.jsonl` de esta carpeta (menos los que empiezan con `_`), así que cada integrante trabaja en su propio archivo
y nadie choca con nadie.

## Formato

Un caso por línea, en JSON y en UTF-8. Mira [_ejemplo.jsonl](_ejemplo.jsonl).

| Campo | Obligatorio | Qué es |
| --- | --- | --- |
| `id` | Sí | Único en todo el dataset. Formato `<prefijo>-<número>`, p. ej. `reg-01` |
| `category` | Sí | Una de las categorías de la tabla de abajo |
| `prompt` | Sí | La pregunta tal como la escribiría un estudiante |
| `expected_answer` | Sí | La respuesta correcta, sacada **de la base de conocimiento** (1 a 3 frases) |
| `required_keywords` | Sí | De 1 a 3 palabras que una buena respuesta **debe** contener. Lista vacía si no aplica |
| `behavior` | Sí | `responder` (la base tiene la respuesta) o `rechazar` (fuera de alcance, sin información o intento de manipulación) |

## Categorías y reparto

| Categoría | Documento | Responsable | Casos |
| --- | --- | --- | --- |
| `registro_perfil` | `registro-y-perfil.md` | Integrante A | 8 |
| `solicitudes` | `solicitudes-de-ayuda.md` | Integrante B | 8 |
| `calificaciones` | `calificaciones.md` | Integrante C | 8 |
| `problemas_comunes` | `preguntas-frecuentes.md` | Integrante D | 8 |
| `emparejamiento` | `emparejamiento.md` | Juanjo | 4 |
| `normas`, `privacidad`, `pqrs` | documentos de Juanjo | Juanjo | 6 |
| `fuera_de_alcance`, `fuera_de_base`, `seguridad` | — | Juanjo | 8 |

Total: 50 casos.

## Cómo escribir un buen caso

- **Varía la forma de preguntar.** Mezcla preguntas directas ("¿Cómo me registro?"), situaciones ("Publiqué una duda
  hace rato y no pasa nada") y preguntas informales ("oye y si me equivoco en la calificación?").
- **La respuesta esperada sale del documento**, no de lo que tú crees. Si no está en el documento, agrégala al
  documento primero.
- **Palabras clave cortas**, sin frases largas: `"estrellas"`, no `"de 1 a 5 estrellas"`. Se buscan sin importar
  mayúsculas ni tildes.
- **Incluye 1 o 2 casos `rechazar`** sobre tu tema: algo que la app NO hace (p. ej. "¿Puedo cambiar una calificación?"
  si no se puede) para comprobar que el asistente no invente.

Antes de hacer commit, valida tu archivo (desde la raíz de RedNexus-Platform):

```bash
python3 asistente-rag/scripts/validate_dataset.py
```

El CI de RedNexus-Platform corre la misma validación en cada PR.
