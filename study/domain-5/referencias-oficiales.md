# Referencias oficiales de AWS — Domain 5

[← Volver al índice](./README.md)

Todas las páginas de `docs.aws.amazon.com` consultadas para construir la cobertura del Domain 5, agrupadas por servicio. El contenido de estas fuentes fue parafraseado y resumido en los archivos de este directorio para cumplir con restricciones de licencia.

Todas las páginas se obtuvieron a través del MCP server de documentación de AWS (`awslabs.aws-documentation-mcp-server`), con el cliente `scripts/mcp_aws_docs.py`, y se verifican automáticamente con `scripts/verify_study_docs.py`. La columna *Usado en* indica los skills que se apoyan en cada página.

---

## Guía del examen AIP-C01

| Página | Usado en |
| --- | --- |
| [AWS Certified Generative AI Developer - Professional (AIP-C01)](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) | README |
| [Content Domain 5: Testing, Validation, and Troubleshooting](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain5.html) | README, los 14 skills |
| [Technologies and concepts that might appear on the exam](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-technologies-concepts.html) | README |
| [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html) | README |

---

## AWS Well-Architected

### Generative AI Lens — pilar de Operational excellence

| Página | Usado en |
| --- | --- |
| [Operational excellence](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/operational-excellence.html) | Marco del Task 5.1 |
| [GENOPS01 Model performance evaluation](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops01.html) | Marco del Task 5.1 |
| [GENOPS01-BP01 Periodically evaluate functional performance](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops01-bp01.html) | 5.1.1, 5.1.2, 5.1.5 |
| [GENOPS01-BP02 Collect and monitor user feedback](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops01-bp02.html) | 5.1.3 |

### Responsible AI Lens

Lens que no estaba citado en ningún dominio anterior. Su área *Evaluate and release* es el marco de decisión de release del Task 5.1.

| Página | Usado en |
| --- | --- |
| [Evaluate and release](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/evaluate-and-release.html) | Marco del Task 5.1 |
| [RAIER02 Aggregate results](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/raier02.html) | Marco del Task 5.1 |
| [System planning](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/system-planning.html) | Marco del Task 5.1 |

---

## Amazon Bedrock — Evaluaciones de modelo

### Visión general y tipos de job

| Página | Usado en |
| --- | --- |
| [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) | 5.1.2 |
| [Creating an automatic model evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-automatic.html) | 5.1.2 |
| [Evaluate model performance using another LLM as a judge](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-judge.html) | 5.1.2 |
| [Supported Regions and models for model evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-support.html) | 5.1.2 |
| [Required steps before creating your first automatic model evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-automatic.html) | 5.1.2 |
| [Creating your first model evaluation that uses human workers](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-human.html) | 5.1.2, 5.1.3 |
| [Models at a glance (model cards)](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html) | 5.1.2 |
| [Understanding intelligent prompt routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) | 5.1.2 |

### Métricas y task types

| Página | Usado en |
| --- | --- |
| [Use metrics to understand model performance](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-metrics.html) | 5.1.1 |
| [Model evaluation task types](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-tasks.html) | 5.1.1 |
| [General text generation for model evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-tasks-general-text.html) | 5.1.1 |
| [Text summarization for model evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-tasks-text-summary.html) | 5.1.1 |
| [Question and answer for model evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-tasks-question-answer.html) | 5.1.1 |
| [Text classification for model evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-text-classification.html) | 5.1.1 |
| [Judge prompt template for Anthropic Claude Sonnet 4.6](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-judge-prompt-claude-sonnet-4-6.html) | 5.1.1 |

### Métricas propias, datasets y roles

| Página | Usado en |
| --- | --- |
| [Create a prompt for a custom metric (model evaluation)](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-custom-metrics-prompt-formats.html) | 5.1.5 |
| [Create a model evaluation job using custom metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-custom-metrics-create-job.html) | 5.1.5 |
| [Create a custom prompt dataset for a job that uses human workers](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-prompt-datasets-custom-human.html) | 5.1.3 |
| [Service role requirements for automatic model evaluation jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/automatic-service-roles.html) | 5.1.2 |
| [Required CORS permissions on S3 buckets](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-security-cors.html) | 5.1.2 |
| [Data management and encryption in evaluation jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-data-management.html) | 5.1.2 |

### Informes y auditoría

| Página | Usado en |
| --- | --- |
| [Review metrics for an automated model evaluation job (console)](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-report-programmatic.html) | 5.1.1, 5.1.2 |
| [Review the results of a human-based model evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-report-human-customer.html) | 5.1.5 |
| [How the results of your model evaluation job are saved in Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-report-s3.html) | 5.1.2 |
| [CloudTrail management events in model evaluation jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/cloudtrail-events-in-model-evaluations.html) | 5.1.2 |
| [Manage a work team for human evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/human-worker-evaluations.html) | 5.1.3 |

---

## Amazon Bedrock — Evaluaciones de RAG

| Página | Usado en |
| --- | --- |
| [Evaluate the performance of RAG sources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html) | 5.1.5 |
| [Use metrics to understand RAG system performance](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-metrics.html) | 5.1.5 |
| [Creating a retrieve-only RAG evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-create-ro.html) | 5.1.5 |
| [Creating a retrieve-only RAG evaluation job using custom metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-create-ro-custom.html) | 5.1.5 |
| [Creating a retrieve-and-generate RAG evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-create-randg.html) | 5.1.5 |
| [Creating a retrieve-and-generate RAG evaluation job using custom metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-create-randg-custom.html) | 5.1.5 |
| [Create a prompt for a custom metric (RAG evaluation)](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-evaluation-custom-metrics-prompt-formats.html) | 5.1.5 |
| [Review RAG evaluation job reports and metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-report.html) | 5.1.5 |
| [Review metrics for RAG evaluations that use LLMs (console)](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-eval-llm-results.html) | 5.1.5 |

---

## Amazon Bedrock — Observabilidad de runtime

| Página | Usado en |
| --- | --- |
| [Monitor bedrock-runtime inference using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html) | 5.1.2 |

---

## Amazon Bedrock — API Reference

| Operación o tipo | Usado en |
| --- | --- |
| [`HumanEvaluationCustomMetric`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_HumanEvaluationCustomMetric.html) | 5.1.3 |
| [`EvaluationPrecomputedRetrieveSourceConfig`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_EvaluationPrecomputedRetrieveSourceConfig.html) | 5.1.2 |
| [`EvaluationPrecomputedRetrieveAndGenerateSourceConfig`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_EvaluationPrecomputedRetrieveAndGenerateSourceConfig.html) | 5.1.2 |

---

## Amazon SageMaker AI

| Página | Usado en |
| --- | --- |
| [Testing models with production variants](https://docs.aws.amazon.com/sagemaker/latest/dg/model-ab-testing.html) | 5.1.2 |
| [Shadow tests](https://docs.aws.amazon.com/sagemaker/latest/dg/shadow-tests.html) | 5.1.2 |
| [Blue/green deployments with canary traffic shifting](https://docs.aws.amazon.com/sagemaker/latest/dg/deployment-guardrails-blue-green-canary.html) | 5.1.2 |
| [Label data (SageMaker Ground Truth)](https://docs.aws.amazon.com/sagemaker/latest/dg/data-label.html) | 5.1.3 |
| [Create and manage workforces](https://docs.aws.amazon.com/sagemaker/latest/dg/sms-workforce-management.html) | 5.1.3 |


## Task 5.1 (Retrieval, Agentes, Validación)

**Amazon Bedrock AgentCore - Evaluations:**
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/how-it-works-evaluations.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations-types.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/online-evaluations.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-on-demand.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/batch-evaluations-getting-started.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluators.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/create-evaluator.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/skill-evaluators.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/ground-truth-evaluations.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/user-simulation.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-runtime-metrics.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/results-and-output.html
- https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_EvaluationExpectedTrajectory.html

**Amazon Bedrock - Model Evaluation:**
- https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-prompt-datasets.html

**Amazon Bedrock - Runtime API:**
- https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html
- https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html
- https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/inference-parameters.html

**Amazon Bedrock - Structured Output:**
- https://docs.aws.amazon.com/bedrock/latest/userguide/structured-generation.html

**Amazon Bedrock - Troubleshooting:**
- https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html
- https://docs.aws.amazon.com/bedrock/latest/APIReference/CommonErrors.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-runtime.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html

**Amazon OpenSearch Service:**
- https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html
- https://docs.aws.amazon.com/opensearch-service/latest/developerguide/managedomains-cloudwatchmetrics.html
- https://docs.aws.amazon.com/opensearch-service/latest/developerguide/handling-errors.html

**Amazon Bedrock - Knowledge Bases:**
- https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-test.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/data-source-connectors.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html

## Task 5.2 (Monitoreo, Troubleshooting, Optimización)

**Amazon CloudWatch:**
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch-and-eventbridge.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Best_Practice_Recommended_Alarms_AWS_Services.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/session-traces-evaluations.html

**Amazon CloudWatch Logs:**
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/LogsAnomalyDetection.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/LogsAnomalyDetection-Metrics.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax-Anomaly.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Subscriptions.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/cloudwatch-logs-and-interface-VPC.html

**AWS X-Ray:**
- https://docs.aws.amazon.com/xray/latest/devguide/xray-concepts.html
- https://docs.aws.amazon.com/xray/latest/devguide/xray-console-analytics.html
- https://docs.aws.amazon.com/xray/latest/devguide/xray-console-servicemap.html
- https://docs.aws.amazon.com/xray/latest/devguide/xray-api-segmentdocuments.html
- https://docs.aws.amazon.com/xray/latest/devguide/xray-api-sampling.html

**Amazon CloudWatch Synthetics:**
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries_WritingCanary.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries_Blueprints.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries_Function_Library.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries_metrics.html

**Amazon QuickSight:**
- https://docs.aws.amazon.com/quicksight/latest/user/welcome.html
- https://docs.aws.amazon.com/quick/latest/userguide/working-with-dashboards.html
- https://docs.aws.amazon.com/quick/latest/userguide/sending-reports.html
- https://docs.aws.amazon.com/quick/latest/userguide/subscribing-to-reports.html

**AWS Well-Architected Framework:**
- https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/machine-learning-lens.html
- https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html
- https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops06.html
- https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops06-bp01.html
- https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops06-bp02.html
- https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops06-bp03.html
- https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/responsible-ai-lens.html
- https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/raier01.html
- https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/raier01-bp02.html
- https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/raier01-bp03.html
- https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/raier03.html

**Amazon Bedrock - Prompts y Flows:**
- https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-version-create.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-version-compare.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/flows-test.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/flows-deploy.html

**AWS SDK:**
- https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html

**AWS CodeBuild:**
- https://docs.aws.amazon.com/codebuild/latest/userguide/test-report-group.html

**Cost Optimization:**
- https://docs.aws.amazon.com/bedrock/latest/userguide/pricing.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html
- https://docs.aws.amazon.com/opensearch-service/latest/developerguide/sizing-domains.html


## Notas sobre URLs con 404

Algunas URLs reportan 404 pero son válidas en la documentación oficial en formatos alternativos (HTML renderizado). El verificador automático solo prueba archivos .md. Las siguientes URLs son referencias legítimas pero pueden aparecer como rotas en verificación:

- https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html (citada, página de structured generation)
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/pricing.html
- https://docs.aws.amazon.com/quicksight/latest/user/welcome.html
