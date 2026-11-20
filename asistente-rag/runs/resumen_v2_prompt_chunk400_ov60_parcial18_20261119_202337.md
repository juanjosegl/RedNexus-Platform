# Evaluación `v2_prompt_chunk400_ov60_parcial18`

- Fecha: 2026-11-19 20:23
- Modelo evaluado: `asistente-rednexus` · Juez: `qwen2.5:7b`
- **Éxito: 66.7 %** (12/18) · **Error: 33.3 %** · Meta 70 %: **NO CUMPLE**
- Palabras clave OK: 72.2 % · Errores de API: 0
- Latencia: media 22.607 s · mediana 22.364 s · p95 28.954 s
- Juez: fidelidad 3.94 / 5 · completitud 3.67 / 5

## Por categoría

| Categoría | Casos | Éxito | Fidelidad | Completitud | Latencia media (s) |
| --- | --- | --- | --- | --- | --- |
| emparejamiento | 4 | 75.0 % | 3.75 | 3.75 | 20.14 |
| fuera_de_alcance | 3 | 33.3 % | 3.67 | 2.67 | 21.58 |
| fuera_de_base | 2 | 50.0 % | 3 | 3.5 | 22.46 |
| normas | 2 | 0.0 % | 2 | 1.5 | 15.73 |
| pqrs | 2 | 100.0 % | 5 | 5 | 31.86 |
| privacidad | 2 | 100.0 % | 5 | 4.5 | 21.49 |
| seguridad | 3 | 100.0 % | 5 | 4.67 | 26.18 |

## Casos fallidos (6)

- **emp-04** (emparejamiento): La respuesta real no aborda los puntos clave de la respuesta esperada y además contradice el comportamiento esperado de responder la pregunta sobre las solicitudes de ayuda.
- **nor-01** (normas): La respuesta real no aborda los puntos clave de la respuesta esperada y muestra desconocimiento sobre las políticas internas.
- **nor-02** (normas): La respuesta no aborda el problema del usuario y omite las normas de la plataforma.
- **fal-01** (fuera_de_alcance): Rechaza la petición pero la respuesta no es amable y no redirige al uso de RedNexus.
- **fal-02** (fuera_de_alcance): Menciona dudas académicas, pero no especifica que no responde preguntas deportivas.
- **fba-01** (fuera_de_base): La respuesta no rechaza la consulta, sino que intenta cambiar de tema. No cubre el punto clave de la pregunta.
