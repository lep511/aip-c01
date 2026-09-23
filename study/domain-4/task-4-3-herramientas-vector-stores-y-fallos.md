# Task 4.3 — Herramientas, vector stores y modos de fallo

[← Volver al índice](./README.md)

Skills cubiertos: **4.3.4**, **4.3.5**, **4.3.6**.

Segunda mitad del Task 4.3. Aquí está la observabilidad de lo que rodea al modelo: **las herramientas que invoca**, **el vector store que lo alimenta** y **los modos de fallo que no existen en un sistema ML clásico**. La capa de métricas y dashboards de la aplicación está en [task-4-3-observabilidad-y-metricas.md](./task-4-3-observabilidad-y-metricas.md).

---

## Skill 4.3.4 — Rendimiento de herramientas y coordinación multi-agente

> *Crear frameworks de rendimiento de herramientas para asegurar operación y utilización óptimas de las herramientas para los FMs (por ejemplo, usando tracking de patrones de llamada, recogida de métricas de rendimiento, observabilidad de tool calling y tracking de coordinación multi-agente, baselines de uso para detección de anomalías).*

### Dónde viven las métricas de herramienta

El tool use de la Converse API, con sus tres modos, el `toolConfig` y el campo `status` del `toolResult`, está en [Task 2.1 · Skill 2.1.6](../domain-2/task-2-1-agentic-ai-y-herramientas.md#los-tres-modos-de-tool-use-de-bedrock). La observabilidad de agentes con OpenTelemetry, en [Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#agentcore-observability).

Lo que aporta este skill es que **la herramienta tiene métricas propias**, separadas de las del modelo que la invoca. Y la primera decisión es de qué tipo de herramienta se habla:

| Tipo de herramienta | Quién la ejecuta | Quién publica sus métricas |
| --- | --- | --- |
| **Client-side tool** de la Converse API | Tu código, tras recibir el `toolUse` | **Tú**: el modelo no sabe si funcionó |
| **Built-in tool de AgentCore** (code interpreter, browser) | **AgentCore** | **AgentCore**, de fábrica |
| **Action group de un agente de Bedrock** | Lambda o esquema de API | Lambda y el trace del agente |
| **Herramienta vía AgentCore Gateway** | El gateway | AgentCore Observability |

> **Dato decisivo**: con **client-side tool use** el modelo devuelve un bloque `toolUse` y **espera un `toolResult`**. Todo lo que pase en medio es invisible para Bedrock: si la herramienta tardó 8 segundos o falló y se devolvió un error, **no aparece en ninguna métrica de `AWS/Bedrock`**. La observabilidad de esas herramientas hay que construirla, y el lugar natural es un subsegmento de X-Ray o un span propio con los atributos de [Transaction Search](./task-4-3-observabilidad-y-metricas.md#transaction-search-y-el-log-group-awsspans).

### Las métricas de las built-in tools de AgentCore

De [AgentCore generated built-in tools observability data](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-tool-metrics.html). Hay métricas integradas para el **code interpreter** y el **browser**, y un detalle que condiciona la granularidad: **se agrupan en lotes a intervalos de un minuto**.

Los tres grupos, y el segundo y el tercero son los que no se esperan:

**Invoke tool**, las cinco de toda operación de plano de datos:

| Métrica | Qué cuenta |
| --- | --- |
| `Invocations` | Peticiones a la API del plano de datos. **Cada llamada cuenta una, sea cual sea el tamaño del payload o el estado de la respuesta** |
| `Throttles` | Peticiones limitadas por exceder el **TPS** permitido o las cuotas. Devuelven `ThrottlingException` con **HTTP 429** |
| `SystemErrors` | Errores de servidor durante el procesamiento |
| `UserErrors` | Errores de cliente por peticiones inválidas. **Requieren acción del usuario para resolverse** |
| **`Latency`** | Tiempo desde que el servicio recibe la petición **hasta que empieza a enviar el primer token de respuesta** |

**Create tool session**, las mismas cinco más una:

| Métrica | Qué cuenta |
| --- | --- |
| **`Duration`** | La duración de la **sesión de herramienta**. La dimensión `Operation` pasa a ser `CodeInterpreterSession` o `BrowserSession` |

**Browser user takeover**, tres métricas del control humano sobre el navegador:

```
TakerOverCount           veces que un usuario toma el control
TakerOverReleaseCount    veces que lo libera
TakerOverDuration        cuanto tiempo lo tuvo
```

> **Dato decisivo**: `Latency` de una herramienta mide **hasta el primer token de respuesta**, igual que `TimeToFirstToken` mide la del modelo. No mide la ejecución completa; para eso está `Duration` **de la sesión**, no de la invocación. Confundirlas lleva a creer que una herramienta es rápida cuando solo empieza a responder rápido.
>
> Y el par `TakerOverCount` / `TakerOverReleaseCount` es la señal de human-in-the-loop del navegador: si el primero crece y el segundo no, **hay sesiones con control humano sin liberar**, que consumen recursos indefinidamente.

### Uso de recursos: vCPU-hora y GB-hora

La telemetría de recursos de las built-in tools incluye consumo de CPU y memoria:

| Métrica | Unidad | Dimensiones |
| --- | --- | --- |
| **`CPUUsed-vCPUHours`** | vCPU-horas | `Service`; `Service, Resource` |
| **`MemoryUsed-GBHours`** | GB-horas | `Service`; `Service, Resource` |

Las dimensiones: **`Service`** toma los valores `AgentCore.CodeInterpreter` o `AgentCore.Browser`, y **`Resource`** es el ID de la built-in tool. Se publican a **resolución de un minuto**, a nivel de cuenta y a nivel de herramienta, y ambas sirven **para seguimiento de recursos y visibilidad estimada de facturación**.

En la consola de AgentCore Observability, las de cuenta están en la pestaña **Built-in Tools** y las de herramienta en la página **Tools**, cada una con su gráfica de memoria y de CPU.

> **Aviso oficial, y son dos avisos encadenados que importan al diseñar una alarma**: los datos de uso de recursos **pueden retrasarse hasta 60 minutos**, y **la precisión puede diferir entre métricas**. Además, la telemetría **es para monitorización**: la facturación real se calcula con datos de uso medido y **puede diferir de los valores de telemetría** por temporización de agregación, procesos de reconciliación y precisión de medida. La factura autoritativa es el extracto de AWS, no el dashboard.
>
> Consecuencia práctica: **no se puede construir un control de coste en tiempo real sobre estas métricas**. Con hasta una hora de retraso, una alarma sobre `CPUUsed-vCPUHours` avisa cuando el gasto ya ocurrió.

El contexto de estas herramientas está en [Code Interpreter](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-tool.html) y [Browser](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html), y el marco general de la telemetría en [Understand observability for agentic resources in AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-telemetry.html).

### Tracking de patrones de llamada

El skill pide "tracking de patrones de llamada", y el patrón es lo que distingue un agente sano de uno que se comporta mal. Las cuatro señales, con lo que delata cada una:

| Señal | Qué delata |
| --- | --- |
| **Llamadas por sesión** | Un agente que necesita quince herramientas para lo que antes hacía con tres: el prompt o el catálogo cambió |
| **Distribución por herramienta** | Una herramienta que nunca se invoca está inflando el `toolConfig` sin aportar nada, y **los tokens del catálogo se pagan en cada turno** |
| **Repetición con los mismos argumentos** | El agente está en bucle; es el síntoma de la tabla de troubleshooting de [Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#tabla-de-troubleshooting-síntoma--señal--herramienta) |
| **Tasa de `status: error` en `toolResult`** | La herramienta falla y el modelo reintenta o improvisa, lo que suele acabar en respuesta inventada |

> **Dato decisivo de coste que conecta con el Task 4.1**: el catálogo de herramientas viaja en **cada** petición, dentro del campo `tools`, y cuenta como tokens de entrada. Una herramienta que no se usa cuesta dinero en todas las invocaciones. Y como el prefijo del prompt incluye `tools`, **cambiar el catálogo invalida la caché de prompt** del [Skill 4.1.4](./task-4-1-costes-y-eficiencia-de-recursos.md#prompt-caching-solo-la-economía).

### Coordinación multi-agente

Para agentes de Bedrock, el rastro de la coordinación está en el trace, ya desarrollado en [Task 3.4 · Skill 3.4.1](../domain-3/task-3-4-ia-responsable.md#skill-341--transparencia-y-reasoning-traces): los **siete tipos de trace**, el campo **`collaboratorName`** cuando la colaboración multi-agente está habilitada, y sobre todo **`callerChain`**, que con multi-agente contiene los ARN de alias de **todos los agentes que reenviaron la petición** hasta el actual.

> **Dato decisivo**: `callerChain` es **la única estructura documentada que reconstruye la cadena de coordinación** de una petición multi-agente. Con un solo agente contiene su propio ARN de alias, lo que la hace inútil; con colaboración habilitada es la cadena de custodia completa. Para atribuir latencia o coste a un agente concreto dentro de una jerarquía, es el campo que hay que extraer del trace y promover a dimensión de métrica.

Para agentes en AgentCore, las métricas de rendimiento y de decisión de los primitivos (Agents, Memory, Built-in Tools, Gateways, Identity) están en el dashboard de [AgentCore agents](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AgentCore-Agents.html) del [Skill 4.3.1](./task-4-3-observabilidad-y-metricas.md#los-dos-dashboards-preconstruidos), y en entornos multi-cuenta existe [AgentCore Cross-Account Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-cross-account.html), que centraliza logs, métricas, trazas **y resultados de evaluación** desde una sola cuenta de monitorización.

### Baselines de uso para detección de anomalías

El skill cierra pidiendo baselines. La mecánica es la del [Skill 4.3.2](./task-4-3-observabilidad-y-metricas.md#detección-de-anomalías-para-ráfagas-de-tokens-y-drift-de-respuesta): banda de anomalía sobre la métrica, no umbral fijo. Lo específico de herramientas es **sobre qué métrica derivada** ponerla:

```
Llamadas a herramienta por sesion          ← sube: el agente se volvio indeciso
Tasa de error de toolResult                ← sube: la herramienta se degrado
Duration de sesion de built-in tool        ← sube: sesiones que no cierran
TakerOverCount sin TakerOverReleaseCount   ← control humano sin liberar
CPUUsed-vCPUHours por invocacion           ← ojo: hasta 60 min de retraso
```

---

## Skill 4.3.5 — Gestión operativa del vector store

> *Crear sistemas de gestión operativa del vector store para asegurar operación y fiabilidad óptimas del vector store para la aumentación del FM (por ejemplo, usando monitorización de rendimiento para bases de datos vectoriales, rutinas automatizadas de optimización de índices, procesos de validación de calidad de datos).*

### El cuarto namespace de Bedrock

Domain 3 documenta tres namespaces en [Task 3.3 · Skill 3.3.4](../domain-3/task-3-3-governance-y-compliance.md#los-tres-namespaces-de-métricas). Hay un cuarto, y es el de este skill.

De [Observability for managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-observability.html). Para una knowledge base gestionada, Bedrock publica **métricas operativas y logs de ingesta** en la cuenta del cliente, bajo el namespace **`AWS/Bedrock/KnowledgeBases`**, y **sin coste adicional**.

| Métrica | Unidad | Cuándo se publica |
| --- | --- | --- |
| **`Invocations`** | Count | **En cada petición, incluidas las que dan error** |
| **`ClientErrors`** | Count | Solo cuando ocurre. HTTP **4xx distinto de throttling** |
| **`ServerErrors`** | Count | Solo cuando ocurre. HTTP **5xx** |
| **`Throttles`** | Count | Solo cuando ocurre. HTTP **429**. **No cuentan como `ClientErrors` ni como `ServerErrors`** |

> **Dato decisivo**: la asimetría es deliberada y se examina. **`Invocations` se publica siempre**, con éxito o con error; las otras tres **solo se publican cuando la condición se da**. Consecuencia para las alarmas: una alarma sobre `ClientErrors` con `TreatMissingData` mal configurado no dispara nunca o dispara siempre, porque **la ausencia de dato significa que no hubo errores**, no que no hubo tráfico. Y el patrón de `Throttles` es el mismo que `InvocationThrottles` en `AWS/Bedrock`: no son errores, así que una tasa de error a cero puede convivir con throttling severo.

### La métrica que cierra el bucle del agentic retrieval

Para la operación `AgenticRetrieveStream` hay una métrica más:

| Métrica | Unidad | Detalle |
| --- | --- | --- |
| **`TotalIterationCount`** | Count | Número total de **iteraciones de recuperación agentic** durante la petición. **Solo para `AgenticRetrieveStream`**, y **solo cuando la petición termina con éxito** |

> **Dato decisivo**: es la métrica que hace observable el coste del agentic retrieval del [Skill 4.2.2](./task-4-2-retrieval-y-parametros.md#agentic-retrieval-recuperación-con-evaluación-de-suficiencia). Cada iteración es una planificación más una evaluación del FM, así que `TotalIterationCount` es **proporcional al coste y a la latencia** de la petición. Una media que sube significa que el modelo necesita más pasadas para considerar suficientes los resultados, y eso apunta al retrieval, no al modelo.
>
> El matiz que se pregunta: **solo se publica si la petición acaba bien**. Las peticiones que fallan a mitad no aportan iteraciones al agregado, así que la media está sesgada hacia los casos que funcionaron.

### Dimensiones, y la que falta

| Dimensión | Valores |
| --- | --- |
| **`Operation`** | **`Retrieve`** o **`AgenticRetrieveStream`** |
| **`KnowledgeBaseId`** | La knowledge base objetivo, en formato **`knowledge-base/knowledge-base-id`** |

> **Gotcha de atribución**: `KnowledgeBaseId` **se incluye para la operación `Retrieve`**, que apunta a una sola knowledge base. **Las operaciones que no apuntan a una única knowledge base se publican solo con la dimensión `Operation`.** En un montaje donde una consulta abarca varias knowledge bases, **no se puede atribuir la métrica a ninguna de ellas**. Ahí la atribución tiene que salir de los traces, no de las métricas.

### El gotcha de permisos que rompe la observabilidad en silencio

Bedrock publica estas métricas **con las credenciales asociadas a la petición**, y no son las mismas según la operación:

| Operación | Identidad usada |
| --- | --- |
| **`Retrieve`** | El **service role de la knowledge base** |
| **Las demás** | Las credenciales de **la identidad que llama**, mediante una **forward access session** |

Esa identidad debe tener permiso para `cloudwatch:PutMetricData` **acotado al namespace** `AWS/Bedrock/KnowledgeBases`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "cloudwatch:PutMetricData",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "AWS/Bedrock/KnowledgeBases"
        }
      }
    }
  ]
}
```

> **Gotcha crítico**: la publicación de métricas es **best effort**. Si la identidad no tiene el permiso, **las métricas no se publican, pero la petición a la knowledge base no se ve afectada**. El sistema funciona perfectamente y no hay ninguna métrica. Es el modo de fallo más difícil de diagnosticar de todo el dominio, porque **no hay error que investigar**: hay que sospechar del permiso.
>
> Y el detalle que lo complica: hay que conceder el permiso **al service role de la knowledge base y a cualquier identidad que llame a las operaciones**. Conceder solo al service role deja sin métricas todo lo que no sea `Retrieve`, incluido `AgenticRetrieveStream`.

### La métrica de almacenamiento

| Métrica | Unidad | Cuándo |
| --- | --- | --- |
| **`RawDataSize`** | **Gigabytes** | Tamaño total en bruto de los datos de origen almacenados. Se publica **después de que termine un job de ingesta** |

Usa la dimensión `KnowledgeBaseId` en el mismo formato.

> **Dato decisivo**: `RawDataSize` **no se actualiza de forma continua**, sino al completarse una ingesta. Es la serie temporal que permite ver crecer el corpus y anticipar cuándo el índice dejará de caber en la capacidad configurada, ya sean OCUs de OpenSearch Serverless o la memoria del grafo k-NN de [Task 1.4 · Skill 1.4.3](../domain-1/task-1-4-vector-stores.md#dimensionado-de-memoria-de-grafos-k-nn).

### Observabilidad de ingesta: por qué un documento no aparece en los resultados

Bedrock emite logs que rastrean el progreso de un job de ingesta, **incluidos el estado global del job y el estado de cada documento procesado**. Los tres usos que documenta, y el segundo es el que resuelve la pregunta más frecuente de un RAG:

```
1 · Confirmar QUE documentos se ingirieron
2 · Investigar POR QUE un documento no aparecio en los resultados de retrieval
3 · Diagnosticar fallos de ingesta
```

> **Dato decisivo**: cuando un usuario dice *el asistente no conoce este documento*, hay **dos hipótesis distintas** y estos logs las separan. O el documento **nunca se ingirió**, y entonces el problema es de pipeline; o se ingirió y **el retrieval no lo devuelve**, y entonces el problema es de chunking, embeddings o filtros, que es el terreno del [Skill 4.2.2](./task-4-2-retrieval-y-parametros.md#skill-422--rendimiento-del-retrieval). Sin logs de ingesta no se puede distinguir, y se acaba ajustando el retrieval de un documento que no está.

### Configurar la entrega de logs de ingesta

Los destinos son tres: **CloudWatch Logs, Amazon S3 o Amazon Data Firehose**. Por consola se edita la knowledge base para añadir una entrega y se comprueba que el estado sea **Delivery active**.

Por API son cuatro llamadas, y usan las APIs de entrega de CloudWatch Logs, no las de Bedrock:

| Paso | Llamada | Detalle |
| --- | --- | --- |
| 1 | [`GetKnowledgeBase`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_GetKnowledgeBase.html) | Obtener el ARN, con formato `arn:aws:bedrock:region:cuenta:knowledge-base/id` |
| 2 | [`PutDeliverySource`](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutDeliverySource.html) | El ARN como `resourceArn` y **`APPLICATION_LOGS`** como `logType` |
| 3 | [`PutDeliveryDestination`](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutDeliveryDestination.html) | Dónde se guardan, con `outputFormat` en **`json`, `plain`, `w3c`, `raw` o `parquet`** |
| 4 | [`CreateDelivery`](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_CreateDelivery.html) | Enlaza origen y destino |

Para entregar a otra cuenta se usa además `PutDeliveryDestinationPolicy` sobre la cuenta destino.

> **Dato decisivo**: el `logType` es **`APPLICATION_LOGS`**, el mismo que el logging de knowledge bases del [Task 3.3 · Skill 3.3.4](../domain-3/task-3-3-governance-y-compliance.md#response-logging-de-las-knowledge-bases). Y el formato **`parquet`** es la opción que convierte los logs de ingesta en algo consultable con Athena a escala, útil cuando el corpus tiene cientos de miles de documentos y el análisis por log group deja de ser práctico.

### Monitorizar el vector store subyacente

Para la capa de almacenamiento, de [Monitoring Amazon OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-monitoring.html), las tres vías son **CloudWatch** para métricas, **CloudTrail** para llamadas de API, y **EventBridge** para un flujo casi en tiempo real de eventos del sistema.

Las métricas de capacidad, de [Managing capacity limits for Amazon OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-scaling.html):

| Métrica | Qué mide |
| --- | --- |
| **`SearchOCU`** | OCUs consumidas por búsqueda |
| **`IndexingOCU`** | OCUs consumidas por indexado |

Cada **OCU** son **6 GiB de memoria** más la vCPU correspondiente y la transferencia de datos al almacenamiento compartido y a S3. La capacidad se fija con mínimo y máximo **por collection group, por separado para indexado y para búsqueda**, con estos límites:

| Límite | Valor |
| --- | --- |
| **Mínimo** | **0 OCUs** para indexado y 0 para búsqueda. Con 0, no se consumen OCUs en reposo |
| **Máximo por collection group** | **1.700 OCUs de indexado y 1.700 de búsqueda** |
| **Valores válidos** | **2, 4, 8, 16, o cualquier múltiplo de 16** hasta el máximo |
| **Índices por colección** | Máximo **1.000** |
| **Colecciones Classic** | **120 GiB de almacenamiento hot efímero por OCU**, y hasta **10 TiB de hot storage gestionado por colección** |

> **Dato decisivo, y es el tradeoff operativo del vector store serverless**: el **mínimo** evita el **cold start** y da un arranque determinista; el **máximo** es un **control presupuestario**. Poner el mínimo a 0 ahorra en reposo a cambio de latencia en la primera consulta tras un periodo de inactividad, que en un asistente de uso esporádico es exactamente el peor momento para ser lento.
>
> Y la restricción de agrupación: las colecciones de un collection group **comparten OCUs** para eficiencia de coste, pero **solo cabe un tipo de colección por grupo** (search, time series o vector search). No se puede mezclar un índice vectorial con uno de series temporales para compartir capacidad.

La recomendación explícita de la documentación: **configurar alarmas para avisar cuando la cuenta se acerca a un umbral de capacidad**, y usar esas métricas para decidir si los máximos configurados son los adecuados. El resto de optimizaciones de OpenSearch Serverless está en [Task 1.4 · Skill 1.4.3](../domain-1/task-1-4-vector-stores.md#optimizaciones-de-opensearch-serverless).

### Rutinas automatizadas de optimización de índice y validación de calidad

El skill pide las dos, y [GENPERF04-BP01](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf04-bp01.html) es lo que las respalda. Para la calidad de datos, sus exigencias son cuatro:

| Exigencia | Detalle |
| --- | --- |
| **Evaluaciones regulares** | De **frescura, exactitud y representatividad** |
| **Vigilancia de drift de datos** | Y procesos de **ingesta continua y re-embedding periódico** |
| **Tres mecanismos de comprobación** | **Chequeos automatizados, revisión humana y análisis de la salida de la IA** |
| **Governance** | Políticas claras y **control de versiones del vector store** |

Y para la operación del índice, la práctica pide algo que suele faltar: **runbooks operativos** que faciliten cambios rápidos de arquitectura, porque advierte que **los cuellos de botella se desplazan entre capas** a medida que el sistema escala y los patrones de uso cambian.

> **Dato decisivo**: la práctica exige **monitorizar todos los componentes por separado** y nombra cuatro: **generación de embeddings, construcción del índice, procesamiento de consultas y recuperación de resultados**, siguiendo **latencia, throughput y utilización de recursos** en cada uno. Es la instrumentación que permite ver el desplazamiento del cuello de botella; con una sola métrica de latencia de retrieval, el desplazamiento es invisible.

El monitoreo del mantenimiento de datos, las semánticas de sincronización incremental y los prerrequisitos que hacen fallar una sincronización están en [Task 1.4 · Skill 1.4.5](../domain-1/task-1-4-vector-stores.md#skill-145--sistemas-de-mantenimiento-de-datos).

---

## Skill 4.3.6 — Troubleshooting de modos de fallo propios de GenAI

> *Desarrollar frameworks de troubleshooting específicos de FM para identificar modos de fallo únicos de GenAI que no están presentes en sistemas ML tradicionales (por ejemplo, usando golden datasets para detectar hallucinations, técnicas de output diffing para análisis de consistencia de respuesta, reasoning path tracing para identificar errores lógicos, pipelines de observabilidad especializados).*

### Qué falla en un sistema GenAI que no falla en un ML clásico

El enunciado del skill se apoya en la premisa de [GENPERF02](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02.html): los FM son **inherentemente no deterministas** e introducen aleatoriedad en el sistema, difícil de contabilizar **especialmente cuando las técnicas tradicionales de evaluación de rendimiento se apoyan en el determinismo**.

De ahí salen los cuatro modos de fallo del skill:

| Modo de fallo | Por qué no existe en ML clásico | Técnica del skill |
| --- | --- | --- |
| **Hallucination** | Un clasificador se equivoca; no inventa una categoría que no existe | **Golden dataset** |
| **Inconsistencia de respuesta** | La misma entrada da la misma salida en un modelo determinista | **Output diffing** |
| **Error lógico en el razonamiento** | No hay razonamiento intermedio que auditar | **Reasoning path tracing** |
| **Degradación sin cambio de código** | El modelo, el prompt y el contexto pueden cambiar por separado | **Pipelines especializados** |

### El golden dataset: la definición oficial

De [Define a ground truth data set of prompts and responses](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf01-bp01.html), la única práctica del portal que define el término que usa el skill. **Ground truth data, también llamado golden dataset**, son los datos considerados de la máxima calidad para un caso de uso concreto, y para cargas GenAI suelen ser **pares prompt-respuesta**.

Las cinco propiedades que documenta, y la tercera es la que más se pasa por alto:

| Propiedad | Detalle |
| --- | --- |
| **Escala variable** | Desde **decenas hasta miles o más** de prompts de ejemplo con sus respuestas esperadas |
| **Variantes agrupadas** | Varios prompts con **variaciones de la misma petición**, y varias respuestas describiendo **variaciones de una respuesta aceptable** |
| **No obsesionarse con las diferencias menores** | **No hay que preocuparse por diferencias ligeras entre prompts que piden esencialmente la misma tarea** |
| **Artefacto vivo** | Cambia y se extiende según los casos de uso probados y los paradigmas de uso implementados |
| **Específico de la tarea** | Los prompts deben ser específicos **del tipo de tarea que se espera que el modelo resuelva** |

> **Dato decisivo**: los pares prompt-respuesta son el núcleo, pero **el dataset necesita metadatos adicionales** para cubrir todos los paradigmas de uso. El ejemplo que da la documentación: un workflow de agente sintetiza varias respuestas intermedias antes de la final, así que el ground truth **debe poder capturar un flujo de prompt ideal, trazando el workflow del agente por los distintos sistemas**. Un golden dataset de pares planos no puede evaluar un agente.

Y una exigencia de governance que condiciona su construcción: hay que desarrollarlo **conforme a la política de IA de la organización**. Si esa política prohíbe probar modelos contra datos de producción, el golden dataset debe contener **referencias a datos funcionalmente equivalentes**, con **datasets simulados y endpoints simulados** para probar flujos agentic. Y debe contener **las instrucciones que el harness de testing necesita para ejecutarse de forma autónoma contra cualquier endpoint de modelo disponible, incluidos modelos autoalojados**.

> **Dato decisivo de retorno de la inversión**: además de acelerar el testing y la evaluación, los golden datasets **sirven para afinar modelos rápidamente o destilar modelos student a partir de teachers**. Los workflows de customización necesitan datos de alta calidad, así que mantener un golden dataset robusto por caso de uso **acelera la capacidad de personalizar modelos**. Es el argumento para financiarlo: no es solo gasto de QA.

### Cómo construirlo, según la práctica

Los cinco pasos, con los servicios que nombra cada uno:

```
1 · Definir prompts y respuestas esperadas
      SageMaker Ground Truth o similar para escalar la curacion
      enriquecer los pares con metadatos segun la politica de IA
            │
2 · Almacenar para busqueda tipo diccionario
      capas superiores organizativas: idioma, dominio de negocio, caso de uso
      capa final: el prompt es la clave, la respuesta esperada el valor
      almacen de objetos: Amazon S3
            │
3 · Crear un diccionario de datos
      rastrear el almacen con un AWS Glue Crawler
            │
4 · Desarrollar un harness de testing
      que pruebe modelos automaticamente a medida que estan disponibles
      consultar segmentos con una solucion federada: Amazon Athena
      incorporar datos de produccion simulados y tooling para agentes o RAG
            │
5 · Definir escenarios de prueba
      metricas exigidas por la politica de IA
      seguir el rendimiento por prueba y metrica, evaluando los tradeoffs
```

> El paso 2 es el que da la estructura: **el prompt es la clave y la respuesta esperada el valor**, con capas organizativas por encima. Esa forma es la que hace que el harness pueda pedir "todos los casos de resumen en español del dominio de seguros" sin recorrer el dataset entero.

### Detección de hallucinations: las tres capas

| Capa | Qué hace | Cuándo actúa |
| --- | --- | --- |
| **Contextual grounding check** | Devuelve `score` y `threshold` para `GROUNDING` y `RELEVANCE` | **En runtime**, por petición |
| **RAG evaluation** | Métricas built-in contra ground truth | **En pre-producción**, por lote |
| **Golden dataset con harness** | Compara la respuesta con la esperada | **En CI y en regresión** |

El contextual grounding check está en [Task 3.1 · Skill 3.1.3](../domain-3/task-3-1-controles-de-seguridad-entrada-salida.md#skill-313--verificación-de-exactitud-y-reducción-de-hallucinations), con sus tres restricciones de uso y el recordatorio de que **no cubre las referencias recuperadas**.

De [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html), la **RAG evaluation basada en LLM** calcula métricas de rendimiento **tanto para la recuperación de la knowledge base como para la generación de la respuesta**. Entre las métricas built-in de un job de retrieve-and-generate están **Correctness, Faithfulness y CitationCoverage**, según [Create a retrieve and generate evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-create-randg.html), y los resultados se recogen en un [informe de evaluación](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-report.html) accesible por consola o en S3.

> **Dato decisivo**: **Faithfulness** es la métrica de hallucination en el vocabulario de Bedrock, y mide si la respuesta se sostiene en el contexto recuperado. **Correctness** mide si la respuesta es correcta frente al ground truth, que es otra cosa: una respuesta puede ser fiel a un contexto equivocado. Y **CitationCoverage** mide cuánto de la respuesta está respaldado por citas. Las tres juntas separan *el modelo inventó* de *el retrieval trajo lo incorrecto* de *la respuesta no está atribuida*. El desarrollo completo de las familias de evaluación está en [Task 3.4 · Skill 3.4.2](../domain-3/task-3-4-ia-responsable.md#las-métricas-de-rag-que-no-son-las-mismas).

### Output diffing para análisis de consistencia

El skill lo pide y no tiene página propia: es la técnica de ejecutar el mismo prompt varias veces, o antes y después de un cambio, y comparar las salidas. Los tres usos que tiene sentido distinguir:

| Comparación | Qué detecta | Herramienta documentada |
| --- | --- | --- |
| **Mismo prompt, N ejecuciones** | Cuánta varianza introduce el no determinismo con los parámetros actuales | Harness propio sobre el golden dataset |
| **Antes y después de un cambio** | Regresión al mover una versión de prompt o de modelo | **Comparison queries** de Logs Insights, solo en QL |
| **Entre modelos** | Si el candidato responde como el actual | **Advanced Prompt Optimization**, hasta 5 modelos |

> **Dato decisivo**: las **comparison queries** de CloudWatch Logs Insights comparan eventos de un log group **con los de un periodo anterior**, y están **solo disponibles en Logs Insights QL**, no en PPL ni en SQL. Es la forma documentada de detectar una regresión tras desplegar una versión de prompt, según [Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#cloudwatch-logs-insights).
>
> Y el prerrequisito de medición: para que el diffing antes-después funcione, las invocaciones deben llevar `requestMetadata` con la versión, como en el A/B testing del [Skill 4.2.4](./task-4-2-retrieval-y-parametros.md#ab-testing-de-verdad-versiones-y-alias).

### Reasoning path tracing para identificar errores lógicos

Es el trace de agente, ya desarrollado en [Task 3.4 · Skill 3.4.1](../domain-3/task-3-4-ia-responsable.md#los-siete-tipos-de-trace). Lo que corresponde aquí es qué campo sirve para qué diagnóstico:

| Campo del trace | Qué revela |
| --- | --- |
| **`rationale`** dentro de `parsedResponse` | **El razonamiento del agente**: es el reasoning path en sí |
| **`isValid`** del `PreProcessingTrace` | Si el paso consideró válida la entrada |
| **`FailureTrace`** | La razón del fallo de un paso. **Es el único tipo sin `ModelInvocationInput`** |
| **`promptCreationMode`** y **`parserMode`** | Si la plantilla o el parser por defecto fueron **`OVERRIDDEN`** |
| **`type`** de `ModelInvocationInput` | En qué fase ocurrió: `PRE_PROCESSING`, `ORCHESTRATION`, `ROUTING_CLASSIFIER`, `KNOWLEDGE_BASE_RESPONSE_GENERATION`, `POST_PROCESSING` |

> **Dato decisivo para el diagnóstico de un error lógico**: el `rationale` está **dentro de `parsedResponse`**, no en la raíz del trace, y hay que habilitar **`enableTrace`** en `InvokeAgent` para que exista. Sin él no hay reasoning path que trazar, y un agente que razona mal es indistinguible de un agente que recupera mal. Se activa en [`InvokeAgent`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeAgent.html) y el detalle está en [Track agent's step-by-step reasoning process using trace](https://docs.aws.amazon.com/bedrock/latest/userguide/trace-events.html).

Para agentes gestionados en AgentCore, el equivalente son las **retrieval traces y agentic traces** con instrumentación compatible con OpenTelemetry, que capturan **trazas de invocación de herramienta, detalles de interacción con el modelo y patrones de acceso a memoria**.

### Pipelines de observabilidad especializados

El skill cierra pidiéndolos, y lo que los hace "especializados" es que capturan señales que ningún pipeline de aplicación captura. La composición, con lo que aporta cada pieza:

```
INGESTA        Logs de ingesta de la knowledge base
               · estado por documento
               · responde: se ingirio o no se ingirio
                      │
RUNTIME        AWS/Bedrock/KnowledgeBases
               · Invocations siempre; errores solo si ocurren
               · TotalIterationCount del agentic retrieval
                      │
GROUNDING      Scores de contextual grounding, publicados a mano
               · score y threshold por GROUNDING y RELEVANCE
               · el MARGEN sobre el umbral anticipa la degradacion
                      │
RAZONAMIENTO   Traces de agente con enableTrace
               · rationale, isValid, FailureTrace, callerChain
               · promovidos a spans de Transaction Search
                      │
CONTENIDO      Model invocation logging
               · prompt y respuesta completos
               · requestMetadata con version y tenant
               · con enmascaramiento de datos sensibles
                      │
REGRESION      Harness sobre el golden dataset en CI
               · Correctness, Faithfulness, CitationCoverage
               · comparison queries para el antes y despues
```

> La señal que más rinde y que casi nadie publica es **el margen del score de grounding sobre su umbral**, tratado en [Task 3.4 · Skill 3.4.1](../domain-3/task-3-4-ia-responsable.md#métricas-de-confianza-e-incertidumbre): una serie de márgenes decrecientes **anticipa la degradación del retrieval antes de que empiecen los bloqueos**. Un dashboard que solo mira bloqueos se entera cuando ya hay usuarios afectados.

### Tabla de modos de fallo propios de GenAI

| Síntoma | Hipótesis a descartar por orden | Señal que decide |
| --- | --- | --- |
| **El asistente no conoce un documento** | No se ingirió → se ingirió pero no se recupera | **Logs de ingesta**, estado por documento |
| **Respuesta inventada con contexto disponible** | Retrieval irrelevante → modelo poco fiel | `Faithfulness` frente a `Correctness` |
| **Respuesta sin citas** | Generación no atribuida | **`CitationCoverage`** |
| **La misma pregunta da respuestas distintas** | Temperatura alta → contexto variable | **Output diffing** con N ejecuciones |
| **Empeoró sin desplegar nada** | Drift del modelo → drift de los datos | Anomalía sobre longitud de salida y score de grounding |
| **Empeoró tras desplegar un prompt** | Regresión de la versión | **Comparison queries** de Logs Insights (solo QL) |
| **El agente concluye mal con datos buenos** | Error lógico en el razonamiento | **`rationale`** del trace, con `enableTrace` |
| **El agente no avanza** | Bucle de herramienta | Repetición con mismos argumentos; `TotalIterationCount` |
| **Retrieval agentic lento y caro** | Demasiadas iteraciones | **`TotalIterationCount`**, solo en peticiones con éxito |
| **No hay métricas de la knowledge base** | Falta `cloudwatch:PutMetricData` | **Best effort**: no hay error, solo ausencia |
| **Consultas lentas tras un periodo inactivo** | Cold start de OCUs | Mínimo de OCUs a 0 |
| **La herramienta parece rápida pero tarda** | `Latency` mide hasta el primer token | Comparar con **`Duration`** de sesión |

---

## Resumen operativo: herramientas, vector stores y fallos

| Si la pregunta menciona… | La respuesta apunta a |
| --- | --- |
| Latencia de una herramienta client-side | **No existe en `AWS/Bedrock`**: hay que instrumentarla |
| Métricas de code interpreter o browser | **AgentCore built-in tool metrics**, en lotes de **1 minuto** |
| `Latency` de una built-in tool | Hasta el **primer token de respuesta**, no la ejecución completa |
| Duración real de una sesión de herramienta | **`Duration`**, con `Operation` en `CodeInterpreterSession`/`BrowserSession` |
| Control humano del navegador sin liberar | `TakerOverCount` sin su `TakerOverReleaseCount` |
| Consumo de CPU y memoria de las herramientas | **`CPUUsed-vCPUHours`** y **`MemoryUsed-GBHours`** |
| Control de coste en tiempo real sobre esas métricas | **No es viable**: hasta **60 minutos** de retraso |
| La telemetría no cuadra con la factura | Esperado: la facturación usa **datos de uso medido**, no telemetría |
| Una herramienta que nunca se invoca | Sigue costando: el catálogo **viaja en cada petición** |
| Cambiar el catálogo de herramientas | **Invalida la caché de prompt**: `tools` está en el prefijo |
| Reconstruir una coordinación multi-agente | **`callerChain`** del trace |
| Métricas de una knowledge base gestionada | Namespace **`AWS/Bedrock/KnowledgeBases`**, sin coste |
| `Invocations` de una knowledge base con errores | Se publica **en cada petición**, error incluido |
| `ClientErrors` sin datos | **Solo se publica cuando ocurre**: ausencia significa cero errores |
| `Throttles` de una knowledge base | HTTP 429, y **no cuentan como `ClientErrors` ni `ServerErrors`** |
| Coste y latencia del agentic retrieval | **`TotalIterationCount`**, solo en peticiones **con éxito** |
| Atribuir una métrica a una knowledge base concreta | `KnowledgeBaseId` **solo en `Retrieve`**; el resto, solo `Operation` |
| Métricas que no aparecen sin error alguno | Falta **`cloudwatch:PutMetricData`**: publicación **best effort** |
| Qué identidad publica las métricas | **Service role** en `Retrieve`; **forward access session** en las demás |
| Cuánto ocupa el corpus de una knowledge base | **`RawDataSize`** en GB, tras completar la ingesta |
| Por qué un documento no sale en los resultados | **Logs de ingesta**: separa "no ingerido" de "no recuperado" |
| Destinos de los logs de ingesta | **CloudWatch Logs, S3 o Data Firehose** |
| Configurar la entrega por API | `PutDeliverySource` con **`APPLICATION_LOGS`**, `PutDeliveryDestination`, `CreateDelivery` |
| Analizar logs de ingesta a gran escala | `outputFormat` en **`parquet`** |
| Capacidad de OpenSearch Serverless | **`SearchOCU`** e **`IndexingOCU`**; 6 GiB por OCU |
| Evitar el cold start del vector store | **Mínimo de OCUs mayor que 0** |
| Controlar el gasto del vector store | El **máximo de OCUs** como control presupuestario |
| Máximo de OCUs por collection group | **1.700** de indexado y **1.700** de búsqueda |
| Valores válidos de OCU | **2, 4, 8, 16 o múltiplos de 16** |
| Mezclar tipos de colección para compartir OCUs | **No se puede**: un solo tipo por collection group |
| Qué componentes monitorizar en un RAG | **Embeddings, construcción de índice, procesamiento de consulta, recuperación** |
| Definición oficial de golden dataset | **Ground truth data**: pares prompt-respuesta de máxima calidad |
| Golden dataset para un agente | Necesita **metadatos que tracen el flujo ideal** por los sistemas |
| Política que prohíbe datos de producción en pruebas | **Datos y endpoints simulados** funcionalmente equivalentes |
| Segundo uso de un golden dataset | **Fine-tuning y distillation**: acelera la customización |
| Cómo almacenar un golden dataset | S3 con **prompt como clave y respuesta como valor**, Glue Crawler y Athena |
| Métrica de hallucination en Bedrock | **`Faithfulness`** |
| Respuesta fiel a un contexto equivocado | `Faithfulness` alta con **`Correctness`** baja |
| Cuánto de la respuesta está respaldado por citas | **`CitationCoverage`** |
| Detectar una regresión tras desplegar un prompt | **Comparison queries** de Logs Insights, **solo en QL** |
| Comparar el mismo prompt en varios modelos | **Advanced Prompt Optimization** |
| Ver el razonamiento de un agente | **`rationale`** dentro de `parsedResponse`, con **`enableTrace`** |
| El único tipo de trace sin `ModelInvocationInput` | **`FailureTrace`** |
| Anticipar la degradación del retrieval | **Margen del score de grounding sobre su umbral** |
