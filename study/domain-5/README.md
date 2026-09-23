# Domain 5 — Testing, Validation, and Troubleshooting

Cobertura completa del **Domain 5** del examen **AWS Certified Generative AI Developer – Professional (AIP-C01)**, construida a partir de documentación oficial de AWS (`docs.aws.amazon.com`).

> El contenido de las fuentes AWS fue parafraseado y resumido para cumplir con restricciones de licencia. Cada sección enlaza a la página oficial correspondiente.

## Datos del dominio

| Dato | Valor |
| --- | --- |
| Peso en el examen | **11 % del contenido puntuado** (el dominio con menor peso, tras el 31 % del Domain 1, el 26 % del Domain 2, el 20 % del Domain 3 y el 12 % del Domain 4) |
| Tasks | 2 |
| Skills | 14 |
| Preguntas puntuadas | 65 (más 10 no puntuadas, no identificadas) |
| Score de aprobación | 750 en escala 100–1000 |
| Modelo de scoring | Compensatorio: no hace falta aprobar cada sección, solo el examen global |

Fuentes: [Exam Guide AIP-C01](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) · [Content Domain 5](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain5.html)

## Índice de archivos

| Archivo | Task | Skills | Tema |
| --- | --- | --- | --- |
| [task-5-1-frameworks-y-herramientas.md](./task-5-1-frameworks-y-herramientas.md) | 5.1 | 5.1.1, 5.1.2, 5.1.3, 5.1.5 | Frameworks de evaluación: modelo-como-evaluador, ground-truth, datasets, métricas de RAG |
| [task-5-1-retrieval-y-agentes.md](./task-5-1-retrieval-y-agentes.md) | 5.1 | 5.1.4, 5.1.6, 5.1.7, 5.1.8, 5.1.9 | Validación de retrieval, agentic workflows, AgentCore, user simulation, drift |
| [task-5-2-monitoreo-troubleshooting-optimizacion.md](./task-5-2-monitoreo-troubleshooting-optimizacion.md) | 5.2 | 5.2.1, 5.2.2, 5.2.3, 5.2.4, 5.2.5 | Canaries, alarmas, traces, troubleshooting en producción, optimización post-despliegue |
| [referencias-oficiales.md](./referencias-oficiales.md) | — | — | Inventario completo de URLs oficiales de AWS usadas como fuente |

## Skill map

Este dominio cubre **14 skills** organizados en **2 tasks statement**:

### Task 5.1: Test and validate generative AI solutions (9 skills)

1. **5.1.1** — Configurar evaluaciones con modelo-como-evaluador  
   → Cobertura: builtin judges (11), custom judges, task types (QA, RAG, Summarization, Classification), AgentCore Evaluations (online, on-demand, batch)

2. **5.1.2** — Seleccionar datasets y métricas de evaluación  
   → Cobertura: Amazon Bedrock datasets (JSONL, S3), métricas builtin (accuracy, robustness, toxicity, relevance), custom metrics

3. **5.1.3** — Evaluar outputs vs ground-truth  
   → Cobertura: similarity metrics, completitud, correctness, feedback loops (humano, sintético)

4. **5.1.4** — Diagnosticar problemas de retrieval  
   → Cobertura: chunk relevance, semantic search quality, kNN troubleshooting, parsing y chunking issues

5. **5.1.5** — Evaluar métricas de RAG  
   → Cobertura: context relevance, context coverage, faithfulness, answer relevance, Knowledge Base Evaluation (2 tipos)

6. **5.1.6** — Evaluar agentic workflows con traces  
   → Cobertura: AWS X-Ray integration, spans, subsegments, service maps, trace analysis

7. **5.1.7** — Evaluar respuestas de agentes con AgentCore  
   → Cobertura: AgentCore Evaluations (online/on-demand/batch), task completion, reasoning quality, hallucinations

8. **5.1.8** — Configurar user simulation  
   → Cobertura: canaries vs simulación, workflows de evaluación automatizados, test datasets sintéticos

9. **5.1.9** — Diagnosticar drift en comportamiento  
   → Cobertura: semantic drift detection, prompt drift, output consistency, version control

### Task 5.2: Monitor, troubleshoot, and optimize generative AI solutions (5 skills)

1. **5.2.1** — Crear canaries sintéticos  
   → Cobertura: CloudWatch Synthetics, blueprints, custom canaries, métricas de disponibilidad

2. **5.2.2** — Configurar alarmas y dashboards  
   → Cobertura: CloudWatch Alarms (composite, anomaly-based), QuickSight dashboards, EventBridge integration

3. **5.2.3** — Analizar traces distribuidos  
   → Cobertura: AWS X-Ray traces, service maps, analytics console, latency profiling, error analysis

4. **5.2.4** — Troubleshooting de errores en producción  
   → Cobertura: stopReason analysis (9 valores), API errors (ThrottlingException, ValidationException), CloudWatch Logs anomaly detection

5. **5.2.5** — Optimizar post-despliegue  
   → Cobertura: token burndown analysis, latency optimization, cost reduction, capacity planning

## Relaciones con otros dominios

### Con Domain 1 (Design and Architecture)

- **5.1.4** valida decisiones de chunking y embedding de **1.4** (Data preparation)
- **5.1.5** evalúa configuración RAG definida en **1.5** (Retrieval strategies)
- **5.1.9** detecta desvíos en prompt templates de **1.6** (Prompt engineering)

### Con Domain 2 (Deployment and Automation)

- **5.2.1** implementa canaries para workflows de **2.1** (Agentic AI)
- **5.2.3** analiza traces de integraciones de **2.3** (Enterprise integration)
- **5.2.4** diagnostica errores en APIs de **2.4** (API integration)

### Con Domain 3 (Security, Governance, and Responsible AI)

- **5.2.2** monitorea violaciones de guardrails de **3.1** (Input/output controls)
- **5.2.4** troubleshooting incluye análisis de controles IAM de **3.2** (Data security)

### Con Domain 4 (Optimization and Performance)

- **5.2.5** aplica optimizaciones basadas en métricas de **4.2** (Latency/throughput) y **4.3** (Observability)
- **5.1.2** evalúa métricas de calidad vs. costo de **4.1** (Cost efficiency)

## Servicios AWS en scope

### Evaluación y Validación
- **Amazon Bedrock** (Model Evaluation, Knowledge Base Evaluation, AgentCore Evaluations)
- **Amazon SageMaker** (Model Monitor, Clarify, Ground Truth)
- **AWS Lambda** (simulación de usuarios)

### Monitoreo y Observabilidad
- **Amazon CloudWatch** (Logs, Metrics, Alarms, Synthetics)
- **AWS X-Ray** (distributed tracing, service maps, analytics)
- **Amazon QuickSight** (dashboards operacionales)
- **AWS CloudTrail** (auditoría de llamadas API)

### Almacenamiento y Búsqueda
- **Amazon OpenSearch Service** (monitoreo kNN, diagnóstico)
- **Amazon S3** (datasets de evaluación, logs)

### Infraestructura
- **Amazon EventBridge** (orquestación de canaries)
- **AWS Step Functions** (workflows de evaluación)
- **AWS Systems Manager** (runbooks)

## Conceptos transversales

### Testing y Validación
- **Model-as-a-Judge**: builtin judges (11), custom judges, task types (QA, RAG, Summarization, Classification)
- **Ground-truth evaluation**: similarity, exactitud, completitud
- **Métricas RAG**: context relevance, context coverage, faithfulness, answer relevance
- **Agent evaluation**: AgentCore (online, on-demand, batch), task completion, reasoning quality
- **User simulation**: canaries vs. simulación, workflows automatizados

### Troubleshooting
- **Análisis de traces**: AWS X-Ray spans, subsegments, annotations, service maps
- **Diagnóstico de retrieval**: chunk relevance, semantic drift, kNN performance
- **Análisis de errores**: stopReason (9 valores), ThrottlingException, ValidationException, model errors
- **Root cause analysis**: service maps, anomaly detection, filter patterns

### Optimización Post-Despliegue
- **Token burndown analysis**: optimize inference cost, reduce prompt size
- **Latency profiling**: P50/P90/P99, identify bottlenecks
- **Error rate tracking**: 4xx/5xx, model errors, timeout analysis
- **Capacity planning**: TPS limits, burst capacity, scaling strategies

### Observabilidad
- **Metrics**: latency, throughput, error rate, token consumption
- **Logs**: structured logging, filter patterns, anomaly detection
- **Traces**: distributed tracing, end-to-end visibility, X-Ray integration
- **Alarms**: composite alarms, anomaly-based, threshold-based, EventBridge integration
