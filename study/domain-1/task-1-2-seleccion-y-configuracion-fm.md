# Task 1.2 — Seleccionar y configurar FMs

[← Volver al índice](./README.md)

Skills cubiertos: **1.2.1**, **1.2.2**, **1.2.3**, **1.2.4**.

---

## Skill 1.2.1 — Evaluar y elegir FMs

> *Evaluar y elegir FMs para asegurar alineación óptima con casos de uso de negocio y requisitos técnicos (por ejemplo, benchmarks de rendimiento, análisis de capacidades, evaluación de limitaciones).*

### Criterios oficiales de selección

La fase *model selection* del [Generative AI lifecycle](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lifecycle.html) enumera los factores a considerar:

| Factor | Qué evaluar |
| --- | --- |
| **Modality** | Texto, imagen, audio, vídeo, multimodal |
| **Size** | Tamaño del modelo frente al coste y la latencia |
| **Accuracy** | Calidad sobre tu tarea concreta, medida con tu dataset |
| **Training data** | Datos con los que se entrenó y su ajuste a tu dominio |
| **Pricing** | Coste por token de entrada y salida |
| **Context window** | Tamaño máximo de contexto disponible |
| **Inference latency** | Latencia aceptable para el caso de uso |
| **Compatibility** | Encaje con la infraestructura existente |
| **Data usage policies** | Políticas de uso de datos del proveedor de hosting |

Añade el Lens: si usas SageMaker AI para training o hosting, hay que evaluar **tipos de instancia**; y si vas a usar RAG, hay que evaluar la **selección y disponibilidad del vector database** como parte de la misma decisión.

### Dónde consultar capacidades y límites por modelo

| Necesidad | Página oficial |
| --- | --- |
| Capacidades, modalidades y bloques de contenido soportados por modelo | [Models at a glance / model cards](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html) |
| Modelos y Regiones soportados | [Supported foundation models in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) |
| Parámetros de inferencia específicos por modelo | [Inference request parameters and response fields](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html) |
| Cuotas y límites | [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html) |
| Guías de prompting por proveedor | [Prompt engineering concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html) |

### Benchmarking con Bedrock evaluations

Para comparar modelos con datos propios usa [Amazon Bedrock evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html). Los tipos y su uso están detallados en [Task 1.1 · Skill 1.1.2](./task-1-1-analisis-y-diseno.md#skill-112--poc-técnicas-para-validar-viabilidad-rendimiento-y-valor). Recuerda que se puede evaluar un **inference profile** como si fuera un modelo.

### Opciones de hosting y su impacto en la selección

| Modo | Característica | Documentación |
| --- | --- | --- |
| **On-demand** | Pago por token, sujeto a cuotas de la cuenta | [Making inference requests](https://docs.aws.amazon.com/bedrock/latest/userguide/inference.html) |
| **Batch inference** | Procesamiento masivo, menor coste por token, no interactivo | [Batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html) |
| **Provisioned Throughput** | Throughput reservado a coste fijo por hora, medido en **Model Units (MU)**. Obligatorio para usar modelos personalizados | [Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) |
| **Inference profiles** | Recurso que asocia un modelo con una o varias Regiones; habilita tracking de uso, tags de coste y cross-Region inference | [Inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html) |

**Detalles de Provisioned Throughput para el examen**: el precio por hora depende del modelo elegido (para modelos personalizados se aplica el precio del modelo base), del número de MUs y de la duración del compromiso. Los niveles de compromiso son **sin compromiso** (borrable en cualquier momento), **1 mes** y **6 meses**; con compromiso no se puede borrar antes de que termine el plazo, y la facturación continúa hasta que se borra. Una MU define cuántos tokens de entrada puede procesar y cuántos de salida puede generar por minuto agregando todas las peticiones.

> **Limitación cruzada importante**: los inference profiles **no soportan Provisioned Throughput**. Si necesitas throughput reservado, no puedes obtenerlo a través de un inference profile.

---

## Skill 1.2.2 — Selección dinámica de modelo sin cambiar código

> *Crear patrones de arquitectura flexibles para habilitar selección dinámica de modelo y cambio de proveedor sin requerir modificaciones de código (por ejemplo, usando AWS Lambda, Amazon API Gateway, AWS AppConfig).*

### Capa 1 — API uniforme: Converse

La [Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) es el mecanismo nativo de Bedrock para escribir el código una vez y usarlo con distintos modelos. Ofrece una interfaz consistente para todos los modelos de Bedrock que soportan mensajes, y permite pasar parámetros únicos de un modelo concreto mediante `additionalModelRequestFields` sin romper la interfaz común.

Puntos que conviene memorizar:

- Está disponible **solo en el endpoint `bedrock-runtime`**.
- `Converse` requiere permiso `bedrock:InvokeModel`; `ConverseStream` requiere `bedrock:InvokeModelWithResponseStream`.
- Con modelos de **Mistral AI y Meta**, Converse encapsula la entrada en la plantilla de prompt específica del modelo para habilitar conversación.
- `modelId` es un parámetro **de cabecera obligatorio** y admite el ARN de un inference profile, lo que convierte el destino de la inferencia en configuración en lugar de código.

### Capa 2 — Indirección de recurso: inference profiles

Un [inference profile](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html) define un modelo y una o más Regiones a las que se pueden enrutar las invocaciones. Hay dos tipos:

| Tipo | Origen | Uso |
| --- | --- | --- |
| **Cross Region (system-defined)** | Predefinido por Amazon Bedrock, incluye varias Regiones | Distribuir inferencia entre Regiones |
| **Application inference profile** | Lo crea el usuario | Trackear coste y uso; puede apuntar a una Región o envolver un perfil system-defined para varias |

Los inference profiles se pueden usar con: model inference (`InvokeModel`, `InvokeModelWithResponseStream`, `Converse`, `ConverseStream`), embeddings y generación de respuesta en knowledge bases, parsing de datos no textuales, model evaluation, Prompt management y Flows.

Además soportan **tags para cost allocation**, lo que permite atribuir coste por aplicación o equipo sin tocar el código de invocación.

### Capa 3 — Enrutamiento por calidad: Intelligent Prompt Routing

[Intelligent prompt routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) expone un único endpoint serverless que enruta cada petición entre modelos **de la misma familia**, prediciendo dinámicamente la calidad de respuesta de cada modelo para esa petición.

| Concepto | Detalle |
| --- | --- |
| **Default prompt routers** | Preconfigurados por AWS, funcionan sin ajustes. Recomendados para empezar |
| **Configured prompt routers** | Definidos por el usuario, con criterios de enrutamiento propios |
| **Fallback model** | Modelo base de referencia; actúa como ancla |
| **Response quality difference** | Umbral que decide cuándo cambiar del fallback a otro modelo. Un valor de 10 % significa que solo se cambia si el otro modelo es un 10 % mejor |

Limitaciones oficiales: está optimizado **solo para prompts en inglés**, no ajusta decisiones según datos de rendimiento específicos de tu aplicación, y puede no dar el enrutamiento óptimo en casos de uso muy especializados porque depende de los datos de entrenamiento iniciales.

### Capa 4 — Configuración externa: AWS AppConfig

[AWS AppConfig](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html) permite cambiar el comportamiento de la aplicación en producción sin redespliegue. Aplicado a selección de modelo: el `modelId`, el inference profile, los parámetros de inferencia y el guardrail activo se convierten en configuración dinámica.

Tipos de perfil de configuración:

- **Feature flags** — releases controlados, rollouts graduales, pruebas en producción.
- **Free-form configurations** — almacenar y recuperar datos de configuración de fuentes externas y actualizarlos sin redespliegue.

Mecanismos de seguridad de AppConfig relevantes para cambiar modelos en caliente:

| Mecanismo | Qué hace |
| --- | --- |
| **Validators** | Verifican que la configuración es sintáctica y semánticamente correcta antes del despliegue; si fallan, AppConfig hace rollback automático |
| **Deployment strategies** | Despliegan el cambio de forma gradual durante un periodo definido |
| **Monitoring y rollback automático** | Integración con CloudWatch: si una alarma se dispara tras el cambio, AppConfig revierte automáticamente |

AppConfig puede tomar la configuración desde su propio **hosted configuration store**, Secrets Manager, Systems Manager Parameter Store o Amazon S3. La aplicación la recupera llamando a un endpoint local expuesto por **AWS AppConfig Agent**, que cachea la configuración desplegada; el agent funciona en EC2, Lambda, ECS y EKS. AppConfig se integra con IAM para control de acceso, KMS para cifrado y CloudTrail para auditoría.

### Arquitectura de referencia

```
Cliente
  │
  ▼
Amazon API Gateway        ← autenticación (Cognito / IAM), throttling, versionado de API
  │
  ▼
AWS Lambda (capa de abstracción de modelo)
  │   ├─ lee configuración de AWS AppConfig (Agent, cacheado)
  │   │     · modelId o ARN de inference profile
  │   │     · parámetros de inferencia
  │   │     · guardrailId + guardrailVersion
  │   │     · feature flag de proveedor activo
  │   ▼
  └─ bedrock-runtime: Converse / ConverseStream
        └─ destino: modelo, inference profile o prompt router
```

Con esta separación, cambiar de modelo o de proveedor es un despliegue de configuración de AppConfig, no un despliegue de código. Un cambio problemático se revierte con el rollback automático de AppConfig disparado por una alarma de CloudWatch.

---

## Skill 1.2.3 — Sistemas resilientes ante interrupciones

> *Diseñar sistemas de IA resilientes para asegurar operación continua durante interrupciones de servicio (por ejemplo, patrones circuit breaker con AWS Step Functions, Amazon Bedrock Cross-Region Inference para modelos con disponibilidad regional limitada, despliegue de modelos cross-Region, estrategias de degradación elegante).*

### Cross-Region Inference

Con [cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) eliges un inference profile ligado a una geografía (US, EU, APAC) o un perfil global. Amazon Bedrock selecciona automáticamente una Región comercial de AWS para procesar la petición.

| Característica | Geographic | Global |
| --- | --- | --- |
| **Residencia de datos** | Dentro de la frontera geográfica (US, EU, APAC) | Cualquier Región comercial de AWS soportada, a nivel mundial |
| **Enrutamiento** | Dentro de la geografía | Mundial |
| **Coste** | Precio estándar | Aproximadamente **10 % de ahorro** |
| **Requisito de SCP** | Permitir todas las Regiones destino del perfil | Permitir `"aws:RequestedRegion": "unspecified"` |
| **Recomendado para** | Organizaciones con regulación de residencia de datos | Organizaciones que priorizan optimización de coste |

Consideraciones generales que aparecen en el examen:

- **No hay coste adicional de enrutamiento**. El precio se calcula según la **Región desde la que se llama** al inference profile.
- Cross-Region inference **puede enrutar a Regiones que no están habilitadas manualmente** en tu cuenta. No se requiere habilitación manual.
- Todo el tráfico entre Regiones permanece en la red de AWS, **no pasa por internet público**, y va **cifrado en tránsito**.
- **CloudTrail registra todas las peticiones en la Región de origen**. El campo `additionalEventData.inferenceRegion` identifica dónde se procesó realmente la petición. Este es el mecanismo de auditoría para demostrar dónde se procesan los datos.
- Los inference profiles **no soportan Provisioned Throughput**.
- Servicios de AWS construidos sobre Bedrock también pueden usar CRIS.
- Advertencia explícita en Knowledge Bases: si usas cross-Region inference, **tus datos pueden compartirse entre Regiones**.

### Patrones de recuperación: GENREL03-BP01

La best practice [GENREL03-BP01 Use logic to manage prompt flows and gracefully recover from failure](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel03-bp01.html) es la fuente directa del patrón circuit breaker en el examen. Nivel de riesgo si no se implementa: **medio**.

Pasos de implementación oficiales:

1. **Establecer un sistema de clasificación de errores**: categorizar tipos de fallo, definir niveles de severidad, crear plantillas de respuesta por categoría, montar detección automatizada.
2. **Implementar mecanismos de recuperación**: reintentos con **exponential backoff**, plantillas de prompt de fallback, **implementaciones de circuit breaker**, workflows de recuperación automatizados.
3. **Configurar monitoreo y alertas**: tasa de éxito de recuperación, efectividad de la remediación, alertas ante fallos repetidos, seguimiento de rendimiento.
4. **Crear un proceso de mejora continua**: analizar patrones de fallo, actualizar estrategias de remediación, refinar plantillas de prompt, optimizar workflows de recuperación.

Guía de implementación adicional que conviene retener:

- Crear **capas de abstracción entre usuarios y modelos** para facilitar reintentos, manejo de errores y fallos elegantes.
- En flujos multi-paso, añadir lógica que compruebe que el prompt contiene la información esperada y que la respuesta del modelo contiene el contenido esperado.
- Para prompts que consumen fuentes externas: verificar que el dato relevante existe y **definir una acción de fallback o modalidad por defecto** cuando no hay datos. Lo mismo aplica a respuestas enriquecidas con embeddings de un vector search: comprobar relevancia de lo devuelto y definir fallback si no se devuelve nada.
- En workflows agénticos, hacer que el agent **clasifique las respuestas de sistemas externos como accionables o no accionables**. Una respuesta accionable es esperada y bien entendida (por ejemplo, una consulta que devuelve al menos un resultado); una no accionable requiere manejo de error a nivel software (códigos de error, respuestas vacías). Esto reduce el no determinismo.
- El Lens recomienda explícitamente **Amazon Bedrock Flows** para orquestar prompts multi-paso, usando sus **nodos iterator y condition** para implementar recuperación elegante en lugar de construir una capa de abstracción propia.

### Principios y focos de Reliability del Lens

Del pilar [Reliability](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/reliability.html):

**Principios**
- *Design for distributed resilience*: desplegar en varias Regiones y AZs; distribuir endpoints de modelo, datos de embeddings y capacidades de agent geográficamente.
- *Implement robust error management*: monitorear robustez y compleción, recuperación automatizada, evitar fallos en cascada en workflows de agents.
- *Standardize resource management through catalogs*: catálogos centralizados de prompts y modelos.
- *Architect for intelligent scalability*: escalado dinámico y balanceo de carga según utilización real.

**Áreas de foco**

| Área | Contenido |
| --- | --- |
| [GENREL01](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel01.html) | Gestión de cuotas de throughput |
| [GENREL02](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel02.html) | Fiabilidad de red entre endpoints, infraestructura y clientes |
| [GENREL03](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel03.html) | Remediación de prompts y acciones de recuperación |
| [GENREL04](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel04.html) | Prompt management: control de versiones y gestión de cambios |
| [GENREL05](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel05.html) | Disponibilidad distribuida. **GENREL05-BP01**: balancear peticiones de inferencia entre todas las Regiones de disponibilidad |
| [GENREL06](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel06.html) | Tareas de cómputo distribuido. **GENREL06-BP01**: diseñar tolerancia a fallos para tareas distribuidas de alto rendimiento como model customization |

**Métricas clave de reliability en GenAI** según el Lens: disponibilidad de inferencia del modelo, consistencia del tiempo de respuesta, RTO, RPO, tasas de error y tasas de éxito de recuperación.

**Retos comunes y mitigaciones** que el Lens documenta: rendimiento inconsistente del modelo (testing robusto, versionado de modelos y prompts, monitoreo continuo), picos de tráfico inesperados (auto-scaling, rate limiting y throttling, capacidad de burst), training distribuido a gran escala (checkpointing, frameworks tolerantes a fallos), consistencia de datos multi-Región (replicación robusta, consistencia eventual donde aplique, resolución de conflictos), y model drift o calidad de datos (monitoreo continuo, ciclos de reentrenamiento, checks de calidad en ingesta).

### Degradación elegante: catálogo de estrategias

| Fallo | Degradación |
| --- | --- |
| Throttling del modelo primario | Reintento con backoff → modelo secundario de la misma familia vía prompt router o inference profile |
| Región degradada | Cross-Region inference geográfica; despliegue multi-Región de endpoints de SageMaker AI |
| Vector store no disponible | Responder solo con el conocimiento del modelo y **declarar explícitamente** que no se consultaron fuentes internas |
| Retrieval sin resultados relevantes | Acción de fallback definida; no inventar. Reforzar con contextual grounding de Guardrails |
| Herramienta externa caída | Clasificar respuesta como no accionable y responder con capacidad reducida |
| Guardrail bloquea la respuesta | Mensaje configurado de guardrail, no error genérico |

Guardrails también admite [distribuir inferencia de guardrail entre Regiones](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region.html), para que la capa de seguridad no se convierta en el punto único de fallo.

---

## Skill 1.2.4 — Despliegue y ciclo de vida de FMs personalizados

> *Implementar despliegue y gestión del ciclo de vida de customización de FMs (por ejemplo, SageMaker AI para desplegar modelos fine-tuned de dominio, técnicas de adaptación eficiente en parámetros como LoRA y adapters, SageMaker Model Registry para versionado y despliegue, pipelines automatizados de despliegue, estrategias de rollback, gestión del ciclo de vida para retirar y reemplazar modelos).*

### Métodos de customización en Amazon Bedrock

De [Customize your model](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html):

| Método | Cómo funciona | Cuándo |
| --- | --- | --- |
| **Supervised fine-tuning** | Datos **etiquetados**; el modelo aprende qué salida corresponde a qué entrada y se ajustan sus parámetros | Tareas concretas con ejemplos etiquetados disponibles |
| **Reinforcement fine-tuning** | No se dan pares entrada-salida: se definen **reward functions** (implementables con AWS Lambda) que evalúan la calidad de la respuesta; el modelo aprende iterativamente con los scores. Admite datasets de prompts propios o **logs de invocación de Bedrock existentes**. Bedrock automatiza el workflow y da métricas en tiempo real | Alinear con criterios de calidad difíciles de etiquetar |
| **Distillation** | Transfiere conocimiento de un modelo grande (**teacher**) a uno más pequeño, rápido y económico (**student**). Bedrock genera respuestas del teacher para tus prompts y con ellas hace fine-tuning del student. Opcionalmente se pueden aportar pares prompt-respuesta etiquetados | Reducir coste y latencia manteniendo accuracy cercana al teacher |

**Facturación**: el entrenamiento se cobra por tokens procesados (tokens del corpus de entrenamiento × número de epochs) más almacenamiento mensual por modelo.

> **Regla crítica**: para **usar** un modelo personalizado en Bedrock hay que **comprar Provisioned Throughput**. No hay modo on-demand para modelos personalizados. Ver [Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html).

### LoRA en SageMaker AI: adapter inference components

De [Fine-tune models with adapter inference components](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-adapt.html). El principio de **LoRA (Low-Rank Adaptation)** es que solo una pequeña parte de un modelo grande necesita actualizarse para adaptarlo a nuevas tareas o dominios: el adapter añade unas pocas capas extra sobre la inferencia del modelo base.

Arquitectura:

| Componente | Contenido |
| --- | --- |
| **Base inference component** | El foundation model a adaptar. Se despliega en un endpoint de SageMaker AI y **aporta los recursos de cómputo** |
| **Adapter inference component** | Referencia al adapter LoRA almacenado en S3. Usa el cómputo del base inference component |

Requisitos previos: tener el base inference component ya desplegado en un endpoint, y los artefactos del adapter LoRA almacenados como archivo **`tar.gz` en Amazon S3**.

Creación (SDK for Python / Boto3):

```python
sm_client.create_inference_component(
    InferenceComponentName=adapter_ic_name,
    EndpointName=endpoint_name,
    Specification={
        "BaseInferenceComponentName": base_inference_component_name,
        "Container": {
            "ArtifactUrl": adapter_s3_uri
        },
    },
)
```

**Diferencia clave frente a un inference component normal**: en `Specification` se **omite** la clave `ComputeResourceRequirements`, porque el adapter usa el cómputo del componente base.

Invocación: se especifica el nombre del adapter en `InferenceComponentName`.

```python
response = sm_rt_client.invoke_endpoint(
    EndpointName=endpoint_name,
    InferenceComponentName=adapter_ic_name,
    Body=json.dumps({
        "inputs": prompt,
        "parameters": {"max_new_tokens": 100, "temperature": 0.9}
    }),
    ContentType="application/json",
)
```

SageMaker AI combina el adapter con el modelo base para aumentar la respuesta generada. Esto habilita **multi-LoRA serving**: varios adapters sobre un mismo modelo base desplegado, sirviendo variantes fine-tuned distintas sin despliegues separados. Existe además soporte de [inference recommendations para modelos con adapters LoRA](https://docs.aws.amazon.com/sagemaker/latest/dg/generative-ai-inference-recommendations-adapters.html) y [benchmarking de endpoints multi-LoRA](https://docs.aws.amazon.com/sagemaker/latest/dg/generative-ai-inference-recommendations-benchmark.html).

### SageMaker Model Registry: versionado y governance

De [Model Registration Deployment with Model Registry](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html). Capacidades:

- Catalogar modelos para producción.
- Gestionar **versiones** de modelo.
- Asociar **metadatos**, como métricas de entrenamiento.
- Ver información de **SageMaker Model Cards** en los modelos registrados.
- Ver **model lineage** para trazabilidad y reproducibilidad.
- Definir una **construcción de staging** por la que los modelos progresan en su ciclo de vida.
- Gestionar el **approval status** del modelo.
- Desplegar a producción y **automatizar el despliegue con CI/CD**.
- Compartir modelos con otros usuarios.

Jerarquía y flujo típico:

1. Crear un **Model (Package) Group** que agrupe todas las versiones que resuelven un problema.
2. Crear un pipeline de ML que entrena el modelo (ver [Pipelines](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines-build.html)).
3. En cada ejecución del pipeline, registrar una **versión de modelo** en ese Model Group.
4. Añadir el Model Group a una o más **Model Registry Collections** ([doc](https://docs.aws.amazon.com/sagemaker/latest/dg/modelcollections.html)).

El **approval status** es el punto de enganche del CI/CD: un cambio de estado a aprobado dispara el pipeline de despliegue, y el estado combinado con las versiones permite el **rollback** apuntando a una versión anterior ya aprobada.

### Ciclo de vida completo: del entrenamiento al retiro

| Etapa | Mecanismo Bedrock | Mecanismo SageMaker AI |
| --- | --- | --- |
| Customización | Fine-tuning, reinforcement fine-tuning, distillation | Training jobs, PEFT / LoRA |
| Registro y versionado | Modelo personalizado con nombre y versión | Model Registry: model groups, versions, approval status |
| Habilitación para servir | Compra de Provisioned Throughput | Endpoint + inference components (base y adapter) |
| Despliegue automatizado | CodePipeline / CodeBuild / CDK; configuración vía AppConfig | SageMaker Pipelines + CodePipeline disparados por approval status |
| Rollback | Cambiar el destino de invocación a la versión anterior (configuración, no código) | Apuntar a la versión previa aprobada en Model Registry; revertir inference component |
| Evaluación previa a promoción | Bedrock evaluations sobre el modelo personalizado | SageMaker Clarify, Model Monitor |
| Retiro | Borrar el Provisioned Throughput (atención a los compromisos de 1 y 6 meses) y el modelo | Borrar inference components y endpoint; archivar la versión en el registry |
| Monitoreo post-despliegue | CloudWatch, model invocation logging | SageMaker Model Monitor, CloudWatch |

**Trampa de examen sobre retiro**: si compraste Provisioned Throughput con compromiso de 1 o 6 meses, **no puedes borrarlo antes de que expire el plazo** y la facturación continúa hasta que se borra. La estrategia de retiro de modelos personalizados debe tener en cuenta ese plazo.

---

## Preguntas de autoevaluación

1. Tu aplicación debe poder cambiar de modelo sin redesplegar código. ¿Qué tres capas combinas y qué aporta cada una?
2. ¿Qué campo de CloudTrail te dice en qué Región se procesó realmente una petición de cross-Region inference?
3. Una política de la organización exige que los datos no salgan de la UE. ¿Geographic o Global cross-Region inference? ¿Qué condición de SCP corresponde a cada opción?
4. ¿Puedes combinar un inference profile con Provisioned Throughput?
5. Al crear un adapter inference component, ¿qué clave se omite en `Specification` y por qué?
6. ¿Qué método de customización de Bedrock puede usar logs de invocación existentes como datos de entrada?
7. Acabas de fine-tunear un modelo en Bedrock. ¿Qué necesitas obligatoriamente antes de poder invocarlo?
8. ¿Qué atributo de SageMaker Model Registry se usa como disparador de un pipeline de despliegue CI/CD?

## Fuentes oficiales de esta sección

**Amazon Bedrock**
- [Route model inference requests across AWS Regions with cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)
- [Set up a model invocation resource using inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)
- [Understanding intelligent prompt routing in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html)
- [Increase model invocation capacity with Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)
- [Customize your model to improve its performance for your use case](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html)
- [Inference using Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html)
- [Distribute guardrail inference across AWS Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region.html)
- [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html)

**AWS Well-Architected Generative AI Lens**
- [Generative AI lifecycle](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lifecycle.html)
- [Reliability](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/reliability.html)
- [GENREL03-BP01 Use logic to manage prompt flows and gracefully recover from failure](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel03-bp01.html)
- [GENREL05 Distributed availability](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel05.html)
- [GENREL06-BP01 Design for fault-tolerance for high-performance distributed computation tasks](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genrel06-bp01.html)

**Amazon SageMaker AI**
- [Fine-tune models with adapter inference components](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-adapt.html)
- [Model Registration Deployment with Model Registry](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html)
- [Get recommendations for models with LoRA adapters](https://docs.aws.amazon.com/sagemaker/latest/dg/generative-ai-inference-recommendations-adapters.html)

**AWS AppConfig**
- [What is AWS AppConfig?](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html)
- [Deploying feature flags and configuration data in AWS AppConfig](https://docs.aws.amazon.com/appconfig/latest/userguide/deploying-feature-flags.html)
