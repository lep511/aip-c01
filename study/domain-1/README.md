# Domain 1 — Foundation Model Integration, Data Management, and Compliance

Cobertura completa del **Domain 1** del examen **AWS Certified Generative AI Developer – Professional (AIP-C01)**, construida a partir de documentación oficial de AWS (`docs.aws.amazon.com`).

> El contenido de las fuentes AWS fue parafraseado y resumido para cumplir con restricciones de licencia. Cada sección enlaza a la página oficial correspondiente.

## Datos del dominio

| Dato | Valor |
| --- | --- |
| Peso en el examen | **31 % del contenido puntuado** (el dominio con mayor peso) |
| Tasks | 6 |
| Skills | 28 |
| Preguntas puntuadas | 65 (más 10 no puntuadas, no identificadas) |
| Score de aprobación | 750 en escala 100–1000 |
| Modelo de scoring | Compensatorio: no hace falta aprobar cada sección, solo el examen global |

Fuentes: [Exam Guide AIP-C01](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) · [Content Domain 1](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain1.html)

## Índice de archivos

| Archivo | Task | Skills | Tema |
| --- | --- | --- | --- |
| [task-1-1-analisis-y-diseno.md](./task-1-1-analisis-y-diseno.md) | 1.1 | 1.1.1 – 1.1.3 | Analizar requisitos y diseñar soluciones GenAI |
| [task-1-2-seleccion-y-configuracion-fm.md](./task-1-2-seleccion-y-configuracion-fm.md) | 1.2 | 1.2.1 – 1.2.4 | Seleccionar y configurar FMs |
| [task-1-3-datos-para-consumo-fm.md](./task-1-3-datos-para-consumo-fm.md) | 1.3 | 1.3.1 – 1.3.4 | Validación y procesamiento de datos para consumo por FMs |
| [task-1-4-vector-stores.md](./task-1-4-vector-stores.md) | 1.4 | 1.4.1 – 1.4.5 | Diseñar e implementar soluciones de vector store |
| [task-1-5-retrieval.md](./task-1-5-retrieval.md) | 1.5 | 1.5.1 – 1.5.6 | Mecanismos de retrieval para augmentación de FMs |
| [task-1-6-prompt-engineering-governance.md](./task-1-6-prompt-engineering-governance.md) | 1.6 | 1.6.1 – 1.6.6 | Prompt engineering y governance de interacciones con FMs |
| [referencias-oficiales.md](./referencias-oficiales.md) | — | — | Todas las páginas de AWS usadas, agrupadas por servicio |

## Mapa de las 28 skills

### Task 1.1 — Analizar requisitos y diseñar soluciones GenAI
- **1.1.1** Diseños arquitectónicos alineados a necesidades de negocio y restricciones técnicas: FMs apropiados, patrones de integración, estrategias de despliegue.
- **1.1.2** PoC técnicas para validar viabilidad, características de rendimiento y valor de negocio antes de escalar (Amazon Bedrock).
- **1.1.3** Componentes técnicos estandarizados para implementación consistente (AWS Well-Architected Framework, WA Tool Generative AI Lens).

### Task 1.2 — Seleccionar y configurar FMs
- **1.2.1** Evaluar y elegir FMs: benchmarks de rendimiento, análisis de capacidades, evaluación de limitaciones.
- **1.2.2** Arquitecturas flexibles para selección dinámica de modelo y cambio de proveedor sin modificar código (Lambda, API Gateway, AppConfig).
- **1.2.3** Sistemas resilientes ante interrupciones: circuit breaker con Step Functions, Bedrock Cross-Region Inference, despliegue multi-Región, degradación elegante.
- **1.2.4** Despliegue y ciclo de vida de FMs personalizados: SageMaker AI, LoRA y adapters, Model Registry, pipelines automatizados, rollback, retiro de modelos.

### Task 1.3 — Pipelines de validación y procesamiento de datos
- **1.3.1** Validación de calidad de datos: AWS Glue Data Quality, SageMaker Data Wrangler, Lambda, métricas de CloudWatch.
- **1.3.2** Procesamiento de tipos complejos (texto, imagen, audio, tabular): modelos multimodales de Bedrock, SageMaker Processing, Amazon Transcribe, pipelines multimodales avanzados.
- **1.3.3** Formateo de entrada según requisitos del modelo: JSON para la API de Bedrock, datos estructurados para endpoints de SageMaker AI, formato conversacional.
- **1.3.4** Mejorar la calidad de la entrada: Bedrock para reformatear texto, Comprehend para extraer entidades, Lambda para normalizar.

### Task 1.4 — Diseñar e implementar soluciones de vector store
- **1.4.1** Arquitecturas avanzadas de vector database: Bedrock Knowledge Bases, OpenSearch Service con Neural plugin, RDS con repositorios S3, DynamoDB con vector databases.
- **1.4.2** Frameworks de metadatos: metadatos de objeto S3, atributos personalizados, sistemas de tagging.
- **1.4.3** Alto rendimiento a escala: sharding en OpenSearch, multi-índice, indexación jerárquica.
- **1.4.4** Integración con recursos corporativos: document management, knowledge bases, wikis internos.
- **1.4.5** Mantenimiento de datos: actualizaciones incrementales, detección de cambios en tiempo real, sincronización automatizada, refresh programado.

### Task 1.5 — Diseñar mecanismos de retrieval
- **1.5.1** Segmentación de documentos: chunking de Bedrock, fixed-size con Lambda, chunking jerárquico personalizado.
- **1.5.2** Embeddings: Amazon Titan según dimensionalidad y dominio, evaluación de modelos de embedding de Bedrock, generación por lotes con Lambda.
- **1.5.3** Vector search: OpenSearch Service, Aurora con pgvector, Bedrock Knowledge Bases con vector store gestionado.
- **1.5.4** Búsqueda avanzada: semántica en OpenSearch, híbrida keywords + vectores, modelos reranker de Bedrock.
- **1.5.5** Manejo de consultas: expansión con Bedrock, descomposición con Lambda, transformación con Step Functions.
- **1.5.6** Acceso consistente: function calling para vector search, clientes MCP, patrones de API estandarizados.

### Task 1.6 — Prompt engineering y governance
- **1.6.1** Frameworks de instrucción: Bedrock Prompt Management para roles, Bedrock Guardrails para IA responsable, plantillas de formato.
- **1.6.2** Sistemas interactivos con contexto: Step Functions para clarificación, Comprehend para intención, DynamoDB para histórico.
- **1.6.3** Gestión y governance de prompts: Prompt Management con plantillas parametrizadas y aprobaciones, S3 como repositorio, CloudTrail para uso, CloudWatch Logs para acceso.
- **1.6.4** Calidad de prompts: Lambda para verificar salida esperada, Step Functions para casos límite, CloudWatch para regresión.
- **1.6.5** Refinamiento iterativo: componentes de entrada estructurados, especificación de formato de salida, chain-of-thought, feedback loops.
- **1.6.6** Prompts complejos: Bedrock Prompt Flows para cadenas secuenciales, ramificación condicional, componentes reutilizables, pre/post-procesamiento integrado.

## Sobre la palabra "Compliance" del título

El título oficial del dominio incluye *Compliance*, pero la guía no publica skills dedicados a ello. El requisito aparece **embebido** en otros skills:

| Aspecto de compliance | Dónde se cubre |
| --- | --- |
| Residencia de datos y fronteras geográficas | Task 1.2 → Cross-Region Inference geográfica vs global, SCPs |
| Auditoría de invocaciones y uso de prompts | Task 1.6 → CloudTrail, CloudWatch Logs, model invocation logging |
| Cifrado de datos y recursos de knowledge base | Task 1.4 → KMS, SSE-S3 / SSE-KMS, Secrets Manager |
| IA responsable y seguridad de contenido | Task 1.6 → Bedrock Guardrails, contextual grounding |
| Trazabilidad y versionado de artefactos | Task 1.2 → SageMaker Model Registry; Task 1.6 → versiones y alias |

El [Domain 3 — AI Safety, Security, and Governance](../domain-3/README.md) (20 %) profundiza en estos temas: las seis políticas de Bedrock Guardrails al detalle, el ciclo completo de PII, la trazabilidad con CloudTrail y data lineage, y los principios de IA responsable.

## Servicios en alcance más relevantes para este dominio

Del listado oficial de [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html), los que aparecen de forma directa en los skills del Domain 1:

- **Machine Learning**: Amazon Bedrock, Bedrock AgentCore, Bedrock Knowledge Bases, Bedrock Prompt Management, Bedrock Prompt Flows, Comprehend, Kendra, Titan, Transcribe, Textract, SageMaker AI, SageMaker Data Wrangler, SageMaker Model Registry, SageMaker Processing, SageMaker JumpStart, SageMaker Clarify, SageMaker Model Monitor, Augmented AI.
- **Analytics**: OpenSearch Service, AWS Glue, Athena, EMR, Kinesis, MSK.
- **Database**: Aurora, RDS, DynamoDB, DynamoDB Streams, Neptune, DocumentDB, ElastiCache.
- **Storage**: Amazon S3 (incluye S3 Vectors, Lifecycle policies, Intelligent-Tiering, Cross-Region Replication).
- **Application Integration**: Step Functions, EventBridge, AppConfig, SNS, SQS, AppFlow.
- **Compute / Networking**: Lambda, API Gateway, AppSync, PrivateLink.
- **Management & Governance**: CloudWatch, CloudWatch Logs, CloudTrail, AWS Well-Architected Tool, Systems Manager.
- **Security**: IAM, KMS, Secrets Manager, Macie, Cognito.
- **Migration & Transfer**: DataSync, Transfer Family.

## Conceptos transversales del examen

De [Technologies and concepts](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-technologies-concepts.html), los que se concentran en Domain 1: RAG, vector databases y embeddings, prompt engineering y management, integración de FMs, evaluación y validación de modelos, patrones de diseño e integración de APIs, arquitecturas event-driven, serverless, IaC y CI/CD para aplicaciones de IA.
