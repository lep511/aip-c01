# Task 3.2 — Controles de seguridad y privacidad de datos

[← Volver al índice](./README.md)

Skills cubiertos: **3.2.1**, **3.2.2**, **3.2.3**.

El recorrido de este task es el de un dato sensible: primero la red por la que viaja, luego el permiso con el que se lee, luego el filtro que lo enmascara, y por último cuánto tiempo sobrevive.

---

## Skill 3.2.1 — Entornos de IA protegidos

> *Desarrollar entornos de IA protegidos para asegurar seguridad integral de los despliegues de FM (por ejemplo, usando VPC endpoints para aislar redes, políticas IAM para imponer patrones seguros de acceso a datos, AWS Lake Formation para dar acceso granular a datos, Amazon CloudWatch para monitorizar el acceso a datos).*

### Interface VPC endpoints para Bedrock

De [Use interface VPC endpoints (AWS PrivateLink) to create a private connection between your VPC and Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html).

Lo que consigue un interface endpoint: acceder a Bedrock **como si estuviera en tu VPC**, sin internet gateway, sin NAT device, sin conexión VPN y sin Direct Connect. Las instancias de la VPC **no necesitan direcciones IP públicas**. AWS crea una **endpoint network interface en cada subnet** que habilites, son **requester-managed** y sirven como punto de entrada del tráfico destinado a Bedrock.

Las **cinco categorías de API** y su sufijo de endpoint:

| Categoría de API | Sufijo |
| --- | --- |
| Control Plane | **`bedrock`** |
| Runtime | **`bedrock-runtime`** |
| Mantle | **`bedrock-mantle`** |
| Agents Build-time | **`bedrock-agent`** |
| Agents Runtime | **`bedrock-agent-runtime`** |

Pero los **service names** que se pueden crear son **siete**, porque hay dos variantes FIPS:

```
com.amazonaws.region.bedrock
com.amazonaws.region.bedrock-runtime
com.amazonaws.region.bedrock-mantle
com.amazonaws.region.bedrock-agent
com.amazonaws.region.bedrock-agent-runtime
com.amazonaws.region.bedrock-fips              ← FIPS
com.amazonaws.region.bedrock-runtime-fips      ← FIPS
```

> **Dato decisivo**: los endpoints FIPS (`bedrock-fips` y `bedrock-runtime-fips`) **solo existen en seis Regiones**: `us-east-1`, `us-east-2`, `us-west-2`, `ca-central-1`, `us-gov-east-1` y `us-gov-west-1`. Si el requisito es módulos criptográficos validados **FIPS 140-3** y la carga vive en Europa o Asia-Pacífico, no hay endpoint FIPS disponible. Es una restricción de arquitectura, no de configuración.

Con **private DNS** habilitado no hace falta tocar el código: las llamadas usan el nombre DNS regional estándar y se enrutan por el endpoint. Sin private DNS hay que indicar la URL del endpoint de forma explícita.

Un detalle de nomenclatura que delata que Mantle es distinto: su DNS regional es **`bedrock-mantle.region.api.aws`**, no `.amazonaws.com` como los otros cuatro.

```python
import boto3

# Sin private DNS habilitado hay que apuntar explicitamente al endpoint.
# Con private DNS habilitado, basta boto3.client("bedrock-runtime").
runtime = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
    endpoint_url="https://vpce-id.bedrock-runtime.us-east-1.vpce.amazonaws.com",
)
```

### Endpoint policies: el control que casi nadie configura

Una **endpoint policy** es un recurso de IAM que se adjunta al interface endpoint. La política **por defecto permite acceso completo a Bedrock** a través del endpoint, así que sin una política personalizada el aislamiento de red no aporta autorización.

Especifica tres cosas: los principals que pueden actuar, las acciones permitidas y los recursos sobre los que se permiten.

```python
import json

import boto3

ec2 = boto3.client("ec2")

# Restringe el endpoint a inferencia: nada de operaciones de control plane.
politica = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Principal": "*",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
            ],
            "Resource": "*",
        }
    ],
}

ec2.modify_vpc_endpoint(
    VpcEndpointId="vpce-0123456789abcdef0",
    PolicyDocument=json.dumps(politica),
)
```

La base de PrivateLink y de residencia de datos está en [Task 2.3 · Skill 2.3.4](../domain-2/task-2-3-integracion-empresarial.md#skill-234--soluciones-cross-environment-y-compliance-entre-jurisdicciones). Lo que añade este skill es el mapa completo de sufijos y la advertencia de la política por defecto.

### Acceso granular a datos con Lake Formation

De [Data filtering and cell-level security in Lake Formation](https://docs.aws.amazon.com/lake-formation/latest/dg/data-filtering.html). Los tres niveles de seguridad:

| Nivel | Qué restringe | Ejemplo oficial |
| --- | --- | --- |
| **Column-level** | Qué columnas y columnas anidadas ve el usuario | Impedir que quien no trabaja en RR. HH. vea el número de la seguridad social o la fecha de nacimiento de una tabla `persons` |
| **Row-level** | Qué filas ve, según los valores de una o más columnas | Limitar a cada oficina regional de RR. HH. a los registros de empleados de su región |
| **Cell-level** | **Combina fila y columna**: restringe columnas distintas según la fila | Ocultar la columna de dirección si `country` es "UK", pero mostrarla si es "US" |

El mecanismo es el **data filter**, que se selecciona al conceder el permiso **`SELECT`**.

> **Dato decisivo**: *los filtros aplican solo a operaciones de lectura*, y por eso **el único permiso de Lake Formation que admite filtros es `SELECT`**. No se puede filtrar un `INSERT` ni un `DELETE` de esta manera.

Un data filter contiene: nombre del filtro, Catalog ID de la tabla, nombre de tabla, nombre de la base de datos, **column specification** (lista de columnas y columnas anidadas de tipo `struct` a incluir o excluir) y **row filter expression** (expresión con la sintaxis de una cláusula **`WHERE` de PartiQL**, con algunas restricciones).

La parte que se pregunta: **el nivel que obtienes depende de cómo rellenas el filtro**.

| Column specification | Row filter | Nivel resultante |
| --- | --- | --- |
| Comodín "todas las columnas" | Expresión concreta | **Row-level** solamente |
| Columnas concretas incluidas o excluidas | Comodín "todas las filas" (**`AllRowsWildcard`** en API, *Access to all rows* en consola) | **Column-level** solamente |
| Columnas concretas incluidas o excluidas | Expresión concreta | **Cell-level** |

```python
import boto3

lakeformation = boto3.client("lakeformation")

# Cell-level: excluye customer_name y solo devuelve filas de product_type 'pharma'.
lakeformation.create_data_cells_filter(
    TableData={
        "Name": "restrict-pharma",
        "DatabaseName": "sales",
        "TableName": "orders",
        "TableCatalogId": "111122223333",
        "RowFilter": {"FilterExpression": "product_type='pharma'"},
        "ColumnWildcard": {"ExcludedColumnNames": ["customer_name"]},
    }
)

# Row-level solamente: todas las columnas, filas que NO son 'pharma'.
lakeformation.create_data_cells_filter(
    TableData={
        "Name": "no-pharma",
        "DatabaseName": "sales",
        "TableName": "orders",
        "TableCatalogId": "111122223333",
        "RowFilter": {"FilterExpression": "product_type<>'pharma'"},
        "ColumnNames": ["customer_id", "customer_name", "order_num", "price"],
    }
)
```

Dos detalles de sintaxis que la documentación subraya: los literales de cadena van entre **comillas simples** (`'pharma'`), y las **columnas anidadas** se referencian con nombres cualificados entre **comillas dobles** (`"product"."offer"`), lo que evita errores cuando el nombre de columna tiene caracteres especiales y mantiene compatibilidad con las definiciones de column-level de primer nivel.

Para crear data filters hace falta permiso **`SELECT` con grant option** sobre la tabla. Los **Data Lake Administrators** lo tienen por defecto sobre todas las tablas de la cuenta.

> **Gotcha de motores**: se pueden definir data filters con cell-level security **sobre columnas anidadas**, pero los motores que soportan ejecutar consultas contra tablas anidadas gestionadas por Lake Formation con seguridad de fila y columna son **Amazon Athena, Amazon EMR y Amazon Redshift Spectrum**. Fuera de esos tres, la combinación no está soportada.

La conexión con GenAI: cuando una knowledge base o un agente consulta datos estructurados mediante el text-to-SQL del [Skill 3.1.2](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-312--seguridad-de-contenido-en-las-salidas), el filtrado de Lake Formation es lo que impide que el FM vea filas o columnas que el usuario final no debería ver. **El control de acceso se aplica en el motor de datos, no en el prompt**, que es la única forma robusta de hacerlo.

### Políticas IAM para patrones seguros de acceso a datos

> **Hueco de documentación**: no existe una página del portal dedicada a *patrones seguros de acceso a datos para FMs*. La página de [Identity and access management for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html) es la plantilla estándar del servicio. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#14-patrones-iam-de-acceso-a-datos-para-fms-sin-página-propia).

Las piezas documentadas que sí cubren el requisito, y dónde están desarrolladas:

| Pieza | Dónde |
| --- | --- |
| Federación de identidad y control de acceso basado en rol | [Task 2.3 · Skill 2.3.3](../domain-2/task-2-3-integracion-empresarial.md#skill-233--frameworks-de-acceso-seguro) |
| Permissions boundaries para acotar lo que un agente puede hacer | [Task 2.1 · Skill 2.1.3](../domain-2/task-2-1-agentic-ai-y-herramientas.md#skill-213--workflows-con-salvaguardas-y-comportamiento-controlado) |
| Endpoint policies del VPC endpoint | Este skill, más arriba |
| Data filters de Lake Formation | Este skill, más arriba |
| Cifrado con KMS y secretos en Secrets Manager | [Task 1.4](../domain-1/task-1-4-vector-stores.md) |
| Forzar un guardrail concreto en la inferencia | [`guardrails-permissions-id.html`](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions-id.html) |

Esa última merece atención: permite que una política IAM **exija** que toda invocación lleve un guardrail determinado. Sin ella, un guardrail es una recomendación que el código puede omitir; con ella, es un control obligatorio.

### Monitorizar el acceso a datos

De [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html). El model invocation logging recoge logs de invocación, datos de entrada y datos de salida de todas las invocaciones de la cuenta en una Región.

| Aspecto | Detalle |
| --- | --- |
| **Estado inicial** | **Deshabilitado por defecto**. Una vez activado, los logs se almacenan **hasta que se elimina la configuración de logging** |
| **Operaciones cubiertas** | `Converse`, `ConverseStream`, `InvokeModel`, `InvokeModelWithResponseStream` |
| **Destinos** | CloudWatch Logs, Amazon S3, o **ambos** |
| **Restricción de destino** | **Misma cuenta y misma Región** que la configuración de logging |
| **Modalidades seleccionables** | **Text, Image, Embedding, Video** |

> **Gotcha del endpoint**: el model invocation logging **solo captura llamadas hechas por el endpoint `bedrock-runtime`**, incluidas las APIs compatibles con OpenAI (Responses y Chat Completions) **en ese endpoint**. Las mismas APIs invocadas por **`bedrock-mantle` no se capturan**. Una auditoría que asuma cobertura total sobre Bedrock tiene un punto ciego si parte del tráfico va por Mantle.

> **Gotcha de modalidades**: al seleccionar una modalidad se registran los datos de **todos los modelos que la soportan**, como entrada o como salida. Elegir *Image* activa el logging para cualquier modelo que acepte o produzca imágenes, no solo para el que te interesa.

Dos detalles de configuración del destino S3: la **bucket ACL debe estar deshabilitada** para que la bucket policy surta efecto, y la policy se adjunta automáticamente en tu nombre si tienes los permisos `S3:GetBucketPolicy` y `S3:PutBucketPolicy`.

```python
import boto3

bedrock = boto3.client("bedrock")

bedrock.put_model_invocation_logging_configuration(
    loggingConfig={
        "cloudWatchConfig": {
            "logGroupName": "/aws/bedrock/modelinvocations",
            "roleArn": "arn:aws:iam::111122223333:role/BedrockLoggingRole",
            "largeDataDeliveryS3Config": {
                "bucketName": "amzn-s3-demo-bucket",
                "keyPrefix": "bedrock/large-data",
            },
        },
        "s3Config": {
            "bucketName": "amzn-s3-demo-bucket",
            "keyPrefix": "bedrock/invocations",
        },
        "textDataDeliveryEnabled": True,
        "imageDataDeliveryEnabled": True,
        "embeddingDataDeliveryEnabled": True,
        "videoDataDeliveryEnabled": False,
    }
)
```

Las métricas de CloudWatch que acompañan a esto, y la detección de accesos anómalos, se desarrollan en el [Skill 3.3.4](./task-3-3-governance-y-compliance.md#skill-334--monitorización-continua-y-controles-avanzados). El audit trail de llamadas a la API, con CloudTrail, en el [Skill 3.3.2](./task-3-3-governance-y-compliance.md#skill-332--trazabilidad-y-tracking-de-fuentes-de-datos).

---

## Skill 3.2.2 — Sistemas que preservan la privacidad

> *Desarrollar sistemas que preserven la privacidad para proteger información sensible durante las interacciones con el FM (por ejemplo, usando Amazon Comprehend y Amazon Macie para detectar información personal identificable [PII], funcionalidades nativas de privacidad de datos de Amazon Bedrock, Amazon Bedrock guardrails para filtrar salidas, configuraciones de Amazon S3 Lifecycle para implementar políticas de retención de datos).*

### Sensitive information filters

De [Remove PII from conversations by using sensitive information filters](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html). Es una solución **probabilística basada en machine learning y dependiente del contexto**: detecta información sensible según el contexto del prompt o la respuesta, no por coincidencia de patrón. Eso se puede complementar con **regex personalizadas**, que sí funcionan por pattern matching.

Dos modos:

| Modo | Comportamiento | Caso de uso oficial |
| --- | --- | --- |
| **Block** | Bloquea **todo** el contenido de la petición o respuesta y devuelve el mensaje configurado | Preguntas y respuestas generales sobre documentos públicos, donde no debería aparecer PII |
| **Mask** | Anonimiza o redacta, sustituyendo por el **tipo de PII**: `{NAME}`, `{EMAIL}` | Generar resúmenes de conversaciones entre usuarios y agentes de atención al cliente |

El filtro funciona **en lenguaje natural y en dominio de código**: sintaxis, comentarios, literales de cadena y contenido híbrido. Eso permite detectar PII incrustada en nombres de variable, **credenciales hardcodeadas** o documentación de código.

### La taxonomía completa de PII

Organizada por categorías, con las definiciones que hacen distinguibles los tipos parecidos:

| Categoría | Tipos |
| --- | --- |
| **General** | `ADDRESS`, `AGE`, `NAME`, `EMAIL`, `PHONE`, `USERNAME`, `PASSWORD`, `DRIVER_ID`, `LICENSE_PLATE`, `VEHICLE_IDENTIFICATION_NUMBER` |
| **Finance** | `CREDIT_DEBIT_CARD_CVV`, `CREDIT_DEBIT_CARD_EXPIRY`, `CREDIT_DEBIT_CARD_NUMBER`, `PIN`, `INTERNATIONAL_BANK_ACCOUNT_NUMBER`, `SWIFT_CODE` |
| **IT** | `IP_ADDRESS`, `MAC_ADDRESS`, `URL`, `AWS_ACCESS_KEY`, `AWS_SECRET_KEY` |
| **USA specific** | `US_BANK_ACCOUNT_NUMBER`, `US_BANK_ROUTING_NUMBER`, `US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER`, `US_PASSPORT_NUMBER`, `US_SOCIAL_SECURITY_NUMBER` |
| **Canada specific** | `CA_HEALTH_NUMBER`, `CA_SOCIAL_INSURANCE_NUMBER` |
| **UK specific** | `UK_NATIONAL_HEALTH_SERVICE_NUMBER`, `UK_NATIONAL_INSURANCE_NUMBER`, `UK_UNIQUE_TAXPAYER_REFERENCE_NUMBER` |
| **Custom** | **Regex filter** para patrones propios: número de serie, ID de reserva |

Las definiciones numéricas que aparecen en las preguntas:

| Tipo | Formato documentado |
| --- | --- |
| `CREDIT_DEBIT_CARD_NUMBER` | **13 a 16 dígitos**. También lo reconoce **cuando solo están los últimos cuatro** |
| `CREDIT_DEBIT_CARD_CVV` | **Tres dígitos** en VISA, MasterCard y Discover; **cuatro** en American Express |
| `PIN` | **4 o 5 dígitos** |
| `SWIFT_CODE` | **8 u 11 caracteres**. Los de **11 dígitos** identifican una **sucursal**; los de **8**, o los de 11 **terminados en `XXX`**, la **oficina principal** |
| `US_BANK_ACCOUNT_NUMBER` | Típicamente **10 a 12 dígitos** |
| `US_BANK_ROUTING_NUMBER` | Típicamente **nueve dígitos** |
| `US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER` | **Nueve dígitos**, empieza por **"9"** y tiene **"7" u "8" como cuarto dígito** |
| `US_PASSPORT_NUMBER` | **6 a 9 caracteres alfanuméricos** |
| `CA_HEALTH_NUMBER` | **10 dígitos** |
| `CA_SOCIAL_INSURANCE_NUMBER` | **Nueve dígitos** en tres grupos de tres. Validable con el **algoritmo de Luhn** |
| `UK_NATIONAL_HEALTH_SERVICE_NUMBER` | **10 a 17 dígitos**. El **dígito final es un checksum** de detección de error |
| `UK_NATIONAL_INSURANCE_NUMBER` | **Nueve caracteres**: dos letras, seis números y una letra |
| `UK_UNIQUE_TAXPAYER_REFERENCE_NUMBER` | **10 dígitos** |
| `VEHICLE_IDENTIFICATION_NUMBER` | Contenido y formato definidos en la especificación **ISO 3779** |
| `AGE` | Incluye **cantidad y unidad de tiempo**: en "tengo 40 años" reconoce "40 años" |
| `NAME` | **No incluye títulos** como Dr., Mr., Mrs. o Miss. No aplica a nombres que forman parte de organizaciones o direcciones: "John Doe Organization" es organización y "Jane Doe Street" es dirección |
| `ADDRESS` | Puede incluir calle, edificio, localización, ciudad, estado, país, condado, código postal, distrito y barrio. **Menciones aisladas de ciudad, estado o país NO cuentan como dirección válida** |

### Tres avisos que cambian el diseño

> **Hueco crítico de privacidad**: *el enmascarado de PII aplica solo al contenido enviado al modelo de inferencia y al devuelto por él*. **No aplica a los model invocation logs**: el campo `input` en CloudWatch Logs **contiene siempre la petición original sin modificar, independientemente de que el guardrail haya intervenido**. Es decir, puedes tener la PII perfectamente enmascarada de cara al usuario y volcada en claro en tus logs. La mitigación documentada es [CloudWatch log data protection](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html).

> **Segundo hueco**: el campo **`match`** de [`GuardrailPiiEntityFilter`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_GuardrailPiiEntityFilter.html), que se devuelve en las respuestas de la API, como el objeto `trace` de la Converse API, **contiene el valor original de la PII, no la salida enmascarada**. La documentación dice que es **por diseño**, para que la aplicación pueda usar el resultado de la detección en su propia lógica. Consecuencia práctica: si registras el trace completo, estás registrando la PII en claro.

> **Tercera limitación**: el filtro de **regex personalizadas no soporta lookaround**. Cualquier patrón que dependa de `(?=...)`, `(?!...)`, `(?<=...)` o `(?<!...)` no se puede expresar.

Y una recomendación de uso que afecta a la precisión: **el modelo de PII funciona mejor con contexto suficiente**. AWS recomienda explícitamente incluir más información contextual y **evitar enviar palabras sueltas o frases muy cortas**, porque la PII es dependiente del contexto: una cadena de dígitos puede ser una clave de KMS o un ID de usuario según lo que la rodee.

Recordatorio del punto ciego compartido con el [Skill 3.1.1](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-311--seguridad-de-contenido-en-las-entradas): este filtro **no evalúa `toolUse.input`, `toolResult` ni `toolSpec`**. El ejemplo que da la propia documentación es elocuente: si el modelo pasa la dirección de correo de un cliente a una herramienta que escribe un fichero, **esa dirección no se enmascara**.

### Proteger los logs: CloudWatch Logs data protection

De [Help protect sensitive log data with masking](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html). Es la pieza que cierra el hueco anterior.

| Aspecto | Detalle |
| --- | --- |
| **Mecanismo** | **Data protection policies** de log group, que auditan y enmascaran datos sensibles en los eventos ingeridos |
| **Alcance del enmascarado** | Por defecto, en **todos los puntos de egreso**: CloudWatch Logs Insights, metric filters y subscription filters |
| **Quién puede ver el dato en claro** | Solo quien tenga el permiso IAM **`logs:Unmask`** |
| **Ámbito de la política** | Toda la cuenta, o log groups individuales. La de cuenta aplica a log groups **existentes y futuros**, y si hay ambas, **se aplican las dos** de forma acumulativa |
| **Límite** | **Una** política por log group, con muchos identifiers dentro. Máximo **30.720 caracteres** por política |
| **Métrica** | **`LogEventsWithFindings`** en el namespace **`AWS/Logs`**, gratuita, apta para alarmas y dashboards |

> **Dato decisivo de orden temporal**: *los datos sensibles se detectan y enmascaran cuando se ingieren en el log group*. **Los eventos ingeridos antes de fijar la política no se enmascaran.** Activarla no limpia el histórico.

Las categorías que cubre son cinco: credentials, financial information, PII, **PHI** y **device identifiers** como direcciones IP o MAC.

### Amazon Macie: PII en reposo

De [Using managed data identifiers](https://docs.aws.amazon.com/macie/latest/user/managed-data-identifiers.html). Macie usa una **combinación de machine learning y pattern matching**, y el conjunto de criterios y técnicas se denomina **managed data identifiers**.

Las **tres categorías** que detecta:

| Categoría | Contenido |
| --- | --- |
| **Credentials** | Claves privadas, AWS secret access keys |
| **Financial information** | Números de tarjeta, números de cuenta bancaria |
| **Personal information** | **PHI** como números de seguro médico e identificación médica, y **PII** como números de licencia de conducir y de pasaporte |

> **Dato decisivo**: cada managed data identifier tiene un **ID único**, y ese ID es lo que se especifica al **crear un sensitive data discovery job** o al **configurar automated sensitive data discovery**. Las dos páginas de referencia son [Managed data identifiers recommended for sensitive data discovery jobs](https://docs.aws.amazon.com/macie/latest/user/discovery-jobs-mdis-recommended.html) y [Default settings for automated sensitive data discovery](https://docs.aws.amazon.com/macie/latest/user/discovery-asdd-settings-defaults.html).

Para algunos tipos, la detección **depende de encontrar ciertas palabras clave en proximidad** con el dato sensible. Eso está en [Keyword requirements](https://docs.aws.amazon.com/macie/latest/user/managed-data-identifiers-keywords.html).

El encaje de Macie en una arquitectura GenAI es concreto y vale como respuesta de examen: **Macie escanea S3**, y S3 es donde viven el corpus de la knowledge base, los datasets de evaluación y los model invocation logs. Macie no inspecciona prompts en vuelo, eso lo hacen los guardrails; **Macie descubre la PII que ya está almacenada**.

| Servicio | Dónde actúa | Qué protege |
| --- | --- | --- |
| **Bedrock Guardrails** | En vuelo, durante la inferencia | Prompt y respuesta |
| **Amazon Comprehend** | En vuelo, antes o después del modelo | Texto que tú le pasas |
| **Amazon Macie** | **En reposo, en S3** | Corpus, datasets, logs |
| **CloudWatch Logs data protection** | **En la ingesta del log** | Los propios logs |

### Funcionalidades nativas de privacidad de Bedrock

De [Data protection](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html) y [Data retention](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html).

**El Model Deployment Account.** En cada Región donde Bedrock está disponible hay **una cuenta de despliegue por proveedor de modelo**. Esas cuentas son propiedad del equipo de servicio de Bedrock y las opera él. Tras la entrega de un modelo por parte del proveedor, Bedrock hace un **deep copy** del software de inferencia y entrenamiento del proveedor a esas cuentas. **Los proveedores de modelos no tienen ningún acceso a esas cuentas**, y por tanto **no tienen acceso a los logs de Bedrock ni a los prompts y completions de los clientes**.

**La retención de datos**, que es la funcionalidad nativa de privacidad más concreta. Se configura **a nivel de cuenta o de proyecto**, por Región, y se aplica de forma consistente en las APIs Messages, Chat Completions y Responses. **Es por Región: no se propaga a otras.** Una Región sin configurar queda en `inherit`.

Los **cinco modos**, ordenados de menos a más permisivo:

```
none  <  default  <  aws_review  <  provider_data_share
                                    (legacy)

inherit → no opina en este ámbito, delega en uno más amplio
```

| Modo | Comportamiento |
| --- | --- |
| **`none`** | **Zero data retention**. Ni AWS escribe datos de petición o respuesta en almacenamiento durable ni se comparten con el proveedor. En la Responses API, `store` es `false` y **`store=true` se rechaza**. Background mode no disponible |
| **`default`** | Se aplica la política de retención **del modelo**. AWS puede retener datos para seguridad y prevención de abuso. El proveedor no los recibe |
| **`aws_review`** | Permite que entradas y salidas se retengan para **revisión humana por parte de AWS, dentro de la frontera de AWS**. El proveedor no revisa. **Algunos proveedores exigen esta revisión como condición de acceso a sus modelos** |
| **`provider_data_share`** | **Legacy.** Bedrock **no comparte contenido con proveedores hoy**, así que este modo concede un permiso que no se ejerce. Las configuraciones nuevas deben usar `aws_review` |
| **`inherit`** | Sin opinión en este ámbito. **Default para cuentas y proyectos nuevos** |

> **Dato decisivo**: si tu cuenta o proyecto está en **`none`** e invocas un modelo que **requiere retención**, Bedrock **bloquea la petición y devuelve un error**. La política de retención gana sobre la disponibilidad del modelo, no al contrario. Es exactamente el comportamiento que quieres en un entorno regulado, y una fuente de errores desconcertantes si no sabes que existe.

> **Gotcha de `store=false`**: poner `store=false` en la Responses API **no garantiza zero data retention**. Algunos modelos pueden seguir retiniendo datos para revisión de seguridad; en ese caso el dato se retiene pero **no es recuperable por el cliente**. Para garantía real hay que poner `data_retention_mode` en **`none`**.

**Recomendaciones de protección de datos** de la página de data protection, con las cifras que importan: se **requiere TLS 1.2** y se **recomienda TLS 1.3**; si hacen falta módulos criptográficos validados **FIPS 140-3**, hay que usar un endpoint FIPS; y una advertencia explícita de **no poner nunca información confidencial o sensible en tags ni en campos de texto libre** como un campo *Name*, porque esos datos **pueden usarse en logs de facturación y de diagnóstico**.

### Retención con S3 Lifecycle

De [Managing the lifecycle of objects](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html). Exactamente **dos tipos de acción**:

| Acción | Qué hace |
| --- | --- |
| **Transition actions** | Definen cuándo un objeto pasa a otra storage class. Ejemplo oficial: a S3 Standard-IA a los 30 días, o archivar a S3 Glacier Flexible Retrieval al año |
| **Expiration actions** | Definen cuándo expira. **S3 borra los objetos expirados en tu nombre.** Ejemplo oficial: expirar objetos tras un periodo de cumplimiento regulatorio |

> **Gotcha muy examinable**: en **general purpose buckets**, *no puedes usar una bucket policy para impedir borrados o transiciones de una regla de S3 Lifecycle*. **Aunque la bucket policy deniegue todas las acciones a todos los principals, la configuración de Lifecycle sigue funcionando con normalidad.** Si el requisito es impedir el borrado, Lifecycle no es el mecanismo de protección, es el mecanismo de borrado.

Otros detalles con consecuencias:

| Detalle | Consecuencia |
| --- | --- |
| Las reglas aplican a objetos **existentes y futuros** | Añadir hoy una regla de expiración a 30 días **encola para eliminación** los objetos que ya tienen más de 30 días |
| Los cambios de facturación se aplican **en cuanto el objeto es elegible** | Si S3 tarda en expirar un objeto, no se cobra el almacenamiento posterior al momento de expiración |
| **Excepción**: transición a **S3 Intelligent-Tiering** | Aquí el cambio de facturación **no ocurre hasta que el objeto ha transicionado realmente** |
| Las **annotations** no se gestionan de forma independiente | Se facturan siempre a tarifa S3 Standard en Frequent Access, y **cuando una regla expira un objeto se borran todas las annotations de esa versión** |
| No hay cargos de recuperación por transición | Pero **sí hay cargos de ingesta por petición** al mover datos a cualquier storage class |

```python
import boto3

s3 = boto3.client("s3")

# Retencion de model invocation logs: IA a 30 dias, Glacier a 90, borrado a 400.
s3.put_bucket_lifecycle_configuration(
    Bucket="amzn-s3-demo-bucket",
    LifecycleConfiguration={
        "Rules": [
            {
                "ID": "retencion-logs-invocacion-bedrock",
                "Status": "Enabled",
                "Filter": {"Prefix": "bedrock/invocations/"},
                "Transitions": [
                    {"Days": 30, "StorageClass": "STANDARD_IA"},
                    {"Days": 90, "StorageClass": "GLACIER"},
                ],
                "Expiration": {"Days": 400},
            }
        ]
    },
)
```

El ciclo de vida completo que pide el skill combina las dos acciones: transición inicial a Intelligent-Tiering, Standard-IA o One Zone-IA, después transición a Glacier Flexible Retrieval para archivo, y finalmente expiración.

---

## Skill 3.2.3 — Masking y anonimización manteniendo la utilidad

> *Crear sistemas de IA centrados en la privacidad para proteger la privacidad del usuario manteniendo la utilidad y efectividad del FM (por ejemplo, usando técnicas de data masking, detección de PII de Amazon Comprehend, estrategias de anonimización para información sensible, Amazon Bedrock guardrails).*

### Comprehend: localizar y redactar

De [Detecting PII entities](https://docs.aws.amazon.com/comprehend/latest/dg/how-pii.html). Comprehend detecta entidades de PII en documentos de texto **en inglés o español**, y tiene **dos modos de operación** que no son simétricos:

| Modo | Cómo se ejecuta | Qué devuelve |
| --- | --- | --- |
| **Locate** | Análisis **en tiempo real** de un documento (consola o API), **o** job asíncrono en lote sobre una colección | Lista de entidades detectadas |
| **Redact** | **Solo job asíncrono en lote** (consola o API) | Una **copia** del texto de entrada con las redacciones aplicadas |

> **Dato decisivo**: la **redacción de Comprehend no existe en tiempo real**. Solo *locate* admite análisis en tiempo real. Si el requisito es redactar PII en el camino sincrónico hacia el modelo, el patrón es: `DetectPiiEntities` en tiempo real para obtener los offsets, y **tu propio código** aplica la sustitución. La redacción automática es batch.

El límite de tiempo real: el texto de entrada puede incluir hasta **100 kilobytes de caracteres codificados en UTF-8**.

Por cada entidad detectada, la salida trae tres cosas:

| Campo | Contenido |
| --- | --- |
| **`Score`** | Probabilidad estimada de que el fragmento detectado sea de ese tipo |
| **`Type`** | El tipo de entidad de PII |
| **`BeginOffset`** / **`EndOffset`** | La **localización como offsets de carácter** de inicio y fin |

```python
import boto3

comprehend = boto3.client("comprehend")

texto = (
    "Hola Paulo Santos. El ultimo extracto de tu tarjeta de credito "
    "1111-0000-1111-0000 se envio a 123 Any Street, Seattle, WA 98109."
)

resultado = comprehend.detect_pii_entities(Text=texto, LanguageCode="es")


def enmascarar(texto: str, entidades: list[dict], umbral: float = 0.8) -> str:
    """Sustituye cada entidad por su tipo, de atras hacia delante.

    Se recorre en orden inverso para que los offsets de las entidades
    aun no procesadas sigan siendo validos tras cada sustitucion.
    """
    for entidad in sorted(entidades, key=lambda e: e["BeginOffset"], reverse=True):
        if entidad["Score"] < umbral:
            continue
        inicio, fin = entidad["BeginOffset"], entidad["EndOffset"]
        texto = f"{texto[:inicio]}{{{entidad['Type']}}}{texto[fin:]}"
    return texto


print(enmascarar(texto, resultado["Entities"]))
# Hola {NAME}. El ultimo extracto de tu tarjeta de credito {CREDIT_DEBIT_NUMBER}
# se envio a {ADDRESS}.
```

### Las dos taxonomías no son la misma

Comprehend divide sus tipos en **PII universal entity types** y **country-specific PII entity types**. Comparadas con las de Bedrock Guardrails aparecen diferencias que importan:

| Aspecto | Amazon Comprehend | Bedrock Guardrails |
| --- | --- | --- |
| **`DATE_TIME`** | **Sí**, reconoce años, meses, días, horas, fechas parciales, rangos e incluso décadas como "los años 90" | **No existe** |
| **Tipos de India** | **Sí**: `IN_AADHAAR` (12 dígitos), `IN_NREGA` (dos letras y 14 números), `IN_PERMANENT_ACCOUNT_NUMBER` (10 alfanuméricos), `IN_VOTER_NUMBER` | **No existen** |
| **Tipos de Reino Unido** | No están entre los universales | **Sí**: NHS, National Insurance, Unique Taxpayer Reference |
| **`PIN`** | **Cuatro dígitos** | **4 o 5 dígitos** |
| **Nombres de tipo de tarjeta** | `CREDIT_DEBIT_CVV`, `CREDIT_DEBIT_EXPIRY`, `CREDIT_DEBIT_NUMBER` | `CREDIT_DEBIT_CARD_CVV`, `CREDIT_DEBIT_CARD_EXPIRY`, `CREDIT_DEBIT_CARD_NUMBER` |

> **Dato decisivo**: los nombres de tipo **no son intercambiables entre servicios**, y las taxonomías no se solapan por completo. Un pipeline que use Comprehend para pre-filtrar y Guardrails para filtrar en línea **no cubre lo mismo en las dos capas**: Comprehend ve fechas e identificadores indios que Guardrails no ve, y Guardrails ve identificadores británicos que Comprehend no tiene entre los universales. Eso no es un defecto, es la razón por la que la defensa en capas del [Skill 3.1.4](./task-3-1-controles-de-seguridad-entrada-salida.md#skill-314--defensa-en-profundidad-contra-el-mal-uso-del-fm) funciona.

### La tabla de contraste que resuelve el skill

Esta es la comparación que diferencia el enfoque de 3.1.4 (capas) del de 3.2.3 (masking y anonimización):

| | **Amazon Comprehend** | **Bedrock Guardrails sensitive filters** |
| --- | --- | --- |
| **Dónde actúa** | **Fuera del modelo**, antes o después | **Inline en la inferencia** |
| **Idiomas** | **Inglés y español** | **17 idiomas**, todos *Optimized and supported* |
| **Límite de entrada** | **100 KB** UTF-8 en tiempo real | Límites de la API de Bedrock |
| **Salida de detección** | **Offsets de carácter** y **`Score`** numérico por entidad | Tipo y `match`, **sin offsets** |
| **Forma del enmascarado** | Asteriscos (`*****`) en el job de redacción; lo que tú decidas si aplicas los offsets | **Placeholder del tipo**: `{NAME}`, `{EMAIL}` |
| **Redacción en tiempo real** | **No**, solo batch | **Sí**, es el modo `Mask` |
| **Bloqueo completo** | No lo hace: detecta o redacta | **Sí**, es el modo `Block` |
| **Regex propias** | No en esta API | **Sí**, sin lookaround |
| **Detecta en código** | No documentado | **Sí**: sintaxis, comentarios, literales, credenciales hardcodeadas |
| **Umbral ajustable** | **Sí**, por `Score` en tu código | No expuesto como umbral numérico |

> El criterio de elección, en una frase: **Comprehend cuando necesitas el offset y el score para decidir tú**; **Guardrails cuando necesitas que la decisión se aplique sola dentro de la inferencia**.

### Mantener la utilidad del FM

El skill insiste en *manteniendo la utilidad y efectividad del FM*, y es la parte que se olvida. Enmascarar destruye información, y eso degrada la respuesta. Lo que la documentación permite afirmar:

| Técnica | Efecto en la utilidad |
| --- | --- |
| **Mask en lugar de Block** | Conserva la estructura de la frase. El modelo sigue entendiendo que hay un nombre, solo no sabe cuál. El caso oficial es el resumen de transcripciones de atención al cliente |
| **Placeholder tipado** (`{NAME}`) en lugar de asteriscos | Preserva la **semántica del tipo**. `{EMAIL}` le dice al modelo que ahí había un correo; `*****` no le dice nada |
| **Umbral por `Score`** con Comprehend | Permite no enmascarar detecciones de baja confianza, reduciendo el falso positivo que mutila texto legítimo |
| **Selección de tipos** en lugar de todos | Enmascarar solo los tipos que el caso de uso exige, no la taxonomía completa |
| **Contexto suficiente** | La propia documentación advierte que el modelo de PII **es peor con palabras sueltas**: recortar contexto para "proteger" empeora la detección |
| **Regex propias para IDs internos** | Un ID de reserva no es PII estándar pero puede reidentificar. El regex filter lo cubre sin tocar los tipos built-in |

```python
import boto3

bedrock = boto3.client("bedrock")

# Mask para lo que el modelo puede seguir usando de forma anonima,
# Block para lo que no debe aparecer nunca.
bedrock.create_guardrail(
    name="privacidad-transcripciones",
    blockedInputMessaging="No puedo procesar esa entrada.",
    blockedOutputsMessaging="No puedo devolver esa respuesta.",
    sensitiveInformationPolicyConfig={
        "piiEntitiesConfig": [
            # Enmascarar: el resumen sigue siendo util sin el dato real.
            {"type": "NAME", "action": "ANONYMIZE"},
            {"type": "EMAIL", "action": "ANONYMIZE"},
            {"type": "PHONE", "action": "ANONYMIZE"},
            {"type": "ADDRESS", "action": "ANONYMIZE"},
            # Bloquear: no hay caso de uso legitimo para que circulen.
            {"type": "CREDIT_DEBIT_CARD_NUMBER", "action": "BLOCK"},
            {"type": "US_SOCIAL_SECURITY_NUMBER", "action": "BLOCK"},
            {"type": "AWS_SECRET_KEY", "action": "BLOCK"},
            {"type": "PASSWORD", "action": "BLOCK"},
        ],
        "regexesConfig": [
            {
                "name": "id-reserva-interno",
                "description": "Identificador interno que permite reidentificar",
                # Sin lookaround: el filtro no lo soporta.
                "pattern": r"RSV-[0-9]{8}",
                "action": "ANONYMIZE",
            }
        ],
    },
)
```

---

## Resumen operativo del Task 3.2

| Si la pregunta menciona… | La respuesta apunta a |
| --- | --- |
| Acceso a Bedrock sin internet gateway ni NAT | **Interface VPC endpoint** con PrivateLink |
| Módulos criptográficos validados FIPS 140-3 | `bedrock-fips` o `bedrock-runtime-fips`, **solo en seis Regiones** |
| El endpoint está creado pero no restringe nada | La **endpoint policy por defecto permite acceso completo** |
| Ocultar una columna según el valor de otra | **Cell-level security** de Lake Formation |
| Todas las filas en un data filter por API | **`AllRowsWildcard`** |
| Sintaxis de la expresión de filtro de fila | Cláusula **`WHERE` de PartiQL** |
| Filtrar un `INSERT` con Lake Formation | **No se puede**: los filtros solo admiten `SELECT` |
| Columnas anidadas con cell-level security | Solo **Athena, EMR y Redshift Spectrum** |
| Tráfico de Bedrock que no aparece en los logs | Probablemente va por **`bedrock-mantle`** |
| PII enmascarada de cara al usuario pero en claro en los logs | Comportamiento **documentado**: usar **CloudWatch Logs data protection** |
| Ver el dato sin enmascarar en CloudWatch | Permiso **`logs:Unmask`** |
| La política de data protection no limpió el histórico | El enmascarado ocurre **en la ingesta**, no retroactivamente |
| Zero data retention garantizado | **`data_retention_mode: none`**, no `store=false` |
| El modelo devuelve error con retención configurada | La cuenta está en **`none`** y el modelo **exige retención** |
| Los proveedores de modelo no ven prompts | **Model Deployment Account** con deep copy |
| Impedir que Lifecycle borre objetos con una bucket policy | **No funciona** en general purpose buckets |
| Detectar PII **en reposo** en S3 | **Amazon Macie** y sus managed data identifiers |
| Necesito el offset exacto de la PII | **Comprehend**, `BeginOffset` / `EndOffset` |
| Redactar PII en el camino sincrónico | Comprehend `DetectPiiEntities` **más tu código**: la redacción de Comprehend es batch |
| Mantener la utilidad del resumen sin exponer datos | Modo **Mask** con **placeholder tipado** |
| Regex con lookahead o lookbehind | **No soportado** en el regex filter |
