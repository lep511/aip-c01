# Task 1.3 — Pipelines de validación y procesamiento de datos para consumo por FMs

[← Volver al índice](./README.md)

Skills cubiertos: **1.3.1**, **1.3.2**, **1.3.3**, **1.3.4**.

---

## Skill 1.3.1 — Workflows de validación de calidad de datos

> *Crear workflows completos de validación de datos para asegurar que los datos cumplen estándares de calidad para consumo por FMs (por ejemplo, AWS Glue Data Quality, SageMaker Data Wrangler, funciones Lambda personalizadas, métricas de Amazon CloudWatch).*

### AWS Glue Data Quality

De [AWS Glue Data Quality](https://docs.aws.amazon.com/glue/latest/dg/glue-data-quality.html). Está construido sobre el framework open source **DeeQu** y ofrece una experiencia gestionada y serverless. Las reglas se escriben en **DQDL (Data Quality Definition Language)**, un lenguaje de dominio específico ([referencia DQDL](https://docs.aws.amazon.com/glue/latest/dg/dqdl.html)).

**Terminología oficial** que hay que distinguir:

| Término | Definición |
| --- | --- |
| **rule** | Expresión DQDL que comprueba una característica concreta y devuelve un booleano |
| **analyzer** | Expresión DQDL que recolecta estadísticas de datos, usables por algoritmos de ML para detectar anomalías a lo largo del tiempo |
| **ruleset** | Recurso de AWS Glue con un conjunto de reglas; debe asociarse a una tabla del Data Catalog. Al guardarlo recibe un ARN |
| **data quality score** | Porcentaje de reglas que pasan al evaluar un ruleset |
| **observation** | Insight no confirmado que genera Glue analizando estadísticas de reglas y analyzers en el tiempo |

**Dos puntos de entrada** con capacidades distintas:

| Característica | Data Quality para el Data Catalog | Data Quality para ETL jobs |
| --- | --- | --- |
| Enfoque | Evaluar objetos ya catalogados; pensado para data stewards y analistas sin código | **Proactivo**: filtrar datos malos *antes* de cargarlos al data lake |
| Recomendación automática de reglas | Soportado | No soportado |
| Autoría y ejecución de reglas DQDL | Soportado | Soportado |
| Auto scaling | No soportado | Soportado |
| AWS Glue Flex | No soportado | Soportado |
| Identificar los registros que fallaron | **No soportado** | **Soportado** |
| Calidad de datos incremental | Vía pushdown predicates | Vía AWS Glue bookmarks |
| Scheduling | Al evaluar reglas y vía Step Functions | Vía Step Functions y workflows |
| Integración EventBridge / CloudWatch | Soportado | Soportado |
| Escribir resultados a S3 | Soportado | Soportado |
| Detección de anomalías basada en ML | Soportado | Soportado |
| Reglas dinámicas | Soportado | Soportado |
| CloudFormation | Soportado | Soportado |

**Límites** que pueden aparecer en preguntas: hasta **2.000 reglas por ruleset**, tamaño de ruleset de **65 KB**, y un límite de **100.000 estadísticas por cuenta** retenidas hasta **2 años** (las estadísticas no tienen coste de almacenamiento).

**Consideración clave**: las reglas de calidad **no pueden evaluar fuentes anidadas o de tipo lista**. Hay que aplanar primero con la transformación [Flatten nested structs](https://docs.aws.amazon.com/glue/latest/dg/transforms-flatten.html).

Otros datos útiles: hay más de **25 reglas out-of-the-box**, incluidas reglas para validar integridad referencial entre dos datasets, comparar datos entre datasets y comprobar tipos de dato. Soporta S3, Amazon Redshift, fuentes JDBC compatibles con el Data Catalog y formatos de data lake transaccional (Apache Iceberg, Apache Hudi, Delta Lake). Las vistas de Athena catalogadas en Glue **no** están soportadas.

### SageMaker Data Wrangler

[SageMaker Data Wrangler](https://docs.aws.amazon.com/sagemaker/latest/dg/data-wrangler.html) genera el **Data Quality and Insights Report**, que verifica automáticamente la calidad de los datos y detecta anomalías: completitud del dataset, valores ausentes, outliers y poder predictivo de las features. Ver [Get Insights On Data and Data Quality](https://docs.aws.amazon.com/sagemaker/latest/dg/data-wrangler-data-insights.html).

Existe además un [widget interactivo de preparación de datos](https://docs.aws.amazon.com/sagemaker/latest/dg/data-wrangler-interactively-prepare-data-notebook.html) para notebooks que ofrece visualizaciones, insights de calidad con severidad, y transformaciones integradas sobre dataframes de pandas.

### Lambda y CloudWatch en el pipeline de validación

| Componente | Rol |
| --- | --- |
| **AWS Lambda** | Validaciones personalizadas que DQDL no cubre: formato de campos, longitud de texto frente al context window, detección de idioma, comprobación de encoding, validación de esquema JSON |
| **Amazon CloudWatch metrics** | Publicar métricas personalizadas (`PutMetricData`) con el data quality score, porcentaje de registros rechazados, documentos por encima del límite de tamaño de ingesta |
| **CloudWatch alarms** | Disparar alertas o detener el pipeline cuando el score baja de un umbral |
| **Amazon EventBridge** | Reaccionar a resultados de Glue Data Quality y encadenar remediación |
| **AWS Step Functions** | Orquestar el workflow completo y programar evaluaciones |

### Arquitectura de referencia

```
Fuentes ──► S3 (raw)
              │
              ▼
        AWS Glue Data Quality (ruleset DQDL en job ETL)
              │  · identifica registros fallidos
              ├──► S3 (quarantine)   ← datos malos aislados
              │
              ├──► CloudWatch metrics + EventBridge
              │
              ▼
        Lambda (validaciones específicas de FM:
                tamaño, encoding, esquema, idioma)
              │
              ▼
        S3 (curated) ──► ingesta a Bedrock Knowledge Bases
```

**Criterios de calidad propios del consumo por FMs** que hay que validar además de los clásicos:

- Tamaño de archivo frente al límite de **Ingestion job file size** de las [cuotas de Bedrock](https://docs.aws.amazon.com/general/latest/gr/bedrock.html).
- Formato de documento entre los [formatos soportados](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-ds.html).
- Archivos de metadatos: mismo nombre base que el documento con `.metadata.json` añadido, en la misma carpeta, y **máximo 10 KB**.
- Contenido dentro del context window del modelo.
- PII detectada y tratada antes de indexar (Amazon Macie, Comprehend PII, sensitive information filters de Guardrails).

---

## Skill 1.3.2 — Procesamiento de tipos de datos complejos

> *Crear workflows de procesamiento de datos para manejar tipos de datos complejos, incluyendo texto, imagen, audio y datos tabulares, con requisitos de procesamiento especializados para consumo por FMs (por ejemplo, modelos multimodales de Amazon Bedrock, SageMaker Processing, AWS Transcribe, arquitecturas avanzadas de pipeline multimodal).*

### Knowledge bases multimodales: dos enfoques

De [Build a knowledge base for multimodal content](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-multimodal.html). Soporta imágenes, audio y vídeo junto a documentos de texto.

| Enfoque | Qué hace | Cuándo |
| --- | --- | --- |
| **Nova Multimodal Embeddings** | Preserva el formato nativo. Imágenes, audio y vídeo se embeben **directamente sin convertir a texto**. Habilita búsqueda por similitud visual y consultas con imagen como query | Matching de producto, búsqueda por similitud visual, recuperación de imágenes |
| **Bedrock Data Automation (BDA)** | Convierte multimedia a representaciones de texto: audio transcrito con **ASR**, vídeo procesado para extraer resúmenes de escena y transcripciones, imágenes con **OCR** y extracción de contenido visual | Contenido basado en habla; permite `RetrieveAndGenerate` sobre el texto resultante |

**Pipeline de ingesta multimodal** según la documentación:

1. **Conexión de data source** — S3 o custom data source (los demás tipos de connector **omiten** los archivos multimodales durante la ingesta).
2. **Detección de tipo de archivo** por extensión, y enrutamiento al pipeline adecuado.
3. **Procesamiento de contenido** con Nova Multimodal Embeddings o BDA.
4. **Generación de embeddings** con el modelo seleccionado.
5. **Almacenamiento vectorial** junto a metadatos: referencias de archivo, timestamps para audio y vídeo, tipo de contenido.
6. **Multimodal storage opcional** — copiar los archivos originales a un destino dedicado para recuperación fiable, garantizando disponibilidad aunque los originales se modifiquen o borren.

**Chunking multimodal** — de [How content chunking works](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html):

- Con **Nova multimodal embeddings**, el chunking ocurre **a nivel del modelo de embedding**. La duración de chunk de audio y vídeo es configurable entre **1 y 30 segundos** (por defecto **5 segundos**). Para archivos de vídeo solo aplica la duración de chunk de vídeo, incluso si el vídeo contiene audio; la duración de audio solo aplica a archivos de audio independientes.
- Con el **parser BDA**, el contenido se convierte primero a texto y luego se aplican las estrategias de chunking de texto estándar.
- Las estrategias de chunking de texto configuradas **solo afectan a documentos de texto** cuando se usa Nova multimodal embeddings, no a audio, vídeo ni imágenes.

**Capacidades de query** documentadas: consultas con imagen, recuperación de contenido de audio con referencias de timestamp, extracción de segmentos de vídeo con timestamps precisos, búsqueda cross-modal y referencias de fuente con metadatos temporales.

> **Aviso operativo de la doc**: el sistema devuelve referencias al archivo completo con metadatos de timestamp. **Tu aplicación debe extraer y reproducir el segmento concreto** a partir de los timestamps de inicio y fin. La consola lo hace automáticamente.

`RetrieveAndGenerate` sobre contenido multimodal está soportado cuando se usa procesamiento **BDA** o cuando la knowledge base contiene contenido de texto.

### Opciones de parsing

De [Supported models and Regions for parsing](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html) y [Parsing options for your data source](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html):

- **Parser por defecto** para texto.
- **Foundation model como parser**: familias de modelos con visión — Claude vision, Nova vision, Llama 4 vision.
- **Bedrock Data Automation parser**: disponible en US West (Oregon), en preview y sujeto a cambios.

Se puede usar un **inference profile** para el parsing de información no textual en un data source, lo que permite cross-Region inference y tracking de coste en la fase de ingesta.

### SageMaker Processing

De [Data transformation workloads with SageMaker Processing](https://docs.aws.amazon.com/sagemaker/latest/dg/processing-job.html). Ejecuta pre y post procesamiento, feature engineering y evaluación de modelos como **processing jobs** en infraestructura totalmente gestionada.

| Aspecto | Detalle |
| --- | --- |
| Contenedores | Built-in o propios para lógica de procesamiento personalizada |
| Entrada | Los datos deben estar en **Amazon S3**; alternativamente **Athena** o **Amazon Redshift** como fuentes |
| Salida | Al bucket S3 que especifiques |
| Ciclo de vida | SageMaker AI lanza las instancias, procesa, y **libera los recursos al terminar** |
| API | `CreateProcessingJob` |
| Monitoreo | CloudWatch con métricas de CPU, GPU, memoria, memoria GPU y disco, más logging de eventos |
| Distribuido | Soporta procesamiento distribuido con Spark |

Aporta las capacidades de seguridad y compliance integradas en SageMaker AI, lo que lo hace apropiado para procesar datos sensibles antes de indexarlos.

### Servicios de AI especializados por modalidad

| Modalidad | Servicio | Uso en el pipeline |
| --- | --- | --- |
| Audio → texto | [Amazon Transcribe](https://docs.aws.amazon.com/transcribe/latest/dg/what-is.html) | Transcribir llamadas, reuniones y podcasts antes de indexar |
| Documento escaneado / formulario → texto estructurado | [Amazon Textract](https://docs.aws.amazon.com/textract/latest/dg/what-is.html) | OCR con estructura: formularios y tablas |
| Imagen → etiquetas y texto | [Amazon Rekognition](https://docs.aws.amazon.com/rekognition/latest/dg/what-is.html) | Detección de objetos, moderación, texto en imagen |
| Texto → entidades, sentimiento, PII | [Amazon Comprehend](https://docs.aws.amazon.com/comprehend/latest/dg/what-is.html) | Enriquecer metadatos, detectar PII |
| Multimodal end-to-end | Bedrock Data Automation | Convertir audio, vídeo e imágenes a texto en una sola integración |

### Arquitectura multimodal avanzada

```
S3 (landing, multi-formato)
   │
   ├─ .txt .pdf .docx ──────────────► parser de texto / FM parser (visión)
   │
   ├─ .png .jpg ───┬─ Nova Multimodal Embeddings (nativo, búsqueda visual)
   │               └─ BDA (OCR + extracción visual → texto)
   │
   ├─ .mp3 .wav ───┬─ Nova Multimodal Embeddings (chunks 1-30 s, def. 5 s)
   │               └─ BDA / Amazon Transcribe (ASR → transcripción)
   │
   ├─ .mp4 ────────┬─ Nova Multimodal Embeddings (chunk de vídeo)
   │               └─ BDA (resúmenes de escena + transcripción)
   │
   └─ .csv tabular ──► SageMaker Processing (limpieza, agregación)
                       └─ documentStructureConfiguration para columnas indexadas
   │
   ▼
Embeddings ──► vector store (+ metadatos: URI fuente, timestamps, tipo de contenido)
   │
   └─ multimodal storage destination (copia de originales, opcional)
```

---

## Skill 1.3.3 — Formatear la entrada según los requisitos del modelo

> *Formatear datos de entrada para inferencia de FM según requisitos específicos del modelo (por ejemplo, formato JSON para peticiones de la API de Amazon Bedrock, preparación de datos estructurados para endpoints de SageMaker AI, formato conversacional para aplicaciones de diálogo).*

### Converse API: estructura de la petición

De [Inference using Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html).

| Campo | Función |
| --- | --- |
| `modelId` | **Obligatorio, en la cabecera**. Recurso a usar: modelo, inference profile o prompt router |
| `messages` | Array de objetos `Message` con `role` y `content` |
| `system` | System prompts: instrucciones o contexto para el modelo |
| `inferenceConfig` | Parámetros de inferencia comunes a todos los modelos |
| `additionalModelRequestFields` | Parámetros específicos del modelo concreto |
| `promptVariables` | Valores para las variables de un prompt de Prompt management |
| `guardrailConfig` | Guardrail a aplicar a todo el prompt |
| `toolConfig` | Herramientas disponibles para el modelo |
| `additionalModelResponseFieldPaths` | Campos extra a devolver, como JSON pointer |
| `serviceTier` | Service tier para la petición |
| `requestMetadata` | Metadatos filtrables en los invocation logs |

### El objeto Message y los ContentBlock

`Message` tiene `role` (`user` para el prompt, `assistant` para la respuesta del modelo) y `content`, que es un array de `ContentBlock`. **El contexto conversacional se mantiene incluyendo todos los mensajes de la conversación en las peticiones siguientes**, usando `role` para indicar el emisor.

> Nota de la documentación: Amazon Bedrock **no almacena** el texto, imágenes ni documentos que envías como contenido; los datos solo se usan para generar la respuesta.

**Bloque de texto**

```json
{
  "role": "user",
  "content": [
    { "text": "string" }
  ]
}
```

**Bloque de imagen** — bytes en base64 (los SDK de AWS lo hacen por ti). Si omites el campo `text`, el modelo describe la imagen.

```json
{
  "role": "user",
  "content": [
    {
      "image": {
        "format": "png",
        "source": { "bytes": "image in bytes" }
      }
    }
  ]
}
```

Alternativa con URI de S3, evitando enviar los bytes en el cuerpo:

```json
{
  "role": "user",
  "content": [
    {
      "image": {
        "format": "png",
        "source": {
          "s3Location": {
            "uri": "s3://amzn-s3-demo-bucket/myImage",
            "bucketOwner": "111122223333"
          }
        }
      }
    }
  ]
}
```

**Bloque de documento** — restricciones que suelen aparecer en el examen:

- En el mismo `content` **hay que incluir también un campo `text`** con un prompt relacionado con el documento.
- Bytes en base64 en `bytes` (no necesario si usas un SDK).
- El campo `name` solo admite caracteres alfanuméricos, espacios (no más de uno consecutivo), guiones, paréntesis y corchetes.
- **Advertencia de seguridad oficial**: el campo `name` es **vulnerable a prompt injection**, porque el modelo podría interpretarlo como instrucciones. AWS recomienda usar un nombre neutro.
- Activando el tag `citations` se obtienen citas específicas del documento en la respuesta ([DocumentBlock](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_DocumentBlock.html)).

```json
{
  "role": "user",
  "content": [
    { "text": "string" },
    {
      "document": {
        "format": "pdf",
        "name": "MyDocument",
        "source": { "bytes": "document in bytes" }
      }
    }
  ]
}
```

Qué bloques soporta cada modelo se consulta en [models at a glance](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html).

### Restricciones al usar un prompt de Prompt management con Converse

Cuando `modelId` apunta a un prompt gestionado:

- **No** se pueden incluir `additionalModelRequestFields`, `inferenceConfig`, `system` ni `toolConfig`.
- Si incluyes `messages`, esos mensajes **se añaden después** de los mensajes definidos en el prompt.
- Si incluyes `guardrailConfig`, el guardrail se aplica a todo el prompt; si usas bloques `guardContent` dentro de `ContentBlock`, el guardrail se aplica **solo a esos bloques**.

### Converse vs InvokeModel

| | `Converse` / `ConverseStream` | `InvokeModel` / `InvokeModelWithResponseStream` |
| --- | --- | --- |
| Formato | Unificado entre modelos | **JSON nativo de cada modelo** |
| Portabilidad de código | Alta: se escribe una vez | Baja: cambia por modelo |
| Tool use | Soportado | Soportado (client-side) |
| Guardrails | Soportado | Soportado |
| Cuándo usarlo | Por defecto, y siempre que se quiera cambiar de modelo sin tocar código | Cuando se necesita un campo del modelo no expuesto por Converse |

Ambos grupos de operaciones tienen [restricciones de API](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-api-restrictions.html) que conviene revisar.

### Formato conversacional histórico

De [Prompt engineering concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html): al acceder a los modelos por API, **los modelos no recuerdan prompts ni peticiones anteriores** salvo que la interacción previa se incluya en el prompt actual. Para modelos Anthropic Claude invocados directamente por API, el prompt debe contener `\n\nHuman:` y `\n\nAssistant:`. Para conversación con Titan se usa el formato `User: {{}} \n Bot:`. Con la Converse API esta gestión de turnos la resuelve el array `messages`.

### Endpoints de SageMaker AI

La invocación se hace con `invoke_endpoint`, pasando `Body` como JSON y `ContentType`. El esquema del payload depende del contenedor de serving, no de Bedrock:

```python
response = sm_rt_client.invoke_endpoint(
    EndpointName=endpoint_name,
    InferenceComponentName=adapter_ic_name,   # opcional: adapter LoRA
    Body=json.dumps({
        "inputs": prompt,
        "parameters": {"max_new_tokens": 100, "temperature": 0.9}
    }),
    ContentType="application/json",
)
```

> **Dato cruzado importante**: si usas un modelo de SageMaker AI o un modelo personalizado como generador en una knowledge base, **debes especificar los prompts de orchestration y generation**, y esos prompts deben incluir las variables de información necesarias para acceder a la entrada del usuario y al contexto. Ver [Supported models and Regions for knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html).

### Salida estructurada

Cuando la aplicación downstream necesita JSON válido y no texto libre, la vía oficial es [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html), que además se puede combinar con tool use.

---

## Skill 1.3.4 — Mejorar la calidad de la entrada

> *Mejorar la calidad de los datos de entrada para mejorar la calidad y consistencia de la respuesta del FM (por ejemplo, usar Amazon Bedrock para reformatear texto, Amazon Comprehend para extraer entidades, funciones Lambda para normalizar datos).*

### Amazon Comprehend

De [What is Amazon Comprehend?](https://docs.aws.amazon.com/comprehend/latest/dg/what-is.html). Usa NLP para extraer insights del contenido de documentos. Se puede ejecutar **análisis en tiempo real** para cargas pequeñas o **jobs asíncronos** para conjuntos grandes.

**Insights preentrenados** (no requieren datos de entrenamiento):

| Insight | Qué devuelve |
| --- | --- |
| **Entities** | Nombres de personas, lugares, objetos y ubicaciones |
| **Key phrases** | Frases relevantes del documento |
| **PII** | Datos personales identificables: dirección, número de cuenta, teléfono |
| **Language** | Idioma dominante del documento |
| **Sentiment** | Sentimiento dominante: positivo, neutral, negativo o mixto |
| **Targeted sentiment** | Sentimiento asociado a entidades concretas del documento |
| **Syntax** | Partes del discurso de cada palabra |

**Amazon Comprehend Custom** usa AutoML para construir modelos NLP personalizados sin necesidad de experiencia en ML:

- **Custom classification** — clasificar documentos en tus propias categorías.
- **Custom entity recognition** — reconocer términos y frases nominales específicos de tu dominio.

**Flywheels** ([doc](https://docs.aws.amazon.com/comprehend/latest/dg/flywheels.html)) orquestan el entrenamiento y la gestión de versiones de modelos custom a lo largo del tiempo, para modelos de texto plano de clasificación y reconocimiento de entidades.

**Document clustering / topic modeling** organiza un corpus en temas según frecuencia de palabras; útil para derivar taxonomías de metadatos automáticamente.

Formatos de entrada: todas las features aceptan documentos de texto **UTF-8**; además, custom classification y custom entity recognition aceptan **imágenes, PDF y Word**.

Nota de privacidad de la documentación: Amazon Comprehend **puede almacenar tu contenido** para mejorar continuamente la calidad de sus modelos preentrenados; ver la [FAQ de Amazon Comprehend](https://aws.amazon.com/comprehend/faqs/). Relevante para decisiones de compliance.

### Amazon Bedrock como preprocesador

Usar un FM para **normalizar la entrada antes de la inferencia principal** es un patrón explícito del skill:

| Tarea de preprocesamiento | Implementación |
| --- | --- |
| Reformatear texto desordenado a estructura consistente | Prompt de Bedrock con formato de salida especificado, o [structured output](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html) |
| Resumir documentos largos que exceden el context window | Prompt de resumen en un paso previo del flow |
| Traducir a un idioma común | Prompt de traducción o Amazon Translate |
| Corregir ortografía y expandir abreviaturas | Prompt de limpieza |
| Extraer campos de texto libre a JSON | Tool use o structured output |
| Reescribir la consulta del usuario antes del retrieval | Prompt de orquestación de la knowledge base, o query expansion (ver [Task 1.5 · Skill 1.5.5](./task-1-5-retrieval.md#skill-155--manejo-sofisticado-de-consultas)) |

Un modelo más pequeño y económico es suficiente para la mayoría de estas tareas: es el mismo razonamiento de coste que sustenta distillation e intelligent prompt routing.

### Lambda para normalización determinista

Lo que **no** conviene delegar a un modelo, porque debe ser exacto y reproducible:

- Normalización de fechas, monedas, unidades y husos horarios.
- Normalización de encoding y de caracteres Unicode.
- Eliminación de HTML, boilerplate, cabeceras y pies repetidos.
- Deduplicación por hash de contenido.
- Truncado seguro por límite de tokens.
- Enmascarado o hash de identificadores antes de enviarlos al modelo.
- Enriquecimiento con metadatos derivados (autor, fecha, departamento) para los filtros del vector store.

### Enriquecimiento de metadatos: el puente con Task 1.4

La salida de Comprehend se convierte en metadatos filtrables del vector store. Ejemplo de archivo `documento.pdf.metadata.json` generado por Lambda a partir de las entidades detectadas:

```json
{
  "metadataAttributes": {
    "company": {
      "value": { "type": "STRING", "stringValue": "BioPharm Innovations" },
      "includeForEmbedding": true
    },
    "created_date": {
      "value": { "type": "NUMBER", "numberValue": 20221205 },
      "includeForEmbedding": true
    },
    "author": {
      "value": { "type": "STRING", "stringValue": "Lisa Thompson" },
      "includeForEmbedding": true
    }
  }
}
```

El significado exacto de `includeForEmbedding` se detalla en [Task 1.4 · Skill 1.4.2](./task-1-4-vector-stores.md#skill-142--frameworks-de-metadatos).

### Pipeline completo de mejora de entrada

```
Documento raw
   │
   ▼
Lambda: limpieza determinista (encoding, HTML, dedup, truncado)
   │
   ▼
Amazon Comprehend: entidades, key phrases, idioma, PII
   │      └─► Macie / Guardrails PII filters si hay datos sensibles
   ▼
Lambda: construye <archivo>.metadata.json (≤ 10 KB)
   │
   ▼
Bedrock (modelo económico): reformateo / resumen si hace falta
   │
   ▼
S3 curated ──► ingesta a knowledge base ──► retrieval de mayor precisión
```

---

## Preguntas de autoevaluación

1. Necesitas saber **qué registros concretos** fallaron las reglas de calidad. ¿Qué punto de entrada de Glue Data Quality usas y por qué el otro no sirve?
2. ¿Qué hay que hacer antes de aplicar reglas DQDL a un dataset con estructuras anidadas?
3. Tienes vídeos con audio. Con Nova multimodal embeddings, ¿qué duración de chunk se aplica?
4. Quieres poder consultar la knowledge base **con una imagen** como query. ¿Qué enfoque de procesamiento multimodal eliges?
5. Vas a enviar un PDF con la Converse API. ¿Qué bloque adicional es obligatorio en el mismo `content` y qué riesgo de seguridad tiene el campo `name`?
6. Estás usando un prompt de Prompt management con `Converse`. ¿Qué cuatro campos no puedes incluir?
7. ¿Qué límite de tamaño tiene un archivo `.metadata.json` y dónde debe residir?
8. Usas un modelo de SageMaker AI como generador de una knowledge base. ¿Qué configuración adicional es obligatoria?

## Fuentes oficiales de esta sección

**AWS Glue**
- [AWS Glue Data Quality](https://docs.aws.amazon.com/glue/latest/dg/glue-data-quality.html)
- [Data Quality Definition Language (DQDL) reference](https://docs.aws.amazon.com/glue/latest/dg/dqdl.html)
- [Getting started with AWS Glue Data Quality for the Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/data-quality-getting-started.html)
- [Flatten nested structs](https://docs.aws.amazon.com/glue/latest/dg/transforms-flatten.html)

**Amazon SageMaker AI**
- [Data transformation workloads with SageMaker Processing](https://docs.aws.amazon.com/sagemaker/latest/dg/processing-job.html)
- [Prepare ML Data with Amazon SageMaker Data Wrangler](https://docs.aws.amazon.com/sagemaker/latest/dg/data-wrangler.html)
- [Get Insights On Data and Data Quality](https://docs.aws.amazon.com/sagemaker/latest/dg/data-wrangler-data-insights.html)

**Amazon Bedrock**
- [Inference using Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Prompt engineering concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html)
- [Build a knowledge base for multimodal content](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-multimodal.html)
- [Choosing your multimodal processing approach](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-multimodal-choose-approach.html)
- [How content chunking works for knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html)
- [Parsing options for your data source](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html)
- [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html)
- [Connect to Amazon S3 for your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/s3-data-source-connector.html)

**Servicios de AI**
- [What is Amazon Comprehend?](https://docs.aws.amazon.com/comprehend/latest/dg/what-is.html)
- [Amazon Comprehend Flywheels](https://docs.aws.amazon.com/comprehend/latest/dg/flywheels.html)
- [What is Amazon Transcribe?](https://docs.aws.amazon.com/transcribe/latest/dg/what-is.html)
- [What is Amazon Textract?](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)
