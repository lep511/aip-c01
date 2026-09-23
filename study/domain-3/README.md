# Domain 3 — AI Safety, Security, and Governance

Cobertura completa del **Domain 3** del examen **AWS Certified Generative AI Developer – Professional (AIP-C01)**, construida a partir de documentación oficial de AWS (`docs.aws.amazon.com`).

> El contenido de las fuentes AWS fue parafraseado y resumido para cumplir con restricciones de licencia. Cada sección enlaza a la página oficial correspondiente.

## Datos del dominio

| Dato | Valor |
| --- | --- |
| Peso en el examen | **20 % del contenido puntuado** (tercer dominio por peso, tras el 31 % del Domain 1 y el 26 % del Domain 2) |
| Tasks | 4 |
| Skills | 15 |
| Preguntas puntuadas | 65 (más 10 no puntuadas, no identificadas) |
| Score de aprobación | 750 en escala 100–1000 |
| Modelo de scoring | Compensatorio: no hace falta aprobar cada sección, solo el examen global |

Fuentes: [Exam Guide AIP-C01](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) · [Content Domain 3](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain3.html)

## Índice de archivos

| Archivo | Task | Skills | Tema |
| --- | --- | --- | --- |
| [task-3-1-controles-de-seguridad-entrada-salida.md](./task-3-1-controles-de-seguridad-entrada-salida.md) | 3.1 | 3.1.1 – 3.1.5 | Controles de seguridad de entrada y salida |
| [task-3-2-seguridad-y-privacidad-de-datos.md](./task-3-2-seguridad-y-privacidad-de-datos.md) | 3.2 | 3.2.1 – 3.2.3 | Controles de seguridad y privacidad de datos |
| [task-3-3-governance-y-compliance.md](./task-3-3-governance-y-compliance.md) | 3.3 | 3.3.1 – 3.3.4 | Mecanismos de governance y compliance de IA |
| [task-3-4-ia-responsable.md](./task-3-4-ia-responsable.md) | 3.4 | 3.4.1 – 3.4.3 | Principios de IA responsable |
| [referencias-oficiales.md](./referencias-oficiales.md) | — | — | Todas las páginas de AWS usadas, agrupadas por servicio, más las discrepancias detectadas |

## Mapa de las 15 skills

### Task 3.1 — Implementar controles de seguridad de entrada y salida
- **3.1.1** Sistemas completos de seguridad de contenido para proteger contra entradas dañinas de usuario a los FMs (Bedrock Guardrails para filtrar contenido, Step Functions y Lambda para workflows de moderación personalizados, mecanismos de validación en tiempo real).
- **3.1.2** Frameworks de seguridad de contenido para prevenir salidas dañinas (Bedrock Guardrails para filtrar respuestas, evaluaciones de FM especializadas para moderación de contenido y detección de toxicidad, transformaciones text-to-SQL para asegurar resultados deterministas).
- **3.1.3** Sistemas de verificación de exactitud para reducir hallucinations en las respuestas del FM (Bedrock Knowledge Bases para fundamentar respuestas y hacer fact-checking, confidence scoring y búsqueda por similitud semántica para verificación, JSON Schema para imponer salidas estructuradas).
- **3.1.4** Sistemas de seguridad de defensa en profundidad para dar protección integral contra el mal uso del FM (Comprehend para filtros de pre-procesamiento, Bedrock para guardrails basados en modelo, Lambda para validación de post-procesamiento, API Gateway para filtrado de respuestas de API).
- **3.1.5** Detección avanzada de amenazas para proteger contra entradas adversariales y vulnerabilidades de seguridad (mecanismos de detección de prompt injection y jailbreak, sanitización de entrada y filtros de contenido, safety classifiers, workflows de testing adversarial automatizado).

### Task 3.2 — Implementar controles de seguridad y privacidad de datos
- **3.2.1** Entornos de IA protegidos para asegurar seguridad integral de los despliegues de FM (VPC endpoints para aislar redes, políticas IAM para imponer patrones seguros de acceso a datos, AWS Lake Formation para dar acceso granular a datos, CloudWatch para monitorizar el acceso a datos).
- **3.2.2** Sistemas que preservan la privacidad para proteger información sensible durante las interacciones con el FM (Comprehend y Macie para detectar PII, funcionalidades nativas de privacidad de datos de Bedrock, Bedrock Guardrails para filtrar salidas, configuraciones de S3 Lifecycle para implementar políticas de retención).
- **3.2.3** Sistemas de IA centrados en privacidad que protegen al usuario manteniendo la utilidad y efectividad del FM (técnicas de data masking, detección de PII de Comprehend, estrategias de anonimización, Bedrock Guardrails).

### Task 3.3 — Implementar mecanismos de governance y compliance de IA
- **3.3.1** Frameworks de compliance para asegurar cumplimiento regulatorio de los despliegues de FM (SageMaker AI para desarrollar model cards programáticas, AWS Glue para rastrear data lineage automáticamente, metadata tagging para atribución sistemática de fuente de datos, CloudWatch Logs para recoger decision logs completos).
- **3.3.2** Tracking de fuentes de datos para mantener trazabilidad en aplicaciones GenAI (AWS Glue Data Catalog para registrar fuentes de datos, metadata tagging para atribución de fuente en contenido generado por el FM, CloudTrail para audit logging).
- **3.3.3** Sistemas de governance organizacional para asegurar supervisión consistente de las implementaciones de FM (frameworks completos que alinean políticas organizacionales, requisitos regulatorios y principios de IA responsable).
- **3.3.4** Monitorización continua y controles avanzados de governance para soportar auditorías de seguridad y preparación regulatoria (detección automatizada de misuse, drift y violaciones de política; bias drift monitoring; workflows automatizados de alerta y remediación; token-level redaction; response logging; filtros de política de salida de IA).

### Task 3.4 — Implementar principios de IA responsable
- **3.4.1** Sistemas de IA transparentes en las salidas del FM (reasoning displays para dar explicaciones de cara al usuario, CloudWatch para recoger métricas de confianza y cuantificar incertidumbre, presentación de evidencia para atribución de fuente, agent tracing de Bedrock para dar reasoning traces).
- **3.4.2** Evaluaciones de fairness para asegurar salidas del FM sin sesgo (métricas de fairness predefinidas en CloudWatch, Bedrock Prompt Management y Bedrock Prompt Flows para A/B testing sistemático, Bedrock con soluciones LLM-as-a-judge para evaluaciones automatizadas de modelo).
- **3.4.3** Sistemas conformes a política para asegurar adherencia a prácticas de IA responsable (Bedrock Guardrails basados en requisitos de política, model cards para documentar limitaciones del FM, Lambda para chequeos de compliance automatizados).

## Relación con el Domain 1 y el Domain 2

El Domain 1 cubre **cómo integrar un FM y alimentarlo con datos**, el Domain 2 **cómo llevarlo a producción en una empresa**, y el Domain 3 **cómo impedir que haga daño y demostrar que no lo hizo**. Los temas se solapan, y estos archivos enlazan en lugar de duplicar:

| Tema | Dónde está la base | Qué añade el Domain 3 |
| --- | --- | --- |
| Guardrails como framework de IA responsable | [Task 1.6 · Skill 1.6.1](../domain-1/task-1-6-prompt-engineering-governance.md#skill-161--frameworks-de-instrucción-del-modelo) | Las seis políticas al detalle, con sus cuotas, tiers y puntos ciegos (3.1.1 – 3.1.4, 3.4.3) |
| Guardrails como salvaguarda de agente | [Task 2.1 · Skill 2.1.3](../domain-2/task-2-1-agentic-ai-y-herramientas.md#skill-213--workflows-con-salvaguardas-y-comportamiento-controlado) | Prompt injection, jailbreak y testing adversarial (3.1.5) |
| Auditoría de prompts con CloudTrail y CloudWatch Logs | [Task 1.6 · Skill 1.6.3](../domain-1/task-1-6-prompt-engineering-governance.md#skill-163--gestión-y-governance-de-prompts) | Data events por tipo de recurso y decision logs auditables (3.3.1, 3.3.2) |
| Retrieval y fundamentación de respuestas | [Task 1.5 · Skill 1.5.4](../domain-1/task-1-5-retrieval.md#skill-154--arquitecturas-de-búsqueda-avanzada) | Contextual grounding check y atribución de fuente verificable (3.1.3, 3.4.1) |
| Comprehend para procesar la entrada | [Task 1.3 · Skill 1.3.4](../domain-1/task-1-3-datos-para-consumo-fm.md#skill-134--mejorar-la-calidad-de-la-entrada) | Detección y redacción de PII como capa de pre-procesamiento (3.1.4, 3.2.2, 3.2.3) |
| PrivateLink y residencia de datos | [Task 2.3 · Skill 2.3.4](../domain-2/task-2-3-integracion-empresarial.md#skill-234--soluciones-cross-environment-y-compliance-entre-jurisdicciones) | Los cinco sufijos de VPC endpoint de Bedrock y el aislamiento del plano de datos (3.2.1) |
| Federación de identidad y least privilege | [Task 2.3 · Skill 2.3.3](../domain-2/task-2-3-integracion-empresarial.md#skill-233--frameworks-de-acceso-seguro) | Acceso granular a datos con Lake Formation (3.2.1) |
| Observabilidad y troubleshooting de FM | [Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#skill-256--troubleshooting-de-aplicaciones-de-fm) | Las tres listas de métricas de `AWS/Bedrock` y la detección de drift (3.3.4) |
| Human-in-the-loop y revisión humana | [Task 2.1 · Skill 2.1.5](../domain-2/task-2-1-agentic-ai-y-herramientas.md#skill-215--sistemas-colaborativos-con-expertise-humana) | Evaluaciones con human workers como sustituto documentado de A2I (3.3.4) |
| Evaluación de recursos de Bedrock | [Task 2.3 · Skill 2.3.5](../domain-2/task-2-3-integracion-empresarial.md#skill-235--cicd-y-arquitecturas-de-genai-gateway) | Las tres familias de evaluación y los IDs `Builtin.*` de fairness (3.4.2) |
| Versiones y alias de prompts y flows | [Task 1.6 · Skill 1.6.4](../domain-1/task-1-6-prompt-engineering-governance.md#skill-164--aseguramiento-de-calidad-de-prompts) | Versión más alias como mecanismo real de A/B testing (3.4.2) |
| Model Registry y ciclo de vida del modelo | [Task 1.2 · Skill 1.2.4](../domain-1/task-1-2-seleccion-y-configuracion-fm.md#skill-124--despliegue-y-ciclo-de-vida-de-fms-personalizados) | Model cards programáticas, risk rating y versionado inmutable (3.3.1, 3.4.3) |

## Relación con el Domain 4

El [Domain 4 — Operational Efficiency and Optimization for GenAI Applications](../domain-4/README.md) (12 %) comparte con este dominio toda la capa de observabilidad, pero con otro propósito: aquí se mide **para demostrar que no hubo daño**, y allí **para saber qué cuesta y qué tarda**. La misma métrica sirve a las dos lecturas:

| Tema | Base en el Domain 3 | Qué añade el Domain 4 |
| --- | --- | --- |
| Los tres namespaces de métricas de Bedrock | [Task 3.3 · Skill 3.3.4](./task-3-3-governance-y-compliance.md#los-tres-namespaces-de-métricas) | Un **cuarto namespace**, `AWS/Bedrock/KnowledgeBases`, con `TotalIterationCount` y la publicación best effort que falla en silencio ([4.3.5](../domain-4/task-4-3-herramientas-vector-stores-y-fallos.md#skill-435--gestión-operativa-del-vector-store)) |
| Métricas de token y cuota TPM | [Task 3.3 · Skill 3.3.4](./task-3-3-governance-y-compliance.md#métricas-de-runtime) | La asimetría de la caché como palanca de coste y de throughput ([4.1.1](../domain-4/task-4-1-costes-y-eficiencia-de-recursos.md#skill-411--sistemas-de-eficiencia-de-tokens)) |
| Anomaly detection sin umbral fijo | [Task 3.3 · Skill 3.3.4](./task-3-3-governance-y-compliance.md#detección-de-drift-sin-umbral-fijo) | Sobre qué métrica aplicarla: tokens **por invocación**, no totales, y el contraste con AWS Cost Anomaly Detection ([4.3.2](../domain-4/task-4-3-observabilidad-y-metricas.md#skill-432--monitorización-proactiva-y-kpis-específicos-de-fm)) |
| Los siete tipos de trace de agente | [Task 3.4 · Skill 3.4.1](./task-3-4-ia-responsable.md#los-siete-tipos-de-trace) | El `rationale` como reasoning path para diagnosticar errores lógicos, y `callerChain` para atribuir latencia y coste ([4.3.6](../domain-4/task-4-3-herramientas-vector-stores-y-fallos.md#skill-436--troubleshooting-de-modos-de-fallo-propios-de-genai)) |
| Métricas de confianza que no existen | [Task 3.4 · Skill 3.4.1](./task-3-4-ia-responsable.md#métricas-de-confianza-e-incertidumbre) | El mismo patrón en tres de los cuatro KPIs del skill 4.3.2, y el **margen sobre el umbral** de grounding como señal que anticipa la degradación ([4.3.2](../domain-4/task-4-3-observabilidad-y-metricas.md#skill-432--monitorización-proactiva-y-kpis-específicos-de-fm)) |
| Las familias de evaluación de Bedrock | [Task 3.4 · Skill 3.4.2](./task-3-4-ia-responsable.md#las-métricas-de-rag-que-no-son-las-mismas) | `Faithfulness` frente a `Correctness` frente a `CitationCoverage` como diagnóstico diferencial de hallucination ([4.3.6](../domain-4/task-4-3-herramientas-vector-stores-y-fallos.md#skill-436--troubleshooting-de-modos-de-fallo-propios-de-genai)) |
| Contextual grounding check | [Task 3.1 · Skill 3.1.3](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-313--verificación-de-exactitud-y-reducción-de-hallucinations) | Su score como base de la tasa de hallucination monitorizable ([4.3.2](../domain-4/task-4-3-observabilidad-y-metricas.md#skill-432--monitorización-proactiva-y-kpis-específicos-de-fm)) |
| Model invocation logging como audit trail | [Task 3.2 · Skill 3.2.1](./task-3-2-seguridad-y-privacidad-de-datos.md#skill-321--entornos-de-ia-protegidos) | El mismo logging habilitado para observar pone prompts completos en un log group: enmascarar deja de ser opcional ([4.3.3](../domain-4/task-4-3-observabilidad-y-metricas.md#skill-433--observabilidad-integrada-y-accionable)) |
| Versiones y alias de prompts | [Task 3.4 · Skill 3.4.2](./task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness) | El mismo mecanismo aplicado a A/B testing de rendimiento, con `requestMetadata` para atribuir ([4.2.4](../domain-4/task-4-2-retrieval-y-parametros.md#skill-424--rendimiento-del-fm-y-configuración-de-parámetros)) |

## Servicios en alcance más relevantes para este dominio

Del listado oficial de [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html), los que aparecen de forma directa en los skills del Domain 3:

- **Machine Learning**: Amazon Bedrock (Guardrails, Knowledge Bases, Prompt Management, Prompt Flows, Agents, evaluaciones), Amazon Comprehend, Amazon SageMaker AI, **Amazon SageMaker Clarify**, **Amazon SageMaker Model Monitor**, Amazon SageMaker Unified Studio, Amazon Augmented AI, Amazon Rekognition.
- **Security, Identity, and Compliance**: IAM, IAM Identity Center, IAM Access Analyzer, **Amazon Macie**, AWS KMS, AWS Secrets Manager, AWS WAF, Amazon Cognito, AWS Encryption SDK.
- **Management and Governance**: **AWS CloudTrail**, **Amazon CloudWatch**, **Amazon CloudWatch Logs**, AWS Systems Manager, AWS Well-Architected Tool, AWS Service Catalog, AWS Chatbot.
- **Analytics**: **AWS Glue**, Amazon Athena, Amazon EMR, Amazon OpenSearch Service.
- **Networking and Content Delivery**: **Amazon VPC**, **AWS PrivateLink**, Amazon API Gateway, AWS AppSync, Amazon CloudFront.
- **Application Integration**: AWS Step Functions, Amazon EventBridge, Amazon SNS, Amazon SQS.
- **Compute**: AWS Lambda.
- **Storage**: **Amazon S3**, **Amazon S3 Lifecycle policies**, Amazon S3 Intelligent-Tiering, Amazon S3 Cross-Region Replication.
- **Developer Tools**: AWS CloudFormation, AWS CDK, AWS Tools and SDKs, AWS X-Ray.

Tres servicios centrales de este dominio **no figuran en la lista de In-Scope Services** aunque su documentación es la única que cubre los skills: **AWS Lake Formation** (nombrado literalmente en el skill 3.2.1), **AWS Audit Manager** y **Amazon DataZone**. Quedan registrados en [referencias-oficiales.md](./referencias-oficiales.md).

## Conceptos transversales del examen

De [Technologies and concepts](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-technologies-concepts.html), los que se concentran en Domain 3: **responsible AI practices**, **content safety and moderation**, **security and governance for AI applications**, model evaluation and validation, monitoring and observability for AI systems, y event-driven architectures para los workflows de alerta y remediación.

## Advertencia sobre lo que la guía nombra y la documentación no respalda

Este dominio es el que acumula más desajustes entre el enunciado de los skills y lo que existe en `docs.aws.amazon.com`. Se documentan **doce discrepancias** en [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación). Las cuatro que más afectan al estudio:

| Discrepancia | Impacto |
| --- | --- |
| La guía atribuye el **data lineage a AWS Glue**, pero el Glue Developer Guide no tiene ninguna página de lineage. El lineage vive en Amazon DataZone y en el catálogo de SageMaker | 3.3.1 |
| **SageMaker Clarify y SageMaker Model Monitor están cerrados a clientes nuevos**, y son justo el anclaje del *bias drift monitoring* que pide el skill | 3.3.1, 3.3.4, 3.4.2 |
| Las **métricas de fairness predefinidas en CloudWatch** no existen. En Bedrock las palancas reales son `Builtin.Stereotyping` y `Builtin.Harmfulness` de las evaluaciones | 3.4.2 |
| El namespace `AWS/Bedrock` **no publica ninguna métrica de confianza ni de incertidumbre**. Hay que emitirla con `PutMetricData` o derivarla de los scores de contextual grounding | 3.4.1 |

Y tres puntos ciegos de seguridad que la propia documentación admite, desarrollados en su skill correspondiente:

1. Los guardrails **no evalúan los campos de tool use**: ni `toolUse.input`, ni `toolResult`, ni `toolSpec`. Lo que el modelo escribe en argumentos de herramienta no se filtra ni se enmascara.
2. Con `InvokeModel`, el filtro de prompt attack **solo actúa si el input de usuario va envuelto en input tags**. Sin tags, no filtra.
3. En `RetrieveAndGenerate`, los guardrails cubren la entrada y la respuesta generada, **no las referencias recuperadas**.

## Verificar estos materiales

El repositorio incluye un verificador que comprueba que toda URL oficial citada sigue viva, que los enlaces relativos y sus anclas resuelven, que no hay bloques de código de shell y que cada task documenta los skills que declara:

```python
# uv run python scripts/verify_study_docs.py study/domain-3
# uv run python scripts/verify_study_docs.py study --no-network
```
