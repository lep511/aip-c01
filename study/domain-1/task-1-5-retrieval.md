# Task 1.5 — Diseñar mecanismos de retrieval para augmentación de FMs

[← Volver al índice](./README.md)

Skills cubiertos: **1.5.1**, **1.5.2**, **1.5.3**, **1.5.4**, **1.5.5**, **1.5.6**.

---

## Skill 1.5.1 — Segmentación de documentos (chunking)

> *Desarrollar enfoques efectivos de segmentación de documentos para optimizar el rendimiento de recuperación para augmentación de contexto de FMs (por ejemplo, capacidades de chunking de Amazon Bedrock, funciones Lambda para chunking de tamaño fijo, procesamiento personalizado para chunking jerárquico basado en la estructura del contenido).*

De [How content chunking works for knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html). Durante la ingesta, Bedrock divide los documentos en chunks manejables, los convierte a embeddings y los escribe en el índice vectorial manteniendo el mapeo al documento original.

### Estrategias disponibles

| Estrategia | Parámetros | Comportamiento |
| --- | --- | --- |
| **Fixed-size** | `maxTokens` (máximo de tokens por chunk) y `overlapPercentage` (solape entre chunks consecutivos) | Control explícito del tamaño |
| **Default** | Ninguno | Chunks de aproximadamente **300 tokens**. **Respeta los límites de frase**, preservando frases completas en cada chunk |
| **No chunking** | Ninguno | Cada documento es **un único chunk de texto** |
| **Hierarchical** | Tamaño máximo de chunk **parent**, tamaño máximo de chunk **child**, y **tokens de solape** | Estructura anidada de dos niveles |
| **Semantic** | `maxTokens`, **buffer size**, **breakpoint percentile threshold** | Divide por significado, no por estructura sintáctica |

> **Restricción operativa clave**: la estrategia de chunking **no se puede cambiar después de conectar el data source** ([S3 connector](https://docs.aws.amazon.com/bedrock/latest/userguide/s3-data-source-connector.html)). Cambiarla implica recrear el data source.

### Detalles de fixed-size y default

Para contenido **parseado** (con parsers avanzados o convertido desde HTML), Bedrock puede ajustar el chunking para optimizar resultados: el chunker **respeta los límites lógicos del documento** (páginas, secciones) y **no fusiona contenido cruzando esas fronteras**, incluso si aumentar `maxTokens` permitiría chunks mayores.

Si eliges **no chunking**, se recomienda pre-procesar los documentos dividiéndolos en archivos separados. Consecuencia documentada: con *no chunking* **no puedes ver el número de página en las citas ni filtrar por el campo de metadatos `x-amz-bedrock-kb-document-page-number`**.

### Hierarchical chunking

Organiza la información en estructuras anidadas de chunks child y parent. **En la recuperación, el sistema recupera primero los child chunks y luego los sustituye por los parent chunks**, más amplios, para dar al modelo contexto más completo.

El razonamiento oficial: los embeddings de texto pequeño son **más precisos**, pero la recuperación busca **contexto completo**. El chunking jerárquico equilibra ambas necesidades sustituyendo child por parent cuando corresponde.

Bedrock soporta **dos niveles**: parent (tamaño máximo de token del parent) y child (tamaño máximo de token del child), más el número absoluto de tokens de solape entre parents consecutivos y entre childs consecutivos.

**Dos consecuencias que se examinan:**

1. Como los child chunks se sustituyen por parents, **el número de resultados devueltos puede ser menor que el solicitado**. El parámetro `numberOfResults` mapea al **número de child chunks** que la knowledge base recuperará; los childs que comparten parent se colapsan en ese parent.
2. **No se recomienda con S3 vector bucket**: con un número alto de tokens (más de **8000 combinados**) se pueden exceder los límites de tamaño de metadatos.

### Semantic chunking

Técnica de NLP que divide el texto en chunks con significado, buscando precisión de recuperación centrada en el contenido semántico más que en la estructura sintáctica.

| Hiperparámetro | Función | Efecto de subirlo |
| --- | --- | --- |
| **Maximum tokens** | Máximo de tokens por chunk, respetando límites de frase | Chunks mayores |
| **Buffer size** | Número de frases circundantes que se añaden para crear el embedding. Un buffer de **1** combina y embebe **3 frases**: la actual, la anterior y la siguiente | Más contexto capturado, pero puede introducir ruido. Un buffer pequeño puede perder contexto, aunque da un chunking más preciso |
| **Breakpoint percentile threshold** | Percentil de distancia o disimilitud entre frases para marcar un corte | Exige que las frases sean más distinguibles para separarse → **menos chunks y tamaño medio mayor** |

> **Coste**: semantic chunking tiene **coste adicional** porque usa un foundation model. El coste depende del volumen de datos.

### Chunking multimodal

- **Nova multimodal embeddings**: el chunking ocurre **a nivel del modelo de embedding**. Duración de chunk de audio y vídeo configurable entre **1 y 30 segundos** (por defecto **5 segundos**). En archivos de vídeo solo aplica la duración de vídeo, aunque el vídeo contenga audio; la duración de audio solo aplica a archivos de audio independientes.
- **Parser BDA**: el contenido se convierte primero a texto (transcripciones y resúmenes de escena) y luego se aplican las estrategias de chunking de texto.
- Las estrategias de chunking de texto **solo afectan a documentos de texto** cuando se usa Nova multimodal embeddings.

### Chunking personalizado con Lambda

De [Use a custom transformation Lambda function](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-custom-transformation.html). Dos modos de uso, según el objetivo:

| Objetivo | Configuración |
| --- | --- |
| **Lógica de chunking propia** no soportada nativamente | Elegir estrategia **no chunking** y especificar la función Lambda con tu lógica. Además hay que especificar un bucket S3 donde la knowledge base escribirá los archivos a chunkear |
| **Metadatos a nivel de chunk**, manteniendo chunking nativo | Elegir una estrategia predefinida (default o fixed-size) y aportar referencia a la Lambda y al bucket. La KB guarda los archivos parseados y pre-chunkeados en el bucket antes de llamar a la Lambda |

La Lambda escribe los archivos resultantes **de vuelta al mismo bucket** y devuelve referencias para que la knowledge base continúe el procesamiento. Opcionalmente se puede aportar una clave KMS propia para cifrar los archivos del bucket.

> **Precedencia**: los **metadatos a nivel de chunk tienen prioridad y sobrescriben los metadatos a nivel de archivo** en caso de colisión.
>
> **Nota sobre web connectors**: si se usan, a la Lambda se le pasa **texto markdown en lugar de HTML**.

Contrato de API:

```json
{
  "vectorIngestionConfiguration": {
    "customTransformationConfiguration": {
      "intermediateStorage": {
        "s3Location": { "uri": "string" }
      },
      "transformations": [{
        "transformationFunction": {
          "transformationLambdaConfiguration": { "lambdaArn": "string" }
        },
        "stepToApply": "POST_CHUNKING"
      }]
    },
    "chunkingConfiguration": {
      "chunkingStrategy": "string",
      "fixedSizeChunkingConfiguration": {
        "maxTokens": "number",
        "overlapPercentage": "number"
      }
    }
  }
}
```

El único valor de `stepToApply` documentado es **`POST_CHUNKING`**.

Formato de entrada a la Lambda: `version`, `knowledgeBaseId`, `dataSourceId`, `ingestionJobId`, `bucketName`, `priorTask` y `inputFiles`, donde cada entrada tiene `originalFileLocation`, `fileMetadata` y `contentBatches`. La salida replica la estructura en `outputFiles`. Los objetos referenciados contienen `fileContents` con `contentBody`, `contentType` y `contentMetadata`.

### Cómo elegir

| Situación | Estrategia |
| --- | --- |
| Documentos homogéneos, control de coste | Default (~300 tokens, respeta frases) |
| Necesitas tamaño y solape exactos | Fixed-size |
| Documentos con jerarquía clara (manuales, normativa) y necesitas contexto amplio | Hierarchical, evitando S3 Vectors |
| Documentos con temas que cambian sin estructura marcada | Semantic, asumiendo el coste del FM |
| Cada archivo es ya una unidad atómica (FAQ, ficha) | No chunking, con pre-split previo |
| Reglas de negocio de segmentación propias | No chunking + Lambda de transformación |
| Quieres metadatos por chunk | Estrategia nativa + Lambda `POST_CHUNKING` |

---

## Skill 1.5.2 — Selección y configuración de embeddings

> *Seleccionar y configurar soluciones óptimas de embedding para crear representaciones vectoriales eficientes para búsqueda semántica (por ejemplo, embeddings de Amazon Titan según dimensionalidad y ajuste de dominio, evaluando las características de rendimiento de los modelos de embedding de Amazon Bedrock, funciones Lambda para generar embeddings por lotes).*

### Modelos de embedding soportados en Knowledge Bases

De [Supported models for vector embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html):

| Proveedor | Modelo | Model ID |
| --- | --- | --- |
| Amazon | Titan Embeddings G1 – Text | `amazon.titan-embed-text-v1` |
| Amazon | Titan Text Embeddings V2 | `amazon.titan-embed-text-v2:0` |
| Cohere | Embed English | `cohere.embed-english-v3` |
| Cohere | Embed Multilingual | `cohere.embed-multilingual-v3` |

### Tipos de vector y dimensiones

| Modelo | Tipo de vector | Dimensiones soportadas |
| --- | --- | --- |
| Amazon Titan Embeddings G1 – Text | Floating-point | **1536** |
| Amazon Titan Text Embeddings V2 | Floating-point, **binary** | **256, 512, 1024** |
| Cohere Embed (English) | Floating-point, **binary** | **1024** |
| Cohere Embed (Multilingual) | Floating-point, **binary** | **1024** |
| Amazon Titan Multimodal Embeddings G1 | Floating-point | **1024** |
| Cohere Embed v3 (Multimodal) | Floating-point, **binary** | **1024** |
| Amazon Nova Multimodal Embeddings | Floating-point | **1024** |

Esta tabla es material de examen directo. Dos reglas derivadas:

1. **Las dimensiones del índice vectorial deben coincidir con las del modelo de embedding.** En Neptune Analytics esto es especialmente rígido: el índice solo se crea al crear el grafo.
2. **Los vectores binarios solo se pueden almacenar en OpenSearch Serverless y OpenSearch Managed Clusters.** Si eliges binarios, el vector store queda determinado.

### Criterios de selección

| Criterio | Cómo decidir |
| --- | --- |
| **Dominio y ajuste lingüístico** | Contenido multilingüe → Cohere Embed Multilingual o Titan V2. Contenido solo en inglés → Cohere Embed English o Titan V2 |
| **Dimensionalidad** | Titan V2 permite 1024, 512 o 256. Menos dimensiones = menos almacenamiento, memoria y latencia, a cambio de algo de precisión |
| **Tipo de vector** | Binarios reducen drásticamente almacenamiento y memoria, pero limitan el vector store a OpenSearch |
| **Multimodalidad** | Titan Multimodal G1, Cohere Embed v3 multimodal o Nova Multimodal Embeddings |
| **Disponibilidad regional** | Titan V2 es el de mayor cobertura regional del listado, incluidas Regiones GovCloud |
| **Compatibilidad con Managed KB** | Si aportas tu propio modelo a una managed KB, debe ser **float32 con 1024 dimensiones** |
| **Métrica de distancia** | OpenSearch Serverless: AWS recomienda **Euclidean** para float. S3 Vectors: **Cosine** o **Euclidean**. Aurora: `vector_cosine_ops` en el ejemplo oficial |

### Coste: reducir la longitud del vector

La best practice [GENCOST04-BP01](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost04-bp01.html) del Generative AI Lens trata explícitamente la reducción del tamaño del vector en los embeddings de datos, para disminuir tokens de salida del modelo, coste de cómputo del vector database y el TCO de la aplicación GenAI. El procedimiento es identificar y aplicar la longitud de vector más pequeña viable **verificando que la calidad de recuperación sigue siendo aceptable**.

### Generación por lotes con Lambda

Cuando no usas Bedrock Knowledge Bases y gestionas los embeddings tú mismo:

```
S3 (documentos curados)
   │
   ▼
EventBridge / SQS ──► Lambda (worker)
                         ├─ lee lote de chunks
                         ├─ InvokeModel al modelo de embedding
                         │     · agrupa varios textos por llamada donde el modelo lo permita
                         ├─ reintentos con exponential backoff ante throttling
                         └─ escribe vectores + metadatos al vector store
   │
   ▼
CloudWatch: vectores/minuto, throttles, coste estimado
```

Consideraciones prácticas: respetar las cuotas del modelo de embedding, usar SQS para desacoplar y reintentar, y mantener **idempotencia** por hash de chunk para no duplicar vectores en reintentos. Para volúmenes grandes, [batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html) es más económico que las llamadas individuales, y **SageMaker Processing** encaja para lotes masivos con cómputo distribuido.

### Embeddings dentro del propio motor de búsqueda

OpenSearch Service se integra con Amazon Bedrock para generar embeddings, y también con SageMaker AI, modelos de Hugging Face y modelos propios ([Vector search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vector-search.html)). Esto permite que el motor genere los embeddings en la ingesta y en la consulta sin código intermedio: es el enfoque al que alude el skill 1.4.1 cuando menciona el **Neural plugin**.

---

## Skill 1.5.3 — Desplegar soluciones de vector search

> *Desplegar y configurar soluciones de vector search para habilitar capacidades de búsqueda semántica para augmentación de FMs (por ejemplo, OpenSearch Service con capacidades de vector search, Amazon Aurora con la extensión pgvector, Amazon Bedrock Knowledge Bases con funcionalidad de vector store gestionado).*

La configuración detallada de cada vector store está en [Task 1.4 · Skill 1.4.1](./task-1-4-vector-stores.md#skill-141--arquitecturas-avanzadas-de-vector-database). Aquí el foco es la **decisión de despliegue**.

### Matriz de decisión

| Opción | Provisionas tú | Búsqueda híbrida | Binarios | Casos donde gana |
| --- | --- | --- | --- | --- |
| **Bedrock Managed KB** | Nada | Híbrida agéntica y semántica gestionada | — | RAG end-to-end, menos operación, connectors nativos, recuperación agéntica, integración AgentCore Gateway |
| **OpenSearch Serverless** | Collection + índice | **Sí** | **Sí** | Escala elástica, filtros ricos (`startsWith`, `listContains`), acceso privado por PrivateLink |
| **OpenSearch Managed Cluster** | Dominio + índice | Sí | **Sí** | Control fino del clúster, tiering a UltraWarm/cold. **Debe ser público** |
| **Aurora PostgreSQL + pgvector** | Clúster, tabla, índices, secreto | **Sí** | No | Ya usas PostgreSQL; vectores junto a datos relacionales y transacciones. Menor latencia de disponibilidad post-ingesta |
| **S3 Vectors** | Vector bucket + índice | No | No | Coste mínimo, consulta poco frecuente, datasets grandes, latencia sub-segundo |
| **Neptune Analytics** | Grafo con índice vectorial | No | No | GraphRAG: relaciones entre entidades además de similitud |
| **Pinecone** | Cuenta e índice en Pinecone | Según el proveedor | — | Estandarización previa en Pinecone |

**Nota sobre búsqueda híbrida**: solo está soportada en **Amazon RDS/Aurora, OpenSearch Serverless y MongoDB** con un campo de texto filtrable; con otros vector stores o sin ese campo, la consulta cae a **búsqueda semántica** ([kb-test-config](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html)).

### Aurora pgvector: puntos de despliegue críticos

- El clúster **debe estar en la misma cuenta AWS** que la knowledge base.
- Los campos de la tabla **deben existir antes de crear la knowledge base** y **no se pueden actualizar después**.
- Índices obligatorios: HNSW sobre `embedding`, GIN sobre `to_tsvector(chunks)`, y GIN sobre `custom_metadata` si usas esa columna.
- Con metadata filtering, habilitar **HNSW iterative scans** (pgvector 0.8.0+), porque sin ellos el filtrado se aplica **después** del escaneo del índice y devuelve menos resultados.
- Credenciales gestionadas en **AWS Secrets Manager**.
- Ventaja operativa documentada: con Aurora los embeddings recién ingeridos están disponibles para consulta **sin el retardo de unos minutos** que aplica a los demás vector stores.

### Cuándo la knowledge base gestionada no basta

Señales de que necesitas customer-managed:

- Necesitas una configuración de índice específica (parámetros HNSW, engine, métrica).
- Necesitas embeddings **binarios** o dimensiones distintas de 1024 float32.
- Necesitas acceso directo al vector store desde otras aplicaciones.
- Necesitas GraphRAG.
- Tienes restricciones de residencia o de red que exigen control del datastore.

---

## Skill 1.5.4 — Arquitecturas de búsqueda avanzada

> *Crear arquitecturas de búsqueda avanzada para mejorar la relevancia y precisión de la información recuperada para el contexto del FM (por ejemplo, OpenSearch para búsqueda semántica, búsqueda híbrida que combina keywords y vectores, modelos reranker de Amazon Bedrock).*

### Tipos de búsqueda en Knowledge Bases

De [Configure and customize queries and response generation](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html). El *search type* define cómo se consultan los data sources:

| Tipo | API `overrideSearchType` | Comportamiento |
| --- | --- | --- |
| **Default** | Sin valor | Amazon Bedrock decide la estrategia según la configuración de tu vector store |
| **Hybrid** | `HYBRID` | Combina búsqueda de embeddings (semántica) con búsqueda en el **texto crudo** |
| **Semantic** | `SEMANTIC` | Solo embeddings |

```json
"retrievalConfiguration": {
  "vectorSearchConfiguration": {
    "overrideSearchType": "HYBRID"
  }
}
```

En consola: panel **Configurations** → sección **Search type** → activar **Override default search**.

> **Requisito de híbrida**: soportada solo en **Amazon RDS, Amazon OpenSearch Serverless y MongoDB** con un campo de texto **filtrable**. Con otro vector store, o sin ese campo, la consulta usa búsqueda semántica.

En Aurora, para mejorar precisión y latencia de híbrida con contenido en inglés se recomienda el diccionario `'english'` en lugar de `'simple'` al crear el índice GIN.

### Número de resultados

Por defecto una consulta devuelve **hasta cinco resultados**, cada uno correspondiente a un source chunk.

```json
"retrievalConfiguration": {
  "vectorSearchConfiguration": {
    "numberOfResults": 10
  }
}
```

`numberOfResults` es un **máximo**, no una garantía. Con hierarchical chunking mapea al número de **child chunks** a recuperar, y como los childs con parent común se colapsan, el resultado final puede ser menor.

### Reranking

De [Improve the relevance of query responses with a reranker model](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html). Un modelo reranker calcula la relevancia de los chunks respecto a la consulta y **reordena los resultados según los scores** que calcula.

**Beneficio central**: permite recuperar **menos resultados pero más relevantes**. Al alimentar el FM generador con esos resultados, **se reduce coste y latencia**. Los modelos reranker están entrenados para identificar señales de relevancia a partir de la consulta y usarlas para ordenar documentos.

**Entradas mínimas**: el modelo reranker, la consulta del usuario, y la lista de documentos a reordenar.

**Dos formas de uso**:

| Forma | Cómo |
| --- | --- |
| **API directa** | Operación [`Rerank`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Rerank.html): envía consulta, documentos y configuración; el modelo devuelve los documentos reordenados |
| **Dentro de Knowledge Bases** | Usar el reranker al llamar a `Retrieve` o `RetrieveAndGenerate`, o al consultar en consola. **Los resultados del reranking sobrescriben el ranking por defecto** de la knowledge base |

> **Limitación**: el reranking funciona **solo con datos textuales**.

En consola: panel **Configurations** → sección **Reranking** → seleccionar modelo, actualizar permisos si hace falta, ajustar opciones y probar con **Run**.

Regiones y modelos soportados: [Supported Regions and models for reranking](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-supported.html). Permisos: [Permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-prereq.html).

Las **Managed Knowledge Bases** incluyen un **reranker semántico gestionado sin coste extra**, y admiten sustituirlo por un reranker propio de Bedrock en tiempo de consulta.

### Pipeline de recuperación de alta relevancia

```
Consulta del usuario
   │
   ├─► (opcional) query decomposition / expansion  ← Skill 1.5.5
   │
   ▼
Filtro de metadatos (explícito o implicit filtering)
   │
   ▼
Búsqueda híbrida: vectores + texto crudo
   │   recuperar N amplio (p.ej. 25)
   ▼
Reranker de Bedrock
   │   quedarse con los K mejores (p.ej. 5)
   ▼
Contexto al FM  ── menos tokens, mayor relevancia, menor coste y latencia
   │
   ▼
Guardrails con contextual grounding ← detecta respuestas no fundamentadas
```

Cada etapa ataca un modo de fallo distinto: los filtros eliminan lo irrelevante por atributo, la híbrida recupera coincidencias exactas que la semántica pierde (códigos, nombres propios, SKUs), el reranker corrige el orden, y el contextual grounding detecta alucinaciones en la generación.

### Guardrails aplicados al retrieval

Se pueden aplicar guardrails a una knowledge base para configurar denied topics y content filters sobre entradas y respuestas:

```json
"generationConfiguration": {
  "guardrailConfiguration": {
    "guardrailId": "string",
    "guardrailVersion": "string"
  }
}
```

> Nota de la documentación: usar guardrails con **contextual grounding** para knowledge bases **no está soportado en Claude 3 Sonnet ni Haiku**.

### Streaming de respuestas

Para respuestas progresivas se usa [`RetrieveAndGenerateStream`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerateStream.html). En consola: **Streaming preference** → **Stream response**.

---

## Skill 1.5.5 — Manejo sofisticado de consultas

> *Desarrollar sistemas sofisticados de manejo de consultas para mejorar la efectividad de la recuperación y la calidad de resultados para augmentación de FMs (por ejemplo, Amazon Bedrock para expansión de consulta, funciones Lambda para descomposición de consulta, Step Functions para transformación de consulta).*

### Query decomposition nativa

De [Configure and customize queries and response generation](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html). Es la técnica de descomponer consultas complejas en sub-consultas más pequeñas y manejables. Ayuda a recuperar información más precisa y relevante cuando la consulta inicial es **multifacética o demasiado amplia**. Activarla puede provocar **varias consultas ejecutadas contra la knowledge base**, lo que ayuda a una respuesta final más precisa.

Ejemplo oficial: para *"¿Quién anotó más en el Mundial FIFA 2022, Argentina o Francia?"*, Bedrock puede generar primero estas sub-consultas antes de la respuesta final:

1. ¿Cuántos goles anotó Argentina en la final del Mundial FIFA 2022?
2. ¿Cuántos goles anotó Francia en la final del Mundial FIFA 2022?

Configuración por API:

```json
{
  "input": { "text": "string" },
  "retrieveAndGenerateConfiguration": {
    "knowledgeBaseConfiguration": {
      "orchestrationConfiguration": {
        "queryTransformationConfiguration": {
          "type": "QUERY_DECOMPOSITION"
        }
      }
    }
  }
}
```

En consola: crear y sincronizar un data source, abrir el panel de configuración de la ventana de test, y habilitar query decomposition.

### El prompt de orquestación: donde vive la transformación de consulta

Cuando consultas una knowledge base con generación de respuesta, Bedrock usa una plantilla de prompt que combina instrucciones y contexto con la consulta del usuario. Además de la plantilla de **generación**, se puede personalizar el **prompt de orquestación**, que es el que **convierte el prompt del usuario en una consulta de búsqueda**. Ahí es donde se implementa expansión, reescritura y normalización de consultas.

**Prompt placeholders** disponibles, rellenados dinámicamente en tiempo de ejecución y rodeados por `$`:

| Variable | Plantilla | Reemplazado por | Obligatorio |
| --- | --- | --- | --- |
| `$query$` | Orchestration, generation | La consulta del usuario enviada a la knowledge base | Sí en Claude Instant y Claude v2.x. No en Claude 3 Sonnet, donde se incluye automáticamente |
| `$search_results$` | Generation | Los resultados recuperados para la consulta | **Sí**, todos los modelos |
| `$output_format_instructions$` | Orchestration | Instrucciones subyacentes de formato de respuesta y citas. Varía por modelo | **Sí**. **Sin este placeholder la respuesta no contiene citas** |
| `$current_time$` | Orchestration, generation | La hora actual | No |

Si defines tus propias instrucciones de formato, AWS sugiere **quitar** `$output_format_instructions$`.

**XML tags**: los modelos Anthropic soportan etiquetas XML para estructurar y delimitar prompts; se recomiendan nombres de etiqueta descriptivos. El prompt de sistema por defecto usa, por ejemplo, la etiqueta `<database>` para delimitar una base de preguntas previas.

> Advertencia de la documentación: si no aportas plantilla personalizada, Bedrock usa un prompt de sistema por defecto que **incluye contenido de ejemplo genérico** (preguntas y respuestas de temas no relacionados) para guiar el formato de respuesta del modelo.

### Parámetros de inferencia en la generación

```json
"inferenceConfig": {
  "textInferenceConfig": {
    "temperature": 0.5,
    "topP": 0.5,
    "maxTokens": 2048,
    "stopSequences": ["\nObservation"]
  }
},
"additionalModelRequestFields": { "top_k": 50 }
```

Reglas oficiales del comportamiento de estos campos:

- `textInferenceConfig` admite `temperature`, `topP`, `maxTokenCount` y `stopSequences`.
- Parámetros no soportados por `textInferenceConfig` se pasan por `additionalModelRequestFields`.
- Si omites un parámetro de `textInferenceConfig`, se usa el valor por defecto.
- Parámetros **no reconocidos** en `textInferenceConfig` se **ignoran**; en `additionalModelRequestFields` **lanzan excepción**.
- El **mismo parámetro en ambos sitios lanza una validation exception**.
- `inferenceConfig` va en `knowledgeBaseConfiguration` si consultas una knowledge base, o en `externalSourcesConfiguration` si haces *chat with your document*.

### Patrones de orquestación de consultas

| Técnica | Implementación nativa | Implementación personalizada |
| --- | --- | --- |
| **Descomposición** | `QUERY_DECOMPOSITION` | Lambda que llama a un FM para generar sub-consultas y agrega los resultados |
| **Expansión** | Prompt de orquestación personalizado | Lambda con un FM que genera sinónimos, variantes y términos relacionados |
| **Reescritura y normalización** | Prompt de orquestación | Lambda: corregir ortografía, expandir siglas, añadir contexto de la conversación |
| **Enrutamiento a knowledge base** | — | Nodo condition de un flow, o Lambda que clasifica la intención y elige la KB |
| **Generación del filtro de metadatos** | `implicitFilterConfiguration` con Claude | Lambda que construye el objeto `filter` |
| **Transformación multi-paso con estado** | — | **Step Functions**: normalizar → descomponer → recuperar en paralelo (Map) → rerankear → agregar |
| **Clarificación al usuario** | — | Step Functions con espera de input; ver [Task 1.6 · Skill 1.6.2](./task-1-6-prompt-engineering-governance.md#skill-162--sistemas-interactivos-que-mantienen-contexto) |

Arquitectura con Step Functions:

```
Consulta ──► Step Functions
               ├─ Lambda: normalizar y detectar idioma
               ├─ Choice: ¿consulta simple o compleja?
               │     simple  ──► Retrieve directo
               │     compleja──► Lambda: descomponer en sub-consultas
               │                   └─ Map state: Retrieve en paralelo por sub-consulta
               ├─ Lambda: deduplicar y consolidar chunks
               ├─ Rerank
               ├─ Choice: ¿hay resultados relevantes?
               │     no ──► acción de fallback (GENREL03-BP01)
               └─ RetrieveAndGenerate / Converse con el contexto final
```

---

## Skill 1.5.6 — Mecanismos de acceso consistentes

> *Crear mecanismos de acceso consistentes para habilitar integración fluida con FMs (por ejemplo, interfaces de function calling para vector search, clientes de Model Context Protocol [MCP] para consultas vectoriales, patrones de API estandarizados para augmentación de recuperación).*

### Tool use en Amazon Bedrock

De [Use a tool to complete an Amazon Bedrock model response](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html). Principio fundamental: **el modelo no llama la herramienta directamente**. Al enviar un mensaje también envías definiciones de una o más herramientas; **el modelo decide cuándo se necesita una herramienta**, y tu código de aplicación —o Amazon Bedrock en modo server-side— la ejecuta y devuelve el resultado para que el modelo lo incorpore a su respuesta final.

**Tres modos de tool use**:

| Modo | Quién ejecuta la herramienta | Cuándo usarlo | APIs |
| --- | --- | --- | --- |
| **Client-side** | Tu código de aplicación, tras recibir la petición de tool-call del modelo | La mayoría de casos | Responses, Chat Completions, **Converse**, InvokeModel |
| **Server-side** | **Amazon Bedrock**. Registras una función **Lambda** o un **AgentCore Gateway** y Bedrock invoca la herramienta en nombre del modelo | Ejecución centralizada y segura de herramientas sin gestionar orquestación en la aplicación | Actualmente disponible en la **Responses API** |
| **Anthropic Claude tool use** | Tu código, con tipos de herramienta definidos por Anthropic (`computer_*`, `bash_*`, `text_editor_*`, `memory_*`) y el formato de la Anthropic Messages API | Computer use, ejecución de código, edición de ficheros, memoria persistente, streaming fino de herramientas | `bedrock-runtime`, `bedrock-mantle` |

El tool use se puede combinar con [structured outputs](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html) para obtener JSON validado.

Aplicado a retrieval: se define una herramienta `search_knowledge_base(query, filters)` cuya implementación llama a `Retrieve`. El modelo decide cuándo buscar y con qué filtros, y la interfaz permanece estable aunque cambie el vector store por debajo.

### AgentCore Gateway y MCP

De [Core concepts for Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-core-concepts.html). Gateway proporciona un **punto de entrada estandarizado y seguro para tráfico agéntico**, permitiendo que los agentes descubran e interactúen con herramientas, otros agentes y LLMs.

**Conceptos clave**

| Concepto | Definición |
| --- | --- |
| **Gateway** | Punto único y seguro de acceso. Puede tener múltiples targets en tres categorías: MCP, HTTP e inference |
| **Gateway Target** | El backend al que se conecta el gateway |
| **Authorizer** | Configuración de autorización de entrada, obligatoria en cada gateway |
| **Credential Provider** | Credenciales que el gateway usa al llamar a tus APIs o Lambda |

**Tres categorías de target**

| Categoría | Comportamiento |
| --- | --- |
| **MCP target** | Opera en **modo agregación**: el gateway combina las capacidades de todos los MCP targets en **un único MCP server virtual**. Los clientes ven una sola respuesta `tools/list` consolidada. Soporta sincronización de capacidades, **semantic tool search** y **three-legged OAuth (3LO)** a nivel de target |
| **HTTP target** | Envía tráfico **directamente** al target, sin agregación ni traducción de protocolo. **No** soporta sincronización de capacidades ni semantic tool search. Los clientes direccionan cada target por **path-based routing**. Incluye agentes de AgentCore Runtime, otros agentes (A2A), MCP servers externos y cualquier endpoint HTTP por passthrough |
| **Inference target** | Enruta tráfico de LLM a uno o varios proveedores de modelo por un endpoint unificado, seleccionando el destino según el campo **`model`** de la petición. Da a los agentes una interfaz consistente entre proveedores como Amazon Bedrock, OpenAI y Anthropic |

**Tipos de autorización de entrada**: **OAuth (JWT)** para autorización basada en token, **IAM (AWS Signature Version 4)** para autorización por identidad de AWS, **authenticate only** (valida el token y delega la autorización al target), y **no authorization** para desarrollo y pruebas.

**Credenciales de salida**: en targets **Smithy o Lambda**, el gateway usa el **execution role** adjunto. En targets **OpenAPI o MCP server**, se adjunta un **AgentCore credential provider** que guarda la API key o credenciales OAuth, o se configura autorización IAM con firma SigV4, o ninguna autorización para endpoints públicos.

**Tipos de herramienta MCP soportados**

| Tipo | Qué aporta |
| --- | --- |
| **OpenAPI specifications** | Convierte REST APIs existentes en herramientas MCP; el gateway traduce entre MCP y REST |
| **Lambda functions** | Lógica de negocio propia en tu lenguaje preferido; el gateway invoca la Lambda y traduce la respuesta a formato MCP |
| **Smithy models** | Define interfaces de API y genera herramientas MCP que interactúan con servicios AWS o APIs propias |
| **MCP servers** | MCP servers remotos que aportan **tools, prompts y resources**. Las **tools son obligatorias**; prompts y resources son opcionales. Los prompts aportan plantillas reutilizables con argumentos; los resources aportan datos contextuales identificados por URI. En la sincronización, el gateway descubre todas las capacidades que el MCP server anuncia |
| **Integrations** | Plantillas preconfiguradas de proveedores de integración |
| **Connectors** | Connectors integrados a herramientas |

### Exponer una knowledge base como herramienta MCP

Una **Managed Knowledge Base** se puede registrar como target de AgentCore Gateway: ver [Connect to your knowledge base through AgentCore Gateway](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-gateway-target.html). Con ello, el retrieval queda expuesto por MCP y es consumible por cualquier cliente compatible sin código específico. Nota: la integración con AgentCore Gateway **solo está soportada en managed knowledge bases**, no en customer-managed.

También se puede exponer una REST API de **Amazon API Gateway** como target MCP del gateway ([API Gateway como target](https://docs.aws.amazon.com/apigateway/latest/developerguide/mcp-server.html)), lo que permite envolver un servicio de retrieval propio.

### APIs estandarizadas de retrieval en Bedrock

| API | Uso |
| --- | --- |
| [`Retrieve`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html) | Devuelve chunks; la generación la controla tu aplicación. Soporta `filter`, `overrideSearchType`, `numberOfResults`, `implicitFilterConfiguration` y reranking |
| [`RetrieveAndGenerate`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerate.html) | Recuperación y generación con citas en una llamada |
| [`RetrieveAndGenerateStream`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerateStream.html) | Igual, con respuesta en streaming |
| [`Rerank`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Rerank.html) | Reordenar documentos sin knowledge base |

Patrón recomendado de capas:

```
Agente / aplicación
   │  contrato estable de herramienta
   ▼
AgentCore Gateway (MCP)  ── o ──  API Gateway + Lambda
   │
   ▼
Retrieve / RetrieveAndGenerate / Rerank
   │
   ▼
Vector store (intercambiable sin afectar al contrato superior)
```

La capa de gateway o de API es la que hace que cambiar de OpenSearch a S3 Vectors, o de customer-managed a managed knowledge base, no obligue a modificar el agente.

---

## Preguntas de autoevaluación

1. Con hierarchical chunking, ¿a qué mapea `numberOfResults` y por qué puedes recibir menos resultados de los pedidos?
2. ¿Qué hiperparámetro de semantic chunking hace que se generen **menos** chunks al aumentarlo?
3. Necesitas lógica de chunking propia. ¿Qué estrategia nativa eliges y qué recurso adicional hay que aportar?
4. ¿Qué dimensiones admite Titan Text Embeddings V2 y qué vector stores soportan su variante binaria?
5. Tu vector store es S3 Vectors. ¿Puedes usar búsqueda híbrida? ¿Y `startsWith` como filtro?
6. ¿Qué dos beneficios económicos aporta el reranking, según la documentación?
7. Quitas `$output_format_instructions$` del prompt de orquestación. ¿Qué pierdes?
8. Pasas `temperature` tanto en `textInferenceConfig` como en `additionalModelRequestFields`. ¿Qué ocurre?
9. En modo **server-side tool use**, ¿quién ejecuta la herramienta y qué dos tipos de recurso se pueden registrar?
10. ¿En qué modo opera un **MCP target** de AgentCore Gateway y qué implica para el cliente?
11. ¿Se puede conectar una customer-managed knowledge base a AgentCore Gateway?

## Fuentes oficiales de esta sección

**Chunking e ingesta**
- [How content chunking works for knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html)
- [Use a custom transformation Lambda function to define how your data is ingested](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-custom-transformation.html)
- [Customize ingestion for a data source](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-customize-ingestion.html)
- [Parsing options for your data source](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html)

**Embeddings y vector search**
- [Supported models and Regions for Amazon Bedrock knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html)
- [Prerequisites for using a vector store you created for a knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-setup.html)
- [Vector search in Amazon OpenSearch Service](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vector-search.html)
- [GENCOST04-BP01 Reduce vector length on embedded tokens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost04-bp01.html)
- [Batch inference](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html)

**Consulta, relevancia y reranking**
- [Configure and customize queries and response generation](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html)
- [Improve the relevance of query responses with a reranker model](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html)
- [Supported Regions and models for reranking](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank-supported.html)
- [Query a knowledge base and retrieve data](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve.html)
- [Query a knowledge base and generate responses](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve-generate.html)
- [Influence response generation with inference parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-parameters.html)

**Acceso estandarizado, tool use y MCP**
- [Use a tool to complete an Amazon Bedrock model response](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html)
- [Client-side tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-client-side.html)
- [Server-side tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-server-side.html)
- [Core concepts for Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-core-concepts.html)
- [Use an AgentCore gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-using.html)
- [Connect to your knowledge base through AgentCore Gateway](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-gateway-target.html)
- [Add an API Gateway REST API as a target for AgentCore Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/mcp-server.html)
- [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html)
