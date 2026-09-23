# Task 1.1 — Analizar requisitos y diseñar soluciones GenAI

[← Volver al índice](./README.md)

Skills cubiertos: **1.1.1**, **1.1.2**, **1.1.3**.

---

## Skill 1.1.1 — Diseños arquitectónicos alineados a negocio y restricciones técnicas

> *Crear diseños arquitectónicos completos que se alineen con necesidades de negocio y restricciones técnicas específicas (por ejemplo, usando FMs apropiados, patrones de integración, estrategias de despliegue).*

### El ciclo de vida GenAI como marco de diseño

El [Generative AI lifecycle](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lifecycle.html) del Well-Architected Generative AI Lens define las fases que debe recorrer todo diseño. Cada fase se evalúa contra los seis pilares del framework.

| Fase | Foco | Decisiones que se toman aquí |
| --- | --- | --- |
| **Scoping** | Entender el problema de negocio | ¿Es GenAI relevante para este problema? ¿Un modelo off-the-shelf basta o hay que personalizar? ¿Un modelo o varios orquestados? Métricas de éxito, viabilidad técnica y organizativa, perfil de riesgo, matrices de security scoping, disponibilidad y calidad de datos. |
| **Model selection** | Elegir y adoptar el modelo | Opciones de hosting, batch vs real-time vs inference profiles, model routing, catálogo de modelos, arquitecturas de disponibilidad del modelo. Si se usa RAG, selección y disponibilidad del vector database. |
| **Model customization** | Alinear el modelo al objetivo | Prompt engineering, RAG, agents, fine-tuning, continuous pre-training, model distillation, alineación con feedback humano. Gestión de plantillas de prompts. Proceso iterativo. |
| **Development and integration** | Integrar en la aplicación | Interfaces conversacionales, catálogos de prompts, agents, knowledge bases. Conexión a bases de datos, pipelines y aplicaciones internas. Guardrails contra riesgos como la alucinación. Optimización para inferencia. APIs y UI. Testing automatizado. |
| **Deployment** | Despliegue controlado y escalado | CI/CD, uptime y resiliencia, IaC con AWS CDK, CloudFormation o Terraform, control de versiones, documentación y versionado de infraestructura para rollbacks rápidos, validación de requisitos de seguridad y privacidad. |
| **Continuous improvement** | Refinar con uso real | Monitoreo de accuracy, toxicity y coherence, feedback de usuarios, actualización del dataset, mitigación de sesgos, experimentación con nuevas técnicas. |

**Punto clave del scoping para el examen**: el Lens señala que muchos componentes introducen coste en un workload GenAI —longitud de prompts, arquitectura y patrones de acceso a datos, selección de modelo y orquestación de agents— y que ese análisis de coste pertenece a la fase de scoping, no al final.

### Decisiones arquitectónicas por pilar

El [Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html) organiza sus áreas así:

| Pilar | Qué cubre en GenAI |
| --- | --- |
| **Operational excellence** | Consistencia de la calidad de salida, monitoreo de salud operativa, trazabilidad, automatización del ciclo de vida, cuándo ejecutar customization. |
| **Security** | Proteger endpoints GenAI, mitigar salidas dañinas y *excessive agency*, monitorear y auditar eventos, asegurar prompts, remediar riesgos de model poisoning. |
| **Reliability** | Requisitos de throughput, comunicación fiable entre componentes, observabilidad, fallos elegantes, versionado de artefactos, distribución de inferencia, verificación de cómputo distribuido. |
| **Performance efficiency** | Capturar y mejorar el rendimiento del modelo, mantener niveles aceptables, optimizar recursos de cómputo, mejorar el rendimiento de recuperación de datos. |
| **Cost optimization** | Seleccionar modelos coste-optimizados, balancear coste y rendimiento de inferencia, ingeniería de prompts orientada a coste, optimizar vector stores y workflows de agents. |
| **Sustainability** | Minimizar cómputo en training, customization, hosting, procesamiento y almacenamiento; técnicas de eficiencia de modelo y arquitecturas serverless. |

### Alcance del Lens

El Lens cubre aplicaciones GenAI que usan FMs en **Amazon Bedrock** o modelos gestionados por el cliente en **Amazon SageMaker AI**, e incluye guía para construir aplicaciones de negocio con **Amazon Q**, Bedrock y SageMaker AI. Para ML tradicional en SageMaker AI, la referencia es el [Machine Learning Lens](https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/machine-learning-lens.html).

### Patrones de integración que debes reconocer

| Patrón | Servicios | Cuándo |
| --- | --- | --- |
| Inferencia síncrona directa | Bedrock `Converse` / `InvokeModel` desde Lambda tras API Gateway | Chat, Q&A, latencia baja |
| Inferencia con streaming | `ConverseStream` / `InvokeModelWithResponseStream` | UX de respuesta progresiva |
| RAG gestionado | Bedrock Knowledge Bases + `RetrieveAndGenerate` | Respuestas fundamentadas en datos propios |
| Orquestación declarativa | Bedrock Flows (nodos prompt, knowledge base, agent, Lambda, condición) | Workflows multi-paso sin código de orquestación |
| Event-driven / asíncrono | EventBridge, SQS, Step Functions, flow executions asíncronas | Cargas por lotes, procesos largos, desacoplamiento |
| Agentic | Bedrock AgentCore, tool use, AgentCore Gateway | Tareas que requieren herramientas y decisiones |

---

## Skill 1.1.2 — PoC técnicas para validar viabilidad, rendimiento y valor

> *Desarrollar implementaciones de prueba de concepto técnica para validar viabilidad, características de rendimiento y valor de negocio antes de pasar a despliegue a gran escala (por ejemplo, usando Amazon Bedrock).*

### Ruta de PoC en Amazon Bedrock

1. **Solicitar acceso a modelos** — sin acceso concedido en la Región, las llamadas fallan. Ver [Request access to models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html).
2. **Explorar en los playgrounds de la consola** — probar prompts y parámetros de inferencia sin escribir código.
3. **Comparar variantes con Prompt management** — el [prompt builder](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html) permite crear *prompt variants* (mensaje, modelo o configuración de inferencia distintos), probarlos y guardar el que mejor funcione.
4. **Probar RAG sin infraestructura** — [Chat with your document](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-chatdoc.html) permite consultar un documento sin knowledge base configurada.
5. **Medir con Amazon Bedrock evaluations** — ver tabla siguiente.
6. **Trazar coste y uso** — crear un *application inference profile* con tags para atribuir coste de las llamadas de la PoC ([inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)).

### Tipos de evaluación en Amazon Bedrock

De [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html):

| Tipo | Cómo funciona | Uso en PoC |
| --- | --- | --- |
| **Programmatic model evaluation** | Scores y métricas calculadas; dataset de prompts propio o built-in | Descartar modelos rápidamente sobre una tarea concreta |
| **Human workers** | Empleados propios o expertos de dominio puntúan y dan preferencias | Validar utilidad percibida y valor de negocio |
| **Judge model (LLM-as-a-judge)** | Un segundo LLM puntúa cada respuesta y explica el score | Escalar la evaluación cualitativa sin humanos |
| **RAG evaluation (LLM-based)** | Mide si la fuente RAG recupera información relevante y genera respuestas útiles; requiere dataset con *ground truth* | Validar la calidad del pipeline de retrieval, no solo del modelo |

Los jobs de evaluación de modelos admiten como sujeto: foundation models, modelos de Bedrock Marketplace, modelos personalizados, modelos importados, **prompt routers** y modelos con Provisioned Throughput comprado. También se puede pasar un **inference profile** como modelo a evaluar.

### Qué debe demostrar una PoC antes de escalar

- **Viabilidad**: el modelo resuelve la tarea con la calidad mínima aceptable.
- **Rendimiento**: latencia y throughput bajo carga representativa; si hay límites de cuota, evaluar Provisioned Throughput o cross-Region inference.
- **Valor de negocio**: métricas de éxito definidas en scoping, no métricas técnicas genéricas.
- **Coste proyectado**: tokens de entrada/salida por transacción, coste de embeddings e ingesta, coste del vector store.
- **Riesgo**: perfil de riesgo técnico y de negocio, y qué guardrails se necesitan.

---

## Skill 1.1.3 — Componentes estandarizados con Well-Architected

> *Crear componentes técnicos estandarizados para asegurar implementación consistente en múltiples escenarios de despliegue (por ejemplo, usando el AWS Well-Architected Framework, AWS WA Tool Generative AI Lens).*

### Cómo se obtiene el Generative AI Lens

El Generative AI Lens es un **custom lens**, no un lens nativo del AWS Well-Architected Tool. El flujo oficial es:

1. Descargar el JSON del lens desde el repositorio público [aws-samples/sample-well-architected-custom-lens](https://github.com/aws-samples/sample-well-architected-custom-lens) (archivo `generative-ai-lens/generative-ai-lens.json`).
2. Importarlo en **AWS WA Tool** como custom lens.
3. Ejecutar la revisión del workload contra el lens.

Fecha de publicación del documento del lens: **19 de noviembre de 2025**. Ver [Lens availability](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html).

### Otros lenses relacionados

| Lens | Cuándo usarlo | Enlace |
| --- | --- | --- |
| **Generative AI Lens** | Aplicaciones GenAI con FMs en Bedrock o modelos propios en SageMaker AI | [Doc](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html) |
| **Agentic AI Lens** | Diseñar, revisar u operar sistemas agénticos | [Doc](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html) |
| **Responsible AI Lens** | Governance para IA responsable y escalable | [Doc](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/responsible-ai-lens.html) |
| **Machine Learning Lens** | ML tradicional en SageMaker AI | [Doc](https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/machine-learning-lens.html) |

Los tres primeros se distribuyen como custom lenses desde el mismo repositorio de GitHub y se importan igual.

### Estandarización operativa: catálogos como fuente de verdad

Uno de los cuatro principios del pilar de **Reliability** del Lens es *standardize resource management through catalogs*: mantener catálogos centralizados de prompts y modelos para lograr acceso consistente y gobernado, con una única fuente de verdad, control de versiones y capacidad de actualización o rollback. Esto reduce el riesgo de usar recursos obsoletos. Ver [Reliability](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/reliability.html).

Traducción a servicios concretos:

| Componente estandarizado | Implementación AWS |
| --- | --- |
| Catálogo de prompts | [Bedrock Prompt Management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html) con versiones; repositorio de plantillas en S3 |
| Catálogo de modelos | [Inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html) de aplicación; [SageMaker Model Registry](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html) para modelos propios |
| Plantillas de infraestructura reutilizables | AWS CDK, CloudFormation, AWS Service Catalog |
| Políticas de seguridad de contenido reutilizables | [Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) versionados y compartidos entre aplicaciones |
| Workflows reutilizables | [Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html) con versiones inmutables y alias |

### Responsabilidad compartida en IA responsable

El Lens enfatiza las **responsabilidades compartidas entre model producers, providers y consumers**. Al diseñar, hay que documentar qué controles aporta cada parte: el proveedor del modelo, AWS como proveedor de la plataforma, y tu aplicación como consumidora.

---

## Preguntas de autoevaluación

1. ¿En qué fase del ciclo de vida GenAI se decide si un modelo off-the-shelf es suficiente o hace falta personalizarlo?
2. ¿Por qué el análisis de coste pertenece a la fase de scoping y no a deployment?
3. Necesitas validar que tu pipeline RAG recupera los chunks correctos, no solo que el modelo escribe bien. ¿Qué tipo de evaluación de Bedrock usas y qué dato extra requiere el dataset?
4. ¿El Generative AI Lens está disponible directamente en el AWS WA Tool o hay que importarlo? ¿Desde dónde?
5. ¿Qué lens aplicas si el workload es un sistema multi-agente en producción?
6. ¿Cuál es el principio de Reliability del Lens que justifica centralizar prompts y modelos en catálogos?

## Fuentes oficiales de esta sección

- [Generative AI Lens — AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html)
- [Generative AI lifecycle](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lifecycle.html)
- [Reliability (Generative AI Lens)](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/reliability.html)
- [Agentic AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html)
- [Lens Catalog for AWS WA Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lens-catalog.html)
- [Custom lenses in AWS WA Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html)
- [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html)
- [Construct and store reusable prompts with Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html)
- [Set up a model invocation resource using inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)
