# Task 2.5 — Patrones de integración de aplicaciones y herramientas de desarrollo

[← Volver al índice](./README.md)

Skills cubiertos: **2.5.1**, **2.5.2**, **2.5.3**, **2.5.4**, **2.5.5**, **2.5.6**.

---

## Skill 2.5.1 — Interfaces de API para cargas GenAI

> *Crear interfaces de API de FM para atender los requisitos específicos de las cargas GenAI (por ejemplo, usando API Gateway para manejar respuestas en streaming, gestión de límites de tokens, estrategias de reintento para manejar timeouts del modelo).*

### Los tres requisitos que diferencian una API GenAI

Una API convencional responde en milisegundos con un payload de tamaño acotado. Una API sobre un FM tiene tres características que rompen ese supuesto, y este skill es la respuesta a cada una:

| Característica | Consecuencia | Mecanismo |
| --- | --- | --- |
| **La respuesta llega poco a poco** | Esperar el final multiplica la latencia percibida | Streaming: `ConverseStream`, response streaming de Lambda, WebSocket |
| **La unidad de consumo es el token** | El coste y la cuota no se miden en peticiones | `CountTokens`, `maxTokens`, cuotas TPM, usage plans |
| **La generación puede tardar o cortarse** | Los timeouts y los reintentos tienen semántica propia | `retry_mode`, colas, idempotencia |

### Streaming a través de la capa de API

El detalle técnico completo (formato de salida, delimitador de 8 bytes nulos, `Transfer-Encoding: chunked`, tabla de combinaciones soportadas, límites de WebSocket) está en [Skill 2.4.2](./task-2-4-integraciones-api-fm.md#skill-242--interacción-en-tiempo-real-y-streaming). Lo que corresponde a este skill es la decisión de contrato:

| Contrato público | Implementación | Cuándo |
| --- | --- | --- |
| **Respuesta completa** (JSON) | Integración proxy bufferizada | Clasificación, extracción, cualquier salida estructurada que el cliente consume entera |
| **Stream de texto** | Lambda proxy en modo stream, o function URL | Generación de texto para mostrar al usuario |
| **Eventos bidireccionales** | WebSocket API con `@connections` | Chat con interrupción, progreso de herramientas, multi-turno |
| **Publicación a suscriptores** | AppSync subscriptions | Varios clientes esperando el mismo resultado |
| **Aceptar y notificar** | `202` + SQS + notificación posterior | Generación larga que no cabe en la ventana del llamante |

> Regla que se deriva de la tabla de combinaciones soportadas de API Gateway: **el modo de transferencia es parte del contrato de la API, no un detalle de implementación**. Pasar de bufferizado a streaming obliga a cambiar el formato de salida de la Lambda y el URI de la integración. Conviene decidirlo antes de publicar.

### Gestión de límites de tokens

De [Monitor your token usage by counting tokens before running inference](https://docs.aws.amazon.com/bedrock/latest/userguide/count-tokens.html). El número de tokens de entrada contribuye al coste de la petición **y a la cuota de tokens por minuto y por día**. La API **`CountTokens`** estima el uso antes de enviar la petición, devolviendo el conteo que se usaría si esa misma entrada se enviara en una petición de inferencia.

| Dato | Detalle |
| --- | --- |
| **Coste de usarla** | **Usar `CountTokens` no incurre cargos** |
| **Exactitud** | El conteo devuelto **coincide con el que se facturaría** si la misma entrada se enviara a inferencia |
| **Por qué es específico del modelo** | Los modelos usan **estrategias de tokenización distintas** |
| **Formato del `body`** | Para `InvokeModel`, un string que representa un objeto JSON cuyo formato depende del modelo. Para `Converse`, un objeto JSON con `messages` y `system` |
| **Permisos** | `bedrock:CountTokens` y `bedrock:InvokeModel` (que habilita `InvokeModel` y `Converse`), acotado al menos al ARN del foundation model |
| **Soporte** | Consultar [models at a glance](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html) por modelo |

Los tres usos que enumera la documentación: **estimar costes** antes de enviar, **optimizar prompts para que quepan en los límites de tokens**, y **planificar el uso de tokens** en la aplicación.

> **Excepción documentada**: algunos modelos Anthropic Claude, incluidos los que se lanzan **solo con cross-Region inference (CRIS)** en `bedrock-runtime`, **no soportan `CountTokens` en `bedrock-runtime`**. Para esos modelos hay que contar los tokens de entrada llamando a la API `count_tokens` de Anthropic **en el endpoint `bedrock-mantle`**.

Las capas de control de tokens en la API:

```
BORDE          API Gateway
               · request validation: rechazar payloads fuera de esquema
                 ANTES de que consuman tokens
               · límite de tamaño del body en el modelo de validación
               · usage plan por consumidor: cuota y rate limit propios
                  │
PRE-INFERENCIA CountTokens (gratis)
               · ¿cabe en el context window del modelo elegido?
               · ¿cabe en el presupuesto del tenant o de la sesión?
               · si no cabe: truncar el histórico, resumir turnos antiguos,
                 o enrutar a un modelo de contexto mayor
                  │
INFERENCIA     inferenceConfig.maxTokens  → techo de la salida
               stopSequences               → corte controlado
               serviceTier                 → Flex / Standard / Priority
               prompt caching              → reduce tokens de entrada
                                             facturados (estático primero)
                  │
POST-INFERENCIA campo usage de la respuesta
               · acumular por tenant, por caso de uso, por versión de prompt
               · requestMetadata para poder filtrar los invocation logs
               · alarma de CloudWatch al acercarse al presupuesto
```

Los límites del tier (RPM y TPM de Flex, Standard y Priority) y las cuotas de batch están en [Task 2.2 · Skill 2.2.1](./task-2-2-despliegue-de-modelos.md#límites-y-cuotas-por-tier). El detalle de prompt caching, incluidos los mínimos por checkpoint y el TTL, en [Task 2.2 · Skill 2.2.3](./task-2-2-despliegue-de-modelos.md#reducir-el-coste-sin-cambiar-de-modelo-prompt-caching).

### Estrategias de reintento ante timeouts del modelo

La mecánica completa del SDK (modos `standard`, `adaptive` y `legacy`, retry quota, `AWS_MAX_ATTEMPTS`, backoff diferenciado por tipo de error) está en [Skill 2.4.3](./task-2-4-integraciones-api-fm.md#reintentos-del-sdk-los-tres-modos). Lo específico de la capa de API:

| Problema | Tratamiento en la capa de API |
| --- | --- |
| **La generación excede la ventana del llamante** | Cambiar el contrato: `202` + polling, o `202` + notificación por WebSocket. Reintentar no lo arregla |
| **Reintentar una generación ya iniciada** | **Idempotencia obligatoria**: clave de idempotencia con escritura condicional en DynamoDB y TTL. Sin ella se paga dos veces la misma generación |
| **Throttling de Bedrock** | El `retry_mode` standard del SDK lo reintenta con backoff más largo que un error transitorio. Si persiste, encolar en SQS, cambiar de tier o de modelo |
| **Timeout de la integración de API Gateway** | Acotar la generación con `maxTokens` para que quepa, o mover a streaming, donde el primer byte llega pronto |
| **Cliente que corta la conexión** | En Lambda response streaming, **la ejecución no se interrumpe y se factura la duración completa**. Hace falta un límite propio, no confiar en la desconexión |
| **Reintento del cliente** | Devolver `429` con cabecera de reintento y documentar la política, para que el cliente reintente **de forma limitada en tasa** como recomienda la documentación de throttling |

> El punto que más se pasa por alto: **una respuesta en streaming que falla a mitad ya consumió tokens**. La contabilidad de coste no puede basarse solo en las respuestas completas.

---

## Skill 2.5.2 — Interfaces de IA accesibles

> *Desarrollar interfaces de IA accesibles para acelerar la adopción e integración de FMs (por ejemplo, usando AWS Amplify para desarrollar componentes de UI declarativos, especificaciones OpenAPI para enfoques de desarrollo API-first, Amazon Bedrock Prompt Flows como constructores de workflows no-code).*

### AWS Amplify

De [Welcome to AWS Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/welcome.html). Amplify Hosting provee un **workflow basado en Git** para alojar aplicaciones web serverless full-stack **con despliegue continuo**, desplegando a la **red global de distribución de contenido (CDN) de AWS**.

**Frameworks soportados:**

| Categoría | Frameworks |
| --- | --- |
| **SSR** | Next.js, Nuxt, Astro (con adaptador de la comunidad), SvelteKit (con adaptador de la comunidad), cualquier framework SSR con adaptador propio |
| **SPA** | React, Angular, Vue.js, Ionic, Ember |
| **Generadores estáticos** | Eleventy, Gatsby, Hugo, Jekyll, VuePress |

**Funcionalidades de Amplify Hosting**, y por qué importan en una aplicación GenAI:

| Funcionalidad | Valor |
| --- | --- |
| **Feature branches** | Gestionar entornos de producción y staging de frontend y backend conectando ramas nuevas: una rama por variante de prompt o de modelo |
| **Custom domains** | Dominio propio |
| **Pull request previews** | Previsualizar cambios durante la revisión de código: útil para revisar un cambio de prompt sobre la UI real |
| **End-to-end testing** | Tests end-to-end integrados en el pipeline |
| **Password protected branches** | Proteger con contraseña para trabajar en funcionalidades nuevas sin exponerlas |
| **Redirects y rewrites** | Mantener SEO y enrutar tráfico según los requisitos del cliente |
| **Atomic deployments** | **Eliminan ventanas de mantenimiento**: la app se actualiza solo cuando el despliegue completo termina, evitando estados donde algunos ficheros no subieron bien |

Repositorios soportados para el despliegue continuo: **GitHub, BitBucket, GitLab y AWS CodeCommit**.

**Amplify Gen 2** introduce una experiencia de desarrollo **code-first basada en TypeScript** para definir backends.

> **Hueco de documentación**: el skill habla de *componentes de UI declarativos*, pero la documentación de **Amplify Gen 2** (librerías de Data y Auth y la **Amplify UI library**) vive en **`docs.amplify.aws`**, fuera de `docs.aws.amazon.com`. El portal de AWS cubre **Amplify Hosting**; el modelo de componentes y el backend code-first se documentan aparte. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación).

### OpenAPI para desarrollo API-first

De [Develop REST APIs using OpenAPI in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-import-api.html). API Gateway permite **importar una REST API desde un fichero de definición externo**. Soporta **OpenAPI v2.0 y OpenAPI v3.0**, con las excepciones listadas en las notas importantes para REST APIs.

| Capacidad | Detalle |
| --- | --- |
| **Importar** | Desde un fichero de definición externo |
| **Actualizar** | **Sobrescribiendo** con una definición nueva, o **fusionando** la definición con una API existente. Se elige con el parámetro de query **`mode`** en la URL de la petición |
| **Exportar** | [Export a REST API from API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-export-api.html) |
| **basePath** | Se controla con la [propiedad `basePath` de OpenAPI](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-import-api-basePath.html) |
| **Variables de AWS** | [AWS variables for OpenAPI import](https://docs.aws.amazon.com/apigateway/latest/developerguide/import-api-aws-variables.html) para parametrizar la definición |
| **Tipos de endpoint** | Importación de APIs [edge-optimized](https://docs.aws.amazon.com/apigateway/latest/developerguide/import-edge-optimized-api.html) y [Regional](https://docs.aws.amazon.com/apigateway/latest/developerguide/import-export-api-endpoints.html) |
| **Diagnóstico** | [Errores y avisos de la importación](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-import-api-errors-warnings.html) |

El valor del enfoque API-first en un contexto GenAI: la especificación es el contrato que **desacopla al consumidor del modelo**. El cliente programa contra el esquema; detrás puede cambiar el modelo, el proveedor, la versión de prompt o incluso pasar de Bedrock a un endpoint de SageMaker AI.

> Y hay un segundo uso, menos evidente pero directamente relevante: **AgentCore Gateway acepta especificaciones OpenAPI como tipo de herramienta MCP**, transformando REST APIs existentes en herramientas compatibles con MCP y traduciendo automáticamente entre MCP y REST. La misma especificación sirve para documentar la API a humanos y para exponerla a agentes. Ver [Task 2.1 · Skill 2.1.6](./task-2-1-agentic-ai-y-herramientas.md#centralizar-herramientas-con-agentcore-gateway).

### Bedrock Prompt Flows como constructor no-code

La mecánica completa de [Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html), incluidos los tipos de nodo, las expresiones, el despliegue con versiones y alias, los guardrails en el flow y la conversación multi-turno, está en [Task 1.6 · Skill 1.6.6](../domain-1/task-1-6-prompt-engineering-governance.md). Lo que aporta a este skill es el argumento de accesibilidad:

| Aspecto | Por qué acelera la adopción |
| --- | --- |
| **Constructor visual** | El workflow se compone arrastrando nodos, sin escribir código de orquestación |
| **Nodos reutilizables** | Prompt nodes que referencian prompts versionados de Prompt Management, knowledge base nodes, nodos de Lambda, de Lex, de condición |
| **Versiones y alias** | Promoción controlada sin tocar la aplicación que invoca el flow |
| **Guardrails integrados** | La política de contenido se aplica dentro del flow |
| **Conversación multi-turno** | El flow puede pedir información adicional al usuario en medio de la ejecución |
| **Ejecución asíncrona** | Flow executions para trabajos largos |

La decisión frente a Step Functions, que conviene tener clara:

| | **Bedrock Flows** | **Step Functions** |
| --- | --- | --- |
| **Perfil de usuario** | Perfiles no técnicos o prototipado rápido | Ingeniería, con control fino |
| **Primitivas** | Nodos orientados a GenAI | Estados de propósito general |
| **Reintentos y timeouts por paso** | Limitados a lo que expone el nodo | `Retry`, `Catch`, `TimeoutSeconds`, `HeartbeatSeconds` por estado |
| **Espera humana** | Interacción multi-turno del flow | `.waitForTaskToken` con heartbeat (solo Standard) |
| **Estado durable** | Traceability del flow | Historial de ejecución completo, hasta 1 año |
| **Integraciones** | Las de los tipos de nodo | Más de doscientos servicios vía AWS SDK integrations |

### Las tres vías de acceso, por audiencia

```
NO-CODE        Bedrock Prompt Flows (constructor visual)
               Amazon Q Business (asistente sobre contenido corporativo)
               Bedrock Playground para experimentar
                  │
LOW-CODE       Amplify Hosting + framework SPA/SSR
               · feature branches por variante
               · PR previews para revisar cambios de prompt
               · atomic deployments
                  │
API-FIRST      Especificación OpenAPI como contrato
               · importada a API Gateway (mode: overwrite o merge)
               · exportable para generar clientes
               · reutilizable como MCP target en AgentCore Gateway
                  │
CÓDIGO         SDKs de AWS por lenguaje contra Bedrock Runtime
               Step Functions para orquestación con control fino
```

---

## Skill 2.5.3 — Mejoras de sistemas de negocio

> *Crear mejoras de sistemas de negocio (por ejemplo, usando funciones Lambda para implementar mejoras de customer relationship management [CRM], Step Functions para orquestar sistemas de procesamiento de documentos, Amazon Bedrock Data Automation para gestionar workflows automatizados de procesamiento de datos).*

### Bedrock Data Automation

De [Transform unstructured data into meaningful insights using Amazon Bedrock Data Automation](https://docs.aws.amazon.com/bedrock/latest/userguide/bda.html). Servicio que **simplifica la extracción de insights de contenido no estructurado** (documentos, imágenes, vídeo y audio), usando IA generativa para **automatizar la transformación de datos multimodales a formatos estructurados**.

Los tres casos de uso oficiales:

| Caso de uso | Qué aporta |
| --- | --- |
| **Procesamiento de documentos** | Automatiza workflows de **intelligent document processing (IDP)** a escala **sin orquestar** tareas complejas de clasificación, extracción, normalización o validación. Transforma documentos no estructurados en salidas estructuradas específicas del negocio |
| **Análisis de medios** | Resúmenes de cada escena, identificación de contenido no seguro o explícito, extracción del texto que aparece en el vídeo, y clasificación por anuncios o marcas. Habilita búsqueda inteligente de vídeo, colocación contextual de publicidad y brand safety |
| **Asistentes GenAI** | Mejora el rendimiento de aplicaciones **RAG** aportando representaciones ricas y específicas por modalidad extraídas de documentos, imágenes, vídeo y audio |

Provee una experiencia **unificada y API-driven** que permite procesar contenido multimodal **por una sola interfaz**, eliminando la necesidad de gestionar y orquestar múltiples modelos y servicios. Incorpora salvaguardas integradas: **visual grounding y confidence scores**.

### Standard output frente a custom output

De [Standard output in Bedrock Data Automation](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-standard-output.html). El standard output es **la forma predeterminada** de interactuar con BDA: si se pasa un documento a la API **sin blueprint ni proyecto establecido**, devuelve el standard output por defecto para ese tipo de fichero.

| Aspecto | Standard output | Custom output |
| --- | --- | --- |
| **Cuándo se genera** | **Siempre**. BDA da respuesta de standard output **incluso cuando hay custom output** | Solo si se configura un blueprint |
| **Configuración** | Se modifica mediante **proyectos**, que almacenan la configuración por tipo de dato. **Una configuración de standard output por tipo de dato y proyecto** | Mediante **blueprints** |
| **Obligatoriedad en un proyecto** | **Obligatorio** | **Opcional** |
| **Qué produce** | Transcripciones, resúmenes, resúmenes de escena, texto detectado y demás opciones por tipo de dato | **Exactamente los campos que defines** |

### Proyectos

De [Bedrock Data Automation projects](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-projects.html). Un proyecto es **una agrupación de configuraciones de standard y custom output**. Al llamar a **`InvokeDataAutomationAsync`** con el ARN de un proyecto, el fichero se procesa automáticamente con esas configuraciones.

| Característica | Detalle |
| --- | --- |
| **Stages** | **`LIVE`** o **`DEVELOPMENT`**. Cada stage es una **versión única y mutable** del proyecto: se edita y prueba con `DEVELOPMENT` y se sirven peticiones de clientes con `LIVE`. **Los proyectos `DEVELOPMENT` no son accesibles en la consola** y deben cambiarse e invocarse por API |
| **Multi-tipo** | Un proyecto sirve **varios tipos de fichero**: un audio enviado al proyecto ABC se procesa con la configuración de standard output de audio de ABC; un documento, con la de documento |
| **Herencia del custom output** | Un proyecto configurado para generar custom output **genera standard output automáticamente también** |
| **Tipos no configurados** | Si se pasa un tipo de fichero sin configurar en el proyecto, se recibe **el standard output por defecto** de ese tipo |

**Límites y comportamientos de los blueprints dentro de un proyecto**, que son datos muy concretos y por tanto material de examen:

| Límite | Valor |
| --- | --- |
| **Blueprints de documento por proyecto** | Hasta **40**. BDA **empareja automáticamente** cada documento con el blueprint apropiado configurado en el proyecto |
| **Blueprints de imagen por proyecto** | **Uno solo** |
| **Blueprints de audio por proyecto** | **Uno solo** |
| **Document splitting** | Si se pasa un fichero que contiene **varios documentos**, se puede elegir **dividirlo** al crear el proyecto: BDA escanea el fichero y lo divide en documentos individuales **según el contexto**, y luego los empareja con el blueprint correcto |

> **Recomendación oficial sobre imágenes**: los tipos JPG y PNG **pueden tratarse como imágenes o como documentos escaneados según su contenido**. AWS recomienda **crear un blueprint personalizado para imágenes** al procesar custom output de documentos, para que BDA dé la salida deseada con ficheros de imagen que contienen texto.

El ejemplo oficial que ilustra el valor del proyecto: si solo interesan los resúmenes de transcripción de audio y vídeo, por defecto BDA devuelve además transcripciones completas, resúmenes por escena, texto detectado y más. Configurando un proyecto que habilite **solo Full Video Summary** (y el equivalente en audio), se evita **gastar tiempo y recursos en recoger información que no se necesita**.

### Blueprints

De [Blueprints](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-blueprint-info.html). Artefactos que configuran la **lógica de negocio del procesamiento**. Cada blueprint consiste en una lista de nombres de campo a extraer, el formato de dato en que se quiere la respuesta (string, number, boolean) y **contexto en lenguaje natural para cada campo** con el que especificar reglas de normalización y validación. Se crea un blueprint **por clase de fichero**: un W2, una nómina, un documento de identidad. Cada blueprint es un **recurso de AWS con su propio ID y ARN**.

**Dos orígenes**: blueprints del **catálogo** (punto de partida prefabricado si ya se sabe el tipo de fichero) o **personalizados** para ficheros que no están en el catálogo.

**Tres métodos de creación**: generado mediante **blueprint prompt**, creación manual añadiendo campos individuales, o escribiendo el **JSON en el JSON Editor**. Se pueden guardar en la cuenta y compartir.

> **Los blueprints de audio no se pueden crear mediante Blueprint Prompts.**

**Límites del blueprint:**

| Límite | Valor |
| --- | --- |
| **Tamaño máximo** | **100.000 caracteres**, en formato JSON |
| **Campos máximos con `InvokeDataAutomationAsync`** | **100** |
| **Campos máximos con `InvokeDataAutomation`** | **15** |
| **Longitud de los prompts de campo** | Hasta **300 caracteres** |
| **Subcampos de un table field** | Hasta **15** |
| **Campos de custom type por blueprint** | Hasta **30** |

> **Aviso de seguridad oficial**: al usar blueprints se usan prompts, en campos o para la creación del blueprint. **Permitir solo que fuentes de confianza controlen la entrada del prompt. Amazon Bedrock no es responsable de validar la intención del blueprint.** Es el mismo principio de contenido no confiable que en el resto del dominio.

**Los dos tipos de extracción:**

| Tipo | Uso | Ejemplo oficial |
| --- | --- | --- |
| **Explicit** | Información **claramente indicada y visible** en el documento | El nombre tal como aparece |
| **Implicit** (inferred) | Información que **necesita transformarse** respecto a cómo aparece | Quitar los guiones de un número de seguridad social, convirtiendo `111-22-3333` en `111223333` |

**Los componentes de un campo:**

| Componente | Detalle |
| --- | --- |
| **Field name** | El nombre que se usa en el sistema downstream, por ejemplo `Place_of_birth`. **No puede contener barras (`/`)**: usar guiones bajos o alfanuméricos |
| **Description** | **Contexto en lenguaje natural** que describe reglas de normalización o validación: `Date of birth in YYYY-MM-DD format`, o incluso `Is the year of birth before 1992?`. Sirve además para **iterar y mejorar la precisión**: un prompt detallado ayuda a los modelos subyacentes |
| **Results** | La información extraída según el prompt y el nombre del campo |
| **Type** | string, number, boolean, **array of string** y **array of numbers** |
| **Confidence score** | El **porcentaje de certeza** de BDA sobre la precisión de la extracción |
| **Extraction type** | Explicit o inferred |
| **Page number** | En qué página del documento se encontró el resultado |

> **Dos excepciones importantes**:
> - **Los blueprints de audio e imagen no devuelven confidence score.**
> - **Los blueprints de audio y vídeo no devuelven page number.**
>
> Un pipeline que enrute a revisión humana según el confidence score **no puede aplicarse a audio ni a imágenes**: ahí la señal no existe.

**Tres estructuras más allá del campo simple:**

| Estructura | Qué es |
| --- | --- |
| **Table fields** | Campo con **column fields** (nombre, descripción y tipo de columna). En la tabla de extracción, los resultados de columna se agrupan bajo el nombre de la tabla. **Máximo 15 subcampos** |
| **Groups** | Estructura para organizar varios resultados en una sola ubicación de la extracción. Se nombra el grupo y se colocan campos dentro |
| **Custom types** | Se crean editando un blueprint en el **Blueprint Playground**. **Cualquier campo puede ser un custom type**. Tiene nombre único y provoca la creación de los campos que lo componen. Ejemplo oficial: un custom type `Address` con `zip_code`, `city_name`, `street_name` y `state`, usable luego en un campo `company_address` que devuelve toda la información agrupada. **Máximo 30 campos de custom type por blueprint** |

### Las tres vías de procesamiento de documentos: cuál elegir

Esta es la comparación que el skill exige poder hacer, y las tres opciones están documentadas en el portal de AWS:

| | **Bedrock Data Automation** | **Textract + Step Functions** | **Parsing de knowledge base** |
| --- | --- | --- | --- |
| **Qué produce** | **Campos estructurados** definidos por blueprint, más standard output | Texto, formularios, tablas y firmas; la estructura la construyes tú | **Chunks indexados** para retrieval |
| **Orquestación** | **Gestionada**: no hay que orquestar clasificación, extracción, normalización ni validación | **Propia**: tú compones los pasos | Gestionada, dentro del ingestion job |
| **Modalidades** | Documento, imagen, **vídeo y audio** | Documento e imagen | Lo que soporte el parser configurado |
| **Confianza** | **Confidence score** por campo (no en audio ni imagen) y **visual grounding** | Scores de confianza de Textract | — |
| **Clasificación automática** | **Sí**: empareja el documento con el blueprint adecuado entre hasta 40 | Propia, con un clasificador que añades | — |
| **División de ficheros multi-documento** | **Sí**, por contexto | Propia | — |
| **Salida esperada** | JSON con el esquema del blueprint | Lo que construyas | Respuestas generadas con citas |
| **Cuándo** | IDP a escala con esquema de negocio conocido | Control fino, pasos propios, integración con lógica existente | Preguntas en lenguaje natural sobre el corpus |

La base de parsing de knowledge base y de procesamiento multimodal está en [Task 1.3 · Skill 1.3.2](../domain-1/task-1-3-datos-para-consumo-fm.md) y [Task 1.5 · Skill 1.5.1](../domain-1/task-1-5-retrieval.md).

### Orquestar el procesamiento con Step Functions

Incluso con BDA gestionando la extracción, sigue haciendo falta el workflow de negocio alrededor:

```
Documento llega a S3
   │  notificación de evento
   ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step Functions Standard                                           │
│                                                                   │
│ ├─ Task: InvokeDataAutomationAsync con el ARN del proyecto        │
│ │     stage LIVE en producción, DEVELOPMENT para pruebas          │
│ │                                                                 │
│ ├─ Wait / Choice: sondear hasta que el job termine                │
│ │                                                                 │
│ ├─ Task: Lambda de validación de negocio                          │
│ │     · ¿campos obligatorios presentes?                           │
│ │     · ¿cuadran los totales?                                     │
│ │     · ¿el confidence score supera el umbral?                    │
│ │       (ojo: no existe en audio ni imagen)                       │
│ │                                                                 │
│ ├─ Choice: ¿confianza suficiente?                                 │
│ │     no ──► Task con .waitForTaskToken: revisión humana          │
│ │            · contexto completo: campos, scores, página          │
│ │            · HeartbeatSeconds para no colgarse                  │
│ │            · escalado a revisor secundario                      │
│ │            (patrón de Task 2.1 · Skill 2.1.5)                   │
│ │                                                                 │
│ ├─ Map: procesar cada documento individual si hubo splitting      │
│ │                                                                 │
│ ├─ Task: escribir en el sistema de negocio                        │
│ │     · idempotencia con escritura condicional en DynamoDB        │
│ │     · adaptador con taxonomía canónica de errores               │
│ │       (AGENTREL06, Task 2.3 · Skill 2.3.1)                      │
│ │                                                                 │
│ └─ Catch States.ALL ──► DLQ + notificación SNS                    │
└───────────────────────────────────────────────────────────────────┘
```

Por qué **Standard** y no Express: el workflow puede incluir espera humana (`.waitForTaskToken`, exclusivo de Standard) y las escrituras en el sistema de negocio **no son idempotentes por naturaleza**, así que la semántica **exactly-once** importa.

### Mejoras de CRM con Lambda

El patrón que nombra el skill, con las piezas ya establecidas:

| Mejora | Implementación |
| --- | --- |
| **Resumen de la interacción** | Webhook del CRM → API Gateway → Lambda → `Converse` → escribir el resumen de vuelta |
| **Clasificación y enrutado del caso** | Comprehend custom classification o un FM pequeño; el resultado alimenta la asignación |
| **Extracción de entidades del adjunto** | BDA con blueprint del tipo de documento, o Comprehend custom entity recognition |
| **Respuesta sugerida al agente** | RAG sobre la knowledge base de producto, con citas para que el agente verifique |
| **Enriquecimiento del registro** | Detectar sentimiento e intención y persistirlos como atributos |
| **Deduplicación** | Embeddings para detectar casos duplicados |
| **Sincronización** | AppFlow para el SaaS, EventBridge para el desacoplamiento |

Las consideraciones de integración, ya tratadas en [Task 2.3 · Skill 2.3.1](./task-2-3-integracion-empresarial.md#skill-231--conectividad-empresarial-y-acoplamiento-débil): **verificación de firma del webhook**, **responder rápido y procesar aparte** porque la ventana del webhook es corta, **idempotencia** porque los webhooks se reentregan, y **rate limiting en el adaptador** para no saturar el CRM con patrones de invocación agent-native.

> Y la advertencia que cierra el círculo con el resto del dominio: el contenido que llega del CRM (un ticket, un correo del cliente, un adjunto) es **contenido no confiable**. Puede traer prompt injection indirecta, y el guardrail de la invocación **no evalúa los resultados de herramienta** ([Skill 2.4.2](./task-2-4-integraciones-api-fm.md#guardrails-y-tool-use-lo-que-no-se-evalúa)). Validarlo aparte con `ApplyGuardrail`.

---

## Skill 2.5.4 — Productividad del desarrollador

> *Mejorar la productividad del desarrollador para acelerar los workflows de desarrollo de aplicaciones GenAI (por ejemplo, usando Amazon Q Developer para generar y refactorizar código, sugerencias de código para asistencia de API, testing de componentes de IA, optimización de rendimiento).*

### Amazon Q Developer

De [What is Amazon Q Developer?](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/what-is.html). Asistente conversacional impulsado por IA generativa que ayuda a entender, construir, extender y operar aplicaciones de AWS. Responde preguntas sobre arquitectura de AWS, recursos propios, best practices, documentación y soporte.

| Aspecto | Detalle |
| --- | --- |
| **Sobre qué está construido** | **Amazon Bedrock**, e incluye **detección automática de abuso implementada en Bedrock** para imponer seguridad y uso responsable de la IA |
| **Contenido del modelo** | El modelo que lo impulsa está **augmentado con contenido de AWS de alta calidad**, para dar respuestas más completas, accionables y **referenciadas** |
| **En el IDE** | Chat sobre código, **completions inline**, generación de código nuevo, escaneo de vulnerabilidades de seguridad, y upgrades y mejoras: actualizaciones de lenguaje, debugging y optimizaciones |
| **Planes** | Free tier y suscripción **Amazon Q Developer Pro** |

> **Aviso de fin de soporte, presente en la propia documentación oficial**: el **30 de abril de 2027 AWS discontinuará el soporte de los plugins de IDE de Amazon Q Developer**. Para capacidades similares, la documentación remite a **Kiro**, que da acceso a los modelos y funcionalidades más recientes, **incluidos agentic coding, chat y soporte de MCP**. Ver [Amazon Q Developer IDE plugins end of support](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/q-developer-ide-end-of-support.html).
>
> Kiro **figura en la lista de [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html)** del examen, en la categoría Developer Tools, y el [Agentic AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html) lo describe como IDE agentic que acelera el desarrollo de agentes mediante **workflows spec-driven, steering files para estándares de equipo y hooks para comprobaciones automatizadas de calidad**. Discrepancia registrada en [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación).

### Code reviews: los seis tipos de problema

De [Reviewing code with Amazon Q Developer](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/code-reviews.html). Revisa el código base buscando **vulnerabilidades de seguridad y problemas de calidad** a lo largo del ciclo de desarrollo. Se puede revisar un código base entero (todos los ficheros del proyecto o workspace local), un único fichero, o habilitar **auto reviews** que evalúan el código a medida que se escribe.

> **Cómo se generan las revisiones**: están impulsadas **tanto por IA generativa como por automatic reasoning basado en reglas**. Los [Amazon Q detectors](https://docs.aws.amazon.com/codeguru/detector-library), informados por años de best practices de seguridad de AWS y Amazon.com, alimentan las revisiones basadas en reglas. **A medida que las políticas de seguridad se actualizan y se añaden detectores, las revisiones los incorporan automáticamente.**

| Tipo de problema | Qué detecta |
| --- | --- |
| **SAST scanning** | Vulnerabilidades de seguridad en el código fuente: fugas de recursos, **SQL injection**, cross-site scripting |
| **Secrets detection** | Exposición de información sensible: **contraseñas hardcodeadas, cadenas de conexión a base de datos y nombres de usuario**. Los hallazgos incluyen información sobre el secreto desprotegido y cómo protegerlo |
| **IaC issues** | Evalúa la postura de seguridad de los ficheros de **infraestructura como código**: misconfiguración, compliance y seguridad |
| **Code quality issues** | Calidad, mantenibilidad y eficiencia: rendimiento, **reglas de machine learning** y best practices de AWS |
| **Code deployment risks** | Riesgos de desplegar o liberar el código, incluidos rendimiento de la aplicación y **disrupción de operaciones** |
| **Software composition analysis (SCA)** | Componentes, librerías, frameworks y dependencias de terceros integrados en el código, para asegurar que son seguros y están actualizados |

**Cómo decide qué revisar**, que es un detalle práctico que evita sorpresas:

```
Antes de revisar, Q aplica FILTRADO y excluye:
  · lenguajes no soportados
  · código de test
  · código open source

Por defecto, si solo pides "revisa mi código":
  · revisa SOLO los cambios del fichero activo en el IDE
  · los cambios se determinan por la salida de `git diff`
  · si no hay diff → revisa el fichero completo
  · si no hay fichero abierto → busca cambios en el proyecto

Si pides revisar el proyecto o workspace entero:
  · primero intenta revisar tus cambios
  · si no hay diff → revisa el código base completo
```

**Cuotas de los escaneos**, distinguiendo dos magnitudes: el *input artifact size* (tamaño máximo de todos los ficheros del workspace, **incluidas librerías de terceros, JARs de build y ficheros temporales**) y el *source code size* (tamaño máximo del código fuente que se escanea **tras filtrar** librerías de terceros y ficheros no soportados):

| Recurso | **Auto reviews** | **Revisiones de fichero o proyecto** |
| --- | --- | --- |
| **Input artifact size** | 200 KB | **500 MB** |
| **Source code size** | 200 KB | **50 MB** |

> La diferencia de tres órdenes de magnitud explica por qué las auto reviews son continuas y las de proyecto son puntuales: las primeras están dimensionadas para el fichero en el que estás trabajando.

### Transformaciones de código

Amazon Q Developer puede transformar código, con documentación tanto de la experiencia en IDE como de la **línea de comandos** ([transformaciones por CLI](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/transform-CLI.html), con la herramienta `qct` y comandos como `qct transform resume`). El flujo documentado en [How Amazon Q Developer transforms code for Java language upgrades](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/how-CT-works.html) incluye construir el código y crear un **plan de transformación**, transformar, **construir el código en el entorno local** para verificar, y revisar el resumen antes de aceptar los cambios, con soporte para completar transformaciones parcialmente exitosas. Se puede aportar un **fichero YAML de dependencias** para upgrades dirigidos de librerías.

> **Best practice de seguridad que documenta AWS** para las transformaciones: **evitar incluir artefactos externos no verificados en el repositorio del proyecto, y validar siempre el código transformado tanto en funcionalidad como en seguridad.** Es el mismo principio de contenido no confiable que recorre todo el dominio, aplicado al código generado.

### Qué significa "testing de componentes de IA" y "optimización de rendimiento"

El skill nombra las dos cosas junto a la generación de código. La traducción a lo que AWS documenta:

| Necesidad del skill | Herramienta documentada |
| --- | --- |
| **Generar y refactorizar código** | Q Developer: chat, completions inline, generación de código nuevo, transformaciones. Kiro para workflows spec-driven |
| **Asistencia de API** | Q Developer con contenido de AWS augmentado y respuestas referenciadas; y el modelo del SDK para las operaciones de Bedrock Runtime |
| **Testing de componentes de IA** | **Bedrock evaluations** (automática, judge model, humana, RAG evaluation), **AgentCore Evaluations** sobre sesiones, traces y spans, y el pipeline de QA de prompts de [Task 1.6 · Skill 1.6.4](../domain-1/task-1-6-prompt-engineering-governance.md) |
| **Optimización de rendimiento** | El escaneo de code quality de Q Developer para el código; **AgentCore Optimization** para el agente, con recomendaciones generadas por IA, bundles de configuración versionados y **A/B testing vía traffic splitting en Gateway**; y las palancas de [Task 2.2 · Skill 2.2.3](./task-2-2-despliegue-de-modelos.md#skill-223--despliegue-optimizado-y-model-cascading) |

### El toolchain del desarrollador GenAI

```
ESCRIBIR       Kiro: spec-driven, steering files, hooks
               Amazon Q Developer: chat, completions, generación
                 (plugins de IDE con EOS el 2027-04-30)
                  │
REVISAR        Q Developer code reviews
               SAST · secrets · IaC · calidad · riesgo de despliegue · SCA
               auto reviews (200 KB) vs proyecto (500 MB / 50 MB)
                  │
PROBAR         Bedrock evaluations: automática · judge · humana · RAG
               AgentCore Evaluations: sesiones, traces, spans
               Lambda para aserciones deterministas
               Step Functions para orquestar el set de regresión
               FIS para validar cadenas de fallback
                  │
ENTREGAR       CodePipeline con stage conditions
               CodeBuild para build y security scans
               CloudFormation / CDK para la infraestructura
               rollback por AppConfig, versiones de AgentCore, CodeDeploy
                  │
OPTIMIZAR      AgentCore Optimization: recomendaciones + A/B testing
               prompt caching · cascada · tier adecuado
```

---

## Skill 2.5.5 — Aplicaciones GenAI avanzadas

> *Desarrollar aplicaciones GenAI avanzadas para implementar capacidades de IA sofisticadas (por ejemplo, usando Strands Agents y AWS Agent Squad para orquestación nativa de AWS, Step Functions para orquestar patrones de diseño de agente, Amazon Bedrock para gestionar patrones de prompt chaining).*

### Los tres niveles de sofisticación

Este skill es en buena medida una recapitulación del Task 2.1 desde la perspectiva de la aplicación. Los tres niveles que nombra, de menos a más:

| Nivel | Qué es | Dónde está el detalle |
| --- | --- | --- |
| **Prompt chaining** | La salida de una invocación alimenta la siguiente, en una secuencia determinada por el diseño | [Task 1.6 · Skill 1.6.6](../domain-1/task-1-6-prompt-engineering-governance.md) con Bedrock Flows |
| **Patrones de agente** | El modelo decide qué paso dar: elige herramienta, observa, reevalúa | [Task 2.1 · Skill 2.1.2](./task-2-1-agentic-ai-y-herramientas.md#skill-212--razonamiento-estructurado-y-descomposición-de-problemas) con Step Functions |
| **Multi-agente** | Varios agentes especializados colaboran, con árbitro, taxonomía de capacidades y cadenas de fallback | [Task 2.1 · Skill 2.1.1](./task-2-1-agentic-ai-y-herramientas.md#coordinación-multi-agente-el-marco-oficial) con AGENTREL04 |

### Prompt chaining sobre Bedrock

Las dos formas documentadas de encadenar:

| Forma | Mecanismo | Cuándo |
| --- | --- | --- |
| **Bedrock Flows** | Prompt nodes conectados, con prompts versionados de Prompt Management, knowledge base nodes, condiciones y nodos de Lambda | Cadena conocida de antemano; constructor visual; despliegue con versiones y alias |
| **Step Functions** | Un `Task` por eslabón, con `Pass` para transformar entre pasos | Hace falta reintento por paso, timeout por paso, espera humana o historial de ejecución |

La diferencia práctica entre prompt chaining y un patrón de agente: en el chaining **la secuencia la decide el diseñador**; en el patrón de agente **la decide el modelo** en cada iteración. Eso cambia lo que hay que acotar: una cadena tiene un número fijo de pasos, un agente necesita **stopping conditions**, presupuesto de iteraciones y de tokens, como se detalla en [Task 2.1 · Skill 2.1.3](./task-2-1-agentic-ai-y-herramientas.md#capa-determinista-1-stopping-conditions-en-step-functions).

### Patrones de diseño de agente sobre Step Functions

Los patrones que se pueden expresar con los estados de Amazon States Language, todos ya desarrollados en el Task 2.1:

| Patrón | Estados que lo implementan |
| --- | --- |
| **ReAct** (razonar, actuar, observar) | `Task` de inferencia → `Choice` sobre `stopReason` → `Task` de herramienta → `Pass` que acumula → vuelta |
| **Chain-of-thought explícito** | Un `Task` por paso de razonamiento, con la salida de cada uno como entrada del siguiente |
| **Descomposición paralela** | `Map` sobre las sub-preguntas independientes, o `Parallel` para ramas heterogéneas |
| **Ensemble con agregación** | `Parallel` con un modelo por rama, más una Lambda de agregación |
| **Cascada** | `Choice` sobre la confianza, escalando al modelo siguiente |
| **Arbiter** | Un `Task` de árbitro que se invoca solo cuando hay conflicto; event-driven con EventBridge en el nivel 4 de AGENTREL04 |
| **Human-in-the-loop** | `Task` con `.waitForTaskToken` y `HeartbeatSeconds` (solo Standard) |
| **Circuit breaker** | `Choice` sobre el estado del disyuntor en DynamoDB, con sonda de recuperación |

> Recordatorio de las dos restricciones que más condicionan el diseño: **Express solo soporta Request Response**, así que cualquier patrón con espera humana o `.sync` exige **Standard**; y en Standard **cada transición de estado se factura, incluidos los reintentos**.

### Sobre Strands Agents y AWS Agent Squad

El skill nombra los dos frameworks como vía de "orquestación nativa de AWS". Lo que puede afirmarse desde `docs.aws.amazon.com`:

| Framework | Qué dice el portal de AWS |
| --- | --- |
| **Strands Agents** | El [Agentic AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html) lo describe como framework **open source model-driven** con soporte nativo de **herramientas MCP, protocolo A2A y patrones multi-agente (Graph, Swarm y Workflow)**, compatible con Bedrock, Anthropic, OpenAI, Ollama y otros proveedores. [AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html) lo lista entre los frameworks soportados por su SDK de Python, junto a LangGraph y CrewAI. [AgentCore Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html) y [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) documentan integración con él. **No existe guía de servicio propia en el portal**, y no aparece en la lista de In-Scope AWS Services |
| **AWS Agent Squad** | **No tiene ninguna página en `docs.aws.amazon.com`**, ni aparece en la lista de In-Scope AWS Services |

**Cómo estudiar estos skills sin la documentación que la guía presupone**: el sustrato que AWS sí documenta cubre las mismas responsabilidades.

| Responsabilidad del framework | Servicio documentado que la cubre |
| --- | --- |
| Ejecutar el agent loop | **AgentCore Harness** (agent loop gestionado, invocable con una sola llamada de API) o **Step Functions** |
| Alojar el agente | **AgentCore Runtime** (microVM por sesión, versiones inmutables, endpoints por entorno) |
| Conectar herramientas | **AgentCore Gateway** (MCP, HTTP e inference targets) y el tool use de Bedrock |
| Recordar | **AgentCore Memory** (short-term, long-term con cuatro estrategias) |
| Autenticar | **AgentCore Identity** (workload identities, token vault, OAuth 2LO y 3LO) |
| Acotar | **AgentCore Policy** (Cedar, intercepta cada tool call en el Gateway) |
| Coordinar varios agentes | El patrón **arbiter** de AGENTREL04, con EventBridge, Step Functions y **AWS Agent Registry** |
| Observar | **AgentCore Observability** (OTEL) y **AgentCore Evaluations** |
| Descubrir | **AWS Agent Registry** (hybrid search, endpoint MCP nativo, workflow de aprobación) |

Detalle registrado en [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación).

---

## Skill 2.5.6 — Troubleshooting de aplicaciones de FM

> *Mejorar la eficiencia del troubleshooting para aplicaciones de FM (por ejemplo, usando CloudWatch Logs Insights para analizar prompts y respuestas, X-Ray para trazar llamadas a la API de FM, Amazon Q Developer para implementar reconocimiento de patrones de error específicos de GenAI).*

### La fuente: model invocation logging

De [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html). Permite recoger **logs de invocación, datos de entrada y datos de salida del modelo** para todas las invocaciones de la cuenta en una Región, con los **datos completos de petición y respuesta más los metadatos**.

| Aspecto | Detalle |
| --- | --- |
| **Estado inicial** | **Deshabilitado por defecto**. Una vez habilitado, **los logs se almacenan hasta que se elimine la configuración de logging** |
| **Destinos** | **CloudWatch Logs** y **Amazon S3**. **Solo destinos de la misma cuenta y Región** |
| **Operaciones que registran** | `Converse`, `ConverseStream`, `InvokeModel`, `InvokeModelWithResponseStream` |
| **Endpoint** | **Solo llamadas por el endpoint `bedrock-runtime`**, incluidas las APIs Responses y Chat Completions compatibles con OpenAI en ese endpoint. Las llamadas por otros endpoints, **como las mismas APIs en `bedrock-mantle`, no se capturan** |
| **Imágenes y documentos** | Con la Converse API, las imágenes y documentos que se pasan **se registran en S3** si se habilita la entrega y el logging de imágenes en S3 |
| **Cifrado** | Si se configura SSE-KMS en el bucket hay que añadir una política a la clave que permita `kms:GenerateDataKey` al principal `bedrock.amazonaws.com`, con condiciones de `aws:SourceAccount` y `aws:SourceArn` |
| **Requisito del bucket** | **La ACL del bucket debe estar deshabilitada** para que la política de bucket surta efecto |

> El hueco a tener presente: **lo que va por `bedrock-mantle` no aparece en los invocation logs**. Y recordar de [Skill 2.5.1](#skill-251--interfaces-de-api-para-cargas-genai) que algunos modelos Claude requieren `bedrock-mantle` para contar tokens. Son dos superficies distintas con observabilidad distinta.

El campo **`requestMetadata`** de la petición es lo que convierte el log en herramienta de análisis: etiqueta cada invocación con metadatos de negocio (tenant, caso de uso, versión de prompt) **filtrables después en los logs**. Base en [Task 1.6 · Skill 1.6.3](../domain-1/task-1-6-prompt-engineering-governance.md).

### CloudWatch Logs Insights

De [Analyzing log data with CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html). Permite buscar y analizar interactivamente los datos de log. Además de consultar por log groups, se puede consultar usando **facets, data source y data type**. Ante una incidencia sirve para **identificar causas potenciales y validar las correcciones desplegadas**.

**Los tres lenguajes de consulta:**

| Lenguaje | Características |
| --- | --- |
| **Logs Insights QL** | Lenguaje propósito-específico, con **comandos pocos pero potentes** |
| **OpenSearch PPL** | Comandos delimitados por **pipes (`|`)**, encadenables para transformar y procesar datos. Filtrado, agregación y funciones matemáticas, de string, de fecha y condicionales |
| **OpenSearch SQL** | Análisis declarativo con `SELECT`, `FROM`, `WHERE`, `GROUP BY`, `HAVING`. Permite **`JOIN` entre log groups**, correlacionar datos con subconsultas, y funciones JSON, matemáticas, de string y condicionales |

> Con SQL o PPL, **los campos con caracteres especiales deben encerrarse en backticks** para poder consultarlos: `` `@message` ``, `` `Operation.Export` ``, `` `Test::Field` ``. Los nombres puramente alfabéticos no lo necesitan.

**Límites de concurrencia y de ejecución:**

| Límite | Valor |
| --- | --- |
| Consultas concurrentes de **Logs Insights QL** por cuenta | **100**, incluidas las añadidas a dashboards |
| Consultas concurrentes de **PPL o SQL** | **15** |
| **Timeout** de una consulta | **60 minutos** |
| **Disponibilidad de resultados** | **7 días** |
| **Coste** | Basado en la cantidad de **datos de log sin comprimir escaneados** |

**Funcionalidades disponibles con cualquier lenguaje:**

| Funcionalidad | Qué aporta en troubleshooting de GenAI |
| --- | --- |
| **Descubrimiento automático de campos** | En logs de servicios de AWS (Route 53, Lambda, CloudTrail, VPC) y **en cualquier log propio que emita eventos como JSON**, que es el caso de los invocation logs |
| **Field indexes** | **Reducen coste y aceleran resultados**: la consulta salta los eventos que no incluyen el campo indexado y procesa menos datos. Indexar por `modelId`, tenant o versión de prompt. El comando `filterIndex` existe **solo en Logs Insights QL** |
| **Detección de patrones** | Un patrón es una **estructura de texto compartida que recurre** entre los campos. La pestaña **Patterns** los muestra sobre una muestra de los resultados |
| **Guardar consultas** | Historial, reejecución y **consultas guardadas con parámetros** |
| **Consultas en dashboards** | Convertir la consulta en un panel permanente |
| **Cifrado de resultados con KMS** | Relevante cuando los prompts contienen datos sensibles |
| **Generación de consultas en lenguaje natural** | Describir los datos buscados y obtener la consulta generada **con explicación línea a línea** de cómo funciona |
| **Facets** | Agrupar, filtrar y explorar interactivamente |
| **Surrounding logs** | Ver **5, 10, 20, 50 o 100 líneas antes y después** de un registro concreto, con búsqueda de keywords dentro del contexto |
| **Comparison queries** (solo QL) | Comparar eventos de un log group **con los de un periodo anterior**: la forma directa de detectar una regresión tras desplegar una versión de prompt |

Dos avisos oficiales: **Logs Insights no puede acceder a eventos con timestamps anteriores a la creación del log group**; y desde una **cuenta de monitorización** de CloudWatch cross-account observability se pueden consultar log groups de cuentas de origen enlazadas, **incluso varias cuentas en una sola consulta**.

### AgentCore Observability

De [Observe your agent applications on Amazon Bedrock AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html). Permite trazar, depurar y monitorizar el rendimiento de los agentes en producción, con **visualizaciones detalladas de cada paso del workflow** para inspeccionar la ruta de ejecución, **auditar salidas intermedias** y depurar cuellos de botella y fallos.

| Aspecto | Detalle |
| --- | --- |
| **Métricas clave** | **Session count, latencia, duración, uso de tokens y tasas de error** |
| **Formato** | Telemetría en formato estandarizado **OpenTelemetry (OTEL)**, integrable con el stack de monitorización existente |
| **Almacenamiento** | **Todas las métricas, spans y logs se almacenan en Amazon CloudWatch**, visibles en la consola o descargables por CLI y SDKs |
| **Dashboard** | Para datos de **agent runtime**, la consola de CloudWatch ofrece un dashboard de observabilidad con **visualizaciones de trazas, gráficas de métricas de span personalizadas y desglose de errores** |
| **Metadatos** | **Etiquetado y filtrado ricos de metadatos** para simplificar la investigación de incidencias a escala |
| **Instrumentación propia** | Se puede instrumentar el código del agente para aportar **spans, trazas, métricas y logs personalizados** |

**Qué datos se generan por defecto y qué requiere habilitarse**, de [Amazon Bedrock AgentCore generated observability data](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-service-provided.html):

| Tipo de recurso | Datos que provee el servicio |
| --- | --- |
| **Agent** | Métricas, spans\*, logs\* |
| **Memory** | Métricas, spans\*, logs\* |
| **Payments** | Métricas, spans, logs |
| **Gateway** | Métricas, spans, logs\* |
| **Tools** | Métricas, spans\*, logs\* |
| **Policy** | Métricas, spans\*, logs |

Las señales marcadas con asterisco **requieren habilitación explícita**; **las métricas se proveen por defecto para todos los tipos de recurso**.

> **Requisito de setup que es fácil olvidar**: para ver métricas, spans y trazas de AgentCore hay que realizar **un proceso de configuración único para habilitar CloudWatch Transaction Search**.

Dos detalles más: se puede usar AgentCore Observability para monitorizar memory, gateway y built-in tools **incluso si no se usa AgentCore Runtime para alojar los agentes**; y la observabilidad de **Policy se muestra bajo la pestaña de AgentCore Gateway** en la página de gen AI observability de CloudWatch.

### Tabla de troubleshooting: síntoma → señal → herramienta

| Síntoma | Señal a mirar | Herramienta |
| --- | --- | --- |
| **Latencia alta end-to-end** | Desglose por subsegmento: ¿retrieval, inferencia o herramienta? | **X-Ray** trace map y subsegmentos; **AgentCore Observability** para latencia y duración por paso |
| **Latencia percibida alta con latencia real normal** | Time-to-first-token; ¿está activo el streaming? | Anotaciones de X-Ray; AGENTPERF02 como referencia de diseño |
| **Pausas a mitad de respuesta** | Invocaciones de herramienta durante el stream sin eventos de progreso | Spans de AgentCore Observability |
| **Throttling (`429`, `ThrottlingException`)** | Métricas de throttle; ¿qué capa limita: usage plan, stage, cuenta o Bedrock? | Métricas de **CloudWatch**; orden de aplicación de throttling de [Skill 2.4.3](./task-2-4-integraciones-api-fm.md#rate-limiting-en-api-gateway) |
| **Coste subiendo sin más tráfico** | Tokens de entrada por invocación; ¿creció el system prompt o el catálogo de herramientas? | Campo `usage`, invocation logs filtrados por `requestMetadata`; problema frecuente de AGENTCOST02 |
| **Cache hit rate bajo** | Campos de cache usage de la respuesta; ¿el prefijo estático cambia entre peticiones? | Respuesta del modelo; ver [Task 2.2 · Skill 2.2.3](./task-2-2-despliegue-de-modelos.md#reducir-el-coste-sin-cambiar-de-modelo-prompt-caching) |
| **Respuesta vacía o truncada** | `stopReason`; ¿`max_tokens` o `stop_sequence`? | Invocation logs |
| **Bloqueo inesperado** | Traza del guardrail (`trace: enabled`) y qué política intervino | Invocation logs; métricas de intervención en CloudWatch |
| **Contenido inapropiado que se colara en streaming** | ¿`streamProcessingMode` en `ASYNCHRONOUS`? | Configuración de la petición; recordar que asíncrono **no soporta masking** |
| **Contenido problemático que el guardrail no vio** | ¿Venía en un `toolResult` o en `toolUse.input`? | El guardrail **no evalúa esos campos**; ver [Skill 2.4.2](./task-2-4-integraciones-api-fm.md#guardrails-y-tool-use-lo-que-no-se-evalúa) |
| **Alucinación** | Contextual grounding check; ¿el retrieval devolvió algo relevante? | Bedrock evaluations RAG; [Task 1.5](../domain-1/task-1-5-retrieval.md) |
| **Agente en bucle** | Contador de iteraciones, herramienta repetida con los mismos argumentos | Historial de ejecución de **Step Functions**; spans de AgentCore |
| **Herramienta que falla siempre** | Estado del disyuntor; ¿abrió y nunca cerró por falta de sonda? | DynamoDB de estado; problema frecuente 5 de AGENTREL06 |
| **Regresión tras desplegar un prompt** | Comparar el periodo actual con el anterior | **Comparison queries** de Logs Insights (solo QL); AgentCore Evaluations |
| **Drift de comportamiento** | Salidas más largas, más llamadas a herramienta, cambio en la distribución | **CloudWatch Anomaly Detection** sobre baselines; AGENTREL02-BP03 |
| **Región de procesamiento inesperada** | Campo `additionalEventData.inferenceRegion` | **CloudTrail** |
| **Cola de aprobación creciendo** | Profundidad de la cola | **CloudWatch**, según AGENTREL02-BP05 |
| **Endpoint caído sin aviso** | Comprobación sintética periódica | **CloudWatch Synthetics** |
| **No aparecen logs de una invocación** | ¿Fue por `bedrock-mantle` en lugar de `bedrock-runtime`? | El invocation logging **solo captura `bedrock-runtime`** |

### Consulta de ejemplo sobre los invocation logs

Una consulta de Logs Insights QL sobre los invocation logs, aprovechando el descubrimiento automático de campos JSON:

```
fields @timestamp, modelId, input.inputTokenCount, output.outputTokenCount
| filter requestMetadata.tenant = "acme"
| filter requestMetadata.promptVersion = "v7"
| stats avg(output.outputTokenCount) as avgOut,
        sum(input.inputTokenCount)  as totalIn,
        count(*)                    as invocations
        by modelId
| sort totalIn desc
```

Con **field indexes** sobre `modelId` y `requestMetadata.tenant`, la consulta procesa menos datos y cuesta menos, porque **salta los eventos que no incluyen el campo indexado**.

### El reconocimiento de patrones de error que nombra el skill

El skill menciona Amazon Q Developer para "reconocimiento de patrones de error específicos de GenAI". Las dos capacidades documentadas que lo materializan, ambas con IA generativa:

| Capacidad | Dónde |
| --- | --- |
| **Detección de patrones en los logs** | La pestaña **Patterns** de Logs Insights, que identifica estructuras de texto recurrentes entre los campos |
| **Generación de consultas en lenguaje natural** | Describir lo que se busca y obtener la consulta **con explicación línea a línea**, en [Use natural language to generate and update CloudWatch Logs Insights queries](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatchLogs-Insights-Query-Assist.html) |

Complementadas por el chat de Q Developer sobre recursos de AWS y su escaneo de calidad y seguridad del código, con la salvedad del fin de soporte de los plugins de IDE el **30 de abril de 2027** y la remisión oficial a **Kiro**.

### Las capas de observabilidad del dominio, en una vista

```
CÓDIGO         Q Developer code reviews (SAST, secrets, IaC, calidad, SCA)
                  │
PETICIÓN       X-Ray: trace map, segmentos y subsegmentos
               anotaciones: modelId, tokens, stopReason, tier, cache hit
                  │
INVOCACIÓN     Model invocation logging → CloudWatch Logs y S3
               requestMetadata como dimensión filtrable
               SOLO bedrock-runtime, no bedrock-mantle
                  │
AGENTE         AgentCore Observability (OTEL) → CloudWatch
               métricas por defecto; spans y logs requieren habilitarse
               requiere habilitar CloudWatch Transaction Search (una vez)
               dashboard de gen AI observability para agent runtime
                  │
ANÁLISIS       CloudWatch Logs Insights
               QL (100 concurrentes) · PPL y SQL (15 concurrentes)
               field indexes · patterns · surrounding logs
               comparison queries (solo QL) para detectar regresiones
               generación de consultas en lenguaje natural
                  │
CALIDAD        Bedrock evaluations · AgentCore Evaluations
               CloudWatch Anomaly Detection sobre baselines por agente
                  │
AUDITORÍA      CloudTrail: management events, inferenceRegion
               logs de decisiones de AgentCore Policy
                  │
EXTERIOR       CloudWatch Synthetics · Managed Grafana
```
