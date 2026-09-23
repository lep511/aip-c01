# Domain 4 — Operational Efficiency and Optimization for GenAI Applications

Cobertura completa del **Domain 4** del examen **AWS Certified Generative AI Developer – Professional (AIP-C01)**, construida a partir de documentación oficial de AWS (`docs.aws.amazon.com`).

> El contenido de las fuentes AWS fue parafraseado y resumido para cumplir con restricciones de licencia. Cada sección enlaza a la página oficial correspondiente.

## Datos del dominio

| Dato | Valor |
| --- | --- |
| Peso en el examen | **12 % del contenido puntuado** (cuarto dominio por peso, tras el 31 % del Domain 1, el 26 % del Domain 2 y el 20 % del Domain 3) |
| Tasks | 3 |
| Skills | 16 |
| Preguntas puntuadas | 65 (más 10 no puntuadas, no identificadas) |
| Score de aprobación | 750 en escala 100–1000 |
| Modelo de scoring | Compensatorio: no hace falta aprobar cada sección, solo el examen global |

Fuentes: [Exam Guide AIP-C01](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) · [Content Domain 4](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain4.html)

## Índice de archivos

Los Tasks 4.2 y 4.3 tienen seis skills cada uno y se reparten en dos archivos, con un corte temático y no aritmético. Cada archivo declara en su línea `Skills cubiertos:` solo los skills que documenta.

| Archivo | Task | Skills | Tema |
| --- | --- | --- | --- |
| [task-4-1-costes-y-eficiencia-de-recursos.md](./task-4-1-costes-y-eficiencia-de-recursos.md) | 4.1 | 4.1.1 – 4.1.4 | Optimización de costes y eficiencia de recursos |
| [task-4-2-latencia-y-throughput.md](./task-4-2-latencia-y-throughput.md) | 4.2 | 4.2.1, 4.2.3, 4.2.5 | Capacidad y tiempo de respuesta |
| [task-4-2-retrieval-y-parametros.md](./task-4-2-retrieval-y-parametros.md) | 4.2 | 4.2.2, 4.2.4, 4.2.6 | Calidad de lo recuperado y de lo generado |
| [task-4-3-observabilidad-y-metricas.md](./task-4-3-observabilidad-y-metricas.md) | 4.3 | 4.3.1 – 4.3.3 | La aplicación y sus métricas |
| [task-4-3-herramientas-vector-stores-y-fallos.md](./task-4-3-herramientas-vector-stores-y-fallos.md) | 4.3 | 4.3.4 – 4.3.6 | Herramientas, vector stores y modos de fallo |
| [referencias-oficiales.md](./referencias-oficiales.md) | — | — | Todas las páginas de AWS usadas, agrupadas por servicio |

## Mapa de las 16 skills

### Task 4.1 — Implementar estrategias de optimización de costes y eficiencia de recursos

- [**4.1.1**](./task-4-1-costes-y-eficiencia-de-recursos.md#skill-411--sistemas-de-eficiencia-de-tokens) Sistemas de eficiencia de tokens para reducir costes de FM manteniendo la efectividad (estimación y tracking de tokens, optimización de la ventana de contexto, controles de tamaño de respuesta, compresión de prompt, poda de contexto, limitación de respuesta).
- [**4.1.2**](./task-4-1-costes-y-eficiencia-de-recursos.md#skill-412--frameworks-de-selección-de-modelo-coste-efectiva) Frameworks de selección de modelo coste-efectivos (evaluación del tradeoff coste-capacidad, uso escalonado de FM según complejidad de la consulta, balance del coste de inferencia frente a la calidad, medición del ratio precio-rendimiento, patrones de inferencia eficientes).
- [**4.1.3**](./task-4-1-costes-y-eficiencia-de-recursos.md#skill-413--sistemas-de-alto-rendimiento-batching-capacidad-y-escalado) Sistemas de FM de alto rendimiento para maximizar utilización y throughput (estrategias de batching, planificación de capacidad, monitorización de utilización, configuraciones de auto-scaling, optimización de provisioned throughput).
- [**4.1.4**](./task-4-1-costes-y-eficiencia-de-recursos.md#skill-414--sistemas-de-caching-inteligente) Sistemas de caching inteligente para reducir costes y tiempos de respuesta evitando invocaciones innecesarias (caché semántica, result fingerprinting, edge caching, hashing determinista de peticiones, prompt caching).

### Task 4.2 — Optimizar el rendimiento de la aplicación

- [**4.2.1**](./task-4-2-latencia-y-throughput.md#skill-421--sistemas-de-ia-responsivos) Sistemas de IA responsivos para los tradeoffs latencia-coste (pre-computación de consultas predecibles, modelos de Bedrock optimizados para latencia, peticiones en paralelo, streaming de respuestas, benchmarking).
- [**4.2.2**](./task-4-2-retrieval-y-parametros.md#skill-422--rendimiento-del-retrieval) Rendimiento del retrieval para mejorar relevancia y velocidad de la información recuperada (optimización de índices, preprocesado de consultas, búsqueda híbrida con scoring personalizado).
- [**4.2.3**](./task-4-2-latencia-y-throughput.md#skill-423--optimización-de-throughput-del-fm) Optimización de throughput del FM (optimización del procesamiento de tokens, estrategias de batch inference, gestión de invocaciones concurrentes).
- [**4.2.4**](./task-4-2-retrieval-y-parametros.md#skill-424--rendimiento-del-fm-y-configuración-de-parámetros) Rendimiento del FM para casos de uso concretos (configuraciones de parámetros específicas del modelo, A/B testing, selección apropiada de temperatura y top-k/top-p según requisitos).
- [**4.2.5**](./task-4-2-latencia-y-throughput.md#skill-425--asignación-eficiente-de-recursos) Asignación eficiente de recursos para cargas de FM (planificación de capacidad para procesamiento de tokens, monitorización de utilización de patrones de prompt y completion, auto-scaling optimizado para tráfico GenAI).
- [**4.2.6**](./task-4-2-retrieval-y-parametros.md#skill-426--perfilado-y-comunicación-entre-servicios) Rendimiento del sistema de FM en workflows GenAI (perfilado de llamadas a la API, optimización de consultas a la base de datos vectorial, técnicas de reducción de latencia específicas de LLM, patrones eficientes de comunicación entre servicios).

### Task 4.3 — Implementar sistemas de monitorización para aplicaciones GenAI

- [**4.3.1**](./task-4-3-observabilidad-y-metricas.md#skill-431--observabilidad-holística) Observabilidad holística para visibilidad completa del rendimiento (métricas operativas, performance tracing, tracing de interacción con el FM, métricas de impacto de negocio con dashboards personalizados).
- [**4.3.2**](./task-4-3-observabilidad-y-metricas.md#skill-432--monitorización-proactiva-y-kpis-específicos-de-fm) Monitorización proactiva y KPIs de FM (CloudWatch para uso de tokens, efectividad del prompt, tasas de hallucination y calidad de respuesta; detección de anomalías de ráfagas de tokens y drift; Model Invocation Logs; benchmarks; detección de anomalías de coste).
- [**4.3.3**](./task-4-3-observabilidad-y-metricas.md#skill-433--observabilidad-integrada-y-accionable) Observabilidad integrada con insights accionables (dashboards de métricas operativas, visualizaciones de impacto de negocio, monitorización de compliance, trazabilidad forense y audit logging, tracking de interacción de usuario y de patrones de comportamiento del modelo).
- [**4.3.4**](./task-4-3-herramientas-vector-stores-y-fallos.md#skill-434--rendimiento-de-herramientas-y-coordinación-multi-agente) Frameworks de rendimiento de herramientas (tracking de patrones de llamada, recogida de métricas, observabilidad de tool calling y tracking de coordinación multi-agente, baselines de uso para detección de anomalías).
- [**4.3.5**](./task-4-3-herramientas-vector-stores-y-fallos.md#skill-435--gestión-operativa-del-vector-store) Gestión operativa del vector store (monitorización de rendimiento de bases de datos vectoriales, rutinas automatizadas de optimización de índices, procesos de validación de calidad de datos).
- [**4.3.6**](./task-4-3-herramientas-vector-stores-y-fallos.md#skill-436--troubleshooting-de-modos-de-fallo-propios-de-genai) Troubleshooting de modos de fallo propios de GenAI (golden datasets para detectar hallucinations, output diffing para consistencia de respuesta, reasoning path tracing para errores lógicos, pipelines de observabilidad especializados).

## El marco oficial que la guía no nombra

Los dos pilares del [Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/cost-optimization.html) que estructuran este dominio, y que de sus nueve preguntas **solo tenían `GENCOST04-BP01` citado** en los dominios anteriores:

```
Cost optimization                            Performance efficiency
GENCOST01  Model selection and cost          GENPERF01  Performance evaluation processes
GENCOST02  Generative AI pricing model       GENPERF02  Maintaining model performance
GENCOST03  Cost-aware prompting              GENPERF03  High-performance compute
GENCOST04  Cost-informed vector stores       GENPERF04  Vector store optimization
GENCOST05  Cost-informed agents
```

`GENCOST04` se desarrolla en [Task 1.4](../domain-1/task-1-4-vector-stores.md) y [Task 1.5](../domain-1/task-1-5-retrieval.md) de Domain 1. `GENPERF03` queda cubierto por la tabla de decisión de hosting de [Task 2.2](../domain-2/task-2-2-despliegue-de-modelos.md#la-tabla-de-decisión-completa). Las siete restantes se desarrollan aquí.

## Relación con los Domains 1, 2 y 3

El Domain 1 cubre **cómo integrar un FM y alimentarlo con datos**, el Domain 2 **cómo llevarlo a producción**, el Domain 3 **cómo impedir que haga daño**, y el Domain 4 **cómo hacer que salga a cuenta y se pueda operar**. Los temas se solapan mucho, y estos archivos enlazan en lugar de duplicar:

| Tema | Dónde está la base | Qué añade el Domain 4 |
| --- | --- | --- |
| Opciones de capacidad y Provisioned Throughput | [Task 2.2 · Skill 2.2.1](../domain-2/task-2-2-despliegue-de-modelos.md#las-seis-opciones-de-capacidad-de-amazon-bedrock) | GENCOST02-BP01: plazo corto primero, y la secuencia de compra de capacidad ([4.1.3](./task-4-1-costes-y-eficiencia-de-recursos.md#optimización-de-provisioned-throughput)) |
| Prompt caching | [Task 2.2 · Skill 2.2.3](../domain-2/task-2-2-despliegue-de-modelos.md#reducir-el-coste-sin-cambiar-de-modelo-prompt-caching) | La economía: cache-read no cuenta para la cuota TPM y cache-write sí ([4.1.1](./task-4-1-costes-y-eficiencia-de-recursos.md#las-métricas-de-token-y-lo-que-cada-una-cuenta-para-la-cuota), [4.1.4](./task-4-1-costes-y-eficiencia-de-recursos.md#prompt-caching-solo-la-economía)) |
| Latency-optimized inference | [Task 2.2 · Skill 2.2.3](../domain-2/task-2-2-despliegue-de-modelos.md#reducir-la-latencia-sin-cambiar-de-modelo-latency-optimized-inference) | `TimeToFirstToken` frente a `InvocationLatency` y el degradado silencioso a Standard ([4.2.1](./task-4-2-latencia-y-throughput.md#las-dos-latencias-que-no-miden-lo-mismo)) |
| Model cascading e intelligent prompt routing | [Task 2.2 · Skill 2.2.3](../domain-2/task-2-2-despliegue-de-modelos.md#skill-223--despliegue-optimizado-y-model-cascading) | GENCOST01-BP01 y la instrumentación de coste con Cost Explorer ([4.1.2](./task-4-1-costes-y-eficiencia-de-recursos.md#skill-412--frameworks-de-selección-de-modelo-coste-efectiva)) |
| `CountTokens` y límites de tokens | [Task 2.5 · Skill 2.5.1](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#gestión-de-límites-de-tokens) | Bajar `maxTokens` como palanca de **throughput**, no solo de coste ([4.2.3](./task-4-2-latencia-y-throughput.md#optimización-del-procesamiento-de-tokens)) |
| Streaming y reintentos | [Task 2.4 · Skill 2.4.2](../domain-2/task-2-4-integraciones-api-fm.md#skill-242--interacción-en-tiempo-real-y-streaming) | El streaming como palanca de latencia percibida de lo no cacheado ([4.2.1](./task-4-2-latencia-y-throughput.md#streaming-como-palanca-de-latencia-percibida)) |
| Tuning de índices vectoriales | [Task 1.4 · Skill 1.4.3](../domain-1/task-1-4-vector-stores.md#skill-143--arquitecturas-de-vector-database-de-alto-rendimiento) | Los cuatro algoritmos ANN de GENPERF04-BP01 y las OCUs de OpenSearch Serverless ([4.2.2](./task-4-2-retrieval-y-parametros.md#los-cuatro-algoritmos-ann-y-qué-optimiza-cada-uno), [4.3.5](./task-4-3-herramientas-vector-stores-y-fallos.md#monitorizar-el-vector-store-subyacente)) |
| Búsqueda híbrida y reranking | [Task 1.5 · Skill 1.5.4](../domain-1/task-1-5-retrieval.md#tipos-de-búsqueda-en-knowledge-bases) | La restricción de vector store que degrada a semántica en silencio, y el agentic retrieval ([4.2.2](./task-4-2-retrieval-y-parametros.md#búsqueda-híbrida-y-su-restricción-de-almacén)) |
| Parámetros de inferencia | [Task 1.5 · Skill 1.5.5](../domain-1/task-1-5-retrieval.md#parámetros-de-inferencia-en-la-generación) | El método de búsqueda de GENPERF02-BP02: extremos y luego bisección ([4.2.4](./task-4-2-retrieval-y-parametros.md#el-método-de-búsqueda-que-documenta-el-lens)) |
| Versiones y alias de prompts | [Task 1.6 · Skill 1.6.3](../domain-1/task-1-6-prompt-engineering-governance.md#bedrock-prompt-management) | Versión más alias como mecanismo real de A/B testing, con `requestMetadata` para atribuir ([4.2.4](./task-4-2-retrieval-y-parametros.md#ab-testing-de-verdad-versiones-y-alias)) |
| Los tres namespaces de métricas de Bedrock | [Task 3.3 · Skill 3.3.4](../domain-3/task-3-3-governance-y-compliance.md#los-tres-namespaces-de-métricas) | Un **cuarto namespace**, `AWS/Bedrock/KnowledgeBases`, y la capa de GenAI observability encima ([4.3.1](./task-4-3-observabilidad-y-metricas.md#cloudwatch-generative-ai-observability), [4.3.5](./task-4-3-herramientas-vector-stores-y-fallos.md#el-cuarto-namespace-de-bedrock)) |
| Anomaly detection sin umbral fijo | [Task 3.3 · Skill 3.3.4](../domain-3/task-3-3-governance-y-compliance.md#detección-de-drift-sin-umbral-fijo) | Sobre qué métrica aplicarla: tokens **por invocación**, no totales ([4.3.2](./task-4-3-observabilidad-y-metricas.md#detección-de-anomalías-para-ráfagas-de-tokens-y-drift-de-respuesta)) |
| Model invocation logging y Logs Insights | [Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#la-fuente-model-invocation-logging) | Es **prerrequisito** del dashboard de Model Invocations, no solo auditoría ([4.3.2](./task-4-3-observabilidad-y-metricas.md#model-invocation-logs-para-el-análisis-de-petición-y-respuesta)) |
| X-Ray y AgentCore Observability | [Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#agentcore-observability) | Application Signals con los 8 atributos `gen_ai.*`, y Transaction Search ([4.3.1](./task-4-3-observabilidad-y-metricas.md#los-ocho-atributos-genai-de-opentelemetry)) |
| Los siete tipos de trace de agente | [Task 3.4 · Skill 3.4.1](../domain-3/task-3-4-ia-responsable.md#los-siete-tipos-de-trace) | El `rationale` como reasoning path para diagnosticar errores lógicos ([4.3.6](./task-4-3-herramientas-vector-stores-y-fallos.md#reasoning-path-tracing-para-identificar-errores-lógicos)) |
| Tool use y su `toolConfig` | [Task 2.1 · Skill 2.1.6](../domain-2/task-2-1-agentic-ai-y-herramientas.md#los-tres-modos-de-tool-use-de-bedrock) | Las métricas propias de las built-in tools y el coste del catálogo en cada petición ([4.3.4](./task-4-3-herramientas-vector-stores-y-fallos.md#skill-434--rendimiento-de-herramientas-y-coordinación-multi-agente)) |
| Troubleshooting de aplicaciones de FM | [Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#skill-256--troubleshooting-de-aplicaciones-de-fm) | Los modos de fallo que no existen en ML clásico y el **golden dataset** ([4.3.6](./task-4-3-herramientas-vector-stores-y-fallos.md#el-golden-dataset-la-definición-oficial)) |
| Evaluación de recursos de Bedrock | [Task 3.4 · Skill 3.4.2](../domain-3/task-3-4-ia-responsable.md#las-métricas-de-rag-que-no-son-las-mismas) | `Faithfulness` frente a `Correctness` frente a `CitationCoverage` como diagnóstico ([4.3.6](./task-4-3-herramientas-vector-stores-y-fallos.md#detección-de-hallucinations-las-tres-capas)) |
| Contextual grounding check | [Task 3.1 · Skill 3.1.3](../domain-3/task-3-1-controles-de-seguridad-entrada-salida.md#skill-313--verificación-de-exactitud-y-reducción-de-hallucinations) | El **margen sobre el umbral** como señal que anticipa la degradación ([4.3.6](./task-4-3-herramientas-vector-stores-y-fallos.md#pipelines-de-observabilidad-especializados)) |

## Servicios en alcance más relevantes para este dominio

Del listado oficial de [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html), los que aparecen de forma directa en los skills del Domain 4. En **negrita**, los que entran por primera vez en estos materiales:

- **Management and Governance**: Amazon CloudWatch, Amazon CloudWatch Logs, **AWS Cost Explorer**, **AWS Cost Anomaly Detection**, **AWS Auto Scaling**, **Amazon Managed Grafana**, Amazon CloudWatch Synthetics, AWS CloudTrail, AWS Systems Manager, AWS Well-Architected Tool.
- **Machine Learning**: Amazon Bedrock, Amazon Bedrock AgentCore, Amazon Bedrock Knowledge Bases, Amazon Bedrock Prompt Management, Amazon SageMaker AI, **Amazon SageMaker Ground Truth**, Amazon SageMaker JumpStart, Amazon SageMaker Neo.
- **Database**: **Amazon ElastiCache**, Amazon Aurora, Amazon DynamoDB, Amazon Neptune.
- **Networking and Content Delivery**: Amazon API Gateway, **Amazon CloudFront**, AWS AppSync, Elastic Load Balancing.
- **Analytics**: Amazon OpenSearch Service, **Amazon Athena**, AWS Glue, Amazon Quick Sight.
- **Developer Tools**: AWS X-Ray, AWS Tools and SDKs, AWS CloudFormation, AWS CDK, AWS CLI.
- **Application Integration**: **Amazon EventBridge**, Amazon SQS, Amazon SNS, AWS Step Functions.
- **Compute**: AWS Lambda, AWS Lambda@Edge.
- **Storage**: Amazon S3, Amazon S3 Intelligent-Tiering, Amazon S3 Lifecycle policies.

## Conceptos transversales del examen

De [Technologies and concepts](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-technologies-concepts.html), los tres que se concentran casi por completo en este dominio: **cost optimization for AI workloads**, **performance tuning for AI applications** y **monitoring and observability for AI systems**. Aparecen además model evaluation and validation en el skill 4.3.6, y API design and integration patterns en el 4.2.6.

## Advertencia sobre lo que la guía nombra y la documentación no respalda

Este dominio tiene menos desajustes que el Domain 3, pero los que hay son de un tipo distinto: no son servicios retirados, son **capacidades que la guía presenta como si existieran de fábrica y que hay que construir**. Las seis que más afectan al estudio, cada una desarrollada como callout en su skill:

| Desajuste | Dónde | Cómo tratarlo |
| --- | --- | --- |
| Los skills **4.1.3** y **4.2.5** piden *auto-scaling configurations* para cargas de FM, pero **Amazon Bedrock no figura entre los recursos escalables de Application Auto Scaling** | [4.1.3](./task-4-1-costes-y-eficiencia-de-recursos.md#auto-scaling-dónde-existe-y-dónde-no) | En Bedrock se escala **comprando capacidad** y absorbiendo picos con colas y reintentos. El autoescalado por política aplica al endpoint de SageMaker AI, la caché, la tabla y la concurrencia de Lambda |
| La lista de In-Scope Services nombra **AWS Auto Scaling**, que es un servicio distinto de **Application Auto Scaling**, el que documenta las cuatro políticas | [4.1.3](./task-4-1-costes-y-eficiencia-de-recursos.md#auto-scaling-dónde-existe-y-dónde-no) | Conocer los cuatro tipos de política (target tracking, step, scheduled, predictive) y los recursos de SageMaker AI que soportan |
| El skill **4.3.2** presenta cuatro KPIs como si fueran métricas de CloudWatch, y **solo *token usage* existe**. Prompt effectiveness, hallucination rate y response quality hay que calcularlas | [4.3.2](./task-4-3-observabilidad-y-metricas.md#lo-que-la-plataforma-publica-y-lo-que-hay-que-construir) | CloudWatch es **el destino** de las cuatro, no la fuente. Las tres restantes salen de contextual grounding, evaluations y métricas propias con `PutMetricData` |
| El skill **4.1.2** pide medir el ratio precio-rendimiento, y **AWS Budgets no está en la lista de In-Scope Services** aunque es el servicio natural de control presupuestario | [4.1.2](./task-4-1-costes-y-eficiencia-de-recursos.md#la-instrumentación-de-coste-en-aws) | Las palancas en alcance son **Cost Explorer**, **Cost Anomaly Detection** y los cost allocation tags sobre application inference profiles |
| Las métricas de knowledge base gestionada son **best effort**: sin `cloudwatch:PutMetricData` no se publican **y la petición no falla** | [4.3.5](./task-4-3-herramientas-vector-stores-y-fallos.md#el-gotcha-de-permisos-que-rompe-la-observabilidad-en-silencio) | Conceder el permiso al **service role de la knowledge base y a toda identidad que llame** a sus operaciones. Ante ausencia total de métricas sin error, sospechar del permiso |
| Cuatro técnicas que el enunciado nombra **no tienen página propia** en el portal: pre-computación, result fingerprinting, hashing determinista de peticiones y output diffing | [4.1.4](./task-4-1-costes-y-eficiencia-de-recursos.md#hashing-determinista-y-result-fingerprinting), [4.2.1](./task-4-2-latencia-y-throughput.md#pre-computación-de-consultas-predecibles), [4.3.6](./task-4-3-herramientas-vector-stores-y-fallos.md#output-diffing-para-análisis-de-consistencia) | Se cubren por contraste con lo que sí está documentado: caché semántica, batch inference y comparison queries de Logs Insights |

Y una trampa de vocabulario que el enunciado del skill 4.1.4 introduce y conviene tener clara: pide *evitar invocaciones innecesarias del FM* y enumera **prompt caching** entre las técnicas, pero **el prompt caching no evita ninguna invocación**. Abarata los tokens de entrada de una invocación que sí ocurre. Las capas que evitan la llamada son el hashing determinista, la caché semántica, la caché de API Gateway y CloudFront.

## Verificar estos materiales

El repositorio incluye un verificador que comprueba que toda URL oficial citada sigue viva, que los enlaces relativos y sus anclas resuelven, que no hay bloques de código de shell y que cada task documenta los skills que declara:

```python
# uv run python scripts/verify_study_docs.py study/domain-4
# uv run python scripts/verify_study_docs.py study/domain-4 --no-network
# uv run python scripts/verify_study_docs.py study
```

Las páginas oficiales de este dominio se consultaron con el MCP de documentación de AWS, accesible también desde la línea de comandos:

```python
# uv run python scripts/mcp_aws_docs.py search "Bedrock batch inference quotas"
# uv run python scripts/mcp_aws_docs.py read https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html
# uv run python scripts/mcp_aws_docs.py sections <url> "Implementation guidance"
```
