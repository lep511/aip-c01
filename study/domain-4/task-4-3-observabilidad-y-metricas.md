# Task 4.3 — Observabilidad y métricas

[← Volver al índice](./README.md)

Skills cubiertos: **4.3.1**, **4.3.2**, **4.3.3**.

El Task 4.3 tiene seis skills y se reparte en dos archivos. Este cubre **la aplicación y sus métricas**: qué se observa, qué se mide y cómo se presenta. El de **herramientas, vector stores y modos de fallo** (skills 4.3.4, 4.3.5 y 4.3.6) está en [task-4-3-herramientas-vector-stores-y-fallos.md](./task-4-3-herramientas-vector-stores-y-fallos.md).

El catálogo de métricas de los tres namespaces de Bedrock no se repite aquí: está en [Task 3.3 · Skill 3.3.4](../domain-3/task-3-3-governance-y-compliance.md#los-tres-namespaces-de-métricas). Lo que aportan estos tres skills es la capa que AWS construyó **encima** de ese catálogo.

---

## Skill 4.3.1 — Observabilidad holística

> *Crear sistemas de observabilidad holísticos para dar visibilidad completa del rendimiento de la aplicación de FM (por ejemplo, usando métricas operativas, performance tracing, tracing de interacción con el FM, métricas de impacto de negocio con dashboards personalizados).*

### Las cuatro señales que pide el skill, y de dónde sale cada una

| Señal del skill | Fuente documentada |
| --- | --- |
| **Métricas operativas** | Namespaces `AWS/Bedrock` y `AWS/Bedrock/Guardrails` |
| **Performance tracing** | **Application Signals** y **Transaction Search** |
| **Tracing de interacción con el FM** | **Prompt tracing end-to-end** de CloudWatch generative AI observability |
| **Métricas de impacto de negocio con dashboards** | `PutMetricData` propio más **dashboards de CloudWatch** |

### CloudWatch generative AI observability

De [Generative AI observability](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/GenAI-observability.html). Es la capa que faltaba en los dominios anteriores: permite observar cargas de IA generativa, **incluidos agentes de Bedrock AgentCore**, y obtener información sobre **rendimiento, salud y exactitud** de la IA. Da vistas preconfiguradas de **latencia, uso y errores**.

Lo que la documentación declara que permite hacer:

| Capacidad | Detalle |
| --- | --- |
| **Evaluar calidad y exactitud a escala** | Monitorización automatizada que **reduce la necesidad de revisión manual**, capturando salidas del modelo, métricas de calidad de respuesta e interacciones de usuario final |
| **Monitorizar el inventario completo** | Invocaciones de modelo, **agentes (gestionados, autoalojados y de terceros)**, knowledge bases, guardrails y herramientas |
| **Prompt tracing end-to-end** | Identificar rápido el origen del error en componentes como **knowledge bases, herramientas y modelos** |
| **Reutilizar el stack existente** | Application Signals, alarmas, dashboards, protección de datos sensibles y Logs Insights |
| **Trazas de modelos de terceros** | Acceso a prompt traces en Bedrock, y envío de **trazas estructuradas de modelos de terceros con el SDK de ADOT** |

> **Dato decisivo**: es compatible con frameworks de orquestación de terceros, y la documentación nombra tres: **AWS Strands, LangChain y LangGraph**. Es la respuesta cuando una pregunta plantea observar una aplicación GenAI que **no** está construida sobre agentes de Bedrock.

### Los dos dashboards preconstruidos

| Capacidad | Qué cubre |
| --- | --- |
| **Model Invocations** | Dashboard de métricas detallado sobre **uso del modelo, consumo de tokens** y una **tabla curada de invocation logs** para ver el contenido de entrada y salida de las inferencias |
| **Amazon Bedrock AgentCore agents** | Métricas de **rendimiento y de decisión** de los primitivos de AgentCore: [Agents, Memory, Built-in Tools, Gateways e Identity](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AgentCore-Agents.html) |

Las métricas clave que ofrecen ambos, y conviene fijarse en las dos últimas:

```
Invocaciones totales y media
Uso de tokens: total, media por consulta, entrada, salida
Latencia: media, P90, P99                     ← percentiles, no solo media
Tasas de error y eventos de throttling
Atribucion de coste por aplicacion,
  rol de usuario o usuario concreto            ← atribucion, no solo total
```

> **Dato decisivo**: es el único lugar del portal donde AWS ofrece **latencia en P90 y P99** para cargas GenAI de fábrica, y **atribución de coste por usuario o rol**. Una pregunta sobre "el percentil 99 de latencia de las invocaciones" no se responde con el namespace `AWS/Bedrock` a pelo, sino con esta vista.

Existe además una tercera vista para agentes de codificación, [Coding Agent Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/coding-agents-insights.html).

### El dashboard de Model Invocations, widget a widget

De [Model Invocations](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/model-invocations.html).

> **Restricción importante, y es la primera pregunta que hay que hacerse ante un dashboard vacío**: **hay que habilitar el model invocation logging de Bedrock para poder ver las invocaciones**. Los dashboards preconfigurados aparecen automáticamente al empezar a invocar, pero **la tabla de invocaciones y el contenido de entrada y salida requieren el logging habilitado** con destino a CloudWatch Logs. El detalle del logging está en [Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#la-fuente-model-invocation-logging) y su configuración en [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html).

Los widgets, y el tercero desde el final es el que no se espera:

| Widget | Qué muestra |
| --- | --- |
| **Invocation count** | Peticiones **con éxito** a `Converse`, `ConverseStream`, `InvokeModel` e `InvokeModelWithResponseStream` |
| **Invocation latency** | Latencia de las invocaciones |
| **Token Counts by Model** | Conteos por modelo, **separando entrada y salida** |
| **Daily Token Counts by ModelID** | Totales diarios por model ID |
| **InputTokenCount, OutputTokenCount** | Totales de la cuenta a través de los modelos seleccionados |
| **Requests, grouped by input tokens** | Peticiones agrupadas por tokens de entrada en **6 rangos**, una línea por rango |
| **Invocation Throttles** | Invocaciones limitadas por el sistema |
| **Invocation Error Count** | Invocaciones con errores de servidor y de cliente |

> **Dato decisivo**: el widget **Requests grouped by input tokens** en **6 rangos** es el histograma de tamaño de prompt, y no existe como métrica en `AWS/Bedrock`. Es la herramienta directa para detectar que **la distribución de tamaños de prompt se desplazó**, que es la causa más frecuente de un coste que sube sin que suba el tráfico.

> **Aviso oficial sobre los throttles**: el número de throttles que se ve **depende de la configuración de reintentos del SDK**. Un `retry_mode` agresivo los multiplica; el modo `adaptive` los reduce moderando el ritmo. La métrica no mide solo la capacidad del servicio: mide también cómo insiste el cliente. Los tres modos están en [Task 2.4 · Skill 2.4.3](../domain-2/task-2-4-integraciones-api-fm.md#reintentos-del-sdk-los-tres-modos).

El flujo de investigación que documenta la página, de la gráfica al log en cuatro saltos:

```
Grafica de metrica
  · pasar el cursor para ver detalles
  · icono de Alarm para crear una alarma sobre ese grafico
  · desplegable ModelID para filtrar por modelo
  · Period override: 1 minuto, 1 hora, 6 horas
        │
Tabla de Invocations
  · elegir un Request ID
        │
Vista de Request ID
  · entrada y salida de la invocacion en el panel derecho
        │
Actions > View in Logs Insights
  · consulta sobre los invocation logs
```

### Application Signals: la telemetría de la llamada a Bedrock

De [Example: Use Application Signals to troubleshoot generative AI applications interacting with Amazon Bedrock models](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Services-example-scenario-GenerativeAI.html). Aporta **datos de telemetría de serie**, y **genera y correlaciona automáticamente métricas de rendimiento y trazas para las llamadas a la API de Bedrock**.

Los cuatro casos de uso que declara resolver:

| Caso | Qué diagnostica |
| --- | --- |
| **Model configuration issues** | Parámetros mal puestos |
| **Model usage costs** | Coste por uso |
| **Model latency** | Latencia del modelo |
| **Model response generation stopped reasons** | **Por qué se detuvo la generación** |

Los modelos soportados: **AI21 Jamba, Amazon Titan, Anthropic Claude, Cohere Command, Meta Llama, Mistral AI y Nova**.

Y lo que lo hace útil frente a las métricas planas: genera métricas de rendimiento **a nivel de recurso**, con cuatro identificadores:

```
Model ID
Guardrails ID
Knowledge Base ID
Bedrock Agent ID
```

Además de spans de traza correlacionados **al mismo nivel**, para tener la vista completa de la ejecución y sus dependencias.

> **Dato decisivo**: esos cuatro identificadores son lo que permite responder *qué guardrail y qué knowledge base intervinieron en esta petición concreta*, algo que el namespace `AWS/Bedrock` no permite porque su única dimensión es `ModelId`. Es la diferencia entre monitorizar el modelo y monitorizar la aplicación.

Se habilita según [Enabling Application Signals](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Signals-Enable.html), dentro del conjunto de capacidades de [monitorización de aplicaciones](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Monitoring-Sections.html).

### Los ocho atributos GenAI de OpenTelemetry

Application Signals genera atributos de IA generativa **siguiendo la convención semántica de OpenTelemetry**. Son ocho, y sirven para analizar **uso del modelo, coste y calidad de respuesta**:

| Atributo | Qué captura |
| --- | --- |
| `gen_ai.system` | El sistema de IA generativa |
| `gen_ai.request.model` | El modelo solicitado |
| **`gen_ai.request.max_tokens`** | El techo de salida pedido |
| **`gen_ai.request.temperature`** | La temperatura usada |
| **`gen_ai.request.top_p`** | El top-p usado |
| `gen_ai.usage.input_tokens` | Tokens de entrada |
| `gen_ai.usage.output_tokens` | Tokens de salida |
| **`gen_ai.response.finish_reasons`** | **Por qué terminó la generación** |

> **Dato decisivo**: tres de los ocho atributos son **parámetros de inferencia** (`max_tokens`, `temperature`, `top_p`). Eso convierte a Application Signals en el instrumento que cierra el A/B testing del [Skill 4.2.4](./task-4-2-retrieval-y-parametros.md#ab-testing-de-verdad-versiones-y-alias): permite correlacionar **qué configuración se usó** con **qué coste y qué calidad produjo**, sin instrumentar nada a mano.
>
> Y `gen_ai.response.finish_reasons` es el diagnóstico de respuesta truncada: distingue *el modelo terminó* de *se agotó `max_tokens`* de *se alcanzó una stop sequence*.

El uso que propone la documentación es directamente el del [Skill 4.1.2](./task-4-1-costes-y-eficiencia-de-recursos.md#medir-el-ratio-precio-rendimiento): con la capacidad analítica de **Transaction Search**, **comparar el uso de tokens y el coste entre distintos modelos de LLM para el mismo prompt**, habilitando una selección de modelo coste-eficiente.

### Transaction Search y el log group `aws/spans`

De [Transaction Search](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Transaction-Search.html). Los spans son las unidades fundamentales de operación de una traza distribuida, organizados en **jerarquía padre-hijo**, y cada uno registra inicio, fin, duración y metadatos, que pueden incluir atributos de negocio.

Los números y el mecanismo que importan:

| Aspecto | Detalle |
| --- | --- |
| **Captura** | **El 100 % de los spans** como logs estructurados en CloudWatch, lo que **evita trazas rodas** |
| **Tamaño de traza** | Hasta **10.000 spans** en una traza |
| **Indexado en X-Ray** | Solo **un porcentaje** de los spans se indexa como trace summaries, para búsqueda y analítica end-to-end |
| **Dónde acaban** | Un log group llamado **`aws/spans`** |
| **Formato** | Convención semántica con **trace IDs de W3C**. Las trazas de X-Ray **se convierten automáticamente** a ese formato antes de almacenarse |
| **Qué se puede hacer con ellos** | **Metric filters** para extraer métricas propias, **subscription filters** para reenviar, y **data masking** para proteger PII |

> **Dato decisivo**: la asimetría entre **ingerir el 100 %** y **indexar un porcentaje** es el diseño central de Transaction Search. Todo span está disponible como log estructurado consultable; solo una muestra alimenta la búsqueda de trazas end-to-end. Para una carga GenAI eso significa que **ninguna invocación se pierde del registro**, aunque no toda aparezca en el trace map.

Y el detalle que conecta con los guardrails de privacidad de [Task 3.2](../domain-3/task-3-2-seguridad-y-privacidad-de-datos.md): al ser logs de CloudWatch, se les puede aplicar **data masking** con [políticas de protección de datos](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/cloudwatch-logs-data-protection-policies.html), que es imprescindible si los spans llevan prompts.

Las dos vías de entrada, según si ya se usa X-Ray: habilitar Transaction Search directamente, o usar **Application Signals**, que trae un **setup de OpenTelemetry preempaquetado con ADOT, el agente de CloudWatch, o OpenTelemetry directamente**. Los atributos propios se añaden según [Adding custom attributes](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Transaction-Search-add-custom-attributes.html), y el log group se detalla en [Spans](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Transaction-Search-ingesting-span-log-groups.html).

### Las capas de tracing de una aplicación GenAI

```
NEGOCIO        Metricas propias con PutMetricData
               · consultas resueltas sin escalar a humano
               · tickets cerrados por sesion
               · coste por respuesta correcta
                      │
GENAI          CloudWatch generative AI observability
               · dashboards Model Invocations y AgentCore
               · prompt tracing end-to-end
               · latencia P90 y P99, atribucion de coste por usuario
                      │
APLICACION     Application Signals
               · metricas por Model ID, Guardrails ID,
                 Knowledge Base ID, Bedrock Agent ID
               · 8 atributos gen_ai.* de OpenTelemetry
                      │
TRANSACCION    Transaction Search
               · 100 % de spans en aws/spans
               · hasta 10.000 spans por traza
               · metric filters para metricas propias
                      │
PETICION       X-Ray: trace map, segmentos, subsegmentos
                      │
INVOCACION     Model invocation logging → CloudWatch Logs y S3
               requestMetadata como dimension filtrable
                      │
METRICA        AWS/Bedrock · AWS/Bedrock/Guardrails
               metricas de agentes
```

> La regla que se deduce: **cada capa responde una pregunta distinta y ninguna sustituye a otra**. La métrica dice *cuánto*; el invocation log dice *qué se pidió y qué se respondió*; el span dice *dónde se fue el tiempo*; Application Signals dice *con qué configuración y contra qué recursos*; la capa GenAI dice *cómo se ve todo junto*; y la de negocio dice *si sirvió para algo*.

### Métricas de impacto de negocio

El skill las pide explícitamente y no hay servicio que las produzca: son métricas propias publicadas con `PutMetricData`, como las de confianza del [Task 3.4 · Skill 3.4.1](../domain-3/task-3-4-ia-responsable.md#métricas-de-confianza-e-incertidumbre). La alternativa sin código es extraerlas de los logs con **metric filters** sobre los invocation logs o sobre `aws/spans`.

```python
import boto3

cloudwatch = boto3.client("cloudwatch")


def publicar_impacto(sesion: dict) -> None:
    """Publica metricas de negocio de una sesion de asistente.

    Ninguna de estas tres la produce AWS: son la traduccion de la actividad
    del FM a algo que el negocio reconoce. Sin ellas, un dashboard de GenAI
    solo demuestra que el sistema funciona, no que sirve.
    """
    cloudwatch.put_metric_data(
        Namespace="GenAI/Negocio",
        MetricData=[
            {
                # Numerador de la unica metrica de coste que importa:
                # coste por respuesta correcta, no coste por invocacion.
                "MetricName": "ResolucionSinEscalado",
                "Dimensions": [
                    {"Name": "CasoDeUso", "Value": sesion["caso_de_uso"]},
                    {"Name": "VersionPrompt", "Value": sesion["version_prompt"]},
                ],
                "Value": 1.0 if sesion["resuelta_sin_humano"] else 0.0,
                "Unit": "Count",
            },
            {
                "MetricName": "TurnosHastaResolucion",
                "Dimensions": [{"Name": "CasoDeUso", "Value": sesion["caso_de_uso"]}],
                "Value": sesion["turnos"],
                "Unit": "Count",
            },
            {
                "MetricName": "TokensPorResolucion",
                "Dimensions": [{"Name": "CasoDeUso", "Value": sesion["caso_de_uso"]}],
                "Value": sesion["tokens_entrada"] + sesion["tokens_salida"],
                "Unit": "Count",
            },
        ],
    )
```

---

## Skill 4.3.2 — Monitorización proactiva y KPIs específicos de FM

> *Implementar sistemas completos de monitorización de GenAI para identificar problemas de forma proactiva y evaluar indicadores clave de rendimiento específicos de implementaciones de FM (por ejemplo, usando CloudWatch para rastrear uso de tokens, efectividad del prompt, tasas de hallucination y calidad de respuesta; detección de anomalías para patrones de ráfaga de tokens y drift de respuesta; Amazon Bedrock Model Invocation Logs para análisis detallado de petición y respuesta; benchmarks de rendimiento; detección de anomalías de coste).*

### Lo que la plataforma publica y lo que hay que construir

El skill nombra cuatro KPIs seguidos, y **solo el primero existe como métrica**. Separarlos es la mitad del skill:

| KPI del skill | ¿Existe como métrica? | De dónde sale realmente |
| --- | --- | --- |
| **Token usage** | **Sí** | `InputTokenCount`, `OutputTokenCount`, `CacheRead`/`CacheWriteInputTokenCount` |
| **Prompt effectiveness** | **No** | Métrica propia: tasa de resolución, `finish_reasons`, tasa de reintento del usuario |
| **Hallucination rate** | **No** | Scores de **contextual grounding check**, más evaluaciones con golden dataset |
| **Response quality** | **No** | **Bedrock evaluations** con juez automático, humano o LLM-as-a-judge |

> **Dato decisivo**: la formulación *usando CloudWatch para rastrear uso de tokens, efectividad del prompt, tasas de hallucination y calidad de respuesta* hace parecer que las cuatro son métricas de CloudWatch. No lo son. CloudWatch es **el destino** de las cuatro, pero tres hay que calcularlas y publicarlas. Es el mismo patrón que la discrepancia de las métricas de confianza registrada en [Task 3.4 · Skill 3.4.1](../domain-3/task-3-4-ia-responsable.md#métricas-de-confianza-e-incertidumbre).

La tasa de hallucination se apoya en el **contextual grounding check** del [Task 3.1 · Skill 3.1.3](../domain-3/task-3-1-controles-de-seguridad-entrada-salida.md#skill-313--verificación-de-exactitud-y-reducción-de-hallucinations), que devuelve `score` y `threshold` por cada filtro de `GROUNDING` y `RELEVANCE`. La calidad de respuesta, en las cuatro familias de evaluación del [Task 3.4 · Skill 3.4.2](../domain-3/task-3-4-ia-responsable.md#las-cuatro-familias-de-evaluación-de-bedrock).

### Detección de anomalías para ráfagas de tokens y drift de respuesta

La mecánica de [CloudWatch anomaly detection](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Anomaly_Detection.html), con la banda de valores esperados, la función de metric math `ANOMALY_DETECTION_BAND` y las [alarmas de anomalía](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Create_Anomaly_Detection_Alarm.html), está desarrollada en [Task 3.3 · Skill 3.3.4](../domain-3/task-3-3-governance-y-compliance.md#detección-de-drift-sin-umbral-fijo). Lo que aporta este skill es **sobre qué métrica aplicarla**, y son dos casos distintos:

| Caso del skill | Métrica sobre la que se aplica | Qué detecta |
| --- | --- | --- |
| **Ráfaga de tokens** | `InputTokenCount` y `OutputTokenCount`, o mejor **tokens por invocación** | Que el consumo se sale del patrón, con tráfico normal |
| **Drift de respuesta** | **Longitud media de salida**, distribución de `finish_reasons`, score medio de grounding | Que el modelo empezó a responder distinto sin que nadie lo cambiara |

> **Dato decisivo**: para las ráfagas hay que vigilar **tokens por invocación**, no tokens totales. Los totales suben con el tráfico y una banda de anomalía sobre ellos alerta cada campaña de marketing. Los tokens por invocación son independientes del volumen: si suben, **cambió el prompt, el contexto o el comportamiento del modelo**, que es la señal que se busca.

El `AnomalyDetectorMetricStat` se alimenta de cualquier métrica, incluidas las propias, así que el patrón completo es: publicar la métrica derivada con `PutMetricData` y poner la banda encima.

```python
import boto3

cloudwatch = boto3.client("cloudwatch")

# Tokens por invocacion como metrica derivada: es la que detecta un cambio
# de comportamiento sin confundirlo con un cambio de volumen.
cloudwatch.put_metric_alarm(
    AlarmName="genai-rafaga-de-tokens-por-invocacion",
    ComparisonOperator="GreaterThanUpperThreshold",
    EvaluationPeriods=2,
    # Con ThresholdMetricId no se fija umbral: se compara contra la banda.
    ThresholdMetricId="banda",
    TreatMissingData="notBreaching",
    Metrics=[
        {
            "Id": "entrada",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/Bedrock",
                    "MetricName": "InputTokenCount",
                    "Dimensions": [{"Name": "ModelId", "Value": "amazon.nova-pro-v1:0"}],
                },
                "Period": 300,
                "Stat": "Sum",
            },
            "ReturnData": False,
        },
        {
            "Id": "invocaciones",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/Bedrock",
                    "MetricName": "Invocations",
                    "Dimensions": [{"Name": "ModelId", "Value": "amazon.nova-pro-v1:0"}],
                },
                "Period": 300,
                "Stat": "Sum",
            },
            "ReturnData": False,
        },
        {
            "Id": "por_invocacion",
            "Expression": "entrada / invocaciones",
            "Label": "Tokens de entrada por invocacion",
            "ReturnData": True,
        },
        {
            "Id": "banda",
            "Expression": "ANOMALY_DETECTION_BAND(por_invocacion, 2)",
            "ReturnData": False,
        },
    ],
)
```

### Model Invocation Logs para el análisis de petición y respuesta

El skill los nombra por su nombre propio. La configuración, los destinos, las cuatro operaciones que registran y el hueco de `bedrock-mantle` están en [Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#la-fuente-model-invocation-logging), y las consultas con Logs Insights, los field indexes y las comparison queries en [CloudWatch Logs Insights](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#cloudwatch-logs-insights).

Lo que añade este task es que el logging **es un prerrequisito de la vista de GenAI observability**, no solo una fuente de auditoría: sin él, la tabla curada de invocaciones y el contenido de entrada y salida del dashboard **no aparecen**.

> **Gotcha de privacidad**: la propia página del dashboard remite a [Help protect sensitive log data with masking](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html) al hablar de ver el contenido de entrada y salida. Habilitar el logging para poder observar **pone prompts y respuestas completas en un log group**, con todo lo que eso implica. El enmascaramiento y el permiso `logs:Unmask` se tratan en [Task 3.2 · Skill 3.2.2](../domain-3/task-3-2-seguridad-y-privacidad-de-datos.md#skill-322--sistemas-que-preservan-la-privacidad).

### Benchmarks de rendimiento y detección de anomalías de coste

Las dos últimas piezas del skill ya están desarrolladas y aquí solo corresponde el mapa:

| Pieza del skill | Mecanismo | Dónde |
| --- | --- | --- |
| **Performance benchmarks** | Harness de carga a tasas configurables contra golden dataset (GENPERF02-BP01) | [Skill 4.2.1](./task-4-2-latencia-y-throughput.md#benchmarking-qué-exige-genperf02-bp01) |
| **Cost anomaly detection** | AWS Cost Anomaly Detection: monitores gestionados o propios, severidad por anormalidad | [Skill 4.1.2](./task-4-1-costes-y-eficiencia-de-recursos.md#cost-anomaly-detection) |

> **Dato decisivo sobre las dos detecciones de anomalía**: son **dos servicios distintos** y el examen puede contraponerlos. **CloudWatch anomaly detection** actúa sobre **métricas**, en minutos, y detecta cambios de comportamiento técnico. **AWS Cost Anomaly Detection** actúa sobre **el gasto facturado**, con el retardo de los datos de facturación, y detecta desviaciones de coste. Un prompt que se duplicó de tamaño se ve en la primera en cinco minutos y en la segunda al día siguiente.

---

## Skill 4.3.3 — Observabilidad integrada y accionable

> *Desarrollar soluciones de observabilidad integradas para dar insights accionables en aplicaciones de FM (por ejemplo, usando dashboards de métricas operativas, visualizaciones de impacto de negocio, monitorización de compliance, trazabilidad forense y audit logging, tracking de interacción de usuario, tracking de patrones de comportamiento del modelo).*

### Dashboards de CloudWatch

De [Using Amazon CloudWatch dashboards](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Dashboards.html). Hay **dashboards automáticos prefabricados** y dashboards propios, y permiten monitorizar recursos en una sola vista **incluso repartidos entre Regiones distintas**.

Los tres usos que documenta, y el segundo es el que el skill llama "accionable":

| Uso | Detalle |
| --- | --- |
| **Vista única de salud** | Métricas y alarmas seleccionadas para evaluar la salud de recursos y aplicaciones **en una o más Regiones**, con **color elegible por métrica** para seguir la misma métrica entre gráficas |
| **Operational playbook** | Guía para el equipo **durante un evento operativo** sobre cómo responder a incidentes concretos |
| **Vista común compartida** | Medidas críticas compartidas por el equipo **para comunicar más rápido durante un evento** |

> **Dato decisivo**: la documentación describe el dashboard como **playbook operativo**, no solo como panel de gráficas. Es la diferencia que el skill pide con la palabra *accionable*: un dashboard que muestra veinte métricas sin decir qué hacer con ellas no cumple el enunciado. Los textos de un widget de tipo texto son parte del entregable.

Se crean desde consola, CLI o la operación **`PutDashboard`**, y admiten [variables](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_dashboard_variables.html) y varios [tipos de widget](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/create-and-work-with-widgets.html). La creación paso a paso está en [Creating a customized dashboard](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/create_dashboard.html).

Los permisos son granulares, y conviene conocerlos porque separan lectura de escritura:

| Permiso | Para qué |
| --- | --- |
| `cloudwatch:GetDashboard` y `cloudwatch:ListDashboards` | **Ver** dashboards |
| `cloudwatch:PutDashboard` | **Crear o modificar** |
| `cloudwatch:DeleteDashboards` | **Borrar** |

> **Dato decisivo para GenAI**: las **variables de dashboard** son lo que convierte un panel en reutilizable en una carga multi-modelo o multi-tenant. Una variable sobre `ModelId` permite el mismo dashboard para todos los modelos, y una sobre una dimensión propia (tenant, versión de prompt) permite comparar variantes de un A/B sin duplicar paneles.

### Cross-account: el caso multi-cuenta

Con **CloudWatch cross-account observability** se pueden construir dashboards en una cuenta de monitorización que:

- **Grafiquen métricas que residen en cuentas de origen**, y **una sola gráfica puede incluir métricas de varias cuentas**.
- **Creen alarmas en la cuenta de monitorización que vigilen métricas de cuentas de origen**.
- Vean eventos de log de log groups de cuentas de origen, y ejecuten consultas de Logs Insights sobre ellos: **una sola consulta puede abarcar varios log groups en varias cuentas**.
- Vean **nodos de cuentas de origen en un trace map de X-Ray**, filtrables por cuenta.

El detalle está en [CloudWatch cross-account observability](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Unified-Cross-Account.html). Señal visual útil: en una cuenta de monitorización aparece una **insignia azul de Monitoring account** arriba a la derecha en cada página que soporta la funcionalidad.

> Para una plataforma GenAI centralizada que sirve a varias cuentas de negocio, es el mecanismo que permite **una sola vista de coste y latencia por cuenta consumidora** sin replicar dashboards.

### Compliance, trazabilidad forense y audit logging

Las tres las cubre el Domain 3 y aquí corresponde el mapa, porque el skill las nombra desde el ángulo de la observabilidad:

| Pieza del skill | Mecanismo | Dónde |
| --- | --- | --- |
| **Compliance monitoring** | AWS Config conformance packs, Audit Manager, las ocho dimensiones de IA responsable | [Task 3.3 · Skill 3.3.3](../domain-3/task-3-3-governance-y-compliance.md#skill-333--governance-organizacional) |
| **Trazabilidad forense y audit logging** | CloudTrail por tipo de recurso, invocation logs, decision logs | [Task 3.3 · Skill 3.3.2](../domain-3/task-3-3-governance-y-compliance.md#skill-332--trazabilidad-y-tracking-de-fuentes-de-datos) |
| **Correlación entre fronteras asíncronas** | **Correlation ID único que sobreviva las fronteras asíncronas**, de AGENTSEC05 | [Task 3.4 · Skill 3.4.1](../domain-3/task-3-4-ia-responsable.md#respaldo-en-los-lenses) |

> **Dato decisivo que conecta este skill con Transaction Search**: los spans de `aws/spans` llevan **trace IDs de W3C** y admiten **atributos personalizados**. Ese es el vehículo natural del correlation ID que pide AGENTSEC05: un identificador que viaja en el span y sobrevive el salto por SQS o EventBridge, donde una traza de X-Ray sin más se rompe.

### Tracking de interacción de usuario y de comportamiento del modelo

Las dos últimas señales del skill, y cada una tiene su fuente:

| Señal | Fuente |
| --- | --- |
| **Tracking de interacción de usuario** | Las capturas de **interacciones de usuario final** de generative AI observability, más `requestMetadata` con el identificador de sesión y la **atribución de coste por usuario o rol** del dashboard |
| **Tracking de patrones de comportamiento del modelo** | Distribución de `gen_ai.response.finish_reasons`, longitud de salida, histograma de tokens de entrada en 6 rangos, y **anomaly detection** sobre todas ellas |

> **Gotcha de privacidad, y es el que cierra el task**: rastrear la interacción del usuario y el contenido de las respuestas exige **almacenar prompts y salidas**. La combinación de invocation logging con destino a CloudWatch Logs, spans con atributos de negocio y una tabla de invocaciones consultable **construye un registro completo de lo que cada usuario preguntó**. Las políticas de protección de datos de CloudWatch Logs, las políticas de retención y el `logs:Unmask` no son opcionales en este diseño: son parte de él.

### El dashboard mínimo de una aplicación GenAI

```
FILA 1 · SALUD
  Invocations · InvocationClientErrors · InvocationServerErrors
  InvocationThrottles          ← recordar: depende del retry del SDK
  alarma de anomalia sobre tokens por invocacion
FILA 2 · EXPERIENCIA
  TimeToFirstToken (solo si hay streaming)
  InvocationLatency  media, P90, P99
  distribucion de finish_reasons
FILA 3 · CONSUMO
  InputTokenCount · OutputTokenCount
  CacheReadInputTokenCount vs CacheWriteInputTokenCount
  histograma de peticiones por rango de tokens de entrada
FILA 4 · SEGURIDAD
  InvocationsIntervened por GuardrailPolicyType
  scores de contextual grounding
  ModelInvocationLogsS3DeliveryFailure   ← el audit trail se rompio
FILA 5 · NEGOCIO
  resoluciones sin escalado · turnos hasta resolucion
  tokens por resolucion · coste por respuesta correcta
FILA 6 · PLAYBOOK
  widget de texto: que hacer cuando cada alarma suena
```

> Las filas 1 a 3 salen de fábrica del dashboard de Model Invocations. La 4 exige mirar **otro namespace**, `AWS/Bedrock/Guardrails`. La 5 no existe si nadie la publica. Y la 6 es lo que convierte el dashboard en el playbook operativo que describe la documentación.

---

## Resumen operativo: observabilidad y métricas

| Si la pregunta menciona… | La respuesta apunta a |
| --- | --- |
| Observar una app GenAI construida con LangChain o LangGraph | **CloudWatch generative AI observability**: compatible con Strands, LangChain y LangGraph |
| Trazas de un modelo de terceros | Enviarlas estructuradas con el **SDK de ADOT** |
| Los dos dashboards preconstruidos | **Model Invocations** y **AgentCore agents** |
| Latencia en P90 y P99 de fábrica | **Generative AI observability**, no el namespace `AWS/Bedrock` |
| Atribución de coste por usuario o rol | El dashboard de generative AI observability |
| Dashboard de invocaciones vacío | Falta habilitar el **model invocation logging** a CloudWatch Logs |
| Detectar que los prompts crecieron | Widget **Requests grouped by input tokens**, en **6 rangos** |
| Los throttles no cuadran con la capacidad | Dependen de la **configuración de reintentos del SDK** |
| Del gráfico al contenido de la invocación | Tabla de Invocations → **Request ID** → panel derecho → **View in Logs Insights** |
| Saber qué guardrail y qué KB intervinieron | **Application Signals**: métricas por Guardrails ID y Knowledge Base ID |
| Los cuatro identificadores de Application Signals | **Model ID, Guardrails ID, Knowledge Base ID, Bedrock Agent ID** |
| Por qué se detuvo la generación | **`gen_ai.response.finish_reasons`** |
| Correlacionar parámetros usados con coste y calidad | Los atributos `gen_ai.request.*` más `gen_ai.usage.*` |
| Comparar coste y tokens entre modelos con el mismo prompt | **Transaction Search** sobre los atributos GenAI |
| Cuántos spans captura Transaction Search | **El 100 %** como logs; solo **un porcentaje** se indexa en X-Ray |
| Dónde acaban los spans | El log group **`aws/spans`**, con trace IDs de **W3C** |
| Tamaño máximo de una traza | **10.000 spans** |
| Extraer una métrica propia de los spans | **Metric filters** sobre `aws/spans` |
| Correlation ID que sobreviva una frontera asíncrona | **Atributos personalizados** de span en Transaction Search |
| Métricas de impacto de negocio | **No existen**: `PutMetricData` o metric filters |
| Efectividad del prompt como métrica de CloudWatch | **No existe**: hay que calcularla y publicarla |
| Tasa de hallucination como métrica | **No existe**: scores de **contextual grounding** más golden dataset |
| Calidad de respuesta como métrica | **No existe**: **Bedrock evaluations** |
| Alertar de una ráfaga de tokens sin falsos positivos | Banda de anomalía sobre **tokens por invocación**, no sobre totales |
| Detectar drift de respuesta | Anomalía sobre **longitud de salida**, `finish_reasons`, score de grounding |
| Alarma sin umbral fijo | **`ANOMALY_DETECTION_BAND`** con `ThresholdMetricId` |
| CloudWatch anomaly detection frente a Cost Anomaly Detection | **Métricas en minutos** frente a **gasto facturado con retardo** |
| Habilitar logging para observar y el riesgo que crea | Pone **prompts y respuestas completas** en un log group: enmascarar |
| Un dashboard que no dice qué hacer | La documentación lo describe como **operational playbook** |
| Reutilizar un dashboard entre modelos o tenants | **Variables de dashboard** |
| Permiso para crear un dashboard | **`cloudwatch:PutDashboard`**; ver exige `GetDashboard` y `ListDashboards` |
| Una gráfica con métricas de varias cuentas | **Cross-account observability** en una cuenta de monitorización |
| Una consulta de Logs Insights sobre varias cuentas | Soportado desde la cuenta de monitorización |
| El audit trail dejó de escribirse | Alarma sobre **`ModelInvocationLogsS3DeliveryFailure`** |
