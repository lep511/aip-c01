# Task 2.2 — Estrategias de despliegue de modelos

[← Volver al índice](./README.md)

Skills cubiertos: **2.2.1**, **2.2.2**, **2.2.3**.

---

## Skill 2.2.1 — Desplegar FMs según necesidades y requisitos de rendimiento

> *Desplegar FMs según necesidades específicas de la aplicación y requisitos de rendimiento (por ejemplo, usando funciones Lambda para invocación on-demand, configuraciones de Provisioned Throughput de Amazon Bedrock, endpoints de SageMaker AI para implementar soluciones híbridas).*

### Las seis opciones de capacidad de Amazon Bedrock

De [Capacity and Performance](https://docs.aws.amazon.com/bedrock/latest/userguide/capacity-limits-cost-optimization.html). Bedrock ofrece opciones flexibles de capacidad para ajustar carga de trabajo y presupuesto. Entender las diferencias entre los tiers on-demand, el reserved tier, el procesamiento batch y la inferencia cross-Region es lo que permite optimizar rendimiento y coste a la vez.

| Tipo de capacidad | Caso de uso | Características |
| --- | --- | --- |
| **On-Demand: Flex** | Cargas esporádicas y de bajo volumen | Coste por token **más bajo**; disponibilidad best-effort; **puede sufrir throttling**; **sin SLA** |
| **On-Demand: Standard** | Cargas de producción regulares | Balance coste/rendimiento; garantías moderadas de throughput; SLA estándar; **la elección más común** |
| **On-Demand: Priority** | Aplicaciones de alta prioridad y sensibles a latencia | Coste on-demand **más alto**; asignación premium de throughput; SLA mejorado; **riesgo reducido de throttling** |
| **Reserved Tier** | Cargas consistentes de alto volumen | **Model units reservadas**; capacidad garantizada; compromisos de **1 o 3 meses**; rendimiento predecible |
| **Batch** | Procesamiento a gran escala no sensible al tiempo | **50 % de ahorro** frente a on-demand; ventana de procesamiento de **24 horas**; ideal para inferencia masiva |
| **Cross-Region Inference** | Cargas que pueden procesarse fuera de una sola Región | Enruta peticiones entre las Regiones del inference profile; **reduce costes de token en algunos modelos con perfiles globales**; usa precios on-demand |

### Límites y cuotas por tier

| Tier | Rango RPM | Rango TPM | Riesgo de throttling |
| --- | --- | --- | --- |
| **Flex** | 10–100 | 5K–50K | **Alto** |
| **Standard** | 100–500 | 50K–150K | Medio |
| **Priority** | 500–1000+ | 150K–300K+ | **Bajo** |

Notas oficiales sobre estos límites: hay **burst capacity** disponible en todos los tiers para picos cortos; son **soft limits**, ampliables por petición de service quota; y los límites reales **varían según el modelo**.

| Otros límites | Valor |
| --- | --- |
| **Reserved tier** | Compromiso mínimo de **1 model unit**; máximo específico de cuenta y Región; límites de tokens de entrada/salida según las unidades compradas; **sin throttling de RPM dentro de la capacidad comprada** |
| **Batch** | Hasta **10.000 registros** por batch; fichero de entrada de **máximo 200 MB**; ventana de finalización de **24 horas**; jobs concurrentes con cuotas por Región |
| **Cross-Region inference** | **Hereda los límites del tier on-demand por Región**; sin overhead de cuota adicional; routing automático sin gestión manual de límites |

### El framework de decisión oficial

| Escenario | Opción recomendada | Por qué |
| --- | --- | --- |
| Desarrollo y testing | **Flex** | Coste más bajo, aceptable para no producción |
| Producción estándar | **Standard** | Mejor balance coste/rendimiento |
| Aplicaciones críticas de cara al usuario | **Priority** | Fiabilidad y rendimiento por encima del coste |
| Carga alta y estable | **Reserved Tier** | **30–50 % de ahorro** con compromiso |
| Procesamiento masivo de datos | **Batch** | **50 % de descuento**, cargas no urgentes |
| Uptime de misión crítica | **Cross-Region Inference** | Disponibilidad por encima de coste |

### Estrategias de optimización que documenta AWS

**Elegir el tier on-demand correcto**: empezar con **Standard** para la mayoría de cargas, bajar a **Flex** en entornos de dev y test, y **subir a Priority solo cuando el throttling afecta a los usuarios**. Monitorizar las métricas de throttle de CloudWatch para informar la decisión.

**Transición al Reserved Tier**: cuando la carga consistente excede el **40 % de los costes on-demand**. Calcular el punto de equilibrio comparando el coste mensual on-demand con el compromiso reservado. Empezar con el compromiso de **1 mes**. El reserved tier **puede funcionar junto a cualquier tier on-demand**.

**Usar Batch para**: generación de datos de entrenamiento, colas pendientes de moderación de contenido, generación de informes y pipelines de enriquecimiento de datos.

**Combinar enfoques**, que es la respuesta que el examen probablemente premia frente a elegir una sola opción:

```
Reserved tier            → tráfico base
Standard on-demand       → picos moderados
Priority on-demand       → periodos de pico críticos
Batch                    → procesamiento offline
Cross-Region inference   → cargas que pueden procesarse fuera de una Región
```

**Monitorización de coste**: comparar costes por tier (Flex < Standard < Priority), rastrear tokens por petición, usar métricas de CloudWatch de uso y throttling, fijar alarmas de facturación ante picos inesperados, revisar el uso del reserved tier mensualmente, y **evaluar subidas de tier solo cuando ocurre throttling**.

### Provisioned Throughput: el modelo de model units

De [Increase model invocation capacity with Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html). *Throughput* es el número y la tasa de entradas y salidas que un modelo procesa y devuelve. Provisioned Throughput aprovisiona un nivel más alto de throughput para un modelo **a coste fijo**.

> **Dato decisivo**: si personalizaste un modelo, **debes comprar Provisioned Throughput para poder usarlo**. No hay opción on-demand para modelos personalizados (con la excepción de Custom Model Import, que se ve más abajo).

La facturación es **por hora**, y el precio depende de tres factores:

| Factor | Detalle |
| --- | --- |
| **El modelo elegido** | Para modelos personalizados, el precio es el mismo que el del modelo base del que se personalizó |
| **El número de Model Units (MUs)** | Una MU entrega un nivel específico de throughput para el modelo indicado: el número de **tokens de entrada** que puede procesar en todas las peticiones dentro de un minuto, y el número de **tokens de salida** que puede generar en todas las peticiones dentro de un minuto |
| **La duración del compromiso** | Cuanto más largo, más descuento en el precio por hora |

Los tres niveles de compromiso:

| Compromiso | Restricción |
| --- | --- |
| **Sin compromiso** | Se puede eliminar el Provisioned Throughput en cualquier momento |
| **1 mes** | No se puede eliminar hasta que termine el plazo de un mes |
| **6 meses** | No se puede eliminar hasta que termine el plazo de seis meses |

> **La facturación continúa hasta que eliminas el Provisioned Throughput.** No basta con dejar de invocarlo.

El proceso oficial: determinar cuántas MUs comprar y para cuánto tiempo comprometerse, comprar el Provisioned Throughput para un modelo base o personalizado, y usar el modelo aprovisionado para ejecutar inferencia.

> Ojo con la discrepancia de plazos entre páginas: la página de capacidad describe el **reserved tier** con compromisos de **1 o 3 meses**, mientras que la de Provisioned Throughput lista **sin compromiso, 1 mes y 6 meses**. Son dos páginas oficiales con vocabulario distinto sobre capacidad reservada; conviene conocer ambos conjuntos de cifras y no fiarse de una sola. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación).

### Las opciones de inferencia de SageMaker AI

De [Deploy models for inference](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html). SageMaker AI ofrece varias opciones de inferencia: endpoints en tiempo real para latencia baja, endpoints serverless para infraestructura totalmente gestionada con auto-scaling, y endpoints asíncronos para lotes de peticiones.

**Los tres casos de uso y la herramienta recomendada para cada uno:**

| | **Caso 1** | **Caso 2** | **Caso 3** |
| --- | --- | --- | --- |
| Perfil | Desplegar en entorno low-code o no-code | Desplegar con más flexibilidad y control usando código | Desplegar a escala |
| Herramienta | **JumpStart en Studio** | **`ModelBuilder`** del SageMaker Python SDK | **CloudFormation** con Boto3, IaC y CI/CD |
| Optimizado para | Despliegues rápidos de modelos open source populares | Desplegar tus propios modelos | Gestión continua de modelos en producción |
| Consideración | **Falta de personalización** de ajustes de contenedor y necesidades específicas | Sin UI; requiere desarrollar y mantener código Python | Requiere gestión de infraestructura y familiaridad con Boto3 o plantillas de CloudFormation |
| Entorno | Un dominio de SageMaker AI | Entorno Python con credenciales y el SDK, o un IDE como SageMaker JupyterLab | AWS CLI, entorno local, herramientas de IaC y CI/CD |

**Las tres modalidades de endpoint:**

| Modalidad | Perfil | Límites y características |
| --- | --- | --- |
| **[Real-time inference](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html)** | Cargas interactivas con requisitos de latencia baja | Instancias siempre activas |
| **[Serverless Inference](https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html)** | Sin configurar ni gestionar infraestructura | Ideal para cargas con **periodos de inactividad entre ráfagas de tráfico** y que **toleran cold starts** |
| **[Asynchronous inference](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html)** | Encola las peticiones entrantes y las procesa de forma asíncrona | Payloads grandes (**hasta 1 GB**), tiempos de procesamiento largos (**hasta una hora**), latencia casi en tiempo real |

**Cómo funciona el asíncrono**, que es la modalidad con más mecánica propia: se crea igual que un endpoint en tiempo real, especificando el objeto **`AsyncInferenceConfig`** en `CreateEndpointConfig`. Para invocarlo hay que **colocar el payload en Amazon S3** y pasar un puntero a ese payload en la petición **`InvokeEndpointAsync`**. SageMaker AI encola la petición y devuelve un identificador y la ubicación de salida; al procesarla, deja el resultado en la ubicación de S3. Opcionalmente se reciben notificaciones de éxito o error con **Amazon SNS**.

Dos avisos oficiales del asíncrono: la presencia del objeto `AsyncInferenceConfig` en la configuración del endpoint implica que **el endpoint solo puede recibir invocaciones asíncronas**; y permite ahorrar costes **escalando el número de instancias a cero** cuando no hay peticiones, de modo que solo se paga cuando el endpoint procesa.

**Opciones de optimización de coste** que documenta la misma página: [SageMaker Neo](https://docs.aws.amazon.com/sagemaker/latest/dg/neo.html) para optimizar modelos con mejor rendimiento y eficiencia, minimizando coste de cómputo al optimizarlos automáticamente para entornos como chips **AWS Inferentia**; y [automatic scaling](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling.html) para ajustar dinámicamente los recursos de cómputo según los patrones de tráfico entrante.

### Lambda como capa de invocación

El skill nombra Lambda para invocación on-demand. Los límites de [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) que condicionan el diseño están detallados en [Task 2.1 · Skill 2.1.3](./task-2-1-agentic-ai-y-herramientas.md#skill-213--workflows-con-salvaguardas-y-comportamiento-controlado). Los tres que más importan aquí:

| Límite | Consecuencia de diseño |
| --- | --- |
| **Timeout de 900 s (15 min)** | Una generación larga o un bucle de razonamiento no caben. Alternativas: Step Functions Standard, AgentCore Runtime o ECS |
| **Payload de 6 MB** de petición y respuesta sincrónicas | Documentos grandes van por S3 con referencia, no en el body |
| **200 MB por respuesta en streaming**, sin límite de banda los primeros 6 MB y **2 MB/s** después | El streaming de tokens cabe holgadamente; el cuello de botella no es Lambda |

El patrón habitual es Lambda como capa fina: valida, resuelve configuración (modelo, prompt, guardrail), invoca Bedrock, normaliza la respuesta y registra métricas. La lógica de resiliencia y routing se trata en [Task 2.4](./task-2-4-integraciones-api-fm.md).

### La tabla de decisión completa

| | **Bedrock on-demand** | **Bedrock Provisioned Throughput** | **Bedrock Batch** | **SageMaker real-time** | **SageMaker serverless** | **SageMaker async** |
| --- | --- | --- | --- | --- | --- | --- |
| **Latencia** | Baja, variable con throttling según tier | Baja y **predecible** | Ventana de **24 h** | Baja y consistente | Baja con **cold starts** | Minutos, **hasta 1 h** |
| **Throughput** | RPM/TPM del tier, soft limits | **Garantizado** por model units | Masivo | Según instancias y auto scaling | Automático | Encolado |
| **Coste** | Por token; Flex < Standard < Priority | **Por hora**, fijo, con descuento por compromiso | **50 % menos** que on-demand | Por instancia-hora, siempre activo | Por uso | Por uso, **escala a cero** |
| **Control del modelo** | Modelos de Bedrock | Modelos de Bedrock, incluidos personalizados | Modelos de Bedrock | **Cualquier modelo y contenedor** | Cualquier modelo (con restricciones) | Cualquier modelo |
| **Payload** | Límites de la API de Bedrock | Ídem | 200 MB de fichero, 10.000 registros | Límites del endpoint | Ídem | **Hasta 1 GB vía S3** |
| **Cuándo** | Producción general, prototipado | Modelos personalizados, carga estable alta, latencia predecible | Enriquecimiento, informes, datos de entrenamiento | Modelo propio con latencia baja | Tráfico intermitente que tolera cold start | Payloads grandes o procesado largo |

**Soluciones híbridas**, que es lo que pide literalmente el skill: la combinación habitual es Bedrock para los FMs gestionados y SageMaker AI para el modelo propio o afinado que Bedrock no ofrece, detrás de una fachada común. Esa fachada es la capa de abstracción del [Skill 2.3.5](./task-2-3-integracion-empresarial.md#skill-235--cicd-y-arquitecturas-de-genai-gateway), y AgentCore Gateway la materializa con **inference targets** que enrutan por el campo `model` de la petición, como se vio en [Task 2.1 · Skill 2.1.6](./task-2-1-agentic-ai-y-herramientas.md#skill-216--integraciones-de-herramientas-y-operaciones-fiables).

---

## Skill 2.2.2 — Retos propios de los LLMs frente a despliegues ML tradicionales

> *Desplegar soluciones de FM abordando los retos únicos de los large language models (LLMs) que difieren de los despliegues ML tradicionales (por ejemplo, implementando patrones de despliegue basados en contenedor optimizados para requisitos de memoria, utilización de GPU y capacidad de procesamiento de tokens; siguiendo estrategias especializadas de carga de modelo).*

### Qué cambia respecto a un modelo ML clásico

| Dimensión | ML tradicional | LLM |
| --- | --- | --- |
| **Tamaño del artefacto** | MB a pocos GB | Decenas o cientos de GB; cientos de miles de millones de parámetros |
| **Tiempo de carga** | Segundos | Minutos, dominado por descarga y descompresión |
| **Acelerador** | Opcional | **GPU o acelerador dedicado**, con la memoria del acelerador como restricción dura |
| **Unidad de trabajo** | Una petición | **Tokens**: la capacidad se mide en tokens por minuto, no en peticiones por segundo |
| **Duración de la petición** | Milisegundos | Segundos, proporcional a los tokens generados |
| **Paralelismo** | Réplicas del modelo completo | **Model parallelism**: el modelo puede no caber en un solo acelerador |
| **Batching** | Estático | **Continuous batching**: las peticiones entran y salen del lote en curso |

### Contenedores especializados: LMI

De [Model parallelism and large model inference](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference.html). SageMaker AI incluye **deep learning containers (DLCs)**, librerías y tooling especializados para **model parallelism y large model inference (LMI)**.

Los cuatro recursos que agrupa esa sección:

| Recurso | Contenido |
| --- | --- |
| [The LMI container documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-container-docs.html) | Componentes y arquitectura de los contenedores LMI, selección de tipo de instancia y backend, configuración y despliegue, optimización con **quantization, tensor parallelism y continuous batching**, y benchmarking de endpoints |
| [SageMaker AI endpoint parameters for large model inference](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-hosting.html) | Parámetros del endpoint para modelos grandes |
| [Deploying uncompressed models](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-uncompressed.html) | La estrategia de carga de modelo que pide el skill |
| [Deploy large models with TorchServe](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-tutorials-torchserve.html) | Alternativa con TorchServe |

> **Hueco de documentación**: la página oficial de LMI containers **delega el contenido al sitio de Deep Java Library**, fuera de `docs.aws.amazon.com`. Los conceptos que enumera (quantization, tensor parallelism, continuous batching, selección de backend) sí están nombrados en el portal de AWS, pero su desarrollo no. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación).

### Estrategia de carga de modelo: desplegar sin comprimir

De [Deploying uncompressed models](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-uncompressed.html). Este es el detalle técnico central del skill, y el razonamiento oficial es explícito: al desplegar modelos, una opción es archivar y comprimir los artefactos en formato `tar.gz`. Funciona bien con modelos pequeños, pero **comprimir un artefacto con cientos de miles de millones de parámetros y descomprimirlo en el endpoint puede llevar un tiempo significativo**. Para large model inference, AWS **recomienda desplegar el modelo sin comprimir**.

El procedimiento:

1. Subir **todos** los artefactos del modelo a Amazon S3 y organizarlos bajo un **prefijo común de S3**.
2. Usar **`/` como delimitador** (requisito para desplegar con SageMaker AI).
3. Asegurar que **solo** los artefactos asociados al modelo están organizados bajo ese prefijo. Para modelos con un único artefacto sin comprimir, el prefijo es idéntico al nombre de clave.
4. Especificar la ubicación en el campo **`ModelDataSource`** al invocar **`CreateModel`**.

```python
create_model_response = sagemaker_client.create_model(
    ModelName = model_name,
    ExecutionRoleArn = sagemaker_role,
    PrimaryContainer = {
        "Image": container,
        "ModelDataSource": {
            "S3DataSource": {
                "S3Uri": "s3://amzn-s3-demo-bucket/prefix/to/model/data/",
                "S3DataType": "S3Prefix",
                "CompressionType": "None",
            },
        },
    },
)
```

SageMaker AI **descarga automáticamente los artefactos sin comprimir a `/opt/ml/model`** para inferencia. Verificar qué objetos están bajo el prefijo con:

```
aws s3 ls --recursive s3://bucket/prefix
```

Si en lugar de un prefijo común el artefacto es **un único objeto de S3 sin comprimir**, se apunta `S3Uri` al objeto y se cambia `S3DataType` a **`S3Object`**.

> **Restricción importante**: `ModelDataSource` **no se puede usar** con AWS Marketplace, **SageMaker AI batch transform**, **SageMaker Serverless Inference** ni **multi-model endpoints**. Es decir, la estrategia de carga recomendada para modelos grandes es incompatible con serverless: un LLM grande va a endpoint en tiempo real o asíncrono, no a serverless.

### Empaquetar varios modelos en un endpoint: inference components

De [Deploy models for real-time inference](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-deploy-models.html). Cuando varios modelos comparten un endpoint utilizan conjuntamente los recursos alojados: instancias de cómputo ML, CPUs y aceleradores. **La forma más flexible de desplegar varios modelos en un endpoint es definir cada modelo como un inference component.**

Un *inference component* es un objeto de hosting de SageMaker AI con el que se despliega un modelo a un endpoint. En sus ajustes se especifica el modelo, el endpoint y **cómo el modelo utiliza los recursos que el endpoint aloja**. El modelo se indica con un objeto Model de SageMaker AI, o directamente con los artefactos y la imagen.

| Beneficio | Detalle |
| --- | --- |
| **Flexibilidad** | El inference component **desacopla los detalles de hosting del endpoint en sí**. Permite alojar múltiples modelos en la misma infraestructura, añadir o quitar modelos según haga falta, y **actualizar cada modelo de forma independiente** |
| **Escalabilidad** | Se especifica **cuántas copias** de cada modelo alojar y un mínimo de copias para asegurar que el modelo carga en la cantidad necesaria. **Cualquier copia se puede escalar a cero**, lo que hace sitio para que otra copia escale hacia arriba |

En los ajustes se optimiza la utilización de recursos ajustando cómo se asignan al modelo los **núcleos de CPU, los aceleradores y la memoria** requeridos. Se despliegan varios inference components a un endpoint, cada uno con un modelo y sus necesidades de recursos.

Tras desplegar un inference component, se invoca el modelo asociado directamente con la acción **`InvokeEndpoint`**.

SageMaker AI empaqueta los modelos como inference components al desplegarlos mediante: **SageMaker Studio Classic**, el **SageMaker Python SDK** desplegando un objeto Model con el tipo de endpoint puesto a **`EndpointType.INFERENCE_COMPONENT_BASED`**, o el **AWS SDK for Python (Boto3)** definiendo objetos **`InferenceComponent`**.

> El detalle de **escalar una copia a cero para hacer sitio a otra** es la respuesta al problema real de los LLMs: la memoria del acelerador es el recurso escaso, y no caben todas las copias de todos los modelos a la vez.

Para adapters y multi-LoRA sobre un modelo base compartido, ver [Task 1.2 · Skill 1.2.4](../domain-1/task-1-2-seleccion-y-configuracion-fm.md), que cubre los adapter inference components y las recomendaciones de benchmarking de endpoints multi-LoRA.

### Traer un modelo personalizado a Bedrock

De [Use Custom model import](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-import-model.html). Permite importar FMs personalizados en otros entornos, **como Amazon SageMaker AI**, para usarlos con las funcionalidades de Bedrock. El caso típico: un modelo creado en SageMaker AI con pesos propietarios, importado a Bedrock para hacerle llamadas de inferencia.

| Aspecto | Detalle |
| --- | --- |
| **Throughput** | Se puede usar el modelo importado **con on-demand throughput**, lo que lo diferencia del resto de modelos personalizados |
| **Operaciones** | **`InvokeModel`** e **`InvokeModelWithResponseStream`** |
| **Regiones soportadas** | `eu-central-1`, `us-east-1`, `us-east-2`, `us-west-2` |
| **Incompatibilidades** | **No se puede usar con Batch inference ni con CloudFormation** |

Los **tres patrones** de personalización que soporta:

| Patrón | Qué se cambia |
| --- | --- |
| **Fine-tuned model** | Los **pesos** con datos propietarios, **manteniendo la configuración** del modelo base |
| **Adaptation** | Adaptación al dominio cuando el modelo no generaliza bien. Modifica el modelo para generalizar en un dominio objetivo y tratar discrepancias entre dominios (ejemplo oficial: sector financiero que quiere un modelo que generalice bien en precios). También **adaptación de idioma**, por ejemplo para generar respuestas en portugués o tamil, lo que a menudo implica **cambios en el vocabulario** |
| **Pretrained from scratch** | Además de pesos y vocabulario, **parámetros de configuración** del modelo: número de attention heads, hidden layers o **longitud de contexto** |

**Arquitecturas soportadas**: Mistral (decoder-only con Sliding Window Attention y opciones de Grouped Query Attention), Mixtral (decoder-only con Mixture of Experts disperso), Flan (versión mejorada de T5, encoder-decoder), Llama 2, Llama 3, Llama 3.1, Llama 3.2, Llama 3.3 y Mllama (con Grouped Query Attention), y GPTBigCode (versión optimizada de GPT-2 con Multi-Query attention).

> Aviso de licencia que incluye la documentación: asegurar que la importación y el uso de los modelos en Bedrock **cumple los términos o licencias aplicables** a esos modelos.

### Contenedores propios: ECR, ECS, EKS y Fargate

El skill nombra "patrones de despliegue basados en contenedor". Los destinos en alcance del examen y su papel:

| Servicio | Papel |
| --- | --- |
| **Amazon ECR** | Registro de las imágenes: DLCs de LMI, contenedores propios de inferencia, imágenes de agentes para AgentCore Runtime (que exige **ARM64**) |
| **Amazon ECS / AWS Fargate** | Servidores de herramientas complejas y procesos sin techo de duración, según la tabla de [Task 2.1 · Skill 2.1.7](./task-2-1-agentic-ai-y-herramientas.md#skill-217--frameworks-de-extensión-del-modelo) |
| **Amazon EKS** | Lo mismo sobre Kubernetes, cuando la organización ya opera ahí |
| **SageMaker AI endpoints** | Hosting gestionado con inference components, auto scaling y las tres modalidades de endpoint |

### Reducir el coste de carga y de memoria

Las palancas documentadas en el portal de AWS, ordenadas por dónde actúan:

| Palanca | Efecto | Dónde está documentada |
| --- | --- | --- |
| **Artefactos sin comprimir** | Elimina el tiempo de descompresión en el endpoint | [Deploying uncompressed models](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-uncompressed.html) |
| **Inference components con copias y scale-to-zero** | Reparte memoria de acelerador entre modelos según demanda | [Deploy models for real-time inference](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-deploy-models.html) |
| **Quantization, tensor parallelism, continuous batching** | Reducen memoria por parámetro, reparten el modelo entre aceleradores y mejoran el throughput de tokens | Nombradas en [LMI container documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-container-docs.html) |
| **SageMaker Neo** | Optimiza el modelo para el entorno destino, incluidos chips **AWS Inferentia** | [SageMaker Neo](https://docs.aws.amazon.com/sagemaker/latest/dg/neo.html) |
| **Auto scaling** | Ajusta cómputo al tráfico entrante | [Automatic scaling](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling.html) |
| **Async con escalado a cero** | No se paga cuando no hay peticiones | [Asynchronous inference](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html) |
| **Prompt caching** | Reduce latencia y coste de tokens de entrada reutilizando prefijos | [Prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html), detallado en el skill siguiente |

---

## Skill 2.2.3 — Despliegue optimizado y model cascading

> *Desarrollar enfoques optimizados de despliegue de FM para balancear rendimiento y requisitos de recursos en cargas GenAI (por ejemplo, seleccionando modelos apropiados, usando modelos pre-entrenados más pequeños para tareas específicas, usando model cascading basado en API para atender consultas rutinarias).*

### El marco: el modelo más pequeño que cumple la barra

La guía oficial de este skill es [AGENTCOST02](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentcost02.html) y [AGENTPERF02](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentperf02.html) del Agentic AI Lens, ya desarrollados en [Task 2.1 · Skill 2.1.4](./task-2-1-agentic-ai-y-herramientas.md#skill-214--coordinación-de-modelos-y-optimización-entre-capacidades). Los dos enunciados que aplican directamente:

- Cada clase de tarea se enruta al **modelo más pequeño que cumple su barra de calidad**, con fallback en cascada a un modelo más capaz cuando el asignado produce salidas de baja confianza.
- La selección de modelo coincide con la complejidad de la tarea: **clasificación y formateo rutinarios en modelos coste-eficientes**, y modelos premium reservados para razonamiento que realmente los necesita.

Y el problema frecuente que describe el antipatrón: **cada invocación por defecto al modelo de propósito general más capaz**, con costes de inferencia más altos para clasificación y formateo rutinarios que podrían usar alternativas coste-efectivas.

> El nivel 2 de madurez de AGENTCOST02 marca un detalle que se pasa por alto: además de mapear tipos de tarea a tiers de modelo, hay que **alinear los entornos al tier de precio on-demand adecuado** (Flex, Standard, Priority). Un entorno de desarrollo en Priority es dinero tirado.

### Model cascading

El patrón: empezar por el modelo pequeño y escalar solo cuando la confianza es baja.

```
Petición
   │
   ▼
┌─────────────────────────────────────────────┐
│ Pre-clasificador (modelo pequeño o reglas)  │  ← nivel 3 de AGENTCOST02
│ Estima la complejidad de la tarea           │
└─────────────────────────────────────────────┘
   │
   ├─ simple ──► modelo económico
   │                 │
   │                 ▼
   │            ¿confianza suficiente?
   │                 │ no
   │                 ▼
   └─ compleja ──► modelo capaz  ◄────── escalada por baja confianza
                      │
                      ▼
                 respuesta
                      │
                      ▼
            Métricas por tier:
            · cost-per-correct-response
            · cascade escalation rate
            · cache hit rate
```

La métrica que decide si la cascada funciona es el **cascade escalation rate**: si casi todo escala, el modelo pequeño no cumple la barra y la cascada solo añade latencia y coste. Si casi nada escala, quizá el modelo grande no hacía falta en absoluto.

### Intelligent prompt routing: la cascada gestionada

De [Understanding intelligent prompt routing in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html). Proporciona **un único endpoint serverless** para enrutar peticiones entre distintos FMs **dentro de la misma familia de modelos**. Predice dinámicamente la calidad de respuesta de cada modelo para cada petición y enruta a la de mejor calidad, optimizando calidad y coste a la vez.

| Beneficio | Detalle |
| --- | --- |
| **Calidad y coste optimizados** | Enruta prompts a distintos modelos para lograr la mejor calidad al menor coste |
| **Gestión simplificada** | **Elimina la necesidad de lógica de orquestación compleja** |
| **Future-proof** | Incorpora modelos nuevos a medida que están disponibles |

**Dos tipos de router:**

| Tipo | Qué es | Cuándo |
| --- | --- | --- |
| **Default prompt routers** | Sistemas de routing **preconfigurados** por Bedrock, con ajustes predefinidos, diseñados para funcionar out-of-the-box con modelos concretos | AWS **recomienda empezar experimentando con ellos** |
| **Configured prompt routers** | Configuraciones propias adaptadas a necesidades y preferencias | Cuando se requiere más control sobre cómo enrutar y qué modelos usar. Permiten optimizar según métricas de calidad de respuesta y casos de uso |

El camino recomendado: experimentar con los default, luego configurar los propios, **evaluar la calidad de respuesta en el playground** y llevarlos a producción si cumplen los requisitos.

**Criterios de routing y fallback model**: al configurar routers propios se especifica el criterio de routing, usado para determinar qué modelo procesa una petición **según la diferencia de calidad de respuesta**. El criterio determina **cuánto deben acercarse las respuestas del fallback model a las de los otros modelos**. La recomendación sobre el fallback: elegir un modelo que funcione bien para tus peticiones, porque **sirve de baseline fiable**.

**Modelos soportados** (familias Amazon, Anthropic y Meta), con soporte single-region y de cross-Region inference profile:

| Proveedor | Modelos soportados |
| --- | --- |
| **Amazon** | Nova Lite, Nova Pro |
| **Anthropic** | Claude 3 Haiku, Claude 3.5 Haiku, Claude 3.5 Sonnet, Claude 3.5 Sonnet v2 |
| **Meta** | Llama 3.1 8B/70B Instruct, Llama 3.2 11B/90B Instruct, Llama 3.3 70B Instruct |

> **Consideraciones y limitaciones oficiales**, que son las respuestas a "cuándo NO usar prompt routing":
> - Está **optimizado solo para prompts en inglés**.
> - **No puede ajustar decisiones de routing ni respuestas según datos de rendimiento específicos de la aplicación.**
> - Puede **no dar el routing más óptimo para casos de uso únicos o especializados**; su eficacia depende de los datos de entrenamiento iniciales.
>
> Las tres apuntan al mismo sitio: si el caso de uso es especializado, multiidioma, o si se quiere enrutar según métricas propias, hay que construir el routing (ver [Skill 2.4.4](./task-2-4-integraciones-api-fm.md#skill-244--routing-inteligente-de-modelos)). El routing gestionado se limita además a **modelos de la misma familia**.

### Obtener un modelo pequeño que rinda: distillation

De [Customize a model with distillation in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html). *Model distillation* transfiere conocimiento de un modelo más grande e inteligente (**teacher**) a uno más pequeño, rápido y coste-eficiente (**student**), mejorando el rendimiento del student para un caso de uso concreto. Bedrock usa técnicas de síntesis de datos para generar respuestas diversas y de alta calidad (**datos sintéticos**) del teacher, y afina el student con ellas.

Los tres pasos:

**1. Elegir teacher y student.**

**2. Preparar los datos de entrenamiento**, una colección de prompts en ficheros `.jsonl`. Tres opciones de preparación:

| Opción | Cómo |
| --- | --- |
| **Optimizar prompts** | Formatear los prompts de entrada para el caso de uso deseado |
| **Usar ejemplos etiquetados** | Preparar datos como **pares prompt-respuesta**, que Bedrock usa como **golden examples** al generar respuestas del teacher |
| **Usar invocation logs** | Con CloudWatch Logs invocation logging habilitado, usar **respuestas del teacher ya existentes** en los logs de invocación almacenados en S3 como datos de entrenamiento |

**3. Crear el job de distillation**, que produce un modelo más pequeño, rápido y coste-efectivo. **Solo tú puedes acceder al modelo destilado final**, y Bedrock **no usa tus datos para entrenar ningún otro modelo teacher o student de uso público**.

**Cómo funciona internamente**: Bedrock genera respuestas del teacher, añade técnicas de síntesis de datos para mejorar la generación y afina el student con las respuestas generadas. El dataset aumentado se divide en datasets separados de **entrenamiento y validación**, y solo el de entrenamiento se usa para afinar.

Las técnicas propietarias de síntesis que puede aplicar: **generar prompts similares** para obtener respuestas más diversas del teacher, o usar los pares etiquetados que aportes como golden examples para instruir al teacher a generar respuestas similares de alta calidad.

> **Dos avisos de coste**: si Bedrock usa sus técnicas propietarias de síntesis de datos, la cuenta **incurre en cargos adicionales por las llamadas de inferencia al teacher**, facturadas a las tarifas on-demand del teacher. Y esas técnicas pueden **aumentar el tamaño del dataset de fine-tuning hasta un máximo de 15.000 pares prompt-respuesta**.

La opción de **invocation logs** merece atención: si ya tienes respuestas del teacher en los logs de invocación, se pueden usar para afinar el student sin pagar inferencia nueva del teacher. Requiere dar a Bedrock acceso a los logs. Es el argumento operativo para activar [model invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) desde el principio, más allá de la auditoría tratada en [Task 1.6 · Skill 1.6.3](../domain-1/task-1-6-prompt-engineering-governance.md).

Recordar que un modelo destilado es un modelo personalizado: según la página de Provisioned Throughput, **usarlo requiere comprar Provisioned Throughput**, salvo que se configure inferencia on-demand para modelo personalizado según [Set up inference for a custom model](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-use.html).

### Reducir el coste sin cambiar de modelo: prompt caching

De [Prompt caching for faster model inference](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html). Funcionalidad opcional que **reduce la latencia de respuesta y el coste de tokens de entrada**. Ayuda en cargas con **contextos largos y repetidos** reutilizados frecuentemente en múltiples consultas. El ejemplo oficial: un chatbot donde los usuarios suben documentos y hacen preguntas sobre ellos; sin caché el modelo procesa el documento en cada entrada del usuario.

**Los dos tipos**, que se diferencian en cómo se selecciona el contenido reutilizable:

| Tipo | Cómo funciona | Configuración de la petición |
| --- | --- | --- |
| **Implicit Prompt Caching** | Bedrock y el modelo **intentan reutilizar automáticamente** prefijos elegibles | **No requiere** cache controls ni breakpoints |
| **Explicit Prompt Caching** | **Tú identificas** los prefijos reutilizables añadiendo cache controls o breakpoints específicos del modelo | La petición debe incluir los cache controls soportados por el modelo y la API |

**Implicit**: es **best effort**. Repetir un prompt idéntico **no garantiza un cache hit**, y las tasas de acierto pueden variar. La recomendación operativa: mantener el **contenido estático al principio** del prompt y el **dinámico al final**, para aumentar la probabilidad de coincidencia exacta de prefijo.

**Explicit**: usa **cache checkpoints**, marcadores que definen la subsección contigua del prompt a cachear. Los prefijos deben **permanecer estáticos entre peticiones**; cambiarlos produce cache misses.

Los mínimos de tokens por checkpoint, que varían por modelo:

| Modelo | Mínimo por cache checkpoint |
| --- | --- |
| **Claude Opus 5** | 512 tokens |
| **Claude Sonnet 5** | 1.024 tokens |
| **Claude Haiku 4.5** | 4.096 tokens |

El mínimo **aplica de forma acumulativa a todo el prefijo del prompt antes de cada checkpoint**, incluyendo cuando corresponda el contenido de los campos `tools`, `system` y `messages`. **No hay mínimo entre checkpoints**: con un modelo de mínimo 1.024, se pueden definir checkpoints adicionales a menos de 1.024 tokens de distancia siempre que el prefijo total antes de cada uno contenga al menos 1.024. Si se añade un checkpoint antes de que el prefijo alcance el mínimo, **la inferencia sigue funcionando pero el prefijo no se cachea**.

**TTL**: la caché tiene un Time To Live que **se reinicia con cada cache hit exitoso**. Si no hay aciertos dentro de la ventana, la caché expira. **Muchos modelos soportan un TTL de 5 minutos**; el model card indica las condiciones exactas.

**Facturación**: en ambos tipos, los tokens leídos de caché se reportan como **cached tokens** y se facturan a la **tarifa de cache-read** del modelo. Los que no se leen de caché van a la tarifa estándar de token de entrada. **Según el modelo, los tokens escritos a caché pueden facturarse a una tarifa superior a la estándar de entrada.**

**Dónde está disponible**: APIs `Converse` y `ConverseStream`, APIs `InvokeModel` e `InvokeModelWithResponseStream`, junto con **cross-Region inference** (que selecciona automáticamente la Región óptima de tu geografía; en momentos de alta demanda estas optimizaciones **pueden provocar más escrituras de caché**), y **Bedrock Prompt Management**, donde al crear o modificar un prompt se puede habilitar el caching de system prompts, system instructions y messages.

> **Dos avisos críticos**:
> - **El soporte de prompt caching no garantiza un cache hit para ninguna petición.** Hay que **comprobar los campos de cache usage en la respuesta del modelo** para saber si los tokens se leyeron o escribieron en caché.
> - **Prompt caching solo se soporta en endpoints de inferencia on-demand. No se soporta con la API de batch inference.**

### Reducir la latencia sin cambiar de modelo: latency-optimized inference

De [Optimize model inference for latency](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html). **La funcionalidad está en preview release y sujeta a cambios.** Entrega tiempos de respuesta más rápidos sin comprometer la precisión, y **no requiere setup adicional ni fine-tuning**: basta poner el parámetro de latencia a `optimized` al llamar a la API de runtime.

```json
"performanceConfig": {
  "latency": "standard | optimized"
}
```

**Por defecto todas las peticiones van por `standard`.**

| Proveedor | Modelo | Model ID | Regiones (vía cross-Region inference) |
| --- | --- | --- | --- |
| Amazon | **Nova Pro** | `amazon.nova-pro-v1:0` | `us-east-1`, `us-east-2` |
| Anthropic | **Claude 3.5 Haiku** | `anthropic.claude-3-5-haiku-20241022-v1:0` | `us-east-2`, `us-west-2` |
| Meta | **Llama 3.1 405B Instruct** | `meta.llama3-1-405b-instruct-v1:0` | `us-east-2` |
| Meta | **Llama 3.1 70B Instruct** | `meta.llama3-1-70b-instruct-v1:0` | `us-east-2`, `us-west-2` |

Comportamiento ante cuota y observabilidad:

- Al alcanzar la cuota de uso de optimización de latencia para un modelo, Bedrock **intenta servir la petición con latencia Standard**, y en ese caso **se factura a tarifas Standard**.
- La configuración de latencia de una petición servida es **visible en la respuesta de la API y en los logs de AWS CloudTrail**.
- Las métricas de peticiones optimizadas se ven en **CloudWatch bajo `model-id+latency-optimized`**.
- **Llama 3.1 405B** soporta actualmente peticiones con un total de tokens de entrada y salida **hasta 11K**; por encima, **se vuelve al modo standard**.

### Resumen: las palancas de optimización, por orden de intervención

```
1 · Elegir el modelo          → el más pequeño que cumple la barra (AGENTCOST02)
                                 modelos pre-entrenados menores para tareas concretas
2 · Enrutar                   → intelligent prompt routing (misma familia, inglés)
                                 o routing propio por contenido y métricas
3 · Cascada                   → modelo económico primero, escalar por baja confianza
                                 vigilar el cascade escalation rate
4 · Especializar              → distillation teacher→student
                                 datos de invocation logs para no pagar inferencia nueva
                                 Custom Model Import para modelos afinados fuera
5 · Reutilizar contexto       → prompt caching implicit o explicit
                                 estático al principio, dinámico al final
                                 solo on-demand, NO con batch
6 · Elegir el tier            → Flex en dev · Standard por defecto
                                 Priority solo si el throttling afecta a usuarios
                                 Reserved cuando la carga estable supera el 40 %
                                 Batch para lo no urgente (50 % menos)
7 · Optimizar la latencia     → latency-optimized inference (preview, 4 modelos)
                                 con fallback automático a standard al agotar cuota
8 · Optimizar el hosting      → artefactos sin comprimir con ModelDataSource
                                 inference components con copias y scale-to-zero
                                 quantization · tensor parallelism · continuous batching
                                 SageMaker Neo · Inferentia · auto scaling
                                 async con escalado a cero
```

Las palancas 1 a 5 actúan sobre **qué y cómo se invoca**; la 6 y 7 sobre **cómo se compra la capacidad**; la 8 sobre **cómo se aloja el modelo propio**. Confundir los tres planos es el error clásico: comprar Provisioned Throughput no arregla un prompt de sistema que creció sin revisión.
