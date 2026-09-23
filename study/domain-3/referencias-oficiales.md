# Referencias oficiales de AWS — Domain 3

[← Volver al índice](./README.md)

Todas las páginas de `docs.aws.amazon.com` consultadas para construir la cobertura del Domain 3, agrupadas por servicio. El contenido de estas fuentes fue parafraseado y resumido en los archivos de este directorio para cumplir con restricciones de licencia.

**Total: 170 páginas oficiales.** La columna *Usado en* indica los skills que se apoyan en cada página. Todas se verifican automáticamente con `scripts/verify_study_docs.py`.

---

## Guía del examen AIP-C01

| Página | Usado en |
| --- | --- |
| [AWS Certified Generative AI Developer - Professional (AIP-C01)](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) | README |
| [Content Domain 3: AI Safety, Security, and Governance](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain3.html) | README, los 15 skills |
| [Technologies and concepts that might appear on the exam](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-technologies-concepts.html) | README |
| [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html) | README |

---

## AWS Well-Architected

### Generative AI Lens

| Página | Usado en |
| --- | --- |
| [Responsible AI](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/responsible-ai.html) | 3.3.3, marco del Task 3.4 |
| [Security](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/security.html) | 3.3.3 |
| [GENSEC02-BP01 Implement guardrails to mitigate harmful or incorrect model responses](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gensec02-bp01.html) | 3.3.3, 3.4.3 |
| [GENSEC03-BP01 Implement control plane and data access monitoring](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gensec03-bp01.html) | 3.3.3 |
| [GENOPS03-BP02 Enable tracing for agents and RAG workflows](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops03-bp02.html) | 3.3.3, 3.4.1 |

Códigos nombrados en estos materiales sin página propia consultada: GENSEC01 (BP01–BP04), GENSEC04 (BP01–BP02), GENSEC05, GENSEC06, GENOPS01 (BP01–BP02), GENOPS02 (BP01–BP03), GENOPS05.

### Agentic AI Lens

| Página | Usado en |
| --- | --- |
| [AGENTSEC04-BP01 Guardrails and alignment controls](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec04-bp01.html) | 3.4.3 |
| [AGENTSEC05 Agent observability and non-repudiation](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec05.html) | 3.4.1 |
| [AGENTSEC07-BP02 Clear confidence indicators and manipulation warnings](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec07-bp02.html) | 3.4.1 |
| [AGENTSEC08-BP02 Output filtering for sensitive information](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec08-bp02.html) | 3.4.3 |

Códigos nombrados sin página propia consultada: AGENTSEC01 a AGENTSEC09 en conjunto, AGENTOPS02-BP02 (config drift detection and remediation) y AGENTOPS05-BP03 (structured logging y audit trails). El desarrollo completo del Agentic AI Lens está en [Task 2.1 de Domain 2](../domain-2/task-2-1-agentic-ai-y-herramientas.md).

### Otros lenses y herramienta

| Página | Usado en |
| --- | --- |
| [LSREL07-BP04 Use AWS Glue Data Catalog to maintain lineage records](https://docs.aws.amazon.com/wellarchitected/latest/life-sciences-lens/lsrel07-bp04.html) | 3.3.1, discrepancia 1 |
| [Custom lenses in AWS WA Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) | 3.3.3 |

---

## AWS Prescriptive Guidance

| Página | Usado en |
| --- | --- |
| [Common prompt injection attacks](https://docs.aws.amazon.com/prescriptive-guidance/latest/llm-prompt-engineering-best-practices/common-attacks.html) | 3.1.5 |

---

## AWS AI Service Cards

Doc sets independientes con el patrón `ai/responsible-ai/<slug>/overview.html`. Ver la discrepancia 8 sobre la ausencia de índice navegable.

| Página | Usado en |
| --- | --- |
| [Amazon Bedrock Guardrails (AI Service Card)](https://docs.aws.amazon.com/ai/responsible-ai/bedrock-guardrails/overview.html) | 3.3.3, 3.4.3 |
| [Amazon Titan Image Generator (AI Service Card)](https://docs.aws.amazon.com/ai/responsible-ai/titan-image-generator/overview.html) | 3.3.3 |

---

## Amazon Bedrock Guardrails

### Visión general y políticas

| Página | Usado en |
| --- | --- |
| [Detect and filter harmful content by using Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) | Marco del Task 3.1, 3.4.3 |
| [Create your guardrail](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-components.html) | Marco del Task 3.1 |
| [Block harmful words and conversations with content filters](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-content-filters.html) | 3.1.1, 3.1.4 |
| [Block harmful images with content filters](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-mmfilter.html) | 3.1.1 |
| [Block denied topics to help remove harmful content](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-denied-topics.html) | 3.1.1 |
| [Remove a specific list of words and phrases from conversations with word filters](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-word-filters.html) | 3.1.1 |
| [Remove PII from conversations by using sensitive information filters](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html) | 3.2.2, 3.2.3, 3.3.4 |
| [Use contextual grounding check to filter hallucinations in responses](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html) | 3.1.3, 3.4.1 |
| [Detect prompt attacks with Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-prompt-attack.html) | 3.1.1, 3.1.5 |
| [Options for handling harmful content detected by Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-harmful-content-handling-options.html) | 3.1.4 |

### Tiers, idiomas y Regiones

| Página | Usado en |
| --- | --- |
| [Safeguard tiers for guardrails policies](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tiers.html) | 3.1.1, 3.1.4, 3.1.5 |
| [Languages supported by Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-supported-languages.html) | 3.1.4 |
| [Distribute guardrail inference across AWS Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region.html) | 3.1.4 |

### Uso en runtime

| Página | Usado en |
| --- | --- |
| [Use the ApplyGuardrail API in your application](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-independent-api.html) | 3.1.2, 3.1.5 |
| [Include a guardrail with the Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-converse-api.html) | 3.1.1, 3.1.2 |
| [Apply tags to user input to filter content](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html) | 3.1.3, 3.1.5 |
| [Configure streaming response behavior to filter content](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-streaming.html) | 3.1.2 |
| [Use a guardrail identifier to enforce a guardrail](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions-id.html) | 3.2.1 |

---

## Amazon Bedrock — Automated Reasoning checks

| Página | Usado en |
| --- | --- |
| [What are Automated Reasoning checks in Amazon Bedrock Guardrails?](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html) | 3.4.3 |
| [Automated Reasoning checks concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/automated-reasoning-checks-concepts.html) | 3.4.3 |
| [Create your Automated Reasoning policy](https://docs.aws.amazon.com/bedrock/latest/userguide/create-automated-reasoning-policy.html) | 3.4.3 |
| [Automated Reasoning policy best practices](https://docs.aws.amazon.com/bedrock/latest/userguide/automated-reasoning-policy-best-practices.html) | 3.4.3 |
| [Test an Automated Reasoning policy](https://docs.aws.amazon.com/bedrock/latest/userguide/test-automated-reasoning-policy.html) | 3.4.3 |
| [Address failed Automated Reasoning tests](https://docs.aws.amazon.com/bedrock/latest/userguide/address-failed-automated-reasoning-tests.html) | 3.4.3 |
| [Deploy your Automated Reasoning policy in your application](https://docs.aws.amazon.com/bedrock/latest/userguide/deploy-automated-reasoning-policy.html) | 3.4.3 |
| [Integrate Automated Reasoning checks in your application](https://docs.aws.amazon.com/bedrock/latest/userguide/integrate-automated-reasoning-checks.html) | 3.4.3 |
| [Permissions for Automated Reasoning policies with ApplyGuardrail](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrail-automated-reasoning-permissions.html) | 3.4.3 |

---

## Amazon Bedrock — Evaluación

| Página | Usado en |
| --- | --- |
| [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) | 3.1.2, 3.4.2 |
| [Creating an automatic model evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-automatic.html) | 3.4.2 |
| [Model evaluation jobs that use human workers](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-human.html) | 3.4.2 |
| [Evaluate model performance using another LLM as a judge](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-judge.html) | 3.1.2, 3.4.2 |
| [Evaluate the performance of RAG sources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html) | 3.4.2 |
| [Use metrics to understand model performance](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-metrics.html) | 3.4.2 |
| [Use metrics to understand RAG system performance](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-metrics.html) | 3.4.2 |
| [General text generation for model evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-tasks-general-text.html) | 3.1.2, 3.4.2 |
| [Create a prompt for a custom metric](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-custom-metrics-prompt-formats.html) | 3.4.2 |
| [Create a model evaluation job using custom metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-custom-metrics-create-job.html) | 3.4.2 |
| [Review model evaluation job reports and metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-report.html) | 3.4.2 |

---

## Amazon Bedrock — Knowledge Bases y agentes

| Página | Usado en |
| --- | --- |
| [Build a knowledge base by connecting to a structured data store](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-structured.html) | 3.1.2 |
| [Query a knowledge base and generate responses based off the retrieved data](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve-generate.html) | 3.3.2, 3.4.1 |
| [Knowledge bases logging](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-bases-logging.html) | 3.3.4 |
| [Track agent's step-by-step reasoning process using trace](https://docs.aws.amazon.com/bedrock/latest/userguide/trace-events.html) | 3.4.1 |
| [Implement safeguards by associating a guardrail with your agent](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-guardrail.html) | 3.1.5 |
| [Enhance agent's accuracy using advanced prompt templates](https://docs.aws.amazon.com/bedrock/latest/userguide/advanced-prompts.html) | 3.1.5 |
| [Lambda parser for agent response](https://docs.aws.amazon.com/bedrock/latest/userguide/lambda-parser.html) | 3.1.5 |
| [Use a tool to complete an Amazon Bedrock model response](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html) | 3.1.3 |
| [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html) | 3.1.3, discrepancia 5 |

---

## Amazon Bedrock — Prompt Management y Flows

| Página | Usado en |
| --- | --- |
| [Deploy a prompt to your application using versions](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-deploy.html) | 3.4.2 |
| [Build an end-to-end generative AI workflow with Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html) | 3.4.3 |
| [Deploy a flow using versions and aliases](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-deploy.html) | 3.4.2 |

---

## Amazon Bedrock — Observabilidad y auditoría

| Página | Usado en |
| --- | --- |
| [Monitor bedrock-runtime inference using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html) | 3.3.4 |
| [Monitor Amazon Bedrock Guardrails using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-guardrails-cw-metrics.html) | 3.3.4 |
| [Monitor Amazon Bedrock Agents using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-agents-cw-metrics.html) | 3.3.4 |
| [Monitor bedrock-mantle inference using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-mantle-metrics.html) | 3.3.4 |
| [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) | 3.2.1, 3.3.1, 3.3.4 |
| [Monitor Amazon Bedrock API calls using CloudTrail](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html) | 3.3.2 |
| [Monitor bedrock-mantle API calls using CloudTrail](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-cloudtrail-mantle.html) | 3.3.2 |
| [CloudTrail management events in model evaluation jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/cloudtrail-events-in-model-evaluations.html) | 3.3.2 |

---

## Amazon Bedrock — Red, protección de datos y abuso

| Página | Usado en |
| --- | --- |
| [Use interface VPC endpoints (AWS PrivateLink) with Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html) | 3.2.1 |
| [Data protection](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html) | 3.2.2 |
| [Data retention](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html) | 3.2.2 |
| [Identity and access management for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html) | 3.2.1, discrepancia 14 |
| [Amazon Bedrock abuse detection](https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html) | 3.3.4 |
| [Prompt injection security](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-injection.html) | 3.1.5 |

---

## Amazon Bedrock — API Reference

| Operación o tipo | Usado en |
| --- | --- |
| [`ApplyGuardrail`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ApplyGuardrail.html) | 3.1.2 |
| [`GuardrailPiiEntityFilter`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_GuardrailPiiEntityFilter.html) | 3.2.2 |
| [`Retrieve`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html) | 3.1.2 |
| [`RetrieveAndGenerate`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerate.html) | 3.1.2 |
| [`GenerateQuery`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_GenerateQuery.html) | 3.1.2 |
| [`InvokeAgent`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeAgent.html) | 3.4.1 |
| [`TracePart`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_TracePart.html) | 3.4.1 |
| [`Trace`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Trace.html) | 3.4.1 |
| [`ModelInvocationInput`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_ModelInvocationInput.html) | 3.4.1 |
| [`PreProcessingTrace`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_PreProcessingTrace.html) | 3.4.1 |
| [`OrchestrationTrace`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_OrchestrationTrace.html) | 3.4.1 |
| [`PostProcessingTrace`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_PostProcessingTrace.html) | 3.4.1 |
| [`CustomOrchestrationTrace`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_CustomOrchestrationTrace.html) | 3.4.1 |
| [`RoutingClassifierTrace`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RoutingClassifierTrace.html) | 3.4.1 |
| [`FailureTrace`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_FailureTrace.html) | 3.4.1 |
| [`GuardrailTrace`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_GuardrailTrace.html) | 3.4.1 |
| [`FoundationModelLifecycle`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_FoundationModelLifecycle.html) | 3.3.4 |
| [`ListCustomModels`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ListCustomModels.html) | 3.3.1 |

---

## Amazon SageMaker AI — Model cards y governance

| Página | Usado en |
| --- | --- |
| [Amazon SageMaker Model Cards](https://docs.aws.amazon.com/sagemaker/latest/dg/model-cards.html) | 3.3.1, 3.4.3 |
| [Create a model card](https://docs.aws.amazon.com/sagemaker/latest/dg/model-cards-create.html) | 3.3.1 |
| [`CreateModelCard`](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateModelCard.html) | 3.3.1 |
| [Model governance](https://docs.aws.amazon.com/sagemaker/latest/dg/governance.html) | 3.3.1 |
| [Amazon SageMaker Model Dashboard](https://docs.aws.amazon.com/sagemaker/latest/dg/model-dashboard.html) | 3.3.1 |

---

## Amazon SageMaker Clarify

> Servicio **cerrado a clientes nuevos**. Ver discrepancia 4.

| Página | Usado en |
| --- | --- |
| [Clarify availability change](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-availability-change.html) | 3.4.2, discrepancia 4 |
| [Pre-training Bias Metrics](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-measure-data-bias.html) | 3.4.2 |
| [Post-training Data and Model Bias Metrics](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-measure-post-training-bias.html) | 3.4.2, discrepancia 15 |

### Las ocho métricas pre-training

| Sigla | Página | Usado en |
| --- | --- | --- |
| CI | [Class Imbalance](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-bias-metric-class-imbalance.html) | 3.4.2 |
| DPL | [Difference in Proportions of Labels](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-true-label-imbalance.html) | 3.4.2 |
| KL | [Kullback-Leibler Divergence](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-kl-divergence.html) | 3.4.2 |
| JS | [Jensen-Shannon Divergence](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-jensen-shannon-divergence.html) | 3.4.2 |
| LP | [Lp-norm](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-lp-norm.html) | 3.4.2 |
| TVD | [Total Variation Distance](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-total-variation-distance.html) | 3.4.2 |
| KS | [Kolmogorov-Smirnov](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-kolmogorov-smirnov.html) | 3.4.2 |
| CDD | [Conditional Demographic Disparity](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-cddl.html) | 3.4.2 |

### Las trece métricas post-training

| Sigla | Página | Usado en |
| --- | --- | --- |
| DPPL | [Difference in Positive Proportions in Predicted Labels](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-dppl.html) | 3.3.4, 3.4.2 |
| DI | [Disparate Impact](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-di.html) | 3.4.2 |
| DCAcc | [Difference in Conditional Acceptance](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-dcacc.html) | 3.4.2 |
| DCR | [Difference in Conditional Rejection](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-dcr.html) | 3.4.2 |
| SD | [Specificity difference](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-sd.html) | 3.4.2 |
| RD | [Recall Difference](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-rd.html) | 3.4.2 |
| DAR | [Difference in Acceptance Rates](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-dar.html) | 3.4.2 |
| DRR | [Difference in Rejection Rates](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-drr.html) | 3.4.2 |
| AD | [Accuracy Difference](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-ad.html) | 3.4.2 |
| TE | [Treatment Equality](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-te.html) | 3.4.2 |
| CDDPL | [Conditional Demographic Disparity in Predicted Labels](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-cddpl.html) | 3.4.2 |
| FT | [Counterfactual Fliptest](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-ft.html) | 3.4.2 |
| GE | [Generalized entropy](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-ge.html) | 3.4.2 |

### Explicabilidad

| Página | Usado en |
| --- | --- |
| [Model explainability](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-explainability.html) | 3.4.2 |
| [Feature Attributions that Use Shapley Values](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-shapley-values.html) | 3.4.2 |
| [Online explainability](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-online-explainability.html) | 3.4.2 |

---

## Amazon SageMaker Model Monitor

> Servicio **cerrado a clientes nuevos**. Ver discrepancia 4.

| Página | Usado en |
| --- | --- |
| [Amazon SageMaker Model Monitor](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html) | 3.3.4 |
| [Model Monitor availability change](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-availability-change.html) | 3.3.4, discrepancia 4 |
| [Monitor model quality](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-model-quality.html) | 3.3.4 |
| [Monitor data quality](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-data-quality.html) | 3.3.4 |
| [Bias drift for models in production](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-monitor-bias-drift.html) | 3.3.4 |
| [Create a Bias Drift Baseline](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-monitor-bias-drift-baseline.html) | 3.3.4 |
| [Bias Drift Violations](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-monitor-bias-drift-violations.html) | 3.3.4 |
| [Parameters to Monitor Bias Drift](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-config-json-monitor-bias-parameters.html) | 3.3.4 |
| [Schedule Bias Drift Monitoring Jobs](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-monitor-bias-drift-schedule.html) | 3.3.4 |
| [Feature Attribution Drift](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-monitor-feature-attribution-drift.html) | 3.3.4 |

---

## Amazon Comprehend

| Página | Usado en |
| --- | --- |
| [Detecting PII entities](https://docs.aws.amazon.com/comprehend/latest/dg/how-pii.html) | 3.1.4, 3.2.2, 3.2.3 |

---

## Amazon Macie

| Página | Usado en |
| --- | --- |
| [Using managed data identifiers](https://docs.aws.amazon.com/macie/latest/user/managed-data-identifiers.html) | 3.2.2 |
| [Keyword requirements](https://docs.aws.amazon.com/macie/latest/user/managed-data-identifiers-keywords.html) | 3.2.2 |
| [Managed data identifiers recommended for sensitive data discovery jobs](https://docs.aws.amazon.com/macie/latest/user/discovery-jobs-mdis-recommended.html) | 3.2.2 |
| [Default settings for automated sensitive data discovery](https://docs.aws.amazon.com/macie/latest/user/discovery-asdd-settings-defaults.html) | 3.2.2 |

---

## AWS Lake Formation

| Página | Usado en |
| --- | --- |
| [Data filtering and cell-level security in Lake Formation](https://docs.aws.amazon.com/lake-formation/latest/dg/data-filtering.html) | 3.2.1 |

---

## AWS Glue

| Página | Usado en |
| --- | --- |
| [Data discovery and cataloging in AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html) | 3.3.1, 3.3.2 |
| [Business context in the Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/catalog-business-context.html) | 3.3.1 |
| [Metadata forms](https://docs.aws.amazon.com/glue/latest/dg/catalog-metadata-forms.html) | 3.3.1 |
| [Business glossaries](https://docs.aws.amazon.com/glue/latest/dg/catalog-business-glossaries.html) | 3.3.1 |
| [Semantic search](https://docs.aws.amazon.com/glue/latest/dg/catalog-semantic-search.html) | 3.3.1 |
| [AWS tags in AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/monitor-tags.html) | 3.3.1 |

---

## Amazon DataZone y catálogo de SageMaker

| Página | Usado en |
| --- | --- |
| [Data lineage in Amazon DataZone](https://docs.aws.amazon.com/datazone/latest/userguide/datazone-data-lineage.html) | 3.3.1, 3.3.2 |
| [Data lineage in Amazon SageMaker Unified Studio](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/datazone-data-lineage.html) | 3.3.2 |

---

## AWS Audit Manager

> Servicio **cerrado a clientes nuevos**. Ver discrepancia 11.

| Página | Usado en |
| --- | --- |
| [AWS Generative AI Best Practices Framework v2](https://docs.aws.amazon.com/audit-manager/latest/userguide/aws-generative-ai-best-practices.html) | 3.3.1, 3.3.3 |
| [AWS Audit Manager availability change](https://docs.aws.amazon.com/audit-manager/latest/userguide/audit-manager-availability-change.html) | 3.3.1, discrepancia 11 |
| [Framework overviews](https://docs.aws.amazon.com/audit-manager/latest/userguide/framework-overviews.html) | 3.3.1 |
| [Framework library](https://docs.aws.amazon.com/audit-manager/latest/userguide/framework-library.html) | 3.3.1 |
| [Review standard controls in the control library](https://docs.aws.amazon.com/audit-manager/latest/userguide/control-library-review-standard-controls.html) | 3.3.1 |

---

## Amazon CloudWatch

| Página | Usado en |
| --- | --- |
| [Help protect sensitive log data with masking](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html) | 3.2.2, 3.3.1, 3.3.4 |
| [Using CloudWatch anomaly detection](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Anomaly_Detection.html) | 3.3.4, 3.4.1 |
| [Create an anomaly detection alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Create_Anomaly_Detection_Alarm.html) | 3.3.4 |
| [Create a composite alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Create_Composite_Alarm.html) | 3.3.4 |

---

## Otros servicios

| Página | Usado en |
| --- | --- |
| [Conformance packs — AWS Config](https://docs.aws.amazon.com/config/latest/developerguide/conformance-packs.html) | 3.3.3, 3.4.3 |
| [AWS Systems Manager Automation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html) | 3.3.4 |
| [Managing the lifecycle of objects — Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html) | 3.2.2 |
| [Override your API's request and response parameters — API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-override-request-response-parameters.html) | 3.1.4 |
| [Invoke and customize Amazon Bedrock models with Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/connect-bedrock.html) | 3.1.1 |

---

## Notas sobre discrepancias encontradas en la documentación

Al construir estos materiales se detectaron **quince puntos** donde la guía del examen y la documentación oficial no encajan, donde el contenido que la guía presupone no está en `docs.aws.amazon.com`, o donde el servicio que sostiene el skill ya no está disponible para clientes nuevos. Se documentan aquí para que no se conviertan en confusión durante el estudio.

Este dominio acumula más desajustes que los dos anteriores, y la causa es estructural: **tres de los servicios que la guía nombra están cerrados a clientes nuevos** (SageMaker Clarify, SageMaker Model Monitor y AWS Audit Manager), y **dos de las capacidades que atribuye a un servicio viven en otro** (data lineage y métricas de fairness).

### 1. AWS Glue y el data lineage que no está en Glue

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **3.3.1** pide *"usando AWS Glue para rastrear data lineage automáticamente"* |
| **Qué dice la documentación** | El **AWS Glue Developer Guide no tiene ninguna página de data lineage**. Lo que Glue documenta es [Data Catalog y crawlers](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html), [business context](https://docs.aws.amazon.com/glue/latest/dg/catalog-business-context.html), [metadata forms](https://docs.aws.amazon.com/glue/latest/dg/catalog-metadata-forms.html), [business glossaries](https://docs.aws.amazon.com/glue/latest/dg/catalog-business-glossaries.html) y [tags](https://docs.aws.amazon.com/glue/latest/dg/monitor-tags.html) |
| **Dónde está entonces** | En [Amazon DataZone](https://docs.aws.amazon.com/datazone/latest/userguide/datazone-data-lineage.html) y en el [catálogo de SageMaker Unified Studio](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/datazone-data-lineage.html). Glue actúa solo como **origen capturado**: el lineage se captura automáticamente al añadir bases de datos de Glue a DataZone, y desde ejecuciones de Spark ETL en Glue 5.0 o superior. Lo único que se acerca a "Glue como registro de lineage" es [LSREL07-BP04](https://docs.aws.amazon.com/wellarchitected/latest/life-sciences-lens/lsrel07-bp04.html), del Life Sciences Lens, que propone usar el Data Catalog como registro centralizado |
| **Además** | **Amazon DataZone no figura en la lista de [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html)** del examen, aunque Amazon SageMaker Unified Studio sí |
| **Cómo tratarlo** | Estudiar lo que Glue sí aporta al skill (catálogo, crawlers, metadata forms, tags con su límite de **50 por entidad**) y el lineage por su nombre real: **OpenLineage en DataZone**, con `sourceIdentifier` y column-level lineage. Si una pregunta contrapone Glue y DataZone para lineage, DataZone es lo que la documentación respalda. Desarrollado en [Task 3.3 · Skill 3.3.2](./task-3-3-governance-y-compliance.md#skill-332--trazabilidad-y-tracking-de-fuentes-de-datos) |

### 2. Métricas de fairness predefinidas en CloudWatch

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **3.4.2** pide *"usando métricas de fairness predefinidas en Amazon CloudWatch"* |
| **Qué dice la documentación** | **CloudWatch no publica ninguna métrica de fairness.** Ni el namespace `AWS/Bedrock`, ni `AWS/Bedrock/Guardrails`, ni ningún otro namespace de los servicios de este dominio incluye una métrica de equidad |
| **Qué existe en su lugar** | En Bedrock, las métricas built-in **`Builtin.Stereotyping`** y **`Builtin.Harmfulness`** de las evaluaciones con judge model, y el dataset **BOLD** de la familia programmatic, que evalúa equidad en cinco dominios. En SageMaker, las **8 métricas pre-training** y **13 post-training** de Clarify, que Model Monitor sí escribe a CloudWatch cuando detecta drift |
| **Cómo tratarlo** | La lectura razonable del enunciado es *métricas de fairness que acaban visibles en CloudWatch*, no *métricas que CloudWatch provee*. Conocer los nombres exactos de las métricas de Bedrock y las siglas de Clarify. Desarrollado en [Task 3.4 · Skill 3.4.2](./task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness) |

### 3. Métricas de confianza e incertidumbre en CloudWatch

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **3.4.1** pide *"usando Amazon CloudWatch para recoger métricas de confianza y cuantificar incertidumbre"* |
| **Qué dice la documentación** | El catálogo de [métricas de runtime](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html) del namespace `AWS/Bedrock` cubre invocaciones, latencia, tokens, throttles, caché y `TimeToFirstToken`. **Ninguna métrica de confianza ni de incertidumbre** |
| **Qué existe en su lugar** | Tres señales de confianza que produce la plataforma y que hay que publicar uno mismo con `put_metric_data`: los **scores de grounding y relevance** del contextual grounding check, los **findings de Automated Reasoning** (`FindingCounts`, `TotalFindings`, y los resultados `VALID`/`INVALID`/`TRANSLATION_AMBIGUOUS`/`TOO_COMPLEX`), y el campo **`confidence`** de los content filters con valores `NONE`/`LOW`/`MEDIUM`/`HIGH` |
| **Cómo tratarlo** | Saber que la métrica no viene dada y que el patrón documentado es emitirla como métrica custom, y desde ahí aplicar [anomaly detection](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Anomaly_Detection.html). Desarrollado en [Task 3.4 · Skill 3.4.1](./task-3-4-ia-responsable.md#skill-341--transparencia-y-reasoning-traces) |

### 4. SageMaker Clarify y Model Monitor cerrados a clientes nuevos

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | **Amazon SageMaker Clarify** y **Amazon SageMaker Model Monitor** figuran en la lista de **In-Scope AWS Services**. El skill **3.3.4** pide *bias drift monitoring* y el **3.4.2** evaluaciones de fairness |
| **Qué dice la documentación** | Aviso literal, idéntico en ambos servicios: *ya no está abierto a clientes nuevos. Los clientes existentes pueden seguir usándolo con normalidad. AWS sigue invirtiendo en mejoras de seguridad y disponibilidad, pero no planeamos introducir funcionalidades nuevas.* Ver [Clarify availability change](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-availability-change.html) y [Model Monitor availability change](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-availability-change.html) |
| **Además** | Son el **único** anclaje documentado del bias drift monitoring y de las bias metrics. No hay sustituto equivalente en el portal: Bedrock evaluations cubre fairness de salidas de FM, pero **no calcula métricas de bias sobre un dataset tabular** |
| **Cómo tratarlo** | Conocer el vocabulario completo porque sigue en alcance: las **8 métricas pre-training** (CI, DPL, KL, JS, LP, TVD, KS, CDD), las **post-training** (DPPL, DI, DCAcc, DCR, SD, RD, DAR, DRR, AD, TE, CDDPL, FT, GE), SHAP, y la mecánica del bias drift con **intervalo de confianza bootstrap frente a rango permitido**. Para diseñar hoy la evaluación de fairness de un FM, el camino abierto es **Bedrock evaluations**. Desarrollado en [Task 3.4 · Skill 3.4.2](./task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness) y [Task 3.3 · Skill 3.3.4](./task-3-3-governance-y-compliance.md#skill-334--monitorización-continua-y-controles-avanzados) |

### 5. Structured outputs: la trampa está en las citations, no en la página

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **3.1.3** pide *"usando JSON Schema para imponer salidas estructuradas"* |
| **Qué dice la documentación** | **Sí existe página dedicada**: [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html). Documenta **dos mecanismos complementarios**: el **JSON Schema output format** (`outputConfig.textFormat` en Converse, `output_config.format` en `InvokeModel` con Claude, `response_format` en modelos open weight) y el **strict tool use** con el flag `strict: true` |
| **El desajuste real** | No es la ausencia de documentación, sino **dos incompatibilidades y un límite** que la guía no anticipa. Primero: *structured outputs es incompatible con citations en modelos de Anthropic*, y habilitar ambas devuelve **error 400**. Eso choca con la atribución de fuente que pide el skill **3.4.1**. Segundo: **no funciona con la Anthropic Messages API en el endpoint `bedrock-mantle`**, también con 400. Tercero: el subconjunto soportado es **JSON Schema Draft 2020-12 parcial**, y funcionalidades habituales como esquemas recursivos, `$ref` externas, `minimum`/`maximum` y `minLength`/`maxLength` **provocan 400 inmediato** |
| **Y el punto ciego que persiste** | El `toolSpec.inputSchema` es **uno de los campos que los guardrails no evalúan**, según la tabla oficial de [Include a guardrail with the Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-converse-api.html). Imponer estructura reduce la hallucination de **formato**, no de **contenido**, y mueve el contenido a un campo sin vigilancia |
| **Cómo tratarlo** | Conocer los tres nombres de parámetro según API, el flag `strict`, el caché de gramática de **24 horas** con compilación inicial de varios minutos, y sobre todo **la incompatibilidad con citations**. Desarrollado en [Task 3.1 · Skill 3.1.3](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-313--verificación-de-exactitud-y-reducción-de-hallucinations) |

### 6. La métrica de toxicidad existe, pero no donde se la busca

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **3.1.2** pide *"evaluaciones de FM especializadas para moderación de contenido y detección de toxicidad"* |
| **La confusión habitual** | Buscar una métrica de toxicidad entre las built-in del **judge model** y no encontrarla. En esa familia están `Builtin.Harmfulness` y `Builtin.Stereotyping`, pero **no hay ninguna llamada toxicity** |
| **Qué dice la documentación** | **La toxicidad sí existe**, en la familia **programmatic (automatic)**, calculada con el algoritmo **detoxify**. Está disponible en los task types de generación de texto general, question and answer, resumen de texto y clasificación de texto, con los datasets built-in **`Builtin.RealToxicityPrompts`** (100.000 prompts diseñados para provocar lenguaje tóxico) y **`Builtin.Bold`** (23.679 prompts en cinco dominios). Ver [General text generation for model evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-tasks-general-text.html) |
| **Aviso oficial adicional** | La documentación registra un problema conocido por el que **los modelos de Cohere no completan la evaluación de toxicidad** en la tarea de generación de texto general |
| **Cómo tratarlo** | Saber que **la familia importa**: toxicidad con detoxify es programmatic; daño y estereotipo son judge model. Si una pregunta pide medir toxicidad con un corpus estándar, la respuesta es la evaluación programmatic con `Builtin.RealToxicityPrompts`. Desarrollado en [Task 3.1 · Skill 3.1.2](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-312--seguridad-de-contenido-en-las-salidas) |

### 7. A/B testing de prompts sin página propia

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **3.4.2** pide *"Amazon Bedrock Prompt Management y Amazon Bedrock Prompt Flows para realizar A/B testing sistemático"* |
| **Qué dice la documentación** | **No hay página titulada *A/B testing*** en Bedrock. El mecanismo documentado para desplegar y comparar variantes es **versión más alias**: [Deploy a prompt using versions](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-deploy.html) y [Deploy a flow using versions and aliases](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-deploy.html) |
| **Cómo tratarlo** | El patrón defendible es: dos versiones de prompt, un job de evaluación con el **mismo dataset y el mismo evaluator model** sobre cada una, comparación de métricas, y promoción moviendo el **alias**. El alias desacopla la variante del código, igual que en la selección dinámica de modelo de [Task 1.2 · Skill 1.2.2](../domain-1/task-1-2-seleccion-y-configuracion-fm.md#skill-122--selección-dinámica-de-modelo-sin-cambiar-código). Desarrollado en [Task 3.4 · Skill 3.4.2](./task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness) |

### 8. El índice de Responsible AI y las AI Service Cards

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | Los skills **3.3.3** y **3.4.3** piden alinear con *principios de IA responsable* y documentar limitaciones |
| **Qué dice la documentación** | Las **AI Service Cards existen** en el portal como doc sets independientes con el patrón `https://docs.aws.amazon.com/ai/responsible-ai/<slug>/overview.html`, verificadas por ejemplo para [Bedrock Guardrails](https://docs.aws.amazon.com/ai/responsible-ai/bedrock-guardrails/overview.html) y [Titan Image Generator](https://docs.aws.amazon.com/ai/responsible-ai/titan-image-generator/overview.html). Pero **no hay índice navegable** que las enumere: no existe una página raíz de `ai/responsible-ai/` |
| **Consecuencia práctica** | No se puede recorrer el catálogo completo desde el portal. Hay que conocer el slug del servicio concreto |
| **Dónde sí hay marco** | Las **ocho dimensiones de IA responsable de AWS** están documentadas en [Responsible AI del Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/responsible-ai.html): Fairness, Explainability, Privacy and security, Safety, Controllability, Veracity and robustness, Governance, Transparency |
| **Cómo tratarlo** | Usar el Generative AI Lens como marco canónico de las ocho dimensiones, y entender las AI Service Cards por su función: cierran **el lado del proveedor** de la cadena de suministro de IA, mientras los **model cards** cierran el lado del deployer. Desarrollado en [Task 3.3 · Skill 3.3.3](./task-3-3-governance-y-compliance.md#skill-333--governance-organizacional) |

### 9. Lambda para chequeos de compliance automatizados

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **3.4.3** pide *"funciones Lambda para realizar chequeos de compliance automatizados"* |
| **Qué dice la documentación** | **No hay página que ligue AWS Lambda a chequeos de compliance de IA.** No existe un patrón documentado con ese nombre |
| **Qué existe en su lugar** | Tres caminos documentados: **reglas custom de AWS Config con Lambda**, empaquetadas en un [conformance pack](https://docs.aws.amazon.com/config/latest/developerguide/conformance-packs.html) con su acción de remediación; **nodos Lambda en Bedrock Flows** para comprobaciones deterministas en medio del workflow; y **Lambda como capa de post-procesamiento** en la arquitectura de defensa en profundidad |
| **Cómo tratarlo** | Reconocer el patrón arquitectónico en lugar de buscar el servicio. Es donde encajan los findings de Automated Reasoning: la Lambda recibe el veredicto y decide servir, reescribir o escalar. Desarrollado en [Task 3.4 · Skill 3.4.3](./task-3-4-ia-responsable.md#skill-343--sistemas-conformes-a-política) y [Task 3.1 · Skill 3.1.4](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-314--defensa-en-profundidad-contra-el-mal-uso-del-fm) |

### 10. El miembro citation deprecado en RetrieveAndGenerateStream

| Aspecto | Detalle |
| --- | --- |
| **Qué ocurre** | El miembro **`citation`** está **deprecado** en los eventos de streaming de `RetrieveAndGenerateStream` |
| **Qué usar** | **`generatedResponse`** junto con **`retrievedReferences`**. Ver [Query a knowledge base and generate responses](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve-generate.html) |
| **Gotcha de seguridad asociado** | En la misma página: los guardrails se aplican **al input y a la respuesta generada, no a las referencias recuperadas**. Un pasaje con contenido dañino o PII llega al usuario dentro de `retrievedReferences` **sin pasar por el filtro** |
| **Cómo tratarlo** | Usar `retrievedReferences` para la atribución de fuente, y evaluar esas referencias por separado con `ApplyGuardrail` antes de mostrarlas. Afecta a los skills **3.3.2** y **3.4.1** |

### 11. Audit Manager: el framework v1 sin soporte y el servicio cerrado a clientes nuevos

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | Los skills **3.3.1** y **3.3.3** piden frameworks de compliance y de governance organizacional. AWS Audit Manager es el único servicio de AWS con un framework prefabricado de GenAI |
| **Qué dice la documentación** | Dos avisos superpuestos. Primero: **AWS Audit Manager ya no está abierto a clientes nuevos**, ver [availability change](https://docs.aws.amazon.com/audit-manager/latest/userguide/audit-manager-availability-change.html). Segundo: el **AWS generative AI best practices framework v1 ya no está soportado** desde el **11 de junio de 2024**; las assessments existentes siguen funcionando, pero **no se pueden crear nuevas desde v1**. Solo **v2**, que añadió soporte de SageMaker AI además de Bedrock |
| **Además** | **AWS Audit Manager no figura en la lista de In-Scope AWS Services** del examen, aunque es la única fuente oficial de los ocho principios |
| **Limitación regional del framework** | Usa la operación [`ListCustomModels`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ListCustomModels.html), **soportada solo en `us-east-1` y `us-west-2`**. Por eso **no aparece evidencia de uso de modelos personalizados** en Tokio, Singapur ni Fráncfort |
| **Cómo tratarlo** | Memorizar los **ocho principios** porque son la mejor taxonomía publicada de governance de GenAI en AWS: **Responsible, Safe, Fair, Sustainable, Resilience, Privacy, Accuracy, Secure**. **No afirmar ningún recuento de controles**: la documentación agrupa los controles en control sets y delega el detalle en el [control library](https://docs.aws.amazon.com/audit-manager/latest/userguide/control-library-review-standard-controls.html), sin publicar una cifra verificable. Desarrollado en [Task 3.3 · Skill 3.3.1](./task-3-3-governance-y-compliance.md#skill-331--frameworks-de-compliance-regulatorio) |

### 12. Amazon Augmented AI cerrado a clientes nuevos

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | Amazon Augmented AI figura en la lista de **In-Scope AWS Services**, y el skill **3.3.4** pide workflows de alerta y supervisión |
| **Estado** | **Ya registrado en el Domain 2**, discrepancia 5. Ver [referencias-oficiales.md de Domain 2](../domain-2/referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación). No se duplica aquí |
| **Sustituto documentado en este dominio** | Las [evaluaciones con human workers](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-human.html) de Bedrock, que son una de las cuatro familias de evaluación. Para el human-in-the-loop de un agente, el camino es AGENTREL02-BP05 con Step Functions, desarrollado en [Task 2.1 · Skill 2.1.5](../domain-2/task-2-1-agentic-ai-y-herramientas.md#skill-215--sistemas-colaborativos-con-expertise-humana) |

### 13. Testing adversarial automatizado y safety classifiers sin página de servicio

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **3.1.5** pide *"safety classifiers"* y *"workflows de testing adversarial automatizado"* |
| **Qué dice la documentación** | **Ninguno de los dos tiene página de servicio.** [Prompt injection security](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-injection.html) delega en **AWS Prescriptive Guidance** ([Common prompt injection attacks](https://docs.aws.amazon.com/prescriptive-guidance/latest/llm-prompt-engineering-best-practices/common-attacks.html)) y en blogs y código de ejemplo |
| **Qué es el safety classifier realmente** | El **default pre-processing prompt** de un agente de Bedrock, documentado en [advanced prompts](https://docs.aws.amazon.com/bedrock/latest/userguide/advanced-prompts.html): un prompt ligero que usa un FM para **determinar si la entrada del usuario es segura de procesar**. Personalizable, y con la opción de un [parser propio en Lambda](https://docs.aws.amazon.com/bedrock/latest/userguide/lambda-parser.html) para reglas adicionales |
| **Cómo construir el testing adversarial** | Con piezas documentadas: **`ApplyGuardrail`** sobre un corpus adversarial sin gastar inferencia, **detect mode** (`action: NONE`) para medir sin bloquear, **`Builtin.RealToxicityPrompts`** como corpus oficial de 100.000 prompts, **`Builtin.Refusal`** para cuantificar el falso positivo, **`guardrailCoverage.textCharacters`** para detectar texto sin evaluar, y CI/CD para ejecutarlo en cada cambio de configuración |
| **Cómo tratarlo** | No buscar un servicio que no existe. Desarrollado en [Task 3.1 · Skill 3.1.5](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-315--detección-avanzada-de-amenazas-adversariales) |

### 14. Patrones IAM de acceso a datos para FMs sin página propia

| Aspecto | Detalle |
| --- | --- |
| **Qué dice la guía** | El skill **3.2.1** pide *"políticas IAM para imponer patrones seguros de acceso a datos"* |
| **Qué dice la documentación** | [Identity and access management for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html) es **la plantilla estándar de IAM que AWS publica para todos sus servicios**. No hay una página de *patrones seguros de acceso a datos para FMs* |
| **Qué existe en su lugar** | Los controles concretos están repartidos: **endpoint policies** del VPC endpoint (la por defecto **permite acceso completo**), **data filters** de Lake Formation, [forzar un guardrail concreto en la inferencia](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions-id.html), y las **permissions boundaries** y federación de identidad ya tratadas en Domain 2 |
| **Cómo tratarlo** | Estudiar los controles por separado en lugar de buscar una página que los unifique. El detalle más olvidado y más preguntable: **crear un interface endpoint no restringe nada por sí solo**, porque la endpoint policy por defecto permite acceso completo. Desarrollado en [Task 3.2 · Skill 3.2.1](./task-3-2-seguridad-y-privacidad-de-datos.md#skill-321--entornos-de-ia-protegidos) |

### 15. El recuento de bias metrics post-training de Clarify

| Aspecto | Detalle |
| --- | --- |
| **La inconsistencia** | La prosa de [Post-training Data and Model Bias Metrics](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-measure-post-training-bias.html) declara que Clarify proporciona **once** métricas de bias post-training. **El índice de temas de esa misma página lista trece** páginas de métrica: DPPL, DI, DCAcc, DCR, SD, RD, DAR, DRR, AD, TE, CDDPL, FT y GE |
| **Cómo tratarlo** | Conocer **las trece por su sigla**, porque las trece tienen página propia y son las que se pueden calcular. Si una pregunta pide un recuento, la cifra que **declara** AWS es **once**. Desarrollado en [Task 3.4 · Skill 3.4.2](./task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness) |

---

## Nota sobre el tier Classic de Guardrails

No es una discrepancia, es una señal a vigilar. La documentación de [Safeguard tiers](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tiers.html) **no declara el tier Classic como deprecado**, pero lo describe como *funcionalidad establecida* frente a un Standard que es "más robusto", con "soporte lingüístico más completo", que **usa cross-Region inference** y que añade **detección de prompt leakage** y soporte de dominio de código. La diferencia de alcance es grande:

| Dimensión | Standard | Classic |
| --- | --- | --- |
| Idiomas en content filters y prompt attacks | **84** | **3** |
| Idiomas en denied topics | **100** | **3** |
| Definición de denied topic | **1.000 caracteres** | **200 caracteres** |
| Detección de prompt leakage | **Sí** | **No** |
| Cross-Region inference | **Requerido** | No soportado |

La dirección es evidente, y hay una consecuencia de arquitectura que conviene tener presente: **elegir Standard obliga a cross-Region inference**, lo que mueve la evaluación del guardrail fuera de la Región de origen y puede chocar con requisitos de residencia de datos.

## Nota sobre la métrica `LegacyModelInvocations`

La métrica **`LegacyModelInvocations`** del namespace `AWS/Bedrock` cuenta las invocaciones a modelos en estado **Legacy** del ciclo de vida de los FMs, definido en [`FoundationModelLifecycle`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_FoundationModelLifecycle.html). Es el control de drift más directo del ciclo de vida del modelo: detecta que la aplicación sigue invocando algo que AWS ya marcó para retirada, antes de que la retirada ocurra.

---

## Páginas citadas de Domain 1 y Domain 2

Estos materiales enlazan a Domain 1 y Domain 2 en lugar de duplicar contenido. Las referencias completas de esas páginas están en [referencias-oficiales.md de Domain 1](../domain-1/referencias-oficiales.md) y [referencias-oficiales.md de Domain 2](../domain-2/referencias-oficiales.md). Los temas que se delegan:

| Tema | Dónde está |
| --- | --- |
| Guardrails como framework de instrucción del modelo | [Domain 1 · Task 1.6](../domain-1/task-1-6-prompt-engineering-governance.md) |
| Retrieval, chunking y arquitecturas de vector store | [Domain 1 · Task 1.4](../domain-1/task-1-4-vector-stores.md) y [Task 1.5](../domain-1/task-1-5-retrieval.md) |
| Frameworks de metadatos para atribución | [Domain 1 · Task 1.4 · Skill 1.4.2](../domain-1/task-1-4-vector-stores.md#skill-142--frameworks-de-metadatos) |
| KMS, Secrets Manager y cifrado de knowledge bases | [Domain 1 · Task 1.4](../domain-1/task-1-4-vector-stores.md) |
| Model Registry y ciclo de vida del modelo | [Domain 1 · Task 1.2 · Skill 1.2.4](../domain-1/task-1-2-seleccion-y-configuracion-fm.md#skill-124--despliegue-y-ciclo-de-vida-de-fms-personalizados) |
| Well-Architected Tool y custom lenses | [Domain 1 · Task 1.1 · Skill 1.1.3](../domain-1/task-1-1-analisis-y-diseno.md#skill-113--componentes-estandarizados-con-well-architected) |
| Salvaguardas de agente, stopping conditions y permissions boundaries | [Domain 2 · Task 2.1 · Skill 2.1.3](../domain-2/task-2-1-agentic-ai-y-herramientas.md#skill-213--workflows-con-salvaguardas-y-comportamiento-controlado) |
| Human-in-the-loop y revisión humana | [Domain 2 · Task 2.1 · Skill 2.1.5](../domain-2/task-2-1-agentic-ai-y-herramientas.md#skill-215--sistemas-colaborativos-con-expertise-humana) |
| Federación de identidad y least privilege | [Domain 2 · Task 2.3 · Skill 2.3.3](../domain-2/task-2-3-integracion-empresarial.md#skill-233--frameworks-de-acceso-seguro) |
| PrivateLink y residencia de datos entre jurisdicciones | [Domain 2 · Task 2.3 · Skill 2.3.4](../domain-2/task-2-3-integracion-empresarial.md#skill-234--soluciones-cross-environment-y-compliance-entre-jurisdicciones) |
| CI/CD, GenAI gateway y evaluación en el pipeline | [Domain 2 · Task 2.3 · Skill 2.3.5](../domain-2/task-2-3-integracion-empresarial.md#skill-235--cicd-y-arquitecturas-de-genai-gateway) |
| Observabilidad y troubleshooting con X-Ray y Logs Insights | [Domain 2 · Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#skill-256--troubleshooting-de-aplicaciones-de-fm) |
| Agentic AI Lens completo | [Domain 2 · Task 2.1](../domain-2/task-2-1-agentic-ai-y-herramientas.md) |
