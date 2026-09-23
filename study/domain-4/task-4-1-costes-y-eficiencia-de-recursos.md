# Task 4.1 — Optimización de costes y eficiencia de recursos

[← Volver al índice](./README.md)

Skills cubiertos: **4.1.1**, **4.1.2**, **4.1.3**, **4.1.4**.

El marco oficial de este task es el pilar de **Cost optimization** del [Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/cost-optimization.html), que ningún skill nombra pero que ordena los cuatro. Sus tres principios, y el skill al que corresponde cada uno:

| Principio del Lens | Qué exige | Skill |
| --- | --- | --- |
| **Optimize model and inference selection** | Elegir modelo y paradigma de inferencia alineados con los requisitos reales de rendimiento, sin sobreaprovisionar | 4.1.2, 4.1.3 |
| **Control resource consumption parameters** | Controlar las variables que mueven el coste directamente: longitud de prompt, tamaño de respuesta, dimensión de vector | 4.1.1 |
| **Design workflow boundaries** | Poner límites y condiciones de salida para que ningún workflow consuma recursos sin freno | 4.1.1, y los agentes en 4.1.4 |

Las cinco preguntas del pilar, con su cobertura en estos materiales:

```
GENCOST01  Model selection and cost optimization   → 4.1.2
GENCOST02  Generative AI pricing model             → 4.1.2, 4.1.3
GENCOST03  Cost-aware prompting                    → 4.1.1, 4.1.4
GENCOST04  Cost-informed vector stores             → Task 1.4 y Task 1.5 de Domain 1
GENCOST05  Cost-informed agents                    → 4.1.1 (stopping conditions)
```

---

## Skill 4.1.1 — Sistemas de eficiencia de tokens

> *Desarrollar sistemas de eficiencia de tokens para reducir los costes de FM manteniendo la efectividad (por ejemplo, usando estimación y tracking de tokens, optimización de la ventana de contexto, controles de tamaño de respuesta, compresión de prompt, poda de contexto, limitación de respuesta).*

### Las cuatro palancas de GENCOST03

De [Cost-aware prompting](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost03.html). La pregunta que plantea el Lens es *cómo se diseñan los prompts para optimizar coste*, y da cuatro prácticas. Las cuatro caben en este skill:

| Práctica | Qué ataca | Riesgo si no se implementa |
| --- | --- | --- |
| [**GENCOST03-BP01**](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost03-bp01.html) Optimizar la longitud del prompt | Tokens de entrada | Medio |
| [**GENCOST03-BP02**](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost03-bp02.html) Controlar la longitud de la respuesta | Tokens de salida | Medio |
| [**GENCOST03-BP03**](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost03-bp03.html) Implementar prompt caching | Tokens de entrada repetidos | Medio |
| [**GENCOST03-BP04**](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost03-bp04.html) Anotar la entrada de usuario para filtrado consciente del coste | Unidades de texto del guardrail | Medio |

> **Dato decisivo**: GENCOST03-BP01 explica por qué acortar el prompt importa **incluso cuando no se paga por token**. Con infraestructura autoalojada o con Provisioned Throughput, un prompt más largo **requiere más tiempo de computación y aumenta la escala de infraestructura necesaria**. Con modelos gestionados, el efecto es directo sobre el coste por inferencia. No hay paradigma en el que un prompt inflado sea gratis.

### Acortar el prompt: las dos vías que ofrece Bedrock

GENCOST03-BP01 sugiere algo poco intuitivo: **usar un LLM aparte para acortar el prompt** sin perder rendimiento, y nombra la optimización de prompts de Bedrock como herramienta. De [Optimize and migrate prompts in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-optimization-migration.html) hay **dos** opciones, y confundirlas es un error de examen:

| | [**Simple optimization**](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-optimize.html) | [**Advanced Prompt Optimization (AdvPO)**](https://docs.aws.amazon.com/bedrock/latest/userguide/advanced-prompt-optimization-how.html) |
| --- | --- | --- |
| **Qué hace** | Reescritura **heurística** y rápida de un prompt corto para un modelo | Optimización **iterativa dirigida por tu evaluación** |
| **Tamaño de entrada** | Prompts de **aproximadamente 1.000 tokens o menos** | Plantillas de cualquier longitud que quepa en la ventana de contexto |
| **Entrada** | Un solo texto de prompt | Hasta **10 plantillas por job**, con hasta **100 samples de evaluación por plantilla** |
| **Modelos** | **1** | Hasta **5 comparados simultáneamente** (baseline más 4 candidatos) |
| **Evaluación** | **Ninguna** | Criterios de dirección en lenguaje natural, rúbrica **LLM-as-a-judge**, o **función Lambda** propia |
| **Salida** | Prompt reescrito, al instante | Plantillas optimizadas con **scores de evaluación, estimaciones de coste y latencia por modelo** |
| **Ejecución** | **Sincrónica**, segundos | **Job asíncrono**, de 15 minutos a horas |
| **Multimodal** | No | Sí: JPG, JPEG, PNG, GIF, WebP y PDF |
| **Migración de modelo** | Parcial: reescribe, pero sin comparación lado a lado | Sí, compara el modelo actual contra candidatos |

La API de la vía simple es [`OptimizePrompt`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_OptimizePrompt.html), y la recomendación oficial es **optimizar prompts en inglés** para obtener mejores resultados.

> **Dato decisivo**: AdvPO devuelve **estimaciones de coste y latencia por modelo** junto a los scores. Es la única herramienta del portal que produce las tres dimensiones del ratio precio-rendimiento del [Skill 4.1.2](#skill-412--frameworks-de-selección-de-modelo-coste-efectiva) en una sola ejecución.

Dos detalles operativos de AdvPO que se pasan por alto. El primero: por defecto el optimizador **reescribe cualquier parte de la plantilla**, y para acotarlo hay que envolver secciones en etiquetas `<advpo:optimize>` o `<advpo:exclude>`.

```json
{
  "comentario": "Solo se optimiza lo que va dentro de advpo:optimize.",
  "plantilla": "Eres un agente de atencion al cliente. Se cortes y profesional.\n<advpo:optimize>Al responder una reclamacion, resume el problema y propon una resolucion.</advpo:optimize>\nNunca reveles precios internos ni informacion de empleados."
}
```

El segundo: las entradas multimodales viajan en el payload junto al prompt, pero **no deben referenciarse en una variable `{{placeholder}}`**.

> **Gotcha de calidad**: la documentación insiste en que **tanto el dataset como el código de la métrica moldean la calidad de la optimización**. El sistema usa el dataset para probar candidatos de prompt, y **lee el código de la métrica, incluidos su texto fuente y sus docstrings, para entender qué significa "bueno"** y diagnosticar dónde fallan los prompts. Un evaluador Lambda sin docstring optimiza peor.

### Controlar la longitud de la respuesta

GENCOST03-BP02 va más allá del parámetro de longitud. Su aportación es **introducir determinismo** cuando no hace falta texto libre: instruir al modelo para que evalúe su respuesta contra un conjunto de opciones con clave y devuelva solo la clave.

El ejemplo oficial cierra la plantilla de prompt pidiendo que, si tras evaluar toda la información disponible la respuesta es afirmativa, responda solo con la palabra `True`, y en caso contrario `False` con explicación detallada. El efecto es doble: respuestas más cortas **y determinismo introducido en el sistema para el caso afirmativo**.

Los pasos que lista la práctica, en orden: definir un esquema de respuesta minimalista (por ejemplo `0` para afirmativo y `1` para rechazo), informar al modelo del esquema en el prompt, introducir un control de longitud de respuesta, fijar el **límite duro** con el hiperparámetro de longitud, y seguir probando.

### Anotar la entrada para no pagar por filtrar lo que ya es de confianza

GENCOST03-BP04 es la práctica menos conocida del pilar, y la que conecta coste con seguridad. La idea: los guardrails facturan por **unidades de texto**, así que filtrar el prompt completo en cada turno paga por evaluar contenido que ya se sabe de confianza. Con [input tags](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html) se marca solo la parte que hay que filtrar.

El reparto que documenta la práctica:

| Tipo de aplicación | Qué se etiqueta | Qué se deja sin etiquetar |
| --- | --- | --- |
| **RAG** | Solo las consultas del usuario | Los pasajes recuperados |
| **Chat** | El mensaje nuevo del usuario | El histórico de conversación |
| **Moderación de contenido** | Contenido generado por usuarios | Contenido ya verificado |
| **Procesamiento de documentos** | Los fragmentos de texto extraído que requieren revisión | El material fuente de confianza |

La mecánica: etiquetas de estilo XML con un **sufijo aleatorio único por petición**, de 1 a 20 caracteres alfanuméricos, declarado en `guardrailConfig` mediante `tagSuffix`. El sufijo aleatorio existe **para reducir ataques de prompt injection**: sin él, un atacante podría cerrar la etiqueta e inyectar contenido fuera del bloque filtrado.

> **Restricción importante**: los input tags **no se soportan con la API `ApplyGuardrail`**. Para aprovecharlos hay que implementar el filtrado en el lado de la aplicación.

### Contar antes de pagar

La estimación previa de tokens con `CountTokens`, que es gratis y coincide con lo que se facturaría, está desarrollada en [Task 2.5 · Skill 2.5.1](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#gestión-de-límites-de-tokens), incluidos el formato del `body` por API, los permisos y la excepción de los modelos Claude que exigen `bedrock-mantle`. Lo que corresponde aquí es la consecuencia económica: **es el único punto del flujo donde se puede rechazar una petición antes de gastar**.

### Las métricas de token y lo que cada una cuenta para la cuota

El catálogo completo del namespace `AWS/Bedrock` está en [Task 3.3 · Skill 3.3.4](../domain-3/task-3-3-governance-y-compliance.md#métricas-de-runtime). Las cuatro que sostienen este skill, de [Monitor bedrock-runtime inference using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html):

| Métrica | Factura | Cuenta para la cuota TPM |
| --- | --- | --- |
| `InputTokenCount` | Tarifa estándar de entrada | Sí |
| `OutputTokenCount` | Tarifa estándar de salida | Sí |
| `CacheReadInputTokenCount` | **Tarifa reducida de cache-read** | **No** |
| `CacheWriteInputTokenCount` | Puede ser **superior** a la estándar de entrada | **Sí** |

> **Dato decisivo**: la asimetría de la caché es lo que decide si el prompt caching sale rentable. Leer de caché es más barato **y libera cuota**; escribir a caché puede costar más que no cachear **y consume cuota**. Un prefijo que cambia en cada petición escribe siempre y no lee nunca: el peor de los dos mundos.

### Poner límites al workflow: GENCOST05-BP01

De [Create stopping conditions to control long-running workflows](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost05-bp01.html), la única práctica de [GENCOST05](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost05.html) y **la de riesgo más alto de todo el pilar de coste: Alto**, frente al Medio de las demás.

El resultado deseado que enuncia es la frase que resume el skill: **el coste máximo del runtime de un agente debe poder predecirse a partir de las condiciones de parada implementadas**. Si no se puede predecir, no hay condiciones de parada suficientes.

Los tres pasos, con el detalle que importa:

1. **Estimar el tiempo máximo** que el agente necesita, incluyendo **tiempos de respuesta del modelo, tiempos de ejecución de herramienta y latencia de red**.
2. **Implementar condiciones de parada** que permitan llegar a esa duración máxima: un mecanismo de timeout como el de Bedrock, o en la capa de prompt flow, o en una capa de abstracción propia.
3. **Rearquitecturar** para facilitarlas: timeouts en las herramientas externas (Lambda, endpoints de API), **verificar que los prompts saben manejar una respuesta de timeout**, y fijar **límites de token en las respuestas del modelo para simular un timeout** cortando generaciones largas.

> **Dato decisivo**: el paso 3 usa el límite de tokens **como mecanismo de parada**, no solo como control de coste. Es la respuesta a una pregunta sobre cómo acotar un agente cuando no se puede instrumentar el bucle: se acota lo que el modelo puede escribir.

---

## Skill 4.1.2 — Frameworks de selección de modelo coste-efectiva

> *Crear frameworks de selección de modelo coste-efectivos (por ejemplo, usando evaluación del tradeoff coste-capacidad, uso escalonado de FM según la complejidad de la consulta, balance del coste de inferencia frente a la calidad de respuesta, medición del ratio precio-rendimiento, patrones de inferencia eficientes).*

### GENCOST01-BP01: empezar por el más pequeño, no por el mejor

De [Right-size model selection to optimize inference costs](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost01-bp01.html), la única práctica de [GENCOST01](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost01.html). El resultado deseado está redactado con precisión: permite **gestionar el gasto en inferencia sin adivinar los requisitos de capacidad** del modelo.

La estrategia oficial es probar primero con un modelo más pequeño y **aumentar tamaño y capacidades gradualmente hasta que uno resulte aceptable**. El razonamiento: empezando por el más pequeño **se mejoran las probabilidades de acabar en el modelo con el coste de token más efectivo**. Empezar por el más capaz garantiza no saber nunca si uno menor bastaba.

Los cuatro pasos:

1. Identificar los **requisitos mínimos** de rendimiento para un FM.
2. Determinar qué modelos disponibles **cumplen esa barra mínima**.
3. Seleccionar el **más coste-eficiente** según las dimensiones de coste priorizadas: paradigma de hosting, tamaño de modelo, coste de token.
4. **Reevaluar de forma continua**, porque aparecen modelos nuevos, las necesidades cambian y el prompting se refina.

> **Dato decisivo**: el right-sizing es una **actividad continua**, no una decisión de diseño. La práctica lo dice explícitamente, y añade dos consecuencias arquitectónicas: **desplegar varios modelos en un único multi-model endpoint** donde tenga sentido, y **descomponer la carga para enrutar a modelos de distinto tamaño según la necesidad de cada petición**.

El enrutado por complejidad que pide el skill tiene dos implementaciones, ambas ya desarrolladas en [Task 2.2 · Skill 2.2.3](../domain-2/task-2-2-despliegue-de-modelos.md#skill-223--despliegue-optimizado-y-model-cascading): el [intelligent prompt routing](../domain-2/task-2-2-despliegue-de-modelos.md#intelligent-prompt-routing-la-cascada-gestionada) gestionado, limitado a modelos de la misma familia, y el [model cascading](../domain-2/task-2-2-despliegue-de-modelos.md#model-cascading) propio. GENCOST01-BP01 añade la tercera salida cuando la latencia no es un requisito: **si no hace falta inferencia en tiempo real, elegir un paradigma más barato como batch**.

### Los dos regímenes de coste

La distinción que organiza todo el skill, de GENCOST01-BP01:

| Régimen | Cómo se factura | Qué lo mueve |
| --- | --- | --- |
| **Modelos gestionados** (Bedrock) | Consumo medido en **tokens de entrada y de salida** | Cuántos tokens entran y salen, y la tarifa del modelo |
| **Modelos autoalojados** (EC2, endpoints de SageMaker AI) | **Costes de infraestructura tradicionales**: uptime, más almacenamiento y red | Cuánto tiempo está encendido, no cuánto se usa |

> **Dato decisivo**: en el régimen gestionado, un modelo sin tráfico cuesta cero. En el autoalojado, cuesta lo mismo. Ese es el criterio que decide entre importar un modelo a Bedrock con Custom Model Import o alojarlo en un endpoint, y es exactamente el escenario que plantea GENCOST02-BP01 para cargas **pequeñas y periódicas**.

La documentación advierte además que los modelos **más nuevos y más grandes suelen costar más** que los más antiguos o pequeños, lo que convierte la actualización de modelo en una decisión de coste, no solo de capacidad.

### GENCOST02: el paradigma de inferencia como decisión de coste

De [Generative AI pricing model](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost02.html), con dos prácticas.

[**GENCOST02-BP01**](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost02-bp01.html) trata la capacidad reservada con una secuencia concreta y verificable: si el modelo tiene necesidades de throughput, **comprar primero un plazo corto**, medir si Provisioned Throughput mejora de verdad el rendimiento de la aplicación, y solo entonces, si el caso es sólido, **pasar a un plan de seis meses**, cuyo coste unitario suele ser menor que ir mes a mes. Y la advertencia inversa: **validar los requisitos de escalado con compromisos de duración corta para evitar sobreaprovisionar**.

> Uno de los beneficios que enuncia la práctica es llamativo por lo explícito: conviene optar por un paradigma gestionado o serverless **por lo intratable que resulta el coste total de propiedad del hosting de un foundation model**. No es una preferencia estética.

[**GENCOST02-BP02**](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost02-bp02.html) cubre el autoalojado: dimensionar el endpoint a la **instancia más pequeña** que cumpla los objetivos, **apagar y reencender la instancia según el horario** cuando el patrón de uso es predecible, evaluar Reserved Instances o Savings Plans, y **usar SageMaker AI Inference Recommender antes de comprometerse** para verificar que el tipo, generación y tamaño de endpoint son los ideales. Nombra además **quantization y adaptación LoRA** como técnicas que reducen el consumo de recursos en inferencia.

### Medir el ratio precio-rendimiento

El skill pide medirlo, y la documentación ofrece tres instrumentos que miden cosas distintas:

| Instrumento | Qué devuelve | Dónde está el detalle |
| --- | --- | --- |
| **Bedrock evaluations** | Calidad de respuesta por métrica, con juez automático o humano | [Task 1.2 · Skill 1.2.1](../domain-1/task-1-2-seleccion-y-configuracion-fm.md#benchmarking-con-bedrock-evaluations) y [Task 3.4](../domain-3/task-3-4-ia-responsable.md#las-cuatro-familias-de-evaluación-de-bedrock) |
| **Advanced Prompt Optimization** | Scores de evaluación **más coste y latencia por modelo**, hasta 5 a la vez | [Skill 4.1.1](#skill-411--sistemas-de-eficiencia-de-tokens) |
| **Cost Explorer** | El gasto real, desglosado por la dimensión que se haya etiquetado | Este skill |

> **Dato decisivo**: ninguno de los tres mide el ratio por sí solo. El numerador (calidad) sale de evaluations o de AdvPO; el denominador (coste real) sale de Cost Explorer, y **solo si se etiquetó la invocación antes**. El orden importa: sin etiquetado previo no hay denominador que recuperar después.

### La instrumentación de coste en AWS

De [Tagging Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/tagging.html). Las etiquetas sirven para tres cosas, y solo la segunda es de coste: identificar y organizar recursos, **asignar costes**, y controlar el acceso mediante políticas basadas en tag.

> **Gotcha de facturación**: etiquetar no basta. Hay que **activar las etiquetas en el panel de AWS Billing and Cost Management** para que AWS las use al categorizar costes, según [Use cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html). Una etiqueta puesta y no activada no aparece en el informe. El vehículo para etiquetar una invocación de Bedrock, que no es un recurso persistente, es el **application inference profile** del [Task 1.2 · Skill 1.2.2](../domain-1/task-1-2-seleccion-y-configuracion-fm.md#capa-2--indirección-de-recurso-inference-profiles).

De [Analyzing your costs and usage with AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html), los números que condicionan su uso:

| Aspecto | Valor |
| --- | --- |
| **Histórico disponible** | Hasta **13 meses** |
| **Previsión** | Hasta **18 meses** |
| **Disponibilidad del mes en curso** | En unas **24 horas** tras habilitarlo; el resto tarda unos días más |
| **Frecuencia de refresco** | **Al menos cada 24 horas**, dependiendo de los datos de facturación aguas arriba |
| **Coste de la interfaz** | **Gratis** |
| **Coste de la API** | **0,01 USD por cada petición paginada** |
| **Reversibilidad** | **No se puede deshabilitar** una vez habilitado |

> **Dato decisivo para el diseño de un dashboard de coste**: la API de Cost Explorer **se paga por petición paginada**, y los datos se refrescan como mucho cada 24 horas. Un panel que consulte Cost Explorer cada cinco minutos paga por datos que no han cambiado. El coste por token en tiempo casi real se saca de las métricas de CloudWatch del [Skill 4.1.1](#skill-411--sistemas-de-eficiencia-de-tokens), no de Cost Explorer.

### Cost Anomaly Detection

De [Getting started with AWS Cost Anomaly Detection](https://docs.aws.amazon.com/cost-management/latest/userguide/getting-started-ad.html). Hace falta **al menos un cost monitor** para empezar a vigilar, y después se le enganchan alert subscriptions por email o **Amazon SNS**.

Los **dos enfoques de monitor**, que es la distinción examinable:

| | **AWS managed** | **Customer managed** |
| --- | --- | --- |
| Alcance | Sigue automáticamente **los 5.000 valores principales** de una dimensión, **cada uno por separado** | Valores concretos que se seleccionan a mano, **agregados entre sí** |
| Crecimiento | Los valores nuevos **se incluyen solos** al aparecer | Hay que añadirlos a mano |
| Tope | — | **10 valores** por monitor |
| Cuándo | Cobertura completa, adaptación automática, mantenimiento mínimo | Umbrales distintos por grupo, o vigilancia especial de cargas prioritarias |

Las cuatro dimensiones disponibles: **AWS services** (solo managed; la variante customer managed **no existe**), **linked accounts** (managed solo en la cuenta de gestión), **cost allocation tags** y **cost categories**.

> **Gotcha organizativo**: los monitores y sus suscripciones **solo son accesibles desde la cuenta que los creó**, y los de linked accounts, cost allocation tags y cost categories **solo se pueden crear en la cuenta de gestión**. Una cuenta miembro no puede vigilar su propio tag de equipo.

Y la práctica recomendada que evita el ruido: **no crear monitores que abarquen varias dimensiones**, para no recibir alertas duplicadas.

Los dos campos que convierten una anomalía en una decisión:

| Campo | Cálculo |
| --- | --- |
| **Cost impact** | `gasto real − gasto esperado` |
| **Impact %** | `(cost impact / gasto esperado) × 100`. Si el gasto esperado es cero, se muestra `N/A` |

> **Dato decisivo, y contraintuitivo**: la **severidad** no mide el tamaño del pico. Mide **cuán anormal es el pico frente al patrón histórico**. Un pico pequeño sobre un gasto históricamente estable se clasifica como **severidad alta**, y un pico grande sobre un gasto históricamente irregular se clasifica como **severidad baja**. Para una carga GenAI cuyo gasto es estable, una subida modesta de tokens dispara severidad alta, que es justo lo que se quiere.

---

## Skill 4.1.3 — Sistemas de alto rendimiento: batching, capacidad y escalado

> *Desarrollar sistemas de FM de alto rendimiento para maximizar la utilización de recursos y el throughput en cargas GenAI (por ejemplo, usando estrategias de batching, planificación de capacidad, monitorización de utilización, configuraciones de auto-scaling, optimización de provisioned throughput).*

### Batch inference: qué es y qué cuesta

De [Process multiple prompts with batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html). Se envían múltiples prompts y las respuestas se generan **de forma asíncrona**, en una sola petición, dejando los resultados en un bucket de S3. El propósito declarado: **mejorar el rendimiento de la inferencia sobre datasets grandes**.

El ahorro del 50 % frente a on-demand y la ventana de 24 horas están en la tabla de capacidad de [Task 2.2 · Skill 2.2.1](../domain-2/task-2-2-despliegue-de-modelos.md#las-seis-opciones-de-capacidad-de-amazon-bedrock), junto con las cuotas de 10.000 registros y 200 MB por fichero. Lo que aporta este skill es la mecánica del job.

### Las dos restricciones que descartan batch de entrada

> **Restricción importante**, y son las dos preguntas que deciden si batch es viable:
> - **No se soporta para modelos provisionados.** Batch y Provisioned Throughput son alternativas, no complementos.
> - **No soporta tool calling (function calling) ni structured output (`response_format`).** El motivo que da la documentación: cada registro del JSONL **se procesa de forma independiente, sin interacción multi-turno**, así que cualquier funcionalidad que exija ida y vuelta entre modelo y cliente queda fuera.

A eso se suma lo ya visto en Domain 2: **prompt caching tampoco funciona con batch**. Las tres restricciones juntas definen el perfil de carga de batch: una pasada, sin herramientas, sin esquema forzado y sin caché.

### Crear el job

De [Create a batch inference job](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-create.html), con [`CreateModelInvocationJob`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_CreateModelInvocationJob.html) contra el **endpoint del plano de control** de Bedrock, no el de runtime.

Campos **obligatorios**:

| Campo | Para qué |
| --- | --- |
| `jobName` | Nombre del job |
| `roleArn` | Service role con permisos para crear y gestionar el job |
| `modelId` | ID o ARN del modelo |
| `inputDataConfig` | Ubicación de S3 con los datos de entrada |
| `outputDataConfig` | Ubicación de S3 donde escribir las respuestas |

Campos **opcionales**, y tres de ellos deciden la arquitectura:

| Campo | Para qué |
| --- | --- |
| **`modelInvocationType`** | Formato de la entrada: **`InvokeModel` (por defecto)** o **`Converse`** |
| **`timeoutDurationInHours`** | Horas tras las cuales el job expira |
| `tags` | Etiquetas para asignación de coste |
| **`vpcConfig`** | Configuración de VPC para proteger los datos durante el job |
| `clientRequestToken` | Idempotencia de la petición |

> **Gotcha de la consola**: hay **tres escenarios que obligan a usar la API** y no la consola. Enviar el job **usando una VPC**, que la entrada esté en un bucket **de otra cuenta**, y que la salida vaya a un bucket **de otra cuenta**. En un montaje multi-cuenta, la consola de batch inference no sirve.

Detalle de la entrada que ahorra trabajo: batch inference **procesa todos los ficheros JSONL y sus ficheros de contenido acompañantes en esa ubicación de S3**, tanto si es una carpeta como un único fichero JSONL. No hace falta enumerar los ficheros.

```python
import boto3

# Ojo al cliente: batch inference vive en el plano de control ("bedrock"),
# no en "bedrock-runtime".
bedrock = boto3.client("bedrock")

respuesta = bedrock.create_model_invocation_job(
    jobName="enriquecimiento-catalogo-2026-09",
    roleArn="arn:aws:iam::111122223333:role/BedrockBatchInference",
    modelId="amazon.nova-lite-v1:0",
    # Converse unifica el formato con el resto de la aplicacion; sin esto
    # se espera el formato especifico de cada modelo.
    modelInvocationType="Converse",
    inputDataConfig={
        "s3InputDataConfig": {"s3Uri": "s3://mi-bucket/batch/entrada/"}
    },
    outputDataConfig={
        "s3OutputDataConfig": {"s3Uri": "s3://mi-bucket/batch/salida/"}
    },
    # Techo duro de duracion: la condicion de parada de GENCOST05-BP01
    # aplicada a una carga batch.
    timeoutDurationInHours=20,
    tags=[{"key": "caso-de-uso", "value": "catalogo"}],
)

print(respuesta["jobArn"])
```

### Monitorizar el job sin hacer polling

De [Monitor batch inference jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-monitor.html). Los estados posibles están en el campo `status` de [`ModelInvocationJobSummary`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ModelInvocationJobSummary.html).

Para seguir el progreso hay **contadores** que devuelven [`GetModelInvocationJob`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_GetModelInvocationJob.html) y [`ListModelInvocationJobs`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ListModelInvocationJobs.html), con el total de registros de entrada y cuántos se han procesado. La documentación subraya la ventaja: permiten **monitorizar la finalización sin mirar los buckets de salida de S3**.

> **Dato decisivo**: la recomendación oficial es explícita en que **en lugar de hacer polling del estado, se use Amazon EventBridge** para recibir notificaciones automáticas al completarse o cambiar de estado. De [Monitor Amazon Bedrock job state changes using Amazon EventBridge](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-eventbridge.html), los eventos cubren **model customization jobs** y **batch inference jobs**, se entregan **en tiempo casi real** y con **best-effort**, y **recibir eventos de AWS desde EventBridge no tiene coste**. El argumento que da la documentación para preferirlo: entrega actualizaciones de estado **sin invocar una API Get**, lo que ayuda con los límites de tasa de API, con los cambios de API y con la **reducción de recursos de cómputo adicionales**.

### Leer los resultados

De [View the results of a batch inference job](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-results.html). Bedrock genera **un fichero JSONL de salida por cada JSONL de entrada**, con una línea por registro:

```json
{ "recordId": "3223593EFGH", "modelInput": {}, "modelOutput": {} }
```

> **Dato decisivo para el manejo de errores**: en cualquier línea donde la inferencia falló, **un objeto `error` sustituye al campo `modelOutput`**. No hay fichero de errores aparte: el éxito y el fallo conviven en el mismo JSONL, y hay que comprobar qué campo trae cada línea.

Y el fichero **`manifest.json.out`**, que es donde está la contabilidad del job:

| Campo | Qué cuenta |
| --- | --- |
| `totalRecordCount` | Registros enviados al job |
| `processedRecordCount` | Registros procesados, **éxitos y errores incluidos** |
| `successRecordCount` | Registros procesados con éxito |
| `errorRecordCount` | Registros que dieron error |
| **`inputTokenCount`** | **Total de tokens de entrada del job** |
| **`outputTokenCount`** | **Total de tokens de salida generados** |

> Los dos últimos campos son la razón por la que el manifest importa más de lo que parece: son el **coste del job en tokens**, disponible sin recorrer la salida ni consultar CloudWatch.

Batch inference funciona además con **modelos personalizados** y con **perfiles de inferencia cross-Region**, según [Supported Regions and models for batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-supported.html). El resto de prerrequisitos (formato de los datos, permisos y VPC) está en [Prerequisites for batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-prereq.html), con páginas propias para [el formato de los datos](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-data.html), [los permisos](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-permissions.html) y [la protección con VPC](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-vpc.html).

### Planificación de capacidad

Las seis opciones de capacidad, los rangos de RPM y TPM por tier, el modelo de model units y el umbral del 40 % para pasar a capacidad reservada están en [Task 2.2 · Skill 2.2.1](../domain-2/task-2-2-despliegue-de-modelos.md#límites-y-cuotas-por-tier) y en [Capacity and Performance](https://docs.aws.amazon.com/bedrock/latest/userguide/capacity-limits-cost-optimization.html). Lo que aporta este skill es el aviso sobre con qué **no** se planifica:

> **Aviso oficial**: la métrica `EstimatedTPMQuotaUsage` **es una aproximación y no refleja el consumo basado en reserva** que dirige las decisiones de throttling, porque el throttling reserva por adelantado los tokens de entrada **más `max_tokens`**. La documentación es explícita: **no usarla como único indicador de uso de cuota ni para planificación de capacidad**. El desarrollo está en [Task 3.3 · Skill 3.3.4](../domain-3/task-3-3-governance-y-compliance.md#métricas-de-runtime).

La consecuencia práctica: la planificación de capacidad en Bedrock se hace con **`InputTokenCount` más `OutputTokenCount` observados**, y reservando el techo de `maxTokens` que la aplicación permite, no con la métrica que parece diseñada para eso.

### Optimización de Provisioned Throughput

De [Increase model invocation capacity with Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html), desarrollado en [Task 2.2 · Skill 2.2.1](../domain-2/task-2-2-despliegue-de-modelos.md#provisioned-throughput-el-modelo-de-model-units). Las tres reglas de optimización que se derivan de GENCOST02-BP01, en orden de aplicación:

```
1 · Comprobar que hace falta   → medir throttling real, no anticipado
                                  (InvocationThrottles, no EstimatedTPMQuotaUsage)
2 · Comprar plazo corto        → validar que mejora el rendimiento de verdad
                                  sin compromiso, o 1 mes
3 · Alargar el compromiso      → 6 meses solo con el caso demostrado
                                  coste unitario menor que mes a mes
```

Y la regla que no cambia entre páginas: **la facturación continúa hasta que se elimina el Provisioned Throughput**, no hasta que se deja de invocarlo.

### Auto-scaling: dónde existe y dónde no

El skill pide "configuraciones de auto-scaling" para cargas de FM. De [What is Application Auto Scaling?](https://docs.aws.amazon.com/autoscaling/application/userguide/what-is-application-auto-scaling.html), las cuatro políticas disponibles:

| Política | Cómo decide |
| --- | --- |
| **Target tracking** | Escala según un **valor objetivo** de una métrica de CloudWatch |
| **Step scaling** | Ajustes que **varían según el tamaño del incumplimiento** de la alarma |
| **Scheduled scaling** | Una vez, o de forma recurrente |
| **Predictive scaling** | **Proactivo**, anticipando carga a partir de datos históricos |

Los recursos relacionados con FM que soporta: **SageMaker AI endpoint variants**, **SageMaker AI inference components** y **SageMaker AI Serverless provisioned concurrency**. También ElastiCache, DynamoDB, ECS y **provisioned concurrency de Lambda**, que son piezas habituales alrededor de una aplicación GenAI. El listado completo está en [AWS services that you can use with Application Auto Scaling](https://docs.aws.amazon.com/autoscaling/application/userguide/integrated-services-list.html).

> **Hueco de documentación, y probablemente el matiz más preguntable del skill**: **Amazon Bedrock no figura en la lista de recursos escalables de Application Auto Scaling**. No hay política de escalado que se pueda aplicar a un modelo de Bedrock. La lista de [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html) nombra además **AWS Auto Scaling**, que es un servicio distinto de Application Auto Scaling.
>
> Lo que sí existe en Bedrock es **elasticidad gestionada por el servicio** dentro de los límites del tier, más **compra de capacidad** (subir de tier, model units, Provisioned Throughput). La respuesta correcta ante "autoescalar una carga de Bedrock" es que **se escala comprando capacidad y absorbiendo picos con colas y reintentos**, no configurando una política. El autoescalado por política aplica a lo que rodea al modelo: el endpoint de SageMaker AI, la caché, la tabla, la concurrencia de Lambda.

```
CARGA DE BEDROCK                      CARGA DE SAGEMAKER AI
─────────────────────────────         ─────────────────────────────
Elasticidad del servicio              Application Auto Scaling
  dentro del tier                       target tracking
  burst capacity                        step scaling
        │                                scheduled
Comprar capacidad                        predictive
  subir de tier                               │
  model units                           Escalar a cero
  Provisioned Throughput                  async endpoints
        │                                 serverless
Absorber el pico                          inference components
  SQS + reintentos                            │
  degradar a modelo menor               Instancia y generacion
  batch lo no urgente                     Inference Recommender
```

---

## Skill 4.1.4 — Sistemas de caching inteligente

> *Crear sistemas de caching inteligente para reducir costes y mejorar los tiempos de respuesta evitando invocaciones innecesarias del FM (por ejemplo, usando caché semántica, result fingerprinting, edge caching, hashing determinista de peticiones, prompt caching).*

### Las cuatro capas donde se puede cachear

El skill nombra cinco técnicas que no están al mismo nivel: dos son capas de infraestructura, dos son patrones de implementación y una es una funcionalidad del modelo.

```
BORDE            CloudFront
                 · cachea la respuesta HTTP completa
                 · clave de caché = lo que se incluya en la cache policy
                        │
API              API Gateway response caching
                 · por stage, TTL configurable
                 · solo GET por defecto
                        │
APLICACION       Cache semantica (ElastiCache for Valkey)
                 · clave = embedding de la consulta
                 · acierta con consultas parecidas, no identicas
                 · hashing determinista y fingerprinting para el caso exacto
                        │
MODELO           Prompt caching de Bedrock
                 · no evita la invocacion: abarata el prefijo
                 · unica capa que sigue llamando al modelo
```

> **Dato decisivo**: el enunciado del skill dice *evitando invocaciones innecesarias del FM*, y **prompt caching no evita ninguna invocación**. Reduce el coste de los tokens de entrada de una invocación que sí ocurre. Las tres capas superiores son las que evitan la llamada. Confundirlas es confundir "pagar menos por invocar" con "no invocar".

### Prompt caching: solo la economía

El detalle completo (implicit frente a explicit, cache checkpoints, mínimos por modelo, regla del prefijo acumulativo, TTL de 5 minutos) está en [Task 2.2 · Skill 2.2.3](../domain-2/task-2-2-despliegue-de-modelos.md#reducir-el-coste-sin-cambiar-de-modelo-prompt-caching). Lo que añade GENCOST03-BP03 es el bucle operativo en cuatro pasos: **identificar oportunidades** (revisar componentes repetidos, verificar que se llega al mínimo de tokens, estimar el ahorro), **habilitar**, **monitorizar** (tasas de hit y miss, coste de tokens cacheados frente a no cacheados, mejoras de latencia) y **optimizar** (ajustar la colocación de checkpoints, reestructurar el prompt, y **balancear el coste de escritura contra el ahorro de lectura**).

De [Prompt caching for faster model inference](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html), la regla de estructura que decide la tasa de acierto: **contenido estático al principio del prompt, dinámico al final**.

### Caché semántica: por qué no basta la coincidencia exacta

De [Overview of semantic caching](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/semantic-caching-overview.html). A diferencia de una caché tradicional que depende de coincidencias exactas de cadena, una caché semántica recupera **por similitud semántica**, usando embeddings que capturan el significado en un espacio vectorial de alta dimensión.

El mecanismo: se almacenan representaciones vectoriales de las consultas junto a sus respuestas. Cada consulta nueva se compara contra los vectores cacheados; si hay una por encima del **umbral de similitud configurado**, se devuelve la respuesta previa **en lugar de invocar el LLM**. Si no, se invoca el modelo y se cachean juntos el embedding de la consulta y la respuesta.

El ejemplo oficial lo explica mejor que cualquier definición. Tres consultas sobre instalar la VPN corporativa, redactadas de tres formas distintas: una caché de coincidencia exacta trata cada una como única e **invoca el LLM tres veces**; la semántica las reconoce como equivalentes e **invoca una sola vez**.

Los cuatro beneficios que documenta, con sus cifras de benchmark: **coste reducido** hasta un **86 %** menos de gasto en inferencia, **latencia menor** con respuestas en milisegundos en lugar de segundos y hasta un **88 %** de reducción, **escalabilidad mejorada** al servir más peticiones **dentro de los mismos límites de throughput del modelo sin aumentar capacidad**, y **consistencia mejorada** al devolver la misma respuesta a preguntas equivalentes.

Dónde es efectiva, de la misma página:

| Tipo de aplicación | Por qué | Ejemplo oficial |
| --- | --- | --- |
| **Asistentes y copilots sobre RAG** | Muchas consultas son duplicados de distintos usuarios contra una base de conocimiento compartida | Chatbot de soporte informático, bot de FAQ de producto |
| **Aplicaciones agentic** | Los agentes descomponen tareas en pasos pequeños que **buscan repetidamente información parecida** | Agente de compliance que reutiliza consultas de política |
| **Aplicaciones multimodales** | Coincidencia de segmentos de audio, imágenes o vídeo parecidos | Sistemas telefónicos automáticos que reutilizan la guía para peticiones repetidas |

### Los números que deciden el umbral de similitud

De [Impact and benchmarks](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/semantic-caching-benchmarks.html). AWS evaluó el enfoque sobre **63.796 consultas reales de chatbot** y sus variantes parafraseadas, del dataset público SemBenchmarkLmArena, con una instancia `cache.r7g.large`, **Amazon Titan Text Embeddings V2** para los embeddings y **Claude 3 Haiku** para la inferencia. La caché arrancó vacía y las consultas se enviaron como tráfico aleatorio.

| Umbral de similitud | Tasa de acierto | Exactitud de lo cacheado | Ahorro de coste | Reducción de latencia |
| --- | --- | --- | --- | --- |
| Sin caché (baseline) | — | — | — | — |
| **0,99** muy estricto | 23,5 % | 92,1 % | 15,8 % | 17,1 % |
| **0,95** estricto | 56,0 % | 92,6 % | 51,9 % | 57,7 % |
| **0,90** moderado | 74,5 % | 92,3 % | 72,5 % | 72,2 % |
| **0,80** equilibrado | 87,6 % | 91,8 % | 84,6 % | 86,1 % |
| **0,75** relajado | 90,3 % | **91,2 %** | **86,3 %** | **88,3 %** |
| **0,50** muy relajado | 94,3 % | **87,5 %** | 88,0 % | 89,3 % |

> **Dato decisivo**: la exactitud se mantiene **en torno al 92 % desde 0,99 hasta 0,80**, y sigue en 91,2 % a 0,75. Solo al bajar a **0,50 cae al 87,5 %**, mientras el ahorro apenas sube del 86,3 % al 88,0 %. El punto de inflexión está en **0,75**: relajar más el umbral compra casi nada de ahorro a cambio de casi cuatro puntos de exactitud. Es la forma de la curva lo que se examina, no la cifra suelta.

Dos matices que la propia página añade. La elección de LLM, modelo de embeddings y almacén **afecta tanto al coste como a la latencia**, así que las cifras no son transferibles sin más. Y la caché semántica **rinde proporcionalmente mejor cuanto más grande y caro es el LLM**: con un modelo económico, el ahorro relativo es menor.

En latencia individual, un acierto de caché redujo la latencia **hasta 59 veces**, de 6,51 s a 0,11 s en el caso extremo, y 12 veces en otro (1,64 s a 0,13 s).

### Por qué ElastiCache for Valkey como almacén

De [Why ElastiCache for Valkey for semantic caching](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/semantic-caching-why-elasticache.html). El razonamiento arranca de los tres requisitos que impone una caché semántica, y son los que hay que saber reconocer:

| Requisito | Por qué |
| --- | --- |
| **Actualización de vectores en tiempo real** | Las consultas y respuestas nuevas deben estar disponibles **de inmediato** para mantener la tasa de acierto |
| **Búsquedas de baja latencia** | La caché está **en el camino online de cada consulta**: la búsqueda no puede añadir retardo perceptible |
| **Gestión eficiente de lo efímero** | Las entradas se escriben, leen y expulsan constantemente: hay que gestionar un *hot set* |

Lo que aporta ElastiCache frente a eso: latencia de búsqueda vectorial **de microsegundos con hasta un 99 % de recall**, **arquitectura multihilo** que soporta actualizaciones en tiempo real y throughput de escritura alto manteniendo la latencia de búsqueda baja, funcionalidades de caché ya incorporadas (**TTL**, políticas de expulsión como `allkeys-lru`, operaciones atómicas), soporte de índices **HNSW y FLAT** con métricas de distancia **COSINE, euclídea y producto interno**, escalado **sin downtime**, e integración con **Bedrock AgentCore a través del framework LangGraph**.

> **Dato decisivo**: la política de expulsión `allkeys-lru` y el TTL no son detalles de configuración, son **el mecanismo de invalidación de la caché semántica**. Una respuesta cacheada envejece igual que cualquier otra, y sin expulsión la caché devuelve información obsoleta con alta confianza, que es el peor modo de fallo de este patrón.

### Las dos rutas de una petición

De [Solution architecture](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/semantic-caching-architecture.html), el patrón es una **caché read-through**:

```
Peticion del usuario
      │
      ▼
Generar embedding de la consulta        ← esta llamada se paga SIEMPRE
      │
      ▼
Buscar en ElastiCache por similitud
      │
      ├─ ACIERTO (>= umbral) ──► devolver la respuesta cacheada
      │                           · latencia de milisegundos
      │                           · SIN coste de inferencia del LLM
      │                           · solo se invoco el modelo de embeddings
      │
      └─ FALLO ────────────────► invocar el LLM
                                  · generar la respuesta
                                  · devolverla al usuario
                                  · cachear embedding + respuesta
```

> **Coste que no se ve**: la ruta de acierto **invoca el modelo de embeddings, no el LLM**. La caché semántica no es gratis: cambia una llamada caro por una llamada barata más una búsqueda vectorial. Con un LLM económico y un embeddings caro, el margen se estrecha, que es la otra cara del aviso de que el patrón rinde mejor con modelos grandes.

La implementación de referencia, con la creación del índice vectorial, las funciones de búsqueda y actualización y el patrón read-through, está en [Implementing a semantic cache with ElastiCache for Valkey](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/semantic-caching-implementation.html). El marco de diseño en el Agentic AI Lens es [AGENTCOST02-BP03](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentcost02-bp03.html), que trata el caching inteligente como forma de reducir invocaciones redundantes del modelo, y complementa la vista de coste de agente de [Task 2.1 · Skill 2.1.4](../domain-2/task-2-1-agentic-ai-y-herramientas.md#el-marco-de-coste-right-sizing-del-modelo).

### Hashing determinista y result fingerprinting

Estas dos técnicas del skill no tienen página propia en el portal: son el caso exacto que la caché semántica generaliza. El hashing determinista construye la clave de caché a partir de un hash estable de la petición normalizada, y el fingerprinting identifica un resultado por su huella para detectar duplicados. Conviene tenerlas claras como **la capa previa y más barata**: si la petición es literalmente idéntica, no hace falta calcular un embedding ni hacer búsqueda vectorial.

```python
import hashlib
import json


def clave_determinista(mensajes: list[dict], modelo: str, temperatura: float) -> str:
    """Huella estable de una peticion de inferencia.

    Normaliza antes de hashear: sin esto, el mismo prompt con las claves del
    JSON en otro orden produce una clave distinta y la cache nunca acierta.
    La temperatura entra en la clave porque cambia la respuesta esperada; una
    peticion con temperatura alta no deberia cachearse en absoluto.
    """
    canonico = json.dumps(
        {"mensajes": mensajes, "modelo": modelo, "temperatura": temperatura},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()
```

> **Gotcha de determinismo**: cachear una respuesta generada con temperatura alta rompe la premisa de la caché. El modelo fue configurado para variar, y la caché fija esa variación para siempre. La temperatura y el resto de parámetros de inferencia deben formar parte de la clave, o la caché debe limitarse a peticiones deterministas.

### Caché de respuestas en API Gateway

De [Cache settings for REST APIs in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-caching.html). Se habilita **por stage** y cachea las respuestas del endpoint durante un TTL, respondiendo desde la caché en lugar de llamar al backend.

| Aspecto | Valor |
| --- | --- |
| **TTL por defecto** | **300 segundos** |
| **TTL máximo** | **3.600 segundos** |
| **TTL = 0** | Desactiva el caching |
| **Tamaño máximo de respuesta cacheable** | **1.048.576 bytes**. El cifrado de los datos de caché **puede aumentar el tamaño** de la respuesta al cachearla |
| **Métodos cacheados por defecto** | **Solo `GET`**, por seguridad y disponibilidad de la API. El resto requiere override de method settings |
| **Garantía** | **Best-effort**. Se monitoriza con `CacheHitCount` y `CacheMissCount` en CloudWatch |
| **Facturación** | **Por hora según el tamaño de caché elegido**, y **no es elegible para la capa gratuita** |

> **Gotcha operativo, de los que rompen producción**: aprovisionar la caché **tarda hasta 4 minutos**, y **cambiar la capacidad elimina la instancia de caché existente y crea otra, borrando todos los datos cacheados**. Redimensionar la caché de un API en caliente vacía la caché y devuelve todo el tráfico al modelo de golpe.

La recomendación oficial de dimensionado: ejecutar un **load test de 10 minutos** con tráfico que refleje el de producción, incluyendo rampa, tráfico constante y picos, **con respuestas que puedan servirse de caché y respuestas únicas que la llenen**, vigilando latencia, 4xx, 5xx, hit y miss.

> **Restricción de aplicabilidad**: una API GenAI casi siempre expone `POST` con el prompt en el body, y API Gateway **cachea `GET` por defecto** y construye la clave de caché a partir de parámetros de la petición. La caché de API Gateway encaja en consultas parametrizadas e idempotentes, no en un chat. Para el chat, la capa útil es la semántica.

### Edge caching con CloudFront

De [Optimizing caching and availability](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/ConfiguringCaching.html). Es la capa más externa, y en una aplicación GenAI su papel suele ser distinto del que sugiere el skill: sirve el frontend y los activos estáticos, y cachea respuestas de API solo cuando son públicas, idempotentes y compartibles entre usuarios. Una respuesta generada para un usuario concreto no se cachea en el borde sin convertir la clave de caché en algo específico de ese usuario, momento en el que la tasa de acierto se hunde.

### Tabla de decisión de la capa de caché

| Si el escenario es… | La capa es… | Por qué |
| --- | --- | --- |
| Mismo prompt literal, repetido | **Hashing determinista** | Sin coste de embedding ni de búsqueda |
| Prompts distintos con el mismo significado | **Caché semántica** | Es exactamente lo que resuelve |
| Prefijo largo y estable, consulta variable | **Prompt caching** | Abarata el prefijo; sigue invocando |
| Consulta parametrizada e idempotente sobre `GET` | **Caché de API Gateway** | TTL por stage, sin código |
| Contenido público compartido entre usuarios | **CloudFront** | Se sirve desde el borde |
| Consultas predecibles conocidas de antemano | **Pre-computación** | Ver [Skill 4.2.1](./task-4-2-latencia-y-throughput.md#skill-421--sistemas-de-ia-responsivos) |
| Temperatura alta o respuesta que debe variar | **Ninguna** | Cachear contradice el diseño |

---

## Resumen operativo del Task 4.1

| Si la pregunta menciona… | La respuesta apunta a |
| --- | --- |
| Acortar el prompt cuando no se paga por token | Sigue importando: **más computación y más infraestructura** (GENCOST03-BP01) |
| Reescribir un prompt corto para un modelo, al instante | **Simple optimization**, heurística, sincrónica, ~1k tokens, 1 modelo |
| Comparar prompt y modelo con evaluación propia | **Advanced Prompt Optimization**: 5 modelos, 10 plantillas, 100 samples |
| Obtener coste y latencia estimados por modelo | Salida de **AdvPO** |
| Limitar la optimización a parte de la plantilla | Etiquetas **`<advpo:optimize>`** y **`<advpo:exclude>`** |
| Acortar la respuesta sin perder utilidad | **Esquema de respuesta con clave** más límite duro (GENCOST03-BP02) |
| Pagar menos por filtrar contenido ya confiable | **Input tags** con `tagSuffix` aleatorio (GENCOST03-BP04) |
| Los input tags no funcionan | Correcto: **no se soportan con `ApplyGuardrail`** |
| Tokens de caché y cuota TPM | **Read no cuenta y es más barato; write sí cuenta y puede costar más** |
| Predecir el coste máximo de un agente | **Condiciones de parada** de GENCOST05-BP01, riesgo **Alto** |
| Cortar un agente sin instrumentar el bucle | **Límite de tokens en la respuesta**, como timeout simulado |
| Elegir modelo por coste | **Empezar por el más pequeño** y subir hasta la barra (GENCOST01-BP01) |
| Un modelo sin tráfico que sigue costando | Está **autoalojado**: se factura por uptime, no por token |
| Cuándo comprar capacidad reservada | **Plazo corto primero**, medir, y solo entonces 6 meses (GENCOST02-BP01) |
| Verificar el tipo de endpoint antes de comprometerse | **SageMaker AI Inference Recommender** (GENCOST02-BP02) |
| Etiquetas puestas que no aparecen en la factura | Falta **activarlas en Billing and Cost Management** |
| Coste de la API de Cost Explorer | **0,01 USD por petición paginada**; datos refrescados cada 24 h |
| Histórico y previsión de Cost Explorer | **13 meses atrás, 18 meses adelante** |
| Vigilar todos los equipos de un tag sin mantenerlo | **AWS managed monitor**: top **5.000 valores**, se autoamplía |
| Umbrales distintos por grupo de cuentas | **Customer managed monitor**, hasta **10 valores** |
| Un pico pequeño que dispara severidad alta | Correcto: la **severidad mide lo anormal**, no el tamaño |
| Alertas de coste duplicadas | Monitores que **abarcan varias dimensiones** |
| Batch inference sobre un modelo provisionado | **No se soporta** |
| Batch inference con tool calling o structured output | **No se soportan**: cada registro se procesa sin multi-turno |
| Crear un job de batch | **`CreateModelInvocationJob`** en el **plano de control** |
| Batch con VPC o buckets de otra cuenta | **Obliga a usar la API**, no la consola |
| Saber si el job terminó sin mirar S3 | **Contadores de progreso** de `GetModelInvocationJob` |
| Evitar el polling del estado del job | **EventBridge**, sin coste, best-effort, tiempo casi real |
| Dónde están los errores del batch | Un objeto **`error` sustituye a `modelOutput`** en la línea |
| Coste en tokens de un job de batch | **`inputTokenCount`** y **`outputTokenCount`** de `manifest.json.out` |
| Planificar capacidad con `EstimatedTPMQuotaUsage` | **No**: es aproximada y no refleja la reserva |
| Autoescalar una carga de Bedrock | **No existe**: se compra capacidad y se absorben picos |
| Escalar un endpoint de SageMaker AI | **Application Auto Scaling**: target tracking, step, scheduled, predictive |
| Evitar la invocación del FM | Hashing determinista, **caché semántica**, API Gateway, CloudFront |
| Prompt caching como forma de evitar invocaciones | **No evita ninguna**: abarata el prefijo de una invocación real |
| Tres formas de pedir lo mismo, una sola invocación | **Caché semántica** |
| Umbral de similitud recomendado | **0,75**: 86,3 % de ahorro con 91,2 % de exactitud |
| Bajar el umbral a 0,50 | Ahorro casi igual, **exactitud cae al 87,5 %** |
| Mejora de latencia de un acierto de caché | Hasta **59×**; hasta 88 % de reducción media |
| Requisitos del almacén de una caché semántica | Escritura en tiempo real, lectura de baja latencia, gestión del *hot set* |
| Índices y métricas de ElastiCache | **HNSW y FLAT**; COSINE, euclídea, producto interno |
| Invalidar una caché semántica | **TTL** y **`allkeys-lru`**: sin expulsión sirve datos obsoletos |
| Qué se paga en un acierto de caché semántica | **El modelo de embeddings**, no el LLM |
| TTL de la caché de API Gateway | **300 s** por defecto, **3.600 s** máximo, 0 desactiva |
| Respuesta grande que no se cachea en API Gateway | Tope de **1.048.576 bytes** |
| La caché de API Gateway se vació sola | **Cambiar la capacidad** destruye la instancia y los datos |
| Caché de API Gateway en un endpoint de chat | Encaja mal: **solo `GET` por defecto** y clave por parámetros |
