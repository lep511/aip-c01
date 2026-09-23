# Task 3.4 — Principios de IA responsable

[← Volver al índice](./README.md)

Skills cubiertos: **3.4.1**, **3.4.2**, **3.4.3**.

Las ocho dimensiones de IA responsable de AWS están en el [Skill 3.3.3](./task-3-3-governance-y-compliance.md#skill-333--governance-organizacional). Este task implementa cuatro de ellas: **Transparency** y **Explainability** en 3.4.1, **Fairness** en 3.4.2, y **Veracity and robustness** en 3.4.3.

---

## Skill 3.4.1 — Transparencia y reasoning traces

> *Desarrollar sistemas de IA transparentes en las salidas del FM (por ejemplo, usando reasoning displays para dar explicaciones de cara al usuario, Amazon CloudWatch para recoger métricas de confianza y cuantificar incertidumbre, presentación de evidencia para atribución de fuente, agent tracing de Amazon Bedrock para dar reasoning traces).*

### El trace de un agente

De [Track agent's step-by-step reasoning process using trace](https://docs.aws.amazon.com/bedrock/latest/userguide/trace-events.html). **Cada respuesta de un agente de Bedrock viene acompañada de un trace** que detalla los pasos orquestados, y permite seguir el proceso de razonamiento que llevó a esa respuesta.

Lo que expone: las **entradas** a los action groups que el agente invoca y a las knowledge bases que consulta, las **salidas** que devuelven, el **razonamiento** con el que el agente decidió la acción o la consulta, y **la razón del fallo** si un paso falla.

### Los siete tipos de trace

Se activa con **`enableTrace`** en [`InvokeAgent`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeAgent.html). Cada `chunk` del stream lleva un campo `trace` que mapea a un [`TracePart`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_TracePart.html), y dentro hay un [`Trace`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Trace.html) que puede ser de uno de estos tipos:

| Tipo | Qué traza |
| --- | --- |
| [**`PreProcessingTrace`**](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_PreProcessingTrace.html) | El paso de pre-procesamiento, donde el agente **contextualiza y categoriza la entrada del usuario y determina si es válida** |
| [**`OrchestrationTrace`**](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_OrchestrationTrace.html) | El paso de orquestación: interpreta la entrada, invoca action groups y consulta knowledge bases |
| [**`PostProcessingTrace`**](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_PostProcessingTrace.html) | Cómo el agente maneja la salida final de la orquestación y decide cómo devolver la respuesta |
| [**`CustomOrchestrationTrace`**](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_CustomOrchestrationTrace.html) | El paso de orquestación personalizada, donde el agente determina **el orden de ejecución** de las acciones |
| [**`RoutingClassifierTrace`**](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RoutingClassifierTrace.html) | La entrada y salida del **clasificador de enrutado** |
| [**`FailureTrace`**](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_FailureTrace.html) | La razón por la que un paso falló |
| [**`GuardrailTrace`**](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_GuardrailTrace.html) | Las acciones del guardrail |

> **Dato decisivo**: son **siete** tipos, y **todos salvo `FailureTrace` contienen un objeto [`ModelInvocationInput`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_ModelInvocationInput.html)**. `FailureTrace` es la excepción porque describe un fallo, no una invocación.

El `TracePart` que envuelve todo trae los campos de identidad, y uno merece atención especial:

| Campo | Contenido |
| --- | --- |
| `agentId`, `agentName`, `agentVersion`, `agentAliasId` | Identidad del agente que publica el trace |
| `sessionId` | Identificador de la sesión |
| **`collaboratorName`** | Si la **colaboración multi-agente** está habilitada, el nombre del agente colaborador |
| **`callerChain`** | **Lista de llamantes entre el agente que publicó el trace y el usuario final** |

> **Dato decisivo para trazabilidad multi-agente**: con un solo agente, `callerChain` contiene el ARN de alias **de ese mismo agente**. Con colaboración multi-agente habilitada, contiene los ARN de alias de **todos los agentes que reenviaron la petición del usuario final** hasta el agente actual. Es la cadena de custodia de la decisión, y lo que permite el *non-repudiation* que pide AGENTSEC05.

### Lo que hay dentro de `ModelInvocationInput`

| Campo | Contenido |
| --- | --- |
| `traceId` | Identificador único del trace |
| `text` | **El texto del prompt que se pasó al agente en este paso** |
| **`type`** | `PRE_PROCESSING`, `ORCHESTRATION`, `ROUTING_CLASSIFIER`, `KNOWLEDGE_BASE_RESPONSE_GENERATION`, `POST_PROCESSING` |
| `foundationModel` | El FM del agente colaborador. **Solo se rellena si `type` es `ROUTING_CLASSIFIER`** |
| `inferenceConfiguration` | `maximumLength`, `stopSequences`, `temperature`, `topK`, `topP` |
| **`promptCreationMode`** | `DEFAULT` u **`OVERRIDDEN`**: si se sobrescribió la plantilla base del prompt |
| **`parserMode`** | `DEFAULT` u **`OVERRIDDEN`**: si se sobrescribió el parser de respuesta |
| `overrideLambda` | ARN de la función Lambda parser, si se sobrescribió el parser por defecto |

Y la salida, `modelInvocationOutput`, es donde está el razonamiento utilizable:

```python
# Estructura de modelInvocationOutput dentro de un trace.
{
    "metadata": {"usage": {"inputToken": 0, "outputToken": 0}},
    "rawResponse": {"content": "..."},
    "parsedResponse": {
        # Si el paso considero la entrada valida.
        "isValid": True,
        # El razonamiento del agente: esto es el "reasoning display".
        "rationale": "...",
    },
    "traceId": "...",
}
```

> **Dato decisivo**: el campo **`rationale`** vive dentro de **`parsedResponse`**, no en la raíz del trace, y es lo que materializa el *reasoning display* que pide el skill. El campo **`isValid`** del `PreProcessingTrace` es el veredicto del safety classifier visto en [Task 3.1 · Skill 3.1.5](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-315--detección-avanzada-de-amenazas-adversariales).

> **Gotcha de transparencia**: `promptCreationMode` y `parserMode` con valor `OVERRIDDEN` revelan que la plantilla o el parser por defecto fueron sustituidos. En una auditoría, eso es exactamente lo que hay que poder demostrar: si el comportamiento del agente viene del default de AWS o de una personalización propia.

```python
import boto3

agent_runtime = boto3.client("bedrock-agent-runtime")

respuesta = agent_runtime.invoke_agent(
    agentId="AGENT123",
    agentAliasId="ALIAS123",
    sessionId="sesion-usuario-42",
    inputText="¿Puedo cancelar mi poliza sin penalizacion?",
    # Sin enableTrace no hay reasoning trace en la respuesta.
    enableTrace=True,
)

for evento in respuesta["completion"]:
    if "trace" not in evento:
        continue

    parte = evento["trace"]
    traza = parte["trace"]

    # La cadena de custodia: con multi-agente lista todos los agentes
    # que reenviaron la peticion hasta este.
    cadena = [c["agentAliasArn"] for c in parte.get("callerChain", [])]

    for nombre in (
        "preProcessingTrace",
        "orchestrationTrace",
        "postProcessingTrace",
        "customOrchestrationTrace",
        "routingClassifierTrace",
        "guardrailTrace",
        # failureTrace es el unico sin modelInvocationInput.
        "failureTrace",
    ):
        if nombre not in traza:
            continue

        paso = traza[nombre]
        entrada = paso.get("modelInvocationInput", {})
        salida = paso.get("modelInvocationOutput", {})
        parseada = salida.get("parsedResponse", {})

        print(
            nombre,
            "| tipo:", entrada.get("type"),
            "| prompt propio:", entrada.get("promptCreationMode") == "OVERRIDDEN",
            "| valido:", parseada.get("isValid"),
            "| razonamiento:", parseada.get("rationale"),
            "| llamantes:", cadena,
        )
```

### Presentación de evidencia para atribución de fuente

Ya desarrollado en [Task 3.3 · Skill 3.3.2](./task-3-3-governance-y-compliance.md#skill-332--trazabilidad-y-tracking-de-fuentes-de-datos): `retrievedReferences` de `RetrieveAndGenerate`, con el miembro `citation` deprecado en streaming, y el recordatorio de que **los guardrails no cubren las referencias recuperadas**, así que la evidencia que se muestra al usuario hay que evaluarla por separado.

### Métricas de confianza e incertidumbre

> **Discrepancia 3**: el skill pide *CloudWatch para recoger métricas de confianza y cuantificar incertidumbre*, pero el namespace **`AWS/Bedrock` no publica ninguna métrica de confianza ni de incertidumbre**. Su catálogo, listado en [Task 3.3 · Skill 3.3.4](./task-3-3-governance-y-compliance.md#skill-334--monitorización-continua-y-controles-avanzados), cubre invocaciones, latencia, tokens, throttles y caché. Nada más. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#3-métricas-de-confianza-e-incertidumbre-en-cloudwatch).

Las tres señales de confianza que **sí** produce la plataforma, y que hay que publicar uno mismo con `put_metric_data`:

| Señal | De dónde sale | Qué mide |
| --- | --- | --- |
| **Scores de contextual grounding** | `contextualGroundingPolicy` del assessment: `{"type": "GROUNDING"\|"RELEVANCE", "score": double, "threshold": double}` | Confianza en que la respuesta está fundamentada y es relevante |
| **Findings de Automated Reasoning** | `FindingCounts` y `TotalFindings`, y los resultados `VALID`, `INVALID`, `TRANSLATION_AMBIGUOUS`, `TOO_COMPLEX` | Si la respuesta es demostrablemente consistente con la política |
| **`confidence` de los content filters** | `contentPolicy.filters[].confidence` con valores `NONE`, `LOW`, `MEDIUM`, `HIGH` | Confianza de la detección de contenido dañino |

```python
import boto3

cloudwatch = boto3.client("cloudwatch")
runtime = boto3.client("bedrock-runtime")


def publicar_confianza(assessment: dict, modelo: str) -> None:
    """Emite los scores de grounding como metricas propias.

    AWS/Bedrock no publica metricas de confianza, asi que hay que derivarlas
    de los scores del contextual grounding check y publicarlas a mano.
    """
    datos = []
    for filtro in assessment.get("contextualGroundingPolicy", {}).get("filters", []):
        datos.append(
            {
                "MetricName": f"Confianza{filtro['type'].capitalize()}",
                "Dimensions": [
                    {"Name": "ModelId", "Value": modelo},
                    {"Name": "Accion", "Value": filtro["action"]},
                ],
                "Value": filtro["score"],
                "Unit": "None",
            }
        )
        # El margen sobre el umbral cuantifica cuan cerca estuvo del bloqueo.
        datos.append(
            {
                "MetricName": f"Margen{filtro['type'].capitalize()}",
                "Dimensions": [{"Name": "ModelId", "Value": modelo}],
                "Value": filtro["score"] - filtro["threshold"],
                "Unit": "None",
            }
        )

    if datos:
        cloudwatch.put_metric_data(Namespace="GenAI/Confianza", MetricData=datos)
```

> El **margen sobre el umbral** es la métrica que más información aporta y que nadie publica: un score de 0.72 con umbral 0.70 pasó por los pelos. Una serie de márgenes decrecientes anticipa una degradación del retrieval antes de que empiecen los bloqueos.

Con esa métrica propia ya se puede aplicar la **anomaly detection** del [Skill 3.3.4](./task-3-3-governance-y-compliance.md#skill-334--monitorización-continua-y-controles-avanzados), que es la forma documentada de alertar sin umbral fijo.

### Respaldo en los lenses

| Práctica | Contenido |
| --- | --- |
| [**GENOPS03-BP02**](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops03-bp02.html) | Habilitar tracing para agentes y workflows RAG |
| [**AGENTSEC05**](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec05.html) | Observabilidad y **non-repudiation**: fuente de origen en cada acción logueada, **correlation ID único que sobreviva las fronteras asíncronas**, y masking de campos sensibles antes del almacenamiento a largo plazo |
| [**AGENTSEC07-BP02**](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec07-bp02.html) | **Indicadores de confianza claros y avisos de manipulación** de cara al usuario |

> AGENTSEC07-BP02 es la best practice que cierra el skill: no basta con recoger la confianza, hay que **mostrarla al usuario** junto a avisos cuando el sistema detecta un intento de manipulación. Eso es la dimensión **Transparency** en la práctica.

---

## Skill 3.4.2 — Evaluaciones de fairness

> *Aplicar evaluaciones de fairness para asegurar salidas del FM sin sesgo (por ejemplo, usando métricas de fairness predefinidas en Amazon CloudWatch, Amazon Bedrock Prompt Management y Amazon Bedrock Prompt Flows para realizar A/B testing sistemático, Amazon Bedrock con soluciones LLM-as-a-judge para realizar evaluaciones automatizadas de modelo).*

> **Discrepancia 2**: **no existen métricas de fairness predefinidas en CloudWatch.** CloudWatch no publica ninguna. Las palancas reales son `Builtin.Stereotyping` y `Builtin.Harmfulness` de Bedrock evaluations, y las bias metrics de SageMaker Clarify, que Model Monitor sí **escribe a CloudWatch** cuando detecta drift. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#2-métricas-de-fairness-predefinidas-en-cloudwatch).

### Las cuatro familias de evaluación de Bedrock

De [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html):

| Familia | Cómo puntúa | Página |
| --- | --- | --- |
| **Programmatic (automatic)** | Scores calculados, sin revisores | [Creating an automatic model evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-automatic.html) |
| **Human workers** | Personas puntúan y aportan preferencias | [Model evaluation with human workers](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-human.html) |
| **Judge model** | Un segundo LLM puntúa **y explica** | [LLM as a judge](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-judge.html) |
| **RAG evaluations con LLM** | Métricas sobre la knowledge base. **Requiere ground truth** | [Evaluate RAG sources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html) |

> La familia **human workers** es el sustituto documentado de Amazon Augmented AI, que está cerrado a clientes nuevos, como ya se registró en el Domain 2. Ver [referencias-oficiales.md de Domain 2](../domain-2/referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación).

### Las once métricas built-in del judge model

De [Use metrics to understand model performance](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-metrics.html). Los identificadores exactos importan:

| Métrica | Qué mide |
| --- | --- |
| **`Builtin.Correctness`** | Si la respuesta es correcta. **Usa la reference response (ground truth) si se aporta** en el prompt dataset |
| **`Builtin.Completeness`** | Si responde a **todas** las preguntas del prompt. También usa ground truth si se aporta |
| **`Builtin.Faithfulness`** | Si contiene información **que no está en el prompt**, para medir fidelidad al contexto |
| **`Builtin.Helpfulness`** | Si sigue las instrucciones, si es sensata y coherente, y si **anticipa necesidades implícitas** |
| **`Builtin.Coherence`** | Huecos lógicos, inconsistencias y contradicciones |
| **`Builtin.Relevance`** | Relevancia de la respuesta respecto al prompt |
| **`Builtin.FollowingInstructions`** | Si respeta **las indicaciones exactas** del prompt |
| **`Builtin.ProfessionalStyleAndTone`** | Si el estilo, formato y tono son apropiados para un entorno profesional |
| **`Builtin.Harmfulness`** | Si contiene contenido dañino |
| **`Builtin.Stereotyping`** | Si contiene estereotipos de cualquier tipo, **positivos o negativos** |
| **`Builtin.Refusal`** | Si declina responder o rechaza la petición dando razones |

> **Las tres palancas de fairness** en esta familia son **`Builtin.Stereotyping`**, **`Builtin.Harmfulness`** y **`Builtin.Refusal`**. La primera detecta el sesgo en la salida, la segunda el daño, y la tercera el **falso positivo del propio sistema de seguridad**: un guardrail demasiado agresivo produce rechazos legítimos, y eso también es un problema de equidad si afecta desigualmente a unos usuarios.

### Las métricas de RAG, que no son las mismas

De [Use metrics to understand RAG system performance](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-metrics.html). Hay **dos tipos de job de evaluación RAG**, cada uno con su propio conjunto:

**Retrieve only:**

| Métrica | Qué mide |
| --- | --- |
| **`Builtin.ContextRelevance`** | Cuán contextualmente relevantes son los textos recuperados para las preguntas |
| **`Builtin.ContextCoverage`** | Cuánto cubren los textos recuperados de la información del ground truth. **Exige ground truth en el prompt dataset** |

**Retrieve and generate:**

| Métrica | Qué mide |
| --- | --- |
| `Builtin.Correctness` | Exactitud de las respuestas |
| `Builtin.Completeness` | Si resuelven todos los aspectos de la pregunta |
| `Builtin.Helpfulness` | Utilidad holística |
| **`Builtin.LogicalCoherence`** | Ausencia de huecos lógicos, inconsistencias o contradicciones |
| `Builtin.Faithfulness` | Cuánto evita la hallucination **respecto a los textos recuperados** |
| **`Builtin.CitationPrecision`** | Cuántos de los pasajes citados **estaban bien citados** |
| **`Builtin.CitationCoverage`** | Si la respuesta está respaldada por los pasajes citados y **si faltan citas** |
| `Builtin.Harmfulness` | Contenido dañino: **hate, insults, violence o sexual** |
| `Builtin.Stereotyping` | **Afirmaciones generalizadas** sobre individuos o grupos |
| `Builtin.Refusal` | Cuán **evasivas** son las respuestas |

> **Gotcha de nomenclatura muy examinable**: la coherencia lógica se llama **`Builtin.Coherence`** en la evaluación de modelo y **`Builtin.LogicalCoherence`** en la evaluación RAG. Son identificadores distintos para el mismo concepto en dos familias distintas. Usar el equivocado hace fallar la creación del job.

> **`Builtin.CitationPrecision`** y **`Builtin.CitationCoverage`** son las métricas que cuantifican la **atribución de fuente** del [Skill 3.4.1](#skill-341--transparencia-y-reasoning-traces). Precision mide si lo que citas es correcto; coverage, si citaste todo lo que deberías. La transparencia se puede medir, no solo declarar.

```python
import boto3

bedrock = boto3.client("bedrock")

bedrock.create_evaluation_job(
    jobName="fairness-asistente-soporte",
    roleArn="arn:aws:iam::111122223333:role/BedrockEvaluationRole",
    outputDataConfig={
        # El informe completo va a S3; la consola solo muestra el histograma
        # y las explicaciones de los primeros cinco prompts.
        "s3Uri": "s3://amzn-s3-demo-bucket/evaluaciones/"
    },
    evaluationConfig={
        "automated": {
            "datasetMetricConfigs": [
                {
                    "taskType": "General",
                    "dataset": {
                        "name": "prompts-fairness",
                        "datasetLocation": {
                            "s3Uri": "s3://amzn-s3-demo-bucket/datasets/fairness.jsonl"
                        },
                    },
                    "metricNames": [
                        "Builtin.Stereotyping",
                        "Builtin.Harmfulness",
                        # Mide el falso positivo del sistema de seguridad.
                        "Builtin.Refusal",
                    ],
                }
            ],
            "evaluatorModelConfig": {
                "bedrockEvaluatorModels": [
                    {"modelIdentifier": "anthropic.claude-3-5-sonnet-20241022-v2:0"}
                ]
            },
        }
    },
    inferenceConfig={
        "models": [
            {
                "bedrockModel": {
                    "modelIdentifier": "amazon.nova-pro-v1:0",
                    "inferenceParams": '{"temperature":0.0}',
                }
            }
        ]
    },
)
```

Las métricas custom se definen con [Create a prompt for a custom metric](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-custom-metrics-prompt-formats.html) y [Create a model evaluation job using custom metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-custom-metrics-create-job.html). Los informes, en [Review model evaluation job reports and metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-report.html).

La toxicidad de la familia **programmatic**, con el algoritmo detoxify y los datasets `Builtin.RealToxicityPrompts` y `Builtin.Bold`, está en [Task 3.1 · Skill 3.1.2](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-312--seguridad-de-contenido-en-las-salidas). El dataset **BOLD** es además el que evalúa equidad explícitamente, en cinco dominios: profesión, género, raza, ideologías religiosas e ideologías políticas.

### Las bias metrics de SageMaker Clarify

> **Aviso de disponibilidad**: **Amazon SageMaker Clarify ya no está abierto a clientes nuevos.** Los existentes siguen con normalidad; AWS invierte en seguridad y disponibilidad pero **no planea funcionalidades nuevas**. Ver [Clarify availability change](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-availability-change.html).

Hay que conocerlas porque el vocabulario de fairness del examen sale de aquí. El encuadre oficial es honesto y vale como respuesta: **cada medida de bias corresponde a una noción distinta de equidad**, esas nociones **no se pueden satisfacer todas a la vez**, y la selección **requiere juicio humano** y consulta con los stakeholders apropiados.

La notación: **facet *a*** es el valor de la característica que define al grupo **favorecido** por el sesgo, y **facet *d*** el **desfavorecido**. `y` son las etiquetas **observadas** y `y'` las **predichas** por el modelo.

**Las ocho métricas pre-training**, de [Pre-training Bias Metrics](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-measure-data-bias.html). Son **model-agnostic**, porque no dependen de la salida del modelo y por tanto valen para cualquiera:

| Sigla | Nombre | Qué mide | Rango |
| --- | --- | --- | --- |
| **CI** | [Class Imbalance](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-bias-metric-class-imbalance.html) | Desequilibrio en el **número de miembros** entre facets. **No mira outcomes** | `[-1,+1]` |
| **DPL** | [Difference in Proportions of Labels](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-true-label-imbalance.html) | Desequilibrio de **outcomes positivos** entre facets | `[-1,+1]` normalizado |
| **KL** | [Kullback-Leibler Divergence](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-kl-divergence.html) | Cuánto divergen **entrópicamente** las distribuciones de outcome | `[0,+∞)` |
| **JS** | [Jensen-Shannon Divergence](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-jensen-shannon-divergence.html) | Ídem, con divergencia simétrica | `[0,+∞)` |
| **LP** | [Lp-norm](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-lp-norm.html) | Diferencia p-norm entre distribuciones | `[0,+∞)` |
| **TVD** | [Total Variation Distance](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-total-variation-distance.html) | **La mitad de la diferencia en norma L1** entre distribuciones | `[0,+∞)` |
| **KS** | [Kolmogorov-Smirnov](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-kolmogorov-smirnov.html) | **Divergencia máxima** entre outcomes de distintos facets | `[0,+1]` |
| **CDD** | [Conditional Demographic Disparity](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-data-bias-metric-cddl.html) | Disparidad en el conjunto **y por subgrupos** | `[-1,+1]` |

La interpretación del signo es uniforme en las que van de −1 a +1: **valores positivos indican que el facet favorecido *a* tiene más**, cerca de cero indica equilibrio, y **negativos que el desfavorecido *d* tiene más**.

**Las métricas post-training**, de [Post-training Data and Model Bias Metrics](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-measure-post-training-bias.html). La mayoría son **combinaciones de los números de la matriz de confusión** de cada grupo demográfico:

| Sigla | Nombre | Qué mide |
| --- | --- | --- |
| **DPPL** | [Difference in Positive Proportions in Predicted Labels](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-dppl.html) | Diferencia en la proporción de **predicciones positivas** entre *a* y *d* |
| **DI** | [Disparate Impact](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-di.html) | **Ratio** de proporciones de etiquetas predichas. **`1` es paridad demográfica** |
| **DCAcc** | [Difference in Conditional Acceptance](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-dcacc.html) | Compara observadas frente a predichas en aceptaciones |
| **DCR** | [Difference in Conditional Rejection](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-dcr.html) | Ídem en rechazos |
| **SD** | [Specificity difference](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-sd.html) | Diferencia de especificidad |
| **RD** | [Recall Difference](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-rd.html) | Diferencia de recall |
| **DAR** | [Difference in Acceptance Rates](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-dar.html) | Diferencia en tasas de aceptación |
| **DRR** | [Difference in Rejection Rates](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-drr.html) | Diferencia en tasas de rechazo |
| **AD** | [Accuracy Difference](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-ad.html) | Diferencia de exactitud |
| **TE** | [Treatment Equality](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-te.html) | Diferencia en el **ratio de falsos positivos a falsos negativos** |
| **CDDPL** | [Conditional Demographic Disparity in Predicted Labels](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-cddpl.html) | Disparidad de etiquetas predichas, en conjunto y por subgrupos |
| **FT** | [Counterfactual Fliptest](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-ft.html) | Test contrafactual de cambio de predicción |
| **GE** | [Generalized entropy](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-post-training-bias-metric-ge.html) | Desigualdad en los **beneficios** asignados. Rango `(0, 0.5)`, con **0.5 como desigualdad máxima**. **Indefinida si el modelo solo predice falsos negativos** |

> **Inconsistencia interna de la documentación**: la prosa de la página dice que Clarify proporciona **once** métricas de bias post-training, mientras que **el índice de temas de la propia página lista trece**. Aquí se listan las trece que aparecen enlazadas. Si una pregunta pide un recuento, conviene saber que la cifra que declara AWS es **once**. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#15-el-recuento-de-bias-metrics-post-training-de-clarify).

**Explicabilidad**, la otra mitad de Clarify: [Model explainability](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-explainability.html), [Feature Attributions that Use Shapley Values](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-shapley-values.html) para SHAP, y [Online explainability](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-online-explainability.html) para explicaciones en tiempo real en un endpoint.

### A/B testing con versiones y alias

> **Discrepancia 7**: no hay página titulada *A/B testing* en la documentación de Bedrock. El mecanismo documentado para desplegar y comparar variantes es **versión más alias**. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#7-ab-testing-de-prompts-sin-página-propia).

| Recurso | Cómo se versiona | Página de despliegue |
| --- | --- | --- |
| **Prompt Management** | Versiones del prompt, comparables entre sí | [Deploy a prompt using versions](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-deploy.html) |
| **Prompt Flows** | Versiones **y alias** del flow | [Deploy a flow using versions and aliases](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-deploy.html) |

El patrón de A/B sistemático que se construye con esas piezas, y que es la respuesta defendible:

```
                    ┌──────────────────────────┐
  Prompt v3  ──────►│ Job de evaluación        │──► Builtin.Stereotyping
  (control)         │ con judge model          │    Builtin.Harmfulness
                    │ mismo dataset            │    Builtin.Refusal
  Prompt v4  ──────►│ mismo evaluator model    │──► informe completo a S3
  (variante)        └──────────────────────────┘
                                │
                                ▼
                    ¿la variante mejora sin
                    empeorar el rechazo?
                                │
                    sí ─────────┴───────── no
                     │                      │
                     ▼                      ▼
          mover el alias de                descartar
          producción a v4                  la variante
          (cambio sin tocar código)
```

> La clave del diseño es que **el alias desacopla la variante del código**: la aplicación invoca el alias, y promover una variante es mover el alias. Es el mismo razonamiento de selección dinámica de modelo de [Task 1.2 · Skill 1.2.2](../domain-1/task-1-2-seleccion-y-configuracion-fm.md#skill-122--selección-dinámica-de-modelo-sin-cambiar-código), aplicado a prompts en lugar de a modelos. La gestión y governance de prompts está en [Task 1.6 · Skill 1.6.3](../domain-1/task-1-6-prompt-engineering-governance.md#skill-163--gestión-y-governance-de-prompts).

---

## Skill 3.4.3 — Sistemas conformes a política

> *Desarrollar sistemas conformes a política para asegurar adherencia a prácticas de IA responsable (por ejemplo, usando Amazon Bedrock guardrails basados en requisitos de política, model cards para documentar limitaciones del FM, funciones Lambda para realizar chequeos de compliance automatizados).*

### Automated Reasoning checks

De [What are Automated Reasoning checks in Amazon Bedrock Guardrails?](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html). Es la política de guardrail más distinta de todas, y la que mejor responde a *conformidad con una política escrita*.

El problema que resuelve: sin validación, los LLMs producen hallucinations que socavan la confianza. La diferencia con el resto: **los content filters y las topic policies actúan como puertas binarias**, bloquean o permiten. Automated Reasoning checks actúa como **capa de verificación que da feedback detallado y accionable** usando **lógica formal** en lugar de coincidencia de patrones.

Las **tres capacidades**:

| Capacidad | Detalle |
| --- | --- |
| **Detectar afirmaciones factualmente incorrectas** | **Demostrando matemáticamente** que el contenido generado contradice las reglas de la política |
| **Señalar supuestos no declarados** (*unstated assumptions*) | Cuando la respuesta es consistente con la política pero **no aborda todas las reglas relevantes**, indicando que puede estar incompleta |
| **Dar explicaciones verificables matemáticamente** | De por qué una afirmación correcta lo es, **citando las reglas concretas y las asignaciones de variables** que sostienen la conclusión |

**Cuándo usarlo**, según la documentación: industrias reguladas (salud, recursos humanos, servicios financieros), **conjuntos de reglas complejos** donde múltiples condiciones interactúan (aprobación de hipotecas, normativa urbanística, elegibilidad de seguros, beneficios de empleado), escenarios de compliance que exigen respuestas auditables con **prueba matemáticamente verificable**, y aplicaciones de cara al cliente donde una guía incorrecta erosiona la confianza.

### Las cinco limitaciones explícitas

> **Dato decisivo, y el más contraintuitivo del dominio**: **Automated Reasoning checks opera solo en *detect mode*.** Devuelve findings y feedback, **no bloquea contenido**. La decisión de servir la respuesta, reescribirla usando el feedback o pedir aclaración al usuario es de la aplicación. Si una pregunta plantea "bloquear respuestas que contradigan la política", la respuesta no es Automated Reasoning por sí solo.

| Limitación | Detalle | Con qué se compensa |
| --- | --- | --- |
| **Sin protección de prompt injection** | Valida exactamente lo que se le envía. Si la entrada es maliciosa, valida eso tal cual | **Content filters** con prompt attack |
| **Sin detección de off-topic** | Solo analiza texto **relevante para la política**; ignora lo no relacionado y no puede decir si la respuesta está fuera de tema | **Topic policies** |
| **Sin soporte de streaming** | Hay que **validar respuestas completas** | Diseño sincrónico, o validación tras el stream |
| **Solo inglés (US)** | No hay otros idiomas | — |
| **Alcance limitado a la política** | Un resultado **`VALID` solo garantiza validez para las partes capturadas por las variables de la política**. Lo que cae fuera **no se valida** | Ampliar el schema de variables |

El ejemplo oficial de la última limitación es excelente y conviene recordarlo: *"puedo entregar los deberes tarde porque tengo un justificante médico falso"* podría considerarse **válido** si la política **no tiene una variable que capture si el justificante es falso**. La lógica formal solo razona sobre lo que modelaste.

### El flujo de cuatro fases

```
Documento fuente ──► Política extraída ──► Testing ──► Despliegue ──► Integración
   (las reglas)       (lógica formal)     (verificar)  (guardrail)   (validar y actuar
                                                                      sobre el feedback)
```

| Fase | Qué ocurre |
| --- | --- |
| **1. Crear la política** | Se sube un documento fuente con las reglas. Automated Reasoning **extrae reglas de lógica formal y un schema de variables**. Se genera automáticamente un **fidelity report** |
| **2. Testear y refinar** | Se crean tests que imitan las preguntas de los usuarios y las respuestas que el LLM podría dar |
| **3. Desplegar** | Se guarda una **versión inmutable** de la política testeada y se adjunta a un guardrail. **Automatizable con CloudFormation o CI/CD** |
| **4. Integrar** | En runtime los findings llegan por **`Converse`**, **`InvokeModel`** y el **`ApplyGuardrail`** independiente |

El **fidelity report** es la pieza de governance: mide **con qué exactitud la política extraída representa el documento fuente**, con **scores de cobertura y exactitud** y **grounding detallado que enlaza cada regla y variable con las afirmaciones concretas del contenido de origen**. Es lo que permite auditar que la traducción de la política escrita a lógica formal fue fiel.

> **Dato decisivo sobre el testing**: hay **dos tipos de test con propósitos distintos**. Los **generated scenarios** validan **la corrección de las reglas**. Los **QnA tests** validan **la exactitud de la traducción de lenguaje natural a lógica**. Son dos fuentes de error independientes: la política puede estar bien y traducirse mal, o traducirse bien siendo incorrecta.

De [Automated Reasoning checks concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/automated-reasoning-checks-concepts.html), dos conceptos más: la *policy* es un recurso en la cuenta con reglas de lógica formal, schema de variables y tipos personalizados; y las **bare assertions**, reglas sin estructura if-then, crean **axiomas siempre verdaderos**.

### Los límites operativos

| Límite | Valor |
| --- | --- |
| **Regiones (GA)** | **Seis**: N. Virginia, Oregón, Ohio, Fráncfort, París, Irlanda |
| **Idioma** | **Inglés (US) únicamente** |
| **Documento de entrada** | **5 MB** y **50.000 caracteres**. Documentos mayores se dividen y cada sección se fusiona en la política |
| **Imágenes y tablas** | **Cuentan para el número de caracteres de entrada** |
| **Latencia** | Añade latencia. **El número de variables de la política contribuye directamente** a su aumento |
| **Aritmética no lineal** | Puede dar **timeout** o **`TOO_COMPLEX`** con números irracionales o exponentes |
| **Alcance de la política** | Cada política debería centrarse en **un dominio concreto** (RR. HH., finanzas, legal), no cubrir áreas no relacionadas |
| **Facturación** | **Por petición de validación, independientemente del resultado**, incluidos `VALID`, `INVALID` y `TRANSLATION_AMBIGUOUS` |

Los resultados de validación que hay que saber interpretar: **`VALID`**, **`INVALID`**, **`TRANSLATION_AMBIGUOUS`** y **`TOO_COMPLEX`**. Los dos últimos no son veredictos sobre la respuesta: dicen que **el sistema no pudo decidir**, y la aplicación debe tratarlos como tal y no como aprobación.

```python
import boto3

runtime = boto3.client("bedrock-runtime")

respuesta = runtime.converse(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    messages=[{"role": "user", "content": [{"text": "¿Puedo pedir la baja sin preaviso?"}]}],
    guardrailConfig={
        # La politica de Automated Reasoning va asociada al guardrail.
        "guardrailIdentifier": "gr-politica-rrhh",
        "guardrailVersion": "1",
        "trace": "enabled",
    },
)

assessments = respuesta.get("trace", {}).get("guardrail", {}).get("outputAssessment", {})

for lista in assessments.values():
    for assessment in lista:
        politica = assessment.get("automatedReasoningPolicy", {})
        for finding in politica.get("findings", []):
            # Automated Reasoning opera SOLO en detect mode: no bloquea,
            # devuelve el veredicto y la aplicacion decide.
            if "valid" in finding:
                # Ojo: VALID solo cubre lo capturado por las variables.
                servir_respuesta(respuesta)
            elif "invalid" in finding:
                # Hay contradiccion demostrada con reglas citadas.
                reescribir_con_feedback(finding["invalid"])
            elif "satisfiable" in finding:
                # Supuestos no declarados: la respuesta puede estar incompleta.
                pedir_aclaracion(finding["satisfiable"])
            else:
                # translationAmbiguous, tooComplex, impossible: el sistema no
                # pudo decidir. No es una aprobacion.
                escalar_a_revision_humana(finding)
```

El resto de la familia: [Create your policy](https://docs.aws.amazon.com/bedrock/latest/userguide/create-automated-reasoning-policy.html), [Best practices](https://docs.aws.amazon.com/bedrock/latest/userguide/automated-reasoning-policy-best-practices.html), [Test a policy](https://docs.aws.amazon.com/bedrock/latest/userguide/test-automated-reasoning-policy.html), [Address failed tests](https://docs.aws.amazon.com/bedrock/latest/userguide/address-failed-automated-reasoning-tests.html), [Deploy a policy](https://docs.aws.amazon.com/bedrock/latest/userguide/deploy-automated-reasoning-policy.html), [Integrate in your application](https://docs.aws.amazon.com/bedrock/latest/userguide/integrate-automated-reasoning-checks.html) y [Permissions with ApplyGuardrail](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrail-automated-reasoning-permissions.html).

### Guardrails basados en requisitos de política

La otra mitad del skill. El mapa de qué política de guardrail implementa qué tipo de requisito ya está en la tabla de decisión de [Task 3.1 · Skill 3.1.1](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-311--seguridad-de-contenido-en-las-entradas). Lo que añade este skill es el encuadre: la política escrita de la organización se traduce a **controles ejecutables** de tres formas distintas, y elegir mal es el error típico.

| Naturaleza del requisito de política | Mecanismo | Por qué |
| --- | --- | --- |
| "No hablamos de estos temas" | **Denied topics** | Evaluación contextual de un tema |
| "No usamos estas palabras" | **Word filters** | Coincidencia exacta |
| "No exponemos estos datos" | **Sensitive information filters** | Detección tipada con Block o Mask |
| "No inventamos sobre nuestras fuentes" | **Contextual grounding check** | Compara con la fuente |
| **"Nuestras respuestas no pueden contradecir este reglamento"** | **Automated Reasoning checks** | **Lógica formal sobre el documento de la política** |
| "Documentamos para qué sirve y para qué no" | **Model cards** | `intended_uses` y `risk_rating` |

El respaldo Well-Architected es [GENSEC02-BP01 Implement guardrails to mitigate harmful or incorrect model responses](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gensec02-bp01.html), y para agentes [AGENTSEC04-BP01](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec04-bp01.html) sobre guardrails y controles de alineación, más [AGENTSEC08-BP02](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec08-bp02.html) sobre filtrado de salida de información sensible.

### Documentar las limitaciones del FM

Los **model cards** están desarrollados en [Task 3.3 · Skill 3.3.1](./task-3-3-governance-y-compliance.md#skill-331--frameworks-de-compliance-regulatorio). Lo que este skill subraya: la sección **`intended_uses`** debe describir explícitamente **los escenarios en los que el modelo NO se recomienda**, no solo los que sí. Documentar la limitación es lo que convierte el model card en un control de IA responsable y no en material de marketing.

Del lado del proveedor, las **AI Service Cards** cumplen la función equivalente, con la salvedad de que **no tienen índice navegable en el portal**, según el [Skill 3.3.3](./task-3-3-governance-y-compliance.md#skill-333--governance-organizacional).

### Chequeos de compliance automatizados

> **Discrepancia 9**: el skill nombra *funciones Lambda para realizar chequeos de compliance automatizados*, pero **no hay página de la documentación que ligue Lambda a chequeos de compliance de IA**. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#9-lambda-para-chequeos-de-compliance-automatizados).

Los dos caminos documentados que sí existen:

| Camino | Cómo funciona |
| --- | --- |
| **Reglas custom de AWS Config con Lambda** | La regla evalúa la conformidad de un recurso invocando una Lambda propia, y se empaqueta en un [conformance pack](https://docs.aws.amazon.com/config/latest/developerguide/conformance-packs.html) con su acción de remediación |
| **Nodos Lambda en Bedrock Flows** | Un paso del [flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html) ejecuta la comprobación determinista en medio del workflow de generación |

Y el tercero, que es el que el resto de este dominio ha ido construyendo: **Lambda como capa de post-procesamiento** que valida la salida contra reglas de negocio, según la arquitectura de defensa en profundidad de [Task 3.1 · Skill 3.1.4](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-314--defensa-en-profundidad-contra-el-mal-uso-del-fm). Es donde encajan los findings de Automated Reasoning: la Lambda recibe el veredicto y decide servir, reescribir o escalar.

---

## Resumen operativo del Task 3.4

| Si la pregunta menciona… | La respuesta apunta a |
| --- | --- |
| Activar el reasoning trace de un agente | **`enableTrace`** en `InvokeAgent` |
| El tipo de trace sin `ModelInvocationInput` | **`FailureTrace`**, el único |
| Trazar qué agentes reenviaron la petición | **`callerChain`** del `TracePart` |
| Dónde está el razonamiento del agente | **`parsedResponse.rationale`** |
| Saber si se sobrescribió la plantilla del prompt | **`promptCreationMode: OVERRIDDEN`** |
| Métrica de confianza en CloudWatch | **No existe**: emitirla con `put_metric_data` o derivarla de los scores de grounding |
| Mostrar indicadores de confianza al usuario | **AGENTSEC07-BP02** |
| Coherencia lógica en evaluación de modelo | **`Builtin.Coherence`** |
| Coherencia lógica en evaluación RAG | **`Builtin.LogicalCoherence`** |
| Medir si las citas son correctas | **`Builtin.CitationPrecision`** |
| Medir si faltan citas | **`Builtin.CitationCoverage`** |
| Métrica que exige ground truth en retrieve-only | **`Builtin.ContextCoverage`** |
| Detectar sesgo en la salida del FM | **`Builtin.Stereotyping`** y **`Builtin.Harmfulness`** |
| Medir el exceso de celo del guardrail | **`Builtin.Refusal`** |
| Paridad demográfica perfecta | **Disparate Impact (DI) igual a 1** |
| Bias metric que no mira outcomes | **Class Imbalance (CI)** |
| Bias metrics válidas para cualquier modelo | Las **pre-training**, que son model-agnostic |
| Ratio de falsos positivos a falsos negativos | **Treatment Equality (TE)** |
| Desigualdad máxima en generalized entropy | **0.5** |
| A/B testing de prompts | **Versión más alias**; no hay página de A/B testing |
| Bloquear respuestas que contradigan una política | **Automated Reasoning no bloquea**: opera en detect mode |
| Prueba matemáticamente verificable de conformidad | **Automated Reasoning checks** |
| Respuesta consistente pero incompleta | **Unstated assumptions** |
| Medir la fidelidad de la política extraída | **Fidelity report**, con coverage y accuracy |
| Validar la traducción de lenguaje natural a lógica | **QnA tests**; los generated scenarios validan las reglas |
| `VALID` con una afirmación claramente falsa | El dato **no está capturado por las variables** de la política |
| `TOO_COMPLEX` o `TRANSLATION_AMBIGUOUS` | **No son aprobación**: el sistema no pudo decidir |
| Automated Reasoning con streaming | **No soportado** |
| Automated Reasoning en español | **No soportado**: solo inglés (US) |
| Límite del documento fuente de la política | **5 MB y 50.000 caracteres**, tablas e imágenes incluidas |
