# Task 1.4 — Diseñar e implementar soluciones de vector store

[← Volver al índice](./README.md)

Skills cubiertos: **1.4.1**, **1.4.2**, **1.4.3**, **1.4.4**, **1.4.5**.

---

## Skill 1.4.1 — Arquitecturas avanzadas de vector database

> *Crear arquitecturas avanzadas de vector database específicamente para augmentación de FMs, que permitan recuperación semántica eficiente más allá de las capacidades de búsqueda tradicional (por ejemplo, Amazon Bedrock Knowledge Bases para organización jerárquica, Amazon OpenSearch Service con el Neural plugin, Amazon RDS con repositorios de documentos en S3, Amazon DynamoDB con vector databases para metadatos y embeddings).*

### Primera decisión: Managed vs Customer-managed Knowledge Base

De [Build a managed knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-managed.html). AWS recomienda ahora la opción gestionada para el mejor equilibrio entre facilidad de uso, precisión y coste. En una **Bedrock Managed Knowledge Base**, Amazon Bedrock gestiona la ingesta, el almacenamiento, la indexación y la infraestructura de recuperación; tú aportas los data sources.

| Característica | Bedrock Managed | Customer-Managed |
| --- | --- | --- |
| **Agentic retrieval** | Soportado | No soportado |
| **Data store** | Datastore auto-escalable de embeddings, texto, metadatos y archivos originales, gestionado íntegramente por Bedrock | El cliente elige, provisiona, escala y actualiza los datastores vectorial y de texto |
| **Search type** | Recuperación híbrida agéntica y semántica, optimizada para los tipos de archivo ingeridos | Eliges tu propia estrategia de búsqueda |
| **Embedding model gestionado** | Modelo integrado optimizado para precisión y rendimiento, **sin coste extra** | Ninguno |
| **Embedding model propio** | Cualquier modelo de embedding de Bedrock con **float32 y 1024 dimensiones** | Cualquier modelo de embedding de Bedrock |
| **Reranking gestionado** | Reranker semántico integrado, **sin coste extra** | Ninguno |
| **Reranking personalizado** | Modelos reranker de Bedrock | Modelos reranker de Bedrock |
| **Connectors** | **7 nativos**: S3, SharePoint, Confluence, Web Crawler, Google Drive, OneDrive, Custom | **S3 y Custom** |
| **Data parsing** | Parser integrado para tipos de archivo multimodales | Default para texto, Foundation Model, o Bedrock Data Automation |
| **Chunking** | Built-in (default) o fixed-size | Built-in (default) o fixed-size |
| **Integración AgentCore Gateway** | Soportado | No soportado |
| **Gestión de infraestructura** | Ninguna | Provisionas y mantienes tu vector DB, con acceso directo |
| **Mejor para** | RAG gestionado end-to-end con connectors nativos y recuperación agéntica | Configuraciones personalizadas de vector DB |
| **Integración Amazon Quick** | Asociación nativa como knowledge base | Integración propia |

> **Aviso de deprecación relevante**: a partir del **30 de septiembre de 2026** no se soportará la creación de **nuevos** connectors de Confluence, Microsoft SharePoint, Salesforce y Web Crawler en knowledge bases **customer-managed**. Los existentes seguirán funcionando, incluida la ingesta y la recuperación. AWS recomienda la Managed Knowledge Base para aplicaciones que necesiten esos connectors. Ver [Connect a data source to your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/data-source-connectors.html).

### Vector stores soportados en Customer-managed Knowledge Bases

De [Prerequisites for using a vector store you created for a knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-setup.html). Existe un flujo *quick-create* en la consola para algunos de ellos; si lo usas, Bedrock crea el índice vectorial por ti.

| Vector store | Perfil | Notas decisivas |
| --- | --- | --- |
| **Amazon OpenSearch Serverless** | Vector search collection | Soporta **vectores binarios**. Motor **faiss**. Permite red privada vía VPC endpoint (PrivateLink) |
| **Amazon OpenSearch Managed Clusters** | Dominio gestionado | Soporta **vectores binarios** (engine 2.16+). Requiere **2.13+** para índices k-NN. **Debe ser de acceso público**: los dominios detrás de VPC **no** están soportados. Se recomienda fine-grained access control |
| **Amazon S3 Vectors** | Almacenamiento vectorial en S3 | Coste-efectivo, elástico y duradero, con latencia de consulta sub-segundo. **Ideal para cargas de consulta poco frecuente**. Solo **floating-point**, sin binarios |
| **Amazon Aurora (PostgreSQL con pgvector)** | Relacional + vectorial | El clúster **debe estar en la misma cuenta AWS** que la knowledge base. Requiere Secrets Manager |
| **Neptune Analytics (GraphRAG)** | Grafo + vectorial | El índice de búsqueda vectorial **solo se puede crear al crear el grafo**. Bedrock crea la conexión de red automáticamente |
| **Pinecone** | Vector DB de terceros | Requiere autorizar a AWS el acceso a la cuenta de Pinecone |

Campos que hay que mapear al crear la knowledge base:

| Campo | API | Contenido |
| --- | --- | --- |
| Vector field | `vectorField` | Los embeddings generados por el modelo elegido |
| Text field | `textField` | Los chunks de texto extraídos de los archivos |
| Bedrock-managed metadata field | `metadataField` | Metadatos que gestiona Bedrock (atribución de fuente, ingesta y consulta) |
| Primary key (solo Aurora) | `primaryKeyField` | Identificador único por registro (UUID) |
| Custom metadata field (Aurora) | `customMetadataField` | Columna donde Bedrock escribe la información de tus archivos de metadatos |

> **Regla general**: la elección de modelo de embedding y de dimensiones **condiciona qué vector stores puedes usar**. Si no puedes usar tu vector store preferido, ajusta el modelo de embedding y las dimensiones.

### Configuración concreta por vector store

**OpenSearch Serverless** — al crear el índice vectorial: nombre de índice, nombre de campo vectorial (por ejemplo `embeddings`), **Engine: faiss**, dimensiones según el modelo, y métrica de distancia (AWS recomienda **Euclidean** para embeddings float). En *Metadata management* se añaden dos campos: uno de tipo String **filtrable** para los chunks de texto, y otro de tipo String **no filtrable** para los metadatos de Bedrock. Hay que anotar el **Collection ARN**.

**OpenSearch Managed Clusters** — el índice se crea con una petición explícita. Solo **faiss**; **nmslib no está soportado**:

```json
PUT /<index-name>
{
  "settings": { "index": { "knn": true } },
  "mappings": {
    "properties": {
      "<vector-name>": {
        "type": "knn_vector",
        "dimension": <embedding-dimension>,
        "data_type": "binary",
        "space_type": "l2",
        "method": {
          "name": "hnsw",
          "engine": "faiss",
          "parameters": { "ef_construction": 128, "m": 24 }
        }
      },
      "AMAZON_BEDROCK_METADATA":   { "type": "text", "index": "false" },
      "AMAZON_BEDROCK_TEXT_CHUNK": { "type": "text", "index": "true"  }
    }
  }
}
```

`data_type: "binary"` solo es necesario para embeddings binarios. `space_type`: **`l2`** para embeddings float, **`hamming`** para binarios.

Para filtrar por **campos de metadatos personalizados**, hay que declararlos como `keyword`, o como `text` con un subcampo `keyword`. Sin esta estructura, las consultas de filtrado fallan con un error *"Rewrite first"*:

```json
"my_custom_field": {
  "type": "text",
  "fields": { "keyword": { "type": "keyword" } }
}
```

**Amazon S3 Vectors** — los *vector buckets* contienen *vector indexes*; un bucket puede tener varios índices. Configuración:

| Parámetro | Valor |
| --- | --- |
| Dimensiones | Entre **1 y 4096**, coincidiendo con el modelo de embedding |
| Tipo de vector | Solo **floating-point**; binarios **no** soportados |
| Métrica de distancia | **Cosine** o **Euclidean** |
| Metadatos no filtrables | Hasta **10 claves**. Añadir `AMAZON_BEDROCK_TEXT` y `AMAZON_BEDROCK_METADATA` |
| Metadatos con Bedrock KB | Hasta **1 KB** de metadatos personalizados (filtrables + no filtrables) y **35 claves por vector** |
| Cifrado | SSE-S3 por defecto o SSE-KMS. **El tipo de cifrado no se puede cambiar después de crear el bucket** |
| Tags | Hasta **50 tags por vector index** para seguimiento de coste |

Si los metadatos exceden los límites, el job de ingesta lanza una excepción al poblar el índice. Los tipos soportados en los índices vectoriales de S3 son string, boolean y number. Por defecto los metadatos son **filtrables**.

> **Incompatibilidad a recordar**: el chunking **jerárquico no se recomienda con S3 Vectors**. Con un número alto de tokens (más de 8000 combinados) se pueden exceder los límites de tamaño de metadatos, porque las relaciones parent-child y el contexto jerárquico se guardan como metadatos **no filtrables**.

**Aurora PostgreSQL** — esquema de tabla e índices requeridos:

| Columna | Tipo | Campo de la KB |
| --- | --- | --- |
| `id` | UUID primary key | `primaryKeyField` |
| `embedding` | Vector | `vectorField` |
| `chunks` | Text | `textField` |
| `metadata` | JSON | `metadataField` |
| `custom_metadata` | JSONB | `customMetadataField` (opcional) |

Índices obligatorios:

```sql
-- Embeddings (obligatorio)
CREATE INDEX ON bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);

-- Chunks de texto (obligatorio)
CREATE INDEX ON bedrock_integration.bedrock_kb USING gin (to_tsvector('simple', chunks));

-- Metadatos personalizados (solo si creaste la columna)
CREATE INDEX ON bedrock_integration.bedrock_kb USING gin (custom_metadata);
```

Optimizaciones documentadas:

- Para mejorar precisión y latencia de **hybrid search** con contenido en inglés, usar el diccionario `'english'` en lugar de `'simple'`.
- Si usas **metadata filtering**, habilitar **HNSW iterative index scans** (requiere **pgvector 0.8.0 o posterior**). Sin iterative scans, los filtros selectivos pueden devolver menos resultados de lo esperado, porque el filtrado se aplica **después** del escaneo del índice HNSW:

```sql
ALTER DATABASE your_database SET hnsw.iterative_scan = 'relaxed_order';
ALTER DATABASE your_database SET hnsw.max_scan_tuples = 20000;
```

Estos ajustes persisten a nivel de base de datos pero **solo aplican a sesiones nuevas**; con RDS Data API hay que esperar unos minutos a que reciclen las sesiones del pool.

- Si usas filtros de rango sobre metadatos numéricos con frecuencia, crear un índice de expresión sobre la clave concreta:

```sql
CREATE INDEX ON your_table ((custom_metadata->>'year')::double precision);
```

Alternativa a `custom_metadata`: crear una columna por atributo de metadato con su tipo (text, number, boolean). Durante la ingesta, esas columnas se pueblan con los valores correspondientes.

Credenciales: configurar un secreto de **AWS Secrets Manager** para el clúster. Hay que anotar DB Cluster ARN, database name, table name y Secret ARN.

**Neptune Analytics (GraphRAG)** — crear un grafo **vacío** con índice de búsqueda vectorial. El índice **solo se puede crear en el momento de crear el grafo**, especificando la dimensión en *Vector search settings*. Se asigna capacidad en **m-NCUs** (cada m-NCU aporta alrededor de 1 GiB de memoria y cómputo y red correspondientes); AWS recomienda empezar con la instancia más pequeña. No hay que configurar conectividad pública ni endpoints privados: Bedrock crea la conexión al grafo asociado.

### Patrones complementarios del skill

| Patrón mencionado en el skill | Interpretación oficial |
| --- | --- |
| **Bedrock Knowledge Bases para organización jerárquica** | Hierarchical chunking (parent/child) — ver [Task 1.5 · Skill 1.5.1](./task-1-5-retrieval.md#skill-151--segmentación-de-documentos-chunking) |
| **OpenSearch Service con Neural plugin** | Integración de OpenSearch con Bedrock para generar embeddings dentro del propio motor. Ver [Vector search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vector-search.html) |
| **RDS con repositorios de documentos en S3** | Embeddings y metadatos en Aurora/RDS, archivos originales en S3; el vector store guarda el URI de origen |
| **DynamoDB con vector databases para metadatos y embeddings** | DynamoDB como almacén de metadatos operativos y de aplicación (histórico, permisos, estado de sincronización) junto al vector store; **DynamoDB Streams** dispara la actualización incremental |

---

## Skill 1.4.2 — Frameworks de metadatos

> *Desarrollar frameworks completos de metadatos para mejorar la precisión de búsqueda y la conciencia de contexto en las interacciones con FMs (por ejemplo, metadatos de objeto S3 para timestamps de documento, atributos personalizados para información de autoría, sistemas de tagging para clasificación de dominio).*

### Archivos de metadatos en S3

De [Connect to Amazon S3 for your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/s3-data-source-connector.html). Se adjunta un archivo sidecar por documento:

**Reglas obligatorias**
- El nombre debe ser el del documento fuente **con `.metadata.json` añadido al final** (`fileName.extension.metadata.json`).
- Debe estar en **la misma carpeta o ubicación** que el archivo fuente en el bucket.
- **No puede exceder 10 KB**.

**Formato completo**

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
    },
    "origin": {
      "value": { "type": "STRING", "stringValue": "Overview" },
      "includeForEmbedding": true
    }
  }
}
```

**Formato simplificado** (cuando no necesitas controlar el comportamiento de embedding):

```json
{ "metadataAttributes": { "tag": "value" } }
```

Con el formato simplificado el metadato se guarda **para filtrado** pero **no se incluye en el embedding** (equivale a `includeForEmbedding: false`).

### `includeForEmbedding`: la distinción que se examina

| Valor | Comportamiento |
| --- | --- |
| `false` | Solo el texto del chunk se embebe. El metadato **se almacena y sirve para filtrar**, pero **no influye en los resultados de búsqueda semántica** |
| `true` | El par clave-valor se **concatena al texto del chunk antes de embeber** (formato `key1: value1\n\nchunk text`). El metadato entra en el vector, así que consultas que mencionen la clave o el valor **contribuyen al score de similitud** y mejoran la relevancia. El par clave-valor **no** se incluye en el texto del chunk devuelto en los resultados, que conserva solo el contenido original |

### Operadores de filtrado

De [Configure and customize queries and response generation](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html):

| Operador | Consola | API | Tipos | Notas de soporte |
| --- | --- | --- | --- | --- |
| Equals | `=` | `equals` | string, number, boolean | |
| Not equals | `!=` | `notEquals` | string, number, boolean | |
| Greater than | `>` | `greaterThan` | number | |
| Greater than or equals | `>=` | `greaterThanOrEquals` | number | |
| Less than | `<` | `lessThan` | number | |
| Less than or equals | `<=` | `lessThanOrEquals` | number | |
| In | `:` | `in` | string list | Mejor soportado en OpenSearch Serverless y Neptune Analytics GraphRAG |
| Not in | `!:` | `notIn` | string list | Mejor soportado en OpenSearch Serverless y Neptune Analytics GraphRAG |
| String contains | no disponible | `stringContains` | string | Mejor soportado en OpenSearch Serverless. Neptune GraphRAG soporta la variante string pero no la de lista |
| List contains | no disponible | `listContains` | string list | Mejor soportado en OpenSearch Serverless |
| Starts with | no disponible | `startsWith` | string | **Solo** OpenSearch Serverless |

**Operadores lógicos**: `andAll` y `orAll`, cada uno sobre una lista de hasta **5 filtros**. Se pueden combinar hasta **5 grupos de filtros**, con **un nivel de anidamiento**.

**Restricciones por tipo de knowledge base y vector store**
- En **managed knowledge bases**, `startsWith` y `stringContains` **no** están soportados: usa `equals`, `greaterThan`, `lessThan`, `in` o `notIn`.
- Si el índice está en un **S3 vector bucket**, tampoco puedes usar `startsWith` ni `stringContains`.
- Si usas **OpenSearch Serverless**, el índice debe estar configurado con el engine **`faiss`**. Con `nmslib` hay que crear un índice nuevo con faiss y una knowledge base nueva, o dejar que Bedrock cree el índice automáticamente.

**Campos de metadatos reservados**
- En knowledge bases **custom**: prefijo **`x-amz-bedrock`** reservado por el servicio.
- En knowledge bases **fully managed**: prefijo de **underscore** (por ejemplo `_source_uri`, `_data_source_id`).
- No se pueden sobrescribir los campos reservados en ninguno de los dos tipos.

**Metadatos automáticos útiles**
- Con PDFs en OpenSearch Serverless o Aurora, Bedrock genera el número de página en el atributo **`x-amz-bedrock-kb-document-page-number`**. **No** está soportado si eliges *no chunking*.
- El patrón de frescura documentado usa un atributo tipo `epoch_modification_time` (segundos desde el 1 de enero de 1970 UTC) y se filtra con `greaterThan` para quedarse con los documentos más recientes.

### Implicit metadata filtering

Bedrock puede **generar y aplicar el filtro automáticamente** a partir de la consulta del usuario y un esquema de metadatos. Está soportado por modelos **Anthropic Claude**. Se configura con `implicitFilterConfiguration` dentro de `vectorSearchConfiguration` en `Retrieve`:

- `metadataAttributes` — array con los esquemas de los atributos para los que el modelo generará filtro.
- `modelArn` — ARN del modelo a usar.

Esquema de ejemplo:

```json
[
  {
    "key": "company",
    "type": "STRING",
    "description": "The full name of the company. E.g. `Amazon.com, Inc.`, `Alphabet Inc.`, etc"
  },
  {
    "key": "pe_ratio",
    "type": "NUMBER",
    "description": "The price to earning ratio of the company..."
  },
  {
    "key": "is_us_company",
    "type": "BOOLEAN",
    "description": "Indicates whether the company is a US company."
  },
  {
    "key": "tags",
    "type": "STRING_LIST",
    "description": "Tags of the company, indicating its main business..."
  }
]
```

La calidad de la `description` determina la calidad del filtro generado: es prompt engineering aplicado al esquema de metadatos.

### Diseño de un framework de metadatos

| Dimensión | Atributo ejemplo | Tipo | `includeForEmbedding` | Uso |
| --- | --- | --- | --- | --- |
| Temporalidad | `epoch_modification_time` | NUMBER | `false` | Filtro de frescura con `greaterThan` |
| Autoría | `author`, `department` | STRING | `true` si los usuarios preguntan por autor | Filtro y boost semántico |
| Clasificación de dominio | `domain`, `product_line` | STRING | `true` | Segmentación por tema |
| Sensibilidad | `classification` | STRING | `false` | Filtrado de acceso por rol |
| Idioma | `language` | STRING | `false` | Filtrar por idioma del usuario |
| Versión | `doc_version` | STRING | `false` | Excluir versiones obsoletas |
| Taxonomía múltiple | `tags` | STRING_LIST | `false` | `in` / `listContains` |

**Control de acceso**: los filtros de metadatos **no son un mecanismo de autorización por sí solos**. La documentación advierte que todo lo que sincronices desde tu data source queda disponible para cualquiera con permisos `bedrock:Retrieve`, incluidos datos con permisos controlados en origen. Para autorización real hay que aplicar los filtros del lado del servidor en una capa de confianza (Lambda), no dejarlos al cliente, o usar [ACL awareness en managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-acl.html).

---

## Skill 1.4.3 — Arquitecturas de vector database de alto rendimiento

> *Implementar arquitecturas de vector database de alto rendimiento para optimizar el rendimiento de búsqueda semántica a escala para recuperación de FMs (por ejemplo, estrategias de sharding de OpenSearch, enfoques multi-índice para dominios especializados, técnicas de indexación jerárquica).*

### Fundamentos de vector search en OpenSearch

De [Vector search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vector-search.html) y [k-NN search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html):

| Elemento | Detalle |
| --- | --- |
| Tipo de campo | `knn_vector` |
| Dimensiones | La página de *Vector search* indica dimensiones configurables **hasta 16.000**; la página de *k-NN* indica una lista de **hasta 10.000 floats**. Verifica el límite de tu versión y motor |
| Métodos de búsqueda | **k-NN exacto** (los k vecinos más similares) y **k-NN aproximado** con algoritmos como **HNSW**, más rápido en datasets grandes |
| Métricas de distancia | Euclidean, cosine similarity, dot product |
| Habilitar índice | `"settings": { "index": { "knn": true } }` |
| Valor máximo de `k` | **10.000** |
| Integraciones ML | Amazon Bedrock para embeddings, SageMaker AI para modelos propios, modelos de Hugging Face, modelos personalizados |

**Comportamiento de `k` y `size`** — trampa clásica: en una query `knn` hay que incluir también `size`; si no, obtienes `k` resultados **por shard y por segmento** en lugar de `k` para la consulta completa. Y si mezclas la query `knn` con otras cláusulas puedes recibir **menos de `k`** resultados: un `post_filter` de rango puede reducir 2 resultados a 1.

**Búsquedas masivas**: para volúmenes altos manteniendo rendimiento, usar la API [`_msearch`](https://opensearch.org/docs/latest/api-reference/multi-search/) y enviar varias búsquedas en una sola petición.

### Dimensionado de memoria de grafos k-NN

Este cálculo aparece explícitamente en la documentación y es material de examen:

> OpenSearch Service usa **la mitad de la RAM de la instancia para el Java heap** (hasta un heap de 32 GiB). Por defecto, k-NN usa **hasta el 50 % de la mitad restante**. Así, una instancia con **32 GiB de RAM** puede alojar **8 GiB de grafos** (32 × 0,5 × 0,5). El rendimiento se degrada si el uso de memoria de grafos supera ese valor.

Métricas y settings a vigilar:

| Elemento | Qué hace |
| --- | --- |
| `KNNGraphMemoryUsage` | Métrica CloudWatch de uso de memoria de grafos por data node. Compararla con el límite del circuit breaker y la RAM de la instancia |
| `knn.memory.circuit_breaker.limit` | Porcentaje máximo de la RAM restante disponible para memoria de grafos k-NN |
| `KNNEvictionCount` | Grafos expulsados de la caché por restricciones de memoria o inactividad |
| `KNNTotalLoadTime` | Tiempo total de carga de grafos en caché; solo aplica a k-NN aproximado |
| `KNNQueryRequests` | Total de peticiones de consulta recibidas por el plugin k-NN |

En OpenSearch Service se pueden modificar todos los settings de k-NN vía `_cluster/settings` **excepto** `knn.memory.circuit_breaker.enabled` y `knn.circuit_breaker.triggered`.

**Tiering**: un índice k-NN creado en versión 2.x o posterior se puede migrar a [UltraWarm](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/ultrawarm.html) o [cold storage](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/cold-storage.html) en un dominio 2.17 o posterior. Las APIs de clear cache y warmup están bloqueadas para índices warm: en la primera consulta se descargan los grafos desde S3 y se cargan en memoria, y al expirar el TTL se expulsan automáticamente.

### Estrategias de sharding

Del [Amazon OpenSearch Service Lens](https://docs.aws.amazon.com/wellarchitected/latest/amazon-opensearch-service-lens/full.html):

| Best practice | Regla |
| --- | --- |
| [AOSPERF01-BP01](https://docs.aws.amazon.com/wellarchitected/latest/amazon-opensearch-service-lens/aosperf01-bp01.html) | Mantener el tamaño de shard en el rango recomendado de **10–50 GiB**, para eficiencia de indexación, consulta y relocalización |
| [AOSPERF01-BP03](https://docs.aws.amazon.com/wellarchitected/latest/amazon-opensearch-service-lens/aosperf01-bp03.html) | No más de **25 shards por GiB de heap** de cada data node |

Cómo se traduce en decisiones de diseño:

- **Más shards** → más paralelismo en consulta, pero más sobrecarga de coordinación y más memoria de grafos por nodo.
- **Menos shards, más grandes** → menos sobrecarga, pero shards por encima de 50 GiB penalizan relocalización y recuperación.
- Los **replicas** aportan throughput de lectura y disponibilidad, a costa de duplicar la memoria de grafos necesaria.

### Enfoques multi-índice para dominios especializados

| Enfoque | Ventaja | Coste |
| --- | --- | --- |
| **Un índice, filtros de metadatos** | Operación simple, una sola query | Todos los dominios comparten memoria de grafos; el filtrado post-scan puede reducir recall |
| **Un índice por dominio** | Aislamiento de rendimiento, dimensiones y modelo de embedding distintos por dominio, ciclo de vida independiente | Más recursos, hay que decidir a qué índice enrutar |
| **Un índice por inquilino (multi-tenant)** | Aislamiento fuerte de datos | No escala a miles de inquilinos |
| **Índices por antigüedad (hot / warm)** | Datos recientes en hot, históricos en UltraWarm o cold | La consulta debe abarcar varios índices |
| **Alias sobre varios índices** | Rotación y reindexado sin cambiar la aplicación | Requiere gestión de alias |

En Bedrock Knowledge Bases el equivalente funcional del enfoque multi-índice es **varias knowledge bases**, una por dominio, con un router previo que decide a cuál consultar (Lambda o un nodo condition de un flow).

### Indexación jerárquica

Dos niveles complementarios:

1. **A nivel de chunk**: hierarchical chunking de Bedrock (parent/child). Se recuperan child chunks, precisos por ser pequeños, y se sustituyen por sus parent chunks para dar al modelo más contexto. Detalle en [Task 1.5 · Skill 1.5.1](./task-1-5-retrieval.md#skill-151--segmentación-de-documentos-chunking).
2. **A nivel de recuperación**: HNSW es en sí una estructura jerárquica de grafo navegable. Los parámetros que la controlan son `ef_construction` y `m` (en los ejemplos oficiales de Bedrock, 128 y 24 respectivamente): valores mayores mejoran recall a costa de memoria y tiempo de construcción.

### Optimizaciones de OpenSearch Serverless

| Capacidad | Qué hace |
| --- | --- |
| [Vector Auto-Optimize](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-auto-optimize.html) | Evalúa automáticamente la configuración del índice vectorial y recomienda el mejor equilibrio entre calidad de búsqueda, latencia y coste de memoria |
| GPU-acceleration para indexado vectorial | Reduce el tiempo de crear, actualizar y borrar índices vectoriales |
| [Billion-scale workloads](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vector-search.html) | Guía específica para colecciones de escala de miles de millones de vectores |

### Palancas de rendimiento independientes del motor

| Palanca | Efecto |
| --- | --- |
| Reducir dimensiones del embedding (Titan V2: 1024 → 512 → 256) | Menos memoria y cómputo por vector. Base de [GENCOST04-BP01](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost04-bp01.html) |
| Usar **embeddings binarios** | Gran reducción de almacenamiento y memoria. Solo en OpenSearch Serverless y Managed |
| Reranking con menos resultados | Recuperar menos chunks pero más relevantes reduce coste y latencia del FM |
| Elegir S3 Vectors para consulta poco frecuente | Coste muy inferior a un clúster siempre encendido, con latencia sub-segundo |
| Tiering a UltraWarm / cold | Mover histórico fuera de la memoria caliente |

---

## Skill 1.4.4 — Integración con recursos corporativos

> *Usar servicios de AWS para crear componentes de integración que conecten con recursos (por ejemplo, sistemas de gestión documental, knowledge bases, wikis internos para integración completa de datos en aplicaciones GenAI).*

### Connectors nativos de Bedrock Knowledge Bases

De [Connect a data source to your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/data-source-connectors.html):

| Connector | Managed KB | Customer-managed KB | Doc |
| --- | --- | --- | --- |
| Amazon S3 | Sí | Sí | [S3](https://docs.aws.amazon.com/bedrock/latest/userguide/s3-data-source-connector.html) |
| Custom (ingesta directa por API) | Sí | Sí | [Custom](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-data-source-connector.html) |
| Confluence | Sí | Sí, pero sin connectors nuevos desde el 30/09/2026 | [Confluence](https://docs.aws.amazon.com/bedrock/latest/userguide/confluence-data-source-connector.html) |
| Microsoft SharePoint | Sí | Sí, misma restricción | [SharePoint](https://docs.aws.amazon.com/bedrock/latest/userguide/sharepoint-data-source-connector.html) |
| Salesforce | No listado en managed | Sí, misma restricción | [Salesforce](https://docs.aws.amazon.com/bedrock/latest/userguide/salesforce-data-source-connector.html) |
| Web Crawler | Sí | Sí, misma restricción | [Web Crawler](https://docs.aws.amazon.com/bedrock/latest/userguide/webcrawl-data-source-connector.html) |
| Google Drive | Sí | No | — |
| OneDrive | Sí | No | — |

**Soporte multimodal**: imágenes, audio y vídeo **solo** con data sources **S3 y custom**. Los demás tipos de connector **omiten** los archivos multimodales durante la ingesta.

Campos de `CreateDataSource`:

| Campo | Obligatorio | Función |
| --- | --- | --- |
| `knowledgeBaseId` | Sí | ID de la knowledge base |
| `name` | Sí | Nombre |
| `dataSourceConfiguration` | Sí | `type` del servicio y su configuración específica |
| `description` | No | Descripción |
| `vectorIngestionConfiguration` | No | Personalización de la ingesta: chunking, parsing, transformación Lambda |
| `dataDeletionPolicy` | No | **`RETAIN`** o **`DELETE`** de los embeddings en el vector store |
| `serverSideEncryptionConfiguration` | No | `kmsKeyArn` para cifrar datos transitorios durante la sincronización |
| `clientToken` | No | Idempotencia de la petición |

### Cuando no hay connector: patrones de integración

| Fuente | Camino recomendado |
| --- | --- |
| Sistema documental on-premises | [AWS DataSync](https://docs.aws.amazon.com/datasync/latest/userguide/create-s3-location.html) a S3 de forma continua o programada, y S3 como data source. Es el mecanismo que la doc de Bedrock cita explícitamente para transferir múltiples archivos a S3 desde on-premises, edge, otra nube o almacenamiento AWS |
| Transferencia por SFTP / FTPS | AWS Transfer Family hacia S3 |
| SaaS sin connector | Amazon AppFlow hacia S3 |
| Aplicación propia o bases de datos | **Custom data source** con ingesta directa por API |
| Datos estructurados consultables en SQL | [Knowledge base con structured data store](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-structured.html): convierte lenguaje natural a SQL |
| Búsqueda empresarial con connectors amplios y control de acceso | [Amazon Kendra](https://docs.aws.amazon.com/kendra/latest/dg/what-is-kendra.html) |
| Asistente empresarial listo para usar | [Amazon Q Business](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/what-is.html) |

### Exponer el retrieval como herramienta estandarizada

Una Managed Knowledge Base se puede conectar a través de **AgentCore Gateway**, lo que la convierte en una herramienta MCP consumible por cualquier agente compatible. Ver [Connect to your knowledge base through AgentCore Gateway](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-gateway-target.html) y el desarrollo en [Task 1.5 · Skill 1.5.6](./task-1-5-retrieval.md#skill-156--mecanismos-de-acceso-consistentes).

### Consideraciones de red y seguridad en la integración

| Requisito | Solución |
| --- | --- |
| Acceso privado a OpenSearch Serverless | VPC endpoint / [AWS PrivateLink](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vpc.html) |
| OpenSearch Managed Cluster como vector store | **Debe ser público**: los dominios en VPC no están soportados. Usar fine-grained access control |
| Credenciales de Aurora | AWS Secrets Manager |
| Cifrado de recursos de la knowledge base | [Encryption of knowledge base resources](https://docs.aws.amazon.com/bedrock/latest/userguide/encryption-kb.html) con KMS |
| Data sources en S3 cifrados con KMS | Permisos de descifrado en el rol de servicio |
| Permisos de creación automática de rol | `iam:CreateRole` e `iam:CreatePolicy`; con OpenSearch además `aoss:CreateAccessPolicy` e `iam:CreateServiceLinkedRole` |

---

## Skill 1.4.5 — Sistemas de mantenimiento de datos

> *Diseñar y desplegar sistemas de mantenimiento de datos para asegurar que los vector stores contienen información actual y precisa para augmentación de FMs (por ejemplo, mecanismos de actualización incremental, sistemas de detección de cambios en tiempo real, workflows de sincronización automatizados, pipelines de refresh programado).*

### Semántica de sincronización incremental

De [Sync your data with your Amazon Bedrock knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html). Cada vez que añades, modificas o eliminas archivos hay que sincronizar. **La sincronización es incremental**: Bedrock procesa solo los documentos añadidos, modificados o borrados desde la última sincronización. La reingesta incluye parsing, chunking, generación de embeddings e indexación.

| Escenario | Qué ocurre |
| --- | --- |
| Sin cambios detectados | El documento se **omite** |
| Cambió el contenido **o los metadatos** | El documento se **reingiere** (re-parse, re-chunk, re-embed, re-index) |
| Documento nuevo | Solo el nuevo se ingiere |
| Documento borrado | Se **elimina del vector store** |

### Optimización de solo-metadatos

En ciertos casos Bedrock actualiza los metadatos **sin reingerir el documento**: recupera los embeddings existentes del vector store, fusiona los nuevos metadatos y reescribe los embeddings actualizados, **evitando llamadas al modelo de embedding**.

Se aplica **solo si se cumplen todas** estas condiciones:

1. Solo se modificaron archivos `metadata.json`; **ningún archivo de contenido cambió**.
2. Los archivos de contenido asociados **no son CSV**.
3. El data source **no usa una función Lambda de transformación personalizada**.

**Caso especial de CSV**: los CSV usan el campo `documentStructureConfiguration` en los metadatos para controlar qué columnas se indexan. Como Bedrock no puede saber si esa configuración cambió sin reprocesar el archivo, **los CSV siempre se reingieren** cuando se actualizan sus archivos de metadatos.

### APIs de ingesta

| Operación | Función |
| --- | --- |
[`StartIngestionJob`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_StartIngestionJob.html) | Iniciar la sincronización. Requiere `knowledgeBaseId` y `dataSourceId` |
| [`StopIngestionJob`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_StopIngestionJob.html) | Detener un job en curso. Requiere `dataSourceId`, `ingestionJobId` y `knowledgeBaseId`. El job debe estar en ejecución |
| [`GetIngestionJob`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_GetIngestionJob.html) | Seguir el estado. Al terminar, `status` es **`COMPLETE`**. El objeto `statistics` indica si la ingesta tuvo éxito por documento |
| [`ListIngestionJobs`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_ListIngestionJobs.html) | Historial de jobs del data source, filtrable por estado |

Se usa el endpoint build-time de Agents for Amazon Bedrock. En la consola, el botón **Sync** en la sección del data source, con **Sync history** y **View warnings** para diagnosticar fallos.

> **Latencia post-ingesta**: la documentación advierte que, tras completarse la sincronización, **pueden pasar unos minutos** hasta que los embeddings nuevos estén disponibles para consulta, **salvo si usas Amazon Aurora (RDS)** como vector store.

### Prerrequisitos que hacen fallar una sincronización

Antes de ingerir hay que verificar:

- La conexión del data source está configurada.
- El modelo de embedding y el vector store están configurados.
- Los archivos están en [formatos soportados](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-ds.html).
- Los archivos no exceden el **Ingestion job file size** de las [cuotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html).
- Cada `.metadata.json` comparte nombre y extensión con su archivo fuente.
- Si el índice está en **OpenSearch Serverless**, usa engine **`faiss`**; con `nmslib` los metadatos se **ignoran**.
- Si el índice está en **Aurora**, se recomienda usar el campo de metadatos personalizado con un índice sobre esa columna; si no lo aportas, la tabla debe tener **una columna por cada propiedad de metadato** antes de empezar la ingesta.
- En **OpenSearch Managed Clusters**, los fallos de ingesta pueden indicar capacidad insuficiente del dominio: se resuelve aumentando IOPS y throughput.

### Arquitecturas de automatización del refresh

**Detección de cambios en tiempo real (event-driven)**

```
S3 PutObject / DeleteObject
   │
   ▼
Amazon EventBridge (o S3 Event Notifications)
   │
   ▼
Lambda  ── debounce / agrupación de eventos ──►  StartIngestionJob
   │
   ├─ registra estado en DynamoDB (documento, hash, última sync)
   └─ si ya hay un job en curso, encola el evento en SQS
```

Punto de diseño: los jobs de ingesta no son instantáneos y no conviene lanzar uno por cada objeto. El patrón es **agrupar eventos en una ventana temporal** antes de invocar `StartIngestionJob`, usando SQS como buffer y DynamoDB para el estado.

**Refresh programado**

```
EventBridge Scheduler (cron)
   │
   ▼
AWS Step Functions
   ├─ StartIngestionJob
   ├─ GetIngestionJob en bucle con espera hasta COMPLETE
   ├─ leer statistics → publicar métricas en CloudWatch
   └─ si hay fallos → SNS al equipo de datos
```

**Detección de cambios en bases de datos**: DynamoDB Streams o eventos de la aplicación disparan la reconstrucción del documento y su reindexado por el custom data source.

**Sincronización desde fuera de AWS**: AWS DataSync programado hacia S3, y el evento de S3 dispara la ingesta.

### Ciclo de vida y retirada de datos

| Mecanismo | Uso |
| --- | --- |
| `dataDeletionPolicy` = `RETAIN` \| `DELETE` | Decide si los embeddings sobreviven al borrado del data source |
| S3 Lifecycle policies | Mover originales a clases de almacenamiento más económicas tras la ingesta |
| S3 Intelligent-Tiering | Optimizar coste de los archivos fuente sin gestión manual |
| S3 Cross-Region Replication | Disponibilidad de los datos fuente para knowledge bases multi-Región |
| Filtro de frescura por metadatos | Excluir en consulta documentos obsoletos con `lessThan` / `greaterThan` sobre el timestamp |
| [Borrado de la knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-delete.html) | Requiere desasociar agents y limpiar el vector store asociado |

### Observabilidad del mantenimiento

| Señal | Origen |
| --- | --- |
| Éxito y fallo por documento | Objeto `statistics` de `GetIngestionJob` |
| Warnings de ingesta | Consola: **View warnings** en el data source |
| Métricas de la knowledge base gestionada | [Observability for managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-observability.html) |
| Salud del vector store OpenSearch | Métricas k-NN en CloudWatch: `KNNGraphMemoryUsage`, `KNNEvictionCount` |
| Métricas propias del pipeline | `PutMetricData` desde Lambda: documentos procesados, rechazados, antigüedad del índice |
| Auditoría de cambios | CloudTrail sobre las llamadas de ingesta |

---

## Preguntas de autoevaluación

1. ¿Qué dos vector stores soportan embeddings binarios en Bedrock Knowledge Bases?
2. Un requisito exige que el vector store esté dentro de una VPC. ¿Puedes usar un OpenSearch Managed Cluster como vector store de una knowledge base?
3. Un metadato debe servir para filtrar pero **no** debe influir en el score semántico. ¿Qué valor de `includeForEmbedding` usas?
4. Usas Aurora con metadata filtering y obtienes menos resultados de los esperados. ¿Cuál es la causa documentada y cómo se corrige?
5. ¿Por qué el chunking jerárquico no se recomienda con S3 Vectors?
6. Solo se modificó el archivo `.metadata.json` de un PDF. ¿Se vuelve a llamar al modelo de embedding? ¿Y si el archivo fuera un CSV?
7. Instancia de OpenSearch con 64 GiB de RAM. ¿Cuánta memoria de grafos k-NN puede alojar con la configuración por defecto?
8. ¿Qué operadores de filtrado **no** están disponibles en una managed knowledge base?
9. ¿Qué vector store ofrece latencia sub-segundo y es el recomendado para cargas de consulta poco frecuente?
10. ¿Qué campo de `CreateDataSource` decide si los embeddings se conservan al borrar el data source?

## Fuentes oficiales de esta sección

**Amazon Bedrock Knowledge Bases**
- [Build a managed knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-managed.html)
- [Prerequisites for creating a knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-prereq.html)
- [Prerequisites for using a vector store you created for a knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-setup.html)
- [Supported models and Regions for Amazon Bedrock knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html)
- [Configure and customize queries and response generation](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html)
- [Connect a data source to your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/data-source-connectors.html)
- [Connect to Amazon S3 for your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/s3-data-source-connector.html)
- [Sync your data with your Amazon Bedrock knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html)
- [How content chunking works for knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html)
- [Encryption of knowledge base resources](https://docs.aws.amazon.com/bedrock/latest/userguide/encryption-kb.html)
- [Create a service role for Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-permissions.html)
- [Connect to your knowledge base through AgentCore Gateway](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-gateway-target.html)

**Amazon OpenSearch Service**
- [Vector search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vector-search.html)
- [k-Nearest Neighbor (k-NN) search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html)
- [Working with vector search collections](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vector-search.html)
- [Access Amazon OpenSearch Serverless using an interface endpoint (AWS PrivateLink)](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vpc.html)
- [Vector Auto-Optimize](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-auto-optimize.html)
- [AOSPERF01-BP01 Maintain shard sizes at recommended ranges](https://docs.aws.amazon.com/wellarchitected/latest/amazon-opensearch-service-lens/aosperf01-bp01.html)
- [AOSPERF01-BP03 Check the number of shards per GiB of heap memory](https://docs.aws.amazon.com/wellarchitected/latest/amazon-opensearch-service-lens/aosperf01-bp03.html)

**Otros vector stores**
- [Using Aurora PostgreSQL as a knowledge base](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.VectorDB.html)
- [Amazon S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html)
- [Amazon S3 Vectors limitations and restrictions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-limitations.html)
- [Vector indexing in Neptune Analytics](https://docs.aws.amazon.com/neptune-analytics/latest/userguide/vector-index.html)
- [Choosing an AWS vector database for RAG use cases](https://docs.aws.amazon.com/prescriptive-guidance/latest/choosing-an-aws-vector-database-for-rag-use-cases/introduction.html)
