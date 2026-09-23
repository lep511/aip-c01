# Task 3.3 — Mecanismos de governance y compliance de IA

[← Volver al índice](./README.md)

Skills cubiertos: **3.3.1**, **3.3.2**, **3.3.3**, **3.3.4**.

Este es el task con más desajustes entre lo que pide la guía y lo que existe en la documentación. Dos de los cuatro servicios que sostienen los skills (**SageMaker Clarify** y **SageMaker Model Monitor**) están cerrados a clientes nuevos, un tercero (**AWS Audit Manager**) también, y el *data lineage* que la guía atribuye a AWS Glue no vive en Glue. Todo queda registrado en [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación); aquí se estudia lo que la documentación sí sostiene.

---

## Skill 3.3.1 — Frameworks de compliance regulatorio

> *Desarrollar frameworks de compliance para asegurar cumplimiento regulatorio de los despliegues de FM (por ejemplo, usando SageMaker AI para desarrollar model cards programáticas, AWS Glue para rastrear data lineage automáticamente, metadata tagging para atribución sistemática de fuente de datos, CloudWatch Logs para recoger decision logs completos).*

### SageMaker Model Cards

De [Amazon SageMaker Model Cards](https://docs.aws.amazon.com/sagemaker/latest/dg/model-cards.html). El propósito documentado es **documentar detalles críticos de un modelo en un único lugar** para governance y reporting simplificados, capturando información a lo largo del ciclo de vida e implementando prácticas de IA responsable.

Los tres usos que enumera la documentación:

| Uso | Detalle |
| --- | --- |
| **Orientar** | Dar guía sobre **cómo debe usarse** el modelo |
| **Auditar** | Soportar actividades de auditoría con descripciones detalladas del entrenamiento y del rendimiento |
| **Comunicar** | Explicar cómo el modelo pretende **apoyar objetivos de negocio** |

> **Dato decisivo**: *cualquier edición que no sea una actualización del approval status genera una versión adicional del model card*, para tener un **registro inmutable de los cambios del modelo**. El cambio de estado de aprobación es la única excepción. Eso convierte el model card en evidencia de auditoría, no en un documento editable sin rastro.

Model Cards está **integrado con SageMaker Model Registry**: si registras un modelo en el Registry, puedes usar la integración para añadir información de auditoría. La base del Model Registry está en [Task 1.2 · Skill 1.2.4](../domain-1/task-1-2-seleccion-y-configuracion-fm.md#skill-124--despliegue-y-ciclo-de-vida-de-fms-personalizados).

**Intended uses**, que es la sección con valor de compliance. La recomendación oficial es incluir el propósito general del modelo, los casos de uso **para los que fue diseñado**, los casos de uso **para los que NO fue diseñado**, y los **supuestos asumidos** al desarrollarlo. La documentación insiste en que va más allá del detalle técnico: describe cómo debe usarse en producción y consideraciones adicionales como el tipo de datos a usar.

**Risk rating.** El razonamiento oficial: un modelo que aprueba solicitudes de préstamo es de mayor riesgo que uno que clasifica la categoría de un email. Los cuatro valores posibles:

```
unknown  |  low  |  medium  |  high
```

Sirven para etiquetar el modelo y **ayudar a la organización a cumplir reglas existentes sobre qué modelos pueden pasar a producción**.

### El JSON schema del model card

Los detalles de evaluación **deben ir en formato JSON**. Las secciones del esquema y sus límites, que son lo preguntable:

| Sección | Campos y límites |
| --- | --- |
| **`model_overview`** | `model_description`, `model_creator`, `algorithm_type`, `problem_type`, `model_owner` (hasta **1.024 caracteres** cada uno); `model_artifact` como array con **máximo 15 elementos** |
| **`intended_uses`** | `purpose_of_model`, `intended_uses`, `factors_affecting_model_efficiency`, `explanations_for_risk_rating` (hasta **2.048 caracteres**); `risk_rating` |
| **`business_details`** | `business_problem`, `business_stakeholders`, `line_of_business` (hasta **2.048 caracteres**) |
| **`training_details`** | `objective_function`, `training_observations`, `training_job_details` con `training_arn` y `training_datasets` |
| **`evaluation_details`** | Métricas, importables desde informes existentes |

> **Dato decisivo de integración**: si ya tienes informes de evaluación en JSON generados por **SageMaker Clarify** o **SageMaker Model Monitor**, los subes a Amazon S3 y proporcionas un **S3 URI** para que **las métricas de evaluación se parseen automáticamente**. Es el puente entre las métricas de bias del [Skill 3.4.2](./task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness) y el documento de governance.

El model card se puede **exportar a PDF** o descargar para compartir con los stakeholders.

De [`CreateModelCard`](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateModelCard.html), los límites de la API:

| Parámetro | Restricción |
| --- | --- |
| **`Content`** | **Obligatorio**. Máximo **100.000 caracteres**. Debe seguir el model card JSON schema |
| **`ModelCardName`** | Máximo **63 caracteres**, patrón `[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}` |
| **`ModelCardStatus`** | Enumerado, incluye `Draft` (trabajo en curso) y `PendingReview` (pendiente de revisión) |
| **`Tags`** | Aceptado |

```python
import json

import boto3

sagemaker = boto3.client("sagemaker")

contenido = {
    "model_overview": {
        "model_description": "Asistente de atencion al cliente basado en RAG",
        "model_creator": "Equipo de plataforma GenAI",
        "model_owner": "Direccion de Riesgos",
        "problem_type": "Generacion de texto con recuperacion",
    },
    "intended_uses": {
        "purpose_of_model": (
            "Responder preguntas sobre productos a partir del corpus documental "
            "aprobado por Legal."
        ),
        "intended_uses": "Consultas informativas de clientes en canal web.",
        # La documentacion pide explicitar tambien lo que NO esta previsto.
        "factors_affecting_model_efficiency": (
            "No previsto para asesoramiento financiero ni para decisiones de "
            "concesion de credito. Degrada con consultas fuera del corpus."
        ),
        "risk_rating": "medium",
        "explanations_for_risk_rating": (
            "No toma decisiones automatizadas, pero su salida llega al cliente "
            "sin revision humana."
        ),
    },
    "business_details": {
        "business_problem": "Reducir el tiempo de primera respuesta en soporte.",
        "business_stakeholders": "Atencion al cliente, Legal, Riesgos",
        "line_of_business": "Banca minorista",
    },
}

respuesta = sagemaker.create_model_card(
    ModelCardName="asistente-soporte-rag",
    # Content es obligatorio, va como string y tiene un tope de 100.000 caracteres.
    Content=json.dumps(contenido),
    ModelCardStatus="Draft",
    Tags=[
        {"Key": "Dominio", "Value": "GenAI"},
        {"Key": "ClasificacionRiesgo", "Value": "medium"},
    ],
)
```

El proceso de creación desde el SDK de Python, de [Create a model card](https://docs.aws.amazon.com/sagemaker/latest/dg/model-cards-create.html), usa `ModelCardStatusEnum.DRAFT` como valor por defecto si se omite, y `add_metric_group_from_json(...)` con `report_type = "clarify_bias.json"` para incorporar los informes de Clarify.

El resto del ecosistema de governance de modelos: [Model governance](https://docs.aws.amazon.com/sagemaker/latest/dg/governance.html) como hub y el [Model Dashboard](https://docs.aws.amazon.com/sagemaker/latest/dg/model-dashboard.html).

### AWS Audit Manager: el framework de GenAI

De [AWS Generative AI Best Practices Framework v2](https://docs.aws.amazon.com/audit-manager/latest/userguide/aws-generative-ai-best-practices.html).

> **Discrepancia**: la página abre con este aviso: **AWS Audit Manager ya no está abierto a clientes nuevos.** Los existentes pueden seguir usándolo. Ver [AWS Audit Manager availability change](https://docs.aws.amazon.com/audit-manager/latest/userguide/audit-manager-availability-change.html). Es el tercer servicio de este task en esa situación. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#11-audit-manager-el-framework-v1-sin-soporte-y-el-servicio-cerrado-a-clientes-nuevos).

Aun así hay que conocerlo, porque el skill lo presupone y porque **los ocho principios son la mejor taxonomía publicada de governance de GenAI en AWS**.

| Aspecto | Detalle |
| --- | --- |
| **Versión** | **v2**, publicada el **11 de junio de 2024** |
| **Qué añadió v2** | Soporte de best practices para **Amazon SageMaker AI**, además de Amazon Bedrock |
| **Estado de v1** | **Ya no está soportada.** Las assessments existentes siguen funcionando, pero **no se pueden crear nuevas** desde v1 |
| **Colaboración** | Desarrollado con expertos de IA, compliance y security assurance de AWS, **con aportación de Deloitte** |
| **Mecánica** | Cada control automatizado **mapea a una fuente de datos de AWS** de la que Audit Manager recoge evidencia |

Los **ocho principios**, con el enunciado oficial y un ejemplo de la evidencia que se recoge para cada uno:

| # | Principio | Qué exige | Evidencia de ejemplo |
| --- | --- | --- | --- |
| 1 | **Responsible** | Desarrollar y adherirse a guías éticas para despliegue y uso | Documentar origen, naturaleza, calidad y tratamiento de los datos nuevos |
| 2 | **Safe** | Establecer parámetros claros y fronteras éticas para evitar salida dañina | Evaluar el modelo con regularidad contra métricas de rendimiento predefinidas |
| 3 | **Fair** | Considerar y respetar el impacto en distintas sub-poblaciones de usuarios | Herramientas de monitorización automatizada que detecten y alerten de resultados sesgados **en tiempo real** |
| 4 | **Sustainable** | Buscar mayor eficiencia y fuentes de energía más sostenibles | Documentar escenarios donde **modelos existentes pueden reutilizarse** |
| 5 | **Resilience** | Mantener mecanismos de integridad y disponibilidad | Monitorización en tiempo real del sistema con alertas de anomalías o interrupciones |
| 6 | **Privacy** | Proteger datos sensibles de robo y exposición | Procedimientos de notificación ante **derrame de PII** o divulgación no intencionada |
| 7 | **Accuracy** | Construir sistemas exactos, fiables y robustos | Detectar inexactitudes y hacer **análisis de causa raíz** |
| 8 | **Secure** | Prevenir acceso no autorizado | **Cifrado de extremo a extremo** de datos de entrada y salida |

> **No afirmes un recuento de controles.** La documentación describe los ocho principios y agrupa los controles en control sets, pero el detalle se delega en el [control library](https://docs.aws.amazon.com/audit-manager/latest/userguide/control-library-review-standard-controls.html). Aquí no se cita ninguna cifra porque no está verificada.

Tres avisos operativos de la página que sí son concretos:

| Aviso | Consecuencia |
| --- | --- |
| Hay que ejecutar las assessments **en las cuentas y Regiones donde corren los modelos** | Una assessment en la Región equivocada no recoge evidencia |
| Para cifrar los logs de CloudWatch de Bedrock o SageMaker con KMS propio, **Audit Manager necesita acceso a esa clave** | Se configura en los ajustes de cifrado de datos de Audit Manager |
| El framework usa [`ListCustomModels`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_ListCustomModels.html), **soportado solo en `us-east-1` y `us-west-2`** | **No verás evidencia de uso de modelos personalizados** en Tokio, Singapur o Fráncfort |

Otros frameworks de la misma librería: [Framework overviews](https://docs.aws.amazon.com/audit-manager/latest/userguide/framework-overviews.html) y [Framework library](https://docs.aws.amazon.com/audit-manager/latest/userguide/framework-library.html).

### Lo que AWS Glue sí aporta

> **Discrepancia 1, la más gruesa del dominio**: el skill dice *"usando AWS Glue para rastrear data lineage automáticamente"*, pero **el AWS Glue Developer Guide no tiene ninguna página de data lineage**. El lineage automático desde bases de datos de Glue se documenta en **Amazon DataZone** y en el catálogo de SageMaker, no en Glue. Lo único que se acerca en el portal es la best practice [LSREL07-BP04 Use AWS Glue Data Catalog to maintain lineage records](https://docs.aws.amazon.com/wellarchitected/latest/life-sciences-lens/lsrel07-bp04.html), del Life Sciences Lens, que propone configurar el Data Catalog **como registro centralizado** de lineage y transformaciones. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#1-aws-glue-y-el-data-lineage-que-no-está-en-glue).

Lo que Glue sí documenta y cubre la parte de *metadata tagging* y catalogación del skill, de [Data discovery and cataloging in AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html):

| Pieza | Papel en compliance |
| --- | --- |
| **Data Catalog** | Registro central de las fuentes de datos que alimentan la knowledge base |
| **Crawlers** | Descubrimiento y actualización automática del esquema |
| [**Business context**](https://docs.aws.amazon.com/glue/latest/dg/catalog-business-context.html) | Metadatos de negocio sobre los activos técnicos |
| [**Metadata forms**](https://docs.aws.amazon.com/glue/latest/dg/catalog-metadata-forms.html) | Campos estructurados para atribución sistemática, que es literalmente lo que pide el skill |
| [**Business glossaries**](https://docs.aws.amazon.com/glue/latest/dg/catalog-business-glossaries.html) | Vocabulario controlado compartido |
| [**Semantic search**](https://docs.aws.amazon.com/glue/latest/dg/catalog-semantic-search.html) | Localización de activos por significado |

Y el **tagging**, de [AWS tags in AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/monitor-tags.html):

| Aspecto | Valor |
| --- | --- |
| **Máximo de tags por entidad** | **50** |
| **Formato** | `{"string": "string"}` |
| **Permiso necesario** | La acción **`glue:TagResource`** en la política |

### Decision logs

La parte de *CloudWatch Logs para recoger decision logs completos* se materializa con el model invocation logging, desarrollado en [Task 3.2 · Skill 3.2.1](./task-3-2-seguridad-y-privacidad-de-datos.md#skill-321--entornos-de-ia-protegidos). Los dos avisos que lo convierten en un problema de compliance y no solo de observabilidad:

> **Tensión de diseño que conviene poder explicar**: el contenido bloqueado por los guardrails **aparece en texto plano en los model invocation logs**, y el campo `input` **conserva siempre la petición original sin enmascarar**. Es decir, el log que necesitas para demostrar compliance es también el log que concentra el contenido dañino y la PII en claro. La salida documentada es [CloudWatch Logs data protection](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html) con el permiso `logs:Unmask` reservado a los auditores, no deshabilitar el logging.

### Los dos servicios cerrados a clientes nuevos

> **Discrepancia 4**: **SageMaker Clarify** y **SageMaker Model Monitor** están **cerrados a clientes nuevos**. El texto es idéntico en ambos: los clientes existentes pueden seguir usándolos con normalidad, AWS sigue invirtiendo en mejoras de seguridad y disponibilidad, pero **no hay planes de introducir funcionalidades nuevas**. Ver [Amazon SageMaker Model Monitor availability change](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-availability-change.html). Son el anclaje del *bias drift monitoring* del [Skill 3.3.4](#skill-334--monitorización-continua-y-controles-avanzados) y de las bias metrics del [Skill 3.4.2](./task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness). Registrado en [referencias-oficiales.md](./referencias-oficiales.md#4-sagemaker-clarify-y-model-monitor-cerrados-a-clientes-nuevos).

---

## Skill 3.3.2 — Trazabilidad y tracking de fuentes de datos

> *Implementar tracking de fuentes de datos para mantener trazabilidad en aplicaciones GenAI (por ejemplo, usando AWS Glue Data Catalog para registrar fuentes de datos, metadata tagging para atribución de fuente en contenido generado por el FM, AWS CloudTrail para audit logging).*

### CloudTrail con Bedrock: management events frente a data events

De [Monitor Amazon Bedrock API calls using CloudTrail](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html). Esta es la parte más examinable del skill, y también la que más ha cambiado, así que conviene fijarse en el reparto exacto.

**Los data events** son operaciones de plano de datos, de alto volumen, que **CloudTrail no registra por defecto**. Los management events sí.

| Operación | Categoría en CloudTrail |
| --- | --- |
| `InvokeModel` | **Management event** |
| `InvokeModelWithResponseStream` | **Management event** |
| `Converse` | **Management event** |
| `ConverseStream` | **Management event** |
| `ListAsyncInvokes` | **Management event** |
| `InvokeModelWithBidirectionalStream` | **Data event** |
| `GetAsyncInvoke`, `StartAsyncInvoke` | **Data event** |
| **Todas** las operaciones de Agents Runtime (`InvokeAgent`, `InvokeInlineAgent`) | **Data event** |

> **Dato decisivo**: las cuatro operaciones de inferencia habituales **sí se registran como management events**, así que aparecen sin configuración adicional. Lo que exige configuración son los agentes, las knowledge bases, los flows, los guardrails y el streaming bidireccional.

Para los data events hay que configurar **advanced event selectors** por tipo de recurso:

| Operación a registrar | `resource.type` |
| --- | --- |
| `InvokeAgent` | **`AWS::Bedrock::AgentAlias`** |
| `InvokeInlineAgent` | **`AWS::Bedrock::InlineAgent`** |
| `InvokeModelWithBidirectionalStream` | **`AWS::Bedrock::Model`** y **`AWS::Bedrock::AsyncInvoke`** |
| `GetAsyncInvoke`, `StartAsyncInvoke` | **`AWS::Bedrock::Model`** y **`AWS::Bedrock::AsyncInvoke`** |
| `Retrieve`, `RetrieveAndGenerate` | **`AWS::Bedrock::KnowledgeBase`** |
| `InvokeFlow` | **`AWS::Bedrock::FlowAlias`** |
| `RenderPrompt` | **`AWS::Bedrock::Prompt`** |
| `ApplyGuardrail`, **incluidas las evaluaciones durante la invocación del modelo** | **`AWS::Bedrock::Guardrail`** |

Dos detalles con valor de examen:

- **`RenderPrompt`** es una **acción permission-only**: no es una operación de API pública, sino el renderizado de prompts creados con Prompt Management para la invocación. Auditar el uso de prompts pasa por este data event.
- El data event de **`AWS::Bedrock::Guardrail`** cubre **las evaluaciones de guardrail que ocurren dentro de una invocación de modelo**, no solo las llamadas explícitas a `ApplyGuardrail`. Es la forma de demostrar que el guardrail se aplicó.

Desde la consola se elige **Bedrock agent alias** o **Bedrock knowledge base** como *Data event type*, y se puede filtrar además por **`eventName`** y **`resources.ARN`** con una plantilla de log selector personalizada. Desde la CLI o el SDK se fija `resource.type` y `eventCategory` a `Data`.

> **Gotcha del endpoint**: esta página documenta el logging del endpoint `bedrock-runtime.region.amazonaws.com`. Si la aplicación llama a **`bedrock-mantle.region.api.aws`**, aplica otra página distinta, [Monitor bedrock-mantle API calls using CloudTrail](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-cloudtrail-mantle.html). Es el mismo patrón que ya aparecía en el model invocation logging del [Skill 3.2.1](./task-3-2-seguridad-y-privacidad-de-datos.md#skill-321--entornos-de-ia-protegidos): **Mantle se audita por separado**.

```python
import boto3

cloudtrail = boto3.client("cloudtrail")

# Los data events de Bedrock no se registran por defecto.
cloudtrail.put_event_selectors(
    TrailName="arn:aws:cloudtrail:us-east-1:111122223333:trail/genai-audit",
    AdvancedEventSelectors=[
        {
            "Name": "Bedrock knowledge bases y guardrails",
            "FieldSelectors": [
                {"Field": "eventCategory", "Equals": ["Data"]},
                {
                    "Field": "resources.type",
                    "Equals": [
                        "AWS::Bedrock::KnowledgeBase",
                        # Cubre tambien las evaluaciones dentro de la invocacion.
                        "AWS::Bedrock::Guardrail",
                        "AWS::Bedrock::AgentAlias",
                        # Auditoria del renderizado de prompts gestionados.
                        "AWS::Bedrock::Prompt",
                    ],
                },
            ],
        }
    ],
)
```

Las evaluaciones tienen además su propia página de management events: [CloudTrail management events in model evaluation jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/cloudtrail-events-in-model-evaluations.html).

### Data lineage con Amazon DataZone

De [Data lineage in Amazon DataZone](https://docs.aws.amazon.com/datazone/latest/userguide/datazone-data-lineage.html). Es donde vive de verdad el lineage automático que el skill atribuye a Glue.

Es una funcionalidad **compatible con OpenLineage** que captura y visualiza eventos de lineage, desde sistemas habilitados para OpenLineage o mediante APIs, para **trazar orígenes de datos, seguir transformaciones y ver el consumo entre organizaciones**.

**De dónde se captura automáticamente:**

| Origen | Condición |
| --- | --- |
| Bases de datos de **AWS Glue** | Al añadirlas a Amazon DataZone |
| Bases de datos de **Amazon Redshift** | Al añadirlas a Amazon DataZone |
| Ejecuciones de **Spark ETL en AWS Glue** | **Versión 5.0 o superior**, desde consola o notebooks |

Los administradores de dominio configuran el lineage al montar los **blueprints** integrados de data lake y data warehouse, lo que asegura que **todas las ejecuciones de data source creadas desde esos recursos quedan habilitadas para captura automática**.

**Los dos tipos de nodo:**

| Nodo | Contenido |
| --- | --- |
| **Dataset node** | Información de lineage de un activo concreto. Los de Glue y Redshift publicados en el catálogo son **auto-generados** y llevan su icono; los de activos no publicados los crea manualmente el administrador |
| **Job (run) node** | Detalles del job, incluida la última ejecución y sus detalles. Captura **múltiples ejecuciones**, visibles en la pestaña **History** |

**El atributo `sourceIdentifier`** representa los eventos que ocurren sobre un dataset y se usa para **imponer unicidad**: no pueden existir dos nodos de lineage con el mismo `sourceIdentifier`. Sus formatos:

```
Asset                amazon.datazone.asset/<assetId>
Listing (publicado)  amazon.datazone.listing/<listingId>
Tabla de Glue        arn:aws:glue:<region>:<account-id>:table/<database>/<table-name>
Tabla de Redshift    arn:aws:redshift:<region>:<account-id>:table/<cluster>/<db>/<schema>/<table>
Otros datasets       <namespace>/<name> del dataset de entrada o salida
Job                  <jobs_namespace>.<job_name>
Job run              <jobs_namespace>.<job_name>/<run_id>
```

> **Gotcha**: para activos creados con la API `createAsset`, el `sourceIdentifier` **debe actualizarse con `createAssetRevision`** para poder mapear el activo a sus recursos upstream. Si no, el activo queda huérfano en el grafo.

**Lo que resuelve para compliance**, en las palabras de la documentación, son cuatro cosas, y la última es la que interesa a este dominio:

| Capacidad | Para qué |
| --- | --- |
| Entender la **procedencia** | Confianza en el dato conociendo origen, dependencias y transformaciones |
| Entender el **impacto de un cambio** | Identificar todos los consumidores downstream afectados |
| **Causa raíz** de problemas de calidad | Con **column-level lineage**, trazar el dato hacia atrás a nivel de columna |
| **Governance y compliance** | El column-level lineage **demuestra cumplimiento de regulaciones de privacidad**, mostrando **dónde se almacena el dato sensible como la PII y cómo se procesa en actividades downstream** |

> **Dato decisivo**: DataZone **versiona el lineage con cada evento**, lo que permite visualizarlo en cualquier punto del tiempo o **comparar transformaciones a lo largo del histórico** de un activo o un job. Eso es lo que convierte el lineage en evidencia de auditoría y no en una foto del estado actual.

Detalles de la visualización: el column-level lineage se expande cuando hay información de columna origen; el número de columnas mostradas por defecto es **10**, con paginación a partir de ahí; y se puede activar *Display dataset nodes only* para filtrar los nodos de job, aunque con esa vista **el grafo no se puede expandir upstream ni downstream**.

El espejo de esta funcionalidad en el catálogo de SageMaker está en [Data lineage in Amazon SageMaker Unified Studio](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/datazone-data-lineage.html), con los mismos slugs `datazone-*`, señal del movimiento de marca hacia SageMaker.

### Atribución de fuente en el contenido generado

De [Query a knowledge base and generate responses based off the retrieved data](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve-generate.html). Es la parte del skill que pide *atribución de fuente en contenido generado por el FM*.

Las operaciones son `RetrieveAndGenerate` y `RetrieveAndGenerateStream`, y `sessionId` mantiene el contexto entre turnos.

> **Deprecación**: el miembro **`citation` está deprecado** en los eventos de streaming. AWS recomienda usar **`generatedResponse`** junto con **`retrievedReferences`**. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#10-el-miembro-citation-deprecado-en-retrieveandgeneratestream).

> **Gotcha de seguridad que se solapa con el Task 3.1**: los guardrails se aplican **al input y a la respuesta generada, no a las referencias recuperadas**. Un pasaje recuperado con contenido dañino o PII llega al usuario dentro de `retrievedReferences` sin pasar por el filtro. Si la atribución de fuente se muestra en la interfaz, hay que evaluar esas referencias por separado con `ApplyGuardrail`, según el patrón del [Skill 3.1.2](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-312--seguridad-de-contenido-en-las-salidas).

```python
import boto3

agent_runtime = boto3.client("bedrock-agent-runtime")
runtime = boto3.client("bedrock-runtime")

respuesta = agent_runtime.retrieve_and_generate(
    input={"text": "¿Que comisiones tiene la cuenta corriente?"},
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": "KB123456",
            "modelArn": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        },
    },
)

texto = respuesta["output"]["text"]

# retrievedReferences sustituye al miembro citation, deprecado en streaming.
for cita in respuesta.get("citations", []):
    for referencia in cita.get("retrievedReferences", []):
        origen = referencia.get("location", {})
        fragmento = referencia.get("content", {}).get("text", "")

        # Los guardrails NO cubren las referencias recuperadas: hay que
        # evaluarlas de forma explicita antes de mostrarlas al usuario.
        veredicto = runtime.apply_guardrail(
            guardrailIdentifier="gr-123456",
            guardrailVersion="1",
            source="OUTPUT",
            content=[{"text": {"text": fragmento}}],
        )
        if veredicto["action"] == "NONE":
            print("Fuente:", origen, "|", referencia.get("metadata", {}))
```

Los metadatos que acompañan a cada referencia son los que se diseñaron en [Task 1.4 · Skill 1.4.2](../domain-1/task-1-4-vector-stores.md#skill-142--frameworks-de-metadatos): sin un framework de metadatos en la ingesta, no hay atribución que mostrar en la generación.

---

## Skill 3.3.3 — Governance organizacional

> *Crear sistemas de governance organizacional para asegurar supervisión consistente de las implementaciones de FM (por ejemplo, usando frameworks completos que alinean políticas organizacionales, requisitos regulatorios y principios de IA responsable).*

Este es el único skill del dominio que **no nombra ningún servicio**. Pide frameworks, y AWS publica tres que encajan.

### Las ocho dimensiones de IA responsable de AWS

De [Responsible AI](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/responsible-ai.html), en el Generative AI Lens. La definición: *IA responsable es la práctica de diseñar, desarrollar y usar tecnología de IA con el objetivo de maximizar beneficios y minimizar riesgos*.

| Dimensión | Definición oficial | Dónde se implementa en este dominio |
| --- | --- | --- |
| **Fairness** | Considerar los impactos en distintos grupos de stakeholders | [Skill 3.4.2](./task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness) |
| **Explainability** | Entender y evaluar las salidas del sistema | [Skill 3.4.1](./task-3-4-ia-responsable.md#skill-341--transparencia-y-reasoning-traces) |
| **Privacy and security** | Obtener, usar y proteger datos y modelos de forma apropiada | [Task 3.2](./task-3-2-seguridad-y-privacidad-de-datos.md) |
| **Safety** | Reducir la salida dañina y el mal uso | [Task 3.1](./task-3-1-controles-de-seguridad-entrada-salida.md) |
| **Controllability** | Tener mecanismos para monitorizar y dirigir el comportamiento | [Skill 3.3.4](#skill-334--monitorización-continua-y-controles-avanzados) |
| **Veracity and robustness** | Lograr salidas correctas **incluso con entradas inesperadas o adversariales** | [Skill 3.1.3](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-313--verificación-de-exactitud-y-reducción-de-hallucinations) y [Skill 3.1.5](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-315--detección-avanzada-de-amenazas-adversariales) |
| **Governance** | Incorporar best practices **en la cadena de suministro de IA**, incluidos proveedores y deployers | Este skill |
| **Transparency** | Permitir a los stakeholders **tomar decisiones informadas** sobre su interacción con el sistema | [Skill 3.4.1](./task-3-4-ia-responsable.md#skill-341--transparencia-y-reasoning-traces) |

> **Dato decisivo**: el lens dice explícitamente que algunos elementos **pesan más en GenAI que en ML tradicional**, y nombra la **veracidad** como ejemplo. Si una pregunta contrapone dimensiones, la que gana relevancia al pasar de ML clásico a GenAI es la veracidad o truthfulness.

Dos detalles de la redacción que son material de respuesta:

- En **Veracity and robustness**, la documentación nombra el **automated reasoning** como estado del arte: *conceptos que usan afirmaciones matemáticamente demostrables para capturar y corregir hallucinations en tiempo real*. Es el puente directo con Automated Reasoning checks del [Skill 3.4.3](./task-3-4-ia-responsable.md#skill-343--sistemas-conformes-a-política).
- En **Governance**, la práctica que describe es establecer **comités de governance de IA** que incluyan perspectivas técnica, de negocio y de gestión de riesgos, con documentación exhaustiva, rutas de escalado claras y procesos de revisión periódicos.

### Los códigos del Generative AI Lens

De [Security](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/security.html) del Generative AI Lens. Los seis principios de seguridad, con sus best practices:

| Código | Área | Best practices |
| --- | --- | --- |
| **GENSEC01** | Endpoint security | BP01 least privilege a endpoints de FM, BP02 comunicación privada, BP03 permisos de least privilege, BP04 access monitoring |
| **GENSEC02** | Response validation | [BP01 implementar guardrails para mitigar respuestas dañinas o incorrectas](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gensec02-bp01.html) |
| **GENSEC03** | Event monitoring | [BP01 monitorización de control plane y de acceso a datos](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gensec03-bp01.html), con **riesgo clasificado como High** |
| **GENSEC04** | Prompt security | BP01 catálogo seguro de prompts, BP02 sanear y validar entradas |
| **GENSEC05** | Excessive agency | Acotar lo que el sistema puede hacer por su cuenta |
| **GENSEC06** | Data poisoning | Proteger la integridad de los datos de entrenamiento y del corpus |

Y las de excelencia operativa relevantes para governance:

| Código | Contenido |
| --- | --- |
| **GENOPS01** | BP01 evaluación funcional periódica, BP02 recoger y monitorizar feedback de usuario |
| **GENOPS02** | BP01 monitorizar todas las capas, BP02 monitorizar métricas del FM, BP03 mitigar sobrecarga |
| **GENOPS03** | BP01 gestión de plantillas de prompt, [BP02 habilitar tracing para agentes y workflows RAG](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops03-bp02.html) |
| **GENOPS05** | BP01 cuándo personalizar el modelo |

> **GENSEC03-BP01 es la best practice con más peso de este skill**: clasificada de riesgo **High**, recomienda monitorización de plano de control **y de acceso a datos** hacia los servicios de GenAI y los FMs, con CloudTrail cubriendo management events **y data events**. Es exactamente lo que se configura en el [Skill 3.3.2](#skill-332--trazabilidad-y-tracking-de-fuentes-de-datos).

El marco equivalente para sistemas agentic es el **Agentic AI Lens**, ya desarrollado en [Task 2.1](../domain-2/task-2-1-agentic-ai-y-herramientas.md). Los códigos con carga de governance: `AGENTSEC05` (observability y non-repudiation), `AGENTSEC07` (supervisión humana y contención), `AGENTSEC08` (validación de entradas y salidas), `AGENTOPS02-BP02` (detección y remediación de config drift) y `AGENTOPS05-BP03` (logging estructurado y audit trails).

El uso del [AWS Well-Architected Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) para importar estos lenses como custom lens y ejecutar revisiones ya se cubre en [Task 1.1 · Skill 1.1.3](../domain-1/task-1-1-analisis-y-diseno.md#skill-113--componentes-estandarizados-con-well-architected).

### AI Service Cards

> **Discrepancia 8**: las AI Service Cards de AWS **existen en el portal como doc sets independientes**, con el patrón `https://docs.aws.amazon.com/ai/responsible-ai/<slug>/overview.html`, pero **no hay índice navegable** que las enumere. Verificadas individualmente, por ejemplo la de [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/ai/responsible-ai/bedrock-guardrails/overview.html) y la de [Amazon Titan Image Generator](https://docs.aws.amazon.com/ai/responsible-ai/titan-image-generator/overview.html). Registrado en [referencias-oficiales.md](./referencias-oficiales.md#8-el-índice-de-responsible-ai-y-las-ai-service-cards).

Lo que aportan a la governance organizacional: son el documento en el que **AWS, como proveedor**, declara casos de uso previstos, limitaciones y consideraciones de diseño responsable de un servicio de IA. Cierran el lado del proveedor en la *cadena de suministro de IA* que menciona la dimensión de **Governance**, mientras que los **model cards** del [Skill 3.3.1](#skill-331--frameworks-de-compliance-regulatorio) cierran el lado del deployer.

### Controles técnicos de governance organizacional

| Mecanismo | Qué impone |
| --- | --- |
| [**AWS Config conformance packs**](https://docs.aws.amazon.com/config/latest/developerguide/conformance-packs.html) | Colección de reglas de Config y acciones de remediación desplegable como una unidad, para evaluar conformidad de forma continua |
| **Audit Manager frameworks** | Recogida de evidencia mapeada a los ocho principios |
| **Well-Architected Tool con custom lens** | Revisión periódica estructurada de la carga |
| **Permissions boundaries e IAM** | Fronteras duras de lo que cualquier rol puede hacer, ver [Task 2.1 · Skill 2.1.3](../domain-2/task-2-1-agentic-ai-y-herramientas.md#skill-213--workflows-con-salvaguardas-y-comportamiento-controlado) |
| **Versiones de guardrail y de prompt** | Cambios trazables y reversibles en los controles de seguridad |
| **Model card con risk rating** | Puerta documental antes de producción |

---

## Skill 3.3.4 — Monitorización continua y controles avanzados

> *Implementar monitorización continua y controles avanzados de governance para soportar auditorías de seguridad y preparación regulatoria (por ejemplo, usando detección automatizada de misuse, drift y violaciones de política; bias drift monitoring; workflows automatizados de alerta y remediación; token-level redaction; response logging; filtros de política de salida de IA).*

### Los tres namespaces de métricas

Aquí hay un detalle que se pasa por alto y que decide si un dashboard funciona: **las métricas de Bedrock no están todas en el mismo namespace**.

| Namespace | Qué publica | Página |
| --- | --- | --- |
| **`AWS/Bedrock`** | Inferencia del endpoint `bedrock-runtime` y entrega del invocation logging | [Monitor bedrock-runtime inference](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html) |
| **`AWS/Bedrock/Guardrails`** | Todo lo de guardrails y Automated Reasoning | [Monitor Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-guardrails-cw-metrics.html) |
| Métricas de agentes | `InvocationCount`, `TotalTime`, `TTFT` | [Monitor Amazon Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-agents-cw-metrics.html) |

Y una cuarta vía, coherente con lo visto en CloudTrail y en el invocation logging: si la aplicación invoca por `bedrock-mantle`, las métricas están en [Monitor bedrock-mantle inference](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-mantle-metrics.html).

### Métricas de runtime

Namespace **`AWS/Bedrock`**:

| Métrica | Unidad | Detalle |
| --- | --- | --- |
| `Invocations` | Count | Número de peticiones **con éxito** a `Converse`, `ConverseStream`, `InvokeModel` e `InvokeModelWithResponseStream` |
| `InvocationLatency` | MilliSeconds | Desde el envío hasta el **último** token |
| `InvocationClientErrors` | Count | Errores de cliente |
| `InvocationServerErrors` | Count | Errores de servidor de AWS |
| `InvocationThrottles` | Count | Peticiones limitadas. **No cuentan ni como `Invocations` ni como errores** |
| `InputTokenCount` / `OutputTokenCount` | Count | Tokens de entrada y salida |
| `OutputImageCount` | Count | Solo en modelos de generación de imagen |
| `LegacyModelInvocations` | Count | Invocaciones a modelos en estado [**Legacy**](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_FoundationModelLifecycle.html) del ciclo de vida |
| `TimeToFirstToken` | MilliSeconds | Solo en `ConverseStream` e `InvokeModelWithResponseStream` |
| `EstimatedTPMQuotaUsage` | Count | Consumo estimado de cuota TPM |
| `CacheReadInputTokenCount` | Count | Tokens leídos del prompt cache. Tarifa reducida y **no cuentan para la cuota TPM** |
| `CacheWriteInputTokenCount` | Count | Tokens escritos al prompt cache. **Sí cuentan para la cuota TPM** |

> **Aviso oficial sobre `EstimatedTPMQuotaUsage`**: es **una aproximación** y **no refleja el consumo basado en reserva** que dirige las decisiones de throttling. El throttling se basa en la reserva por adelantado de los tokens de entrada **más `max_tokens`**. La documentación es explícita: **no usar esta métrica como único indicador** de uso de cuota ni para planificación de capacidad.

> **Dato decisivo de governance**: **`LegacyModelInvocations`** es la métrica que detecta que la aplicación sigue invocando un modelo que AWS marcó como Legacy. Es el control de *drift* más directo del ciclo de vida del modelo, y encaja con el retiro de modelos de [Task 1.2 · Skill 1.2.4](../domain-1/task-1-2-seleccion-y-configuracion-fm.md#skill-124--despliegue-y-ciclo-de-vida-de-fms-personalizados).

Las dimensiones son **`ModelId`** para todas las métricas, y **`ModelId + ImageSize + BucketedStepSize`** para `OutputImageCount`.

**Métricas de entrega del invocation logging**, también en `AWS/Bedrock` con dimensión *Across all model IDs*. Son seis, y sirven para detectar que el audit trail se está rompiendo:

```
ModelInvocationLogsCloudWatchDeliverySuccess / ...Failure
ModelInvocationLogsS3DeliverySuccess        / ...Failure
ModelInvocationLargeDataS3DeliverySuccess   / ...Failure
```

> Una alarma sobre `ModelInvocationLogsS3DeliveryFailure` es la que avisa de que la evidencia de compliance dejó de escribirse. Sin ella, el hueco se descubre durante la auditoría.

### Métricas de guardrails

Namespace **`AWS/Bedrock/Guardrails`**. Las que no son genéricas:

| Métrica | Qué mide |
| --- | --- |
| **`InvocationsIntervened`** | Número de invocaciones **en las que el guardrail intervino** |
| **`TextUnitCount`** | Unidades de texto consumidas por las políticas |
| **`FindingCounts`** | Contadores **por cada tipo de finding** de `InvokeAutomatedReasoningCheck` |
| **`TotalFindings`** | Número de findings producidos por cada petición de `InvokeAutomatedReasoningCheck` |
| **`Invocations (AutomatedReasoning)`** | Peticiones a `InvokeAutomatedReasoningCheck` |
| **`Latency`** | Latencia de la verificación con política de Automated Reasoning |

Las **dimensiones** son lo que convierte estas métricas en un sistema de governance utilizable:

| Dimensión | Valores | Para qué sirve |
| --- | --- | --- |
| **`Operation`** | `ApplyGuardrail` | Aislar las llamadas independientes |
| **`GuardrailContentSource`** | **`Input`**, **`Output`** | Saber **si el problema entra o sale**: mucho `Input` sugiere ataque, mucho `Output` sugiere modelo mal alineado |
| **`GuardrailPolicyType`** | `ContentPolicy`, `TopicPolicy`, `WordPolicy`, `SensitiveInformationPolicy`, `ContextualGroundingPolicy` | **Qué política interviene más**, disponible en `InvocationsIntervened` y `TextUnitCount` |
| **`GuardrailArn`, `GuardrailVersion`** | ARN y número de versión o `DRAFT` | Comparar versiones de guardrail y detectar tráfico contra el draft |
| **`FindingType` + `PolicyArn` + `PolicyVersion`** | — | Desglose de `FindingCounts` de Automated Reasoning |

> **Dato decisivo**: la combinación de **`InvocationsIntervened`** con la dimensión **`GuardrailPolicyType`** es el cuadro de mando de seguridad de contenido. Permite responder qué política dispara, si sube el volumen de ataques o de fugas de PII, y si un cambio de configuración redujo o aumentó las intervenciones. Y la dimensión **`GuardrailVersion` con valor `DRAFT`** delata que hay tráfico de producción evaluándose contra un borrador.

```python
import datetime

import boto3

cloudwatch = boto3.client("cloudwatch")

fin = datetime.datetime.now(datetime.UTC)
inicio = fin - datetime.timedelta(days=7)

# Intervenciones desglosadas por politica: que salvaguarda esta actuando.
respuesta = cloudwatch.get_metric_data(
    MetricDataQueries=[
        {
            "Id": f"intervenciones_{politica.lower()}",
            "MetricStat": {
                "Metric": {
                    # Ojo al namespace: los guardrails NO estan en AWS/Bedrock.
                    "Namespace": "AWS/Bedrock/Guardrails",
                    "MetricName": "InvocationsIntervened",
                    "Dimensions": [
                        {"Name": "GuardrailPolicyType", "Value": politica},
                    ],
                },
                "Period": 86400,
                "Stat": "Sum",
            },
        }
        for politica in (
            "ContentPolicy",
            "TopicPolicy",
            "WordPolicy",
            "SensitiveInformationPolicy",
            "ContextualGroundingPolicy",
        )
    ],
    StartTime=inicio,
    EndTime=fin,
)

for serie in respuesta["MetricDataResults"]:
    print(serie["Id"], sum(serie["Values"]))
```

### Response logging de las knowledge bases

De [Knowledge bases logging](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-bases-logging.html). El tipo de log es **`APPLICATION_LOGS`**, cubre los jobs de ingesta, y requiere el permiso **`bedrock:AllowVendedLogDeliveryForResource`**.

### Detección automatizada de misuse

De [Amazon Bedrock abuse detection](https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html). Es misuse detection **del lado del servicio**, no configurable por el cliente: AWS implementa mecanismos automatizados de detección de abuso, con política explícita contra material de abuso sexual infantil, y ventanas de retención de datos asociadas a esa detección.

> El matiz de examen: cuando una pregunta habla de *detección automatizada de misuse*, hay que distinguir **la que hace AWS por su cuenta** (abuse detection, no configurable, ligada a la retención de datos del [Skill 3.2.2](./task-3-2-seguridad-y-privacidad-de-datos.md#skill-322--sistemas-que-preservan-la-privacidad)) de **la que construyes tú** (`InvocationsIntervened` por política, alarmas, y el bucle de detect mode del [Skill 3.1.5](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-315--detección-avanzada-de-amenazas-adversariales)).

### Bias drift monitoring

De [Bias drift for models in production](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-monitor-bias-drift.html).

> **Aviso de disponibilidad**: **SageMaker Model Monitor ya no está abierto a clientes nuevos.** Los existentes siguen; AWS invierte en seguridad y disponibilidad pero **no planea funcionalidades nuevas**. Ver [Amazon SageMaker Model Monitor availability change](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-availability-change.html).

El problema que resuelve, y el razonamiento vale para el examen aunque el servicio esté cerrado: **medir el bias solo durante entrenamiento y despliegue puede no bastar**. Después del despliegue, la distribución de los datos en vivo puede diferir de la del dataset de entrenamiento, y eso **introduce bias con el tiempo**. El cambio puede ser temporal, por un evento de corta duración como la temporada navideña, o permanente. El ejemplo oficial: las salidas de un modelo de predicción de precios de vivienda se sesgan si los tipos hipotecarios con los que se entrenó difieren de los reales actuales.

La mecánica estadística, que es lo interesante y lo poco conocido:

| Elemento | Qué es |
| --- | --- |
| **Rango permitido `A`** | Intervalo `(a_min, a_max)` al que debe pertenecer la métrica de bias, por ejemplo `(-0.1, 0.1)` para **DPPL** |
| **Ventana `D_win`** | Los datos que el modelo procesó en la última ventana, cuya frecuencia se configura (por ejemplo, 2 días) |
| **El problema del muestreo** | `D_win` puede tener muy pocas muestras y no ser representativa. Valores muy altos o bajos pueden aparecer **puramente por azar** |
| **Intervalo de confianza `C`** | Construido con el método **Normal Bootstrap Interval**, contiene el valor real de bias con alta probabilidad |
| **La regla de alerta** | Si **`C` y `A` son disjuntos**, Clarify está seguro de que la métrica de bias no está en el rango permitido y **lanza la alerta**. Si se solapan, se interpreta que probablemente sí está dentro |

> **Dato decisivo**: la alerta **no se dispara por comparar el valor puntual con el umbral**, sino por comparar **un intervalo de confianza bootstrap con el rango permitido**. Ese diseño es lo que evita el ruido de ventanas con pocas muestras, y es la respuesta correcta si una pregunta cuestiona por qué no salta la alarma con una desviación puntual.

Las páginas hermanas: [Create a Bias Drift Baseline](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-monitor-bias-drift-baseline.html), [Bias Drift Violations](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-monitor-bias-drift-violations.html), [Parameters to Monitor Bias Drift](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-config-json-monitor-bias-parameters.html) y [Schedule Bias Drift Monitoring Jobs](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-monitor-bias-drift-schedule.html). El drift de atribución de features, en [Feature Attribution Drift](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-monitor-feature-attribution-drift.html). Los otros dos monitores son [Model Monitor](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html) para [model quality](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-model-quality.html) y [data quality](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-data-quality.html).

### Detección de drift sin umbral fijo

La alternativa documentada y disponible para todos, de [Using CloudWatch anomaly detection](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Anomaly_Detection.html):

| Concepto | Detalle |
| --- | --- |
| **Banda de valores esperados** | CloudWatch aplica modelos de machine learning a la métrica y genera un rango esperado |
| **Alarma sin umbral estático** | Se compara el valor contra **la banda**, no contra un número fijo. Se puede alertar por encima, por debajo o en ambos sentidos |
| **Recuperar la banda** | Con `GetMetricData` y la función de metric math **`ANOMALY_DETECTION_BAND`** |

Ver también [Create an anomaly detection alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Create_Anomaly_Detection_Alarm.html).

> Para una carga GenAI esto es más útil que un umbral fijo: el volumen de `InvocationsIntervened` sube y baja con el tráfico, así que "más de 100 intervenciones por hora" genera falsas alarmas. Una banda de anomalía detecta que **las intervenciones se salen del patrón habitual**, que es la señal real de un ataque o de una regresión de configuración.

Para exigir varias condiciones a la vez, las [composite alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Create_Composite_Alarm.html) combinan alarmas con una regla que usa la función `ALARM` sobre cada alarma referenciada. Útil para no despertar a nadie porque suben las intervenciones **sin** que haya subido el error rate.

### Remediación automatizada

| Pieza | Papel |
| --- | --- |
| **Alarma de CloudWatch** | Detecta la condición |
| **Amazon EventBridge** | Enruta el evento hacia la acción |
| [**Systems Manager Automation**](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html) | Ejecuta el **runbook** de remediación |
| **AWS Config conformance packs** | Evaluación continua con **acciones de remediación** incluidas en el pack |

El flujo completo que pide el skill:

```
Métrica                        Detección                  Remediación
───────────────────────────────────────────────────────────────────────────
InvocationsIntervened      ┐
  por GuardrailPolicyType  │
                           │   Alarma de anomalía
FindingCounts              ├─► sobre banda esperada  ──►  EventBridge
  de Automated Reasoning   │   (ANOMALY_DETECTION_BAND)       │
                           │                                  ▼
LegacyModelInvocations     │   Composite alarm          Runbook de SSM
                           │   (varias condiciones)     · subir fuerza de filtro
ModelInvocationLogs...     │                            · cambiar a versión previa
  DeliveryFailure          ┘                            · aislar el endpoint
                                                        · notificar por SNS
Bias drift (Clarify)       ──► C y A disjuntos          · abrir incidencia
```

### Token-level redaction y filtros de política de salida

Las dos últimas piezas del skill ya están desarrolladas en otros skills; aquí solo el mapa:

| Término del skill | Mecanismo documentado | Dónde |
| --- | --- | --- |
| **Token-level redaction** | Sensitive information filters en modo **Mask**, con placeholders `{NAME}` y `{EMAIL}` | [Skill 3.2.2](./task-3-2-seguridad-y-privacidad-de-datos.md#skill-322--sistemas-que-preservan-la-privacidad) |
| **Redacción en los logs** | CloudWatch Logs data protection con `logs:Unmask` | [Skill 3.2.2](./task-3-2-seguridad-y-privacidad-de-datos.md#skill-322--sistemas-que-preservan-la-privacidad) |
| **Response logging** | Model invocation logging con sus cuatro modalidades | [Skill 3.2.1](./task-3-2-seguridad-y-privacidad-de-datos.md#skill-321--entornos-de-ia-protegidos) |
| **AI output policy filters** | Las políticas de guardrail sobre la salida, más Automated Reasoning checks | [Skill 3.1.2](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-312--seguridad-de-contenido-en-las-salidas) y [Skill 3.4.3](./task-3-4-ia-responsable.md#skill-343--sistemas-conformes-a-política) |
| **Violaciones de política** | `InvocationsIntervened` por `GuardrailPolicyType`, y `FindingCounts` por `FindingType` | Este skill |

---

## Resumen operativo del Task 3.3

| Si la pregunta menciona… | La respuesta apunta a |
| --- | --- |
| Registro inmutable de cambios de un modelo | **Model card**: toda edición salvo el approval status crea versión |
| Etiquetar el riesgo de un modelo antes de producción | **Risk rating**: `unknown`, `low`, `medium`, `high` |
| Importar métricas de bias a un model card | Informe JSON de Clarify o Model Monitor en S3, con **S3 URI** |
| Límite del contenido de un model card | **100.000 caracteres** en `Content` |
| Los ocho principios de governance de GenAI | **Audit Manager Generative AI Best Practices Framework v2** |
| Assessments antiguas que siguen pero no se pueden crear | Framework **v1**, sin soporte desde el **11/06/2024** |
| Evidencia de modelos personalizados ausente en Fráncfort | `ListCustomModels` solo en **us-east-1 y us-west-2** |
| Data lineage automático desde bases de Glue | **Amazon DataZone**, no Glue |
| Demostrar dónde se almacena y procesa la PII | **Column-level lineage** de DataZone |
| Unicidad de un nodo de lineage | Atributo **`sourceIdentifier`** |
| `InvokeModel` no aparece en CloudTrail | Debería: es **management event**. Revisar el trail, o si el tráfico va por **Mantle** |
| Auditar `InvokeAgent` | Data event con **`AWS::Bedrock::AgentAlias`** |
| Auditar `Retrieve` y `RetrieveAndGenerate` | Data event con **`AWS::Bedrock::KnowledgeBase`** |
| Demostrar que el guardrail se aplicó en la inferencia | Data event con **`AWS::Bedrock::Guardrail`** |
| Auditar el uso de prompts gestionados | Data event con **`AWS::Bedrock::Prompt`** y la acción `RenderPrompt` |
| Atribución de fuente en la respuesta | **`retrievedReferences`**; `citation` está **deprecado** |
| Las referencias recuperadas no pasan el filtro | Correcto: los guardrails **no las cubren** |
| Métricas de guardrail que no aparecen | Están en **`AWS/Bedrock/Guardrails`**, no en `AWS/Bedrock` |
| Qué política de guardrail interviene más | `InvocationsIntervened` con dimensión **`GuardrailPolicyType`** |
| Tráfico evaluado contra un borrador | Dimensión **`GuardrailVersion`** con valor **`DRAFT`** |
| Planificar capacidad con `EstimatedTPMQuotaUsage` | **No**: es aproximada y no refleja la reserva que dirige el throttling |
| Tokens de caché y cuota TPM | **Read no cuenta**, **write sí** |
| Seguir invocando un modelo retirado | Métrica **`LegacyModelInvocations`** |
| El audit trail dejó de escribirse | Alarma sobre **`ModelInvocationLogsS3DeliveryFailure`** |
| La alerta de bias no salta con una desviación puntual | Compara **intervalo bootstrap `C`** con **rango `A`**, no el valor puntual |
| Alertar sin umbral fijo en tráfico variable | **Anomaly detection** con `ANOMALY_DETECTION_BAND` |
