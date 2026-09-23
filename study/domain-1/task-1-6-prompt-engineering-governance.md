# Task 1.6 — Prompt engineering y governance de interacciones con FMs

[← Volver al índice](./README.md)

Skills cubiertos: **1.6.1**, **1.6.2**, **1.6.3**, **1.6.4**, **1.6.5**, **1.6.6**.

---

## Skill 1.6.1 — Frameworks de instrucción del modelo

> *Crear frameworks efectivos de instrucción de modelo para controlar el comportamiento y las salidas del FM (por ejemplo, Amazon Bedrock Prompt Management para imponer definiciones de rol, Amazon Bedrock Guardrails para imponer guías de IA responsable, configuraciones de plantilla para formatear respuestas).*

### Componentes de un prompt

De [Prompt engineering concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html). *Prompt engineering* es la práctica de optimizar la entrada textual a un LLM para obtener las respuestas deseadas. La calidad del prompt impacta directamente en la calidad de la respuesta.

Un prompt combina uno o más de estos componentes, según el caso de uso, la disponibilidad de datos y la tarea:

| Componente | Función |
| --- | --- |
| **Task / instruction** | Lo que quieres que el LLM haga. Le dice **qué** hacer |
| **Context** | Descripción del dominio relevante. Aporta información y keywords que guían al modelo a usar la entrada al formular la salida |
| **Demonstration examples** | Ejemplos de entrada y salida deseada |
| **Input text** | El texto sobre el que el LLM opera |

En el ejemplo oficial de resumen de una reseña, tanto la instrucción (*resume la reseña en una frase*) como el texto de entrada eran necesarios: sin uno de los dos el modelo no tendría información suficiente.

### Zero-shot vs few-shot

**Few-shot prompting** (también llamado *in-context learning*) consiste en aportar algunos ejemplos para calibrar la salida. Un *shot* corresponde a un par ejemplo-entrada / salida-deseada.

Con modelos **Anthropic Claude**, la documentación recomienda:

- Usar etiquetas `<example></example>` para incluir los ejemplos de demostración.
- Usar delimitadores distintos dentro de los ejemplos, como `H:` y `A:`, para evitar confusión con los delimitadores `Human:` y `Assistant:` del prompt completo.
- En el último ejemplo few-shot, **omitir el `A:` final** en favor de `Assistant:`, para que Claude genere la respuesta.

### Plantillas de prompt

Una plantilla especifica el formato del prompt con contenido intercambiable: son "recetas" para clasificación, resumen, question answering y otros casos. Puede incluir instrucciones, ejemplos few-shot, contexto y preguntas específicas del caso de uso.

```
"""Tell me the sentiment of the following
{{Text Type, e.g., "restaurant review"}} and categorize it
as either {{Sentiment A}} or {{Sentiment B}}.
Here are some examples:

Text: {{Example Input 1}}
Answer: {{Sentiment A}}

Text: {{Example Input 2}}
Answer: {{Sentiment B}}

Text: {{Input}}
Answer:"""
```

> Las dobles llaves `{{ }}` marcan los huecos donde va la información específica y **no deben incluirse en el texto del prompt**.

### Guías de prompting por proveedor

La documentación enlaza guías específicas por familia de modelo, porque cada una tiene características propias:

| Modelo | Guía oficial |
| --- | --- |
| Amazon Nova Micro, Lite, Pro | [Prompting best practices for Amazon Nova understanding models](https://docs.aws.amazon.com/nova/latest/userguide/prompting.html) |
| Amazon Nova Canvas | [Generating images with Amazon Nova](https://docs.aws.amazon.com/nova/latest/userguide/image-generation.html) |
| Amazon Nova Reel | [Generating videos with Amazon Nova](https://docs.aws.amazon.com/nova/latest/userguide/video-generation.html) |
| Anthropic Claude | [Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) |
| Cohere, AI21, Meta, Mistral, Stability AI | Enlazadas en [Prompt engineering concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html) |

### Reducir alucinaciones

La nota oficial señala tres vías: refinar el prompt con técnicas de optimización, usar técnicas como **RAG** para dar al modelo acceso a datos más relevantes, o **usar un modelo distinto** que produzca mejores resultados.

### Amazon Bedrock Guardrails

De [Detect and filter harmful content by using Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html). Ofrece salvaguardas configurables con controles de seguridad y privacidad sobre distintos FMs, para detectar y filtrar contenido no deseado y proteger información sensible presente en entradas de usuario o respuestas del modelo (**excluyendo bloques de contenido de razonamiento**).

**Los seis tipos de salvaguarda**

| Salvaguarda | Qué hace |
| --- | --- |
| **Content filters** | Detecta y filtra texto o imágenes dañinas en prompts o respuestas, según categorías predefinidas: **Hate, Insults, Sexual, Violence, Misconduct y Prompt Attack**. La fuerza del filtro es configurable por categoría. Disponible en tiers Classic y Standard; con **Standard** la detección se extiende a contenido dañino dentro de elementos de código: comentarios, nombres de variables y funciones, y literales de cadena |
| **Denied topics** | Conjunto de temas no deseados en el contexto de tu aplicación; se bloquean si se detectan en consultas o respuestas. Con **Standard tier**, también dentro de elementos de código |
| **Word filters** | Palabras o frases personalizadas (**coincidencia exacta**) a bloquear. Incluye una opción lista para usar contra profanidad, y permite palabras propias como nombres de competidores |
| **Sensitive information filters** | Bloquea o enmascara información sensible como PII en entradas y respuestas. Detección **probabilística** de entidades (SSN, fecha de nacimiento, dirección, etc.) y detección de patrones mediante **expresiones regulares personalizadas** |
| **Contextual grounding checks** | Detecta alucinaciones: respuestas no fundamentadas en la fuente (factualmente inexactas o que añaden información nueva) o irrelevantes respecto a la consulta del usuario. Permite bloquear o marcar respuestas en aplicaciones **RAG** cuando se desvían de la fuente recuperada o no responden la pregunta |
| **Automated Reasoning checks** | Valida la precisión de las respuestas contra un conjunto de **reglas lógicas**. Detecta alucinaciones, **sugiere correcciones** y resalta **supuestos no declarados** |

Además de los filtros, se configuran los **mensajes a devolver al usuario** cuando una entrada o respuesta viola el guardrail.

**Ciclo de vida del guardrail**: al crearlo queda disponible un **working draft** para modificar iterativamente. Se experimenta con configuraciones usando la **ventana de test integrada** y, cuando el resultado satisface, se crea una **versión** del guardrail para usarla con los FMs soportados.

**Dos formas de aplicarlo**

| Forma | Cómo |
| --- | --- |
| Durante la invocación | Especificando el **guardrail ID y la versión** en la llamada de inferencia |
| Independiente del modelo | Con la API **`ApplyGuardrail`**, sin invocar ningún FM |

**Evaluación selectiva del prompt**: en aplicaciones RAG o conversacionales puede interesar evaluar **solo la entrada del usuario**, descartando instrucciones de sistema, resultados de búsqueda, histórico de conversación o ejemplos few-shot. Eso se hace con [Apply tags to user input to filter content](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html). Esta capacidad **está disponible solo por SDK**, no en la consola de gestión, ni en el Bedrock Playground, ni en la consola de Guardrails.

Documentación relacionada: [tiers](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tiers.html), [idiomas soportados](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-supported-languages.html), [distribución cross-Region](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region.html), [enforcements cross-account](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-enforcements.html).

### Framework de instrucción completo

```
Capa 1 · Identidad y rol       → system prompt en Prompt management (versionado)
Capa 2 · Formato de salida     → plantilla + structured output / tool schema
Capa 3 · Ejemplos              → few-shot en la plantilla, con <example> en Claude
Capa 4 · Contexto              → RAG: $search_results$ de la knowledge base
Capa 5 · Restricciones blandas → instrucciones de qué no hacer, en el prompt
Capa 6 · Restricciones duras   → Bedrock Guardrails (versionado, aplicable por SDK o ApplyGuardrail)
```

Las capas 1 a 5 son instrucciones que el modelo **puede** ignorar; la capa 6 es **imposición externa** al modelo. Esa distinción es la clave del skill: las guías de IA responsable no se implementan solo con prompts.

---

## Skill 1.6.2 — Sistemas interactivos que mantienen contexto

> *Construir sistemas de IA interactivos para mantener contexto y mejorar las interacciones del usuario con FMs (por ejemplo, AWS Step Functions para workflows de clarificación, Amazon Comprehend para reconocimiento de intención, Amazon DynamoDB para almacenamiento de histórico de conversación).*

### El modelo no tiene memoria

De [Prompt engineering concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html): al acceder a los modelos de Bedrock por llamadas de API, **los modelos no recuerdan prompts ni peticiones anteriores** salvo que la interacción previa se incluya en el prompt actual. Incluir los prompts previos es lo que permite interacciones de estilo conversacional y peticiones de seguimiento.

### Gestión de turnos con la Converse API

De [Inference using Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html): el contexto conversacional se mantiene **incluyendo todos los mensajes de la conversación en las peticiones `Converse` siguientes**, y usando el campo `role` para indicar si el mensaje es del usuario (`user`) o del modelo (`assistant`).

```json
{
  "messages": [
    { "role": "user",      "content": [{ "text": "¿Cuál es la política de devoluciones?" }] },
    { "role": "assistant", "content": [{ "text": "30 días desde la compra..." }] },
    { "role": "user",      "content": [{ "text": "¿Y si el producto está abierto?" }] }
  ]
}
```

Amazon Bedrock **no almacena** el texto, imágenes ni documentos enviados como contenido: la persistencia del histórico es responsabilidad de tu aplicación.

### DynamoDB como almacén de histórico

| Aspecto de diseño | Recomendación |
| --- | --- |
| Clave de partición | `conversationId` o `sessionId` |
| Clave de ordenación | `timestamp` o número de turno, para recuperar los turnos en orden |
| Atributos | `role`, `content`, `modelId` usado, tokens consumidos, `guardrailAction` aplicada |
| Caducidad | **TTL** de DynamoDB para expirar conversaciones automáticamente: retención por política, no por proceso manual |
| Ventana de contexto | Recuperar solo los **últimos N turnos** o un resumen acumulado, para no exceder el context window |
| Resumen incremental | Cuando el histórico crece, resumir los turnos antiguos con un modelo económico y conservar los recientes literales |
| Cambios reactivos | **DynamoDB Streams** para disparar analítica, alertas o actualización de perfil de usuario |
| Cifrado | Cifrado en reposo con KMS; el histórico puede contener PII |

### Reconocimiento de intención

| Servicio | Qué aporta |
| --- | --- |
| **Amazon Comprehend** | **Custom classification** entrenada con tus categorías de intención; y para extraer los datos de la petición, **custom entity recognition**. También idioma dominante, sentimiento y detección de PII sobre el turno. Ver [Amazon Comprehend Custom](https://docs.aws.amazon.com/comprehend/latest/dg/concepts-custom.html) |
| **Amazon Lex** | Servicio de interfaces conversacionales con intents y slots; se integra como **nodo Lex** en un flow de Bedrock |
| **Tool use de Bedrock** | El propio FM decide qué herramienta invocar; el "reconocimiento de intención" queda implícito en la elección de herramienta |

Los **flywheels** de Comprehend ([doc](https://docs.aws.amazon.com/comprehend/latest/dg/flywheels.html)) permiten reentrenar y versionar el clasificador de intención a medida que aparecen nuevos tipos de petición.

### Workflows de clarificación con Step Functions

Cuando la petición es ambigua o falta información, el patrón es preguntar antes de responder. Este es también un caso de la best practice [GENREL03-BP01](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel03-bp01.html), que recomienda implementar lógica que compruebe si el prompt contiene la información esperada.

```
Mensaje del usuario
   │
   ▼
Step Functions
   ├─ Lambda: cargar histórico de DynamoDB
   ├─ Lambda / Comprehend: detectar intención y slots presentes
   ├─ Choice: ¿faltan datos obligatorios?
   │     sí ──► Lambda: generar pregunta de clarificación
   │            └─ Task con waitForTaskToken: esperar la respuesta del usuario
   │               └─ vuelta al Choice
   │     no ──► Retrieve / Converse con el contexto completo
   ├─ Lambda: persistir el turno en DynamoDB
   └─ Choice: ¿el guardrail bloqueó? ──► mensaje configurado, no error genérico
```

El patrón `waitForTaskToken` es lo que permite pausar la máquina de estados hasta que llega la respuesta del usuario, manteniendo el estado de la conversación en la propia ejecución.

### Conversación multi-turno en flows

Bedrock Flows soporta interacción conversacional: ver [Converse with an Amazon Bedrock flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-multi-turn-invocation.html). Permite que el flow solicite información adicional al usuario en medio de la ejecución, sin construir la máquina de estados manualmente.

### Consistencia de contexto en RAG conversacional

Dos elementos oficiales ayudan aquí:

- El placeholder **`$current_time$`** en las plantillas de orquestación y generación, para que el modelo sepa la hora actual.
- **Query decomposition** y el prompt de orquestación personalizado, para resolver referencias anafóricas ("¿y si está abierto?") reescribiendo la consulta con el contexto del turno anterior antes de buscar. Ver [Task 1.5 · Skill 1.5.5](./task-1-5-retrieval.md#skill-155--manejo-sofisticado-de-consultas).

---

## Skill 1.6.3 — Gestión y governance de prompts

> *Implementar sistemas completos de gestión y governance de prompts para asegurar consistencia y supervisión de las operaciones de FM (por ejemplo, Amazon Bedrock Prompt Management para crear plantillas parametrizadas y flujos de aprobación, Amazon S3 para almacenar repositorios de plantillas, AWS CloudTrail para rastrear uso, Amazon CloudWatch Logs para registrar acceso).*

### Bedrock Prompt Management

De [Construct and store reusable prompts with Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html). Permite crear, editar y guardar prompts propios para aplicar el mismo prompt a distintos workflows.

**Definiciones clave**

| Término | Definición |
| --- | --- |
| **Prompt** | Entrada que se da al modelo para guiarlo a generar una respuesta o salida apropiada |
| **Variable** | Placeholder incluido en el prompt. Sus valores se aportan al probar el prompt o al invocar el modelo en tiempo de ejecución |
| **Prompt variant** | Configuración alternativa del prompt: su mensaje, el modelo, o las configuraciones de inferencia. Se crean variantes, se prueban y se guarda la elegida |
| **Prompt builder** | Herramienta de la consola de Bedrock para crear, editar y probar prompts y sus variantes en una interfaz visual |

**Workflow oficial**

1. Crear el prompt para reutilizarlo entre casos de uso, **incluyendo variables** para dar flexibilidad.
2. Elegir un **modelo, inference profile o agent** para ejecutar la inferencia y ajustar las configuraciones de inferencia.
3. Rellenar valores de prueba para las variables y ejecutar. Crear **variantes** y comparar salidas para elegir la mejor.
4. Integrar el prompt en la aplicación de una de estas dos formas:
   - Especificar el prompt al [ejecutar inferencia](https://docs.aws.amazon.com/bedrock/latest/userguide/inference.html).
   - Añadir un **prompt node** a un [flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html) y especificar el prompt.

**Versionado y despliegue**: mientras iteras puedes **guardar versiones** del prompt. El despliegue a la aplicación se hace mediante versiones: ver [Deploy a prompt to your application using versions](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-deploy.html).

**Optimización asistida**: [Optimize a prompt](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-optimize.html) reescribe el prompt para el modelo destino.

> **Restricciones al usar un prompt gestionado con `Converse`**: no puedes incluir `additionalModelRequestFields`, `inferenceConfig`, `system` ni `toolConfig`. Si incluyes `messages`, esos mensajes se **añaden después** de los del prompt. Si incluyes `guardrailConfig`, el guardrail se aplica a todo el prompt; con bloques `guardContent` se aplica solo a esos bloques.

### Governance: el pilar de Reliability

El Generative AI Lens dedica el área de foco [GENREL04 Prompt management](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel04.html) a establecer **control de versiones y procesos de gestión de cambios** para los prompts, con el objetivo de crear consistencia y fiabilidad en las interacciones con el modelo. Y el principio *standardize resource management through catalogs* del pilar de [Reliability](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/reliability.html) justifica mantener catálogos centralizados de prompts y modelos como única fuente de verdad, con versionado y capacidad de rollback.

### Flujo de aprobación de prompts

Prompt Management aporta las versiones; el flujo de aprobación se construye alrededor:

```
Autor edita el prompt en el prompt builder
   │
   ▼
Prueba variantes, compara salidas
   │
   ▼
Guarda una VERSIÓN (inmutable)
   │
   ▼
Pipeline de QA: Lambda + Step Functions ejecutan el set de regresión (Skill 1.6.4)
   │
   ├─ falla ──► no se promueve, se notifica por SNS
   │
   ▼ pasa
Aprobación (manual o automatizada) ──► AppConfig publica la versión activa
   │                                     · validators verifican la configuración
   │                                     · deployment strategy gradual
   │                                     · rollback automático por alarma CloudWatch
   ▼
Aplicación lee la versión activa desde AppConfig y la usa en Converse
```

Repositorio de plantillas en **Amazon S3**: versionado de bucket activado, y el prompt como artefacto de código revisado por pull request antes de subirse. Es el mecanismo que el skill menciona explícitamente.

### Auditoría y observabilidad

| Necesidad | Mecanismo |
| --- | --- |
| **Quién creó, modificó o borró** un prompt, guardrail o knowledge base | **AWS CloudTrail**: eventos de management de las APIs de Bedrock |
| **Qué se envió y qué se recibió** en cada invocación | [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) |
| **Uso y métricas por aplicación** | **Application inference profiles** con CloudWatch Logs |
| **Coste por aplicación, equipo o entorno** | **Tags** en application inference profiles, con [cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html) |
| **Región real de procesamiento** en cross-Region inference | Campo `additionalEventData.inferenceRegion` en CloudTrail |
| **Metadatos filtrables** en los invocation logs | Campo `requestMetadata` de la petición `Converse` |
| **Eventos de management de jobs de evaluación** | [CloudTrail management events in model evaluation jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/cloudtrail-events-in-model-evaluations.html) |
| **Trazas de un flow** | Traceability de Bedrock Flows |
| **Observabilidad de knowledge base gestionada** | [Observability for managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-observability.html) |

El campo `requestMetadata` merece atención: permite etiquetar cada invocación con metadatos de negocio (tenant, caso de uso, versión de prompt) **filtrables después en los logs de invocación**, lo que convierte el log en una herramienta de análisis por dimensión, no solo en un registro.

### Controles de acceso

| Control | Aplicación |
| --- | --- |
| **IAM** | Permisos granulares: `bedrock:InvokeModel`, `bedrock:Retrieve`, acceso por prompt, guardrail o knowledge base |
| **KMS** | Cifrado de recursos de knowledge base, buckets de plantillas, tablas de histórico |
| **Secrets Manager** | Credenciales de Aurora y de sistemas externos |
| **Guardrails enforcements** | [Salvaguardas cross-account](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-enforcements.html) para imponer guardrails desde una cuenta de governance |
| **SCPs** | Restringir Regiones de procesamiento; recordar el requisito `"aws:RequestedRegion": "unspecified"` para cross-Region inference global |
| **Macie** | Descubrir PII en los buckets de datos fuente antes de indexar |

> **Advertencia de seguridad de la documentación de Knowledge Bases**: todo lo que sincronices desde un data source queda disponible para cualquiera con permisos `bedrock:Retrieve`, **incluidos datos con permisos controlados en el origen**. La governance del retrieval no se hereda del sistema de origen.

---

## Skill 1.6.4 — Aseguramiento de calidad de prompts

> *Desarrollar sistemas de aseguramiento de calidad para asegurar la efectividad y fiabilidad de los prompts para FMs (por ejemplo, funciones Lambda para verificar la salida esperada, Step Functions para probar casos límite, CloudWatch para probar regresión de prompts).*

### El problema: los prompts son código no determinista

Un cambio de prompt, de versión de modelo o de parámetros de inferencia puede degradar la calidad sin producir ningún error. La documentación lo recoge como reto de reliability: *rendimiento inconsistente del modelo*, con mitigación de **frameworks de testing robustos, control de versiones de modelos y prompts, y monitoreo continuo** de métricas de rendimiento ([Reliability](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/reliability.html)).

### Capas de aseguramiento de calidad

| Capa | Herramienta | Qué valida |
| --- | --- | --- |
| **Comparación de variantes** | Prompt builder de Prompt Management | Cuál de varias formulaciones funciona mejor, antes de guardar versión |
| **Evaluación cuantitativa** | [Bedrock evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) programáticas | Scores y métricas sobre un dataset de prompts |
| **Evaluación cualitativa escalable** | Bedrock evaluations con **judge model** | Un segundo LLM puntúa cada respuesta **y explica el score** |
| **Evaluación humana** | Bedrock evaluations con **human workers** (empleados o expertos de dominio) | Preferencias y juicio experto |
| **Calidad del pipeline RAG** | **RAG evaluation** con LLM | Si la fuente recupera información relevante y genera respuestas útiles. Requiere **ground truth**: textos recuperados y respuestas esperadas |
| **Aserciones deterministas** | **Lambda** | Formato, esquema JSON, presencia de campos, ausencia de términos prohibidos, longitud, citas presentes |
| **Orquestación del set de pruebas** | **Step Functions** | Ejecutar todos los casos, incluidos los límite, con paralelismo (Map) y reintentos |
| **Regresión y tendencia** | **CloudWatch** | Métricas históricas de score por versión de prompt, con alarmas ante degradación |
| **Salvaguarda en producción** | **Guardrails** contextual grounding y automated reasoning | Bloquear o marcar respuestas no fundamentadas o lógicamente incorrectas |

### Arquitectura del pipeline de QA de prompts

```
Cambio de prompt (nueva versión en Prompt Management)
   │
   ▼
Step Functions "prompt regression suite"
   ├─ Map state sobre el dataset de casos
   │    ├─ caso normal
   │    ├─ caso límite: entrada vacía, muy larga, ambigua
   │    ├─ caso adversario: intento de prompt injection
   │    ├─ caso multiidioma
   │    └─ caso sin resultados de retrieval
   │         │
   │         ▼
   │    Converse con la versión candidata del prompt
   │         │
   │         ▼
   │    Lambda: aserciones deterministas
   │         · ¿es JSON válido contra el esquema?
   │         · ¿incluye citas?
   │         · ¿respeta la longitud máxima?
   │         · ¿evita términos prohibidos?
   │         · ¿el guardrail intervino cuando debía?
   │         │
   │         ▼
   │    Judge model: score de calidad + explicación
   │
   ├─ Lambda: agregar resultados → PutMetricData a CloudWatch
   │     métricas: PassRate, AvgJudgeScore, GroundednessRate, p95 latencia, tokens medios
   │
   ├─ Choice: ¿PassRate y score por encima del umbral de la versión actual?
   │     no ──► SNS al equipo, no se promueve
   │
   └─ sí ──► promover: AppConfig publica la nueva versión
              · deployment strategy gradual
              · alarma CloudWatch vigilando PassRate en producción
              · rollback automático de AppConfig si la alarma se dispara
```

### Casos límite que el set debe incluir

| Categoría | Ejemplos |
| --- | --- |
| Entrada degenerada | Vacía, solo espacios, un carácter, texto que excede el context window |
| Ambigüedad | Pregunta sin sujeto claro, referencias anafóricas sin contexto |
| Adversario | Intentos de prompt injection, incluidos los que llegan por el **campo `name` de un DocumentBlock** o por el contenido de un documento recuperado |
| Fuera de dominio | Preguntas que deben activar un denied topic |
| Contenido sensible | Entradas con PII que deben activar los sensitive information filters |
| Retrieval vacío | Consulta sin resultados relevantes: debe ejecutarse el fallback, no una alucinación |
| Multiidioma | Idiomas soportados por el guardrail y por el modelo |
| Código | Con Standard tier, contenido dañino dentro de comentarios y literales |

### Métricas de calidad a monitorizar en producción

El Lens indica rastrear **accuracy, toxicity y coherence** de las salidas generadas como parte de la mejora continua, además de recoger feedback de usuarios para identificar sesgos o áreas de ajuste. Complementarias, de reliability: tasa de éxito de recuperación, efectividad de la remediación y alertas ante fallos repetidos (GENREL03-BP01).

---

## Skill 1.6.5 — Refinamiento iterativo del prompt

> *Mejorar el rendimiento del FM refinando prompts iterativamente y mejorando la calidad de respuesta más allá de las técnicas básicas de prompting (por ejemplo, componentes de entrada estructurados, especificaciones de formato de salida, patrones de instrucción chain-of-thought, feedback loops).*

### Componentes de entrada estructurados

| Técnica | Implementación |
| --- | --- |
| **Delimitación explícita de secciones** | Etiquetas XML en modelos Anthropic, con nombres descriptivos. El prompt de sistema por defecto de las knowledge bases usa, por ejemplo, `<database>` para delimitar preguntas previas |
| **Separación instrucción / contexto / entrada** | System prompt para la instrucción persistente; `messages` para la entrada del turno; `$search_results$` para el contexto recuperado |
| **Variables tipadas** | Variables de Prompt Management, con valores aportados en `promptVariables` en tiempo de ejecución |
| **Ejemplos delimitados** | `<example></example>` con delimitadores internos `H:` / `A:` en Claude |
| **Metadatos en el contexto** | Metadatos con `includeForEmbedding: true` para que los atributos influyan en la recuperación, y metadatos devueltos en los resultados para que el modelo cite correctamente |

### Especificación de formato de salida

| Grado de rigor | Mecanismo |
| --- | --- |
| Descripción en el prompt | Instrucción explícita del formato deseado dentro de la plantilla |
| Corte controlado | `stopSequences` en `inferenceConfig` |
| Esquema forzado | [Structured output](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html): resultados JSON validados, combinables con tool use |
| Esquema vía herramienta | `toolConfig` con el esquema de entrada de la herramienta como contrato de salida |
| Citas | Tag `citations` en el `DocumentBlock`; `$output_format_instructions$` en la plantilla de orquestación de la knowledge base |

### Chain-of-thought y patrones de instrucción

Para que el modelo razone antes de responder, los mecanismos disponibles en la plataforma son:

- Instrucciones de razonamiento paso a paso dentro de la plantilla del prompt.
- `stopSequences` para separar el razonamiento de la respuesta final (por ejemplo, el ejemplo oficial usa `"\nObservation"` como stop sequence).
- **Query decomposition** de las knowledge bases, que es chain-of-thought aplicado a la recuperación: descompone la pregunta compleja en sub-preguntas antes de generar la respuesta final.
- Descomposición explícita en **nodos separados de un flow**, donde cada nodo resuelve un paso del razonamiento y su salida alimenta el siguiente.

> Nota relevante de Guardrails: las salvaguardas actúan sobre entradas y respuestas **excluyendo los bloques de contenido de razonamiento**.

### Parámetros de inferencia como palanca de refinamiento

| Parámetro | Efecto | Documentación |
| --- | --- | --- |
| `temperature` | Aleatoriedad de la salida. Bajar para tareas deterministas | [Inference parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-parameters.html) |
| `topP` | Muestreo por masa de probabilidad acumulada | idem |
| `maxTokens` / `maxTokenCount` | Límite de longitud de la respuesta | idem |
| `stopSequences` | Cadenas que detienen la generación | idem |
| `top_k` y otros específicos | Vía `additionalModelRequestFields` | [Model parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html) |

### Optimización asistida y comparación de variantes

- [Optimize a prompt](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-optimize.html) reescribe el prompt adaptándolo al modelo destino.
- Las **prompt variants** del prompt builder permiten comparar formulaciones, modelos y configuraciones de inferencia lado a lado antes de fijar una versión.

### Feedback loops

| Tipo de loop | Implementación |
| --- | --- |
| **Feedback explícito de usuario** | Capturar pulgar arriba/abajo y comentario en la UI, persistir en DynamoDB junto al `conversationId`, la versión de prompt y el `modelId` |
| **Feedback implícito** | Reformulaciones del usuario, abandono de la conversación, escalado a humano |
| **Loop de evaluación** | Alimentar el dataset de Bedrock evaluations con los casos que recibieron feedback negativo |
| **Loop de retrieval** | Casos donde el retrieval falló → ajustar chunking, metadatos, tipo de búsqueda o reranking |
| **Loop de modelo** | **Reinforcement fine-tuning** con reward functions en Lambda, usando datasets de prompts propios o **logs de invocación de Bedrock existentes** ([custom models](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html)) |
| **Human-in-the-loop** | Amazon Augmented AI (A2I) y Bedrock evaluations con human workers |

La fase de **continuous improvement** del ciclo de vida lo formula así: monitorear rendimiento, recoger feedback de usuarios, actualizar el dataset con ejemplos nuevos o datos refinados basados en ese feedback, y mejorar continuamente conforme evolucionan las necesidades y el panorama de datos.

### Orden recomendado de refinamiento

Ordenado de menor a mayor coste y riesgo:

1. Refinar el prompt: instrucción, contexto, ejemplos, formato de salida.
2. Ajustar parámetros de inferencia.
3. Mejorar el retrieval: chunking, metadatos, híbrida, reranking.
4. Cambiar de modelo dentro de la misma familia (prompt router).
5. Cambiar de familia de modelo.
6. Personalizar el modelo: distillation, fine-tuning supervisado, reinforcement fine-tuning.

---

## Skill 1.6.6 — Sistemas de prompts complejos con Flows

> *Diseñar sistemas complejos de prompts para manejar tareas sofisticadas con FMs (por ejemplo, Amazon Bedrock Prompt Flows para cadenas secuenciales de prompts, ramificación condicional basada en las respuestas del modelo, componentes de prompt reutilizables, pasos integrados de pre-procesamiento y post-procesamiento).*

### Qué es Amazon Bedrock Flows

De [Build an end-to-end generative AI workflow with Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html). Permite construir workflows enlazando **prompts, foundation models y otros servicios de AWS** para crear soluciones end-to-end. Aporta un **constructor visual**, integración directa con FMs, knowledge bases y servicios como AWS Lambda transfiriendo datos entre ellos, y despliegue de **workflows inmutables** para pasar de test a producción.

**Precio**: depende de los recursos que uses. Si invocas un flow con un nodo prompt que usa un modelo Titan, se cobra la invocación de ese modelo. Cuotas en [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html).

### Ciclo de vida de un flow

**Crear**
1. Especificar nombre, descripción y permisos IAM apropiados.
2. Decidir los nodos a usar.
3. Crear o definir todos los recursos que requiere cada nodo (por ejemplo, las funciones Lambda necesarias).
4. Añadir nodos, configurarlos y crear las conexiones enlazando la salida de un nodo con la entrada de otro.

**Probar**
1. **Preparar** el flow, para que los últimos cambios se apliquen al **working draft**, la versión que se usa para iterar y probar.
2. Invocar con entradas de ejemplo y ver las salidas.
3. Cuando la configuración satisface, crear una **versión**: una instantánea de la definición del flow en ese momento. **Las versiones son inmutables**.

**Desplegar**
1. Crear un **alias** que apunte a la versión que quieres usar.
2. Configurar la aplicación para hacer peticiones **`InvokeFlow`** al alias. Para volver a una versión anterior o subir a una nueva, se cambia la **routing configuration del alias**.

Este mecanismo alias → versión es el equivalente de rollback instantáneo a nivel de workflow, sin desplegar código.

### Tipos de nodo

De [Node types for your flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-nodes.html). Cada nodo se configura con **Name**, **Type**, **Inputs** (nombre, **expression** y tipo), **Outputs** (nombre y tipo) y **Configuration**.

Las **expressions** definen qué parte de la entrada completa se usa como entrada individual; en tiempo de ejecución Bedrock aplica la expresión a la entrada completa y **valida que el resultado coincide con el tipo de dato declarado**. Ver [Use expressions to define inputs](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-expressions.html).

**Nodos de control de lógica**

| Nodo | Comportamiento |
| --- | --- |
| **Input** | **Cada flow contiene exactamente uno y debe comenzar por él.** Toma el `content` de la petición `InvokeFlow`, valida el tipo de dato y lo pasa al nodo siguiente |
| **Output** | Extrae los datos del nodo anterior según la expresión definida y los devuelve. En la API, en el campo `content` del `flowOutputEvent` de la respuesta de `InvokeFlow`. **Un flow puede tener varios nodos Output** si hay varias ramas |
| **Condition** | Envía los datos a nodos distintos según las condiciones definidas. Puede tomar múltiples entradas |
| **Iterator** | Toma un array y devuelve sus elementos uno a uno al nodo siguiente. **Se procesan de uno en uno, no en paralelo.** El nodo Output devuelve el resultado de cada entrada en una respuesta distinta |
| **Collector** | Toma una entrada iterada más el tamaño que tendrá el array y los devuelve como array. Se usa aguas abajo de un iterator para recolectar las respuestas iteradas |

Tipos de dato de entradas y salidas: `String`, `Number`, `Boolean`, `Object`, `Array`.

**Operadores de condición**

Relacionales: `==` (igual, el tipo de dato también debe coincidir), `!=`, `>`, `>=`, `<`, `<=`. Los tres primeros admiten String, Number y Boolean; los de orden solo Number.

Lógicos: `and`, `or`, `not`. AWS recomienda usar paréntesis para resolver ambigüedades de agrupación.

Se puede comparar una entrada con otra entrada o con una constante: con entradas `profit` y `expenses`, tanto `profit > expenses` como `profit <= 1000` son expresiones válidas.

> **Regla de evaluación crítica**: **las condiciones se evalúan en orden. Si se cumple más de una, tiene precedencia la anterior.** Para la condición por defecto se especifica la condición como `default`.

**Estructura de un nodo Condition en la API**

```json
{
  "name": "string",
  "type": "Condition",
  "inputs": [
    { "name": "string", "type": "Number", "expression": "string" }
  ],
  "configuration": {
    "condition": {
      "conditions": [
        { "name": "string", "expression": "string" }
      ]
    }
  }
}
```

Los nodos Condition **no tienen `outputs`**. Las conexiones se definen en el array `connections` de `CreateFlow` o `UpdateFlow`: una `FlowConnection` de tipo **`Data`** por cada entrada al nodo, y una de tipo **`Conditional`** por cada condición, incluida la default.

```json
{
  "name": "string",
  "source": "string",
  "target": "string",
  "type": "Conditional",
  "configuration": {
    "conditional": { "condition": "string" }
  }
}
```

### Casos de uso oficiales de flows

La documentación enumera estos ejemplos:

- **Crear y enviar una invitación por email**: nodo prompt + nodo knowledge base + nodo Lambda. El prompt genera el cuerpo del email, la knowledge base busca las direcciones del equipo, y la Lambda envía la invitación.
- **Troubleshooting a partir de un mensaje de error y el ID del recurso**: el flow busca causas posibles en una knowledge base de documentación, recoge logs de sistema e información del recurso, y actualiza configuraciones defectuosas.
- **Generar informes**: busca métricas de ventas en una base de datos, las agrega, genera un informe resumen de los productos más vendidos y lo publica en el portal indicado.
- **Ingerir datos de un dataset**: prepara los datos, informa del estado, filtra los fallidos, y al terminar resume los fallos y publica un informe.

### Cadenas secuenciales, ramificación y componentes reutilizables

| Requisito del skill | Implementación en Flows |
| --- | --- |
| **Cadenas secuenciales de prompts** | Varios nodos prompt conectados, cada uno alimentando al siguiente |
| **Ramificación condicional según respuesta del modelo** | Nodo **Condition** evaluando la salida del nodo prompt anterior, con conexiones `Conditional` por rama |
| **Componentes de prompt reutilizables** | Nodos prompt que referencian prompts **versionados de Prompt Management**, compartidos entre flows |
| **Pre-procesamiento integrado** | Nodo **Lambda** al inicio: normalización, validación, enriquecimiento de metadatos |
| **Post-procesamiento integrado** | Nodo **Lambda** al final: validación de esquema, redacción, persistencia, notificación |
| **Procesamiento por lotes dentro del flow** | **Iterator** + **Collector** |
| **Recuperación de contexto** | Nodo **knowledge base** |
| **Delegación a un agente** | Nodo **agent** |
| **Ejecución asíncrona de larga duración** | [Flow executions asíncronas](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-create-async.html) |
| **Conversación multi-turno** | [Converse with a flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-multi-turn-invocation.html) |
| **Seguridad de contenido en el workflow** | [Include guardrails in your flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-guardrails.html) |
| **Lambda en otra cuenta** | [Invoke a Lambda function from a flow in a different account](https://docs.aws.amazon.com/bedrock/latest/userguide/flow-cross-account-lambda.html) |

### Flows como mecanismo de reliability

Recordatorio de [GENREL03-BP01](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel03-bp01.html): al desarrollar flujos multi-paso o cadenas de prompts, el Lens recomienda **Amazon Bedrock Flows** porque habilita fallo y recuperación elegantes en cadenas largas, y sugiere usar sus **nodos iterator y condition** para implementar recuperación en lugar de construir una capa de abstracción propia.

### Ejemplo de flow con las seis capacidades del skill

```
[Input]
   │
[Lambda: pre-procesamiento]          ← normaliza, valida, detecta idioma
   │
[Condition: ¿entrada válida?]
   ├─ no ──────────────────► [Output: mensaje de error controlado]
   │
   └─ sí
      │
   [Prompt: clasificar intención]     ← prompt versionado de Prompt Management
      │
   [Condition: tipo de intención]     ← ramificación según respuesta del modelo
      ├─ consulta de documentación ──► [Knowledge base] ──┐
      ├─ cálculo o acción ──────────► [Agent] ────────────┤
      └─ default ───────────────────► [Prompt: respuesta genérica] ─┤
                                                                     │
                                          [Prompt: redacción final] ←┘
                                                    │
                                    [Lambda: post-procesamiento]     ← valida esquema, persiste, notifica
                                                    │
                                                [Output]
```

Desplegado como **versión inmutable** detrás de un **alias**; un problema en producción se resuelve cambiando la routing configuration del alias a la versión anterior.

---

## Preguntas de autoevaluación

1. ¿Cuáles son las seis salvaguardas de Bedrock Guardrails y cuál detecta específicamente respuestas no fundamentadas en la fuente recuperada?
2. Necesitas evaluar con el guardrail **solo la entrada del usuario**, no los resultados de búsqueda ni el histórico. ¿Cómo se hace y qué limitación de interfaz tiene?
3. ¿Qué API aplica un guardrail **sin invocar** ningún foundation model?
4. ¿Qué diferencia hay entre `equals` con `==` en un nodo Condition y una comparación normal, respecto a los tipos de dato?
5. Un flow tiene tres condiciones y dos se cumplen a la vez. ¿Cuál gana?
6. ¿Cuántos nodos Input puede tener un flow? ¿Y nodos Output?
7. ¿El nodo Iterator procesa los elementos en paralelo?
8. ¿Cómo haces rollback de un flow en producción sin desplegar código?
9. ¿Qué campo de la petición `Converse` permite etiquetar la invocación con metadatos filtrables después en los invocation logs?
10. ¿Qué cuatro campos no puedes incluir en `Converse` si usas un prompt de Prompt Management?
11. ¿Qué placeholder es obligatorio en la plantilla de orquestación para que la respuesta incluya citas?
12. ¿Qué método de customización permite cerrar el feedback loop usando logs de invocación existentes y reward functions en Lambda?

## Fuentes oficiales de esta sección

**Prompt engineering y management**
- [Prompt engineering concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html)
- [Construct and store reusable prompts with Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html)
- [Create a prompt using Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-create.html)
- [Test a prompt using Prompt management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-test.html)
- [Optimize a prompt](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-optimize.html)
- [Deploy a prompt to your application using versions](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-deploy.html)
- [Influence response generation with inference parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-parameters.html)
- [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html)

**Guardrails**
- [Detect and filter harmful content by using Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [How Amazon Bedrock Guardrails works](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-how.html)
- [Safeguard tiers for guardrails policies](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tiers.html)
- [Apply tags to user input to filter content](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html)
- [Distribute guardrail inference across AWS Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region.html)
- [Apply cross-account safeguards with Guardrails enforcements](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-enforcements.html)

**Flows**
- [Build an end-to-end generative AI workflow with Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html)
- [How Amazon Bedrock Flows works](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-how-it-works.html)
- [Node types for your flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-nodes.html)
- [Use expressions to define inputs in Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-expressions.html)
- [Deploy a flow using versions and aliases](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-deploy.html)
- [Include guardrails in your flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-guardrails.html)
- [Run Amazon Bedrock flows asynchronously with flow executions](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-create-async.html)
- [Converse with an Amazon Bedrock flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-multi-turn-invocation.html)

**Governance y observabilidad**
- [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html)
- [Set up a model invocation resource using inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)
- [Organizing and tracking costs using AWS cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html)
- [CloudTrail management events in model evaluation jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/cloudtrail-events-in-model-evaluations.html)
- [Observability for managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-observability.html)
- [GENREL04 Prompt management](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel04.html)
- [GENREL03-BP01 Use logic to manage prompt flows and gracefully recover from failure](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel03-bp01.html)

**Conversación e intención**
- [Inference using Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Amazon Comprehend Custom](https://docs.aws.amazon.com/comprehend/latest/dg/concepts-custom.html)
- [Amazon Comprehend Flywheels](https://docs.aws.amazon.com/comprehend/latest/dg/flywheels.html)
- [Customize your model to improve its performance](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html)
