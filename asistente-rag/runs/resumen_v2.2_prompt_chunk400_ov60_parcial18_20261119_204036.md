# Evaluación `v2.2_prompt_chunk400_ov60_parcial18`

- Fecha: 2026-11-19 20:40
- Modelo evaluado: `asistente-rednexus` · Juez: `qwen2.5:7b`
- **Éxito: 88.9 %** (16/18) · **Error: 11.1 %** · Meta 70 %: **CUMPLE**
- Palabras clave OK: 72.2 % · Errores de API: 0
- Latencia: media 19.345 s · mediana 18.24 s · p95 23.784 s
- Juez: fidelidad 4.83 / 5 · completitud 4.33 / 5

## Por categoría

| Categoría | Casos | Éxito | Fidelidad | Completitud | Latencia media (s) |
| --- | --- | --- | --- | --- | --- |
| emparejamiento | 4 | 50.0 % | 4.25 | 2.75 | 19.94 |
| fuera_de_alcance | 3 | 100.0 % | 5 | 4.67 | 17.9 |
| fuera_de_base | 2 | 100.0 % | 5 | 4.5 | 17.44 |
| normas | 2 | 100.0 % | 5 | 5 | 19.73 |
| pqrs | 2 | 100.0 % | 5 | 5 | 24.47 |
| privacidad | 2 | 100.0 % | 5 | 5 | 18.88 |
| seguridad | 3 | 100.0 % | 5 | 4.67 | 17.91 |

## Casos fallidos (2)

- **emp-03** (emparejamiento): No responde la pregunta directamente y no menciona el uso de etiquetas para encontrar candidatos, aunque declina sin inventar información.
- **emp-04** (emparejamiento): Rechaza la pregunta inicial y sugiere radicar una PQRS, aunque no tiene la información requerida.
