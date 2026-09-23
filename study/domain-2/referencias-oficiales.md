# Referencias oficiales de AWS — Domain 2

[← Volver al índice](./README.md)

Todas las páginas de `docs.aws.amazon.com` consultadas para construir la cobertura del Domain 2, agrupadas por servicio. El contenido de estas fuentes fue parafraseado y resumido en los archivos de este directorio para cumplir con restricciones de licencia.

**Total: 122 páginas oficiales.** La columna *Usado en* indica los skills que se apoyan en cada página.

---

## Guía del examen AIP-C01

| Página | Usado en |
| --- | --- |
| [AWS Certified Generative AI Developer - Professional (AIP-C01)](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) | README |
| [Content Domain 2: Implementation and Integration](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain2.html) | README, los 25 skills |
| [Technologies and concepts that might appear on the exam](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-technologies-concepts.html) | README |
| [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html) | README, 2.1.5, 2.5.4 |

---

## AWS Well-Architected — Agentic AI Lens

Lens publicado el **10 de junio de 2026**. Es la fuente estructural del Task 2.1 y aporta el marco de diseño a varios skills de los Tasks 2.3, 2.4 y 2.5.

| Página | Usado en |
| --- | --- |
| [Agentic AI Lens — AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html) | Marco del Task 2.1, 2.3.5, 2.5.4, 2.5.5 |
| [AGENTOPS01 Operational practices for agentic AI systems](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops01.html) | 2.1.1 |
| [AGENTREL02 Predictable task execution](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel02.html) | 2.1.3, 2.3.5 |
| [AGENTREL02-BP05 Establish tiered human oversight and approval workflows](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel02-bp05.html) | 2.1.5 |
| [AGENTREL04 Multi-agent orchestration](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel04.html) | 2.1.1, 2.1.4, 2.1.7, 2.3.5, 2.4.3 |
| [AGENTREL06 Legacy system integration](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel06.html) | 2.3.1, 2.3.5, 2.4.3 |
| [AGENTSEC03 Agent identity and permission management](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec03.html) | 2.3.3 |
| [AGENTSEC04 Agent goal alignment and manipulation prevention](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec04.html) | Marco del Task 2.1, 2.1.3, 2.1.5, 2.3.2, 2.4.1, 2.4.4 |
| [AGENTPERF02 Core processing and reasoning pipeline optimization](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentperf02.html) | 2.1.4, 2.2.3, 2.4.2, 2.4.4 |
| [AGENTCOST02 Model invocation and token cost optimization](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentcost02.html) | 2.1.4, 2.2.3, 2.4.4 |
| [Custom lenses in AWS WA Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) | Marco del Task 2.1 |

Áreas de foco nombradas en el lens y citadas en estos materiales sin página propia consultada: AGENTOPS05 (tracing y dashboards), AGENTOPS06 (testing y evaluación con LLM-as-judge), AGENTREL01-BP03 (actor model), AGENTREL02-BP01 a BP04, AGENTREL04-BP01 a BP04, AGENTREL06-BP01 a BP05, AGENTSEC04-BP02, AGENTSEC06 (comunicación inter-agente), AGENTSEC07 (agentes rogue), AGENTSEC08 (validación de entradas), AGENTPERF02-BP01 a BP04, AGENTPERF05 (patrones de orquestación), AGENTCOST01 (coste del reasoning loop), AGENTCOST02-BP01 a BP04, AGENTCOST05 (atribución multi-agente), AGENTSUS03 (sostenibilidad organizacional).

---

## Amazon Bedrock AgentCore

### Plataforma y runtime

| Página | Usado en |
| --- | --- |
| [Overview — Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) | 2.5.5, marco del Task 2.1 |
| [microVMs — AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html) | 2.1.1, 2.5.5 |
| [Deploy MCP servers in AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html) | 2.1.7 |
| [MCP protocol contract](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp-protocol-contract.html) | 2.1.7 |

### Memory

| Página | Usado en |
| --- | --- |
| [Add memory to your Amazon Bedrock AgentCore agent](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html) | 2.1.1, 2.5.5 |
| [Configure built-in strategies](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/long-term-configuring-built-in-strategies.html) | 2.1.1 |

### Gateway, Policy y Registry

| Página | Usado en |
| --- | --- |
| [Core concepts for Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-core-concepts.html) | 2.1.6, 2.3.5 |
| [Policy in Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html) | 2.1.3, 2.1.5 |
| [AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) | 2.1.7 |

### Identity

| Página | Usado en |
| --- | --- |
| [Provide identity and credential management for agent applications](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html) | 2.3.3 |
| [Overview of Amazon Bedrock AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity-overview.html) | 2.3.3 |
| [Features of AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/key-features-and-benefits.html) | 2.3.3 |
| [Configure inbound JWT authorizer](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/inbound-jwt-authorizer.html) | 2.3.3 |
| [Manage credential providers with AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity-outbound-credential-provider.html) | 2.3.3 |
| [Configure a consent portal](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity-consent-portal.html) | 2.3.3 |
| [Connect to private identity providers](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity-private-idp.html) | 2.3.3 |

### Observability

| Página | Usado en |
| --- | --- |
| [Observe your agent applications on Amazon Bedrock AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) | 2.5.6 |
| [Amazon Bedrock AgentCore generated observability data](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-service-provided.html) | 2.5.6 |

---

## Amazon Bedrock

### Capacidad, inferencia y coste

| Página | Usado en |
| --- | --- |
| [Capacity and Performance](https://docs.aws.amazon.com/bedrock/latest/userguide/capacity-limits-cost-optimization.html) | 2.2.1, 2.2.3 |
| [Increase model invocation capacity with Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) | 2.2.1 |
| [Optimize model inference for latency](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html) | 2.2.3 |
| [Prompt caching for faster model inference](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) | 2.2.2, 2.2.3, 2.5.1 |
| [Understanding intelligent prompt routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) | 2.1.4, 2.2.3, 2.4.4 |
| [Set up a model invocation resource using inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html) | 2.1.4 |
| [Monitor your token usage by counting tokens before running inference](https://docs.aws.amazon.com/bedrock/latest/userguide/count-tokens.html) | 2.5.1 |
| [Models at a glance / model cards](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html) | 2.5.1 |

### Customización de modelos

| Página | Usado en |
| --- | --- |
| [Use Custom model import to import a customized open-source model](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-import-model.html) | 2.2.2 |
| [Customize a model with distillation in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html) | 2.2.3 |
| [Set up inference for a custom model](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-use.html) | 2.2.3 |

### Tool use y structured output

| Página | Usado en |
| --- | --- |
| [Use a tool to complete an Amazon Bedrock model response](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html) | 2.1.6 |
| [Client-side tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-client-side.html) | 2.1.6 |
| [Server-side tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-server-side.html) | 2.1.6 |
| [Anthropic Claude tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-tool-use.html) | 2.1.6 |
| [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html) | 2.1.4, 2.1.6 |

### Guardrails

| Página | Usado en |
| --- | --- |
| [Detect and filter harmful content by using Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) | 2.1.3, 2.1.5 |
| [Apply tags to user input to filter content](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html) | 2.1.3 |
| [Include a guardrail with the Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-converse-api.html) | 2.4.2 |
| [Configure streaming response behavior to filter content](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-streaming.html) | 2.4.2 |
| [Distribute guardrail inference across AWS Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region.html) | 2.3.4 |

### Flows, evaluación y logging

| Página | Usado en |
| --- | --- |
| [Build an end-to-end generative AI workflow with Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html) | 2.5.2, 2.5.5 |
| [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) | 2.3.5, 2.5.4 |
| [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) | 2.2.3, 2.3.5, 2.5.6 |
| [Access Control Lists awareness enablement](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-acl.html) | 2.3.3 |

### Red y protección de datos

| Página | Usado en |
| --- | --- |
| [Protect your data using Amazon VPC and AWS PrivateLink](https://docs.aws.amazon.com/bedrock/latest/userguide/usingVPC.html) | 2.3.4 |
| [Use interface VPC endpoints (AWS PrivateLink) with Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html) | 2.3.4 |
| [(Example) Restrict data access to your Amazon S3 data using VPC](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-s3.html) | 2.3.4 |
| [Protect batch inference jobs using a VPC](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-vpc.html) | 2.3.4 |
| [Protect your model customization jobs using a VPC](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-job-access-security.html) | 2.3.4 |

### API Reference

| Operación | Usado en |
| --- | --- |
| [`ConverseStream`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html) | 2.4.1, 2.4.2 |

---

## Amazon Bedrock Data Automation

| Página | Usado en |
| --- | --- |
| [Transform unstructured data into meaningful insights using Amazon Bedrock Data Automation](https://docs.aws.amazon.com/bedrock/latest/userguide/bda.html) | 2.5.3 |
| [Bedrock Data Automation projects](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-projects.html) | 2.5.3 |
| [Blueprints](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-blueprint-info.html) | 2.5.3 |
| [Standard output in Bedrock Data Automation](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-standard-output.html) | 2.5.3 |

---

## Amazon SageMaker AI

| Página | Usado en |
| --- | --- |
| [Deploy models for inference](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html) | 2.2.1 |
| [Real-time inference](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html) | 2.2.1 |
| [Deploy models with Amazon SageMaker Serverless Inference](https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html) | 2.2.1 |
| [Asynchronous inference](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html) | 2.2.1, 2.2.2 |
| [Deploy models for real-time inference (inference components)](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-deploy-models.html) | 2.2.2 |
| [Model parallelism and large model inference](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference.html) | 2.2.2 |
| [The large model inference (LMI) container documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-container-docs.html) | 2.2.2 |
| [SageMaker AI endpoint parameters for large model inference](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-hosting.html) | 2.2.2 |
| [Deploying uncompressed models](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-uncompressed.html) | 2.2.2 |
| [Deploy large models for inference with TorchServe](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-tutorials-torchserve.html) | 2.2.2 |
| [Model performance optimization with SageMaker Neo](https://docs.aws.amazon.com/sagemaker/latest/dg/neo.html) | 2.2.1, 2.2.2 |
| [Automatic scaling of Amazon SageMaker AI models](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling.html) | 2.2.1, 2.2.2 |
| [Using Amazon Augmented AI for Human Review](https://docs.aws.amazon.com/sagemaker/latest/dg/a2i-use-augmented-ai-a2i-human-review-loops.html) | 2.1.5 |

---

## AWS Step Functions

| Página | Usado en |
| --- | --- |
| [What is Step Functions?](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html) | 2.1.2 |
| [Choice workflow state](https://docs.aws.amazon.com/step-functions/latest/dg/state-choice.html) | 2.1.2, 2.4.4 |
| [Handling errors in Step Functions workflows](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html) | 2.1.3, 2.1.4 |
| [Discover service integration patterns in Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html) | 2.1.5 |

---

## Amazon API Gateway

| Página | Usado en |
| --- | --- |
| [Overview of WebSocket APIs in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api-overview.html) | 2.4.2 |
| [Set up a Lambda proxy integration with payload response streaming](https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode-lambda.html) | 2.4.2, 2.5.1 |
| [Throttle requests to your REST APIs for better throughput](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html) | 2.4.3, 2.4.4 |
| [Develop REST APIs using OpenAPI in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-import-api.html) | 2.5.2 |
| [Export a REST API from API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-export-api.html) | 2.5.2 |
| [Set the OpenAPI basePath property](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-import-api-basePath.html) | 2.5.2 |
| [AWS variables for OpenAPI import](https://docs.aws.amazon.com/apigateway/latest/developerguide/import-api-aws-variables.html) | 2.5.2 |
| [Import an edge-optimized API into API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/import-edge-optimized-api.html) | 2.5.2 |
| [Import a Regional API into API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/import-export-api-endpoints.html) | 2.5.2 |
| [Errors and warnings from importing your API](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-import-api-errors-warnings.html) | 2.5.2 |

---

## AWS Lambda

| Página | Usado en |
| --- | --- |
| [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) | 2.1.3, 2.1.7, 2.2.1, 2.2.2, 2.4.1 |
| [Response streaming for Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html) | 2.4.2, 2.5.1 |

---

## Integración de aplicaciones y eventos

| Página | Usado en |
| --- | --- |
| [Amazon EventBridge Pipes](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes.html) | 2.3.1, 2.3.2 |

---

## Developer Tools y CI/CD

| Página | Usado en |
| --- | --- |
| [What is AWS CodePipeline?](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html) | 2.3.5 |
| [Continuous delivery and continuous integration](https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts-continuous-delivery-integration.html) | 2.3.5 |
| [CodePipeline concepts](https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts.html) | 2.3.5 |
| [How pipeline executions work](https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts-how-it-works.html) | 2.3.5 |
| [How do stage conditions work?](https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts-how-it-works-conditions.html) | 2.3.5 |
| [Pipeline types](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipeline-types.html) | 2.3.5 |
| [Input and output artifacts](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome-introducing-artifacts.html) | 2.3.5 |
| [Welcome to AWS Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/welcome.html) | 2.5.2 |

---

## Amazon Q Developer

| Página | Usado en |
| --- | --- |
| [What is Amazon Q Developer?](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/what-is.html) | 2.5.4 |
| [Reviewing code with Amazon Q Developer](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/code-reviews.html) | 2.5.4 |
| [Amazon Q Developer IDE plugins end of support](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/q-developer-ide-end-of-support.html) | 2.5.4 |
| [Transforming code on the command line with Amazon Q Developer](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/transform-CLI.html) | 2.5.4 |
| [How Amazon Q Developer transforms code for Java language upgrades](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/how-CT-works.html) | 2.5.4 |
| [Amazon Q Detector Library](https://docs.aws.amazon.com/codeguru/detector-library) | 2.5.4 |

---

## Identidad y seguridad

| Página | Usado en |
| --- | --- |
| [Permissions boundaries for IAM entities](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html) | 2.1.3, 2.3.3 |
| [AWS global condition context keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html) | 2.3.3 |

---

## Híbrido, borde y red

| Página | Usado en |
| --- | --- |
| [What is AWS Outposts?](https://docs.aws.amazon.com/outposts/latest/userguide/what-is-outposts.html) | 2.3.4 |
| [What is AWS Wavelength?](https://docs.aws.amazon.com/wavelength/latest/developerguide/what-is-wavelength.html) | 2.3.4 |
| [Access Amazon OpenSearch Serverless using an interface endpoint (AWS PrivateLink)](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vpc.html) | 2.3.4 |

---

## Observabilidad

| Página | Usado en |
| --- | --- |
| [What is AWS X-Ray?](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html) | 2.4.3, 2.5.6 |
| [Analyzing log data with CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html) | 2.5.6 |
| [Use natural language to generate and update CloudWatch Logs Insights queries](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatchLogs-Insights-Query-Assist.html) | 2.5.6 |

---

## SDKs y facturación

| Página | Usado en |
| --- | --- |
| [Retry behavior — AWS SDKs and Tools Reference Guide](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html) | 2.4.3, 2.5.1 |
| [Organizing and tracking costs using AWS cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html) | 2.3.5 |

---

## Notas sobre discrepancias encontradas en la documentación

Al construir estos materiales se detectaron **siete puntos** donde la guía del examen y la documentación oficial no encajan, o donde el contenido que la guía presupone no está en `docs.aws.amazon.com`. Se documentan aquí para que no se conviertan en confusión durante el estudio.

### 1. Strands Agents: nombrado pero sin guía de servicio

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | Los skills **2.1.1**, **2.1.6** y **2.5.5** nombran Strands Agents para sistemas multi-agente, para la "Strands API" de comportamientos personalizados de herramienta, y para orquestación nativa de AWS |
| **Qué dice la documentación** | El [Agentic AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html) lo describe como framework open source model-driven con soporte de MCP, A2A y patrones multi-agente (Graph, Swarm, Workflow). [AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html), [AgentCore Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html) y AgentCore Evaluations lo listan entre los frameworks soportados. **No existe guía de servicio en el portal**, y su documentación propia vive fuera, en `strandsagents.com` (proyecto open source, Apache 2.0) |
| **Además** | **No aparece en la lista de [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html)** del examen |
| **Cómo tratarlo** | Estudiar el sustrato que AWS sí documenta: AgentCore Harness para el agent loop, Runtime para alojar, Gateway para herramientas, Memory para recordar, Identity para autenticar, Policy para acotar, Evaluations y Observability para medir. La tabla de equivalencias está en [Task 2.5 · Skill 2.5.5](./task-2-5-patrones-de-aplicacion-y-tooling.md#sobre-strands-agents-y-aws-agent-squad) |

### 2. AWS Agent Squad: sin páginas y fuera de `awslabs`

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | Los skills **2.1.1** y **2.5.5** lo nombran para sistemas multi-agente y orquestación nativa de AWS |
| **Qué dice la documentación** | **Cero páginas en `docs.aws.amazon.com`**. Tampoco aparece en la lista de In-Scope AWS Services |
| **Estado del proyecto** | Verificado durante la elaboración de estos materiales: el repositorio **dejó la organización `awslabs`** y se mantiene ahora en `2FastLabs/agent-squad`. El proyecto se llamó antes `multi-agent-orchestrator`. Es decir, **la guía del examen nombra un proyecto que dejó de ser AWS-official** |
| **Cómo tratarlo** | Conocer el patrón conceptual (un *classifier* enruta cada turno al agente más adecuado usando descripciones de agente e histórico; un *orchestrator* persiste el intercambio) y reconocerlo como el **arbiter pattern con capability taxonomy** de [AGENTREL04](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel04.html), que sí está documentado, implementable con EventBridge, Step Functions y AWS Agent Registry |

### 3. LMI containers: documentación delegada fuera del portal

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **2.2.2** pide patrones de despliegue basados en contenedor optimizados para memoria, uso de GPU y capacidad de procesamiento de tokens |
| **Qué dice la documentación** | [The large model inference (LMI) container documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-container-docs.html) **delega el contenido al sitio de Deep Java Library**, fuera de `docs.aws.amazon.com`. La página del portal enumera los temas (componentes y arquitectura, selección de instancia y backend, quantization, tensor parallelism, continuous batching, benchmarking) pero no los desarrolla |
| **Cómo tratarlo** | Cubrir el skill con lo que AWS sí documenta en su portal: [artefactos sin comprimir con `ModelDataSource`](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-uncompressed.html), [inference components con copias y scale-to-zero](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-deploy-models.html), [async inference](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html), [Neo e Inferentia](https://docs.aws.amazon.com/sagemaker/latest/dg/neo.html) y [auto scaling](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling.html). Conocer los términos de optimización por su nombre, aunque su desarrollo esté fuera |

### 4. Amazon Q Developer frente a Kiro

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **2.5.4** nombra Amazon Q Developer para generar y refactorizar código, y el **2.5.6** para reconocimiento de patrones de error específicos de GenAI |
| **Qué dice la documentación** | La propia [página de Amazon Q Developer](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/what-is.html) y la de [code reviews](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/code-reviews.html) abren con un aviso de fin de soporte: **el 30 de abril de 2027 AWS discontinuará el soporte de los plugins de IDE de Amazon Q Developer**, y remiten a **Kiro** para capacidades equivalentes, incluidos agentic coding, chat y soporte de MCP. Ver [Amazon Q Developer IDE plugins end of support](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/q-developer-ide-end-of-support.html) |
| **Además** | **Kiro figura en la lista de In-Scope AWS Services** (categoría Developer Tools), y el Agentic AI Lens lo describe como IDE agentic con workflows spec-driven, steering files y hooks |
| **Cómo tratarlo** | Conocer las capacidades de Q Developer porque el skill las nombra (los seis tipos de code review, las cuotas, las transformaciones), y saber que la dirección oficial apunta a Kiro. Si una pregunta contrapone ambos para trabajo agentic en el IDE, Kiro es la respuesta que la documentación respalda |

### 5. Amazon Augmented AI: cerrado a clientes nuevos

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | Amazon Augmented AI aparece en la lista de **In-Scope AWS Services** (categoría Machine Learning), y el skill **2.1.5** pide patrones de human augmentation |
| **Qué dice la documentación** | [Using Amazon Augmented AI for Human Review](https://docs.aws.amazon.com/sagemaker/latest/dg/a2i-use-augmented-ai-a2i-human-review-loops.html) abre con este aviso: **Amazon SageMaker A2I ya no está abierto a clientes nuevos**. Los existentes pueden seguir usándolo, y AWS continúa invirtiendo en mejoras de seguridad y disponibilidad, pero **no hay planes de introducir funcionalidades nuevas** |
| **Cómo tratarlo** | Conocer el vocabulario y el patrón (human review workflow, human loop, worker task template, output data; disparadores por baja confianza o muestreo aleatorio) porque sigue en alcance. Para diseñar hoy el human-in-the-loop de un agente, el camino documentado es [AGENTREL02-BP05](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel02-bp05.html): AgentCore Policy para clasificar el tier, Guardrails como primera pasada, y Step Functions con `.waitForTaskToken` y `HeartbeatSeconds` para la espera |

### 6. Plazos de capacidad reservada inconsistentes entre dos páginas de Bedrock

| Aspecto | Detalle |
| --- | --- |
| **Discrepancia** | [Capacity and Performance](https://docs.aws.amazon.com/bedrock/latest/userguide/capacity-limits-cost-optimization.html) describe el **Reserved Tier** con compromisos de **1 o 3 meses** y mínimo de 1 model unit. [Increase model invocation capacity with Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) describe **tres niveles de compromiso: sin compromiso, 1 mes y 6 meses** |
| **Cómo tratarlo** | Son dos páginas oficiales con vocabulario distinto sobre capacidad reservada. Conocer **ambos conjuntos de cifras** y no fiarse de una sola. Lo que no varía entre páginas: la facturación es **por hora**, **continúa hasta eliminar el recurso**, y **un modelo personalizado requiere Provisioned Throughput** salvo que se configure inferencia on-demand para modelo personalizado |

### 7. Amplify: los componentes declarativos se documentan fuera del portal

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **2.5.2** nombra AWS Amplify para desarrollar **componentes de UI declarativos** |
| **Qué dice la documentación** | [Welcome to AWS Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/welcome.html) cubre el **hosting**: workflow basado en Git, CDN, frameworks soportados, feature branches, PR previews y atomic deployments. La documentación de **Amplify Gen 2** (experiencia code-first en TypeScript, librerías de Data y Auth, y la **Amplify UI library**) vive en **`docs.amplify.aws`**, fuera de `docs.aws.amazon.com` |
| **Cómo tratarlo** | Del portal de AWS se puede dominar Amplify Hosting, que es lo que aparece como servicio en alcance. El modelo de componentes declarativos hay que reconocerlo conceptualmente: UI generada a partir de una definición de datos, no escrita a mano |

---

## Páginas citadas de Domain 1

Estos materiales enlazan al Domain 1 en lugar de duplicar contenido. Las referencias completas de esas páginas están en [referencias-oficiales.md de Domain 1](../domain-1/referencias-oficiales.md). Los temas compartidos y los enlaces correspondientes están en la [tabla de relación con Domain 1](./README.md#relación-con-el-domain-1) del índice.
