# Task 4.2 — Latencia y throughput

[← Volver al índice](./README.md)

Skills cubiertos: **4.2.1**, **4.2.3**, **4.2.5**.

El Task 4.2 tiene seis skills y se reparte en dos archivos. Este cubre el eje de **capacidad y tiempo de respuesta**: cuánto tarda el sistema, cuánto puede procesar y con qué recursos. El eje de **calidad de lo recuperado y de lo generado** (skills 4.2.2, 4.2.4 y 4.2.6) está en [task-4-2-retrieval-y-parametros.md](./task-4-2-retrieval-y-parametros.md).

El marco oficial es el pilar de **Performance efficiency** del [Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/performance-efficiency.html), que define el rendimiento de un sistema GenAI como la capacidad de **entregar respuestas de alta calidad de forma consistente manteniendo una utilización óptima de recursos**.

---

## Skill 4.2.1 — Sistemas de IA responsivos

> *Crear sistemas de IA responsivos para abordar los tradeoffs entre latencia y coste y mejorar la experiencia de usuario con FMs (por ejemplo, usando pre-computación para consultas predecibles, modelos de Amazon Bedrock optimizados para latencia en aplicaciones sensibles al tiempo, peticiones en paralelo para workflows complejos, streaming de respuestas, benchmarking de rendimiento).*

### Las cinco métricas que el Lens considera rendimiento

Del pilar de [Performance efficiency](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/performance-efficiency.html). Conviene leerlas como una lista cerrada, porque el skill asume que "rendimiento" incluye la tercera, que no es temporal:

| Métrica | Definición oficial |
| --- | --- |
| **Inference latency** | Lo que tarda el modelo en generar una respuesta a un prompt. Crítica en aplicaciones en tiempo real |
| **Throughput** | Número de peticiones **concurrentes** que el modelo puede manejar **sin degradación** |
| **Response quality** | Exactitud, relevancia y coherencia, medidas contra un dataset de ground truth o contra las expectativas del usuario |
| **Resource utilization** | CPU, memoria y GPU: cuán eficientemente se aprovecha el cómputo |
| **Availability** | Porcentaje de tiempo que el sistema responde y puede servir peticiones |

Y los tres principios del pilar, que ordenan los seis skills del task:

| Principio | Qué exige |
| --- | --- |
| **Measure and validate performance systematically** | Frameworks de prueba, datasets de ground truth y load tests, para que las mejoras se basen en **medidas y no en suposiciones** |
| **Optimize model and vector operations** | Ajustar selección de modelo, parámetros de inferencia y dimensión de vector según requisitos **empíricos** |
| **Leverage managed services for operational efficiency** | Usar servicios gestionados para la infraestructura compleja |

> **Dato decisivo**: el primer principio cierra con una frase que es la tesis del task: las mejoras de rendimiento deben apoyarse en **medidas reales, no en suposiciones**. De ahí que GENPERF01 (establecer procesos de evaluación) preceda a GENPERF02 (mantener el rendimiento): sin baseline no hay optimización, solo cambios.

El pilar enumera además cinco retos comunes con su mitigación. Los dos que caen en este skill:

| Reto | Mitigación oficial |
| --- | --- |
| **Rendimiento inconsistente del modelo** | Frameworks de testing robustos, **control de versiones de modelos y prompts**, y monitorización continua de métricas |
| **Picos de tráfico inesperados** | Mecanismos de **auto-scaling**, rate limiting y throttling, y **diseñar para burst capacity** |

### Las dos latencias, que no miden lo mismo

Del namespace `AWS/Bedrock` en [Monitor bedrock-runtime inference using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html), cuyo catálogo completo está en [Task 3.3 · Skill 3.3.4](../domain-3/task-3-3-governance-y-compliance.md#métricas-de-runtime):

| Métrica | Qué mide | Dónde se publica |
| --- | --- | --- |
| **`InvocationLatency`** | Desde el envío **hasta el último token** | Todas las operaciones de inferencia |
| **`TimeToFirstToken`** | Hasta el **primer** token | **Solo en `ConverseStream` e `InvokeModelWithResponseStream`** |

> **Dato decisivo**: son la misma petición medida de dos formas, y optimizar una no mejora la otra. El streaming **no reduce `InvocationLatency`**: la respuesta completa tarda lo mismo. Lo que reduce es `TimeToFirstToken`, que es lo que el usuario percibe. Una pregunta que contraponga "latencia real normal pero usuarios quejándose" apunta a que **falta streaming**, no a que falte capacidad.
>
> Y la implicación inversa, menos conocida: **sin streaming no existe `TimeToFirstToken`**. Una aplicación que invoca en modo bufferizado no puede medir la latencia percibida con métricas de Bedrock, porque esa métrica no se emite.

Para agentes, la métrica equivalente es `TTFT`, junto a `InvocationCount` y `TotalTime`, en [Monitor Amazon Bedrock Agents using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-agents-cw-metrics.html).

### Streaming como palanca de latencia percibida

El detalle técnico completo (formato de salida, delimitadores, las cuatro vías de entrega al cliente, WebSocket, Lambda response streaming) está en [Task 2.4 · Skill 2.4.2](../domain-2/task-2-4-integraciones-api-fm.md#skill-242--interacción-en-tiempo-real-y-streaming). Lo que aporta este skill es la formulación que hace [GENPERF02-BP01](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02-bp01.html): implementar respuestas en streaming **mejora la latencia percibida por el usuario en las respuestas que no están en caché**.

Esa condición final importa: el streaming es la mitigación para lo que **no** se pudo cachear. Con un acierto de caché la respuesta llega en milisegundos y el streaming es irrelevante. El orden de intervención es cachear primero, y hacer streaming de lo que quede.

### Latency-optimized inference

De [Optimize model inference for latency](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html). **La funcionalidad está en preview release y sujeta a cambios.** Entrega tiempos de respuesta más rápidos **sin comprometer la exactitud**, y no requiere setup adicional ni fine-tuning: basta poner el parámetro de latencia a `optimized` en la llamada a la API de runtime.

```json
{
  "performanceConfig": {
    "latency": "standard | optimized"
  }
}
```

**Por defecto, todas las peticiones se enrutan por `standard`.**

Los cuatro modelos soportados, todos **a través de cross-Region inference**:

| Proveedor | Modelo | Model ID | Regiones |
| --- | --- | --- | --- |
| Amazon | **Nova Pro** | `amazon.nova-pro-v1:0` | `us-east-1`, `us-east-2` |
| Anthropic | **Claude 3.5 Haiku** | `anthropic.claude-3-5-haiku-20241022-v1:0` | `us-east-2`, `us-west-2` |
| Meta | **Llama 3.1 405B Instruct** | `meta.llama3-1-405b-instruct-v1:0` | `us-east-2` |
| Meta | **Llama 3.1 70B Instruct** | `meta.llama3-1-70b-instruct-v1:0` | `us-east-2`, `us-west-2` |

Los perfiles de inferencia que lo soportan están en [Supported Regions and models for inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html), y el mecanismo de cross-Region inference en [Increase throughput with cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html), desarrollado en [Task 1.2 · Skill 1.2.3](../domain-1/task-1-2-seleccion-y-configuracion-fm.md#cross-region-inference).

> **Gotcha de cuota y facturación**: al alcanzar la cuota de uso de optimización de latencia para un modelo, Bedrock **intenta servir la petición con latencia Standard**, y en ese caso **se factura a tarifas Standard**. El degradado es silencioso desde el punto de vista funcional: la petición no falla, solo deja de ir rápido. La configuración realmente servida es **visible en la respuesta de la API y en los logs de CloudTrail**, y las métricas de peticiones optimizadas aparecen en CloudWatch bajo **`model-id+latency-optimized`**.
>
> Consecuencia para el diseño del dashboard: si se agrupa la latencia solo por `ModelId`, el degradado a Standard queda invisible. Hay que mirar la dimensión que separa ambos modos.

> **Restricción importante**: **Llama 3.1 405B** soporta peticiones con un total de tokens de entrada y salida **hasta 11K**. Por encima de ese umbral, **se vuelve al modo standard**.

### Pre-computación de consultas predecibles

El skill nombra la pre-computación y el portal no le dedica página propia, así que conviene situarla por contraste con las capas de caché del [Skill 4.1.4](./task-4-1-costes-y-eficiencia-de-recursos.md#skill-414--sistemas-de-caching-inteligente):

| | **Caché** | **Pre-computación** |
| --- | --- | --- |
| **Cuándo se genera** | En el primer fallo, bajo demanda | **Antes de que nadie pregunte** |
| **Quién paga el primer usuario** | Él: sufre el fallo de caché | Nadie: la respuesta ya está |
| **Requisito** | Que las consultas se repitan | **Conocer las consultas de antemano** |
| **Paradigma de inferencia** | On-demand | **Batch**, que es un 50 % más barato |

> **Dato decisivo**: la pre-computación es la única técnica del task donde **la latencia percibida baja a la de una lectura y el coste baja a tarifa de batch a la vez**. Es la salida al tradeoff latencia-coste que enuncia el skill, y solo aplica cuando el conjunto de consultas es acotado y conocido: informes periódicos, FAQ, resúmenes de catálogo, briefings diarios.

El vehículo documentado es el [batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html) del [Skill 4.1.3](./task-4-1-costes-y-eficiencia-de-recursos.md#skill-413--sistemas-de-alto-rendimiento-batching-capacidad-y-escalado): se genera de noche lo que se va a preguntar de día, y la aplicación sirve desde el almacén.

### Peticiones en paralelo para workflows complejos

El paralelismo baja la latencia de un workflow cuando los pasos son independientes, y no la baja en absoluto cuando son secuenciales. La distinción decide la arquitectura:

```
SECUENCIAL (no paralelizable)        PARALELO (paralelizable)
recuperar → generar → validar        consultar 3 fuentes a la vez
   la salida de cada paso              agregar y generar una vez
   es la entrada del siguiente              │
        │                            latencia = la del paso mas lento
latencia = suma de los pasos                │
        │                            Step Functions: estado Map o Parallel
Palanca: acortar cada paso           Lambda concurrente
o eliminar alguno
```

> **Coste del paralelismo**: lanzar N peticiones a la vez consume N veces la cuota de TPM en el mismo minuto, así que el paralelismo **acerca el throttling**. Es la razón por la que este skill y el [Skill 4.2.3](#skill-423--optimización-de-throughput-del-fm) se leen juntos: paralelizar sin margen de cuota cambia latencia por errores `429`.

Los patrones de orquestación con Step Functions están en [Task 2.1](../domain-2/task-2-1-agentic-ai-y-herramientas.md), y la mecánica de reintentos con backoff que absorbe el throttling en [Task 2.4 · Skill 2.4.3](../domain-2/task-2-4-integraciones-api-fm.md#reintentos-del-sdk-los-tres-modos).

### Benchmarking: qué exige GENPERF02-BP01

De [Load test model endpoints](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02-bp01.html), la práctica que materializa el "performance benchmarking" del skill. El mecanismo que propone es un **test suite diseñado para simular la carga más alta esperada antes de la degradación prevista**.

El orden de trabajo en Bedrock: **revisar primero las métricas publicadas** de latencia y throughput del modelo si están disponibles y, si no lo están, **hacer benchmark contra un golden dataset** propio o de un tercero. Los resultados alimentan la selección de modelo. Y si el modelo tiene limitaciones de throughput, las dos salidas documentadas son **Provisioned Throughput** o **endpoints de cross-Region inference**.

Los tres pasos de implementación, con el detalle que los hace útiles:

1. Consultar la política de IA de la organización para saber **qué métricas de rendimiento son las apropiadas**.
2. Desarrollar un **harness de carga que prompte al modelo a tasas configurables**, con capacidad de probar contra **golden datasets internos y datos de benchmarking externos de terceros**.
3. Recoger la información de rendimiento y **evaluar con cuidado dónde está el cuello de botella**.

### La taxonomía de cuellos de botella

El paso 3 de GENPERF02-BP01 es la aportación más valiosa de la práctica, porque clasifica el cuello de botella y a cada clase le asigna remedios distintos:

| Origen del cuello de botella | Remedios documentados |
| --- | --- |
| **La capacidad del modelo de servir peticiones** | Técnicas de **customización de modelo**, o **aumentar el tamaño y la potencia del endpoint** de inferencia |
| **Heredado de los patrones de uso** | **Cross-Region inference**, **prompt caching**, o **un paradigma de inferencia completamente distinto** |

> **Dato decisivo**: es una taxonomía de dos ramas y los remedios **no son intercambiables**. Comprar un endpoint más grande no arregla un patrón de uso que envía el mismo documento en cada turno; activar prompt caching no arregla un modelo que no da el throughput necesario. Diagnosticar la rama antes de gastar es el contenido del skill.

En SageMaker AI, la misma práctica añade que hay que probar **respecto al tipo y tamaño de instancia del endpoint**, y que según el modelo puede haber margen para modificar parámetros de inferencia o aplicar **quantization o LoRA**.

---

## Skill 4.2.3 — Optimización de throughput del FM

> *Implementar optimización de throughput del FM para abordar los retos de throughput específicos de las cargas GenAI (por ejemplo, usando optimización del procesamiento de tokens, estrategias de batch inference, gestión de invocaciones concurrentes).*

### Por qué el throughput de un FM es un problema distinto

La definición del Lens ya lo adelanta: throughput es el número de peticiones **concurrentes sin degradación**. Pero en una carga GenAI la unidad de capacidad no es la petición, es el **token por minuto**, y eso rompe tres supuestos del escalado tradicional:

| Supuesto tradicional | Qué pasa con un FM |
| --- | --- |
| Todas las peticiones cuestan parecido | Una petición puede costar 100 tokens o 100.000 |
| La capacidad se mide en peticiones por segundo | Se mide en **RPM y TPM a la vez**, y se agota la que se agote primero |
| El coste de una petición se conoce al terminar | **Se reserva por adelantado**: tokens de entrada más `maxTokens` |

> **Dato decisivo**: el throttling de Bedrock reserva por adelantado los tokens de entrada **más `max_tokens`**, según el aviso de `EstimatedTPMQuotaUsage` de [Task 3.3 · Skill 3.3.4](../domain-3/task-3-3-governance-y-compliance.md#métricas-de-runtime). Consecuencia directa y contraintuitiva: **bajar `maxTokens` aumenta el throughput efectivo** aunque las respuestas reales no cambien de tamaño, porque se reserva menos cuota por petición. Es la palanca de throughput más barata que existe y no cuesta calidad si el techo estaba sobredimensionado.

### Optimización del procesamiento de tokens

Las tres palancas, en orden de coste de implementación:

```
1 · Reducir lo que se reserva     → bajar maxTokens al techo real
                                     libera cuota TPM por peticion
2 · Reducir lo que se envia       → GENCOST03-BP01, prompt mas corto
                                     context pruning del historico
3 · Reducir lo que se factura     → prompt caching
                                     CacheReadInputTokenCount NO cuenta
                                     para la cuota TPM
```

> **Dato decisivo para throughput, no solo para coste**: los tokens leídos de caché **no cuentan para la cuota de TPM**, mientras los escritos sí. El prompt caching es por tanto una palanca de **throughput**: con un prefijo estable y acertando en caché, la misma cuota sirve más peticiones. Los que escriben caché, en cambio, consumen cuota igual que cualquier token de entrada. El detalle está en el [Skill 4.1.1](./task-4-1-costes-y-eficiencia-de-recursos.md#las-métricas-de-token-y-lo-que-cada-una-cuenta-para-la-cuota).

En modelos autoalojados el frente es otro. De GENPERF02-BP01: los **contenedores LMI (large model inference)** de SageMaker AI ofrecen opciones de **batching de peticiones**, opciones de **quantization**, y soporte de las versiones más recientes de **vLLM**, una librería optimizada para servir e inferir con LLMs. La base de LMI está en [Task 2.2 · Skill 2.2.2](../domain-2/task-2-2-despliegue-de-modelos.md#contenedores-especializados-lmi) y la página oficial en [Model parallelism and large model inference](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference.html).

### Batch inference como estrategia de throughput

La mecánica completa del job está en el [Skill 4.1.3](./task-4-1-costes-y-eficiencia-de-recursos.md#skill-413--sistemas-de-alto-rendimiento-batching-capacidad-y-escalado). Lo que corresponde aquí es cuándo usarlo, y GENPERF02-BP01 lo formula sin ambigüedad: batch inference es **más eficiente para procesar grandes volúmenes de prompts**, especialmente al **evaluar, experimentar o hacer análisis offline**, y permite **agregar respuestas y analizarlas en lote**.

> **Restricción importante**: la misma práctica advierte que **el procesamiento en lote introduce latencia adicional por definición** frente a la inferencia en tiempo real, así que solo debe usarse **en escenarios donde el load testing permita ejecuciones de job largas**. Batch no es una optimización de throughput gratuita: es un intercambio explícito de latencia por volumen y por un 50 % de coste.

### Gestión de invocaciones concurrentes

El skill pide gestionarlas, y las palancas están repartidas por capas. La vista conjunta:

| Capa | Mecanismo | Dónde está el detalle |
| --- | --- | --- |
| **Cliente** | `retry_mode` del SDK (`standard`, `adaptive`, `legacy`), retry quota, `AWS_MAX_ATTEMPTS` | [Task 2.4 · Skill 2.4.3](../domain-2/task-2-4-integraciones-api-fm.md#reintentos-del-sdk-los-tres-modos) |
| **Borde** | Usage plans y rate limiting de API Gateway, por consumidor | [Task 2.4 · Skill 2.4.3](../domain-2/task-2-4-integraciones-api-fm.md#rate-limiting-en-api-gateway) |
| **Cola** | SQS para desacoplar la llegada del procesamiento | [Task 2.4 · Skill 2.4.1](../domain-2/task-2-4-integraciones-api-fm.md) |
| **Cómputo** | Concurrencia reservada y provisionada de Lambda, escalable con Application Auto Scaling | [Skill 4.2.5](#skill-425--asignación-eficiente-de-recursos) |
| **Modelo** | Tier on-demand, model units, Provisioned Throughput, cross-Region inference | [Task 2.2 · Skill 2.2.1](../domain-2/task-2-2-despliegue-de-modelos.md#límites-y-cuotas-por-tier) |

> **Gotcha del modo `adaptive`**: el `retry_mode` adaptativo del SDK **modera el ritmo de envío del cliente** ante throttling, lo que reduce los `429` pero también **reduce el throughput observado**. Es la elección correcta cuando el objetivo es completar el trabajo sin errores, y la incorrecta cuando el objetivo es latencia por petición.

La métrica que cierra el diagnóstico es **`InvocationThrottles`**, que en `AWS/Bedrock` **no cuenta ni como `Invocations` ni como error**. Una carga con throughput insuficiente puede tener cero errores y cero invocaciones perdidas en apariencia, mientras `InvocationThrottles` sube.

### El techo real

Los rangos de RPM y TPM por tier (Flex 10–100 RPM y 5K–50K TPM, Standard 100–500 y 50K–150K, Priority 500–1000+ y 150K–300K+), el hecho de que son **soft limits ampliables** y que hay **burst capacity en todos los tiers**, están en [Task 2.2 · Skill 2.2.1](../domain-2/task-2-2-despliegue-de-modelos.md#límites-y-cuotas-por-tier). Las cuotas exactas por Región y modelo, en [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html).

---

## Skill 4.2.5 — Asignación eficiente de recursos

> *Crear sistemas de asignación eficiente de recursos específicamente para cargas de FM (por ejemplo, usando planificación de capacidad para requisitos de procesamiento de tokens, monitorización de utilización para patrones de prompt y completion, configuraciones de auto-scaling optimizadas para patrones de tráfico de GenAI).*

Este skill se solapa con el [4.1.3](./task-4-1-costes-y-eficiencia-de-recursos.md#skill-413--sistemas-de-alto-rendimiento-batching-capacidad-y-escalado), y el reparto es deliberado: allí se trata **comprar capacidad** (tiers, model units, Provisioned Throughput, batch); aquí, **escalar la que ya se tiene según el patrón de tráfico**, y **medir la utilización**.

### Las dos políticas de escalado de un endpoint, y cuándo cada una

De [Auto scaling policy overview](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling-policy.html). Para escalar automáticamente hay **dos opciones**, y la recomendación oficial es clara: **en la mayoría de los casos, target tracking**.

| | **Target tracking** | **Step scaling** |
| --- | --- | --- |
| **Cómo decide** | Se elige una métrica de CloudWatch y un **valor objetivo**; el escalado **crea y gestiona las alarmas** y calcula el ajuste | Ajustes escalonados que **varían según el tamaño del incumplimiento** de la alarma |
| **Cuándo** | **Recomendado por defecto** | Configuración avanzada: especificar **cuántas instancias desplegar bajo qué condiciones** |
| **Métricas** | Predefinidas (por nombre, desde consola o código) o personalizadas | — |

El ejemplo oficial de target tracking: una política sobre la métrica predefinida **`InvocationsPerInstance`** con **valor objetivo 70** mantiene esa métrica en 70 o cerca.

> **Dato decisivo**: **hay que usar step scaling si se quiere que un endpoint escale desde cero instancias activas**. Target tracking no puede arrancar desde cero. Es el requisito que decide la política cuando el objetivo es escalar a cero para ahorrar, documentado en [Scale an endpoint to zero instances](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling-zero-instances.html).

Y una tercera vía que no es una política sino una acción programada: el **escalado por calendario**, que crea acciones de escalado en momentos concretos, una vez o de forma recurrente. Tras ejecutarse, la política sigue decidiendo dinámicamente.

> **Gotcha de herramienta**: el escalado programado **solo se gestiona desde la AWS CLI o la API de Application Auto Scaling**, no desde la consola de SageMaker AI. Para una carga GenAI con estacionalidad conocida (picos en horario de oficina, valles de noche), esto significa que la configuración vive en IaC, no en la consola.

### Límites y periodo de enfriamiento

| Ajuste | Regla |
| --- | --- |
| **Mínimo** | Debe ser **al menos 1**, y menor o igual que el máximo |
| **Máximo** | Mayor o igual que el mínimo. **SageMaker AI no impone un límite superior** |
| **Cooldown de scale-in y scale-out** | **300 segundos cada uno por defecto** |

Las tres formas de fijar los límites: la consola, `--min-capacity` y `--max-capacity` en `register-scalable-target`, o los parámetros `MinCapacity` y `MaxCapacity` de [`RegisterScalableTarget`](https://docs.aws.amazon.com/autoscaling/application/APIReference/API_RegisterScalableTarget.html).

El cooldown protege del sobre-escalado bloqueando el borrado de instancias en scale-in y limitando su creación en scale-out. La guía de ajuste es simétrica y se puede recitar: si las instancias **entran y salen demasiado rápido**, subir el valor, lo que suele pasar con **tráfico muy picudo o con varias políticas definidas sobre la misma variante**; si **no entran lo bastante rápido** para absorber el tráfico, bajarlo.

> **Dato decisivo**: si el tráfico de una variante **llega a cero**, SageMaker AI **escala hacia dentro hasta el mínimo especificado y emite métricas con valor cero**. Esas métricas a cero no son una caída del endpoint: son el comportamiento documentado. Una alarma mal construida sobre invocaciones a cero dispara cada noche.

Y el truco operativo que documenta la propia página: se puede **escalar hacia fuera a mano subiendo el mínimo**, y **hacia dentro a mano bajando el máximo**.

### Monitorización de utilización: las enhanced metrics

El skill pide "monitorización de utilización para patrones de prompt y completion". En Bedrock eso son las métricas de token del [Skill 4.1.1](./task-4-1-costes-y-eficiencia-de-recursos.md#las-métricas-de-token-y-lo-que-cada-una-cuenta-para-la-cuota). En un endpoint propio, la respuesta es [Amazon SageMaker AI enhanced metrics for inference endpoints](https://docs.aws.amazon.com/sagemaker/latest/dg/monitoring-cloudwatch-enhanced-metrics.html), que aporta granularidad por instancia, por contenedor y **por GPU**.

Las tres granularidades y su dimensión:

| Granularidad | Dimensión | Disponibilidad |
| --- | --- | --- |
| **Por instancia** | **`InstanceId`** | **Todos** los endpoints en tiempo real |
| **Por contenedor** | **`ContainerId`** | Endpoints que usan **inference components** |
| **Por GPU** | **`AcceleratorId`** | Métricas de utilización de GPU |

Se habilitan poniendo **`EnableEnhancedMetrics`** a `True` en el parámetro [`MetricsConfig`](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_MetricsConfig.html) al llamar a [`CreateEndpointConfig`](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpointConfig.html). El segundo campo de `MetricsConfig` es el que más juego da:

| Parámetro | Valores | Por defecto |
| --- | --- | --- |
| `EnableEnhancedMetrics` | Booleano | **`False`** |
| **`MetricPublishFrequencyInSeconds`** | **10, 30, 60, 120, 180, 240, 300** | **60** |

> **Dato decisivo, y es una asimetría fácil de suspender**: cuando `EnableEnhancedMetrics` está en **`False`**, el intervalo de publicación **se aplica solo a las métricas de utilización**, y las de invocación siguen publicándose **al intervalo por defecto de 60 segundos**. Cuando está en **`True`**, se aplica **a las dos**. Para detectar un pico de 15 segundos en las invocaciones hace falta bajar la frecuencia **y** habilitar enhanced metrics; solo lo primero no basta.

Los **tres namespaces** en los que aparecen las dimensiones nuevas:

| Namespace | Qué contiene |
| --- | --- |
| **`/aws/sagemaker/Endpoints`** | Métricas de **utilización** de todos los endpoints en tiempo real |
| **`AWS/SageMaker`** | Métricas de **invocación** |
| **`/aws/sagemaker/InferenceComponents`** | Métricas de **utilización de inference components** |

> **Gotcha de despliegue**: `MetricsConfig` se fija **a nivel de configuración de endpoint**, así que **no se pueden aplicar ajustes distintos a inference components individuales del mismo endpoint**. Y para habilitarlo en un endpoint existente hay que crear una configuración nueva y llamar a [`UpdateEndpoint`](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpoint.html), lo que **dispara un despliegue blue/green o rolling**, y **las métricas mejoradas no aparecen hasta que ese despliegue termina**. Activar observabilidad no es una operación gratuita ni instantánea.

Los Multi-Container Endpoints soportan las métricas mejoradas **a nivel de instancia pero no a nivel de contenedor**.

```python
import boto3

sagemaker = boto3.client("sagemaker")

sagemaker.create_endpoint_config(
    EndpointConfigName="fm-endpoint-config-v3",
    ProductionVariants=[
        {
            "VariantName": "principal",
            "ModelName": "mi-modelo-afinado",
            "InstanceType": "ml.g5.2xlarge",
            "InitialInstanceCount": 2,
        }
    ],
    MetricsConfig={
        # Sin esto no hay dimensiones InstanceId, ContainerId ni AcceleratorId.
        "EnableEnhancedMetrics": True,
        # Con enhanced metrics activo, esta frecuencia aplica tambien a las
        # metricas de invocacion, no solo a las de utilizacion.
        "MetricPublishFrequencyInSeconds": 10,
    },
)
```

### El contraste que resume el skill

```
CARGA DE BEDROCK                        ENDPOINT PROPIO EN SAGEMAKER AI
──────────────────────────────          ────────────────────────────────
Que se mide
  InputTokenCount                         InvocationsPerInstance
  OutputTokenCount                        utilizacion de CPU, memoria, GPU
  CacheRead / CacheWrite                  por InstanceId, ContainerId,
  InvocationThrottles                       AcceleratorId
  TimeToFirstToken                        frecuencia de 10 s a 300 s
  InvocationLatency
        │                                       │
Que se ajusta                            Que se ajusta
  tier on-demand                           target tracking (por defecto)
  model units                              step scaling (para salir de cero)
  Provisioned Throughput                   scheduled (solo CLI o API)
  maxTokens (libera cuota)                 min >= 1, max sin tope
  cross-Region inference                   cooldown 300 s por defecto
        │                                       │
Quien escala                             Quien escala
  el servicio, dentro del tier             Application Auto Scaling
  tu, comprando capacidad                  con las alarmas que el crea
```

> La diferencia de fondo: en Bedrock **la utilización no es observable** porque la infraestructura no es tuya, así que se monitoriza **consumo** (tokens, throttles) y se ajusta **compra**. En un endpoint propio se monitoriza **utilización** (CPU, memoria, GPU por instancia) y se ajusta **número de instancias**. Aplicar el vocabulario de uno al otro es el error que las preguntas de este skill suelen explotar.

---

## Resumen operativo: latencia y throughput

| Si la pregunta menciona… | La respuesta apunta a |
| --- | --- |
| Qué cuenta como rendimiento en el Lens | Latencia, **throughput**, **calidad de respuesta**, utilización y disponibilidad |
| Mejoras basadas en suposiciones | El primer principio lo prohíbe: **medir y validar sistemáticamente** |
| Latencia real normal y usuarios quejándose | Falta **streaming**: optimiza `TimeToFirstToken`, no `InvocationLatency` |
| `TimeToFirstToken` no aparece | Solo existe en **`ConverseStream` e `InvokeModelWithResponseStream`** |
| Latencia hasta el último token | **`InvocationLatency`** |
| Streaming cuando hay acierto de caché | Irrelevante: el streaming cubre **lo que no está en caché** |
| Activar latencia optimizada | `performanceConfig.latency = "optimized"`; por defecto **`standard`** |
| Modelos con latencia optimizada | **4**: Nova Pro, Claude 3.5 Haiku, Llama 3.1 405B y 70B, vía cross-Region |
| Se agotó la cuota de latencia optimizada | Se sirve en **Standard y se factura a tarifa Standard**, sin fallar |
| Ver si una petición fue optimizada | Respuesta de la API, **CloudTrail**, y métricas bajo **`model-id+latency-optimized`** |
| Llama 3.1 405B con más de 11K tokens | **Vuelve a modo standard** |
| Consultas conocidas de antemano | **Pre-computación** con batch: latencia de lectura y tarifa de batch |
| Paralelizar un workflow secuencial | No baja la latencia: **la salida de cada paso alimenta el siguiente** |
| Paralelizar sin margen de cuota | Cambia latencia por **`429`**: N peticiones consumen N veces TPM |
| Cómo hacer benchmark si no hay métricas publicadas | **Golden dataset** propio o de tercero, con harness a **tasas configurables** |
| El modelo no da el throughput necesario | **Provisioned Throughput** o **cross-Region inference** |
| Cuello de botella en la capacidad del modelo | **Customización** o **endpoint más grande** |
| Cuello de botella heredado del patrón de uso | **Cross-Region inference, prompt caching o otro paradigma** |
| Subir el throughput sin tocar el prompt | **Bajar `maxTokens`**: el throttling reserva entrada más `maxTokens` |
| Prompt caching como palanca de throughput | Sí: **cache-read no cuenta para la cuota TPM**; cache-write sí |
| Batching y quantization en un modelo propio | Contenedores **LMI** con soporte de **vLLM** |
| Batch inference y latencia | **Añade latencia por definición**: solo si el load test permite jobs largos |
| Reducir `429` a costa de throughput | `retry_mode` **`adaptive`**, que modera el ritmo del cliente |
| Throttling que no aparece como error | **`InvocationThrottles`** no cuenta como `Invocations` ni como error |
| Política de escalado por defecto | **Target tracking**, con las alarmas gestionadas por el servicio |
| Escalar un endpoint desde cero instancias | **Obliga a step scaling** |
| Escalado por calendario | **Solo desde CLI o API** de Application Auto Scaling |
| Mínimo y máximo de instancias | Mínimo **≥ 1**; máximo **sin tope impuesto** por SageMaker AI |
| Instancias que entran y salen demasiado rápido | **Subir el cooldown**, que por defecto es **300 s** |
| Métricas a cero cada noche | Tráfico a cero: escala al mínimo y **emite métricas con valor cero** |
| Escalar a mano | **Subir el mínimo** para salir, **bajar el máximo** para entrar |
| Utilización por instancia, contenedor o GPU | **Enhanced metrics**: `InstanceId`, `ContainerId`, `AcceleratorId` |
| Publicar métricas cada 10 segundos | `MetricPublishFrequencyInSeconds`; valores 10 a 300, por defecto **60** |
| Invocaciones que siguen a 60 s pese a bajar la frecuencia | Falta **`EnableEnhancedMetrics: True`** |
| Ajustes de métricas por inference component | **No se puede**: `MetricsConfig` es por configuración de endpoint |
| Las enhanced metrics no aparecen | Requieren **`UpdateEndpoint`** y esperar al despliegue blue/green o rolling |
| Utilización de CPU o GPU de un modelo de Bedrock | **No es observable**: se mide consumo de tokens, no utilización |
