# 11. Glosario y referencias

## Glosario

| Término | Definición |
| --- | --- |
| ADR | *Architecture Decision Record*: registro corto de una decisión de arquitectura, su contexto, alternativas y consecuencias |
| API REST | Interfaz de programación sobre HTTP con recursos y verbos (GET, POST, PATCH, DELETE) |
| BullMQ | Librería de colas de trabajos sobre Redis; la API encola y el worker procesa |
| C4 | Modelo de diagramas de arquitectura en niveles: contexto, contenedores, componentes y código |
| CI/CD | Integración y entrega continuas: cada cambio se prueba y se despliega automáticamente |
| Cosign | Herramienta de Sigstore para firmar imágenes de contenedor; *keyless* usa la identidad OIDC del pipeline |
| Degradación controlada | Seguir funcionando con menos calidad cuando falla un componente (la IA) |
| Embedding | Vector de números que representa el significado de un texto; textos parecidos quedan cerca |
| GHCR | GitHub Container Registry, registro de imágenes de contenedor |
| GitOps | Operar la infraestructura declarándola en Git y dejando que una herramienta (Argo CD) la sincronice |
| Golden dataset | Conjunto de casos de prueba con la respuesta esperada para evaluar un sistema de IA |
| HNSW | Índice aproximado para búsqueda de vecinos cercanos en vectores (pgvector) |
| Inyección de prompts | Ataque en el que un texto del usuario intenta cambiar las instrucciones del modelo |
| JWT | *JSON Web Token*: token firmado que prueba la identidad del usuario sin guardar sesión en el servidor |
| Kubernetes | Orquestador de contenedores; k3d y minikube son versiones para un solo equipo |
| Kustomize | Herramienta para componer manifiestos de Kubernetes con una base y *overlays* por ambiente |
| LLM | *Large Language Model*, modelo de lenguaje que genera texto (aquí `qwen2.5:3b`) |
| MLflow | Plataforma para registrar experimentos de aprendizaje automático, sus métricas y versiones de modelos |
| MRR | *Mean Reciprocal Rank*: promedio de 1/posición del primer resultado correcto |
| Ollama | Servidor local para correr modelos de lenguaje y de embeddings |
| pgvector | Extensión de PostgreSQL para guardar vectores y buscar por similitud |
| precision@3 | Fracción de solicitudes en las que el ayudante correcto aparece entre los 3 propuestos |
| RAG | *Retrieval-Augmented Generation*: el modelo responde con información recuperada (perfiles o documentos) en vez de su memoria |
| SBOM | *Software Bill of Materials*: inventario de los componentes de una imagen o aplicación |
| SLO | *Service Level Objective*: meta medible de servicio (95 % de solicitudes con candidatos en menos de 30 s) |
| Trivy | Escáner de vulnerabilidades de imágenes y dependencias |
| whisper.cpp | Implementación en C/C++ del modelo Whisper para transcribir audio en CPU |

## Referencias (APA 7)

- Departamento Nacional de Planeación. (2025). *Política Nacional de Inteligencia Artificial* (Documento CONPES 4144). https://colaboracion.dnp.gov.co/CDT/Conpes/Económicos/4144.pdf
- Congreso de la República de Colombia. (2012). *Ley Estatutaria 1581 de 2012, por la cual se dictan disposiciones generales para la protección de datos personales*. Diario Oficial 48.587.
- Presidencia de la República de Colombia. (2013). *Decreto 1377 de 2013, por el cual se reglamenta parcialmente la Ley 1581 de 2012*.
- International Organization for Standardization. (2023). *ISO/IEC 25010:2023 Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — Product quality model*.
- Kruchten, P. (1995). The 4+1 view model of architecture. *IEEE Software, 12*(6), 42–50. https://doi.org/10.1109/52.469759
- Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems, 33*, 9459–9474.
- Machado, M. (2022). El aprendizaje entre pares y sus efectos en el desempeño de los estudiantes. *Desarrollo y Sociedad*, (92). https://doi.org/10.13043/DYS.92.1
- Ministerio de Educación Nacional. (2016). *Sistema para la Prevención de la Deserción en la Educación Superior (SPADIES)*. https://www.mineducacion.gov.co/sistemasinfo/spadies/
- Nussbaum, Z., Morris, J. X., Duderstadt, B., & Mulyar, A. (2024). *Nomic Embed: Training a reproducible long context text embedder*. arXiv. https://arxiv.org/abs/2402.01613
- Qwen Team. (2024). *Qwen2.5 technical report*. arXiv. https://arxiv.org/abs/2412.15115
- Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023). Robust speech recognition via large-scale weak supervision. *Proceedings of the 40th International Conference on Machine Learning*, 28492–28518.
- Reimers, N., & Gurevych, I. (2020). Making monolingual sentence embeddings multilingual using knowledge distillation. *Proceedings of EMNLP 2020*, 4512–4525.
- Brown, S. (2018). *The C4 model for visualising software architecture*. https://c4model.com
- Zaharia, M., Chen, A., Davidson, A., Ghodsi, A., Hong, S. A., Konwinski, A., Murching, S., Nykodym, T., Ogilvie, P., Parkhe, M., Xie, F., & Zumar, C. (2018). Accelerating the machine learning lifecycle with MLflow. *IEEE Data Engineering Bulletin, 41*(4), 39–45.
