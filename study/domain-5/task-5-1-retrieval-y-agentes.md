# Task 5.1 — Calidad de retrieval, agentes, QA y validación de despliegue

[← Volver al índice](./README.md)

Skills cubiertos: **5.1.4**, **5.1.6**, **5.1.7**, **5.1.8**, **5.1.9**.

El Task 5.1 tiene nueve skills y se reparte en dos archivos. Este cubre el eje de **sobre qué se aplica la evaluación y cómo se opera**: calidad de lo recuperado, rendimiento de agentes, aseguramiento continuo con quality gates, comunicación a stakeholders y validación de despliegue. El eje de **qué se mide y quién puntúa** (skills 5.1.1, 5.1.2, 5.1.3 y 5.1.5) está en [task-5-1-frameworks-y-herramientas.md](./task-5-1-frameworks-y-herramientas.md).

El marco oficial de este bloque es **AGENTOPS06** del [Agentic AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html), la pregunta [*¿cómo se implementan frameworks de testing, evaluación y validación?*](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops06.html). Es el único marco de AWS que trata el testing de sistemas GenAI como disciplina propia, y su enunciado resume el problema del dominio: **sin un framework que cubra todas las etapas del ciclo de vida, las regresiones de calidad por cambios de prompt, de herramientas o de modelo llegan al usuario antes de que alguien se dé cuenta.**

Las cinco intenciones de capacidad de AGENTOPS06, y el skill donde aterriza cada una:

| Intención declarada | Skill |
| --- | --- |
| Validar en todas las capas, desde componentes aislados hasta workflows en modo *production-shadow*, antes de que el cambio llegue al usuario | 5.1.4, 5.1.9 |
| Medir calidad, seguridad, eficiencia y alineación con el negocio de forma continua contra benchmarks versionados, con las regresiones visibles en cuanto aparecen | 5.1.4, 5.1.7 |
| Governance de cambio **proporcional al riesgo**: lo de bajo riesgo pasa por gates automáticos, lo de alto riesgo lo revisan expertos de dominio y responsables de negocio | 5.1.4 |
| Datasets de evaluación, prompts y rúbricas versionados y actualizados a medida que evolucionan las capacidades | 5.1.4 |
| Rutas de rollback definidas, ensayadas y conectadas a la misma telemetría que detecta las violaciones de umbral de calidad | 5.1.9 |

Sus tres best practices: [BP01 multi-layered testing frameworks](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops06-bp01.html), [BP02 evaluate and track ongoing agent performance](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops06-bp02.html) y [BP03 SME-driven validation and business approval workflows](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops06-bp03.html).

---

## Skill 5.1.4 — Aseguramiento de calidad continuo y quality gates

> *Crear procesos sistemáticos de aseguramiento de calidad para mantener estándares de rendimiento consistentes en los FMs (por ejemplo, usando workflows de evaluación continua, testing de regresión de las salidas del modelo, quality gates automatizados para los despliegues).*

### La pirámide de cuatro capas

De [AGENTOPS06-BP01](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops06-bp01.html). El testing tradicional, con aserciones de coincidencia exacta y tests que salen en verde o en rojo, **se le escapan modos de fallo importantes** en sistemas agentic. La pirámide que AWS propone tiene cuatro niveles:

| Capa | Qué cubre |
| --- | --- |
| **Unit** | Componentes aislados: razonamiento, herramientas, memoria |
| **Integration** | Fallos que solo emergen cuando los componentes interactúan con herramientas y servicios reales |
| **End-to-end** | El workflow completo |
| **Shadow** | El sistema corriendo **en producción**, contra datos y patrones de tráfico reales, sin impacto en el usuario |

> **Dato decisivo**: el resultado deseado que AWS declara es que los tests usen **valoración semántica de calidad en lugar de comparación exacta**, precisamente para que las salidas no deterministas no rompan la suite. Tratar el testing de un agente como testing de software tradicional, con coincidencia literal de cadenas en vez de equivalencia semántica, aparece explícitamente en la lista de anti-patrones.

Los otros anti-patrones que la página nombra: probar solo el camino feliz sin casos límite ni entradas adversariales; confiar solo en unit tests; correr los tests solo en entornos aislados sin shadow testing en producción; y **no mantener los datasets de test a medida que las capacidades evolucionan**, con lo que los tests se quedan obsoletos y pierden su valor de detección de regresión.

### Los cinco niveles de madurez, y dónde está la frontera

AGENTOPS06 publica una escala de madurez de cinco niveles. Tres cortes concretos que conviene retener:

| Nivel | La señal que lo define |
| --- | --- |
| **2 Emerging** | La evaluación ocurre **en hitos**, con criterios de aceptación documentados. Los workflows de aprobación distinguen al menos **dos niveles de riesgo** |
| **3 Defined** | La pirámide de cuatro capas es estándar, y los **evaluadores integrados de AgentCore Evaluations actúan como quality gates estandarizados**. El rollback está automatizado mediante triggers de pipeline y se ensaya con regularidad |
| **4 Proactive** | La **evaluación online muestrea interacciones en vivo de forma continua**, con umbrales que disparan rollback automático a través de alarmas de despliegue |

> **Dato decisivo para el examen**: el salto del nivel 3 al 4 no es "más tests", es **pasar de evaluar en hitos a evaluar en producción de forma continua**, con el umbral conectado al rollback. Esa es exactamente la diferencia entre una evaluación batch y una evaluación online en AgentCore, detallada en el [Skill 5.1.7](#skill-517--frameworks-de-rendimiento-de-agentes).

Los problemas comunes que la página lista son, en la práctica, el temario del skill: quedarse en unit tests deterministas sin shadow testing; **medir calidad una vez en el release y nunca más**, con lo que el data drift, la decadencia del prompt y las actualizaciones del modelo upstream erosionan la calidad en silencio; que todos los cambios pasen por el mismo comité, que o bien cuella de botella lo menor o bien aprueba sin criterio los aumentos de autonomía; **datasets creados una vez y nunca refrescados**, con lo que los scores siguen verdes mientras los fallos reales pasan desapercibidos; y procedimientos de rollback que viven en un runbook pero nunca se ensayan, así que el primer intento real descubre artefactos roto, permisos que faltan o versiones de prompt y herramienta descuadradas.

### Testing de regresión: qué lo hace posible

De [Ground truth evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/ground-truth-evaluations.html), la frase que enmarca el skill: el ground truth **convierte una valoración subjetiva de calidad en una medición objetiva**, y eso es lo que habilita la detección de regresión, los datasets de benchmark y la corrección de dominio que los evaluadores genéricos no pueden dar por sí solos.

El mecanismo concreto de regresión es la **batch evaluation** de AgentCore, descrita en [Evaluation types](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations-types.html). Corre evaluadores contra múltiples sesiones en un único job asíncrono, y el servicio se ocupa del descubrimiento de sesiones, la recolección de spans y el scoring. Sus cuatro casos de uso declarados son literalmente el skill:

1. **Medición de baseline** antes de hacer un cambio.
2. **Comparación antes/después** de aplicar una actualización de prompt o de modelo.
3. **Testing de regresión** sobre conjuntos curados de sesiones.
4. **Auditorías periódicas de calidad** sobre tráfico de producción de una ventana temporal concreta.

> **Dato decisivo de arquitectura**: la batch evaluation **no recibe los spans**. Recibe la ubicación en CloudWatch Logs donde están las sesiones del agente, y el servicio las descubre. Frente a la evaluación on-demand, donde hay que recolectar los spans y llamar a la API de evaluación por sesión, aquí el trabajo pesado es del lado del servicio. La guía de arranque está en [Getting started with batch evaluation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/batch-evaluations-getting-started.html).

### La cadena real de un quality gate automatizado

Ninguna página de AWS se titula "quality gate". La cadena se arma con cuatro piezas documentadas por separado:

| Pieza | Servicio | Qué aporta al gate |
| --- | --- | --- |
| **Producir el veredicto** | Job de evaluación de Bedrock, o batch evaluation de AgentCore | El score contra el que se decide |
| **Convertir tests en artefacto de pipeline** | [Report groups de CodeBuild](https://docs.aws.amazon.com/codebuild/latest/userguide/test-report-group.html) | Los casos de test se declaran en el buildspec y cada ejecución genera un test report. **Hasta cinco report groups por proyecto de build** |
| **Bloquear el despliegue** | Alarma de CloudWatch conectada al despliegue | El umbral que para el avance |
| **Deshacer** | [Blue/green con canary](https://docs.aws.amazon.com/sagemaker/latest/dg/deployment-guardrails-blue-green-canary.html) de SageMaker AI | Desplazamiento progresivo y rollback automático |

> **Gotcha de los report groups**: un report group se puede usar en **más de un proyecto de build**, y todos los reports creados con él comparten configuración, permisos y opción de exportación, **aunque los casos de test sean distintos en cada proyecto**. Los casos se definen en el buildspec de cada proyecto, no en el report group.

### Reproducibilidad: el requisito que casi nadie implementa

De [RAIER01-BP03](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/raier01-bp03.html), con **nivel de riesgo alto** si no se establece. Por cada actualización del sistema hay que reejecutar la evaluación y actualizar el registro del sistema. Y el criterio de suficiencia es explícito: los logs de evaluación deben registrar condiciones de test, configuración del sistema, datos de entrada, resultados en bruto y notas metodológicas **con detalle suficiente para que otra persona reproduzca la evaluación exacta meses después**.

Las tres acciones que pide: loguear qué datasets se usaron, qué versión del sistema se probó, en qué configuración de hardware y software, y las salidas en bruto e intermedias; poner los materiales de evaluación bajo control de versiones (scripts de test, ficheros de configuración, salidas); y **enlazar los materiales de evaluación al registro del sistema y al del dataset**, de modo que quede claro qué par de versión de datos y versión de sistema produjo cada resultado.

---

## Skill 5.1.6 — Testing de calidad del retrieval

> *Implementar testing de calidad del retrieval para evaluar y optimizar los componentes de recuperación de información que augmentan al FM (por ejemplo, usando scoring de relevancia, verificación de coincidencia de contexto, mediciones de latencia de recuperación).*

### Las dos métricas que aíslan el retrieval

El job de RAG evaluation de tipo **retrieve only** es la herramienta oficial para este skill, porque evalúa el informe **basándose solo en los datos recuperados**, sin que la generación contamine el resultado. Sus dos métricas están detalladas en el [Skill 5.1.5](./task-5-1-frameworks-y-herramientas.md#skill-515--evaluación-multiperspectiva-rag-juez-y-humanos):

| Lo que pide el skill | La métrica que lo implementa |
| --- | --- |
| **Relevance scoring** | `Builtin.ContextRelevance`, relevancia contextual de los chunks recuperados respecto a las preguntas |
| **Context matching verification** | `Builtin.ContextCoverage`, cuánto cubren los chunks recuperados la información del ground truth. **Exige ground truth** |
| **Retrieval latency measurements** | Ninguna. Ver más abajo |

### Cómo se lee el informe, y el error de signo

De [Review metrics for RAG evaluations that use LLMs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-eval-llm-results.html). Tres hechos sobre el scoring:

- El score de cada métrica es **un valor entre 0 y 1**.
- Es una **media** sobre los textos recuperados o las respuestas generadas de todas las consultas del dataset.
- **Cuanto más cerca de 1, más presente está la característica que la métrica mide** en lo recuperado o generado.

> **Dato decisivo, y la trampa más clara de este skill**: "más cerca de 1" significa "más de esa característica", **no "mejor"**. El propio ejemplo de la documentación lo deja ver: una knowledge base con *Completeness* en 0,82 y **Stereotyping en 0,94**. El 0,94 no es una buena nota: significa que las respuestas contienen una alta cantidad de afirmaciones generalizadas sobre personas o grupos. En `Builtin.Stereotyping`, `Builtin.Harmfulness` y `Builtin.Refusal` **el score bajo es el bueno**; en el resto, el alto.

Cada métrica trae además un **histograma** que cuenta cuántos textos o respuestas caen en cada rango de score. Eso importa porque una media de 0,7 puede venir de una distribución concentrada o de dos grupos en los extremos, y el remedio es distinto en cada caso. Y un requisito operativo: **el informe solo se abre si el estado de la evaluación es *ready* o *available***.

### La latencia de retrieval no sale del job de evaluación

> **Discrepancia**: el skill pide *retrieval latency measurements*, y **el job de RAG evaluation no mide tiempo**. Sus métricas son todas de calidad semántica. La latencia de recuperación hay que medirla en el vector store, no en la evaluación.

Las tres fuentes reales, según el vector store:

| Vector store | De dónde sale la latencia |
| --- | --- |
| **OpenSearch Service** | [Métricas de CloudWatch del dominio](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/managedomains-cloudwatchmetrics.html), desarrolladas en [Domain 4 · Skill 4.3.5](../domain-4/task-4-3-herramientas-vector-stores-y-fallos.md#skill-435--gestión-operativa-del-vector-store) |
| **Knowledge base de Bedrock** | Latencia de la llamada de recuperación, instrumentada en la aplicación. Ver [Domain 4 · Skill 4.2.2](../domain-4/task-4-2-retrieval-y-parametros.md#skill-422--rendimiento-del-retrieval) |
| **Canary de extremo a extremo** | Duración de un canary de Synthetics que ejecuta la consulta real, tratada en el [Skill 5.1.9](#skill-519--validación-de-despliegue) |

### La palanca de k que afecta a la medición

De [k-Nearest Neighbor (k-NN) search](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html). Dos límites del plugin que condicionan cualquier medición de calidad de retrieval:

- Un campo `knn_vector` admite **hasta 10.000 floats**, con el número exacto fijado por el parámetro `dimension` obligatorio.
- El valor máximo de `k` es **10.000**.

> **Gotcha que invalida una medición**: en una consulta `knn`, `k` es el número de vecinos que se quieren, **pero hay que fijar también `size`**. Si no, se obtienen `k` resultados **por shard y por segmento**, no `k` para la consulta completa. Medir precisión de retrieval sin fijar `size` mide otra cosa: un conjunto inflado y no determinista respecto al número de shards. Y si la consulta `knn` se mezcla con otras cláusulas, se pueden recibir menos resultados de los pedidos.

El otro caso donde el número de resultados no coincide con lo pedido es el **chunking jerárquico**: como los child chunks recuperados se sustituyen por sus parent chunks, **el número de resultados devuelto puede ser menor que el solicitado**. Está en [How content chunking works](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html) y se desarrolla en el [Task 5.2 · Skill 5.2.4](./task-5-2-monitoreo-troubleshooting-optimizacion.md#skill-524--troubleshooting-del-sistema-de-retrieval).

---

## Skill 5.1.7 — Frameworks de rendimiento de agentes

> *Desarrollar frameworks de rendimiento de agentes para asegurar que los agentes ejecutan las tareas de forma correcta y eficiente (por ejemplo, usando mediciones de tasa de finalización de tareas, evaluaciones de efectividad del uso de herramientas, evaluaciones de agentes de Amazon Bedrock, valoración de la calidad del razonamiento en workflows multi-paso).*

### Dónde vive de verdad la evaluación de agentes

> **Aclaración importante**: la página [Evaluate the performance of Amazon Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) **solo cubre evaluaciones de modelo y de RAG**. No hay evaluación de agentes ahí. La evaluación de agentes es un servicio distinto con su propio doc set: [**Amazon Bedrock AgentCore Evaluations**](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html). Si una pregunta habla de evaluar agentes y ofrece "Bedrock model evaluation" como opción, la opción es incorrecta.

AgentCore Evaluations mide, según [How it works](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/how-it-works-evaluations.html), exactamente las tres cosas que el skill pide: **la corrección de la finalización de tarea de extremo a extremo (goal attainment)**, **la exactitud de la herramienta que el agente invocó** al atender la petición, y cualquier métrica propia sobre dimensiones específicas del comportamiento. Y evalúa tanto agentes alojados en AgentCore Runtime **como agentes alojados fuera de AgentCore**.

Se integra con frameworks de agentes como **Strands** y **LangGraph**, mediante instrumentación de **OpenTelemetry** y **OpenInference**. Por debajo, los traces se convierten a un formato unificado y se puntúan con técnicas de LLM-as-a-Judge.

### Los tres niveles de evaluación, que determinan qué se puede medir

De [Create evaluator](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/create-evaluator.html), un evaluador se declara en uno de tres niveles, y **el nivel fija qué información ve el juez**:

| Nivel | Alcance | Placeholders disponibles |
| --- | --- | --- |
| `SESSION` | Agrupación lógica de interacciones de un usuario o workflow, con uno o varios traces | `context` (prompts, respuestas y tool calls de todos los turnos), `available_tools` |
| `TRACE` | Registro completo de **una** ejecución o petición | `context` (turnos previos más el actual), `assistant_turn` |
| `TOOL_CALL` | Una invocación concreta de herramienta | `available_tools`, `context`, `tool_turn`, más los placeholders de skill |

> **Dato decisivo**: la **tasa de finalización de tarea es necesariamente de nivel sesión**, porque una tarea atraviesa varios turnos. La **efectividad de uso de herramienta es de nivel tool call**. Pedir una métrica de finalización de tarea a un evaluador de nivel trace no funciona: el evaluador no ve la sesión completa.

### Los evaluadores integrados con ground truth

De [Ground truth evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/ground-truth-evaluations.html). Cinco evaluadores admiten referencia:

| Evaluador | Nivel | Campo de ground truth | Cómo puntúa |
| --- | --- | --- | --- |
| `Builtin.Correctness` | Trace | `expectedResponse` | LLM-as-a-Judge |
| `Builtin.GoalSuccessRate` | Session | `assertions` | LLM-as-a-Judge: valida si el comportamiento satisface afirmaciones en lenguaje natural a lo largo de toda la sesión |
| `Builtin.TrajectoryExactOrderMatch` | Session | `expectedTrajectory` | **Programático, sin llamadas a LLM.** Mismas herramientas, mismo orden, sin extras |
| `Builtin.TrajectoryInOrderMatch` | Session | `expectedTrajectory` | **Programático.** Todas las esperadas en orden, pero admite herramientas extra entre ellas |
| `Builtin.TrajectoryAnyOrderMatch` | Session | `expectedTrajectory` | **Programático.** Todas las esperadas presentes, en cualquier orden, con extras permitidos |

> **Dato decisivo de coste y determinismo**: los **tres evaluadores de trayectoria puntúan de forma programática, sin invocar ningún LLM**. Son deterministas y no consumen tokens de juez. Cuando la pregunta es "¿llamó el agente a las herramientas correctas en el orden correcto?", la respuesta no necesita un juez, y AWS lo implementa así. `Builtin.Correctness` y `Builtin.GoalSuccessRate`, en cambio, sí usan juez.

Los tres campos de ground truth y su alcance:

| Campo | Tipo | Alcance | Contenido |
| --- | --- | --- | --- |
| `expectedResponse` | Cadena | Trace | Respuesta esperada de un turno concreto, asociada a un trace mediante su `traceId` |
| `assertions` | Lista de cadenas | Session | Afirmaciones en lenguaje natural que deberían ser ciertas sobre el comportamiento del agente |
| `expectedTrajectory` | Lista de nombres de herramienta | Session | Secuencia esperada de llamadas a herramienta. Hasta **1.000** nombres, de hasta 500 caracteres cada uno, según [`EvaluationExpectedTrajectory`](https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_EvaluationExpectedTrajectory.html) |

Tres comportamientos que conviene tener claros:

- Los campos de ground truth son **opcionales**. Si se omiten, los evaluadores caen a su modo sin referencia: `Builtin.Correctness` sigue funcionando, evaluando solo a partir del contexto.
- Se pueden aportar **todos los campos en una sola petición**. El servicio elige los relevantes para cada evaluador y devuelve en la respuesta qué campos ignoró.
- **No hace falta `expectedResponse` para cada trace.** Los traces sin referencia se evalúan con la variante sin ground truth del evaluador.

### Los dos evaluadores de skills

De [Skill evaluators](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/skill-evaluators.html). Ambos son de nivel tool call, y **emiten un resultado por invocación de skill**, anclado al span de la llamada que cargó el skill: una sesión con tres invocaciones produce tres resultados por evaluador.

| Evaluador | Qué juzga | Escala |
| --- | --- | --- |
| `Builtin.SkillSelectionAccuracy` | Si el skill que el agente cargó encaja con la tarea, dado el catálogo disponible | `Yes` (1,0) o `No` (0,0) |
| `Builtin.SkillInstructionFollowing` | Cuán completamente siguió el agente los pasos prescritos por el skill cargado | `Fully Followed` (1,0), `Mostly Followed` (0,75), `Partially Followed` (0,5), `Minimally Followed` (0,25), `Not Followed` (0,0) |

> **Dato decisivo sobre el contexto**: `Builtin.SkillInstructionFollowing` recibe **el contexto de sesión completo**, todos los turnos desde el inicio hasta el final, no el snapshot previo a la llamada. La razón está documentada: el agente puede ejecutar los pasos prescritos **en cualquier momento después de cargar el skill**, así que el juez necesita la sesión entera. Es el único caso en el que el placeholder de contexto de un evaluador de nivel tool call cambia de significado, y también aplica a los evaluadores propios que referencien el cuerpo del skill.

`Builtin.SkillSelectionAccuracy` corre siempre que se detecta una invocación de skill; `Builtin.SkillInstructionFollowing` **solo si el trace trae además el cuerpo del fichero de instrucciones**. Si no hay ninguna de las dos señales, ambos evaluadores se omiten y no emiten resultado: con un agente que no carga skills, cero resultados es el comportamiento esperado, no un error.

El catálogo de skills disponibles **no lo emiten todos los frameworks**. Cuando no está en el trace, el placeholder correspondiente queda vacío y `Builtin.SkillSelectionAccuracy` juzga el skill invocado solo contra la petición del usuario y el contexto de la conversación.

### Los tres tipos de evaluación, y cuándo usar cada uno

De [Evaluation types](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations-types.html):

| Tipo | Cuándo se ejecuta | Para qué sirve |
| --- | --- | --- |
| [**Online**](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/online-evaluations.html) | Continuamente, sobre **tráfico de producción en vivo** | Monitorización persistente de calidad. Muestreo por porcentaje de sesiones o filtros condicionales |
| [**On-demand**](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-on-demand.html) | Cuando se pide, sobre spans o traces indicados por ID | Probar un evaluador propio, investigar una interacción concreta, validar una corrección, testing en build time |
| **Batch** | Job asíncrono sobre múltiples sesiones | Baseline, comparación antes/después, regresión, auditorías periódicas |

> **Gotcha que limita la evaluación online**: los **evaluadores propios que usan placeholders de ground truth** (afirmaciones, respuesta esperada, trayectoria esperada) **no se pueden usar en configuraciones de evaluación online**. Tiene sentido: el tráfico en vivo no trae respuestas esperadas. El ground truth es para on-demand y batch.

### Tipos de evaluador, más allá de los integrados

De [Evaluators](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluators.html), hay cuatro familias, y dos son menos conocidas:

| Familia | Detalle |
| --- | --- |
| **Integrados** | Preconfigurados, con plantilla de prompt, modelo evaluador y criterios estandarizados. **Su configuración no se puede modificar**, para preservar consistencia |
| **De terceros** | Provienen de las librerías open source **DeepEval** y **AutoEval**. Se seleccionan por ID y el servicio los ejecuta, sin aportar modelo ni configuración |
| **Propios** | LLM-as-a-judge con instrucciones y escala propias, **o code-based**: una función Lambda con lógica programática, que permite chequeos deterministas, llamadas a APIs externas, coincidencia por expresión regular o reglas de negocio **sin depender de un juez LLM** |
| **Derivados de uno base** | Ejecutan la lógica de un evaluador integrado o de terceros **sobre un modelo propio**, en vez del que elige el servicio |

Los ARN revelan la naturaleza de cada uno:

| Tipo | Forma del ARN |
| --- | --- |
| Integrado | `arn:aws:bedrock-agentcore:::evaluator/Builtin.Nombre` |
| Propio | `arn:aws:bedrock-agentcore:region:cuenta:evaluator/mi-evaluador` |

> **Dato decisivo**: el ARN de un evaluador integrado **no lleva Región ni cuenta**. Es un recurso público accesible a todos. Los recursos de evaluación propios son privados y requieren concesión explícita, con políticas basadas en recurso para evaluadores y configuraciones, y políticas basadas en identidad para usuarios y roles.

Cuotas por defecto: **1.000 configuraciones de evaluación por Región y cuenta**, y hasta **1 millón de tokens de entrada y salida por minuto y cuenta** en las Regiones grandes.

### Requisitos que hacen fallar la primera ejecución

De los prerrequisitos de las páginas de ground truth y de batch:

- Un agente construido con un framework y una librería de instrumentación soportados. El agente de instrumentación soportado es **ADOT (AWS Distro for OpenTelemetry)**.
- El agente desplegado en AgentCore Runtime con observabilidad activada, **incluido Transaction Search**.
- Credenciales con permisos para `bedrock-agentcore`, `bedrock-agentcore-control` y `logs` de CloudWatch.

> **Gotcha de temporización**: después de invocar el agente hay que **esperar entre 2 y 5 minutos** a que CloudWatch ingeste la telemetría antes de lanzar la evaluación. Es la causa número uno de una evaluación que devuelve cero resultados sobre una sesión que sí existió.

### Calidad del razonamiento en workflows multi-paso

El skill pide valorar la calidad del razonamiento. Hay dos capas complementarias:

| Capa | Mecanismo |
| --- | --- |
| **Ver el razonamiento** | El trace del agente de Bedrock, con sus siete tipos y el campo de rationale, desarrollado en [Domain 3 · Skill 3.4.1](../domain-3/task-3-4-ia-responsable.md#skill-341--transparencia-y-reasoning-traces) |
| **Puntuar el razonamiento** | Evaluadores de AgentCore sobre los spans de ese razonamiento: trayectoria para la secuencia de decisiones, `Builtin.GoalSuccessRate` para el resultado |

Las métricas operativas del agente, la otra mitad de "correcta y eficientemente", están en [Observability runtime metrics](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-runtime-metrics.html):

| Métrica | Qué cuenta |
| --- | --- |
| `Invocations` | Peticiones a la API del plano de datos. Cada llamada cuenta una, **independientemente del tamaño del payload o del estado de la respuesta** |
| `SessionCount` | Sesiones **nuevas** creadas en el periodo. Contador acumulativo: cada sesión se cuenta una vez al crearse, y las invocaciones posteriores a la misma sesión no lo incrementan |
| `ActiveSessionCount` | **Gauge en tiempo real** de sesiones activas ahora mismo, publicado una vez por minuto en el namespace `AWS/Bedrock-AgentCore`, con dimensión de servicio |
| `Latency` | Tiempo total entre recibir la petición y enviar **el último token** de la respuesta |
| `Throttles`, `SystemErrors`, `UserErrors`, `TotalErrors` | Throttling y errores de servidor y de cliente. `TotalErrors` se muestra en consola como **porcentaje sobre el total de invocaciones** |

> **Dato decisivo**: `SessionCount` y `ActiveSessionCount` miden cosas distintas y no son intercambiables. El primero es un **contador acumulativo de creaciones**; el segundo, un **gauge de concurrencia**. Para alarmas de consumo de cuota de sesiones, el correcto es `ActiveSessionCount`. Las métricas de runtime se agrupan en intervalos de un minuto, y los datos de uso de recursos pueden **retrasarse hasta 60 minutos**.

La observabilidad de tool calling y la coordinación multi-agente se desarrollan en [Domain 4 · Skill 4.3.4](../domain-4/task-4-3-herramientas-vector-stores-y-fallos.md#skill-434--rendimiento-de-herramientas-y-coordinación-multi-agente).

---

## Skill 5.1.8 — Sistemas de reporting para stakeholders

> *Crear sistemas de reporting completos para comunicar métricas de rendimiento e insights de forma efectiva a los stakeholders de las implementaciones de FM (por ejemplo, usando herramientas de visualización, mecanismos de reporting automatizado, visualizaciones de comparación de modelos).*

### Lo que cada capa ya te da sin construir nada

| Capa | Qué produce por sí sola |
| --- | --- |
| **Job de evaluación de Bedrock** | Tarjeta de informe en consola con scores por métrica, histograma de distribución y explicaciones de los **primeros cinco prompts**. Informe completo en S3 como JSON Lines |
| **Evaluación de RAG** | Tarjeta con gráficos de desglose por métrica, y score medio 0 a 1 por métrica |
| **AgentCore Evaluations** | Resultados en CloudWatch Logs **y scores publicados como métricas de CloudWatch** |
| **Dashboard de GenAI Observability** | Vista de Evaluations por agente, con tendencias y capacidad de alarma |

### Los scores de evaluación de agente son métricas de CloudWatch

Es el hallazgo que resuelve el skill sin salir de AWS. De [Results and output](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/results-and-output.html):

| Aspecto | Detalle |
| --- | --- |
| **Destino por defecto de los logs** | Log group dedicado con prefijo `/aws/bedrock-agentcore/evaluations/results/` más el identificador de la configuración |
| **Alternativa** | Escribir los resultados **en el mismo log group que aportó los traces**, para que las evaluaciones aparezcan junto a los traces que puntuaron |
| **Namespace de métricas por defecto** | `Bedrock-AgentCore/Evaluations` |
| **Namespace propio** | Configurable, por ejemplo para separar por equipo o tenant |
| **Formato del resultado** | Sigue las **convenciones semánticas de OpenTelemetry para eventos de resultado de evaluación de GenAI**. Cada evento se emparenta con el span original y lleva el trace ID y el session ID originales |

> **Dato decisivo**: como los scores son métricas de CloudWatch, **un umbral de calidad puede ser una alarma de CloudWatch normal**. Eso es lo que cierra el círculo del [Skill 5.1.4](#skill-514--aseguramiento-de-calidad-continuo-y-quality-gates): no hace falta un mecanismo especial para convertir un score de calidad en un gate de despliegue.

Dos restricciones de nombres que provocan errores de configuración: el nombre de un log group de salida propio **no puede usar el prefijo reservado de evaluaciones**, salvo el grupo por defecto gestionado por el servicio de esa misma configuración; y el namespace de métricas propio **no puede empezar por `AWS/`**. Si el log group indicado no existe, el servicio lo crea, así que el rol de ejecución necesita permiso de creación de log group.

### El dashboard que ya existe

De [Agent details - Evaluations](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/session-traces-evaluations.html), en la consola de CloudWatch bajo **GenAI Observability**. La frase que define su propósito: en lugar de depender de casos de test simulados, **captura sesiones de usuario e interacciones reales**, dando una vista de extremo a extremo desde la entrada hasta la salida final.

Su estructura reproduce la jerarquía de niveles de evaluación:

| Sección | Qué muestra |
| --- | --- |
| **Evaluation configuration metrics** | Métricas de la configuración global, con enlace a cada evaluador y gráfico de barras de tendencia por evaluador |
| **Session evaluations** | Resultados de evaluadores de nivel sesión. Seleccionar una sesión filtra la lista de traces |
| **Trace evaluations** | Resultados de nivel trace, con todos los evaluadores que corrieron sobre ese trace |
| **Span evaluations** | Resultados de nivel span, con las operaciones de ese span |

Y la palanca de alerting: los gráficos de barras por evaluador permiten **crear una alarma directamente sobre un valor de métrica** desde el propio gráfico.

### Reporting automatizado a stakeholders que no entran en la consola

Para eso el servicio documentado es Amazon Quick Sight, con [dashboards y reports](https://docs.aws.amazon.com/quick/latest/userguide/working-with-dashboards.html) y [envío programado por correo](https://docs.aws.amazon.com/quick/latest/userguide/sending-reports.html).

| Límite | Valor |
| --- | --- |
| Schedules por dashboard | **5 como máximo** |
| Destinatarios de un correo programado | **No más de 5.000** |
| Periodicidad | Una vez, o diaria, semanal, mensual o anual |

Dos propiedades que importan en un contexto de governance:

- Un dashboard es un **snapshot de solo lectura** de un análisis: preserva filtros, parámetros, controles y orden en el momento de publicarlo, pero **no captura los datos**. Al verlo, refleja los datos actuales de los datasets.
- Quick Sight genera **un snapshot de correo personalizado por usuario o grupo** según sus permisos de datos. **Row Level Security, Column Level Security y parámetros dinámicos por defecto funcionan tanto en los correos programados como en los puntuales.** Un informe de calidad de modelo se puede distribuir a varios equipos con la fila filtrada por equipo, sin construir un informe por equipo.

Para que los destinatarios reciban el correo tienen que cumplir tres condiciones: pertenecer a la suscripción, que el dashboard esté ya compartido con ellos, y estar dentro del límite de destinatarios. También pueden [suscribirse ellos mismos](https://docs.aws.amazon.com/quick/latest/userguide/subscribing-to-reports.html) cuando hay un informe disponible.

### Visualizaciones de comparación de modelos

> **Discrepancia**: el skill pide *model comparison visualizations*. **AWS no documenta ninguna vista de comparación lado a lado de jobs de evaluación de modelo.** La tarjeta de informe es por job. La comparación hay que construirla.

Las tres vías con respaldo documental, en orden de esfuerzo:

1. **Un solo job con varios modelos.** Un job de evaluación admite más de un modelo generador, así que la comparación cabe dentro de un informe.
2. **Los ficheros JSON Lines de S3 como fuente de datos.** La ruta de salida incluye el identificador del modelo, así que los resultados de varios jobs se pueden cruzar por modelo.
3. **Métricas de CloudWatch** para los scores de agente, con el namespace y las dimensiones como eje de comparación.

La comparación que **sí** está construida por AWS es de **versiones de prompt**, no de modelos, y se trata en el [Task 5.2 · Skill 5.2.3](./task-5-2-monitoreo-troubleshooting-optimizacion.md#skill-523--troubleshooting-de-prompt-engineering).

Las capas de dashboards operativos y de negocio para métricas de FM están desarrolladas en [Domain 4 · Skill 4.3.3](../domain-4/task-4-3-observabilidad-y-metricas.md#skill-433--observabilidad-integrada-y-accionable).

---

## Skill 5.1.9 — Validación de despliegue

> *Crear sistemas de validación de despliegue para mantener la fiabilidad durante las actualizaciones del FM (por ejemplo, usando workflows sintéticos de usuario, validación de salidas específica de IA para tasas de hallucination y drift semántico, chequeos automatizados de calidad para asegurar consistencia de respuesta).*

### Workflows sintéticos de usuario: dos mecanismos distintos

El enunciado es ambiguo y AWS documenta **dos cosas diferentes** que encajan con él. Distinguirlas es el núcleo del skill.

| Mecanismo | Qué simula | Cuándo aplica |
| --- | --- | --- |
| [**Canaries de CloudWatch Synthetics**](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries.html) | El **camino técnico** de un cliente: endpoints, APIs, navegación de UI | Verificar que el sistema responde y con qué latencia, incluso sin tráfico real |
| [**User simulation de AgentCore**](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/user-simulation.html) | La **conversación** de un usuario: un actor LLM con personalidad y objetivo | Verificar que el agente resuelve el objetivo en diálogo abierto multi-turno |

### Canaries: qué son exactamente

Scripts configurables que corren en un horario y **siguen las mismas rutas y ejecutan las mismas acciones que un cliente**, lo que permite verificar la experiencia de cliente de forma continua aunque no haya tráfico. Detalles que importan:

- Están escritos en **Node.js, Python o Java**, y **crean funciones Lambda en la cuenta** que usan esos runtimes. Funcionan sobre HTTP y HTTPS.
- En Node.js y Python dan acceso programático a navegadores headless mediante **Playwright, Puppeteer o Selenium WebDriver**. **Los canaries en Java no incluyen soporte de navegador ni frameworks.** Selenium solo soporta Chrome.
- Pueden correr **una vez o en horario, hasta una vez por minuto**, con expresiones cron o de rate.
- Publican métricas en el namespace **`CloudWatchSynthetics`**, con `CanaryName` como dimensión, y `StepName` adicional en los canaries que usan las funciones de paso de la [librería de funciones](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries_Function_Library.html).

Las métricas relevantes, de [CloudWatch metrics published by canaries](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries_metrics.html):

| Métrica | Qué mide |
| --- | --- |
| `SuccessPercent` | Porcentaje de ejecuciones que tienen éxito y **no encuentran fallos** |
| `SuccessPercentWithRetries` | Porcentaje que tiene éxito **después de todos los intentos** |
| `Duration` | Duración de la ejecución del canary, en milisegundos |
| `Failed` | Ejecuciones que fallaron al ejecutarse. **Fallos del canary en sí**, no del sistema monitorizado |
| `Failed requests` | Peticiones HTTP sobre el sitio objetivo que fallaron **sin respuesta** |
| `2xx`, `4xx`, `5xx` | Peticiones de red por familia de código de respuesta |
| `VisualMonitoringSuccessPercent` | Porcentaje de comparaciones visuales que coincidieron con las capturas de baseline |

> **Dato decisivo**: `Failed` y `Failed requests` **no miden lo mismo**. `Failed` cuenta fallos **del propio canary**; `Failed requests` cuenta peticiones al sistema monitorizado que no obtuvieron respuesta. Alarmar sobre la métrica equivocada produce o falsos positivos por un script roto, o ceguera ante una caída real.

De los [blueprints](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries_Blueprints.html), el relevante para una API de GenAI es el **API canary**, que prueba las funciones de lectura y escritura de una API REST:

- Admite **canaries multi-paso**: varias APIs en un canary, cada paso con su URL, sus cabeceras y sus reglas propias sobre si se capturan cabeceras y cuerpo de respuesta.
- **No capturar cabeceras ni cuerpo de respuesta es el mecanismo para evitar que datos sensibles queden registrados.** En un canary que llama a un FM, eso es lo que impide que prompts y respuestas acaben en los artefactos del canary.
- Está integrado con API Gateway: se puede elegir una API y un stage de la misma cuenta y Región, o subir una plantilla Swagger para monitorización cross-account y cross-Region.
- El blueprint soporta GET y POST, y obliga a especificar cabeceras.

> **Gotcha**: los blueprints de API canary **no están soportados por los runtimes de Playwright**. Y el blueprint de heartbeat monitoring almacena captura de pantalla y fichero HAR, útil para analizar la lista de peticiones y detectar problemas de tiempo de carga.

Los canaries se integran con el [Trace Map de X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/xray-console-servicemap.html) y con Application Signals, pero **para verlos en Application Signals hay que activar el tracing activo de X-Ray**.

### User simulation: el actor LLM

De [User simulation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/user-simulation.html). Un actor respaldado por un LLM interpreta el papel de usuario final: se define su perfil y su objetivo, y el actor conduce una conversación multi-turno con el agente **hasta que el objetivo se cumple o se alcanza el límite de turnos**.

El bucle tiene cinco pasos, y el tercero es el interesante: el actor recibe la respuesta del agente y produce una respuesta estructurada con tres partes:

| Parte | Contenido |
| --- | --- |
| **Reasoning** | El razonamiento interno del actor sobre por qué responde lo que responde. Sirve para **depurar por qué el actor se comportó de una manera** |
| **Message** | El siguiente mensaje que se envía al agente |
| **Stop signal** | Booleano que indica si el actor considera cumplido su objetivo |

El perfil del actor tiene tres campos:

| Campo | Obligatorio | Contenido |
| --- | --- | --- |
| `context` | Sí | Información de fondo: la situación y los detalles relevantes que el actor debe conocer |
| `goal` | Sí | Lo que el actor quiere conseguir. El actor señala la finalización cuando determina que se ha cumplido |
| `traits` | No | Pares clave-valor con características: nivel de expertise, estilo de comunicación, paciencia |

El límite de turnos por defecto es **10**, con mínimo 1.

> **Dato decisivo**: los escenarios simulados **no admiten trayectoria esperada ni respuesta esperada por turno**, porque el flujo de la conversación no se conoce por adelantado. El único ground truth disponible en simulación son las **afirmaciones**, que consume `Builtin.GoalSuccessRate`. Es una restricción estructural, no una limitación temporal.

Los cuatro usos que AWS declara son los del skill: probar con variación realista, porque el actor genera fraseos, preguntas de seguimiento y caminos distintos en cada ejecución, exponiendo casos límite que los escenarios escritos a mano no alcanzan; evaluar conversaciones abiertas; escalar la cobertura de escenarios sin escribir docenas de guiones; y **testing de regresión con diversidad**, ejecutando el mismo perfil de actor varias veces para comprobar que el agente maneja expresiones variadas de la misma intención.

> **Coste que no se ve**: la simulación de usuario **invoca modelos de Bedrock del lado del SDK** para generar las respuestas del actor, y esas llamadas se facturan como cualquier invocación de modelo. Un escenario de 10 turnos son 10 invocaciones del actor más 10 del agente.

### Tasas de hallucination

El skill pide validación de salidas para tasas de hallucination. Hay dos fuentes, y miden cosas distintas:

| Fuente | Qué da | Dónde está |
| --- | --- | --- |
| **`Builtin.Faithfulness`** del job de RAG retrieve-and-generate | Un score agregado de cuánto evitan las respuestas la hallucination respecto a los textos recuperados | [Skill 5.1.5](./task-5-1-frameworks-y-herramientas.md#skill-515--evaluación-multiperspectiva-rag-juez-y-humanos) |
| **Contextual grounding check** de Guardrails | Un score y un umbral **por invocación**, en tiempo real | [Domain 3 · Skill 3.1.3](../domain-3/task-3-1-controles-de-seguridad-entrada-salida.md#skill-313--verificación-de-exactitud-y-reducción-de-hallucinations) |

> **Dato decisivo**: **una "tasa de hallucination" no es una métrica que AWS publique.** Se construye. La vía offline es el score medio de `Builtin.Faithfulness` sobre un dataset; la vía en producción es contar cuántas invocaciones cruzaron el umbral del contextual grounding check. La segunda es la que sirve como gate de despliegue, porque es continua. El uso de estas señales como KPI operativo se desarrolla en [Domain 4 · Skill 4.3.2](../domain-4/task-4-3-observabilidad-y-metricas.md#skill-432--monitorización-proactiva-y-kpis-específicos-de-fm).

### El drift semántico

> **Discrepancia**: el skill nombra *semantic drift*. **Ninguna página de `docs.aws.amazon.com` documenta una funcionalidad de detección de drift semántico para salidas de FM.** No existe ni como métrica, ni como servicio, ni como configuración.

Lo que AWS sí documenta, y es la respuesta defendible:

| Señal | Mecanismo |
| --- | --- |
| **La calidad se erosionó entre releases** | El problema está nombrado en AGENTOPS06 como decadencia de prompt y erosión silenciosa por actualizaciones del modelo upstream. El remedio es evaluación continua contra un benchmark versionado |
| **Los scores se movieron** | Alarma de anomaly detection sobre las métricas de score del namespace de evaluaciones |
| **La respuesta dejó de ser consistente** | Comparación antes/después con batch evaluation sobre el mismo conjunto curado de sesiones |
| **Los patrones de log cambiaron** | Anomaly detection de CloudWatch Logs, tratado en el [Task 5.2 · Skill 5.2.5](./task-5-2-monitoreo-troubleshooting-optimizacion.md#skill-525--mantenimiento-y-observabilidad-de-prompts) |

Las técnicas de **golden dataset y output diffing** para consistencia de respuesta están desarrolladas en [Domain 4 · Skill 4.3.6](../domain-4/task-4-3-herramientas-vector-stores-y-fallos.md#skill-436--troubleshooting-de-modos-de-fallo-propios-de-genai).

### La decisión de release

El cierre del skill es el marco del Responsible AI Lens. [RAIER01](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/raier01.html) plantea *¿cómo vas a evaluar el sistema contra tus criterios de release?* y aporta dos exigencias que una validación de despliegue puramente automática no cubre:

- **Contrastar las evaluaciones con evaluaciones de expertos ajenos al equipo**, desarrollado en [RAIER01-BP02](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/raier01-bp02.html) para las valoraciones más críticas y subjetivas.
- **Establecer una metodología para combinar los resultados de cada criterio** en una decisión única, en lugar de mirar cada métrica por separado.

Y [RAIER03](https://docs.aws.amazon.com/wellarchitected/latest/responsible-ai-lens/raier03.html) cubre el caso de los criterios no cumplidos. La revisión humana como capa del workflow está en [Domain 2 · Skill 2.1.5](../domain-2/task-2-1-agentic-ai-y-herramientas.md#skill-215--sistemas-colaborativos-con-expertise-humana).

---

## Resumen operativo: retrieval, agentes y validación

| Si la pregunta menciona… | La respuesta apunta a |
| --- | --- |
| Evaluar un **agente** | **AgentCore Evaluations**, no Bedrock model evaluation |
| Tasa de finalización de tarea | `Builtin.GoalSuccessRate`, nivel **sesión**, con afirmaciones |
| Efectividad de uso de herramienta | Evaluador de nivel **`TOOL_CALL`** |
| Secuencia de herramientas correcta | Los tres `Builtin.Trajectory*Match`, **programáticos, sin LLM** |
| Evaluación sin consumir tokens de juez | Trayectoria, o evaluador **code-based** con Lambda |
| ARN sin Región ni cuenta | Evaluador **integrado** de AgentCore |
| Ground truth en producción en vivo | No se puede: los placeholders de ground truth **no valen en evaluación online** |
| Evaluación continua sobre tráfico real | Evaluación **online**, con muestreo por porcentaje o filtros |
| Baseline, antes/después, regresión | Evaluación **batch**, que descubre las sesiones desde CloudWatch Logs |
| Investigar una interacción concreta | Evaluación **on-demand**, por span o trace ID |
| Evaluación que devuelve cero resultados | Esperar **2 a 5 minutos** a la ingesta de telemetría. Comprobar ADOT y Transaction Search |
| Sesiones activas ahora mismo | `ActiveSessionCount`, no `SessionCount` |
| Score alto en Stereotyping | **Es malo**: el score 0 a 1 mide cuánto de esa característica hay, no cuán bueno es |
| Latencia de retrieval | **No sale del job de RAG evaluation**. Métricas del vector store, o duración de un canary |
| Medir precisión de retrieval en OpenSearch | Fijar **`size`** además de `k`, o se devuelven `k` por shard y segmento |
| Simular el camino técnico de un cliente | **Canary de Synthetics**, blueprint de API canary |
| Simular una conversación de usuario | **User simulation** de AgentCore, con perfil de actor |
| Evitar que prompts y respuestas queden en los artefactos del canary | **No capturar cabeceras ni cuerpo** de respuesta en el paso HTTP |
| Canary en Java con navegador | No existe: los canaries Java **no traen soporte de navegador** |
| Tasa de hallucination | Se construye: `Builtin.Faithfulness` offline, o cruces del umbral de **contextual grounding check** en producción |
| Drift semántico | **No existe como funcionalidad.** Anomaly detection sobre scores, más comparación batch antes/después |
| Umbral de calidad que bloquea un despliegue | Alarma de CloudWatch sobre el namespace **`Bedrock-AgentCore/Evaluations`** |
| Distribuir un informe con datos filtrados por equipo | Quick Sight con **RLS y CLS**, que funcionan en los correos programados |
| Comparación lado a lado de modelos | **No existe vista nativa.** Un job con varios modelos, o cruzar los JSON Lines de S3 |
