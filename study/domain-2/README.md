# Domain 2 — Implementation and Integration

Cobertura completa del **Domain 2** del examen **AWS Certified Generative AI Developer – Professional (AIP-C01)**, construida a partir de documentación oficial de AWS (`docs.aws.amazon.com`).

> El contenido de las fuentes AWS fue parafraseado y resumido para cumplir con restricciones de licencia. Cada sección enlaza a la página oficial correspondiente.

## Datos del dominio

| Dato | Valor |
| --- | --- |
| Peso en el examen | **26 % del contenido puntuado** (segundo dominio por peso, tras el 31 % del Domain 1) |
| Tasks | 5 |
| Skills | 25 |
| Preguntas puntuadas | 65 (más 10 no puntuadas, no identificadas) |
| Score de aprobación | 750 en escala 100–1000 |
| Modelo de scoring | Compensatorio: no hace falta aprobar cada sección, solo el examen global |

Fuentes: [Exam Guide AIP-C01](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) · [Content Domain 2](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain2.html)

## Índice de archivos

| Archivo | Task | Skills | Tema |
| --- | --- | --- | --- |
| [task-2-1-agentic-ai-y-herramientas.md](./task-2-1-agentic-ai-y-herramientas.md) | 2.1 | 2.1.1 – 2.1.7 | Soluciones agentic AI e integración de herramientas |
| [task-2-2-despliegue-de-modelos.md](./task-2-2-despliegue-de-modelos.md) | 2.2 | 2.2.1 – 2.2.3 | Estrategias de despliegue de modelos |
| [task-2-3-integracion-empresarial.md](./task-2-3-integracion-empresarial.md) | 2.3 | 2.3.1 – 2.3.5 | Arquitecturas de integración empresarial |
| [task-2-4-integraciones-api-fm.md](./task-2-4-integraciones-api-fm.md) | 2.4 | 2.4.1 – 2.4.4 | Integraciones de API de FM |
| [task-2-5-patrones-de-aplicacion-y-tooling.md](./task-2-5-patrones-de-aplicacion-y-tooling.md) | 2.5 | 2.5.1 – 2.5.6 | Patrones de integración de aplicaciones y herramientas de desarrollo |
| [referencias-oficiales.md](./referencias-oficiales.md) | — | — | Todas las páginas de AWS usadas, agrupadas por servicio, más discrepancias detectadas |

## Mapa de las 25 skills

### Task 2.1 — Implementar soluciones agentic AI e integraciones de herramientas
- **2.1.1** Sistemas autónomos inteligentes con capacidades apropiadas de memoria y gestión de estado (Strands Agents y AWS Agent Squad para sistemas multi-agente, MCP para interacciones agente-herramienta).
- **2.1.2** Sistemas avanzados de resolución de problemas para que los FMs descompongan y resuelvan problemas complejos siguiendo pasos de razonamiento estructurado (Step Functions para patrones ReAct y chain-of-thought).
- **2.1.3** Workflows de IA con salvaguardas para asegurar comportamiento controlado del FM (Step Functions para stopping conditions, Lambda para mecanismos de timeout, políticas IAM para imponer fronteras de recursos, circuit breakers para mitigar fallos).
- **2.1.4** Sistemas sofisticados de coordinación de modelos para optimizar el rendimiento entre múltiples capacidades (FMs especializados, lógica de agregación personalizada para ensembles, frameworks de selección de modelo).
- **2.1.5** Sistemas de IA colaborativos que enriquecen las capacidades del FM con expertise humana (Step Functions para orquestar procesos de revisión y aprobación, API Gateway para mecanismos de recogida de feedback, patrones de human augmentation).
- **2.1.6** Integraciones inteligentes de herramientas para extender las capacidades del FM y asegurar operaciones fiables (Strands API para comportamientos personalizados, definiciones de función estandarizadas, Lambda para manejo de errores y validación de parámetros).
- **2.1.7** Frameworks de extensión del modelo (Lambda para servidores MCP stateless de acceso ligero a herramientas, Amazon ECS para servidores MCP con herramientas complejas, librerías cliente MCP para patrones de acceso consistentes).

### Task 2.2 — Implementar estrategias de despliegue de modelos
- **2.2.1** Desplegar FMs según necesidades de la aplicación y requisitos de rendimiento (Lambda para invocación on-demand, configuraciones de Provisioned Throughput de Bedrock, endpoints de SageMaker AI para soluciones híbridas).
- **2.2.2** Desplegar soluciones de FM abordando los retos propios de los LLMs frente a despliegues ML tradicionales (patrones de despliegue basados en contenedor optimizados para memoria, utilización de GPU y capacidad de procesamiento de tokens; estrategias especializadas de carga de modelo).
- **2.2.3** Enfoques de despliegue optimizados que balancean rendimiento y requisitos de recursos (selección de modelos apropiados, modelos pre-entrenados menores para tareas específicas, model cascading basado en API para consultas rutinarias).

### Task 2.3 — Diseñar e implementar arquitecturas de integración empresarial
- **2.3.1** Soluciones de conectividad empresarial para incorporar capacidades de FM en entornos existentes (integraciones basadas en API con sistemas legacy, arquitecturas event-driven para acoplamiento débil, patrones de sincronización de datos).
- **2.3.2** Capacidades de IA integradas para enriquecer aplicaciones existentes con funcionalidad GenAI (API Gateway para integraciones de microservicios, Lambda para webhook handlers, EventBridge para integraciones event-driven).
- **2.3.3** Frameworks de acceso seguro para asegurar controles de seguridad apropiados (federación de identidad entre servicios de FM y sistemas empresariales, control de acceso basado en rol para modelo y datos, acceso de least privilege a las APIs de FM).
- **2.3.4** Soluciones cross-environment para asegurar compliance de datos entre jurisdicciones habilitando el acceso a FMs (AWS Outposts para integración de datos on-premises, AWS Wavelength para despliegues de borde, routing seguro entre cloud y on-premises).
- **2.3.5** Pipelines CI/CD y arquitecturas de GenAI gateway para patrones de consumo seguros y conformes (CodePipeline, CodeBuild, frameworks de testing automatizado con security scans y soporte de rollback, capas de abstracción centralizadas, mecanismos de observabilidad y control).

### Task 2.4 — Implementar integraciones de API de FM
- **2.4.1** Sistemas flexibles de interacción con el modelo (APIs de Bedrock para peticiones sincrónicas desde distintos entornos de computación, SDKs de AWS por lenguaje y Amazon SQS para procesamiento asíncrono, API Gateway para clientes de API personalizados con validación de peticiones).
- **2.4.2** Sistemas de interacción en tiempo real para dar feedback inmediato del FM (APIs de streaming de Bedrock para entrega incremental de respuesta, WebSockets o server-sent events para generar texto en tiempo real, API Gateway para chunked transfer encoding).
- **2.4.3** Sistemas de FM resilientes para operaciones fiables (SDK de AWS para exponential backoff, API Gateway para gestionar rate limiting, mecanismos de fallback para degradación elegante, AWS X-Ray para observabilidad entre fronteras de servicio).
- **2.4.4** Sistemas inteligentes de routing de modelos para optimizar la selección (código de aplicación para configuraciones de routing estático, Step Functions para routing dinámico basado en contenido hacia FMs especializados, routing inteligente basado en métricas, API Gateway con transformaciones de petición para la lógica de routing).

### Task 2.5 — Implementar patrones de integración de aplicaciones y herramientas de desarrollo
- **2.5.1** Interfaces de API de FM que atienden los requisitos específicos de las cargas GenAI (API Gateway para manejar respuestas en streaming, gestión de límites de tokens, estrategias de reintento ante timeouts del modelo).
- **2.5.2** Interfaces de IA accesibles para acelerar la adopción e integración de FMs (AWS Amplify para componentes de UI declarativos, especificaciones OpenAPI para enfoques API-first, Bedrock Prompt Flows como constructor de workflows no-code).
- **2.5.3** Mejoras de sistemas de negocio (Lambda para mejoras de CRM, Step Functions para orquestar sistemas de procesamiento de documentos, Bedrock Data Automation para workflows automatizados de procesamiento de datos).
- **2.5.4** Productividad del desarrollador para acelerar los workflows de desarrollo de aplicaciones GenAI (Amazon Q Developer para generar y refactorizar código, sugerencias de código para asistencia de API, testing de componentes de IA, optimización de rendimiento).
- **2.5.5** Aplicaciones GenAI avanzadas con capacidades sofisticadas (Strands Agents y AWS Agent Squad para orquestación nativa de AWS, Step Functions para orquestar patrones de diseño de agente, Bedrock para patrones de prompt chaining).
- **2.5.6** Mejorar la eficiencia del troubleshooting de aplicaciones de FM (CloudWatch Logs Insights para analizar prompts y respuestas, X-Ray para trazar llamadas a la API de FM, Amazon Q Developer para reconocimiento de patrones de error específicos de GenAI).

## Relación con el Domain 1

El Domain 1 cubre **cómo integrar un FM y alimentarlo con datos**; el Domain 2 cubre **cómo llevar eso a producción dentro de una empresa**. Los temas se solapan en varios puntos, y estos archivos enlazan al Domain 1 en lugar de duplicar:

| Tema | Dónde está la base | Qué añade el Domain 2 |
| --- | --- | --- |
| Selección dinámica de modelo con AppConfig | [Task 1.2 · Skill 1.2.2](../domain-1/task-1-2-seleccion-y-configuracion-fm.md) | Routing por contenido y por métricas (2.4.4) |
| Circuit breaker y cross-Region inference | [Task 1.2 · Skill 1.2.3](../domain-1/task-1-2-seleccion-y-configuracion-fm.md) | Circuit breaker como salvaguarda de agente (2.1.3) y residencia de datos (2.3.4) |
| Provisioned Throughput e inference profiles | [Task 1.2 · Skill 1.2.1](../domain-1/task-1-2-seleccion-y-configuracion-fm.md) | Tabla de decisión de despliegue completa (2.2.1) |
| Modelos personalizados, LoRA y adapters | [Task 1.2 · Skill 1.2.4](../domain-1/task-1-2-seleccion-y-configuracion-fm.md) | Retos de hosting de LLM: GPU, memoria, carga de modelo (2.2.2) |
| Formato de entrada y `Converse` | [Task 1.3 · Skill 1.3.3](../domain-1/task-1-3-datos-para-consumo-fm.md) | Streaming, asíncrono y resiliencia sobre la misma API (2.4.x) |
| Retrieval, tool use y clientes MCP | [Task 1.5 · Skill 1.5.6](../domain-1/task-1-5-retrieval.md) | Servidores MCP propios y frameworks de extensión (2.1.6, 2.1.7) |
| Histórico de conversación y contexto | [Task 1.6 · Skill 1.6.2](../domain-1/task-1-6-prompt-engineering-governance.md) | Memoria de agente gestionada y estado multi-agente (2.1.1) |
| Prompt Flows y cadenas de prompts | [Task 1.6 · Skill 1.6.6](../domain-1/task-1-6-prompt-engineering-governance.md) | Flows como builder no-code y patrones de agente (2.5.2, 2.5.5) |
| Observabilidad de invocaciones | [Task 1.6 · Skill 1.6.3](../domain-1/task-1-6-prompt-engineering-governance.md) | Troubleshooting con Logs Insights y X-Ray (2.5.6) |

## Relación con el Domain 3

El [Domain 3 — AI Safety, Security, and Governance](../domain-3/README.md) (20 %) toma varios temas de este dominio y los lleva al terreno de la seguridad, la privacidad y la auditoría. Estos archivos son la base; el Domain 3 profundiza:

| Tema | Base en el Domain 2 | Qué añade el Domain 3 |
| --- | --- | --- |
| Guardrails como salvaguarda de agente | [Task 2.1 · Skill 2.1.3](./task-2-1-agentic-ai-y-herramientas.md#skill-213--workflows-con-salvaguardas-y-comportamiento-controlado) | Las seis políticas con sus cuotas y tiers, prompt injection, jailbreak y prompt leakage ([3.1.1](../domain-3/task-3-1-controles-de-seguridad-entrada-salida.md#skill-311--seguridad-de-contenido-en-las-entradas), [3.1.5](../domain-3/task-3-1-controles-de-seguridad-entrada-salida.md#skill-315--detección-avanzada-de-amenazas-adversariales)) |
| Federación de identidad y least privilege | [Task 2.3 · Skill 2.3.3](./task-2-3-integracion-empresarial.md#skill-233--frameworks-de-acceso-seguro) | Acceso granular a datos con Lake Formation y endpoint policies ([3.2.1](../domain-3/task-3-2-seguridad-y-privacidad-de-datos.md#skill-321--entornos-de-ia-protegidos)) |
| PrivateLink y residencia de datos | [Task 2.3 · Skill 2.3.4](./task-2-3-integracion-empresarial.md#skill-234--soluciones-cross-environment-y-compliance-entre-jurisdicciones) | Los siete service names de VPC endpoint de Bedrock, endpoints FIPS y modos de retención de datos ([3.2.1](../domain-3/task-3-2-seguridad-y-privacidad-de-datos.md#skill-321--entornos-de-ia-protegidos), [3.2.2](../domain-3/task-3-2-seguridad-y-privacidad-de-datos.md#skill-322--sistemas-que-preservan-la-privacidad)) |
| Human-in-the-loop y revisión humana | [Task 2.1 · Skill 2.1.5](./task-2-1-agentic-ai-y-herramientas.md#skill-215--sistemas-colaborativos-con-expertise-humana) | Evaluaciones con human workers como una de las cuatro familias de evaluación ([3.4.2](../domain-3/task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness)) |
| Evaluación de recursos de Bedrock en el pipeline | [Task 2.3 · Skill 2.3.5](./task-2-3-integracion-empresarial.md#skill-235--cicd-y-arquitecturas-de-genai-gateway) | Las once métricas `Builtin.*` de judge model y las de RAG, con las palancas de fairness ([3.4.2](../domain-3/task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness)) |
| Observabilidad y troubleshooting de FM | [Task 2.5 · Skill 2.5.6](./task-2-5-patrones-de-aplicacion-y-tooling.md#skill-256--troubleshooting-de-aplicaciones-de-fm) | Los tres namespaces de métricas, CloudTrail por tipo de recurso y detección de drift ([3.3.2](../domain-3/task-3-3-governance-y-compliance.md#skill-332--trazabilidad-y-tracking-de-fuentes-de-datos), [3.3.4](../domain-3/task-3-3-governance-y-compliance.md#skill-334--monitorización-continua-y-controles-avanzados)) |
| Agentic AI Lens y trace de agentes | [Task 2.1](./task-2-1-agentic-ai-y-herramientas.md) | Los siete tipos de trace y el `callerChain` como cadena de custodia ([3.4.1](../domain-3/task-3-4-ia-responsable.md#skill-341--transparencia-y-reasoning-traces)) |

## Relación con el Domain 4

El [Domain 4 — Operational Efficiency and Optimization for GenAI Applications](../domain-4/README.md) (12 %) toma las decisiones de despliegue e integración de este dominio y las convierte en preguntas de **coste, latencia y operación**. Este dominio explica cómo montarlo; el Domain 4, cómo hacer que salga a cuenta y se pueda medir:

| Tema | Base en el Domain 2 | Qué añade el Domain 4 |
| --- | --- | --- |
| Opciones de capacidad y Provisioned Throughput | [Task 2.2 · Skill 2.2.1](./task-2-2-despliegue-de-modelos.md#las-seis-opciones-de-capacidad-de-amazon-bedrock) | GENCOST02-BP01 y la secuencia de compra de capacidad, más batch inference al completo con `CreateModelInvocationJob` ([4.1.3](../domain-4/task-4-1-costes-y-eficiencia-de-recursos.md#skill-413--sistemas-de-alto-rendimiento-batching-capacidad-y-escalado)) |
| Prompt caching | [Task 2.2 · Skill 2.2.3](./task-2-2-despliegue-de-modelos.md#reducir-el-coste-sin-cambiar-de-modelo-prompt-caching) | La economía de la caché y las capas que sí evitan la invocación, con los umbrales de similitud de la caché semántica ([4.1.4](../domain-4/task-4-1-costes-y-eficiencia-de-recursos.md#skill-414--sistemas-de-caching-inteligente)) |
| Latency-optimized inference y model cascading | [Task 2.2 · Skill 2.2.3](./task-2-2-despliegue-de-modelos.md#skill-223--despliegue-optimizado-y-model-cascading) | `TimeToFirstToken` frente a `InvocationLatency` y la taxonomía de cuellos de botella de GENPERF02-BP01 ([4.2.1](../domain-4/task-4-2-latencia-y-throughput.md#skill-421--sistemas-de-ia-responsivos)) |
| `CountTokens` y límites de tokens | [Task 2.5 · Skill 2.5.1](./task-2-5-patrones-de-aplicacion-y-tooling.md#gestión-de-límites-de-tokens) | Bajar `maxTokens` como palanca de throughput, porque el throttling reserva entrada más `maxTokens` ([4.2.3](../domain-4/task-4-2-latencia-y-throughput.md#skill-423--optimización-de-throughput-del-fm)) |
| Endpoints de SageMaker AI | [Task 2.2 · Skill 2.2.1](./task-2-2-despliegue-de-modelos.md#las-opciones-de-inferencia-de-sagemaker-ai) | Políticas de escalado, cooldown y las enhanced metrics por instancia, contenedor y GPU ([4.2.5](../domain-4/task-4-2-latencia-y-throughput.md#skill-425--asignación-eficiente-de-recursos)) |
| Streaming y reintentos del SDK | [Task 2.4 · Skill 2.4.2](./task-2-4-integraciones-api-fm.md#skill-242--interacción-en-tiempo-real-y-streaming) | El orden de las seis técnicas de reducción de latencia específicas de LLM ([4.2.6](../domain-4/task-4-2-retrieval-y-parametros.md#skill-426--perfilado-y-comunicación-entre-servicios)) |
| Model invocation logging y Logs Insights | [Task 2.5 · Skill 2.5.6](./task-2-5-patrones-de-aplicacion-y-tooling.md#la-fuente-model-invocation-logging) | Es prerrequisito del dashboard de Model Invocations, no solo auditoría ([4.3.2](../domain-4/task-4-3-observabilidad-y-metricas.md#skill-432--monitorización-proactiva-y-kpis-específicos-de-fm)) |
| X-Ray y AgentCore Observability | [Task 2.5 · Skill 2.5.6](./task-2-5-patrones-de-aplicacion-y-tooling.md#agentcore-observability) | CloudWatch generative AI observability, Application Signals con los ocho atributos `gen_ai.*` y Transaction Search ([4.3.1](../domain-4/task-4-3-observabilidad-y-metricas.md#skill-431--observabilidad-holística)) |
| Tool use y su `toolConfig` | [Task 2.1 · Skill 2.1.6](./task-2-1-agentic-ai-y-herramientas.md#los-tres-modos-de-tool-use-de-bedrock) | Las métricas propias de las built-in tools y el coste del catálogo en cada petición ([4.3.4](../domain-4/task-4-3-herramientas-vector-stores-y-fallos.md#skill-434--rendimiento-de-herramientas-y-coordinación-multi-agente)) |
| Troubleshooting de aplicaciones de FM | [Task 2.5 · Skill 2.5.6](./task-2-5-patrones-de-aplicacion-y-tooling.md#skill-256--troubleshooting-de-aplicaciones-de-fm) | Los modos de fallo que no existen en ML clásico y el **golden dataset** ([4.3.6](../domain-4/task-4-3-herramientas-vector-stores-y-fallos.md#skill-436--troubleshooting-de-modos-de-fallo-propios-de-genai)) |

## Servicios en alcance más relevantes para este dominio

Del listado oficial de [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html), los que aparecen de forma directa en los skills del Domain 2:

- **Machine Learning**: Amazon Bedrock, Bedrock AgentCore, Bedrock Prompt Flows, Bedrock Prompt Management, Bedrock Knowledge Bases, Amazon Augmented AI, Amazon Q Developer, Amazon Q Business, Amazon Lex, SageMaker AI, SageMaker JumpStart, SageMaker Neo, SageMaker Model Registry.
- **Application Integration**: Step Functions, EventBridge, SQS, SNS, AppConfig, AppFlow.
- **Compute**: Lambda, Lambda@Edge, EC2, App Runner, **AWS Outposts**, **AWS Wavelength**.
- **Containers**: ECS, EKS, ECR, Fargate.
- **Developer Tools**: AWS Amplify, AWS CDK, AWS CloudFormation, CodeArtifact, CodeBuild, CodeDeploy, CodePipeline, **Kiro**, AWS Tools and SDKs, **AWS X-Ray**.
- **Networking and Content Delivery**: API Gateway, AppSync, CloudFront, ELB, Global Accelerator, PrivateLink, Route 53, VPC.
- **Security, Identity, and Compliance**: IAM, IAM Identity Center, IAM Access Analyzer, Cognito, KMS, Secrets Manager, AWS WAF, AWS Encryption SDK.
- **Management and Governance**: CloudWatch, CloudWatch Logs, CloudWatch Synthetics, CloudTrail, Managed Grafana, Service Catalog, Systems Manager, AWS Well-Architected Tool, Auto Scaling.
- **Customer Engagement**: Amazon Connect.
- **Database / Storage**: DynamoDB, DynamoDB Streams, ElastiCache, Amazon S3, EFS, EBS.

## Conceptos transversales del examen

De [Technologies and concepts](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-technologies-concepts.html), los que se concentran en Domain 2: **agentic AI systems**, FM integration, API design and integration patterns, event-driven architectures, serverless computing, container orchestration, infrastructure as code (IaC), CI/CD for AI applications, hybrid cloud architectures, enterprise system integration, monitoring and observability for AI systems, y performance tuning for AI applications.

## Advertencia sobre frameworks nombrados sin documentación en el portal de AWS

Tres skills de este dominio (**2.1.1**, **2.1.6**, **2.5.5**) nombran **Strands Agents** y **AWS Agent Squad**, que no tienen guía de servicio en `docs.aws.amazon.com`. Estos archivos cubren esos skills con lo que AWS sí documenta en su portal (Bedrock AgentCore como sustrato de ejecución, el Agentic AI Lens como marco de diseño, Step Functions como orquestador) y registran el hueco en [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación), junto a otras dos discrepancias detectadas: la documentación de LMI containers delegada fuera del portal, y el fin de soporte anunciado de los plugins de IDE de Amazon Q Developer frente a la presencia de Kiro en la lista de servicios en alcance.
