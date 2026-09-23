# Task 2.4 — Integraciones de API de FM

[← Volver al índice](./README.md)

Skills cubiertos: **2.4.1**, **2.4.2**, **2.4.3**, **2.4.4**.

---

## Skill 2.4.1 — Sistemas flexibles de interacción con el modelo

> *Crear sistemas flexibles de interacción con el modelo (por ejemplo, usando las APIs de Amazon Bedrock para gestionar peticiones sincrónicas desde distintos entornos de computación, SDKs de AWS específicos por lenguaje y Amazon SQS para procesamiento asíncrono, API Gateway para proporcionar clientes de API personalizados con validación de peticiones).*

### Las operaciones de Bedrock Runtime

La base de formato de entrada y de `Converse` está en [Task 1.3 · Skill 1.3.3](../domain-1/task-1-3-datos-para-consumo-fm.md). Lo que interesa aquí es el mapa completo de operaciones y cuándo se usa cada una:

| Operación | Modalidad | Cuándo |
| --- | --- | --- |
| **`Converse`** | Sincrónica, unificada | La opción por defecto: API consistente que funciona con todos los modelos que soportan messages, con parámetros únicos del modelo vía `additionalModelRequestFields` |
| **`ConverseStream`** | Streaming, unificada | Entrega incremental. Requiere el permiso **`bedrock:InvokeModelWithResponseStream`** |
| **`InvokeModel`** | Sincrónica, específica del modelo | Cuando se necesita el formato nativo del proveedor |
| **`InvokeModelWithResponseStream`** | Streaming, específica del modelo | Ídem, con entrega incremental |
| **`CountTokens`** | Utilidad | Contar tokens antes de invocar, para presupuestos y validación |
| **`ApplyGuardrail`** | Utilidad | Evaluar contenido **sin invocar ningún FM**: útil para validar resultados de herramienta en un paso propio |
| **`StartAsyncInvoke`** | Asíncrona | Invocaciones de larga duración |
| **Batch inference** | Diferida | Ventana de 24 h, 50 % de descuento. Detalle en [Task 2.2 · Skill 2.2.1](./task-2-2-despliegue-de-modelos.md#skill-221--desplegar-fms-según-necesidades-y-requisitos-de-rendimiento) |
| **`Retrieve`**, **`RetrieveAndGenerate`**, **`RetrieveAndGenerateStream`**, **`Rerank`** | Agent runtime | Retrieval sobre knowledge bases. Ver [Task 1.5](../domain-1/task-1-5-retrieval.md) |

De [`ConverseStream`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html), el campo del request syntax que conviene conocer entero, porque concentra casi todo lo que el examen puede preguntar sobre la API:

```json
{
  "messages":                      [ { "role": "...", "content": [ ... ] } ],
  "system":                        [ ... ],
  "inferenceConfig":               { "maxTokens": 0, "stopSequences": [], "temperature": 0, "topP": 0 },
  "toolConfig":                    { "toolChoice": {}, "tools": [] },
  "guardrailConfig":               { "guardrailIdentifier": "", "guardrailVersion": "",
                                     "streamProcessingMode": "", "trace": "" },
  "outputConfig":                  { "textFormat": { "structure": {}, "type": "" } },
  "performanceConfig":             { "latency": "standard | optimized" },
  "serviceTier":                   { "type": "" },
  "promptVariables":               { "...": {} },
  "requestMetadata":               { "...": "" },
  "additionalModelRequestFields":  {},
  "additionalModelResponseFieldPaths": [ "" ]
}
```

| Campo | Para qué |
| --- | --- |
| **`serviceTier`** | Selecciona el tier de capacidad on-demand (Flex, Standard, Priority) visto en [Task 2.2](./task-2-2-despliegue-de-modelos.md#las-seis-opciones-de-capacidad-de-amazon-bedrock) |
| **`performanceConfig.latency`** | `standard` u `optimized` para latency-optimized inference |
| **`outputConfig.textFormat`** | Structured output: JSON validado contra esquema |
| **`requestMetadata`** | Metadatos de negocio **filtrables después en los invocation logs** |
| **`promptVariables`** | Valores de las variables de un prompt de Prompt Management |
| **`additionalModelRequestFields`** | Parámetros únicos del modelo que no cubre `inferenceConfig` |

Tres avisos oficiales de la página de `ConverseStream`:

- Para saber si un modelo soporta streaming, llamar a **`GetFoundationModel`** y comprobar el campo **`responseStreamingSupported`**.
- **La AWS CLI no soporta operaciones de streaming en Bedrock**, incluido `ConverseStream`.
- Al usar un prompt de Prompt Management no se pueden incluir `additionalModelRequestFields`, `inferenceConfig`, `system` ni `toolConfig`: deben definirse en Prompt Management.

> **Detalle de IAM que importa**: para **denegar** todo acceso de inferencia a un modelo hay que denegar **las dos acciones**, `bedrock:InvokeModel` y `bedrock:InvokeModelWithResponseStream`. Denegar solo una deja la otra vía abierta, incluidas las operaciones base de inferencia.

Bedrock **no almacena** texto, imágenes ni documentos aportados como contenido: los datos solo se usan para generar la respuesta.

### Invocación desde distintos entornos de computación

| Entorno | Consideraciones |
| --- | --- |
| **Lambda** | Timeout de **900 s**, payload sincrónico de **6 MB**, respuesta en streaming hasta **200 MB**. El entorno por defecto para una capa de invocación fina |
| **ECS / Fargate / EKS** | Sin techo de duración; adecuado para orquestación larga o dependencias pesadas |
| **EC2** | Control total, incluido alojar un modelo propio |
| **AgentCore Runtime** | Sesión de hasta 8 h en microVM aislado. Ver [Task 2.1 · Skill 2.1.1](./task-2-1-agentic-ai-y-herramientas.md#skill-211--sistemas-autónomos-con-memoria-y-gestión-de-estado) |
| **Step Functions** | Integración optimizada con Bedrock que soporta **los tres patrones**: Request Response, `.sync` y `.waitForTaskToken` (en Standard) |
| **App Runner** | Servicio de contenedor gestionado, en la lista de servicios en alcance |

### Procesamiento asíncrono con SQS

El patrón cuando el usuario no está esperando, o cuando la ventana del llamante es más corta que la generación:

```
Productor (API Gateway + Lambda, webhook, evento)
   │  acepta y responde 202 rápido
   ▼
┌──────────────────────────────────────────────────────────────┐
│ Amazon SQS                                                   │
│   · desacopla productor y consumidor                          │
│   · absorbe picos que excederían la cuota de Bedrock          │
│   · visibility timeout ≥ duración de la generación            │
│   · FIFO con MessageGroupId si el orden importa               │
│   · DLQ para lo que falla tras los reintentos                 │
└──────────────────────────────────────────────────────────────┘
   │  event source mapping
   ▼
┌──────────────────────────────────────────────────────────────┐
│ Lambda consumidor                                            │
│   · invoca Bedrock con reintentos y backoff                   │
│   · idempotencia: escritura condicional en DynamoDB + TTL     │
│     (AGENTREL06-BP04, ver Task 2.3 · Skill 2.3.1)             │
│   · maxConcurrency del event source mapping como límite de    │
│     presión sobre la cuota de tokens                          │
└──────────────────────────────────────────────────────────────┘
   │
   ▼
Persistir el resultado · notificar (SNS, WebSocket, AppSync)
```

Las tres razones por las que SQS aparece en este skill y no simplemente "llama a Bedrock en background": **absorbe el throttling** (un `ThrottlingException` no pierde el trabajo, vuelve a la cola), **acota la concurrencia** contra la cuota de TPM del tier, y **da una DLQ** donde inspeccionar lo que falló.

Alternativas documentadas para lo diferido: **Bedrock batch inference** (hasta 10.000 registros, fichero de 200 MB, ventana de 24 h, 50 % de descuento), **`StartAsyncInvoke`** para invocaciones largas, y **SageMaker asynchronous inference** (payload hasta 1 GB vía S3, procesado hasta 1 h, escalado a cero).

### Clientes de API personalizados con validación de peticiones

API Gateway delante del FM aporta una capa que el SDK directo no da:

| Capacidad | Valor en un contexto GenAI |
| --- | --- |
| **Request validation** | Rechaza peticiones mal formadas **en el borde, antes de gastar tokens**. Se define con modelos de esquema JSON sobre el body y con validación de parámetros de query y headers |
| **Authorizers** | Cognito user pool, IAM, JWT o Lambda authorizer |
| **Usage plans + API keys** | Cuota y rate limit **por consumidor**, no global |
| **Throttling** | Protege el backend y la cuota de Bedrock. Detalle en el [Skill 2.4.3](#skill-243--sistemas-de-fm-resilientes) |
| **Transformaciones de petición y respuesta** | Adaptar el contrato público al de Bedrock sin acoplar el cliente. Base del routing del [Skill 2.4.4](#skill-244--routing-inteligente-de-modelos) |
| **Contrato estable** | El cliente no cambia cuando cambia el modelo o el proveedor detrás |

> La validación en el borde no es solo higiene: es la contramedida al problema frecuente de [AGENTSEC04](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec04.html) de *consumir capacidad en entradas adversarias que podían rechazarse por adelantado*.

---

## Skill 2.4.2 — Interacción en tiempo real y streaming

> *Desarrollar sistemas de interacción de IA en tiempo real para dar feedback inmediato del FM (por ejemplo, usando las APIs de streaming de Amazon Bedrock para entrega incremental de respuesta, WebSockets o server-sent events para generar texto en tiempo real, API Gateway para implementar chunked transfer encoding).*

### Por qué el streaming importa

El argumento está en [AGENTPERF02](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentperf02.html), visto en [Task 2.1 · Skill 2.1.4](./task-2-1-agentic-ai-y-herramientas.md#skill-214--coordinación-de-modelos-y-optimización-entre-capacidades): los agentes de cara al usuario deben hacer streaming con **time-to-first-token por debajo del segundo**, y el trabajo previo a la inferencia debe comprimirse para preservar ese presupuesto. El problema frecuente que nombra: esperar la respuesta completa hace que **la latencia percibida iguale el tiempo total de procesado** en lugar del TTFT, mucho más corto.

Y el quinto problema frecuente de la misma área es el que más se olvida: **las invocaciones de herramienta a mitad de stream pausan la salida sin progreso visible**, creando la sensación de cuelgue. La contramedida del nivel 4: que las invocaciones de herramienta durante el streaming **emitan eventos estructurados de progreso** al cliente.

### Guardrails en streaming: la decisión de modo

De [Configure streaming response behavior to filter content](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-streaming.html). Con guardrails sobre una respuesta en streaming hay **dos modos**, y la elección es un trade-off explícito:

| Modo | Comportamiento | Trade-off |
| --- | --- | --- |
| **Synchronous** (por defecto) | Guardrails **almacena en buffer** y aplica las políticas a uno o varios chunks **antes** de enviarlos al usuario | Introduce **latencia** en los chunks, porque la respuesta se retrasa hasta que el escaneo termina. A cambio, **mejor precisión**: cada chunk se escanea antes de salir |
| **Asynchronous** | Envía los chunks al usuario **en cuanto están disponibles**, aplicando las políticas en background | **Sin impacto de latencia**, pero los chunks **pueden contener contenido inapropiado** hasta que el escaneo termina. En cuanto se identifica, **los chunks siguientes se bloquean** |

Se habilita con el parámetro `streamProcessingMode`:

```json
{
  "amazon-bedrock-guardrailConfig": {
    "streamProcessingMode": "ASYNCHRONOUS"
  }
}
```

Con la Converse API el equivalente es el objeto `GuardrailStreamConfiguration` del `guardrailConfig`, que acepta el mismo campo.

> **Aviso crítico**: Bedrock Guardrails **no soporta el enmascarado de información sensible en modo asíncrono**. Si el caso de uso depende de enmascarar PII, el modo asíncrono no es una opción.

### Guardrails y tool use: lo que NO se evalúa

De [Include a guardrail with the Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-converse-api.html). Este es uno de los datos más importantes de todo el dominio, y es fácil suponer lo contrario. Cuando se usan herramientas, **el guardrail especificado en `guardrailConfig` no evalúa todos los campos** de la petición y la respuesta:

| Contenido | Campo | ¿Evaluado? |
| --- | --- | --- |
| **Resultados de herramienta que devuelve tu aplicación** | `messages[].content[].toolResult` | **No** |
| **Definiciones de herramienta que envías** | `toolConfig.tools[].toolSpec.description`, `.inputSchema` | **No** |
| **Argumentos de llamada que genera el modelo** | `output.message.content[].toolUse.input` | **No** |
| Prompts de entrada, system prompts, respuestas del modelo | `text`, `guardContent` | **Sí** |

Esto aplica a **cualquier filtro** del guardrail: content filters, detección de prompt attack, denied topics, word filters y sensitive information filters.

> La consecuencia práctica: el contenido que vuelve de una herramienta (y que puede traer **prompt injection indirecta**) **no está cubierto por el guardrail de la invocación**. Hay que validarlo aparte, con **`ApplyGuardrail`** en un paso propio o con validación determinista. Es exactamente lo que se anticipaba en [Task 2.1 · Skill 2.1.3](./task-2-1-agentic-ai-y-herramientas.md#skill-213--workflows-con-salvaguardas-y-comportamiento-controlado) al tratar el resultado de herramienta como contenido no confiable.

### Las cuatro vías de entrega al cliente

| Vía | Mecanismo | Perfil |
| --- | --- | --- |
| **Lambda function URL con response streaming** | `InvokeWithResponseStream` | Lo más directo: sin API Gateway en medio |
| **API Gateway + Lambda proxy en modo stream** | `InvokeWithResponseStream` con formato específico | Cuando se necesita la capa de API Gateway (authorizers, usage plans, throttling) |
| **API Gateway WebSocket API** | Conexión bidireccional persistente | Cuando el backend debe **empujar** mensajes al cliente, o la interacción es conversacional de ida y vuelta |
| **AppSync subscriptions** | GraphQL sobre WebSocket | Cuando ya se usa AppSync y el resultado se publica a suscriptores |

### Lambda response streaming

De [Response streaming for Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html). Lambda puede hacer streaming de payloads de respuesta de forma nativa a través de **function URLs**, de la API **`InvokeWithResponseStream`**, o de la **integración proxy de API Gateway** (que internamente usa `InvokeWithResponseStream`).

| Aspecto | Dato |
| --- | --- |
| **Beneficio** | Mejora el **time to first byte (TTFB)** al enviar respuestas parciales en cuanto están disponibles |
| **Tamaño** | Hasta **200 MB**, frente a los **6 MB** máximos de respuestas bufferizadas |
| **Memoria** | La función **no necesita mantener la respuesta completa en memoria**, lo que puede reducir la memoria a configurar |
| **Ancho de banda** | **Sin límite en los primeros 6 MB**; después, máximo **2 MB/s**. Si las respuestas nunca exceden 6 MB, el límite nunca aplica |
| **Runtimes** | Soportado en **runtimes gestionados de Node.js**. Para otros lenguajes, **incluido Python**, hace falta un **custom runtime** con integración propia de la Runtime API, o el **Lambda Web Adapter** |
| **Disponibilidad** | **No está disponible en todas las Regiones de AWS** |

> **Tres avisos operativos**:
> - Las respuestas en streaming **incurren coste y no se interrumpen cuando la conexión del cliente se rompe**. Se factura la **duración completa de la función**, así que hay que ser cauto con timeouts largos.
> - Al probar la función **desde la consola de Lambda siempre se ven respuestas bufferizadas**.
> - El límite de banda aplica **solo al payload de respuesta**, no al acceso de red que hace la función.

**Compatibilidad con VPC**, que es una restricción de arquitectura real:

| Situación | Soporte |
| --- | --- |
| **Function URLs dentro de una VPC** | **No soportan** response streaming |
| **Dentro de una VPC vía SDK** | Sí, invocando con **`InvokeWithResponseStream`**, lo que requiere configurar los **VPC endpoints** apropiados para Lambda |
| **Requisito** | Crear un **interface VPC endpoint para Lambda** para la comunicación entre los recursos de la VPC y el servicio |

```
Cliente en la VPC ──► Interface VPC endpoint para Lambda ──► Función Lambda
                                                                   │
                     ◄─────────── streaming de vuelta por la misma ruta
```

### Streaming a través de API Gateway

De [Set up a Lambda proxy integration with payload response streaming](https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode-lambda.html). Las diferencias respecto a una integración proxy normal:

| Diferencia | Detalle |
| --- | --- |
| **API usada** | API Gateway usa **`InvokeWithResponseStream`**, lo que produce un **URI distinto**, con otra fecha de versión de API y otra acción de servicio: `arn:aws:apigateway:REGION:lambda:path/2021-11-15/functions/FUNCTION_ARN/response-streaming-invocations` |
| **Momento de envío** | En proxy normal, API Gateway envía la respuesta **solo tras recibirla completa** de Lambda. En modo streaming, **empieza el stream del payload tras recibir metadatos válidos y el delimitador** |
| **Formato** | El **formato de entrada es el mismo** que el de la integración proxy, pero **requiere un formato de salida distinto** |

El formato de salida, con el delimitador separando los metadatos JSON del payload en bruto:

```
{
  "headers": {"headerName": "headerValue", ...},
  "multiValueHeaders": { "headerName": ["headerValue", "headerValue2", ...], ... },
  "cookies" : ["cookie1", "cookie2"],
  "statusCode": httpStatusCode
}<DELIMITER>PAYLOAD1 | PAYLOAD2 | PAYLOAD3
```

Las reglas del formato:

| Regla | Detalle |
| --- | --- |
| **Delimitador** | Debe ser **8 bytes nulos** y aparecer **dentro de los primeros 16 KB** de datos del stream |
| **Metadatos** | JSON válido. Solo se soportan las claves `headers`, `multiValueHeaders`, `cookies` y `statusCode`; todas pueden omitirse |
| **`headers`** | Solo headers de valor único |
| **`multiValueHeaders`** | Headers multi-valor y también de valor único |
| **Fusión** | Si se especifican ambos, API Gateway los fusiona; si el mismo par clave-valor está en los dos, **solo aparece el de `multiValueHeaders`** |
| **Chunked transfer encoding** | La salida espera headers con **`Transfer-Encoding: chunked`** o **`Content-length`**. **Si la función no devuelve ninguno de los dos, API Gateway añade `Transfer-Encoding: chunked`** |
| **Payload** | API Gateway **no requiere un formato específico** para el payload de la respuesta del método |

> Ahí está el *chunked transfer encoding* que nombra el skill: no es algo que se configure en API Gateway, es el header que API Gateway **añade automáticamente** si la función no lo declara.

**Las combinaciones soportadas** son estrictas, y la tabla oficial deja claro que solo dos funcionan:

| Modo de transferencia | ¿La función cumple el formato? | API de invocación | ¿Soportado? |
| --- | --- | --- | --- |
| **Stream** | **Sí** | `InvokeWithResponseStream` | **Sí**: API Gateway hace streaming de la respuesta |
| Stream | No | `InvokeWithResponseStream` | No: invoca la función y **devuelve un error 500** |
| Stream | Sí | `Invoke` | No soportado |
| Stream | No | `Invoke` | No soportado |
| Buffered | Sí | `InvokeWithResponseStream` | No soportado |
| Buffered | No | `InvokeWithResponseStream` | No soportado |
| **Buffered** | Sí | `Invoke` | Devuelve headers y status code (comportamiento bufferizado normal) |

> Si se usa una **function URL** para hacer streaming y luego se quiere poner API Gateway delante, **hay que modificar la entrada y la salida de la función** para cumplir estos requisitos. No es intercambiable.

### WebSocket APIs de API Gateway

De [Overview of WebSocket APIs in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api-overview.html). Se crea una WebSocket API como **frontend con estado** para un servicio de AWS (Lambda, DynamoDB) o para un endpoint HTTP. A diferencia de una REST API, que recibe y responde peticiones, **soporta comunicación bidireccional**: el backend puede enviar mensajes de callback a los clientes conectados.

Los mensajes JSON entrantes se dirigen a integraciones de backend según **rutas** configuradas (los no-JSON van a la ruta `$default`). Una ruta incluye una **route key**, el valor que se espera tras evaluar la **route selection expression**, un atributo definido a nivel de API (`routeSelectionExpression`) que especifica una propiedad JSON que debe estar presente en el payload. Ejemplo oficial: si los mensajes tienen una propiedad `action`, la expresión puede ser `${request.body.action}`.

**Las tres rutas predefinidas**, más las personalizadas:

| Ruta | Cuándo se invoca |
| --- | --- |
| **`$connect`** | Cuando se **inicia** la conexión persistente entre cliente y API |
| **`$disconnect`** | Cuando el cliente o el servidor se **desconecta** |
| **Rutas personalizadas** | Tras evaluar la route selection expression, si hay coincidencia; la coincidencia determina qué integración se invoca |
| **`$default`** | Si la expresión **no se puede evaluar** o **no hay ruta coincidente** |

**Enviar datos a los clientes conectados**, que es lo que hace útil el WebSocket para GenAI: usar una integración para devolver una respuesta que se entrega por una **route response** definida, o usar la **API `@connections`** para enviar una petición POST.

**Los códigos de estado**, que definen los límites operativos de la conexión:

| Código | Significado |
| --- | --- |
| **1001** | El cliente está **inactivo 10 minutos** o alcanza el **máximo de 2 horas de vida de la conexión** |
| **1003** | El endpoint recibe un **tipo de medio binario**: los tipos binarios **no están soportados** en WebSocket APIs |
| 1005 | El cliente envía un close frame sin código de cierre |
| 1006 | Cierre inesperado de la conexión (la conexión TCP se cerró sin close frame) |
| **1008** | El endpoint recibe **demasiadas peticiones** de un cliente concreto |
| **1009** | El endpoint recibe un mensaje **demasiado grande** para procesarlo |
| 1011 | Error interno del servidor |
| 1012 | El servicio se reinicia |

> Los dos límites duros que condicionan el diseño: **10 minutos de inactividad** y **2 horas de vida máxima**. Una sesión de chat larga necesita reconexión con recuperación de contexto desde donde se persista (AgentCore Memory o DynamoDB, según [Task 2.1 · Skill 2.1.1](./task-2-1-agentic-ai-y-herramientas.md#tabla-de-decisión-dónde-vive-el-estado)).

### Arquitectura de un chat en streaming

```
Navegador
   │  WebSocket
   ▼
┌───────────────────────────────────────────────────────────────────┐
│ API Gateway WebSocket API                                         │
│   $connect     ──► Lambda: autorizar, registrar connectionId      │
│                            en DynamoDB                            │
│   sendMessage  ──► Lambda: iniciar la generación                  │
│   $disconnect  ──► Lambda: limpiar el registro                    │
│   $default     ──► Lambda: mensaje no reconocido                  │
│   Límites: 10 min inactivo · 2 h de vida · sin medios binarios    │
└───────────────────────────────────────────────────────────────────┘
   │
   ▼
┌───────────────────────────────────────────────────────────────────┐
│ Lambda de generación                                              │
│   ConverseStream con guardrailConfig                               │
│     streamProcessingMode: SYNCHRONOUS  → precisión                │
│                           ASYNCHRONOUS → latencia (sin masking)   │
│   Por cada chunk: @connections POST al connectionId                │
│   Si hay tool use a mitad de stream: emitir EVENTO DE PROGRESO     │
│     (AGENTPERF02: evitar el silencio percibido como cuelgue)      │
│   Validar el toolResult aparte con ApplyGuardrail: el guardrail   │
│     de la invocación NO evalúa toolResult                          │
│   Persistir el turno completo al terminar                          │
└───────────────────────────────────────────────────────────────────┘
```

### Tabla de decisión de la vía de entrega

| | **Lambda function URL** | **API Gateway + Lambda stream** | **WebSocket API** | **AppSync subscriptions** |
| --- | --- | --- | --- | --- |
| **Dirección** | Servidor → cliente | Servidor → cliente | **Bidireccional** | Servidor → cliente |
| **Estado** | Sin estado | Sin estado | **Con estado** (`connectionId`) | Con estado (suscripción) |
| **Authorizers de API Gateway** | No | **Sí** | Sí | Auth de AppSync |
| **Usage plans / API keys** | No | **Sí** | — | — |
| **Límite de duración** | Timeout de Lambda | Timeout de Lambda | **10 min inactivo, 2 h total** | — |
| **En VPC** | **No soporta streaming** | Vía SDK con VPC endpoint | Sí | Sí |
| **Complejidad** | Mínima | Media (formato de salida estricto) | Alta (gestión de conexiones) | Media |

---

## Skill 2.4.3 — Sistemas de FM resilientes

> *Crear sistemas de FM resilientes para asegurar operaciones fiables (por ejemplo, usando el SDK de AWS para exponential backoff, API Gateway para gestionar rate limiting, mecanismos de fallback para degradación elegante, AWS X-Ray para proporcionar observabilidad entre fronteras de servicio).*

### Reintentos del SDK: los tres modos

De [Retry behavior](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html). Cuando una petición falla por un error transitorio o por throttling, el SDK puede reintentarla automáticamente.

> **Aviso de versión importante**: el comportamiento descrito en la página oficial **requiere opt-in hasta que sea el predeterminado**, poniendo **`AWS_NEW_RETRIES_2026=true`** en el entorno. Sin ese ajuste, el SDK usa el comportamiento previo a 2026, que **difiere en el timing del backoff, en el coste de cuota de reintentos y en los valores por defecto específicos de servicio**.

| | **Standard** | **Adaptive** | **Legacy** |
| --- | --- | --- | --- |
| **Retry quota** | Sí | Sí | Varía según el SDK |
| **Puede retrasar la petición inicial** | **No** | **Sí** | No |
| **Backoff específico por tipo de error** | Sí | Sí | Varía según el SDK |
| **Estandarizado entre SDKs** | Sí | Sí | **No** |
| **Recomendación** | **Por defecto para todas las cargas** | Recurso único, con mucho throttling, tolerante a latencia | **Solo compatibilidad hacia atrás** |

**Standard mode** (por defecto) reintenta con **exponential backoff con jitter**, usando **retardos más cortos para errores transitorios** (timeouts de red) y **más largos para errores de throttling** (`ThrottlingException`).

Incluye una **retry quota**: un *token bucket* que descuenta tokens por cada reintento y los repone cuando las peticiones tienen éxito. Al agotarse los tokens, **el SDK devuelve el error sin reintentar**, de modo que la aplicación **falla rápido** en lugar de esperar reintentos improbables. El efecto secundario que destaca la documentación: **ayuda a que las interrupciones de servicio se resuelvan antes al reducir el tráfico de reintentos**. En operación normal la cuota está llena y no tiene efecto, y **nunca retrasa ni bloquea la petición inicial**: solo afecta a los reintentos.

**Adaptive mode** añade un **rate limiter del lado del cliente** que rastrea las respuestas de throttling y ajusta el ritmo de envío. A diferencia de standard, **puede retrasar o bloquear la petición inicial**. El rate limiter opera **por instancia de cliente del SDK**: todas las peticiones de un cliente comparten el mismo límite, independientemente de la operación o el recurso al que apunten.

| Usar adaptive cuando | **No** usar adaptive cuando |
| --- | --- |
| El cliente apunta a **un solo recurso** y se espera throttling frecuente. La documentación menciona explícitamente **cargas de IA que llaman a una sola operación con alto volumen** | El cliente envía peticiones a **varios recursos o sirve varios tenants**: el throttling en un recurso hace que el rate limiter **ralentice todas las peticiones de ese cliente**, incluidas las de recursos no afectados |
| Se quiere que el SDK frene automáticamente cuando el servicio señala throttling | Se necesita **latencia predecible** en la petición inicial |

> **Adaptive no está recomendado como valor por defecto general.**

**Legacy mode** es el comportamiento anterior a standard. **No incluye retry quota estandarizada**, así que un cliente **sigue reintentando a pleno ritmo durante una interrupción**, ocupando hilos y conexiones en peticiones improbables y **añadiendo carga que puede retrasar la recuperación del servicio**. Varía entre SDKs en número de reintentos, timing, conjunto de errores reintentables y comportamiento de throttling. Disponible en **Java, Python, Ruby, PHP, C++ y CLI**; **no disponible** en .NET, Go, Kotlin, Rust, Swift y JavaScript. La recomendación es clara: **si usas legacy, cambia a standard**.

### Configuración de los reintentos

| Ajuste | Qué controla | Variable de entorno | Clave del config file | Por defecto |
| --- | --- | --- | --- | --- |
| **Retry mode** | Qué estrategia usar | `AWS_RETRY_MODE` | `retry_mode` | **`standard`** |
| **Max attempts** | **Intentos totales, incluida la petición inicial** | `AWS_MAX_ATTEMPTS` | `max_attempts` | **`3`** |

Un valor de `3` significa **una petición inicial y hasta dos reintentos**. Poner **`1` deshabilita los reintentos por completo**.

> Excepción documentada: los clientes de **DynamoDB y DynamoDB Streams** usan **4 intentos** por defecto, con un **backoff base más corto (25 ms en lugar de 50 ms)** para ajustarse a su perfil de baja latencia. El intento adicional mantiene el backoff máximo del último reintento comparable al de otros servicios.

**Precedencia de configuración**, de mayor a menor: configuración explícita del cliente en código, **variable de entorno**, **shared config file** (`~/.aws/config`), y el valor por defecto del SDK.

### El flujo de un fallo

La secuencia oficial cuando una llamada falla:

```
1. (solo adaptive) Comprobar el rate limiter del cliente.
   Si se detectó throttling, puede retrasar o bloquear la petición ANTES de enviarla.
2. Enviar la petición al endpoint del servicio.
3. Si la respuesta es correcta, devolver el resultado.
4. Si falla, clasificar el error: TRANSIENT · THROTTLING · NON-RETRYABLE.
5. Si es no reintentable → devolver el error inmediatamente, sin reintento.
6. Si es reintentable → ¿se alcanzó el máximo de intentos? Si sí, devolver el error.
7. Comprobar la RETRY QUOTA (token bucket).
   Si el presupuesto está agotado → no reintentar y devolver el error.
   Excepción: en operaciones de long-polling, el SDK aún aplica un backoff
   antes de devolver el error.
8. Calcular el backoff según el TIPO DE ERROR y el número de intento.
```

> El paso 4 es el que conviene retener: **el SDK distingue transitorio de throttling y les aplica backoff distinto**. No es un backoff único.

### Rate limiting en API Gateway

De [Throttle requests to your REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html). API Gateway limita las peticiones con el **algoritmo de token bucket**, donde un token cuenta por petición, examinando la tasa y el burst de envíos **contra todas las APIs de la cuenta, por Región**.

> **Matiz oficial importante**: tanto los throttles como las cuotas se aplican **en base best-effort** y deben entenderse como **objetivos, no como techos garantizados**. Un burst puede permitir un rebasamiento predefinido de esos límites.

Cuando los envíos exceden la tasa en régimen estacionario y los límites de burst, API Gateway empieza a limitar y los clientes pueden recibir **`429 Too Many Requests`**. Al capturar esa excepción, **el cliente puede reenviar las peticiones fallidas de forma limitada en tasa**.

**Los cuatro tipos de ajuste**, de más general a más específico:

| Tipo | Alcance | ¿Modificable? |
| --- | --- | --- |
| **AWS throttling limits** | Todas las cuentas y clientes de una Región | **No, los fija AWS** |
| **Per-account limits** | Todas las APIs de una cuenta en una Región | Ampliable por petición. **Límites más altos son posibles con APIs de timeouts más cortos y payloads más pequeños**. No pueden superar los límites de AWS |
| **Per-API, per-stage limits** | A nivel de método de API para un stage; iguales para todos los métodos o distintos por método | No pueden superar los límites de AWS |
| **Per-client limits** | Clientes que usan **API keys asociadas a un usage plan** como identificador | No pueden superar los límites de cuenta |

**El orden de aplicación** es el dato que el examen puede preguntar:

```
1. Límites per-client o per-method de un usage plan para un stage
2. Límites per-method fijados para un stage de la API
3. Throttling a nivel de cuenta, por Región
4. Throttling regional de AWS
```

En un **usage plan** se fija un objetivo per-method para todos los métodos a nivel de API o de stage, especificando una **throttling rate** (la tasa, en peticiones por segundo, a la que se añaden tokens al bucket) y un **throttling burst** (la capacidad del bucket). El **burst limit** representa el número máximo objetivo de envíos concurrentes que API Gateway atenderá antes de devolver `429`.

### Fallback y degradación elegante

Las capas, combinando lo visto en los tasks anteriores:

| Capa | Mecanismo |
| --- | --- |
| **Reintento con backoff** | `retry_mode` standard del SDK, o el campo `Retry` de Step Functions con `BackoffRate`, `MaxDelaySeconds` y `JitterStrategy: FULL` (ver [Task 2.1 · Skill 2.1.3](./task-2-1-agentic-ai-y-herramientas.md#circuit-breaker-y-degradación-elegante)) |
| **Fail fast** | La retry quota del SDK, que evita esperar reintentos improbables |
| **Otro modelo** | Cascada a un modelo alternativo ante throttling persistente |
| **Otra Región** | Cross-Region inference, geográfica o global según el requisito jurisdiccional (ver [Task 2.3 · Skill 2.3.4](./task-2-3-integracion-empresarial.md#residencia-de-datos-y-la-elección-del-inference-profile)) |
| **Circuit breaker** | Por modelo y por herramienta, con **sonda de recuperación** que cierra el disyuntor; sin ella se queda abierto (problema frecuente 5 de [AGENTREL06](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel06.html)) |
| **Cadena de fallback ordenada** | Con trade-offs de calidad documentados, según [AGENTREL04-BP03](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel04.html) |
| **Fallback por tipo de dato** | Caché para datos de referencia, cola SQS para transaccional, degradación para tiempo real (AGENTREL06-BP02) |
| **Encolar en lugar de fallar** | SQS absorbe el pico; el trabajo no se pierde |
| **Respuesta degradada** | Devolver un resultado sin la parte que falló, indicándolo, en lugar de un error genérico |
| **Presupuesto de latencia** | Las rutas de recuperación acotadas por presupuestos explícitos, para que **no erosionen el SLO en silencio** (AGENTPERF02) |
| **Validación de las rutas** | **AWS Fault Injection Service**, en CI/CD según AGENTREL06 nivel 4 |

### Observabilidad entre fronteras de servicio: X-Ray

De [What is AWS X-Ray?](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html). Recoge datos sobre las peticiones que sirve la aplicación y aporta herramientas para ver, filtrar y obtener insights, identificando problemas y oportunidades de optimización. Para cualquier petición trazada se ve información detallada **no solo de la petición y la respuesta, sino también de las llamadas que la aplicación hace a recursos de AWS downstream, microservicios, bases de datos y APIs web**.

| Concepto | Detalle |
| --- | --- |
| **Instrumentación** | Enviar datos de traza de peticiones entrantes y salientes y de otros eventos, junto con metadatos de cada petición. **Muchos escenarios requieren solo cambios de configuración** |
| **Servicios integrados** | Los servicios de AWS integrados con X-Ray pueden **añadir cabeceras de traza** a las peticiones entrantes, enviar datos de traza, o ejecutar el daemon. **Lambda puede enviar datos de traza y ejecutar el daemon de X-Ray en los workers** |
| **X-Ray daemon** | Los SDK cliente **no envían a X-Ray directamente**: envían documentos de segmento JSON a un **proceso daemon que escucha tráfico UDP**. El daemon **encola los segmentos y los sube en lotes**. Disponible para Linux, Windows y macOS, e **incluido en las plataformas de Elastic Beanstalk y Lambda** |
| **Trace map** | Mapa detallado que muestra el cliente, el servicio frontend y los servicios backend que este llama. Se usa para **identificar cuellos de botella, picos de latencia y otros problemas** |

Lo que hay que trazar específicamente en una aplicación GenAI:

```
Cliente
  │
  ├─ segmento: API Gateway
  │    └─ subsegmento: authorizer
  │    └─ subsegmento: request validation
  │
  ├─ segmento: Lambda
  │    └─ subsegmento: AppConfig (resolver modelo y prompt)
  │    └─ subsegmento: DynamoDB (histórico o idempotencia)
  │    └─ subsegmento: Bedrock Retrieve       ← latencia del retrieval
  │    └─ subsegmento: Bedrock Converse       ← latencia de inferencia
  │         anotaciones: modelId, tokens de entrada y salida,
  │                      stopReason, tier de servicio,
  │                      cache hit de prompt caching
  │    └─ subsegmento: Lambda de herramienta  ← latencia de la herramienta
  │
  └─ segmento: sistema legacy vía adaptador
```

Las **anotaciones** son lo que convierte la traza en algo accionable: permiten filtrar por `modelId`, por tier o por si hubo cache hit, y correlacionar latencia con la decisión de routing. Complementan, no sustituyen, a los mecanismos de [Task 1.6 · Skill 1.6.3](../domain-1/task-1-6-prompt-engineering-governance.md): el campo `requestMetadata` de la petición para filtrar los invocation logs, y **AgentCore Observability** con OTEL para las trazas de agente.

---

## Skill 2.4.4 — Routing inteligente de modelos

> *Desarrollar sistemas inteligentes de routing de modelos para optimizar la selección de modelo (por ejemplo, usando código de aplicación para implementar configuraciones de routing estático, Step Functions para routing dinámico basado en contenido hacia FMs especializados, routing inteligente de modelos basado en métricas, API Gateway con transformaciones de petición para la lógica de routing).*

### Las cuatro estrategias que nombra el skill

| Estrategia | Dónde vive la decisión | Qué la dispara |
| --- | --- | --- |
| **Routing estático** | Código de aplicación o configuración | El tipo de operación, el tenant, el entorno |
| **Routing dinámico por contenido** | Step Functions | El contenido de la petición, evaluado por reglas o por un clasificador |
| **Routing por métricas** | Código o configuración, alimentado por CloudWatch | Latencia observada, tasa de throttling, coste acumulado |
| **Routing en el borde** | API Gateway con transformaciones de petición | El path, un header, el consumidor identificado por API key |

A las que hay que añadir la opción gestionada:

| Estrategia | Dónde vive |
| --- | --- |
| **Intelligent prompt routing** | Bedrock, en un endpoint serverless único. Detalle completo en [Task 2.2 · Skill 2.2.3](./task-2-2-despliegue-de-modelos.md#intelligent-prompt-routing-la-cascada-gestionada) |

### Routing estático externalizado

El routing estático no tiene que estar hardcodeado. El patrón documentado, ya cubierto en [Task 1.2 · Skill 1.2.2](../domain-1/task-1-2-seleccion-y-configuracion-fm.md), es **AWS AppConfig**: la aplicación lee la configuración activa y el cambio de modelo no requiere despliegue.

El nivel 4 de madurez de [AGENTPERF02](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentperf02.html) lo formula como requisito: las **asignaciones de modelo y las reglas de routing se externalizan como configuración de runtime en AppConfig** y se promueven mediante **rollouts progresivos gobernados por alarmas de CloudWatch**.

```
Aplicación ──► AppConfig Agent (caché local) ──► configuración activa
                                                   │
                                                   ├─ mapa tarea → modelId
                                                   ├─ versión de prompt
                                                   ├─ versión de guardrail
                                                   ├─ serviceTier por entorno
                                                   └─ performanceConfig.latency

Promoción:  validators ──► deployment strategy gradual ──► alarma CloudWatch
                                                            │
                                                            └─ rollback automático
```

> El detalle que aporta valor real: externalizar **también el `serviceTier`**. El nivel 2 de [AGENTCOST02](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentcost02.html) pide alinear cada entorno al tier on-demand adecuado (Flex en dev, Standard en producción, Priority solo si el throttling afecta a usuarios). Si el tier está en el código, cambiarlo es un despliegue.

### Routing dinámico por contenido con Step Functions

El patrón que pide el skill, aprovechando el `Choice` state y las integraciones ya descritas en [Task 2.1 · Skill 2.1.2](./task-2-1-agentic-ai-y-herramientas.md#skill-212--razonamiento-estructurado-y-descomposición-de-problemas):

```
Petición
   │
   ▼
┌──────────────────────────────────────────────────────────────┐
│ Task: clasificar                                              │
│   · reglas deterministas (longitud, idioma, tipo de adjunto)  │
│   · o modelo pequeño / Comprehend para intención              │
│   · o CountTokens para decidir por tamaño de contexto         │
└──────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────┐
│ Choice                                                        │
│   clasificación = 'resumen_corto'   ──► FM económico          │
│   clasificación = 'razonamiento'    ──► FM capaz              │
│   clasificación = 'multimodal'      ──► FM multimodal         │
│   clasificación = 'dominio_propio'  ──► endpoint SageMaker AI │
│   Default                           ──► FM por defecto        │
└──────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────┐
│ Task: invocar (integración optimizada con Bedrock)            │
│   Retry: BackoffRate · MaxDelaySeconds · JitterStrategy FULL  │
│   Catch: States.ALL ──► ruta de fallback                      │
└──────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────┐
│ Choice: ¿confianza suficiente?                                │
│   no ──► escalar al modelo siguiente de la cascada            │
│          (vigilar el cascade escalation rate)                 │
└──────────────────────────────────────────────────────────────┘
```

Dos avisos de diseño ya establecidos que aplican aquí:

- Definir siempre **`Default`** en el `Choice`: sin él, si ninguna regla evalúa a `true`, la state machine **lanza un error** por no poder salir del estado.
- **Express solo soporta Request Response**. Un routing que necesite `.sync` o `.waitForTaskToken` tiene que ser **Standard**.

Y la advertencia del quinto problema frecuente de [AGENTSEC04](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec04.html) aplicada al clasificador: si el clasificador es un LLM **expuesto al mismo contenido no confiable** que clasifica, puede ser influido. Para decisiones con consecuencia de seguridad o coste, la clasificación debe ser determinista.

### Routing por métricas

| Señal | Fuente | Decisión que habilita |
| --- | --- | --- |
| **Tasa de throttling** | Métricas de CloudWatch de Bedrock | Desviar a otro modelo, otro tier o otra Región |
| **Latencia p95** | CloudWatch, X-Ray | Cambiar a un modelo más rápido o activar latency-optimized |
| **Tokens y coste acumulado** | `usage` de la respuesta, invocation logs con `requestMetadata` | Degradar a modelo económico al acercarse al presupuesto |
| **Cascade escalation rate** | Métrica propia | Ajustar el umbral de confianza o cambiar el modelo base de la cascada |
| **Cache hit rate** | Campos de cache usage de la respuesta | Reordenar el prompt (estático primero) o ajustar checkpoints |
| **Score de calidad** | Bedrock evaluations, AgentCore Evaluations | Promover o revertir una asignación de modelo |
| **Estado del disyuntor** | DynamoDB, alimentado por la sonda `/ping` | Saltar un destino no sano **sin esperar timeouts** |

Las métricas de `usage` y los campos de cache usage son la fuente que hace posible el routing por coste: la propia respuesta dice cuánto costó.

### Routing en el borde con API Gateway

API Gateway puede decidir el destino antes de que el cómputo entre en juego:

| Mecanismo | Uso |
| --- | --- |
| **Por path o método** | `/v1/summarize` y `/v1/reason` a integraciones distintas |
| **Transformaciones de petición** | Mapping templates que inyectan el `modelId`, el `serviceTier` o el `guardrailIdentifier` según un header o el consumidor |
| **Stage variables** | Un mismo API con stages que apuntan a configuraciones distintas |
| **API keys y usage plans** | Cuota distinta por consumidor, y con ella una asignación de modelo distinta por plan |
| **Authorizer** | El authorizer puede devolver contexto (por ejemplo, el tier del cliente) que la integración usa para elegir destino |

> Recordatorio del orden de throttling: los límites **per-client de un usage plan se aplican primero**, antes de los per-method del stage, los de cuenta y los regionales de AWS. Es el mecanismo para que un consumidor ruidoso no agote la cuota de los demás.

### Tabla comparativa de las estrategias

| | **Estático (AppConfig)** | **Dinámico (Step Functions)** | **Por métricas** | **En el borde (API Gateway)** | **Intelligent prompt routing** |
| --- | --- | --- | --- | --- | --- |
| **Latencia añadida** | Nula (caché local del agente) | **Alta**: clasificación + transiciones de estado | Baja | Muy baja | Baja, gestionada |
| **Coste añadido** | Mínimo | Transiciones de estado + inferencia del clasificador | Métricas y lógica | Mínimo | Gestionado |
| **Complejidad operativa** | Baja | **Alta** | Media | Baja | **Mínima** |
| **Granularidad** | Por configuración | **Por petición, por contenido** | Por condición observada | Por path, header o consumidor | Por petición |
| **Cruza familias de modelo** | Sí | Sí | Sí | Sí | **No: misma familia** |
| **Multiidioma** | Sí | Sí | Sí | Sí | **No: optimizado solo para inglés** |
| **Usa métricas propias de la aplicación** | Sí | Sí | **Sí** | Sí | **No** |
| **Cuándo** | Cambiar de modelo sin desplegar | Tareas heterogéneas que requieren FMs especializados | Optimización operativa continua | Separación por contrato o por consumidor | Empezar rápido dentro de una familia |

La lectura de la tabla: **intelligent prompt routing** es la opción de menor esfuerzo, pero sus tres limitaciones oficiales (misma familia, solo inglés, no ajusta por datos de rendimiento de la aplicación) marcan cuándo hay que construir el routing. Y **Step Functions** da la máxima granularidad al precio más alto en latencia y coste: cada transición de estado se factura en Standard, y los **reintentos también cuentan como transiciones**.

### Combinación recomendada

```
BORDE          API Gateway
               · request validation (rechazar antes de gastar tokens)
               · authorizer que aporta el tier del consumidor al contexto
               · usage plan por consumidor (se aplica ANTES del resto)
               · transformación que inyecta modelId o serviceTier
                  │
CONFIGURACIÓN  AppConfig
               · mapa tarea → modelo, versión de prompt y de guardrail
               · serviceTier por entorno (Flex dev · Standard prod)
               · rollout progresivo con alarma y rollback automático
                  │
DECISIÓN       clasificación determinista cuando hay consecuencia de
               seguridad o coste; modelo pequeño cuando es una
               estimación de complejidad
                  │
EJECUCIÓN      cascada: modelo económico primero, escalar por baja
               confianza; medir el cascade escalation rate
                  │
RESILIENCIA    SDK en retry_mode standard (backoff distinto para
               transitorio y throttling, retry quota para fail fast)
               circuit breaker con sonda de recuperación
               cadena de fallback ordenada
                  │
OBSERVACIÓN    X-Ray con anotaciones de modelId, tokens y cache hit
               invocation logs filtrables por requestMetadata
               CloudWatch para throttling, p95 y coste por dimensión
```
