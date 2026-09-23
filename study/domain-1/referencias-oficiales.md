# Referencias oficiales de AWS — Domain 1

[← Volver al índice](./README.md)

Todas las páginas de `docs.aws.amazon.com` consultadas para construir la cobertura del Domain 1, agrupadas por servicio. El contenido de estas fuentes fue parafraseado y resumido en los archivos de este directorio para cumplir con restricciones de licencia.

---

## Guía del examen AIP-C01

| Página | Contenido |
| --- | --- |
| [AWS Certified Generative AI Developer - Professional (AIP-C01)](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) | Introducción, candidato objetivo, contenido del examen, pesos por dominio |
| [Content Domain 1](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain1.html) | Las 6 tasks y 28 skills del dominio |
| [Content Domain 2: Implementation and Integration](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain2.html) | 26 % del examen |
| [Content Domain 3: AI Safety, Security, and Governance](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain3.html) | 20 % del examen |
| [Content Domain 4: Operational Efficiency and Optimization](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain4.html) | 12 % del examen |
| [Content Domain 5: Testing, Validation, and Troubleshooting](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain5.html) | 11 % del examen |
| [Technologies and concepts](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-technologies-concepts.html) | Lista de conceptos que pueden aparecer |
| [Mentions of AWS services on the exam](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-service-mentions.html) | Cómo se nombran los servicios en las preguntas |
| [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html) | Servicios en alcance por categoría |
| [Out-of-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-out-of-scope-services.html) | Servicios fuera de alcance |

---

## AWS Well-Architected

### Generative AI Lens

| Página | Usado en |
| --- | --- |
| [Generative AI Lens — AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html) | 1.1.1, 1.1.3 |
| [Generative AI lifecycle](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lifecycle.html) | 1.1.1, 1.2.1 |
| [Reliability](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/reliability.html) | 1.1.3, 1.2.3, 1.6.3, 1.6.4 |
| [GENREL01 Manage throughput quotas](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel01.html) | 1.2.3 |
| [GENREL02 Network reliability](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel02.html) | 1.2.3 |
| [GENREL03 Prompt remediation and recovery actions](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel03.html) | 1.2.3 |
| [GENREL03-BP01 Use logic to manage prompt flows and gracefully recover from failure](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel03-bp01.html) | 1.2.3, 1.6.2, 1.6.6 |
| [GENREL04 Prompt management](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel04.html) | 1.6.3 |
| [GENREL05 Distributed availability](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel05.html) | 1.2.3 |
| [GENREL06 Distributed compute tasks](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel06.html) | 1.2.3 |
| [GENREL06-BP01 Design for fault-tolerance for high-performance distributed computation tasks](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel06-bp01.html) | 1.2.3 |
| [GENCOST04-BP01 Reduce vector length on embedded tokens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost04-bp01.html) | 1.4.3, 1.5.2 |

### Otros lenses

| Página | Usado en |
| --- | --- |
| [Agentic AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html) | 1.1.3 |
| [Responsible AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/responsible-ai-lens.html) | 1.1.3 |
| [Machine Learning Lens](https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/machine-learning-lens.html) | 1.1.1, 1.1.3 |
| [Lens Catalog for AWS WA Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lens-catalog.html) | 1.1.3 |
| [Custom lenses in AWS WA Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) | 1.1.3 |
| [Amazon OpenSearch Service Lens](https://docs.aws.amazon.com/wellarchitected/latest/amazon-opensearch-service-lens/full.html) | 1.4.3 |
| [AOSPERF01-BP01 Maintain shard sizes at recommended ranges](https://docs.aws.amazon.com/wellarchitected/latest/amazon-opensearch-service-lens/aosperf01-bp01.html) | 1.4.3 |
| [AOSPERF01-BP03 Check the number of shards per GiB of heap memory](https://docs.aws.amazon.com/wellarchitected/latest/amazon-opensearch-service-lens/aosperf01-bp03.html) | 1.4.3 |

Repositorio público de custom lenses: [aws-samples/sample-well-architected-custom-lens](https://github.com/aws-samples/sample-well-architected-custom-lens)

---

## Amazon Bedrock

### Inferencia y modelos

| Página | Usado en |
| --- | --- |
| [Inference using Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) | 1.2.2, 1.3.3, 1.6.2 |
| [Making inference requests](https://docs.aws.amazon.com/bedrock/latest/userguide/inference.html) | 1.2.1 |
| [API restrictions](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-api-restrictions.html) | 1.3.3 |
| [Models at a glance / model cards](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html) | 1.2.1, 1.3.3 |
| [Supported foundation models in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) | 1.2.1 |
| [Request access to models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) | 1.1.2 |
| [Inference request parameters and response fields for foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html) | 1.2.1, 1.6.5 |
| [Influence response generation with inference parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-parameters.html) | 1.5.5, 1.6.5 |
| [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html) | 1.3.3, 1.3.4, 1.5.6, 1.6.5 |
| [Batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html) | 1.2.1, 1.5.2 |
| [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html) | 1.2.1, 1.3.1, 1.4.5, 1.6.6 |

### Guías de prompting de Amazon Nova

Doc set propio, en `nova/latest/userguide/`.

| Página | Usado en |
| --- | --- |
| [Prompting best practices for Amazon Nova understanding models](https://docs.aws.amazon.com/nova/latest/userguide/prompting.html) | 1.6.5 |
| [Generating images with Amazon Nova](https://docs.aws.amazon.com/nova/latest/userguide/image-generation.html) | 1.6.5 |
| [Generating videos with Amazon Nova](https://docs.aws.amazon.com/nova/latest/userguide/video-generation.html) | 1.6.5 |

### Enrutamiento, capacidad y resiliencia

| Página | Usado en |
| --- | --- |
| [Route model inference requests across AWS Regions with cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) | 1.2.3 |
| [Geographic cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/geographic-cross-region-inference.html) | 1.2.3 |
| [Global cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/global-cross-region-inference.html) | 1.2.3 |
| [Supported Regions and models for inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) | 1.2.2, 1.2.3 |
| [Set up a model invocation resource using inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html) | 1.1.2, 1.1.3, 1.2.1, 1.2.2, 1.6.3 |
| [Understanding intelligent prompt routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) | 1.2.2 |
| [Increase model invocation capacity with Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) | 1.2.1, 1.2.4 |
| [Supported Regions and models for Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-thru-supported.html) | 1.2.1 |

### Customización y evaluación

| Página | Usado en |
| --- | --- |
| [Customize your model to improve its performance for your use case](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html) | 1.2.4, 1.6.5 |
| [Customize a model with fine-tuning](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-fine-tuning.html) | 1.2.4 |
| [Customize a model with reinforcement fine-tuning](https://docs.aws.amazon.com/bedrock/latest/userguide/reinforcement-fine-tuning.html) | 1.2.4, 1.6.5 |
| [Customize a model with distillation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html) | 1.2.4 |
| [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) | 1.1.2, 1.2.1, 1.6.4 |
| [Creating an automatic model evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-automatic.html) | 1.6.4 |
| [Creating a model evaluation job that uses human workers](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-human.html) | 1.6.4 |
| [Evaluate model performance using another LLM as a judge](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-judge.html) | 1.6.4 |
| [Evaluate the performance of RAG sources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html) | 1.6.4 |

### Knowledge Bases

| Página | Usado en |
| --- | --- |
| [Build a managed knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-managed.html) | 1.4.1, 1.5.3 |
| [Prerequisites for creating a knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-prereq.html) | 1.4.1 |
| [Prerequisites for using a vector store you created](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-setup.html) | 1.4.1, 1.5.2, 1.5.3 |
| [Prerequisites for your knowledge base data](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-ds.html) | 1.3.1, 1.4.5 |
| [Supported models and Regions for Amazon Bedrock knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html) | 1.3.2, 1.3.3, 1.5.2 |
| [Create a knowledge base by connecting to a data source](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html) | 1.4.1 |
| [Connect a data source to your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/data-source-connectors.html) | 1.4.1, 1.4.4 |
| [Connect to Amazon S3 for your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/s3-data-source-connector.html) | 1.3.4, 1.4.2, 1.4.4, 1.5.1 |
| [Connect your knowledge base to a custom data source](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-data-source-connector.html) | 1.4.4 |
| [Connect to Confluence for your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/confluence-data-source-connector.html) | 1.4.4 |
| [Connect to Microsoft SharePoint for your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/sharepoint-data-source-connector.html) | 1.4.4 |
| [Connect to Salesforce for your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/salesforce-data-source-connector.html) | 1.4.4 |
| [Connect to the Web Crawler for your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/webcrawl-data-source-connector.html) | 1.4.4 |
| [Build a knowledge base by connecting to a structured data store](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-structured.html) | 1.4.4 |
| [How content chunking works for knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html) | 1.3.2, 1.4.1, 1.5.1 |
| [Parsing options for your data source](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html) | 1.3.2, 1.5.1 |
| [Use a custom transformation Lambda function](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-custom-transformation.html) | 1.5.1 |
| [Customize ingestion for a data source](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-customize-ingestion.html) | 1.5.1 |
| [Sync your data with your Amazon Bedrock knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html) | 1.4.5 |
| [Configure and customize queries and response generation](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html) | 1.4.2, 1.5.4, 1.5.5 |
| [Query a knowledge base and retrieve data](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve.html) | 1.5.4 |
| [Query a knowledge base and generate responses](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve-generate.html) | 1.5.4 |
| [Chat with your document without a knowledge base configured](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-chatdoc.html) | 1.1.2 |
| [Build a knowledge base for multimodal content](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-multimodal.html) | 1.3.2 |
| [Choosing your multimodal processing approach](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-multimodal-choose-approach.html) | 1.3.2 |
| [Native multimodal processing (managed KB)](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-native-multimodal.html) | 1.3.2 |
| [Encryption of knowledge base resources](https://docs.aws.amazon.com/bedrock/latest/userguide/encryption-kb.html) | 1.4.1, 1.4.4 |
| [Create a service role for Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-permissions.html) | 1.4.1, 1.4.4 |
| [Access Control Lists awareness enablement](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-acl.html) | 1.4.2 |
| [Observability for managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-observability.html) | 1.4.5, 1.6.3 |
| [Connect to your knowledge base through AgentCore Gateway](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-gateway-target.html) | 1.4.4, 1.5.6 |
| [Delete an Amazon Bedrock knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-delete.html) | 1.4.5 |

### Retrieval y reranking

| Página | Usado en |
| --- | --- |
| [Improve the relevance of query responses with a reranker model](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html) | 1.5.4 |
| [Supported Regions and models for reranking](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-supported.html) | 1.5.4 |
| [Reranking permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-prereq.html) | 1.5.4 |
| [Use a reranker model](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-use.html) | 1.5.4 |

### Prompts, Flows y Guardrails

| Página | Usado en |
| --- | --- |
| [Prompt engineering concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html) | 1.3.3, 1.6.1, 1.6.2 |
| [Construct and store reusable prompts with Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html) | 1.1.2, 1.1.3, 1.6.1, 1.6.3 |
| [Create a prompt using Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-create.html) | 1.6.3 |
| [Test a prompt using Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-test.html) | 1.6.3, 1.6.4 |
| [Optimize a prompt](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-optimize.html) | 1.6.3, 1.6.5 |
| [Deploy a prompt to your application using versions](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-deploy.html) | 1.6.3 |
| [Build an end-to-end generative AI workflow with Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html) | 1.1.1, 1.2.3, 1.6.6 |
| [How Amazon Bedrock Flows works](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-how-it-works.html) | 1.6.6 |
| [Node types for your flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-nodes.html) | 1.6.6 |
| [Use expressions to define inputs in Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-expressions.html) | 1.6.6 |
| [Deploy a flow using versions and aliases](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-deploy.html) | 1.6.6 |
| [Include guardrails in your flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-guardrails.html) | 1.6.6 |
| [Run Amazon Bedrock flows asynchronously with flow executions](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-create-async.html) | 1.6.6 |
| [Converse with an Amazon Bedrock flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-multi-turn-invocation.html) | 1.6.2, 1.6.6 |
| [Invoke a Lambda function from a flow in a different account](https://docs.aws.amazon.com/bedrock/latest/userguide/flow-cross-account-lambda.html) | 1.6.6 |
| [Detect and filter harmful content by using Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) | 1.1.3, 1.5.4, 1.6.1 |
| [How Amazon Bedrock Guardrails works](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-how.html) | 1.6.1 |
| [Safeguard tiers for guardrails policies](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tiers.html) | 1.6.1 |
| [Languages supported by Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-supported-languages.html) | 1.6.1 |
| [Apply tags to user input to filter content](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html) | 1.6.1 |
| [Distribute guardrail inference across AWS Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region.html) | 1.2.3, 1.6.1 |
| [Apply cross-account safeguards with Guardrails enforcements](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-enforcements.html) | 1.6.1, 1.6.3 |

### Tool use y observabilidad

| Página | Usado en |
| --- | --- |
| [Use a tool to complete an Amazon Bedrock model response](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html) | 1.5.6 |
| [Client-side tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-client-side.html) | 1.5.6 |
| [Server-side tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-server-side.html) | 1.5.6 |
| [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) | 1.6.3 |
| [CloudTrail management events in model evaluation jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/cloudtrail-events-in-model-evaluations.html) | 1.6.3 |

### API Reference

| Operación | Usado en |
| --- | --- |
| [`Converse`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) | 1.2.2, 1.3.3 |
| [`ConverseStream`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html) | 1.2.2 |
| [`InvokeModel`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html) | 1.3.3 |
| [`DocumentBlock`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_DocumentBlock.html) | 1.3.3 |
| [`ContentBlock`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ContentBlock.html) | 1.3.3 |
| [`Retrieve`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html) | 1.4.2, 1.5.4, 1.5.6 |
| [`RetrieveAndGenerate`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerate.html) | 1.5.4, 1.5.5, 1.5.6 |
| [`RetrieveAndGenerateStream`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerateStream.html) | 1.5.4, 1.5.6 |
| [`Rerank`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Rerank.html) | 1.5.4, 1.5.6 |
| [`KnowledgeBaseRetrievalConfiguration`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_KnowledgeBaseRetrievalConfiguration.html) | 1.5.4 |
| [`RetrievalFilter`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrievalFilter.html) | 1.4.2 |
| [`CreateDataSource`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_CreateDataSource.html) | 1.4.4 |
| [`StartIngestionJob`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_StartIngestionJob.html) | 1.4.5 |
| [`StopIngestionJob`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_StopIngestionJob.html) | 1.4.5 |
| [`GetIngestionJob`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_GetIngestionJob.html) | 1.4.5 |
| [`ListIngestionJobs`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_ListIngestionJobs.html) | 1.4.5 |
| [`CreateFlow`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_CreateFlow.html) | 1.6.6 |
| [`FlowNode`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_FlowNode.html) | 1.6.6 |
| [`FlowConnection`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_FlowConnection.html) | 1.6.6 |
| [`NeptuneAnalyticsConfiguration`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_NeptuneAnalyticsConfiguration.html) | 1.4.1 |

---

## Amazon Bedrock AgentCore

| Página | Usado en |
| --- | --- |
| [Core concepts for Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-core-concepts.html) | 1.5.6 |
| [Use an AgentCore gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-using.html) | 1.5.6 |
| [Configure AgentCore Runtime as gateway target](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-vpc-egress.html) | 1.5.6 |
| [MCP protocol contract](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp-protocol-contract.html) | 1.5.6 |
| [AgentCore release notes](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html) | 1.5.6 |

---

## Amazon SageMaker AI

| Página | Usado en |
| --- | --- |
| [Fine-tune models with adapter inference components](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-adapt.html) | 1.2.4 |
| [Deploy models for real-time inference](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-deploy-models.html) | 1.2.4 |
| [Invoke models for real-time inference](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-test-endpoints.html) | 1.3.3 |
| [Model Registration Deployment with Model Registry](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html) | 1.1.3, 1.2.4 |
| [Model Registry Models, Model Versions, and Model Groups](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry-models.html) | 1.2.4 |
| [Model Registry Collections](https://docs.aws.amazon.com/sagemaker/latest/dg/modelcollections.html) | 1.2.4 |
| [Pipelines actions](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines-build.html) | 1.2.4 |
| [Get recommendations for models with LoRA adapters](https://docs.aws.amazon.com/sagemaker/latest/dg/generative-ai-inference-recommendations-adapters.html) | 1.2.4 |
| [Benchmark multi-LoRA endpoints](https://docs.aws.amazon.com/sagemaker/latest/dg/generative-ai-inference-recommendations-benchmark.html) | 1.2.4 |
| [Data transformation workloads with SageMaker Processing](https://docs.aws.amazon.com/sagemaker/latest/dg/processing-job.html) | 1.3.2 |
| [Prepare ML Data with Amazon SageMaker Data Wrangler](https://docs.aws.amazon.com/sagemaker/latest/dg/data-wrangler.html) | 1.3.1 |
| [Get Insights On Data and Data Quality](https://docs.aws.amazon.com/sagemaker/latest/dg/data-wrangler-data-insights.html) | 1.3.1 |
| [Interactive data preparation widget](https://docs.aws.amazon.com/sagemaker/latest/dg/data-wrangler-interactively-prepare-data-notebook.html) | 1.3.1 |
| [Amazon SageMaker AI metrics in Amazon CloudWatch](https://docs.aws.amazon.com/sagemaker/latest/dg/monitoring-cloudwatch.html) | 1.3.2 |

---

## Amazon OpenSearch Service

| Página | Usado en |
| --- | --- |
| [Vector search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vector-search.html) | 1.4.1, 1.4.3, 1.5.2 |
| [k-Nearest Neighbor (k-NN) search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html) | 1.4.3 |
| [Working with vector search collections](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vector-search.html) | 1.4.1, 1.4.3 |
| [Access Amazon OpenSearch Serverless using an interface endpoint (AWS PrivateLink)](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vpc.html) | 1.4.1, 1.4.4 |
| [Vector Auto-Optimize](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-auto-optimize.html) | 1.4.3 |
| [Creating and managing OpenSearch Service domains](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/createupdatedomains.html) | 1.4.1 |
| [Operational best practices for Amazon OpenSearch Service](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/bp.html) | 1.4.5 |
| [UltraWarm storage](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/ultrawarm.html) | 1.4.3 |
| [Cold storage](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/cold-storage.html) | 1.4.3 |
| [Monitoring OpenSearch cluster metrics with CloudWatch](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/managedomains-cloudwatchmetrics.html) | 1.4.3 |
| [Cost optimization](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/cost-optimization.html) | 1.4.3 |

---

## Otros vector stores

| Página | Usado en |
| --- | --- |
| [Using Aurora PostgreSQL as a knowledge base](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.VectorDB.html) | 1.4.1, 1.5.3 |
| [Password management with Amazon Aurora and AWS Secrets Manager](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/rds-secrets-manager.html) | 1.4.1 |
| [Amazon S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html) | 1.4.1 |
| [Create an Amazon Bedrock knowledge base with S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-getting-started.html) | 1.4.1 |
| [S3 Vectors limitations and restrictions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-limitations.html) | 1.4.1 |
| [Data protection and encryption in Amazon S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-data-encryption.html) | 1.4.1 |
| [Vector indexing in Neptune Analytics](https://docs.aws.amazon.com/neptune-analytics/latest/userguide/vector-index.html) | 1.4.1 |
| [Create a Neptune Analytics graph in the console](https://docs.aws.amazon.com/neptune-analytics/latest/userguide/create-graph-using-console.html) | 1.4.1 |
| [Choosing an AWS vector database for RAG use cases](https://docs.aws.amazon.com/prescriptive-guidance/latest/choosing-an-aws-vector-database-for-rag-use-cases/introduction.html) | 1.4.1 |

---

## Datos, calidad y servicios de AI

| Página | Usado en |
| --- | --- |
| [AWS Glue Data Quality](https://docs.aws.amazon.com/glue/latest/dg/glue-data-quality.html) | 1.3.1 |
| [Data Quality Definition Language (DQDL) reference](https://docs.aws.amazon.com/glue/latest/dg/dqdl.html) | 1.3.1 |
| [Getting started with AWS Glue Data Quality for the Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/data-quality-getting-started.html) | 1.3.1 |
| [Flatten nested structs](https://docs.aws.amazon.com/glue/latest/dg/transforms-flatten.html) | 1.3.1 |
| [Evaluating data quality for ETL jobs in AWS Glue Studio](https://docs.aws.amazon.com/glue/latest/dg/tutorial-data-quality.html) | 1.3.1 |
| [What is Amazon Comprehend?](https://docs.aws.amazon.com/comprehend/latest/dg/what-is.html) | 1.3.4 |
| [Amazon Comprehend Custom](https://docs.aws.amazon.com/comprehend/latest/dg/concepts-custom.html) | 1.3.4, 1.6.2 |
| [Amazon Comprehend Flywheels](https://docs.aws.amazon.com/comprehend/latest/dg/flywheels.html) | 1.3.4, 1.6.2 |
| [Amazon Comprehend Insights](https://docs.aws.amazon.com/comprehend/latest/dg/concepts-insights.html) | 1.3.4 |
| [Topic modeling](https://docs.aws.amazon.com/comprehend/latest/dg/topic-modeling.html) | 1.3.4 |
| [What is Amazon Transcribe?](https://docs.aws.amazon.com/transcribe/latest/dg/what-is.html) | 1.3.2 |
| [What is Amazon Textract?](https://docs.aws.amazon.com/textract/latest/dg/what-is.html) | 1.3.2 |
| [What is Amazon Rekognition?](https://docs.aws.amazon.com/rekognition/latest/dg/what-is.html) | 1.3.2 |
| [What is Amazon Kendra?](https://docs.aws.amazon.com/kendra/latest/dg/what-is-kendra.html) | 1.4.4 |
| [What is Amazon Q Business?](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/what-is.html) | 1.4.4 |

---

## Integración, configuración y transferencia

| Página | Usado en |
| --- | --- |
| [What is AWS AppConfig?](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html) | 1.2.2 |
| [Creating a configuration profile in AWS AppConfig](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-configuration-profile.html) | 1.2.2 |
| [Deploying feature flags and configuration data in AWS AppConfig](https://docs.aws.amazon.com/appconfig/latest/userguide/deploying-feature-flags.html) | 1.2.2 |
| [How to use AWS AppConfig Agent to retrieve configuration data](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-agent-how-to-use.html) | 1.2.2 |
| [Create an Amazon S3 location for AWS DataSync](https://docs.aws.amazon.com/datasync/latest/userguide/create-s3-location.html) | 1.4.4 |
| [Add an API Gateway REST API as a target for AgentCore Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/mcp-server.html) | 1.5.6 |
| [Organizing and tracking costs using AWS cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html) | 1.2.2, 1.6.3 |

---

## Notas sobre discrepancias encontradas en la documentación

Al construir estos materiales se detectaron dos puntos donde las páginas oficiales de AWS difieren entre sí. Se documentan aquí para que no se conviertan en confusión durante el estudio:

| Tema | Discrepancia | Cómo tratarla |
| --- | --- | --- |
| **Dimensiones máximas de `knn_vector`** | [Vector search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vector-search.html) indica dimensiones configurables hasta **16.000**; [k-NN search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html) indica una lista de hasta **10.000 floats** | Verificar el límite de la versión y el motor concretos del dominio o colección |
| **Número de fases del ciclo de vida GenAI** | [Generative AI lifecycle](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lifecycle.html) menciona en el texto "siete fases clave" pero enumera y desarrolla **seis**: scoping, model selection, model customization, development and integration, deployment, continuous improvement | Estudiar las **seis fases nombradas**, que son las que se desarrollan como temas |
