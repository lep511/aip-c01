# Task 4.2 — Retrieval, parámetros y perfilado

[← Volver al índice](./README.md)

Skills cubiertos: **4.2.2**, **4.2.4**, **4.2.6**.

Segunda mitad del Task 4.2. Aquí está el eje de **calidad de lo recuperado y de lo generado**: qué se trae del vector store, con qué parámetros se genera y dónde se va el tiempo. El eje de capacidad y tiempo de respuesta (skills 4.2.1, 4.2.3 y 4.2.5) está en [task-4-2-latencia-y-throughput.md](./task-4-2-latencia-y-throughput.md).

El marco es [GENPERF04 Vector store optimization](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf04.html) para el retrieval y [GENPERF02 Maintaining model performance](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02.html) para los parámetros.

---

## Skill 4.2.2 — Rendimiento del retrieval

> *Mejorar el rendimiento del retrieval para mejorar la relevancia y la velocidad de la información recuperada para la aumentación de contexto del FM (por ejemplo, usando optimización de índices, preprocesado de consultas, implementación de búsqueda híbrida con scoring personalizado).*

### Por qué el retrieval es el cuello de botella que más cuesta encontrar

De [GENPERF04](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf04.html), y el enunciado de la pregunta lo dice sin rodeos: un cuello de botella en un sistema de recuperación de datos **tiene efectos en cascada aguas abajo que son difíciles de identificar**.

> **Dato decisivo**: la razón de esa dificultad es que un retrieval lento se manifiesta como *el modelo va lento*, y un retrieval **irrelevante** se manifiesta como *el modelo alucina*. Ninguno de los dos síntomas apunta al vector store. Es el argumento para instrumentar el retrieval por separado, que es lo que pide el [Skill 4.3.5](./task-4-3-herramientas-vector-stores-y-fallos.md#skill-435--gestión-operativa-del-vector-store).

De [Test vector embeddings for latency and relevant performance](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf04-bp01.html), el orden de intervención, que no es negociable: empezar por las estrategias de **chunking y embedding**, porque tienen mayor efecto en el rendimiento y **solo pueden abordarse antes de que los datos entren en el almacén**. Todo lo demás se puede cambiar en caliente; eso no.

Las estrategias de chunking y la elección de modelo de embeddings están en [Task 1.5 · Skill 1.5.1](../domain-1/task-1-5-retrieval.md#skill-151--segmentación-de-documentos-chunking) y [Skill 1.5.2](../domain-1/task-1-5-retrieval.md#skill-152--selección-y-configuración-de-embeddings), incluido el chunking personalizado con Lambda que la propia práctica nombra.

### Los cuatro algoritmos ANN, y qué optimiza cada uno

GENPERF04-BP01 pide considerar el tradeoff entre **exactitud, velocidad, uso de memoria y escalabilidad** al elegir un algoritmo de vecino más cercano aproximado, y enumera cuatro con su punto fuerte:

| Algoritmo | Qué optimiza |
| --- | --- |
| **LSH** (locality-sensitive hashing) | **Indexado rápido** |
| **HNSW** (hierarchical navigable small world) | **Exactitud alta** |
| **IVF** (inverted file index) | **Equilibrio** |
| **PQ** (product quantization) | **Almacenamiento compacto** |

Y la instrucción que acompaña: **hacer benchmark de varios algoritmos con el dataset propio** para encontrar el equilibrio según las métricas priorizadas. No hay respuesta por defecto.

> **Dato decisivo**: HNSW es el que usan por defecto los vector stores de Bedrock, y es el de mayor exactitud **y mayor consumo de memoria**. La fórmula de dimensionado de memoria del grafo k-NN, que es material de examen, está en [Task 1.4 · Skill 1.4.3](../domain-1/task-1-4-vector-stores.md#dimensionado-de-memoria-de-grafos-k-nn). Si una pregunta plantea un índice que no cabe en memoria, las salidas son **PQ** para comprimir o **reducir la dimensión** del vector, no un algoritmo distinto de búsqueda.

Los fundamentos de k-NN exacto frente a aproximado en OpenSearch están en [k-NN search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html) y desarrollados en [Task 1.4 · Skill 1.4.3](../domain-1/task-1-4-vector-stores.md#fundamentos-de-vector-search-en-opensearch).

### Indexación jerárquica

La recomendación de GENPERF04-BP01 es concreta y viene con un veredicto: organizar los índices **de forma jerárquica**, con índices de nivel superior para información general y de nivel inferior para datos detallados. Y añade que **este enfoque generalmente supera a un índice único**.

La configuración concreta (`ef_construction`, `m`) y los enfoques multi-índice por dominio están en [Task 1.4 · Skill 1.4.3](../domain-1/task-1-4-vector-stores.md#indexación-jerárquica).

### Dimensión del vector: el tradeoff que no es lineal

De [Optimize vector sizes for your use case](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf04-bp02.html). La regla general de que a más dimensión más exactitud **existe dentro de una familia de modelos, pero no es universal entre modelos de embedding**. El rendimiento depende de tres cosas: los datos que se codifican, el modelo elegido y la dimensión usada dentro de ese modelo.

La estrategia oficial: **empezar por una codificación más compacta** y subir la dimensión solo si el caso de uso lo justifica. Y el criterio para decidir si subirá o no hará falta: **cuanto más estrecho y profundo sea el contenido, más probable es que el fine-tuning mejore la exactitud reduciendo a la vez la dimensión**.

| Requisito | Dimensión |
| --- | --- |
| **Latencia baja** | Vectores **más pequeños**: recuperación más rápida |
| **Se acepta más latencia** | Vectores **más grandes** dentro de un modelo dado: más exactitud y matiz |

> **Dato decisivo, y contradice la intuición**: un modelo **bien afinado con dimensiones pequeñas, como 256, puede superar a un modelo genérico con dimensiones mayores, de 1024 o más, en exactitud y en velocidad a la vez**. La dimensión no es una medida de calidad. La recomendación operativa que acompaña es consultar un leaderboard como MTEB al elegir el modelo de embeddings.

Y una restricción de plataforma: **algunos modelos ofrecen un rango limitado de dimensiones permitidas**, y eso es **especialmente cierto en el acceso gestionado a modelos de embedding a través de Bedrock**. Para una variedad mayor hay que ir a endpoints de SageMaker AI o a JumpStart. Los tipos de vector y dimensiones disponibles en Knowledge Bases están en [Task 1.5 · Skill 1.5.2](../domain-1/task-1-5-retrieval.md#tipos-de-vector-y-dimensiones), y el ángulo de coste en [Coste: reducir la longitud del vector](../domain-1/task-1-5-retrieval.md#coste-reducir-la-longitud-del-vector).

### Preprocesado de la consulta

GENPERF04-BP01 da dos instrucciones para la optimización de búsqueda en consultas dirigidas por IA, partiendo de que hay que **centrarse en interacciones máquina a máquina**: implementar **expansión de consulta usando contexto generado por IA**, y **desplazar el matching difuso hacia la similitud semántica**.

En Bedrock Knowledge Bases, el preprocesado tiene tres formas documentadas, de menor a mayor sofisticación:

| Técnica | Qué hace | Coste |
| --- | --- | --- |
| **Query decomposition** | Descompone una consulta compleja en **sub-consultas** más manejables | Varias consultas contra la knowledge base |
| **Agentic retrieval** | Descompone, recupera, **evalúa si basta** e itera | Varias pasadas, con llamadas al FM para planificar y evaluar |
| **Prompt de orquestación** | Reescribe la consulta antes de recuperar | Una llamada extra |

De [Configure and customize queries and response generation](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html), la query decomposition **rompe una consulta compleja en sub-consultas más pequeñas y manejables**, lo que ayuda a recuperar información más exacta y relevante, **especialmente cuando la consulta inicial es multifacética o demasiado amplia**. El aviso que acompaña: habilitarla **puede provocar que se ejecuten varias consultas contra la knowledge base**.

Se activa con `queryTransformationConfiguration` dentro de `orchestrationConfiguration`, con el tipo del enumerado [`QueryTransformationConfiguration`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_QueryTransformationConfiguration.html):

```json
{
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

El detalle y el ejemplo oficial están en [Task 1.5 · Skill 1.5.5](../domain-1/task-1-5-retrieval.md#query-decomposition-nativa).

### Agentic retrieval: recuperación con evaluación de suficiencia

De [Use agentic retrieval to query a knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic-retrieve.html). Usa un FM para **descomponer consultas complejas en sub-consultas, recuperar de forma iterativa y evaluar si los resultados recuperados bastan para responder la consulta original**. Mejora la exactitud en preguntas complejas de varios pasos **que una sola pasada de recuperación no cubriría**.

Los seis pasos de `AgenticRetrieveStream`:

```
1 · Carga del historico de sesion
      con memoryConfiguration y sessionBinding, Bedrock restaura
      el historico previo desde AgentCore Memory (corto plazo)
            │
2 · Planificacion
      el FM analiza la consulta y planifica sub-consultas
      cada sub-consulta apunta a una fuente configurada:
        un retriever de knowledge base, o
        AgentCore Memory de largo plazo
      tras recoger resultados, EVALUA si bastan
      si no bastan, planifica mas iteraciones hasta el maximo configurado
            │
3 · Recuperacion
      se ejecutan las sub-consultas contra las fuentes
            │
4 · Expansion a documento completo
      si el FM decide que necesita el documento entero
      (resumir, verificar completitud, acceder a secciones concretas)
      llama a GetDocumentContent
            │
5 · Generacion de respuesta
      con generateResponse en true (el valor por defecto)
      la respuesta se transmite por eventos responseEvent
      con sessionBinding y persistenceMode en DEFAULT,
        se persisten pregunta y respuesta en la sesion
            │
6 · Evento de resultado
      resultados DEDUPLICADOS de todas las iteraciones
      respuesta sintetizada completa y citas
      eventos de trace durante todo el proceso, para observabilidad
```

> **Restricción importante**: agentic retrieval **soporta actualmente solo knowledge bases gestionadas**. Con una customer-managed knowledge base no está disponible, y hay que construir la descomposición e iteración a mano con el prompt de orquestación o con Step Functions.

> **Dato decisivo de rendimiento**: es la técnica de retrieval más exacta y **la más cara en latencia**, porque cada iteración añade una planificación y una evaluación del FM sobre los resultados. El paso 4 puede además traer documentos completos. Es lo contrario de una optimización de velocidad: se compra exactitud con tiempo y tokens. Los **eventos de trace** del paso 6 son lo que permite saber cuántas iteraciones hizo y por qué.

### Búsqueda híbrida y su restricción de almacén

Los tres tipos de búsqueda de [kb-test-config](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html), con `overrideSearchType` en la configuración de búsqueda vectorial:

| Tipo | Qué consulta |
| --- | --- |
| **Default** | **Bedrock decide** la estrategia según la configuración del vector store |
| **`HYBRID`** | Combina embeddings vectoriales (semántica) **con el texto en bruto** |
| **`SEMANTIC`** | Solo embeddings vectoriales |

> **Restricción importante, y es la que más se pregunta**: la búsqueda híbrida **solo se soporta en vector stores de Amazon RDS, Amazon OpenSearch Serverless y MongoDB que contengan un campo de texto filtrable**. Con cualquier otro almacén, o si el almacén no tiene ese campo, **la consulta usa búsqueda semántica**. No falla ni avisa: degrada en silencio. Una aplicación que cree estar usando híbrida sobre un almacén no soportado está usando semántica.

El desarrollo completo está en [Task 1.5 · Skill 1.5.4](../domain-1/task-1-5-retrieval.md#tipos-de-búsqueda-en-knowledge-bases).

### Scoring personalizado: el reranker

El skill pide "búsqueda híbrida con scoring personalizado", y en Bedrock el scoring personalizado es el **reranker model**: se selecciona un modelo de reranking que reordena los resultados de la consulta. El detalle, incluida la limitación de que **funciona solo con datos textuales**, está en [Task 1.5 · Skill 1.5.4](../domain-1/task-1-5-retrieval.md#reranking).

> **Dato decisivo sobre la interacción entre reranking y descomposición**: con **query decomposition activada**, el número de resultados reordenados **puede exceder el número base de resultados hasta cinco veces**, porque cada sub-consulta aporta su propio conjunto. Es el efecto que explica que un pipeline con descomposición y reranking consuma mucho más de lo previsto: el reranker recibe hasta cinco veces más candidatos de los que se pidieron.

### Número de resultados: un máximo, no una cantidad

Por defecto una knowledge base devuelve **hasta cinco resultados**, cada uno correspondiente a un chunk de origen, configurable con `numberOfResults` dentro de [`KnowledgeBaseRetrievalConfiguration`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_KnowledgeBaseRetrievalConfiguration.html).

> **Gotcha de chunking jerárquico**: `numberOfResults` fija un **máximo**, no una cantidad exacta, y con **hierarchical chunking** el parámetro se refiere al número de **chunks hijo** que la knowledge base recupera. Como los hijos que comparten padre **se sustituyen por el padre** en la respuesta final, **el número de resultados devueltos puede ser menor que el solicitado**. Pedir 20 y recibir 6 es el comportamiento documentado, no un fallo del retrieval.

### Filtrado por metadatos como palanca de rendimiento

El catálogo de los diez operadores de filtrado y los dos lógicos está en [Task 1.4 · Skill 1.4.2](../domain-1/task-1-4-vector-stores.md#operadores-de-filtrado), con su tipo de dato en [`RetrievalFilter`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrievalFilter.html). Lo que aporta este skill son las **asimetrías de soporte entre almacenes**, que deciden qué se puede filtrar y por tanto cuánto trabajo se evita al motor:

| Operador | Soporte |
| --- | --- |
| `in`, `notIn` | **Mejor soportados en OpenSearch Serverless y Neptune Analytics GraphRAG** |
| `stringContains` | **Mejor soportado en OpenSearch Serverless**. Neptune Analytics GraphRAG soporta la variante de string **pero no la de lista** |
| `listContains` | **Mejor soportado en OpenSearch Serverless** |
| `startsWith`, `stringContains` | **No disponibles** con un índice vectorial en un **bucket de S3 Vectors** |

Y dos requisitos de configuración que bloquean el filtrado por completo:

> **Gotcha del motor de OpenSearch Serverless**: para filtrar por metadatos, el índice vectorial **debe estar configurado con el motor `faiss`**. Si está con **`nmslib`**, hay que **crear una knowledge base nueva** y dejar que Bedrock cree el índice, o crear otro índice con `faiss` y apuntar una knowledge base nueva a él. No es un cambio de configuración: es una migración.

> **Gotcha de Aurora**: al añadir metadatos a un índice vectorial existente en un clúster de Aurora, la recomendación es dar el nombre de una **columna de metadatos personalizada** que los almacene todos en una sola columna, y **hay que crear un índice sobre esa columna**. Si no se da ese nombre, hay que crear **una columna por atributo de metadato** con su tipo de dato.

Un detalle útil para PDFs: con OpenSearch Serverless o Aurora, las knowledge bases generan números de página y los guardan en **`x-amz-bedrock-kb-document-page-number`**, pero **no si se eligió no aplicar chunking** a los documentos. Y en cuanto a nombres reservados, en knowledge bases personalizadas el prefijo reservado es **`x-amz-bedrock`**, mientras en las **totalmente gestionadas** es un **guion bajo** (`_source_uri`, `_data_source_id`); en ninguno de los dos tipos se pueden sobrescribir.

> **Dato decisivo para gestionadas**: en una knowledge base gestionada, **`startsWith` y `stringContains` no se soportan**, y hay que usar `equals`, `greaterThan`, `lessThan`, `in` o `notIn`. Es el tipo de restricción que obliga a rediseñar el esquema de metadatos: si el filtro previsto era por prefijo, hay que materializar ese prefijo como un atributo propio en la ingesta.

### Calidad de datos y re-embedding

GENPERF04-BP01 cierra con la parte que se olvida: mantener la calidad de los datos mediante **evaluaciones regulares de frescura, exactitud y representatividad**, vigilar el **drift de datos**, e implementar procesos de **ingesta continua y re-embedding periódico**. Los mecanismos de comprobación que nombra son tres y complementarios: **chequeos automatizados, revisión humana y análisis de la salida de la IA**.

Y dos exigencias de governance: **políticas claras** y **control de versiones del vector store**.

> La práctica advierte además que **las optimizaciones en un área pueden afectar al sistema entero**, y que hay que prepararse para que **los cuellos de botella se desplacen entre capas** a medida que el sistema escala y los patrones de uso cambian. De ahí que pida **runbooks operativos** para facilitar esos cambios de arquitectura, que es lo que recoge el [Skill 4.3.5](./task-4-3-herramientas-vector-stores-y-fallos.md#skill-435--gestión-operativa-del-vector-store).

---

## Skill 4.2.4 — Rendimiento del FM y configuración de parámetros

> *Mejorar el rendimiento del FM para lograr resultados óptimos en casos de uso GenAI específicos (por ejemplo, usando configuraciones de parámetros específicas del modelo, A/B testing para evaluar mejoras, selección apropiada de temperatura y top-k/top-p según los requisitos).*

### El punto de partida: identificar la tarea

De [Optimize inference parameters to improve response quality](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02-bp02.html). Los parámetros **varían de modelo a modelo**: en escenarios de texto los comunes son **`temperature`, `p` y `k`**, y los modelos de imagen, sonido y vídeo tienen otros hiperparámetros habituales.

El orden que impone la práctica: **primero identificar la tarea** que el modelo debe completar, porque **la tarea informa qué hiperparámetros son los más importantes** en el contexto de la carga. Tareas de texto habituales: resumen, respuesta a preguntas. Los valores y rangos **impactan la calidad de la respuesta, especialmente para tipos de tarea distintos**.

> **Dato decisivo**: la práctica no da una tabla de valores por tarea, y eso es deliberado. Lo que pide es que **los rangos recomendados por tarea se incorporen a una guía de desarrollo interna** o a la política de IA de la organización, **definiendo claramente el proceso para cambiarlos**. La respuesta correcta a "qué temperatura usar" es "la que el proceso de tuning determinó para esa tarea y quedó documentada", no un número.

Los parámetros de inferencia en la generación de una knowledge base, con su ubicación en `textInferenceConfig` y la precedencia frente a `additionalModelRequestFields`, están en [Task 1.5 · Skill 1.5.5](../domain-1/task-1-5-retrieval.md#parámetros-de-inferencia-en-la-generación), y su uso como palanca de refinamiento de prompt en [Task 1.6 · Skill 1.6.5](../domain-1/task-1-6-prompt-engineering-governance.md#parámetros-de-inferencia-como-palanca-de-refinamiento). La referencia por modelo está en [Inference request parameters and response fields for foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-parameters.html).

### El método de búsqueda que documenta el Lens

Es la parte más concreta de la práctica, y describe un procedimiento en dos fases que se puede aplicar tal cual:

```
FASE 1 · Acotar el rango
  probar el valor MAS ALTO y el MAS BAJO de cada hiperparametro
  comparar el resultado de cada prueba contra los datos golden
  aceptar las configuraciones cuyas respuestas se ajustan mejor
    a la respuesta esperada del prompt de ground truth
            │
FASE 2 · Bisecar
  incrementar o decrementar el hiperparametro A LA MITAD
  observar el efecto sobre la respuesta del modelo
  repetir
            │
  PARAR cuando los efectos del cambio son despreciables
```

> **Dato decisivo**: el Lens llama a la fase 2 un *enfoque newtoniano*, y su condición de parada es explícita: **continuar hasta que los efectos de los cambios del hiperparámetro sean despreciables**. Es una búsqueda por bisección contra el golden dataset, no una exploración por intuición. Y presupone que **el golden dataset ya existe**, que es GENPERF01-BP01 y lo que desarrolla el [Skill 4.3.6](./task-4-3-herramientas-vector-stores-y-fallos.md#skill-436--troubleshooting-de-modos-de-fallo-propios-de-genai).

### Automatizar el tuning con LLM-as-a-judge

La práctica nombra el patrón **LLM-as-a-judge** como *técnica potente para automatizar la naturaleza iterativa del tuning de hiperparámetros*: un LLM aparte evalúa si la respuesta del modelo es apropiada para el prompt dado.

Los dos escenarios en los que lo recomienda: cuando hay **un conjunto grande de prompts de ground truth**, y cuando **faltan recursos para un proceso completo con humano en el bucle**. Y una tercera condición de adopción: conviene adoptar un proceso así de robusto **cuando los requisitos de la carga cambian con regularidad**, porque el tuning deja de ser un ejercicio puntual.

La implementación gestionada es [Evaluate model performance using another LLM as a judge](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-judge.html), con sus once métricas `Builtin.*` desarrolladas en [Task 3.4 · Skill 3.4.2](../domain-3/task-3-4-ia-responsable.md#las-once-métricas-built-in-del-judge-model).

### A/B testing de verdad: versiones y alias

El skill pide A/B testing para evaluar mejoras. El mecanismo documentado no es una funcionalidad llamada "A/B testing", sino la combinación de **versión más alias** de Bedrock Prompt Management, de [Deploy a prompt to your application using versions](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-deploy.html): la versión es el artefacto inmutable, el alias es el puntero que la aplicación invoca, y mover el alias cambia qué variante recibe el tráfico sin desplegar código.

El desarrollo completo está en [Task 1.6 · Skill 1.6.3](../domain-1/task-1-6-prompt-engineering-governance.md#bedrock-prompt-management) y su uso como palanca de comparación en [Task 3.4 · Skill 3.4.2](../domain-3/task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness). Lo que añade este skill es qué se compara:

| Qué se varía entre A y B | Cómo se despliega | Qué se mide |
| --- | --- | --- |
| **Texto del prompt** | Versión nueva, alias movido | Métricas de calidad más tokens de entrada |
| **Parámetros de inferencia** | Versión nueva (van en la versión) | Calidad y longitud de salida |
| **Modelo** | Alias apuntando a otra variante, o AdvPO | Calidad, coste y latencia |
| **Configuración de retrieval** | Configuración de la petición | Relevancia y latencia de retrieval |

> **Gotcha de medición**: para que un A/B sea interpretable hay que poder **atribuir cada invocación a su variante**, y eso exige etiquetar con `requestMetadata` (por ejemplo `promptVersion`) como se vio en [Task 2.5 · Skill 2.5.6](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#la-fuente-model-invocation-logging). Sin esa etiqueta, los invocation logs de las dos variantes son indistinguibles y el experimento no se puede cerrar.

Para comparar el mismo prompt en varios modelos a la vez, la herramienta es **Advanced Prompt Optimization** del [Skill 4.1.1](./task-4-1-costes-y-eficiencia-de-recursos.md#acortar-el-prompt-las-dos-vías-que-ofrece-bedrock), que evalúa hasta cinco modelos y devuelve scores, coste y latencia por modelo. El resto del pipeline de aseguramiento de calidad de prompts está en [Task 1.6 · Skill 1.6.4](../domain-1/task-1-6-prompt-engineering-governance.md#skill-164--aseguramiento-de-calidad-de-prompts).

### El aviso de fondo: no determinismo

De [GENPERF02](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02.html), y es la premisa que hace que este skill exista: los foundation models son **inherentemente no deterministas** e **introducen un elemento de aleatoriedad en los sistemas**, difícil de contabilizar **especialmente cuando las técnicas tradicionales de evaluación de rendimiento se apoyan en el determinismo**.

Lo que la pregunta exige para convivir con eso: **umbrales mínimos de rendimiento bien entendidos**, **requisitos claros para cada tarea del modelo**, y **un conjunto de acciones de remediación** para el caso de degradación o de aparición de un modelo nuevo.

---

## Skill 4.2.6 — Perfilado y comunicación entre servicios

> *Optimizar el rendimiento del sistema de FM para workflows GenAI (por ejemplo, usando perfilado de llamadas a la API para patrones prompt-completion, optimización de consultas a la base de datos vectorial para aumentación de recuperación, técnicas de reducción de latencia específicas de la inferencia de LLM, patrones eficientes de comunicación entre servicios).*

### Perfilar el patrón prompt-completion

De [Collect performance metrics from generative AI workloads](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf01-bp02.html), la instrucción sobre qué recoger es la clave del skill y va contra el instinto de instrumentar cada componente: recoger **métricas y trazas de aplicación relativas al flujo de la información, más que a una pieza concreta del workflow**. El objetivo declarado: **determinar cómo rinde la aplicación entera al interactuar con soluciones de IA generativa**, lo que ayuda a **triar más rápido y mejorar los tiempos de resolución**.

La práctica nombra además dos herramientas concretas para capturar métricas adicionales: un framework de traza tipo **OpenLLMetry**, y **`fmeval`** como framework de evaluación sobre un dataset de benchmarking. Y para el tracking centralizado de experimentos, **SageMaker AI con MLflow**.

El presupuesto de latencia de una petición RAG, que es lo que el perfilado debe descomponer:

```
PETICION                                        contribucion tipica
──────────────────────────────────────────────────────────────────────
1 · Validacion y autorizacion en el borde       milisegundos
2 · Embedding de la consulta                    decenas de ms
3 · Busqueda en el vector store                 ms a decenas de ms
    (si hay reranking, sumar el modelo)
4 · Construccion del prompt                     despreciable
5 · INFERENCIA DEL FM                           segundos  ← domina
    TimeToFirstToken                              primer token
    resto de la generacion                        proporcional a tokens
6 · Guardrail de salida                         decenas de ms
7 · Serializacion y entrega                     milisegundos
```

> **Dato decisivo**: el paso 5 domina el total por uno o dos órdenes de magnitud, y es proporcional a **los tokens generados**. Consecuencia para el perfilado: optimizar los pasos 1 a 4 rara vez mueve la aguja, salvo que el retrieval esté patológicamente mal. Las dos palancas que sí la mueven son **generar menos tokens** (`maxTokens`, esquema de respuesta con clave del [Skill 4.1.1](./task-4-1-costes-y-eficiencia-de-recursos.md#controlar-la-longitud-de-la-respuesta)) y **no generar nada** (caché del [Skill 4.1.4](./task-4-1-costes-y-eficiencia-de-recursos.md#skill-414--sistemas-de-caching-inteligente)).
>
> El corolario que conviene tener presente: **con streaming, el paso 5 deja de dominar la latencia percibida** aunque siga dominando la real. Es la razón por la que `TimeToFirstToken` es la métrica de experiencia de usuario y `InvocationLatency` la de coste y capacidad.

La herramienta para descomponer ese presupuesto entre fronteras de servicio es **AWS X-Ray**, con su trace map, segmentos y subsegmentos, y las anotaciones por `modelId`, tokens, `stopReason` y acierto de caché, desarrollada en [Task 2.4 · Skill 2.4.3](../domain-2/task-2-4-integraciones-api-fm.md#observabilidad-entre-fronteras-de-servicio-x-ray). La capa específica de GenAI se trata en el [Skill 4.3.1](./task-4-3-observabilidad-y-metricas.md#skill-431--observabilidad-holística).

### Optimización de la consulta al vector store

El skill lo pide explícitamente y las palancas están repartidas. La vista conjunta, ordenada por cuándo se puede aplicar:

| Cuándo | Palanca | Efecto |
| --- | --- | --- |
| **Solo antes de ingerir** | Estrategia de chunking, modelo y dimensión de embeddings | El mayor de todos, e irreversible sin re-embedding |
| **Al crear el índice** | Algoritmo ANN, motor (`faiss` frente a `nmslib`), jerarquía de índices, sharding | Alto; cambiarlo después es una migración |
| **Por petición** | `numberOfResults`, `overrideSearchType`, filtros de metadatos, reranking, descomposición | Medio, y el único ajustable en caliente |
| **Continuo** | Re-embedding, chequeos de calidad, vigilancia de drift | Sostiene la relevancia en el tiempo |

> **Dato decisivo**: el **filtrado por metadatos** es la palanca por petición con mejor relación esfuerzo-resultado, porque **reduce el espacio de búsqueda antes de comparar vectores**. Un filtro por fecha o por tenant hace más por la latencia de retrieval que ajustar parámetros del grafo. El ejemplo oficial es filtrar por `epoch_modification_time` mayor que un valor para quedarse con lo reciente.

Las palancas independientes del motor (reducción de dimensiones, embeddings binarios, reranking con menos resultados, S3 Vectors, niveles de almacenamiento) están en [Task 1.4 · Skill 1.4.3](../domain-1/task-1-4-vector-stores.md#palancas-de-rendimiento-independientes-del-motor), y las optimizaciones específicas de OpenSearch Serverless en [Optimizaciones de OpenSearch Serverless](../domain-1/task-1-4-vector-stores.md#optimizaciones-de-opensearch-serverless).

### Técnicas de reducción de latencia específicas de la inferencia de LLM

Las seis que documenta el portal, en el orden en que conviene aplicarlas:

```
1 · Streaming                     → baja TimeToFirstToken, no InvocationLatency
                                     ConverseStream, InvokeModelWithResponseStream
                                     RetrieveAndGenerateStream para RAG
2 · Cachear                       → evita la inferencia por completo
                                     semantica, determinista, prompt caching
3 · Acortar la salida             → maxTokens, stopSequences, esquema con clave
                                     la latencia es proporcional a los tokens
4 · Acortar la entrada            → prompt mas corto, poda del historico
                                     prompt caching del prefijo estable
5 · Elegir modelo y modo          → modelo menor que cumpla la barra
                                     latency-optimized inference (4 modelos)
6 · Acercar el computo            → cross-Region inference
                                     tier Priority si el throttling afecta
```

> El orden importa porque las tres primeras no cambian el modelo ni el coste unitario, y las tres últimas sí. Empezar por la 5 es el error habitual: se cambia de modelo antes de comprobar si el problema era una respuesta de 4.000 tokens que nadie lee.

Para RAG en streaming, la API es [`RetrieveAndGenerateStream`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerateStream.html), y el detalle de la decisión de modo de guardrail sobre un stream está en [Task 2.4 · Skill 2.4.2](../domain-2/task-2-4-integraciones-api-fm.md#skill-242--interacción-en-tiempo-real-y-streaming).

### Patrones eficientes de comunicación entre servicios

El criterio que ordena la elección es si el llamante puede esperar el tiempo que la generación necesita:

| Patrón | Cuándo | Riesgo si se elige mal |
| --- | --- | --- |
| **Sincrónico** con respuesta completa | Salida estructurada corta que el cliente consume entera | Timeout de la integración si la generación crece |
| **Sincrónico con streaming** | Texto para mostrar a una persona | Ninguno para el usuario; sí para el cálculo de coste |
| **Asíncrono con `202` y polling** | Generación larga que no cabe en la ventana del llamante | Coste de polling y latencia de descubrimiento |
| **Asíncrono con notificación** | Igual, pero con cliente conectado por WebSocket | Complejidad de gestión de conexión |
| **Event-driven con cola** | Volumen variable que se puede diferir | Latencia de cola; exige idempotencia |
| **Batch** | Nada urgente | Ventana de 24 h |

> **Gotcha de coste que se pasa por alto**: en **Lambda response streaming**, si el cliente corta la conexión **la ejecución no se interrumpe y se factura la duración completa**. Hace falta un límite propio; no se puede confiar en la desconexión del cliente. El detalle está en [Task 2.5 · Skill 2.5.1](../domain-2/task-2-5-patrones-de-aplicacion-y-tooling.md#estrategias-de-reintento-ante-timeouts-del-modelo).

Y la regla que se deriva de las combinaciones soportadas de API Gateway: **el modo de transferencia es parte del contrato de la API, no un detalle de implementación**. Cambiar de bufferizado a streaming obliga a cambiar el formato de salida de la Lambda y el URI de la integración, así que conviene decidirlo antes de publicar.

---

## Resumen operativo: retrieval y parámetros

| Si la pregunta menciona… | La respuesta apunta a |
| --- | --- |
| Un retrieval lento que parece un modelo lento | Efectos en cascada **difíciles de identificar** (GENPERF04) |
| Qué optimizar primero en un vector store | **Chunking y embeddings**: solo se pueden cambiar antes de ingerir |
| Algoritmo ANN de indexado rápido | **LSH** |
| Algoritmo ANN de exactitud alta | **HNSW** |
| Algoritmo ANN equilibrado | **IVF** |
| Algoritmo ANN de almacenamiento compacto | **PQ** |
| Índice que no cabe en memoria | **PQ** o **reducir dimensión**, no otro algoritmo de búsqueda |
| Índice único frente a jerarquía | La jerarquía **generalmente supera** al índice único |
| Más dimensiones siempre es mejor | **No**: 256 bien afinado puede batir a 1024 genérico |
| Rango de dimensiones limitado | Pasa **en el acceso gestionado de Bedrock**; SageMaker AI ofrece más |
| Descomponer una consulta multifacética | **Query decomposition**, tipo `QUERY_DECOMPOSITION` |
| Recuperación que evalúa si los resultados bastan | **Agentic retrieval** con `AgenticRetrieveStream` |
| Agentic retrieval sobre knowledge base propia | **No disponible**: solo gestionadas |
| El FM necesita el documento completo | Paso de **expansión** con `GetDocumentContent` |
| Saber cuántas iteraciones hizo el agentic retrieval | **Eventos de trace** del evento de resultado |
| Híbrida sobre un vector store no soportado | **Degrada a semántica en silencio** |
| Dónde se soporta híbrida | **RDS, OpenSearch Serverless y MongoDB** con campo de texto filtrable |
| Scoring personalizado sobre híbrida | **Reranker model**, solo datos textuales |
| Reranking con descomposición activada | Los resultados reordenados pueden ser **hasta 5 veces** los base |
| Pedí 20 resultados y llegaron 6 | **Hierarchical chunking**: los hijos se sustituyen por el padre |
| `numberOfResults` como cantidad exacta | Es un **máximo** |
| Filtrar por metadatos y no funciona en OpenSearch Serverless | El índice debe usar el motor **`faiss`**, no `nmslib` |
| Metadatos en Aurora | Columna personalizada única **con índice creado sobre ella** |
| `startsWith` en una knowledge base gestionada | **No se soporta**: usar `equals`, `greaterThan`, `lessThan`, `in`, `notIn` |
| Filtros no disponibles en S3 Vectors | **`startsWith` y `stringContains`** |
| Números de página de un PDF | **`x-amz-bedrock-kb-document-page-number`**, no si se eligió sin chunking |
| Prefijos reservados de metadatos | **`x-amz-bedrock`** en personalizadas, **guion bajo** en gestionadas |
| Mantener la relevancia en el tiempo | **Re-embedding periódico**, chequeos de calidad y vigilancia de drift |
| Los cuellos de botella se mueven de capa | Documentado: por eso pide **runbooks operativos** |
| Qué temperatura usar para una tarea | La que el **tuning determinó** y quedó en la política de IA |
| Método para encontrar el valor de un hiperparámetro | **Extremos primero**, luego **bisección** hasta efecto despreciable |
| Automatizar el tuning iterativo | **LLM-as-a-judge**, sobre todo sin recursos para humano en el bucle |
| Cómo se hace A/B testing de prompts | **Versión más alias**: la versión es inmutable, el alias enruta |
| A/B que no se puede interpretar | Falta **`requestMetadata`** para atribuir la invocación a su variante |
| Comparar un prompt en varios modelos | **Advanced Prompt Optimization**, hasta 5 con coste y latencia |
| Evaluación tradicional que presupone determinismo | Los FM son **inherentemente no deterministas** (GENPERF02) |
| Qué instrumentar en una aplicación GenAI | **El flujo de la información**, no una pieza concreta |
| Qué domina la latencia de una petición RAG | **La inferencia**, por uno o dos órdenes de magnitud |
| Optimizar el retrieval no mejoró la latencia | Esperable: el paso que domina es la **generación** |
| Palanca de retrieval por petición con mejor retorno | **Filtrado por metadatos**: reduce el espacio antes de comparar |
| Primera técnica de reducción de latencia | **Streaming**, y después cachear; cambiar de modelo va al final |
| RAG con respuesta en streaming | **`RetrieveAndGenerateStream`** |
| Cliente que corta un stream de Lambda | **Se factura la duración completa**: hace falta límite propio |
| Cambiar de bufferizado a streaming | Es un **cambio de contrato de la API**, no de implementación |
