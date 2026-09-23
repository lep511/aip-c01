# Referencias oficiales de AWS — Domain 4

[← Volver al índice](./README.md)

Todas las páginas de `docs.aws.amazon.com` consultadas para construir la cobertura del Domain 4, agrupadas por servicio. El contenido de estas fuentes fue parafraseado y resumido en los archivos de este directorio para cumplir con restricciones de licencia.

**Total: 123 páginas oficiales.** La columna *Usado en* indica los skills que se apoyan en cada página. Todas se verifican automáticamente con `scripts/verify_study_docs.py`.

---

## Guía del examen AIP-C01

| Página | Usado en |
| --- | --- |
| [AWS Certified Generative AI Developer - Professional (AIP-C01)](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) | README |
| [Content Domain 4: Operational Efficiency and Optimization for GenAI Applications](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain4.html) | README, los 16 skills |
| [Technologies and concepts that might appear on the exam](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-technologies-concepts.html) | README |
| [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html) | README, 4.1.3 |

---

## AWS Well-Architected — Generative AI Lens

Es la fuente estructural del Task 4.1 y del Task 4.2. De las nueve preguntas de los pilares de Cost optimization y Performance efficiency, **solo `GENCOST04-BP01` estaba citado en los dominios anteriores**.

### Pilar de Cost optimization

| Página | Usado en |
| --- | --- |
| [Cost optimization](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/cost-optimization.html) | Marco del Task 4.1 |
| [GENCOST01 Model selection and cost optimization](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost01.html) | 4.1.2 |
| [GENCOST01-BP01 Right-size model selection to optimize inference costs](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost01-bp01.html) | 4.1.2 |
| [GENCOST02 Generative AI pricing model](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost02.html) | 4.1.2 |
| [GENCOST02-BP01 Balance cost and performance when selecting inference paradigms](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost02-bp01.html) | 4.1.2, 4.1.3 |
| [GENCOST02-BP02 Optimize resource consumption to minimize hosting costs](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost02-bp02.html) | 4.1.2 |
| [GENCOST03 Cost-aware prompting](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost03.html) | 4.1.1 |
| [GENCOST03-BP01 Optimize prompt token length](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost03-bp01.html) | 4.1.1 |
| [GENCOST03-BP02 Control model response length](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost03-bp02.html) | 4.1.1 |
| [GENCOST03-BP03 Implement prompt caching to reduce token costs](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost03-bp03.html) | 4.1.4 |
| [GENCOST03-BP04 Annotate user input to enable cost-aware content filtering](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost03-bp04.html) | 4.1.1 |
| [GENCOST05 Cost-informed agents](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost05.html) | 4.1.1 |
| [GENCOST05-BP01 Create stopping conditions to control long-running workflows](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost05-bp01.html) | 4.1.1 |

`GENCOST04 Cost-informed vector stores` y su única práctica `GENCOST04-BP01 Reduce vector length on embedded tokens` están desarrollados en [Task 1.4](../domain-1/task-1-4-vector-stores.md) y [Task 1.5](../domain-1/task-1-5-retrieval.md) de Domain 1, y registrados en el [inventario de Domain 1](../domain-1/referencias-oficiales.md).

### Pilar de Performance efficiency

| Página | Usado en |
| --- | --- |
| [Performance efficiency](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/performance-efficiency.html) | Marco del Task 4.2 |
| [GENPERF01-BP01 Define a ground truth data set of prompts and responses](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf01-bp01.html) | 4.3.6 |
| [GENPERF01-BP02 Collect performance metrics from generative AI workloads](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf01-bp02.html) | 4.2.6 |
| [GENPERF02 Maintaining model performance](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02.html) | 4.2.4 |
| [GENPERF02-BP01 Load test model endpoints](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02-bp01.html) | 4.2.1, 4.2.3 |
| [GENPERF02-BP02 Optimize inference parameters to improve response quality](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02-bp02.html) | 4.2.4 |
| [GENPERF04 Vector store optimization](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf04.html) | 4.2.2 |
| [GENPERF04-BP01 Test vector embeddings for latency and relevant performance](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf04-bp01.html) | 4.2.2 |
| [GENPERF04-BP02 Optimize vector sizes for your use case](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf04-bp02.html) | 4.2.2 |

---

## AWS Well-Architected — Agentic AI Lens

| Página | Usado en |
| --- | --- |
| [AGENTCOST02-BP03 Use intelligent caching to reduce redundant model invocations](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentcost02-bp03.html) | 4.1.4 |

El desarrollo completo del lens está en [Task 2.1 de Domain 2](../domain-2/task-2-1-agentic-ai-y-herramientas.md), con su inventario en el [referencias-oficiales.md de Domain 2](../domain-2/referencias-oficiales.md).

---

## Amazon Bedrock — Capacidad e inferencia

| Página | Usado en |
| --- | --- |
| [Capacity and Performance](https://docs.aws.amazon.com/bedrock/latest/userguide/capacity-limits-cost-optimization.html) | 4.1.3 |
| [Increase model invocation capacity with Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) | 4.1.3 |
| [Prompt caching for faster model inference](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) | 4.1.4 |
| [Optimize model inference for latency](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html) | 4.2.1 |
| [Increase throughput with cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) | 4.2.1 |
| [Supported Regions and models for inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) | 4.2.1 |
| [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html) | 4.2.3 |

---

## Amazon Bedrock — Batch inference

| Página | Usado en |
| --- | --- |
| [Process multiple prompts with batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html) | 4.1.3 |
| [Prerequisites for batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-prereq.html) | 4.1.3 |
| [Format and upload your batch inference data](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-data.html) | 4.1.3 |
| [Required permissions for batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-permissions.html) | 4.1.3 |
| [Protect batch inference jobs using a VPC](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-vpc.html) | 4.1.3 |
| [Create a batch inference job](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-create.html) | 4.1.3 |
| [Monitor batch inference jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-monitor.html) | 4.1.3 |
| [View the results of a batch inference job](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-results.html) | 4.1.3 |
| [Supported Regions and models for batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-supported.html) | 4.1.3 |
| [Monitor Amazon Bedrock job state changes using Amazon EventBridge](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-eventbridge.html) | 4.1.3 |

---

## Amazon Bedrock — Optimización de prompts y evaluación

| Página | Usado en |
| --- | --- |
| [Optimize and migrate prompts in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-optimization-migration.html) | 4.1.1 |
| [Optimize a prompt](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-optimize.html) | 4.1.1 |
| [How Advanced Prompt Optimization works](https://docs.aws.amazon.com/bedrock/latest/userguide/advanced-prompt-optimization-how.html) | 4.1.1 |
| [Deploy a prompt to your application using versions](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-deploy.html) | 4.2.4 |
| [Evaluate model performance using another LLM as a judge](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-judge.html) | 4.2.4 |
| [Inference request parameters and response fields for foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-parameters.html) | 4.2.4 |

---

## Amazon Bedrock — Knowledge Bases y retrieval

| Página | Usado en |
| --- | --- |
| [Configure and customize queries and response generation](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html) | 4.2.2 |
| [Use agentic retrieval to query a knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic-retrieve.html) | 4.2.2 |
| [Observability for managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-observability.html) | 4.3.5 |
| [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) | 4.3.6 |
| [Create a retrieve and generate evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-create-randg.html) | 4.3.6 |
| [Review knowledge base evaluation job reports and metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-report.html) | 4.3.6 |
| [Track agent's step-by-step reasoning process using trace](https://docs.aws.amazon.com/bedrock/latest/userguide/trace-events.html) | 4.3.6 |

---

## Amazon Bedrock AgentCore

| Página | Usado en |
| --- | --- |
| [Understand observability for agentic resources in AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-telemetry.html) | 4.3.4 |
| [AgentCore generated built-in tools observability data](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-tool-metrics.html) | 4.3.4 |
| [AgentCore Cross-Account Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-cross-account.html) | 4.3.4 |
| [Execute code and analyze data using Amazon Bedrock AgentCore Code Interpreter](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-tool.html) | 4.3.4 |
| [Interact with web applications using Amazon Bedrock AgentCore Browser](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html) | 4.3.4 |

---

## Amazon Bedrock — Etiquetado y monitorización

| Página | Usado en |
| --- | --- |
| [Tagging Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/tagging.html) | 4.1.2 |
| [Monitor bedrock-runtime inference using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html) | 4.1.1, 4.2.1 |
| [Monitor Amazon Bedrock Agents using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-agents-cw-metrics.html) | 4.2.1 |
| [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) | 4.3.1, 4.3.2 |
| [Apply tags to user input to filter content](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html) | 4.1.1 |

---

## Amazon Bedrock — API Reference

| Operación o tipo | Usado en |
| --- | --- |
| [`CreateModelInvocationJob`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_CreateModelInvocationJob.html) | 4.1.3 |
| [`GetModelInvocationJob`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_GetModelInvocationJob.html) | 4.1.3 |
| [`ListModelInvocationJobs`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ListModelInvocationJobs.html) | 4.1.3 |
| [`ModelInvocationJobSummary`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ModelInvocationJobSummary.html) | 4.1.3 |
| [`OptimizePrompt`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_OptimizePrompt.html) | 4.1.1 |
| [`KnowledgeBaseRetrievalConfiguration`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_KnowledgeBaseRetrievalConfiguration.html) | 4.2.2 |
| [`QueryTransformationConfiguration`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_QueryTransformationConfiguration.html) | 4.2.2 |
| [`RetrievalFilter`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrievalFilter.html) | 4.2.2 |
| [`RetrieveAndGenerateStream`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerateStream.html) | 4.2.6 |
| [`InvokeAgent`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeAgent.html) | 4.3.6 |
| [`GetKnowledgeBase`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_GetKnowledgeBase.html) | 4.3.5 |

---

## Amazon ElastiCache — Caché semántica

Doc set completo dedicado a la caché semántica de respuestas de LLM. Es la fuente principal del skill 4.1.4 y no estaba citado en ningún dominio anterior.

| Página | Usado en |
| --- | --- |
| [Overview of semantic caching](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/semantic-caching-overview.html) | 4.1.4 |
| [Why ElastiCache for Valkey for semantic caching](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/semantic-caching-why-elasticache.html) | 4.1.4 |
| [Solution architecture](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/semantic-caching-architecture.html) | 4.1.4 |
| [Implementing a semantic cache with ElastiCache for Valkey](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/semantic-caching-implementation.html) | 4.1.4 |
| [Impact and benchmarks](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/semantic-caching-benchmarks.html) | 4.1.4 |

---

## AWS Cost Management

| Página | Usado en |
| --- | --- |
| [Analyzing your costs and usage with AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html) | 4.1.2 |
| [Getting started with AWS Cost Anomaly Detection](https://docs.aws.amazon.com/cost-management/latest/userguide/getting-started-ad.html) | 4.1.2 |
| [Use cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html) | 4.1.2 |

---

## Amazon SageMaker AI — Escalado y métricas de endpoint

| Página | Usado en |
| --- | --- |
| [Auto scaling policy overview](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling-policy.html) | 4.2.5 |
| [Scale an endpoint to zero instances](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling-zero-instances.html) | 4.2.5 |
| [Amazon SageMaker AI enhanced metrics for inference endpoints](https://docs.aws.amazon.com/sagemaker/latest/dg/monitoring-cloudwatch-enhanced-metrics.html) | 4.2.5 |
| [Model parallelism and large model inference](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference.html) | 4.2.3 |
| [`MetricsConfig`](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_MetricsConfig.html) | 4.2.5 |
| [`CreateEndpointConfig`](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpointConfig.html) | 4.2.5 |
| [`UpdateEndpoint`](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpoint.html) | 4.2.5 |

---

## Amazon CloudWatch — Observabilidad de IA generativa

Capa que AWS construyó encima del catálogo de métricas de Bedrock. No estaba citada en ningún dominio anterior.

| Página | Usado en |
| --- | --- |
| [Generative AI observability](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/GenAI-observability.html) | 4.3.1 |
| [Model Invocations](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/model-invocations.html) | 4.3.1, 4.3.2 |
| [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AgentCore-Agents.html) | 4.3.1, 4.3.4 |
| [Monitor AI coding agents with Amazon CloudWatch Coding Agent Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/coding-agents-insights.html) | 4.3.1 |
| [Example: Use Application Signals to troubleshoot generative AI applications interacting with Amazon Bedrock models](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Services-example-scenario-GenerativeAI.html) | 4.3.1 |
| [Application monitoring with CloudWatch Application Signals](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Monitoring-Sections.html) | 4.3.1 |
| [Enabling CloudWatch Application Signals](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Signals-Enable.html) | 4.3.1 |

---

## Amazon CloudWatch — Transaction Search, dashboards y alarmas

| Página | Usado en |
| --- | --- |
| [Transaction Search](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Transaction-Search.html) | 4.3.1 |
| [Spans](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Transaction-Search-ingesting-span-log-groups.html) | 4.3.1 |
| [Adding custom attributes](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Transaction-Search-add-custom-attributes.html) | 4.3.1, 4.3.3 |
| [Using Amazon CloudWatch dashboards](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Dashboards.html) | 4.3.3 |
| [Creating a customized dashboard](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/create_dashboard.html) | 4.3.3 |
| [Creating dashboards with variables](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_dashboard_variables.html) | 4.3.3 |
| [Using widgets on dashboards](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/create-and-work-with-widgets.html) | 4.3.3 |
| [CloudWatch cross-account observability](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Unified-Cross-Account.html) | 4.3.3 |
| [Using CloudWatch anomaly detection](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Anomaly_Detection.html) | 4.3.2 |
| [Create an anomaly detection alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Create_Anomaly_Detection_Alarm.html) | 4.3.2 |
| [Help protect sensitive log data with masking](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html) | 4.3.2 |
| [Protect sensitive log data with data protection policies](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/cloudwatch-logs-data-protection-policies.html) | 4.3.1 |

---

## Amazon CloudWatch Logs — API de entrega de logs

| Operación | Usado en |
| --- | --- |
| [`PutDeliverySource`](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutDeliverySource.html) | 4.3.5 |
| [`PutDeliveryDestination`](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutDeliveryDestination.html) | 4.3.5 |
| [`CreateDelivery`](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_CreateDelivery.html) | 4.3.5 |

---

## Amazon OpenSearch Service

| Página | Usado en |
| --- | --- |
| [k-NN search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html) | 4.2.2 |
| [Managing capacity limits for Amazon OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-scaling.html) | 4.3.5 |
| [Monitoring Amazon OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-monitoring.html) | 4.3.5 |

---

## Application Auto Scaling

| Página | Usado en |
| --- | --- |
| [What is Application Auto Scaling?](https://docs.aws.amazon.com/autoscaling/application/userguide/what-is-application-auto-scaling.html) | 4.1.3 |
| [AWS services that you can use with Application Auto Scaling](https://docs.aws.amazon.com/autoscaling/application/userguide/integrated-services-list.html) | 4.1.3 |
| [`RegisterScalableTarget`](https://docs.aws.amazon.com/autoscaling/application/APIReference/API_RegisterScalableTarget.html) | 4.2.5 |

---

## Amazon API Gateway y Amazon CloudFront

| Página | Usado en |
| --- | --- |
| [Cache settings for REST APIs in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-caching.html) | 4.1.4 |
| [Optimizing caching and availability](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/ConfiguringCaching.html) | 4.1.4 |

---

## Páginas citadas de Domain 1, Domain 2 y Domain 3

Estos materiales enlazan a los dominios anteriores en lugar de duplicar contenido. Las referencias completas de esas páginas están en sus inventarios respectivos: [Domain 1](../domain-1/referencias-oficiales.md), [Domain 2](../domain-2/referencias-oficiales.md) y [Domain 3](../domain-3/referencias-oficiales.md). Los temas compartidos y los enlaces correspondientes están en la [tabla de relación con los Domains 1, 2 y 3](./README.md#relación-con-los-domains-1-2-y-3) del índice.
