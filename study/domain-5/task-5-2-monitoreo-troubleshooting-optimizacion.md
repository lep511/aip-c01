# Task 5.2 — Troubleshooting de aplicaciones GenAI

[← Volver al índice](./README.md)

Skills cubiertos: **5.2.1**, **5.2.2**, **5.2.3**, **5.2.4**, **5.2.5**.

El Task 5.1 es **medición**: producir un número que caracterice la calidad. El Task 5.2 es **diagnóstico**: partir de un síntoma y llegar a la causa. Cambia el vocabulario y cambian las fuentes: aquí lo que manda son los códigos de error de la API, las razones de parada de la respuesta, las cuotas y los logs.

El hilo conductor del task, y lo que más preguntas genera, es una sola idea: **en una aplicación GenAI muchos fallos no llegan como error**. Llegan como una respuesta con estado 200 que está incompleta, truncada o mal formada. Un `try` alrededor de la llamada al modelo no los ve. El campo que hay que mirar es la razón de parada.

La base de troubleshooting con CloudWatch Logs Insights, X-Ray y reconocimiento de patrones de error está en [Domain 2 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#skill-256--troubleshooting-de-aplicaciones-de-fm). Los modos de fallo propios de GenAI que no existen en ML tradicional están en [Domain 4 · Skill 4.3.6](../domain-4/task-4-3-herramientas-vector-stores-y-fallos.md#skill-436--troubleshooting-de-modos-de-fallo-propios-de-genai). Este task añade el diagnóstico por síntoma.

---

## Skill 5.2.1 — Manejo de contenido, contexto y truncamiento

> *Resolver problemas de manejo de contenido para asegurar que la información necesaria se procesa de forma completa en las interacciones con el FM (por ejemplo, usando diagnóstico de desbordamiento de la ventana de contexto, estrategias dinámicas de chunking, optimización del diseño del prompt, análisis de errores relacionados con truncamiento).*

### Las nueve razones de parada, y las cuatro que son un fallo

Es el dato central del task. La respuesta de la [Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) trae un campo `stopReason` con **nueve valores válidos**, y cuatro de ellos indican un problema aunque el HTTP sea 200.

| Valor de `stopReason` | Significado | ¿Es un fallo? |
| --- | --- | --- |
| `end_turn` | El modelo terminó su turno con normalidad | No |
| `tool_use` | El modelo pide invocar una herramienta | No |
| `stop_sequence` | Se alcanzó una secuencia de parada configurada | No |
| **`max_tokens`** | **La respuesta se cortó al alcanzar el límite de tokens de salida** | **Sí: truncamiento** |
| **`model_context_window_exceeded`** | **La entrada excedió la ventana de contexto del modelo** | **Sí: desbordamiento** |
| `guardrail_intervened` | Un guardrail intervino | Depende del diseño |
| `content_filtered` | El contenido fue filtrado | Depende del diseño |
| **`malformed_model_output`** | **El modelo produjo una salida mal formada** | **Sí** |
| **`malformed_tool_use`** | **El modelo produjo una llamada a herramienta mal formada** | **Sí** |

> **Dato decisivo del task entero**: **el desbordamiento de la ventana de contexto no llega como excepción.** Llega como respuesta correcta con `stopReason` igual a `model_context_window_exceeded`. Una aplicación que solo trata excepciones **no detecta nunca** ni el desbordamiento ni el truncamiento. El diagnóstico de desbordamiento que el skill pide es, literalmente, inspeccionar ese campo.

### Truncamiento frente a desbordamiento: dos fallos, dos remedios

| Aspecto | Truncamiento | Desbordamiento |
| --- | --- | --- |
| **Señal** | `stopReason` igual a `max_tokens` | `stopReason` igual a `model_context_window_exceeded` |
| **Qué se perdió** | El final de la **salida** | Parte de la **entrada** |
| **Causa** | El límite de tokens de salida es menor que lo que el modelo necesitaba | El prompt más el contexto más el historial superan la ventana del modelo |
| **Remedio** | Subir el límite de salida, o pedir una respuesta más corta en el prompt | Recortar contexto: menos chunks, historial resumido, chunking más fino |

> **Gotcha del límite de salida**: subir el límite de tokens **no es gratis**, y no solo por el coste. Según [How tokens are counted in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html), el valor de `max_tokens` **se descuenta de la cuota al principio de la petición**, antes de saber cuánto va a generar el modelo. Un límite inflado "por si acaso" consume cuota que no se usa y **reduce la concurrencia** que la cuota admite.

### Cómo se descuenta la cuota, y por qué importa al diagnosticar

De [Quotas for the bedrock-runtime endpoint](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-runtime.html) y de la página de burndown. El ciclo tiene tres momentos:

| Momento | Qué se descuenta |
| --- | --- |
| **Al iniciar la petición** | Tokens de entrada **más `max_tokens`**. Si eso supera la cuota, la petición se throttlea |
| **Durante el procesado** | La cuota consumida se ajusta periódicamente según los tokens de salida que se van generando |
| **Al terminar** | El consumo real se calcula y **los tokens no usados se devuelven a la cuota** |

La fórmula final es tokens de entrada, más los tokens escritos en caché, más los tokens de salida **multiplicados por la tasa de burndown**. Los tokens **leídos** de caché no entran en el cálculo y no cuentan contra la cuota.

Las tasas de burndown de salida documentadas:

| Modelos | Tasa |
| --- | --- |
| Anthropic Claude versión 4.8 | **15x** |
| Anthropic Claude Opus 5.5, Sonnet 5, Opus 5 y Fable 5.1 | **10x** |
| OpenAI GPT-5.6 Sol, Terra y Luna en `bedrock-runtime` | **10x** |
| Anthropic versión 4.7 y anteriores | **5x** |
| Todos los demás | **1:1** |

> **Dato decisivo para diagnosticar un throttling inesperado**: con una tasa de 5x, una petición de 1.000 tokens de entrada que genera 100 de salida **consume 1.500 tokens de cuota** pero **se factura por 1.100**. La cuota se agota antes de lo que sugiere la factura. Si el síntoma es "me throttlean antes de lo esperado", la primera palanca documentada es **bajar `max_tokens`** para que aproxime el tamaño real de las respuestas.

Dos detalles de alcance que cambian el diagnóstico:

- Las cuotas de un modelo en el endpoint `bedrock-runtime` **se comparten entre todas las APIs de inferencia**: `InvokeModel`, `Converse`, Responses y Chat Completions. Aunque los nombres de cuota mencionen `InvokeModel`, **no son por API**.
- El endpoint `bedrock-runtime` cuenta entrada y salida **juntas contra una sola cuota de tokens por minuto**. El endpoint [`bedrock-mantle`](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html) aplica **cuotas separadas** de entrada y de salida, y el burndown no aplica ahí.
- Las cuotas de peticiones por minuto **son específicas de modelo**: algunos modelos no tienen cuota de peticiones y se gobiernan solo por tokens.

### Chunking dinámico como remedio de contexto

De [How content chunking works for knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html). Las estrategias, y qué problema de contexto resuelve cada una:

| Estrategia | Parámetros | Cuándo es el remedio |
| --- | --- | --- |
| **Fixed-size** | Tokens por chunk y **porcentaje de solape** | Control directo del tamaño del contexto recuperado |
| **Default** | Ninguno: chunks de **unos 300 tokens**, respetando límites de frase | Punto de partida razonable sin ajuste |
| **Hierarchical** | Tamaño de chunk padre, tamaño de chunk hijo y **tokens de solape absolutos** | Cuando se necesita precisión al buscar y amplitud al generar |
| **Semantic** | Máximo de tokens, **buffer size** y **umbral de percentil de breakpoint** | Cuando los límites naturales del contenido importan más que el tamaño |
| **Sin chunking** | Ninguno | Documentos ya pre-troceados en ficheros separados |

El mecanismo del chunking jerárquico explica por qué es una palanca de contexto: durante la recuperación **el sistema recupera primero los chunks hijo y los sustituye por los chunks padre**, más amplios, para dar al modelo más contexto. Embeddings pequeños son más precisos, pero la recuperación busca contexto completo; la jerarquía equilibra las dos cosas.

Tres consecuencias documentadas que hay que conocer:

> **Gotcha 1**: como los chunks hijo se sustituyen por los padre, **el número de resultados devueltos puede ser menor que el solicitado**.

> **Gotcha 2**: el chunking jerárquico **no se recomienda con un bucket de vectores de S3 como vector store**, y con un número alto de tokens de chunking, por encima de unos 8.000 tokens combinados, se puede chocar con **límites de tamaño de metadatos**.

> **Gotcha 3**: con la opción de no chunking **se pierde el número de página en las citas** y la capacidad de filtrar por el campo de metadatos de número de página. Es un coste de trazabilidad, no solo de recuperación.

Dos detalles más sobre el semantic chunking: el **buffer size** define cuántas frases de alrededor se añaden para crear el embedding, así que un buffer de 1 combina la frase actual con la anterior y la siguiente; un buffer grande captura más contexto pero **introduce ruido**, y uno pequeño puede perder contexto pero trocea con más precisión. Y el **umbral de percentil** más alto exige que las frases sean más distinguibles para separarlas, lo que produce **menos chunks y más grandes**. El semantic chunking **tiene coste adicional** porque usa un foundation model.

> **Dato decisivo sobre el chunking de contenido parseado**: con contenido que pasó por parsers avanzados o se convirtió desde HTML, Bedrock puede trocear para optimizar resultados, y **respeta los límites lógicos del documento**, como páginas o secciones: no une contenido a través de esos límites **aunque subir el tamaño máximo de token lo permitiese**. El tamaño configurado es un techo, no una garantía.

Las estrategias de chunking como decisión de diseño están en [Domain 1 · Skill 1.5.1](../domain-1/task-1-5-retrieval.md#skill-151--segmentación-de-documentos-chunking). La optimización de la ventana de contexto como palanca de coste está en [Domain 4 · Skill 4.1.1](../domain-4/task-4-1-costes-y-eficiencia-de-recursos.md#skill-411--sistemas-de-eficiencia-de-tokens).

### El otro límite de contenido: el tamaño del payload

El cuerpo de una petición de [`InvokeModel`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html) admite **hasta 25.000.000 caracteres**. Pasado eso el error no es de ventana de contexto sino de transporte, y aparece como entidad de petición demasiado grande con estado **413**. Es un fallo distinto con un remedio distinto: reducir el tamaño del cuerpo, no recortar contexto.

---

## Skill 5.2.2 — Diagnóstico de la integración con el FM

> *Diagnosticar y resolver problemas de integración del FM para identificar y arreglar fallos de integración de API específicos de servicios GenAI (por ejemplo, usando logging de errores, validación de peticiones, análisis de respuestas).*

### La página que hay que conocer

La fuente canónica es [Troubleshooting Amazon Bedrock API Error Codes](https://docs.aws.amazon.com/bedrock/latest/userguide/troubleshooting-api-error-codes.html), que para cada error da **causa y solución**. Los [errores comunes de la API](https://docs.aws.amazon.com/bedrock/latest/APIReference/CommonErrors.html) son el complemento.

### Los tres errores de capacidad que se confunden

Es la distinción más rentable del skill, porque los tres significan "ahora no puedo" y el remedio difiere.

| Error | Estado | Causa | Remedio documentado |
| --- | --- | --- | --- |
| **`ThrottlingException`** | **429** | Se excedieron **las cuotas de la cuenta** | Reintentos con backoff exponencial y jitter, Provisioned Throughput, o pedir aumento de cuota |
| **`overloaded_error`** | **529** | El modelo no puede procesar por **alta demanda o capacidad de servicio insuficiente**. Error **transitorio de capacidad**, explícitamente distinto de un 429 | Backoff con jitter y, **si la respuesta trae cabecera de reintento, esperar el tiempo indicado**. Inferencia cross-Region |
| **`ServiceUnavailable`** | **503** | El servicio está temporalmente saturado. La documentación aclara que **no tiene relación con las cuotas de la cuenta** | Backoff, cambiar de Región, inferencia cross-Region, Provisioned Throughput |

> **Dato decisivo**: **429 es tu cuota, 529 y 503 son la capacidad de AWS.** Pedir un aumento de cuota ante un 529 no arregla nada. Y el 529 es el único de los tres donde la documentación menciona **respetar una cabecera de reintento** si viene en la respuesta, en lugar de aplicar el backoff propio.

La documentación añade un consejo que suele faltar en las implementaciones: **evitar reintentos inmediatos o sincronizados desde varios clientes**, porque aumentan la carga y retrasan la recuperación. Es el argumento del jitter, no solo del backoff.

### Los errores de modelo, y el que se reintenta solo

| Error | Estado | Qué significa |
| --- | --- | --- |
| `ModelErrorException` | **424** | Fallo al procesar el modelo. Trae el **código de estado original** y el nombre del recurso |
| `ModelNotReadyException` | **429** | El modelo no está listo para servir inferencia |
| `ModelTimeoutException` | — | La petición al modelo agotó su tiempo |
| `InternalServerException` | 500 | Error interno |
| `AccessDeniedException` | 403 | Permisos insuficientes |

> **Dato decisivo**: ante `ModelNotReadyException` **el SDK de AWS reintenta automáticamente hasta 5 veces**. Es el único error de Bedrock con un número de reintentos automáticos documentado de forma explícita. La configuración se ajusta con el [comportamiento de reintento de los SDK](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html). Implementar un reintento propio encima sin saberlo multiplica los intentos reales.

> **Gotcha del 429 duplicado**: tanto `ThrottlingException` como `ModelNotReadyException` devuelven **429**. Ramificar la lógica de error solo por el código HTTP los confunde, y sus remedios son opuestos: uno es cuota, el otro es esperar a que el modelo esté disponible. Hay que mirar el tipo de excepción, no el estado.

### Errores de petición mal construida

| Error | Estado | Causa |
| --- | --- | --- |
| `ValidationError` | 400 | La entrada no cumple las restricciones. Revisar parámetros obligatorios, rangos y patrones |
| `RequestEntityTooLargeException` | **413** | La entidad de la petición es demasiado grande |
| `MalformedHttpRequestException` | 400 | El cuerpo no se puede procesar. Suele ser que **no se puede descomprimir con el algoritmo de codificación indicado**: la cabecera de codificación no coincide con la compresión usada |
| `RequestTimeoutException` | 408 | El servidor no recibió la petición completa en el tiempo esperado |
| `RequestAbortedException` | 400 | La petición se abortó antes de responder. Típicamente **el cliente cerró la conexión** |
| `ResourceNotFound` | 404 | Identificador de modelo, endpoint o recurso incorrecto |
| `RequestExpired` | 400 | Timestamps caducados. **Revisar la sincronización del reloj del sistema** |

Dos errores que solo existen en un contexto de GenAI y que sorprenden la primera vez:

| Error | Estado | Causa |
| --- | --- | --- |
| `FTUFormNotFilled` | **404** | **No se han enviado los detalles de caso de uso del modelo** para la cuenta. Hay que rellenar el formulario de caso de uso antes de usar el modelo |
| Fallos de acuerdo de AWS Marketplace | 403 | La suscripción del modelo en Marketplace falló o sigue en curso. Las causas habituales son **pago inválido y geolocalización restringida**, y hay variantes según si han pasado más o menos de 15 minutos |

> **Dato decisivo**: un **404** al invocar un modelo tiene dos causas muy distintas: identificador incorrecto, o **formulario de caso de uso sin rellenar**. Y un **403** puede no ser de IAM: puede ser una suscripción de Marketplace pendiente. Son errores de aprovisionamiento disfrazados de errores de permisos o de recurso.

Para `ResourceNotFound` la documentación recomienda dos cosas concretas: implementar un **mecanismo de fallback** a modelos o endpoints alternativos, y **sincronizar periódicamente el catálogo local de recursos** listando los foundation models disponibles.

### Logging de errores y análisis de respuestas

De [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html). Es la herramienta de análisis de respuesta del skill: recoge **datos completos de petición, de respuesta y metadatos** de las invocaciones de la cuenta en una Región.

Los hechos operativos:

| Aspecto | Detalle |
| --- | --- |
| **Estado inicial** | **Desactivado por defecto.** Una vez activado, los logs se conservan hasta que se borra la configuración de logging |
| **Destinos** | CloudWatch Logs y S3, **solo de la misma cuenta y Región** |
| **Operaciones cubiertas** | `Converse`, `ConverseStream`, `InvokeModel` e `InvokeModelWithResponseStream` |
| **Imágenes y documentos** | Con la Converse API se registran en S3, si se habilitó la entrega y el logging de imágenes en S3 |

> **Dato decisivo de alcance**: el model invocation logging **solo cubre las llamadas del endpoint `bedrock-runtime`**, incluidas las APIs compatibles con OpenAI de ese endpoint. **Las llamadas por otros endpoints, como las mismas APIs en `bedrock-mantle`, no se capturan.** Si el síntoma es "no aparece nada en los logs de invocación", lo primero que hay que comprobar es por qué endpoint va el tráfico.

La validación de peticiones en la capa de API, con API Gateway, y el trazado de llamadas con X-Ray están desarrollados en [Domain 2 · Skill 2.5.1](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#skill-251--interfaces-de-api-para-cargas-genai) y [Domain 2 · Skill 2.4.3](../domain-2/task-2-4-integraciones-api-fm.md#skill-243--sistemas-de-fm-resilientes).

### Un detalle de la respuesta que ayuda a diagnosticar

La respuesta de `InvokeModel` trae dos cabeceras con valores cerrados que dicen cómo se sirvió realmente la petición:

| Cabecera | Valores válidos |
| --- | --- |
| Configuración de latencia | `standard`, `optimized` |
| Nivel de servicio | `priority`, `default`, `flex`, `reserved` |

Comprobarlas resuelve una clase entera de incidencias de rendimiento: la petición pidió latencia optimizada y el servicio la atendió en modo estándar. La inferencia optimizada para latencia se trata en [Domain 4 · Skill 4.2.1](../domain-4/task-4-2-latencia-y-throughput.md#skill-421--sistemas-de-ia-responsivos).

---

## Skill 5.2.3 — Troubleshooting de prompt engineering

> *Resolver problemas de prompt engineering para mejorar la calidad y la consistencia de las respuestas del FM más allá de los ajustes básicos de prompt (por ejemplo, usando frameworks de testing de prompts, comparación de versiones, refinamiento sistemático).*

### La comparación de versiones que AWS sí construyó

De [Compare versions of a prompt in Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-version-compare.html). Es la única herramienta de comparación lado a lado que la plataforma ofrece para artefactos de GenAI, y funciona así:

- Se seleccionan **exactamente dos versiones** de un prompt en la sección de versiones.
- La herramienta muestra **los objetos JSON que definen cada versión, uno al lado del otro**.
- **Resalta los campos que existen en una versión y no en la otra**: un símbolo de suma y resaltado verde para lo que está en una y falta en la otra, y un símbolo de resta con resaltado rojo para el caso inverso.
- Y la parte que convierte la comparación en un test: se rellenan las **variables de test** y se ejecuta el prompt, para **comparar las respuestas del modelo de las distintas versiones**.

> **Dato decisivo**: la comparación **no es un diff de texto del prompt**. Es un diff de la **definición JSON completa** de la versión, lo que incluye la plantilla, las variables, la configuración de inferencia y el modelo. Eso importa porque una regresión de calidad entre dos versiones muchas veces **no está en el texto del prompt** sino en un parámetro de inferencia o en el modelo asociado, y el diff de texto no lo mostraría.

El versionado de prompts se crea según [Create a version of a prompt](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-version-create.html), y el despliegue por versión y alias está en [Domain 1 · Skill 1.6.3](../domain-1/task-1-6-prompt-engineering-governance.md#skill-163--gestión-y-governance-de-prompts).

### Framework de testing de prompts: las piezas reales

| Necesidad | Mecanismo documentado |
| --- | --- |
| Probar una versión con entradas controladas | Variables de test más ejecución del prompt en la consola de Prompt management |
| Comparar dos versiones | La herramienta de comparación, con ejecución de ambas |
| Probar un workflow completo de prompts | [Test a flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-test.html) de Bedrock Flows |
| Congelar una versión probada para producción | [Versiones y alias de flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-deploy.html) |
| Puntuar la calidad de forma sistemática | Job de evaluación con el prompt como parte del dataset |
| Detectar regresión al cambiar el prompt | Comparación antes/después con batch evaluation |

> **Gotcha de refinamiento sistemático**: el refinamiento iterativo del prompt, desarrollado en [Domain 1 · Skill 1.6.5](../domain-1/task-1-6-prompt-engineering-governance.md#skill-165--refinamiento-iterativo-del-prompt), solo es *sistemático* si cada iteración queda como **versión inmutable** y se mide contra el mismo dataset. Iterar sobre el borrador sin versionar hace imposible saber qué cambio mejoró qué, que es exactamente el anti-patrón que AGENTOPS06 describe como datasets y artefactos sin versionar.

La optimización automática de prompts como palanca previa al refinamiento manual está en [Domain 4 · Skill 4.1.1](../domain-4/task-4-1-costes-y-eficiencia-de-recursos.md#skill-411--sistemas-de-eficiencia-de-tokens). El aseguramiento de calidad de prompts con verificación de salida esperada está en [Domain 1 · Skill 1.6.4](../domain-1/task-1-6-prompt-engineering-governance.md#skill-164--aseguramiento-de-calidad-de-prompts).

### Cuando el problema es el prompt del juez, no el del modelo

Un caso de troubleshooting que solo aparece con evaluación automatizada: si los scores de una métrica propia son incoherentes, la causa puede estar en el prompt de la métrica, no en el modelo evaluado. Las dos causas documentadas, desarrolladas en el [Task 5.1 · Skill 5.1.5](./task-5-1-frameworks-y-herramientas.md#skill-515--evaluación-multiperspectiva-rag-juez-y-humanos):

1. **Instrucciones colocadas después de las variables de entrada**, que hacen que el modelo evaluador no evalúe correctamente.
2. **Desajuste entre la rúbrica del prompt y el esquema de salida declarado**.

---

## Skill 5.2.4 — Troubleshooting del sistema de retrieval

> *Resolver problemas del sistema de retrieval para identificar y arreglar lo que afecta a la efectividad de la recuperación de información que augmenta al FM (por ejemplo, usando análisis de relevancia de la respuesta del modelo, diagnóstico de calidad de embeddings, monitorización de drift, resolución de problemas de vectorización, remediación de chunking y preprocesado, optimización del rendimiento de la búsqueda vectorial).*

### El árbol de diagnóstico

El síntoma casi siempre es el mismo: *la respuesta no es relevante*. El primer paso no es tocar el prompt, es **separar retrieval de generación**.

| Paso | Qué hacer | Qué concluye |
| --- | --- | --- |
| **1** | Job de RAG evaluation **retrieve only** sobre el dataset | Si `Builtin.ContextRelevance` es alto, lo recuperado sirve y el problema está en la generación |
| **2** | Si `Builtin.ContextRelevance` es bajo, el problema está en el retrieval | Seguir bajando |
| **3** | Comprobar si los documentos están **indexados**: estado del ingestion job y del sync | Si no están, no es un problema de relevancia |
| **4** | Comprobar **chunking**: tamaño, solape, estrategia | Chunks demasiado grandes diluyen, demasiado pequeños pierden contexto |
| **5** | Comprobar **embeddings**: modelo y dimensionalidad del índice | Un desajuste de dimensión impide la indexación |
| **6** | Comprobar **filtros de metadatos** | Un filtro que no matchea devuelve cero resultados sin error |
| **7** | Comprobar **parámetros de consulta**: `k` y `size` | Ver el Task 5.1 · Skill 5.1.6 |

### Sync e ingestion: qué falla y por qué

De [Sync your data with your Amazon Bedrock knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html). Las condiciones previas que la página exige antes de ingestar, y que son la checklist de diagnóstico:

- Conexión del data source configurada, con su [conector](https://docs.aws.amazon.com/bedrock/latest/userguide/data-source-connectors.html).
- Modelo de embeddings y vector store configurados, entre los [soportados](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html).
- Ficheros en **formatos soportados**.
- Ficheros que **no excedan el tamaño de fichero de ingestion job** de las cuotas del servicio.

El comportamiento del resync, que explica muchos síntomas:

| Escenario | Qué ocurre |
| --- | --- |
| Sin cambios detectados | El documento **se omite** |
| Contenido o metadatos cambiados | El documento **se reingesta**: se re-parsea, se re-trocea, se re-embebe y se re-indexa |
| Documento nuevo | Solo se ingesta el nuevo |
| Documento borrado | Se elimina del vector store |

> **Dato decisivo**: el sync es **incremental**. Bedrock solo procesa lo añadido, modificado o borrado desde el último sync. Eso significa que **un cambio de estrategia de chunking no se aplica a los documentos que no cambiaron**: siguen troceados como estaban. Si el remedio del diagnóstico es "cambiar el chunking", hay que forzar la reingesta, no solo lanzar un sync.

Hay además una **optimización de solo metadatos**: en ciertos casos Bedrock actualiza los metadatos sin reingestar el documento, recuperando los embeddings existentes del vector store, fusionando los metadatos nuevos y volviéndolos a escribir, lo que evita llamadas al modelo de embeddings.

> **Gotcha de metadatos que se ignoran en silencio**: para que los ficheros de metadatos no se descarten hacen falta dos cosas. Primero, que cada fichero de metadatos **comparta nombre y extensión** con el fichero fuente al que acompaña. Segundo, y este es el que sorprende: si el índice vectorial está en OpenSearch Serverless, **tiene que estar configurado con el motor `faiss`**. Con el motor `nmslib` los ficheros de metadatos se ignoran, y la única salida documentada es **crear un índice nuevo con `faiss` y una knowledge base nueva**: no se puede cambiar en sitio.

Para Aurora, la recomendación es usar el **campo de metadatos personalizado** para guardar todos los metadatos en una sola columna e indexarla. Si no se usa, **la tabla del índice debe tener una columna por cada propiedad de metadatos** antes de empezar la ingesta.

### Remediación de chunking y preprocesado

Las palancas están en la tabla de estrategias del [Skill 5.2.1](#skill-521--manejo-de-contenido-contexto-y-truncamiento). El mapa síntoma a remedio:

| Síntoma | Remedio de chunking |
| --- | --- |
| Los chunks recuperados traen mucho ruido junto a la respuesta | Chunks más pequeños, o **semantic chunking** para respetar límites de significado |
| La respuesta correcta está partida entre dos chunks | Subir el **solape**, o pasar a **jerárquico** |
| El modelo no tiene contexto suficiente aunque el chunk es relevante | **Jerárquico**: los hijos localizan, los padres contextualizan |
| Se recuperan menos resultados de los pedidos | Comportamiento esperado del **jerárquico** |
| Las citas no traen número de página | Se eligió **no chunking**, que pierde ese metadato |
| Chunks jerárquicos que fallan por tamaño de metadatos | Bajar los tokens combinados por debajo de unos 8.000, o cambiar de vector store |

### Rendimiento de la búsqueda vectorial

De [k-NN search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html). Para usar k-NN hay que crear el índice con el ajuste de k-NN activado y añadir campos de tipo vectorial, con el parámetro de dimensión obligatorio. Los límites: hasta **10.000 floats** por vector y un `k` máximo de **10.000**.

> **Gotcha de resultados infladps**: hay que fijar **`size`** además de `k`. Si no, se obtienen `k` resultados **por shard y por segmento** en lugar de `k` para la consulta completa. Y al mezclar la consulta vectorial con otras cláusulas se pueden recibir **menos** resultados de los pedidos.

La documentación de OpenSearch Service advierte de que solo ofrece una visión general del plugin y que el **tuning de rendimiento y los ajustes de clúster específicos de k-NN están en la documentación open source de OpenSearch**, no en el portal de AWS. Es una limitación de alcance útil de conocer: si la pregunta pide parámetros finos de HNSW o de cuantización, la respuesta no está en `docs.aws.amazon.com`.

Las métricas de CloudWatch del dominio de OpenSearch, la optimización de índices y la validación de calidad de datos del vector store están en [Domain 4 · Skill 4.3.5](../domain-4/task-4-3-herramientas-vector-stores-y-fallos.md#skill-435--gestión-operativa-del-vector-store). La optimización de rendimiento del retrieval y la búsqueda híbrida están en [Domain 4 · Skill 4.2.2](../domain-4/task-4-2-retrieval-y-parametros.md#skill-422--rendimiento-del-retrieval) y [Domain 1 · Skill 1.5.4](../domain-1/task-1-5-retrieval.md#skill-154--arquitecturas-de-búsqueda-avanzada).

### Calidad de embeddings y drift

> **Discrepancia**: el skill pide *embedding quality diagnostics* y *drift monitoring*. **AWS no documenta ninguna herramienta de diagnóstico de calidad de embeddings ni de detección de drift de embeddings.**

Lo que sí hay, y es la respuesta con respaldo:

| Necesidad | Mecanismo real |
| --- | --- |
| **Calidad de embeddings** | Se mide **indirectamente**, por el efecto: `Builtin.ContextRelevance` de un job retrieve-only. Si la relevancia contextual es baja con chunking correcto y documentos indexados, el candidato es el modelo de embeddings |
| **Comparar modelos de embedding** | Ejecutar el mismo job retrieve-only sobre dos knowledge bases que difieran solo en el modelo de embeddings |
| **Drift** | Reejecución periódica del mismo job sobre el mismo dataset, y comparación de scores. No hay detector de drift |
| **Problemas de vectorización** | Fallos de ingestion job, desajuste de dimensionalidad y metadatos ignorados, arriba |

La selección y configuración de modelos de embedding está en [Domain 1 · Skill 1.5.2](../domain-1/task-1-5-retrieval.md#skill-152--selección-y-configuración-de-embeddings).

---

## Skill 5.2.5 — Mantenimiento y observabilidad de prompts

> *Resolver problemas de mantenimiento de prompts para mejorar continuamente el rendimiento de las interacciones con el FM (por ejemplo, usando testing de plantillas y CloudWatch Logs para diagnosticar confusión de prompt, X-Ray para implementar pipelines de observabilidad de prompt, validación de esquema para detectar inconsistencias de formato, workflows de refinamiento sistemático de prompts).*

### Validación de esquema: el mecanismo que elimina el problema

De [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html). Es el remedio de raíz a las inconsistencias de formato, y el argumento que AWS da es directo: elimina las tasas de error y los bucles de reintento de los enfoques basados en prompt, y quita la necesidad de lógica propia de parseo y validación.

Dos mecanismos, combinables en la misma petición:

| Mecanismo | Cómo se activa |
| --- | --- |
| **Formato de salida por JSON Schema** | Un campo de formato de salida en la petición. Varía según API y familia de modelo: hay un campo para la Converse API, otro para `InvokeModel` con modelos Claude y otro para modelos de pesos abiertos |
| **Strict tool use** | El flag `strict` a `true` en la definición de la herramienta, que activa validación de esquema sobre **nombres y entradas** de herramienta |

El flujo de proceso tiene un detalle de rendimiento que importa:

| Paso | Qué ocurre |
| --- | --- |
| 1 | Se envía el esquema o la herramienta con validación estricta |
| 2 | Bedrock valida el esquema contra el subconjunto soportado de JSON Schema Draft 2020-12. **Si usa funcionalidades no soportadas, devuelve 400 de inmediato** |
| 3 | Para esquemas nuevos, Bedrock **compila la gramática, lo que puede tardar unos minutos** |
| 4 | Las gramáticas compiladas se **cachean 24 horas desde el primer acceso**, cifradas con claves gestionadas por AWS |
| 5 | Las peticiones siguientes con el mismo esquema y cuenta usan la caché, con latencia comparable a una petición normal |

> **Dato decisivo de rendimiento**: **la primera petición con un esquema nuevo puede tardar minutos** mientras se compila la gramática, y la caché dura **24 horas**. Un esquema que se usa una vez al día puede pagar la compilación cada vez. Si el síntoma es "la primera llamada del día es lentísima", esta es la causa.

Las funcionalidades soportadas y no soportadas, que son la causa habitual de un 400:

| Soportado | No soportado |
| --- | --- |
| Todos los tipos básicos: objeto, array, string, integer, number, boolean, null | **Esquemas recursivos** |
| `enum` (solo strings, números, booleanos o nulos), `const`, `anyOf`, `allOf` con limitaciones | **Referencias `$ref` externas** |
| `$ref`, `$def` y `definitions`, **solo referencias internas** | **Restricciones numéricas**: `minimum`, `maximum`, `multipleOf` |
| Formatos de string: `date-time`, `time`, `date`, `duration`, `email`, `hostname`, `uri`, `ipv4`, `ipv6`, `uuid` | **Restricciones de string**: `minLength`, `maxLength` |
| `minItems` de array, **solo con valores 0 y 1** | `additionalProperties` con cualquier valor distinto de `false` |

> **Gotcha que rompe esquemas reales**: `minLength`, `maxLength`, `minimum` y `maximum` **no están soportados**. Un esquema tomado de una API existente y pegado en una petición de Bedrock casi siempre los lleva, y provoca un 400 en la validación del esquema, no un fallo de generación. Y `minItems` solo admite 0 o 1: cualquier otro valor no vale.

Las salidas estructuradas funcionan en Converse, ConverseStream, `InvokeModel` e `InvokeModelWithResponseStream`, y también con inferencia cross-Region y batch inference sin configuración adicional. Dos incompatibilidades explícitas:

- La API de Anthropic Messages en el endpoint `bedrock-mantle` **rechaza el parámetro de formato con un 400**. Para usar salidas estructuradas con modelos Claude hay que ir por la Converse API o por `InvokeModel` en `bedrock-runtime`.
- Las salidas estructuradas son **incompatibles con las citations** de los modelos Anthropic: activar las dos cosas devuelve un 400.

> **Dato decisivo para una arquitectura RAG**: esa segunda incompatibilidad obliga a elegir entre **respuesta con esquema garantizado** y **respuesta con citas**. En un sistema que necesita atribución de fuente verificable, imponer el esquema por salida estructurada no es una opción con esos modelos, y la validación hay que hacerla en post-procesado.

El uso de JSON Schema como control de determinismo en la salida está en [Domain 3 · Skill 3.1.3](../domain-3/task-3-1-controles-de-seguridad-entrada-salida.md#skill-313--verificación-de-exactitud-y-reducción-de-hallucinations).

### Las dos razones de parada que delatan un problema de formato

Conectando con el [Skill 5.2.1](#skill-521--manejo-de-contenido-contexto-y-truncamiento): `stopReason` con valor `malformed_model_output` o `malformed_tool_use` es la señal, en tiempo de ejecución, de que el modelo produjo algo que no encaja con el formato esperado. Son los dos valores que justifican activar validación de esquema o tool use estricto.

### Diagnosticar la confusión de prompt con logs

La pieza específica que el skill nombra es CloudWatch Logs. Tres mecanismos, de menos a más elaborado:

| Mecanismo | Qué aporta |
| --- | --- |
| **Model invocation logging** | El prompt y la respuesta completos, para ver qué recibió el modelo de verdad |
| **CloudWatch Logs Insights** | Consultas sobre esos logs. Desarrollado en [Domain 2 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#skill-256--troubleshooting-de-aplicaciones-de-fm) |
| [**Anomaly detection de Logs**](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/LogsAnomalyDetection.html) | Detección de patrones nuevos o desviados en los logs, sin definir la consulta por adelantado |

La detección de anomalías en logs tiene además [métricas propias](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/LogsAnomalyDetection-Metrics.html) y una [sintaxis de consulta específica para anomalías](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax-Anomaly.html) en Logs Insights.

> **Dato decisivo sobre la confusión de prompt**: no hay ninguna funcionalidad de AWS que se llame *prompt confusion detection*. Lo que hay es la capacidad de **ver el prompt exacto que llegó al modelo** con el model invocation logging, y compararlo con el que se creía enviar. En un sistema con plantillas, variables, contexto recuperado y prompt de sistema, esa diferencia es la causa real de la mayoría de las respuestas inexplicables.

### Pipeline de observabilidad de prompt con X-Ray

De los [conceptos de X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/xray-concepts.html) y los [documentos de segmento](https://docs.aws.amazon.com/xray/latest/devguide/xray-api-segmentdocuments.html). La pieza que convierte un trace en un pipeline de observabilidad de prompt es la distinción entre dos campos:

| Campo del segmento | Naturaleza | Uso |
| --- | --- | --- |
| **Annotations** | Pares clave-valor **indexados** | Se pueden usar en expresiones de filtro para **buscar traces**. Aquí van la versión de prompt, el identificador de plantilla, el modelo |
| **Metadata** | Pares clave-valor **no indexados** | No se pueden filtrar, pero admiten cualquier valor. Aquí van los datos voluminosos |

> **Dato decisivo**: **solo las annotations son buscables.** Un pipeline de observabilidad de prompt útil anota la **versión del prompt** y el **alias** como annotation, para poder filtrar todos los traces de una versión concreta y comparar su comportamiento con la anterior. Guardarlo como metadata lo hace visible en un trace individual pero **inutilizable para buscar**, que es justo lo que hace falta al diagnosticar una regresión de versión.

El trazado de llamadas a la API de FM con X-Ray está en [Domain 2 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#skill-256--troubleshooting-de-aplicaciones-de-fm). La observabilidad de interacción con el FM y el tracing de rendimiento están en [Domain 4 · Skill 4.3.1](../domain-4/task-4-3-observabilidad-y-metricas.md#skill-431--observabilidad-holística).

### Workflow de refinamiento sistemático

Juntando las piezas del task, el ciclo que la documentación soporta de punta a punta:

| Paso | Mecanismo |
| --- | --- |
| **1. Observar** | Model invocation logging para ver el prompt real, más anomaly detection de logs |
| **2. Localizar** | Traces de X-Ray filtrados por la annotation de versión de prompt |
| **3. Hipótesis** | Comparación de versiones en Prompt management, que incluye parámetros de inferencia y modelo |
| **4. Probar** | Variables de test más ejecución del prompt, y test de flow si es un workflow |
| **5. Medir** | Job de evaluación, o batch evaluation para comparar antes y después |
| **6. Congelar** | Nueva versión de prompt, con alias apuntando a ella |
| **7. Vigilar** | Evaluación online con umbral y alarma |

> **Gotcha del ciclo completo**: el paso 6 es el que casi siempre se omite, y sin él los pasos 3 y 5 dejan de ser posibles en la siguiente iteración. Sin versión inmutable no hay diff, y sin diff no hay diagnóstico de regresión. Es la misma conclusión que AGENTOPS06 expresa como artefactos de evaluación versionados.

---

## Resumen operativo: diagnóstico por síntoma

| Síntoma | Causa y dónde mirar |
| --- | --- |
| La respuesta se corta a media frase | `stopReason` igual a `max_tokens`. **Truncamiento**, no error |
| El prompt parece ignorar parte del contexto | `stopReason` igual a `model_context_window_exceeded`. **Desbordamiento**, con HTTP 200 |
| El modelo devuelve JSON roto | `stopReason` `malformed_model_output`. Remedio: **salida estructurada** |
| La llamada a herramienta viene mal formada | `stopReason` `malformed_tool_use`. Remedio: **`strict` a `true`** en la herramienta |
| Me throttlean antes de lo que sugiere la factura | **Burndown de tokens de salida** más `max_tokens` descontado al inicio. Bajar `max_tokens` |
| 429 | **Cuota de la cuenta** (`ThrottlingException`) **o** modelo no listo (`ModelNotReadyException`). Mirar el tipo, no el estado |
| 529 | **Capacidad del modelo**, no cuota. Respetar la cabecera de reintento si viene |
| 503 | Capacidad del servicio. No tiene relación con la cuota |
| 424 | `ModelErrorException`, con el estado original dentro |
| 413 | Payload demasiado grande. El cuerpo admite hasta 25 millones de caracteres |
| 404 al invocar un modelo | Identificador incorrecto **o formulario de caso de uso sin rellenar** |
| 403 que no es de IAM | Acuerdo de **AWS Marketplace** fallido o pendiente |
| 400 con cuerpo aparentemente válido | Codificación de contenido que no coincide con la compresión usada |
| No aparece nada en los logs de invocación | Está **desactivado por defecto**, o el tráfico no va por `bedrock-runtime` |
| 400 al declarar un esquema de salida | `minLength`, `maxLength`, `minimum`, `maximum` o recursión: **no soportados** |
| La primera llamada del día tarda minutos | **Compilación de gramática** del esquema. Caché de 24 horas |
| Esquema y citas juntos dan 400 | **Incompatibilidad documentada** entre salidas estructuradas y citations |
| Los ficheros de metadatos se ignoran | Nombre distinto del fuente, o motor `nmslib` en OpenSearch Serverless en lugar de `faiss` |
| Cambié el chunking y no cambió nada | El sync es **incremental**: hay que forzar la reingesta |
| Se recuperan menos chunks de los pedidos | **Chunking jerárquico**, o consulta vectorial mezclada con otras cláusulas |
| Las citas no traen número de página | Se eligió **no chunking** |
| La precisión de retrieval medida no cuadra | Falta fijar **`size`** junto a `k` |
| La respuesta no es relevante | Job **retrieve only** primero, para separar retrieval de generación |
| Necesito comparar dos versiones de prompt | Herramienta de comparación: diff del **JSON completo**, no del texto |
| Quiero buscar todos los traces de una versión de prompt | **Annotation** de X-Ray, no metadata |
| Detectar drift de embeddings | **No existe.** Reejecutar el mismo job y comparar scores |
