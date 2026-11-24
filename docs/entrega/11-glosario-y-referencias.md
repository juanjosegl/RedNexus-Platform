# 11. Glosario y referencias

## Glosario

| Término | Definición |
| --- | --- |
| ADR | *Architecture Decision Record*: registro corto de una decisión de arquitectura, su contexto, alternativas y consecuencias |
| API REST | Interfaz de programación sobre HTTP con recursos y verbos (GET, POST, PATCH, DELETE) |
| Argo CD | Herramienta de GitOps que compara lo declarado en Git con lo que corre en Kubernetes y lo sincroniza |
| BullMQ | Librería de colas de trabajos sobre Redis; la API encola y el worker procesa |
| C4 | Modelo de diagramas de arquitectura en niveles: contexto, contenedores, componentes y código |
| CI/CD | Integración y entrega continuas: cada cambio se prueba y se despliega automáticamente |
| Cola de trabajos | Lista de tareas pendientes que un proceso aparte (worker) atiende en orden, con reintentos |
| Cosign | Herramienta de Sigstore para firmar imágenes de contenedor; *keyless* usa la identidad OIDC del pipeline |
| Cuantización | Reducir la precisión de los pesos de un modelo (por ejemplo, a 4 bits, Q4_K_M) para que ocupe menos memoria y corra más rápido |
| Degradación controlada | Seguir funcionando con menos calidad cuando falla un componente (la IA) |
| Dokploy | Plataforma autoalojada para desplegar aplicaciones con Docker; el diplomado ofrecía un servidor compartido |
| *Drift* | Diferencia entre lo que dice Git y lo que corre en el clúster, por ejemplo por un cambio manual |
| Embedding | Vector de números que representa el significado de un texto; textos parecidos quedan cerca |
| GHCR | GitHub Container Registry, registro de imágenes de contenedor |
| GitOps | Operar la infraestructura declarándola en Git y dejando que una herramienta (Argo CD) la sincronice |
| Golden dataset | Conjunto de casos de prueba con la respuesta esperada para evaluar un sistema de IA |
| HNSW | Índice aproximado para búsqueda de vecinos cercanos en vectores (pgvector) |
| IaC | *Infrastructure as Code*: infraestructura descrita en archivos versionados y aplicada por una herramienta (OpenTofu) |
| Inyección de prompts | Ataque en el que un texto del usuario intenta cambiar las instrucciones del modelo |
| JWT | *JSON Web Token*: token firmado que prueba la identidad del usuario sin guardar sesión en el servidor |
| k3d, kind, minikube | Formas de correr Kubernetes en un solo equipo (k3d y kind dentro de Docker) |
| Kubernetes | Orquestador de contenedores: los arranca, los reinicia si fallan y los conecta |
| Kustomize | Herramienta para componer manifiestos de Kubernetes con una base y *overlays* por ambiente |
| Kyverno | Motor de políticas de Kubernetes; aquí rechaza imágenes sin firma o de registros no permitidos |
| LLM | *Large Language Model*, modelo de lenguaje que genera texto (aquí `qwen2.5:3b`) |
| LLM como juez | Usar un modelo más grande (`qwen2.5:7b`) para calificar las respuestas de otro según criterios explícitos |
| MLflow | Plataforma para registrar experimentos de aprendizaje automático, sus métricas y versiones de modelos |
| MLOps / LLMOps | Prácticas para versionar, medir, desplegar y operar modelos de aprendizaje automático y de lenguaje |
| MRR | *Mean Reciprocal Rank*: promedio de 1/posición del primer resultado correcto |
| Ollama | Servidor local para correr modelos de lenguaje y de embeddings |
| Open WebUI | Interfaz web autoalojada para modelos de Ollama, con bases de conocimiento para RAG y API compatible con OpenAI |
| OpenTelemetry | Estándar abierto para emitir trazas, métricas y logs desde una aplicación |
| OpenTofu | Herramienta de infraestructura como código, bifurcación abierta de Terraform |
| pgvector | Extensión de PostgreSQL para guardar vectores y buscar por similitud |
| precision@3 | Fracción de solicitudes en las que el ayudante correcto aparece entre los 3 propuestos |
| RAG | *Retrieval-Augmented Generation*: el modelo responde con información recuperada (perfiles o documentos) en vez de su memoria |
| Sealed Secrets | Secretos de Kubernetes cifrados con una llave pública para poder guardarlos en Git |
| SBOM | *Software Bill of Materials*: inventario de los componentes de una imagen o aplicación |
| SLI / SLO | Indicador de nivel de servicio (lo que se mide, `rednexus.match.latency`) y objetivo (95 % en menos de 30 s) |
| TPS | *Tokens per second*: velocidad con la que el modelo genera texto |
| Traefik | Proxy inverso que enruta dominios hacia contenedores; lo usa Dokploy y el Ingress de k3d |
| Trivy | Escáner de vulnerabilidades de imágenes y dependencias |
| TTFT | *Time to first token*: tiempo desde la petición hasta el primer fragmento de la respuesta |
| whisper.cpp | Implementación en C/C++ del modelo Whisper para transcribir audio en CPU |
| Worker | Proceso que corre aparte de la API y atiende la cola de trabajos (clasificar, emparejar, transcribir) |

## Referencias (APA 7)

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site reliability engineering: How Google runs production systems*. O'Reilly Media.
- Brown, S. (2018). *The C4 model for visualising software architecture*. https://c4model.com
- Burns, B., Grant, B., Oppenheimer, D., Brewer, E., & Wilkes, J. (2016). Borg, Omega, and Kubernetes. *Communications of the ACM, 59*(5), 50–57. https://doi.org/10.1145/2890784
- Congreso de la República de Colombia. (2012). *Ley Estatutaria 1581 de 2012, por la cual se dictan disposiciones generales para la protección de datos personales*. Diario Oficial 48.587.
- Departamento Nacional de Planeación. (2025). *Política Nacional de Inteligencia Artificial* (Documento CONPES 4144). https://colaboracion.dnp.gov.co/CDT/Conpes/Económicos/4144.pdf
- El Tiempo. (2025). *Deserción universitaria: las instituciones de Colombia donde más estudiantes abandonan y cómo les va a las mejores en Saber Pro*. https://www.eltiempo.com/vida/educacion/desercion-universitaria-las-instituciones-de-colombia-donde-mas-estudiantes-abandonan-y-como-les-va-a-las-mejores-en-saber-pro-3599723
- Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2024). RAGAS: Automated evaluation of retrieval augmented generation. *Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations*, 150–158.
- Infobae. (2026, 12 de febrero). *Estas son las reconocidas universidades acreditadas en Colombia de las que se están saliendo los estudiantes: subió la deserción, según el Ministerio de Educación*. https://www.infobae.com/colombia/2026/02/12/estas-son-las-universidades-acreditadas-con-mayor-desercion-en-colombia-comparacion-con-las-mejor-posicionadas-en-rankings-internacionales/
- International Organization for Standardization. (2023). *ISO/IEC 25010:2023 Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — Product quality model*.
- Kruchten, P. (1995). The 4+1 view model of architecture. *IEEE Software, 12*(6), 42–50. https://doi.org/10.1109/52.469759
- La República. (2026). *Estas son las 10 universidades acreditadas que exhiben la mayor tasa de deserción*. https://www.larepublica.co/empresas/estas-son-las-10-universidades-acreditadas-que-exhiben-la-mayor-tasa-de-desercion-4325366
- Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems, 33*, 9459–9474.
- Machado, M. (2022). El aprendizaje entre pares y sus efectos en el desempeño de los estudiantes. *Desarrollo y Sociedad*, (92). https://doi.org/10.13043/DYS.92.1
- Malkov, Y. A., & Yashunin, D. A. (2020). Efficient and robust approximate nearest neighbor search using hierarchical navigable small world graphs. *IEEE Transactions on Pattern Analysis and Machine Intelligence, 42*(4), 824–836. https://doi.org/10.1109/TPAMI.2018.2889473
- Ministerio de Educación Nacional. (2016). *Deserción en educación superior: informe de seguimiento* [SPADIES]. https://www.mineducacion.gov.co/sistemasinfo/spadies/
- Ministerio de Educación Nacional. (s. f.). *SPADIES: estadísticas de deserción*. https://www.mineducacion.gov.co/sistemasinfo/spadies/secciones/Estadisticas-de-desercion/
- National Institute of Standards and Technology. (2022). *Secure Software Development Framework (SSDF) version 1.1* (NIST SP 800-218). https://doi.org/10.6028/NIST.SP.800-218
- National Institute of Standards and Technology. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)* (NIST AI 100-1). https://doi.org/10.6028/NIST.AI.100-1
- Newman, Z., Meyers, J. S., & Torres-Arias, S. (2022). Sigstore: Software signing for everybody. *Proceedings of the 2022 ACM SIGSAC Conference on Computer and Communications Security*, 2353–2367. https://doi.org/10.1145/3548606.3560596
- Nussbaum, Z., Morris, J. X., Duderstadt, B., & Mulyar, A. (2024). *Nomic Embed: Training a reproducible long context text embedder*. arXiv. https://arxiv.org/abs/2402.01613
- Nygard, M. (2011). *Documenting architecture decisions*. https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- OpenGitOps. (2021). *GitOps principles v1.0.0*. Cloud Native Computing Foundation. https://opengitops.dev
- Presidencia de la República de Colombia. (2013). *Decreto 1377 de 2013, por el cual se reglamenta parcialmente la Ley 1581 de 2012*.
- Qwen Team. (2024). *Qwen2.5 technical report*. arXiv. https://arxiv.org/abs/2412.15115
- Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023). Robust speech recognition via large-scale weak supervision. *Proceedings of the 40th International Conference on Machine Learning*, 28492–28518.
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using siamese BERT-networks. *Proceedings of EMNLP-IJCNLP 2019*, 3982–3992.
- Reimers, N., & Gurevych, I. (2020). Making monolingual sentence embeddings multilingual using knowledge distillation. *Proceedings of EMNLP 2020*, 4512–4525.
- Topping, K. J. (1996). The effectiveness of peer tutoring in further and higher education: A typology and review of the literature. *Higher Education, 32*(3), 321–345. https://doi.org/10.1007/BF00138870
- Universidad Icesi. (2025). *Informe de educación superior en Colombia* (agosto de 2025). https://www.icesi.edu.co/wp-content/uploads/2025/08/informe-educacion-superior-082025.pdf
- Zaharia, M., Chen, A., Davidson, A., Ghodsi, A., Hong, S. A., Konwinski, A., Murching, S., Nykodym, T., Ogilvie, P., Parkhe, M., Xie, F., & Zumar, C. (2018). Accelerating the machine learning lifecycle with MLflow. *IEEE Data Engineering Bulletin, 41*(4), 39–45.
- Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., & Stoica, I. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems, 36*.
