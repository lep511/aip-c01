# Task 5.1 — Frameworks de evaluación y evaluación de modelos

[← Volver al índice](./README.md)

Skills cubiertos: **5.1.1**, **5.1.2**, **5.1.3**, **5.1.5**.

Este archivo cubre el eje de **qué se mide y quién puntúa**: las métricas con las que AWS caracteriza la calidad de una salida de FM, la superficie completa de Amazon Bedrock evaluations, y el circuito de feedback humano.

El marco oficial que ordena el task es **GENOPS01** del [Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/operational-excellence.html), la pregunta [*¿cómo se consigue y se verifica una calidad de salida consistente?*](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops01.html). Sus dos best practices se reparten exactamente entre dos skills de este archivo:

| Best practice | Skill |
| --- | --- |
| [GENOPS01-BP01 Periodically evaluate functional performance](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops01-bp01.html) | 5.1.1, 5.1.2, 5.1.5 |
| [GENOPS01-BP02 Collect and monitor user feedback](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops01-bp02.html) | 5.1.3 |

Y el marco de decisión está en el **Responsible AI Lens**, cuya área [Evaluate and release](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/evaluate-and-release.html) plantea la evaluación como insumo de una decisión binaria de release: se prueba el sistema contra cada criterio, se agregan los resultados ([RAIER02](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/raier02.html)) y se decide teniendo en cuenta la **incertidumbre compuesta** de las decisiones individuales, no solo si cada métrica pasó.

> **Dato decisivo del Lens**: si un criterio de release no se cumple, el release **todavía puede ser posible** si el riesgo residual se divulga mediante mecanismos de transparencia. La alternativa es volver a [System planning](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/system-planning.html) a revisar mitigaciones. "No pasa la métrica" no equivale automáticamente a "no se lanza".

---

## Skill 5.1.1 — Frameworks de evaluación de la calidad de las salidas del FM

> *Desarrollar frameworks de evaluación completos para valorar la calidad y la efectividad de las salidas del FM más allá de los enfoques tradicionales de evaluación de ML (por ejemplo, usando métricas de relevancia, exactitud factual, consistencia y fluidez).*

### Las dos familias de métricas que no hay que mezclar

Amazon Bedrock no tiene un catálogo único de métricas. Tiene **dos**, con mecanismos de cálculo distintos, y confundirlas es el error que este skill explota.

| Familia | Cómo se calcula | Dónde se configura |
| --- | --- | --- |
| **Métricas computadas** | Algoritmos deterministas sobre la respuesta y su referencia: F1, BERTScore, word error rate, `detoxify` | Job automático, eligiendo un **task type** y un dataset |
| **Métricas de juez (`Builtin.*`)** | Un segundo LLM puntúa la respuesta y **explica la puntuación** | Job de *model as a judge*, eligiendo métricas de una lista |

### Los cuatro task types y lo que cada uno computa

De [Model evaluation task types](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-tasks.html). **Un job admite un solo task type.** Cada uno trae sus datasets integrados y sus tres métricas posibles: accuracy, robustness y toxicity.

| Task type | Accuracy | Robustness | Datasets integrados (API) |
| --- | --- | --- | --- |
| [General text generation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-tasks-general-text.html) | **Real world knowledge (RWK) score** | **Word error rate** | `Builtin.T-REx`, `Builtin.BOLD`, `Builtin.WikiText2`, `Builtin.RealToxicityPrompts` |
| [Text summarization](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-tasks-text-summary.html) | **BERTScore** | **deltaBERTScore / BERTScore × 100** | Gigaword |
| [Question and answer](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-tasks-question-answer.html) | **NLP-F1** | **deltaF1 / F1 × 100** | BoolQ, NaturalQuestions, TriviaQA |
| [Text classification](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-text-classification.html) | `classification_accuracy_score` | `delta_classification_accuracy_score` | Women's Ecommerce Clothing Reviews |

La toxicity se calcula en los cuatro con el algoritmo **`detoxify`**, y un valor bajo es el bueno.

> **Gotcha documentado**: en general text generation hay un problema conocido del sistema que **impide a los modelos Cohere completar la evaluación de toxicity**. Está en la propia página del task type.

### Por qué esto va "más allá de la evaluación tradicional de ML": la robustness semántica

Es la parte del skill que más se pasa por alto. De [Review metrics for an automated model evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-report-programmatic.html), la robustness **no se mide contra una etiqueta de verdad**: se mide perturbando la entrada y comparando la salida consigo misma.

Bedrock aplica **cinco tipos de perturbación que preservan el significado**, y perturba cada prompt del dataset **aproximadamente 5 veces**:

1. Convertir el texto a minúsculas.
2. Typos de teclado.
3. Convertir números a palabras.
4. Cambios aleatorios a mayúsculas.
5. Añadir o borrar espacios en blanco de forma aleatoria.

Cada respuesta perturbada se envía a inferencia y se usa para calcular el score automáticamente.

> **Dato decisivo de interpretación**: en robustness y en toxicity, **un score bajo es bueno**. En accuracy, un score alto es bueno. La robustness mide *cuánto cambia la salida* ante una perturbación irrelevante, así que cuanto menos cambie, mejor. Invertir esa lectura es el error clásico.

Y el coste oculto que la página deja claro: como cada prompt se perturba unas 5 veces y cada perturbación se envía a inferencia, **activar robustness multiplica por unas seis veces las invocaciones del job** respecto a medir solo accuracy.

### Las once métricas de juez

De [Use metrics to understand model performance](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-metrics.html). El modelo evaluador usa un prompt distinto por métrica.

| Métrica | Identificador | Qué mide |
| --- | --- | --- |
| Correctness | `Builtin.Correctness` | Si la respuesta al prompt es correcta. Si el dataset trae respuesta de referencia (ground truth), el juez la tiene en cuenta |
| Completeness | `Builtin.Completeness` | Si la respuesta contesta **todas** las preguntas del prompt. También aprovecha el ground truth si existe |
| Faithfulness | `Builtin.Faithfulness` | Si la respuesta contiene información que **no está en el prompt**, para medir fidelidad al contexto disponible |
| Helpfulness | `Builtin.Helpfulness` | Utilidad de la respuesta: si sigue las instrucciones, si es sensata y coherente, y si anticipa necesidades implícitas |
| Logical coherence | **`Builtin.Coherence`** | Huecos lógicos, inconsistencias y contradicciones dentro de la respuesta |
| Relevance | `Builtin.Relevance` | Relevancia de la respuesta respecto al prompt |
| Following instructions | `Builtin.FollowingInstructions` | Si la respuesta respeta las indicaciones exactas del prompt |
| Professional style and tone | `Builtin.ProfessionalStyleAndTone` | Si el estilo, el formato y el tono son apropiados en un entorno profesional |
| Harmfulness | `Builtin.Harmfulness` | Si la respuesta contiene contenido dañino |
| Stereotyping | `Builtin.Stereotyping` | Estereotipos de cualquier tipo, **positivos o negativos** |
| Refusal | `Builtin.Refusal` | Si la respuesta declina contestar o rechaza la petición dando razones |

> **Dato decisivo**: la métrica que se llama *Logical coherence* tiene el identificador **`Builtin.Coherence`**, sin el `Logical`. En las evaluaciones de RAG, la misma métrica se llama **`Builtin.LogicalCoherence`**, con el `Logical`. Es el único caso de nombre divergente entre los dos catálogos, y está detallado en el [Skill 5.1.5](#skill-515--evaluación-multiperspectiva-rag-juez-y-humanos).

### Cómo se mapea el enunciado del skill a métricas que existen de verdad

El skill nombra cuatro cualidades. Solo tres tienen una métrica de AWS con ese nombre.

| Cualidad del enunciado | Métrica oficial que la cubre |
| --- | --- |
| **Relevance** | `Builtin.Relevance` de forma directa |
| **Factual accuracy** | `Builtin.Correctness` en el juez, y **RWK score** en el task type de general text generation, que mide la capacidad del modelo de codificar conocimiento factual del mundo real |
| **Consistency** | `Builtin.Coherence` para la consistencia interna de una respuesta, y la **robustness semántica** para la consistencia entre ejecuciones ante entradas equivalentes. Son dos consistencias distintas |
| **Fluency** | **No existe ninguna métrica de AWS llamada *fluency*.** Lo más cercano es `Builtin.ProfessionalStyleAndTone`, más la métrica *Readability* que aparece en las plantillas de prompt del juez |

### Las plantillas de prompt del juez están publicadas

Un detalle que casi nadie mira y que cambia cómo se interpreta un score: AWS publica **el prompt real de cada métrica, por modelo juez**. Hay una página por modelo, por ejemplo la de [Anthropic Claude Sonnet 4.6](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-judge-prompt-claude-sonnet-4-6.html), y dentro hay una sección por métrica más una sección de **score mapping**.

Esas páginas revelan tres cosas que el catálogo de métricas no dice:

- Varias métricas tienen **dos variantes**: *Correctness with ground truth* y *Correctness with no ground truth*, *Completeness with ground truth* y *Completeness without ground truth*. El juez usa un prompt distinto según si el dataset trae referencia.
- Existe una métrica **Readability** en las plantillas.
- Las métricas se puntúan en **escalas Likert de 5 puntos** que luego se mapean a un valor numérico.

> **Gotcha de comparabilidad**: como cada modelo juez tiene su propia plantilla publicada, **los scores de juez no son comparables entre modelos juez distintos**. Cambiar el evaluador cambia el prompt, y por tanto la escala efectiva. Para comparar dos modelos generadores hay que fijar el modelo juez.

---

## Skill 5.1.2 — Evaluación sistemática para identificar la configuración óptima

> *Crear sistemas de evaluación de modelo sistemáticos para identificar configuraciones óptimas (por ejemplo, usando Amazon Bedrock Model Evaluations, A/B testing y canary testing de FMs, evaluación multi-modelo, análisis coste-rendimiento para medir eficiencia de tokens, ratios de latencia frente a calidad y resultados de negocio).*

### Los cuatro tipos de job que existen

De [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html). La superficie es más amplia de lo que el nombre "Model Evaluations" sugiere, porque cubre también recursos que no son modelos.

| Tipo de job | Quién puntúa | Qué evalúa |
| --- | --- | --- |
| [**Programático / automático**](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-automatic.html) | Algoritmos deterministas | Capacidad del modelo de ejecutar un task type, con dataset propio o integrado |
| [**Model as a judge**](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-judge.html) | Un segundo LLM | Respuestas puntuadas y **explicadas** métrica a métrica |
| [**Con human workers**](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-human.html) | Personas de un work team | Valoraciones y preferencias humanas |
| [**RAG evaluations**](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html) | Un LLM evaluador | Knowledge bases de Bedrock y fuentes RAG externas |

### Evaluación multi-modelo, y el truco para evaluar lo que no está en Bedrock

Los tipos de **modelo generador** admitidos van más allá de los foundation models: modelos del Marketplace de Bedrock, modelos personalizados, modelos importados, **prompt routers** y modelos con Provisioned Throughput comprado. Los modelos invocados por la Responses API de OpenAI en el endpoint `bedrock-mantle` también valen, pero con un límite.

> **Gotcha de consola**: los modelos generadores invocados a través de la **Responses API de OpenAI solo se pueden usar desde la CLI y la API de Bedrock**. La consola de Bedrock no permite seleccionarlos.

Y la palanca clave para la evaluación multi-modelo de verdad: **traer las respuestas ya generadas**. En vez de que Bedrock invoque el modelo, se aporta la inferencia dentro del prompt dataset y Bedrock **se salta el paso de invocación** y evalúa directamente los datos aportados. En la configuración del job eso es una fuente de inferencia precomputada en lugar de un modelo de Bedrock, con un identificador propio.

> **Dato decisivo**: eso convierte a Bedrock evaluations en un **motor de scoring independiente del proveedor**. Un modelo self-hosted, un modelo de otro cloud o una versión antigua congelada se pueden puntuar con las mismas métricas `Builtin.*` que un modelo de Bedrock, sin que Bedrock lo invoque nunca. Para RAG hay configuraciones precomputadas equivalentes, tanto para [retrieve-only](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_EvaluationPrecomputedRetrieveSourceConfig.html) como para [retrieve-and-generate](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_EvaluationPrecomputedRetrieveAndGenerateSourceConfig.html).

Las **listas de modelos juez no son una sola**: la de métricas integradas y la de métricas propias se solapan mucho pero no coinciden. Antes de diseñar un job con métricas propias hay que comprobar que el juez elegido está en la segunda lista, no solo en la primera. Los perfiles de **cross-Region inference** están soportados en ambas.

> **Gotcha de documentación**: la página [Supported Regions and models for model evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-support.html) **no contiene ninguna tabla de Regiones ni de modelos**. Solo remite a los [model cards](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html) para consultar modelo por modelo. Si la pregunta plantea "dónde se comprueba qué modelos admiten evaluación", la respuesta es el model card, no una lista central.

### Dónde vive de verdad el A/B testing y el canary testing

El enunciado mete en la misma frase "Bedrock Model Evaluations" y "A/B testing y canary testing de FMs". Son cosas distintas y viven en servicios distintos.

> **Dato decisivo**: **Bedrock evaluations no despliega nada.** Es un job offline que lee un dataset, produce scores y escribe un informe en S3. No enruta tráfico, no tiene variantes, no hace rollback. Todo el A/B y el canary de un FM está fuera de Bedrock evaluations.

| Mecanismo | Dónde está documentado | Qué aporta |
| --- | --- | --- |
| **A/B testing con tráfico repartido** | [Testing models with production variants](https://docs.aws.amazon.com/sagemaker/latest/dg/model-ab-testing.html) de SageMaker AI | Endpoints multi-variante: se reparte la invocación entre variantes por distribución de tráfico, **o** se invoca una variante concreta por petición |
| **Shadow testing** | [Shadow tests](https://docs.aws.amazon.com/sagemaker/latest/dg/shadow-tests.html) | Se despliega la variante nueva en modo sombra y se le enruta **una copia** de las peticiones reales, sin impacto en el usuario final. Valida modelo, contenedor **o instancia** |
| **Canary y blue/green** | [Blue/green con canary traffic shifting](https://docs.aws.amazon.com/sagemaker/latest/dg/deployment-guardrails-blue-green-canary.html) | Desplazamiento progresivo del tráfico con guardrails de despliegue y rollback |
| **Evaluación offline** | Bedrock evaluations | Scores comparables entre configuraciones, antes de que haya tráfico |

> **Gotcha de vocabulario**: la distribución de tráfico entre variantes es **A/B testing**; la copia de tráfico a una variante que no responde al usuario es **shadow testing**. El shadow no reparte usuarios, los duplica. Es la diferencia que las preguntas de este skill suelen explotar.

### Análisis coste-rendimiento: lo que el job no te da

El skill pide medir eficiencia de tokens, ratio latencia-calidad y resultados de negocio. El informe del job de evaluación **no contiene ninguna de las tres cosas**.

| Lo que pide el skill | De dónde sale realmente |
| --- | --- |
| **Calidad** | Scores del job de evaluación |
| **Eficiencia de tokens** | Métricas de runtime de `AWS/Bedrock`: ver [Domain 4 · Skill 4.1.1](../domain-4/task-4-1-costes-y-eficiencia-de-recursos.md#skill-411--sistemas-de-eficiencia-de-tokens) |
| **Latencia** | [Monitor bedrock-runtime inference using CloudWatch metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html), y las palancas de [Domain 4 · Skill 4.2.1](../domain-4/task-4-2-latencia-y-throughput.md#skill-421--sistemas-de-ia-responsivos) |
| **Resultados de negocio** | Métricas propias, correlacionadas en dashboards: ver [Domain 4 · Skill 4.3.1](../domain-4/task-4-3-observabilidad-y-metricas.md#skill-431--observabilidad-holística) |

El **ratio latencia-calidad** es por tanto un cálculo que se construye cruzando dos fuentes: el score del job y la latencia observada del modelo. Ninguna página de AWS lo publica como métrica.

Una palanca de configuración que sí es evaluable end-to-end: los [prompt routers](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) se admiten como modelo generador, así que **la política de routing entre un modelo grande y uno pequeño se puede puntuar como si fuera un modelo más**. Es la forma documentada de validar el escalonado por complejidad del [Skill 4.1.2](../domain-4/task-4-1-costes-y-eficiencia-de-recursos.md#skill-412--frameworks-de-selección-de-modelo-coste-efectiva) con métricas de calidad en vez de con intuición.

### Requisitos y salida del job

De [Required steps before creating your first automatic model evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-automatic.html):

- Todos los datos, de entrada y de salida, deben estar en un bucket de S3 **en la misma Región** que el job.
- Hace falta un **service role** con política de confianza propia, documentado en [Service role requirements](https://docs.aws.amazon.com/bedrock/latest/userguide/automatic-service-roles.html).
- Por defecto Bedrock cifra los datos del job con una clave KMS propiedad de AWS; se puede sustituir por una clave propia. El detalle está en [Data management and encryption](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-data-management.html).

> **Dato decisivo sobre CORS**: la [configuración de CORS en el bucket de S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-security-cors.html) es obligatoria **solo para los jobs con human workers**. Los jobs automáticos no la necesitan. Es un requisito que aparece en las dos páginas de setup precisamente para marcar la diferencia.

Los resultados se guardan como ficheros **JSON Lines**, y la ruta de S3 **difiere según el tipo de job**, según [Understand how the results are saved in Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-report-s3.html):

| Tipo de job | Estructura de la ruta de salida |
| --- | --- |
| Automático | `job-name / job-uuid / models / model-id / taskTypes / task-type / datasets / dataset / fichero` |
| Con human workers | `job-name / job-uuid / datasets / dataset-name / fichero` |

En los jobs automáticos cada registro arranca con una clave de resultado que contiene `scores` (nombre de métrica y valor calculado), más una copia del registro de entrada y las respuestas del modelo con el ARN del modelo evaluado.

Las llamadas de gestión del job quedan auditadas: los eventos de management de CloudTrail para jobs de evaluación están en [CloudTrail management events in model evaluation jobs](https://docs.aws.amazon.com/bedrock/latest/userguide/cloudtrail-events-in-model-evaluations.html).

> **Gotcha de lectura del informe**: la tarjeta del informe muestra el total de prompts del dataset **y cuántos recibieron respuesta**. Si el segundo número es menor, hubo prompts que provocaron un error en el modelo y no devolvieron inferencia. **Solo las respuestas obtenidas entran en el cálculo de las métricas**, así que un score alto sobre un dataset medio fallido no dice lo que parece. Hay que comprobar el fichero de salida en S3.

---

## Skill 5.1.3 — Evaluación centrada en el usuario y feedback humano

> *Desarrollar mecanismos de evaluación centrados en el usuario para mejorar continuamente el rendimiento del FM a partir de la experiencia de uso (por ejemplo, usando interfaces de feedback, sistemas de rating de las salidas del modelo, workflows de anotación para valorar la calidad de la respuesta).*

### Los cinco métodos de rating

Es el dato más concreto del skill, y está en la API, no en la guía: el tipo [`HumanEvaluationCustomMetric`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_HumanEvaluationCustomMetric.html) obliga a declarar, por métrica, **cómo quieres que los humanos la valoren**.

| Método de rating | Naturaleza |
| --- | --- |
| `ThumbsUpDown` | Binario, sobre una sola respuesta |
| `IndividualLikertScale` | Escala, sobre una sola respuesta |
| `ComparisonLikertScale` | Escala, comparando dos respuestas |
| `ComparisonChoice` | Elección de la mejor entre dos |
| `ComparisonRank` | Ordenación de respuestas |

> **Dato decisivo**: los tres métodos `Comparison*` son la razón por la que un job humano **compara como máximo dos foundation models**. El límite no es arbitrario: los métodos de rating comparativos están definidos sobre pares.

Cada métrica humana lleva `name` (1 a 63 caracteres, con patrón restringido a alfanuméricos, guion, subrayado y punto), el `ratingMethod` obligatorio y una `description` opcional. **El nombre es lo que el evaluador humano ve en la interfaz**, así que es parte del diseño de la evaluación, no un identificador interno.

### Los límites del work team

De [Manage a work team for human evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/human-worker-evaluations.html):

| Límite | Valor |
| --- | --- |
| Workers por work team | **50 como máximo** |
| Direcciones de correo por tanda | **50 como máximo** |
| Modelos comparados en un job humano | **2 como máximo** |

Para pasar de ahí hay que gestionar el workforce desde la consola de Amazon Cognito o la de SageMaker Ground Truth, no desde Bedrock.

### Las tres trampas de notificación

Esta página documenta tres comportamientos que rompen un programa de feedback continuo si no se conocen:

1. Los workers reciben notificación de su job asignado **solo la primera vez que se les añade** a un work team.
2. Para cualquier job nuevo asignado a un worker existente, **hay que notificarle a mano** y darle la URL del portal. El portal es el mismo para todos los jobs de la cuenta en esa Región, y el worker reutiliza sus credenciales anteriores.
3. Si se borra a un worker de un work team durante la creación de un job, **pierde el acceso a todos los jobs** que tuviera asignados, no solo a ese.

### Qué hay debajo: flow definitions y human loops

El detalle que explica la arquitectura: los permisos de consola para crear un job humano, listados en [Creating your first model evaluation that uses human workers](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-type-human.html), incluyen acciones de SageMaker AI de crear y describir **flow definitions** y de arrancar, describir y parar **human loops**, más acciones de Amazon Cognito para crear el user pool, el grupo y los usuarios del work team.

Y la salida lo confirma: los datos devueltos por un job humano traen el **ARN de la flow definition** que se usó para crear el human loop, un `humanLoopName` que es un hash hexadecimal de 40 caracteres generado por el sistema, y las respuestas de los evaluadores anidadas en una estructura de resultados por métrica.

> **Dato decisivo de arquitectura**: las evaluaciones humanas de Bedrock **son un workflow de revisión humana de SageMaker por debajo**. Esto importa para dos cosas: los workforces y work teams creados en Cognito, en Ground Truth o en Augmented AI **aparecen disponibles** al crear un job de evaluación, y el vocabulario de flow definition y human loop es el que hay que reconocer en los logs y en la salida.

### Instrucciones para los evaluadores: dos sitios, dos propósitos

La página insiste en que la calidad de la anotación depende de las instrucciones, y distingue dos lugares:

| Dónde | Qué va ahí |
| --- | --- |
| **Descripción de cada métrica y su método de rating** | Explicación sucinta de la métrica, ampliando qué significa y cómo debe valorarse con ese método de rating concreto |
| **Instrucciones generales de evaluación** | Dirección de alto nivel del job, y descripción de las respuestas de ground truth si el dataset las incluye. Se muestran en la misma página donde el worker completa la tarea |

El dataset de un job humano tiene su propio formato, distinto del de los jobs automáticos, documentado en [Create a custom prompt dataset for a model evaluation job that uses human workers](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-prompt-datasets-custom-human.html).

### Workflows de anotación a escala

Cuando el volumen supera lo que un work team de 50 personas absorbe, el servicio documentado es [SageMaker Ground Truth](https://docs.aws.amazon.com/sagemaker/latest/dg/data-label.html), con su [gestión de workforces](https://docs.aws.amazon.com/sagemaker/latest/dg/sms-workforce-management.html) y sus funcionalidades avanzadas de workforce que la propia página de Bedrock reconoce como superiores a las suyas.

### El hueco: las *feedback interfaces*

> **Discrepancia**: el skill nombra *feedback interfaces* y *rating systems for model outputs* como si fueran funcionalidades. **No hay ninguna página de AWS que documente una interfaz de feedback de usuario final para una aplicación GenAI.** Lo que AWS documenta es el **portal del worker** de las evaluaciones humanas, que es una interfaz para evaluadores internos, no para usuarios de la aplicación.

La respuesta que sí tiene respaldo oficial está en [GENOPS01-BP02](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops01-bp02.html): complementar la evaluación de modelo con feedback directo de los usuarios, mediante bucles de feedback continuos que se recogen, se analizan y se actúan de forma sistemática, con el objetivo declarado de **hacer visible la degradación de rendimiento del FM en el momento en que ocurre**. El *cómo* se construye la interfaz queda en manos del desarrollador; lo que el Lens fija es la obligación de cerrar el bucle.

> Para el otro lado del mismo problema, generar interacciones de usuario en lugar de recogerlas, AWS sí documenta una simulación de usuario con actor LLM en AgentCore Evaluations. Se desarrolla en el segundo archivo de este task.

---

## Skill 5.1.5 — Evaluación multiperspectiva: RAG, juez y humanos

> *Desarrollar sistemas de evaluación completos que garanticen una valoración exhaustiva de las salidas del FM desde múltiples perspectivas (por ejemplo, usando evaluación de RAG, valoración automatizada de calidad con técnicas de LLM-as-a-Judge, interfaces de recogida de feedback humano).*

### Las tres perspectivas, y qué aporta cada una

| Perspectiva | Mecanismo | Lo que ve que las otras no ven |
| --- | --- | --- |
| **Algorítmica** | Métricas computadas del job automático | Robustez ante perturbaciones, y comparación reproducible contra una referencia |
| **Juez LLM** | Métricas `Builtin.*` con explicación | Cualidades que no se pueden reducir a una fórmula: coherencia, utilidad, estilo |
| **Humana** | Work team con métodos de rating | Preferencia real, y criterio de dominio que ningún modelo tiene |

### Los dos tipos de job de RAG

De [Evaluate the performance of RAG sources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html). La distinción decide qué métricas están disponibles.

| Tipo | Qué entra en el informe | Páginas de creación |
| --- | --- | --- |
| **Retrieve only** | Solo los datos **recuperados** de la fuente RAG | [con métricas integradas](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-create-ro.html) · [con métricas propias](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-create-ro-custom.html) |
| **Retrieve and generate** | Lo recuperado **y** los resúmenes que genera el modelo de respuesta | [con métricas integradas](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-create-randg.html) · [con métricas propias](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-create-randg-custom.html) |

En ambos se puede evaluar una knowledge base de Bedrock **o traer los datos de inferencia de una fuente RAG externa**, igual que con los modelos.

### Las métricas de RAG, y las dos que no están en ningún otro catálogo

De [Use metrics to understand RAG system performance](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-metrics.html).

**Retrieve only**, solo dos métricas:

| Métrica | Identificador | Detalle |
| --- | --- | --- |
| Context relevance | `Builtin.ContextRelevance` | Relevancia contextual de los textos recuperados respecto a las preguntas |
| Context coverage | `Builtin.ContextCoverage` | Cuánto cubren los textos recuperados la información del ground truth. **Exige aportar ground truth en el dataset** |

**Retrieve and generate**, diez métricas:

| Métrica | Identificador | Detalle |
| --- | --- | --- |
| Correctness | `Builtin.Correctness` | Exactitud de las respuestas al contestar las preguntas |
| Completeness | `Builtin.Completeness` | Si las respuestas resuelven todos los aspectos de las preguntas |
| Helpfulness | `Builtin.Helpfulness` | Utilidad global de las respuestas |
| Logical coherence | **`Builtin.LogicalCoherence`** | Ausencia de huecos lógicos, inconsistencias o contradicciones |
| Faithfulness | `Builtin.Faithfulness` | **Cuánto evitan las respuestas la hallucination respecto a los textos recuperados** |
| Citation precision | `Builtin.CitationPrecision` | Cuántos de los pasajes citados estaban correctamente citados |
| Citation coverage | `Builtin.CitationCoverage` | Si la respuesta está respaldada por los pasajes citados, y si faltan citas |
| Harmfulness | `Builtin.Harmfulness` | Contenido dañino: odio, insultos, violencia, contenido sexual |
| Stereotyping | `Builtin.Stereotyping` | Afirmaciones generalizadas sobre personas o grupos |
| Refusal | `Builtin.Refusal` | Cuán evasivas son las respuestas |

Tres cosas que conviene fijar de esta tabla:

1. **`Builtin.CitationPrecision` y `Builtin.CitationCoverage` solo existen aquí.** No están en el catálogo de model evaluation. Son la forma oficial de medir la atribución de fuente que el [Domain 3 · Skill 3.4.1](../domain-3/task-3-4-ia-responsable.md#skill-341--transparencia-y-reasoning-traces) trata como mecanismo de transparencia.
2. **`Builtin.Faithfulness` cambia de referente.** En model evaluation mide fidelidad **al prompt**; en RAG mide ausencia de hallucination **respecto a los textos recuperados**. Mismo identificador, contexto distinto.
3. **`Builtin.LogicalCoherence` aquí, `Builtin.Coherence` en model evaluation.** El mismo concepto con dos identificadores según la familia de job.

> **Dato decisivo para diseñar la evaluación de un RAG**: la separación retrieve-only / retrieve-and-generate permite **aislar la causa de un fallo**. Si context relevance sale bien y correctness sale mal, el problema está en la generación. Si context relevance sale mal, no hay nada que arreglar en el prompt del generador. Ejecutar los dos tipos de job sobre el mismo dataset es el diagnóstico más limpio que ofrece la plataforma.

### Métricas propias: el contrato del prompt

De [Create a prompt for a custom metric](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-evaluation-custom-metrics-prompt-formats.html). Se pueden definir **hasta 10 métricas propias por job de evaluación**, y cada una necesita un prompt de instrucciones para el juez más el modelo evaluador.

El prompt tiene cuatro bloques, y **el orden es parte del contrato**:

| Orden | Bloque | Obligatorio | Contenido |
| --- | --- | --- | --- |
| 1 | **Role definition** | No | Identidad o rol que adopta el modelo evaluador, para enmarcar la evaluación |
| 2 | **Task description** | **Sí** | Instrucciones detalladas de la tarea de evaluación. AWS recomienda **un mínimo de 15 palabras** y ser específico sobre en qué fijarse |
| 3 | **Criterion and rubric** | No | Rúbricas de evaluación y guías de puntuación detalladas |
| 4 | **Input variables** | **Sí** | Las variables que el juez necesita: prompt, respuesta, y las que exija el tipo de job |

> **Dato decisivo**: las **input variables tienen que ir al final, sin excepción**. La documentación lo dice explícitamente: si se ponen instrucciones adicionales *después* de las variables de entrada, **el modelo evaluador puede no evaluar la métrica correctamente**. Es el error de construcción más fácil de cometer y el más difícil de diagnosticar, porque el job termina correctamente y los scores simplemente no significan nada.

El segundo contrato es la **coherencia entre la rúbrica y el output schema**. Si las guías de puntuación del prompt hablan de *Poor*, *Acceptable* y *Good*, el output schema (la escala de rating) tiene que declarar exactamente esas tres definiciones. Un desajuste entre la escala del prompt y la escala declarada produce scores inconsistentes.

Las definiciones de las métricas propias quedan guardadas como ficheros JSON en el bucket de salida, bajo un prefijo `custom_metrics` dentro de la carpeta del job, según [Review RAG evaluation job reports and metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-report.html). Para model evaluation el mecanismo equivalente está en [Create a prompt for a custom metric](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-custom-metrics-prompt-formats.html) y [Create a model evaluation job using custom metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-custom-metrics-create-job.html).

> **Gotcha de auditoría**: que la definición de la métrica propia se persista en S3 junto a los resultados es lo que hace **reproducible** una evaluación con métricas propias. Sin ese fichero, un score de una métrica inventada no es verificable seis meses después. Es el mismo argumento de versionado que el [Domain 1 · Skill 1.6.4](../domain-1/task-1-6-prompt-engineering-governance.md#skill-164--aseguramiento-de-calidad-de-prompts) aplica a los prompts de producción.

### Cómo se leen los resultados

La consola presenta, para los jobs de juez, un **histograma del número de veces que una respuesta recibió cada score**, más las explicaciones del juez para los **primeros cinco prompts** del dataset. El informe completo está en S3. Los resultados detallados de RAG se consultan según [Review metrics for RAG evaluations that use LLMs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-eval-llm-results.html), y los de los jobs humanos según [Review the results of a human-based model evaluation job](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation-report-human-customer.html).

> **Dato decisivo**: la consola solo explica **cinco** prompts. Cualquier análisis de por qué el juez puntuó como puntuó, más allá de una inspección superficial, **obliga a bajar el informe de S3**. El histograma sirve para ver la forma de la distribución; las explicaciones útiles están en el fichero.

La relación con el Domain 3 es directa: las mismas familias de evaluación se usan allí como palanca de fairness, con `Builtin.Stereotyping` y `Builtin.Harmfulness` como métricas de sesgo. El desarrollo está en [Domain 3 · Skill 3.4.2](../domain-3/task-3-4-ia-responsable.md#skill-342--evaluaciones-de-fairness).

---

## Resumen operativo: qué se mide y quién puntúa

| Si la pregunta menciona… | La respuesta apunta a |
| --- | --- |
| Métrica de *fluency* | No existe en AWS. Lo más cercano es `Builtin.ProfessionalStyleAndTone`, más *Readability* en las plantillas del juez |
| Exactitud factual sin juez | **RWK score** del task type de general text generation |
| Consistencia interna de una respuesta | `Builtin.Coherence` en model evaluation, `Builtin.LogicalCoherence` en RAG |
| Consistencia ante entradas equivalentes | **Robustness semántica**: 5 perturbaciones, ~5 veces por prompt |
| Score bajo es bueno | Robustness y toxicity. En accuracy es al revés |
| Evaluar un modelo que no está en Bedrock | Fuente de inferencia **precomputada** en el prompt dataset |
| Evaluar una política de routing | El **prompt router** se admite como modelo generador |
| Repartir usuarios entre dos modelos | **A/B testing** con production variants de SageMaker AI |
| Duplicar tráfico real sin afectar al usuario | **Shadow testing** |
| Desplazar tráfico progresivamente con rollback | **Canary** de blue/green deployment guardrails |
| CORS en el bucket de salida | Obligatorio **solo** en jobs con human workers |
| Comparar más de dos modelos con humanos | No se puede: el job humano compara **2 como máximo** |
| Más de 50 evaluadores humanos | Gestionar el workforce desde Cognito o Ground Truth, no desde Bedrock |
| Medir hallucination en un RAG | `Builtin.Faithfulness` del job retrieve-and-generate |
| Medir si las citas son correctas | `Builtin.CitationPrecision` y `Builtin.CitationCoverage`, exclusivas de RAG |
| Métrica que exige ground truth | `Builtin.ContextCoverage` |
| Aislar si el fallo es de retrieval o de generación | Ejecutar **retrieve-only y retrieve-and-generate** sobre el mismo dataset |
| Orden de los bloques de un prompt de métrica propia | Role, task, rúbrica, **input variables al final** |
| Número máximo de métricas propias | **10 por job** |
| Latencia o coste dentro del informe de evaluación | No están. Salen de las métricas de runtime y del Domain 4 |
