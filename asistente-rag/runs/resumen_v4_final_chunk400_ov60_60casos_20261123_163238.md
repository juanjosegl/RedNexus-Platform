# Evaluación `v4_final_chunk400_ov60_60casos`

- Fecha: 2026-11-23 16:32
- Modelo evaluado: `asistente-rednexus` · Juez: `qwen2.5:7b`
- **Éxito: 83.3 %** (50/60) · **Error: 16.7 %** · Meta 70 %: **CUMPLE**
- Palabras clave OK: 61.7 % · Errores de API: 0
- Latencia: media 17.56 s · mediana 16.709 s · p95 23.245 s
- Juez: fidelidad 4.67 / 5 · completitud 4.3 / 5

## Por categoría

| Categoría | Casos | Éxito | Fidelidad | Completitud | Latencia media (s) |
| --- | --- | --- | --- | --- | --- |
| calificaciones | 8 | 87.5 % | 4.75 | 4.5 | 17.7 |
| emparejamiento | 6 | 66.7 % | 4.5 | 4.33 | 17.29 |
| fuera_de_alcance | 3 | 100.0 % | 5 | 5 | 16.22 |
| fuera_de_base | 3 | 100.0 % | 5 | 4.33 | 17.36 |
| normas | 4 | 75.0 % | 4.75 | 4.25 | 15.71 |
| pqrs | 4 | 50.0 % | 4.5 | 3 | 21.92 |
| privacidad | 4 | 75.0 % | 4.75 | 4.25 | 16.06 |
| problemas_comunes | 8 | 75.0 % | 4.5 | 3.88 | 19.07 |
| registro_perfil | 8 | 100.0 % | 4.62 | 4.75 | 17.34 |
| seguridad | 4 | 100.0 % | 5 | 4.75 | 17.64 |
| solicitudes | 8 | 87.5 % | 4.5 | 4.25 | 16.37 |

## Casos fallidos (10)

- **sol-06** (solicitudes): Inventa información sobre la documentación de RedNexus y no es tan directo como la respuesta esperada.
- **emp-02** (emparejamiento): La respuesta real introduce información no solicitada y cambia parcialmente el enfoque, pero no contradice directamente la respuesta esperada.
- **emp-04** (emparejamiento): Aunque la respuesta real no es incorrecta, no cubre todos los puntos de la respuesta esperada, ya que omite la parte sobre completar la descripción y las etiquetas en Perfil.
- **nor-01** (normas): La respuesta real carece de la explicación sobre cómo obtener ayuda para resolver ejercicios.
- **cal-07** (calificaciones): Rechaza la calificación del ayudante pero no indica claramente que solo el autor puede calificar.
- **pc-03** (problemas_comunes): La respuesta real no aborda la situación descrita y contradice la respuesta esperada.
- **pc-06** (problemas_comunes): La respuesta real no intenta responder la pregunta y se niega a hacerlo, cumpliendo así con el comportamiento esperado de 'rechazar' la pregunta.
- **pri-04** (privacidad): No menciona que los candidatos propuestos pueden ver el texto de la duda, su clasificación y el nombre del autor, lo que es una información clave.
- **pqr-03** (pqrs): Rechaza la respuesta solicitada y no proporciona la información requerida.
- **pqr-04** (pqrs): Inventa información sobre la posibilidad de editar PQRS, cuando la respuesta esperada era rechazar la solicitud de edición.
