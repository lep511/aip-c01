# Task 2.1 — Soluciones agentic AI e integración de herramientas

[← Volver al índice](./README.md)

Skills cubiertos: **2.1.1**, **2.1.2**, **2.1.3**, **2.1.4**, **2.1.5**, **2.1.6**, **2.1.7**.

---

## El marco de referencia del dominio: Agentic AI Lens

Antes de entrar en los skills conviene fijar el marco, porque AWS publicó un lens específico para esto y los siete skills de este task se apoyan en él.

De [Agentic AI Lens — AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html) (fecha de publicación: 10 de junio de 2026). El lens extiende el Well-Architected Framework con prácticas específicas para diseñar, desplegar y operar sistemas agentic en AWS. Su punto de partida es que las organizaciones ya no preguntan *¿podemos construir un agente?* sino *¿podemos operarlo de forma fiable, segura y rentable a escala?*

### Las cinco dimensiones que hacen distinto a un sistema agentic

| Dimensión | Implicación arquitectónica |
| --- | --- |
| **Los agentes razonan, no solo responden** | Una única petición de usuario puede disparar varias llamadas de inferencia, invocaciones de herramienta, recuperaciones de memoria y comunicaciones entre agentes. Cada una añade latencia, coste y superficie de fallo. La optimización clásica petición-respuesta no cubre bucles de razonamiento iterativos |
| **Los agentes actúan de forma autónoma** | Invocan herramientas, modifican datos e interactúan con sistemas externos sin instrucción humana explícita en cada paso. Exige controles de seguridad, fronteras de permisos y patrones de supervisión diseñados para operación autónoma |
| **El comportamiento es estocástico** | La misma entrada puede producir salidas distintas. La fiabilidad se aborda con monitorización de comportamiento, frameworks de evaluación y degradación elegante, no solo con testing determinista |
| **Los agentes colaboran** | Los sistemas multi-agente introducen overhead de coordinación, complejidad de handoff y modos de fallo distribuidos. Los patrones de orquestación y los protocolos de comunicación pasan a ser preocupaciones de primer nivel |
| **Los agentes recuerdan** | La memoria persistente entre sesiones habilita personalización y aprendizaje, pero introduce retos de integridad de datos, privacidad y gestión de coste que las aplicaciones stateless no tienen |

### Los cinco principios de responsible agentic AI

El lens incorpora IA responsable dentro de sus best practices en lugar de tratarla como tema aparte:

| Principio | Qué significa | Área de foco |
| --- | --- | --- |
| **Bounded autonomy** | Cada agente opera dentro de un alcance explícitamente definido, con guardrails que restringen el comportamiento sin depender de las entradas recibidas | [AGENTSEC04](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec04.html) |
| **Transparencia y explicabilidad** | Las decisiones del agente se registran, se trazan y son auditables, para poder reconstruir qué ocurrió en cualquier ejecución | AGENTOPS05 |
| **Human oversight** | Modelos de supervisión escalonados que ajustan el nivel de revisión humana al riesgo y a la reversibilidad de cada acción | AGENTREL02-BP05 |
| **Goal alignment** | Frameworks de evaluación que comprueban de forma continua si el agente logra los objetivos previstos en lugar de perseguir metas desalineadas | AGENTOPS06 |
| **Sostenibilidad organizacional** | La adopción de agentes preserva la expertise humana y el conocimiento institucional en lugar de crear dependencias de sistemas que solo entienden sus autores originales | AGENTSUS03 |

### Los seis pilares del lens

| Pilar | Enfoque en sistemas agentic |
| --- | --- |
| **Operational excellence** | Operar y mejorar sistemas autónomos: ciclo de vida del prompt, monitorización de comportamiento, governance human-in-the-loop |
| **Security** | Asegurar identidades de agente, acceso a herramientas y flujos de datos; protección frente a prompt injection, escalada de privilegios y manipulación de operaciones autónomas |
| **Reliability** | Ejecución predecible de tareas, recuperación automática de fallos, funcionalidad parcial bajo condiciones adversas |
| **Performance efficiency** | Optimizar cognitive pipelines, selección de modelo, acceso a memoria y coordinación multi-agente |
| **Cost optimization** | Diseñar con el coste como consideración primaria, right-sizing de modelo y memoria, visibilidad total de coste |
| **Sustainability** | Arquitecturas modulares y reutilizables que maximizan la eficiencia de recursos |

### El landscape tecnológico que asume el lens

El lens nombra explícitamente los componentes sobre los que construye:

- **Amazon Bedrock** para acceso a FMs con guardrails, knowledge bases, prompt management y evaluación de modelos.
- **Amazon Bedrock AgentCore** como infraestructura propósito-específica para desplegar y operar agentes a escala, agnóstica de framework y de modelo.
- **Strands Agents** como framework open source model-driven con soporte nativo de herramientas MCP, protocolo A2A y patrones multi-agente (Graph, Swarm y Workflow).
- **MCP y A2A** como protocolos abiertos de comunicación agente-herramienta y agente-agente.
- **Kiro** como IDE agentic con workflows spec-driven, steering files para estándares de equipo y hooks para comprobaciones automatizadas de calidad.

> **Sobre Strands Agents y AWS Agent Squad**: los skills 2.1.1, 2.1.6 y 2.5.5 nombran estos dos frameworks, pero **ninguno tiene guía de servicio en `docs.aws.amazon.com`**. Strands aparece nombrado en el Agentic AI Lens y en las páginas de AgentCore como framework soportado, sin documentación propia en el portal; Agent Squad no aparece en el portal en absoluto. Este archivo cubre esos skills con lo que AWS sí documenta: AgentCore como sustrato de ejecución, el Agentic AI Lens como marco de diseño y Step Functions como orquestador durable. El detalle del hueco está en [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación).

### Rutas de lectura que propone el lens

El propio lens ordena sus áreas de foco por madurez del proyecto, lo que sirve de guía de estudio:

```
Primer agente          → AGENTOPS01 · AGENTREL02 · AGENTSEC03 · AGENTSEC08
A producción           → AGENTOPS05 · AGENTOPS06 · AGENTPERF02 · AGENTCOST01 · AGENTCOST02
Escalar a multi-agente → AGENTREL04 · AGENTPERF05 · AGENTSEC06 · AGENTCOST05
Endurecer lo existente → AGENTSEC04 · AGENTSEC07 · AGENTREL06
```

El lens se descarga como **custom lens** e se importa en [AWS WA Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/lenses-custom.html) desde el repositorio público de custom lenses de AWS Well-Architected.

---

## Skill 2.1.1 — Sistemas autónomos con memoria y gestión de estado

> *Desarrollar sistemas autónomos inteligentes con capacidades apropiadas de memoria y gestión de estado (por ejemplo, usando Strands Agents y AWS Agent Squad para sistemas multi-agente, MCP para interacciones agente-herramienta).*

### El problema de fondo: los FMs son stateless

De [Add memory to your Amazon Bedrock AgentCore agent](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html). AgentCore Memory aborda un reto fundamental de la IA agentic: **la ausencia de estado**. Sin capacidades de memoria, un agente trata cada interacción como una instancia nueva, sin conocimiento de conversaciones previas. Es el mismo punto de partida que ya vimos en [Task 1.6 · Skill 1.6.2](../domain-1/task-1-6-prompt-engineering-governance.md) para conversaciones con `Converse`: la diferencia es que aquí la persistencia es un servicio gestionado en lugar de código propio.

### Los dos tipos de memoria de AgentCore Memory

| Tipo | Alcance | Qué captura | Ejemplo oficial |
| --- | --- | --- | --- |
| **Short-term memory** | Una sola sesión | Interacciones turno a turno, para mantener el contexto inmediato sin que el usuario repita información | El usuario pregunta por el tiempo en Seattle y luego dice "¿y mañana?"; el agente resuelve la referencia con el histórico reciente |
| **Long-term memory** | Entre múltiples sesiones | Extrae y almacena automáticamente insights clave: preferencias de usuario, hechos importantes y resúmenes de sesión | El cliente menciona que prefiere asiento de ventanilla; en interacciones futuras el agente lo ofrece de forma proactiva |

Beneficios que la documentación atribuye al servicio: conversaciones más naturales (resolver afirmaciones ambiguas usando turnos previos), experiencias personalizadas (retener preferencias y hechos entre sesiones) y menor complejidad de desarrollo (delegar la gestión de estado conversacional para centrarse en la lógica de negocio del agente).

### Las cuatro estrategias built-in de memoria de largo plazo

De [Configure built-in strategies](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/long-term-configuring-built-in-strategies.html). Son estrategias preconfiguradas para casos de uso comunes, y **se pueden combinar varias al crear una memoria**:

| Estrategia | Identificador | Qué extrae | Caso de uso oficial |
| --- | --- | --- | --- |
| **User preferences** | `userPreferenceMemoryStrategy` | Preferencias, elecciones y estilos del usuario, construyendo un perfil persistente | Un agente de e-commerce recuerda marcas favoritas y talla preferida para recomendar productos en sesiones futuras |
| **Semantic** | `semanticMemoryStrategy` | Información factual y conocimiento contextual: entidades, eventos y detalles tratados | Un agente de soporte recuerda que el pedido `#ABC-123` está asociado a un ticket concreto, sin volver a pedir el número |
| **Session summaries** | `summaryMemoryStrategy` | Resúmenes condensados y acumulativos dentro de una sesión, con temas y decisiones clave | Tras 30 minutos de troubleshooting, el agente accede a un resumen del problema, los intentos realizados y lo que se entregó |
| **Episodic** | `episodicMemoryStrategy` | Episodios estructurados con escenarios, intenciones, pensamientos, acciones, resultados y artefactos. Añade **reflexiones entre episodios** para extraer insights más amplios | Un agente de soporte registra qué frases y acciones conducen a interacciones exitosas, y aplica los patrones que funcionaron |

Cada estrategia se configura con **`namespaceTemplates`**, que definen el aislamiento de los datos mediante plantillas con variables:

```python
import boto3

control_client = boto3.client('bedrock-agentcore-control', region_name='us-west-2')

response = control_client.create_memory(
    name="ECommerceAgentMemory",
    memoryStrategies=[
        {
            'userPreferenceMemoryStrategy': {
                'name': 'UserPreferenceExtractor',
                'namespaceTemplates': ['/users/{actorId}/preferences/']
            }
        }
    ]
)
```

Las variables disponibles en los namespaces (`{actorId}`, `{sessionId}`, `{memoryStrategyId}`) son el mecanismo de **aislamiento multi-tenant** de la memoria: determinan quién ve qué. La estrategia episódica usa además un bloque `reflection` con su propio namespace, normalmente a nivel de actor y no de sesión, porque las reflexiones cruzan episodios.

> La extracción a memoria de largo plazo es un **proceso asíncrono en background** que analiza los eventos de conversación en crudo aplicando las estrategias configuradas. No es sincrónica con el turno.

### Gestión de estado en AgentCore Runtime: sesiones y microVMs

De [microVMs — AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html). El Runtime se ocupa de escalado, gestión de sesiones, aislamiento de seguridad y gestión de infraestructura. Sus componentes clave:

| Componente | Comportamiento |
| --- | --- |
| **AgentCore Runtime** | Aplicación contenedorizada que hospeda el código del agente o de la herramienta. Tiene **identidad única** y está **versionada** para despliegue y actualización controlados |
| **Versions** | Versiones **inmutables** que capturan un snapshot completo de la configuración. Al crear el runtime se crea V1 automáticamente; cada cambio de configuración (imagen de contenedor, protocolo, red) crea una versión nueva. Da historial de despliegue y capacidad de rollback |
| **Endpoints** | Puntos de acceso direccionables a versiones concretas, cada uno con su ARN. El endpoint `DEFAULT` se crea con `CreateAgentRuntime` y apunta a la última versión, actualizándose automáticamente. Se crean endpoints propios con `CreateAgentRuntimeEndpoint` para separar entornos (dev, test, prod). Los endpoints se actualizan **sin downtime** |
| **Sessions** | Contextos de interacción individuales, identificados por `runtimeSessionId` (lo aporta la aplicación, o lo genera el Runtime en la primera invocación si se deja vacío) |

**Ciclo de vida de una sesión**, que es el dato operativo que más importa para diseñar el estado:

| Aspecto | Valor |
| --- | --- |
| Aislamiento | Cada sesión corre en un **microVM dedicado** con CPU, memoria y sistema de archivos completamente aislados |
| Duración máxima | Hasta **8 horas** de runtime total |
| Terminación por inactividad | **15 minutos** sin procesar peticiones |
| Estados | `Active` (procesando petición o tareas de fondo), `Idle` (sin procesar, manteniendo contexto), `Terminated` |
| Tras terminar | El microVM completo se termina y **la memoria se sanea** |
| Reutilización del ID | Una petición posterior con el mismo `runtimeSessionId` tras la terminación crea un **entorno de ejecución nuevo** |

> **La regla de diseño explícita de la documentación**: el estado de sesión es **efímero** y no debe usarse para durabilidad a largo plazo. Para durabilidad del contexto, AgentCore Memory.

Estados del ciclo de vida de un endpoint: `CREATING`, `CREATE_FAILED`, `READY`, `UPDATING`, `UPDATE_FAILED`.

**Platform versions (V1 y V2)**. El campo `platformVersion` controla cómo arranca el agente. V1 es el valor por defecto. V2 arranca el agente **desde un snapshot**: el Runtime prepara el entorno una vez, lo fotografía y restaura esa foto en cada instancia nueva en lugar de inicializar el entorno en cada arranque.

| Aspecto | V1 | V2 |
| --- | --- | --- |
| Cold start | Inicializa el entorno en cada arranque | Restaura un snapshot preparado: latencia **consistente** independientemente de la concurrencia o del tamaño de la imagen |
| Tiempo hasta `READY` | Segundos | Varios minutos (coste único de preparar el snapshot) |
| Coste | Modelo estándar | Cobra por lo que el agente **usa activamente**; el Runtime reclama memoria a medida que el agente la libera |
| Health check | — | El contenedor debe reportar salud en **`/ping` dentro de 120 segundos**; el snapshot se toma en la primera respuesta saludable |
| Variables de entorno | 4 KB | 1,5 KB para despliegues de código directo y 2,5 KB para agentes en contenedor |

V2 está disponible en `us-east-1`, `us-east-2`, `us-west-2`, `eu-west-1` y `ap-northeast-1`.

> Dos avisos operativos de la documentación de V2: reportar salud en `/ping` **solo después** de completar la inicialización, para que el snapshot capture un agente totalmente inicializado; y hacer **polling de `get_agent_runtime`** hasta un estado terminal (`READY` o algo terminado en `FAILED`), porque `create` y `update` devuelven mientras el runtime sigue en `CREATING` o `UPDATING`, y llamar a `update` o `delete` antes produce `ConflictException`.

### Tabla de decisión: dónde vive el estado

| Opción | Alcance | Durabilidad | Cuándo elegirla |
| --- | --- | --- | --- |
| **Contexto de la petición** (`messages` de `Converse`) | Un turno | Ninguna | Interacciones sin seguimiento. Base cubierta en [Task 1.3 · Skill 1.3.3](../domain-1/task-1-3-datos-para-consumo-fm.md) |
| **Sesión de AgentCore Runtime** (microVM) | Una sesión, máximo 8 h | Efímera, se sanea al terminar | Estado de trabajo del agente: ficheros temporales, resultados intermedios |
| **AgentCore Memory short-term** | Una sesión | Gestionada | Histórico turno a turno sin construir la persistencia |
| **AgentCore Memory long-term** | Entre sesiones | Gestionada, con extracción asíncrona | Preferencias, hechos, resúmenes y episodios; personalización |
| **DynamoDB** | Lo que definas | Tuya, con TTL y Streams | Control total del esquema, auditoría propia, integración con el resto del sistema. Diseño detallado en [Task 1.6 · Skill 1.6.2](../domain-1/task-1-6-prompt-engineering-governance.md) |
| **Estado de ejecución de Step Functions** | Una ejecución, hasta 1 año en Standard | Durable, con historial de ejecución | Workflows de negocio de larga duración con pasos auditables y esperas humanas |
| **Knowledge base** | Corpus compartido | Durable e indexada | Conocimiento de dominio, no estado de conversación. Ver [Task 1.4](../domain-1/task-1-4-vector-stores.md) |

La distinción que el examen puede explorar: **memoria no es lo mismo que knowledge base**. La memoria guarda lo que ocurrió en las interacciones con un actor concreto; la knowledge base guarda el conocimiento del dominio, compartido entre todos. Y ninguna de las dos es el estado de ejecución del workflow.

### Interacción agente-herramienta con MCP

El skill nombra MCP como el mecanismo de interacción agente-herramienta. Dos servicios de AgentCore lo materializan, y el detalle técnico está en el [Skill 2.1.7](#skill-217--frameworks-de-extensión-del-modelo):

| Servicio | Papel respecto a MCP |
| --- | --- |
| **AgentCore Gateway** | Convierte APIs, funciones Lambda y servicios existentes en **tools compatibles con MCP**, y conecta a MCP servers preexistentes, exponiéndolos a los agentes a través de endpoints de Gateway |
| **AgentCore Runtime** | Hospeda **MCP servers propios** con el contrato de protocolo documentado, además de agentes |

### Coordinación multi-agente: el marco oficial

El skill habla de sistemas multi-agente. Las dos áreas de foco del lens que lo cubren:

De [AGENTOPS01 — Operational practices for agentic AI systems](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentops01.html), la intención de capacidad:

- Cada agente tiene un **propósito documentado**, criterios de éxito medibles y fronteras de autonomía trazables a un resultado de negocio concreto.
- La coordinación multi-agente fluye por **protocolos de handoff estandarizados** que transfieren contexto de forma fiable y derivan el trabajo a un revisor humano cuando se exceden umbrales de confianza, de riesgo o de capacidad.
- Los sistemas se validan contra **modos de fallo realistas** en componentes dependientes, protocolos de orquestación y procesos de negocio, antes de producción y en cada cambio de comportamiento.
- Señales operativas, resultados de tests de fallo y métricas de negocio alimentan un **bucle de mejora continua**.
- Los artefactos operativos (descripciones de puesto del agente, runbooks de handoff, escenarios de test de fallo) se tratan como **documentos vivos**.

La progresión de madurez que describe va de conocimiento que vive en la cabeza de cada builder, con handoffs que pierden contexto y fallos descubiertos en incidentes de producción (nivel 1), a cada agente con su *job description* documentada y runbooks básicos de handoff con rutas de escalado humano (nivel 2).

De [AGENTREL04 — Multi-agent orchestration](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel04.html), el patrón arquitectónico:

| Elemento | Qué recomienda |
| --- | --- |
| **Arbiter pattern** | Concentrar la resolución de conflictos en un **árbitro dedicado** que actúa solo cuando hace falta coordinación, para que los agentes especializados operen de forma independiente sin negociar cada desacuerdo peer-to-peer |
| **Capability taxonomy** | Describir los agentes en una **taxonomía estructurada de capacidades** que alimente routing determinista y sustitución automática cuando el agente preferido no está disponible |
| **Fallback chains** | Cada agente crítico tiene una cadena de fallback **explícita y ordenada**, con trade-offs de calidad documentados, para que un fallo individual produzca capacidad reducida y no colapso del workflow |
| **Control plane redundante** | El plano de control es redundante, durable y **débilmente acoplado** a los agentes, para que la infraestructura de coordinación sea al menos tan fiable como los agentes que coordina |
| **Observabilidad de la coordinación** | Decisiones de arbitraje, resultados de routing, activaciones de fallback y salud del control plane son telemetría de primer nivel, validada con **fault injection** y ejercicios de disaster recovery periódicos |

Los servicios que el lens asocia a cada nivel de madurez de la orquestación son un mapa útil de qué usar:

```
Nivel 2  Árbitro central para conflictos críticos
         Catálogo simple de agentes que consultan los orquestadores
         Ejecución en AgentCore Runtime, sin estado de workflow persistido end-to-end

Nivel 3  Políticas de arbitraje externalizadas en SSM Parameter Store o DynamoDB
         Escalado humano vía Amazon SNS para conflictos irresolubles
         Agentes registrados en AgentCore Registry con metadatos de capacidad
           y descubiertos por búsqueda semántica
         Cadenas de fallback documentadas por agente crítico
         Orquestación con AWS Step Functions para estado durable

Nivel 4  Árbitro event-driven con Amazon EventBridge: se activa solo para
           resolver conflictos, no media cada mensaje
         Registro de capacidades automatizado en CI/CD
         Health checking proactivo con el endpoint /ping de AgentCore Runtime,
           que activa el fallback sin esperar timeouts
         AWS Fault Injection Service valida las cadenas de fallback periódicamente
         Los agentes toleran cortes breves del control plane

Nivel 5  Recalibración continua desde telemetría de AgentCore Observability
         Hotspots de contención en CloudWatch Contributor Insights
         Failover del control plane automatizado y demostrable
```

**Problemas frecuentes** que el lens señala, y que son el material natural de un distractor de examen: agentes que coordinan peer-to-peer sin árbitro, produciendo deadlocks cuando compiten por el mismo recurso; orquestación que **hardcodea identificadores de agente**, de modo que el routing no se adapta cuando un agente se reemplaza; cadenas de fallback que existen pero nunca se ejercitan; un control plane con estado en memoria como punto único de fallo; y métricas solo agregadas, que ocultan los hotspots de contención hasta que dominan la experiencia del usuario.

---

## Skill 2.1.2 — Razonamiento estructurado y descomposición de problemas

> *Crear sistemas avanzados de resolución de problemas para dar a los FMs la capacidad de descomponer y resolver problemas complejos siguiendo pasos de razonamiento estructurado (por ejemplo, usando Step Functions para implementar patrones ReAct y enfoques de razonamiento chain-of-thought).*

### Por qué Step Functions y no un bucle en código

De [What is Step Functions?](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html). Step Functions permite crear workflows (llamados *state machines*) para construir aplicaciones distribuidas, automatizar procesos, orquestar microservicios y crear pipelines de datos y machine learning. Cada paso es un *state*; un `Task` state representa una unidad de trabajo que otro servicio de AWS realiza. Las instancias en ejecución son *executions*.

Lo relevante para el razonamiento de un agente: la consola permite **visualizar, editar y depurar** el workflow, examinando el estado de cada paso. Y se pueden crear workflows automatizados de larga duración para aplicaciones que **requieren interacción humana**.

### Standard vs Express: la decisión que condiciona el diseño

| | **Standard** | **Express** |
| --- | --- | --- |
| Semántica de ejecución | **Exactly-once**: cada paso se ejecuta exactamente una vez | **At-least-once**: uno o más pasos pueden ejecutarse más de una vez |
| Duración máxima | **1 año** | **5 minutos** |
| Tasa de ejecución | 2.000 por segundo | 100.000 por segundo |
| Transiciones de estado | 4.000 por segundo | Casi ilimitadas |
| Precio | Por **transición de estado** | Por **número y duración** de ejecuciones |
| Historial | Historial de ejecución y debug visual | Según log level, enviado a CloudWatch |
| Integraciones | Todas, más integraciones optimizadas con algunos servicios | Todas |

Para razonamiento agentic esto se traduce en:

- **Standard** para bucles de razonamiento que pueden tardar, que incluyen esperas humanas, o donde repetir un paso tiene efectos colaterales (una llamada de FM cuesta dinero; una escritura en un sistema de negocio no es idempotente).
- **Express** para pre-procesamiento y clasificación de alto volumen y corta duración, donde la idempotencia está garantizada por diseño.

> El coste por transición de estado en Standard es un dato de diseño, no una nota al pie: un bucle ReAct de 10 iteraciones con 4 estados por iteración son 40 transiciones por consulta. Los **reintentos también cuentan como transiciones de estado** a efectos de facturación.

### Modelar ReAct con Amazon States Language

El patrón ReAct alterna razonamiento y acción: el modelo piensa, elige una herramienta, observa el resultado y vuelve a pensar hasta poder responder. Sobre Step Functions eso se expresa con `Choice`, `Task` y un contador de iteraciones:

```
Entrada del usuario
   │
   ▼
┌─────────────────────────────────────────────────────┐
│ Task: Converse con toolConfig                       │  ← razonamiento
│   El FM decide: ¿responder o invocar herramienta?   │
└─────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────┐
│ Choice: ¿stopReason = tool_use?                     │
│   no  ──────────────────────────────► Succeed       │
│   sí                                                │
└─────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────┐
│ Choice: ¿iteración < maxIteraciones?                │  ← stopping condition
│   no  ──────────────────────────────► Fail / Fallback│
│   sí                                                │
└─────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────┐
│ Task: invocar la herramienta elegida (Lambda)       │  ← acción
│   TimeoutSeconds · Retry · Catch                    │
└─────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────┐
│ Pass: añadir toolResult a messages, iteración += 1  │  ← observación
└─────────────────────────────────────────────────────┘
   │
   └──────────► vuelta al Task de razonamiento
```

De [Choice workflow state](https://docs.aws.amazon.com/step-functions/latest/dg/state-choice.html). El `Choice` state añade lógica condicional. Campos:

| Campo | Obligatoriedad | Función |
| --- | --- | --- |
| `Choices` | Requerido | Array de **Choice Rules** que determina el estado siguiente. Al menos una regla |
| `Default` | Opcional, **recomendado** | Estado al que transicionar si ninguna regla evalúa a `true` |

> **Aviso importante de la documentación**: si ninguna regla evalúa a `true` y no hay `Default`, la state machine **lanza un error** por no poder salir del estado. En un bucle de razonamiento esto es exactamente el fallo que no quieres: definir siempre `Default`.

Los `Choice` states **no soportan el campo `End`**, y usan `Next` solo dentro de `Choices`. Con JSONata, cada Choice Rule tiene un campo `Condition` (expresión JSONata que evalúa a true/false), `Next` (nombre de un estado) y opcionalmente `Assign` para asignar variables cuando esa regla concreta coincide:

```json
{
  "Type": "Choice",
  "Choices": [
    {
      "Condition": "{% $states.input.stopReason = 'tool_use' %}",
      "Next": "InvokeTool",
      "Assign": { "iteration": "{% $iteration + 1 %}" }
    },
    {
      "Condition": "{% $iteration >= 10 %}",
      "Next": "MaxIterationsFallback"
    }
  ],
  "Default": "ReturnFinalAnswer"
}
```

El `Assign` a nivel de regla y a nivel de estado son **mutuamente exclusivos en runtime**: si una regla coincide, Step Functions evalúa solo el `Assign` de esa regla; el `Assign` de nivel superior se evalúa únicamente cuando ninguna regla coincide y el workflow transiciona al `Default`. Es el mecanismo limpio para llevar el contador de iteraciones y el presupuesto de razonamiento sin estado externo.

### Los estados que construyen razonamiento estructurado

| Estado | Papel en el razonamiento |
| --- | --- |
| **`Task`** | Cada paso concreto: una llamada `Converse`, una invocación de herramienta, una consulta a knowledge base |
| **`Choice`** | Ramificación por el `stopReason` del modelo, por confianza, por presupuesto de iteraciones o por clasificación de riesgo |
| **`Map`** | Descomposición en paralelo: resolver N sub-preguntas independientes a la vez, o procesar N documentos |
| **`Parallel`** | Ramas heterogéneas simultáneas: consultar dos fuentes distintas y agregar, o ejecutar dos modelos y comparar |
| **`Wait`** | Esperas deliberadas: backoff explícito, ventanas de consistencia, polling de un job asíncrono |
| **`Pass`** | Transformar el estado entre pasos sin trabajo externo: acumular `messages`, normalizar la observación |
| **`Succeed` / `Fail`** | Terminación explícita, con causa y error nombrados |

`Pass` y `Wait` son los dos únicos estados que **no pueden encontrar errores de runtime**, según la documentación de manejo de errores. Todos los demás sí.

### Chain-of-thought: los mecanismos de la plataforma

Además de la orquestación, la plataforma ofrece palancas dentro de la propia inferencia, ya tratadas en [Task 1.6 · Skill 1.6.5](../domain-1/task-1-6-prompt-engineering-governance.md):

| Mecanismo | Dónde vive |
| --- | --- |
| Instrucciones de razonamiento paso a paso | La plantilla del prompt |
| `stopSequences` para separar razonamiento de respuesta final | `inferenceConfig` de `Converse` |
| **Query decomposition** de las knowledge bases | Configuración de `RetrieveAndGenerate`: descompone la pregunta compleja en sub-preguntas |
| Descomposición en nodos de un flow | Bedrock Flows, cada nodo un paso del razonamiento |
| Descomposición en estados de una state machine | Step Functions, con estado durable y trazas por paso |

La diferencia entre las dos últimas es de control y observabilidad: un flow es más rápido de construir; una state machine da historial de ejecución por paso, reintentos configurables por estado y esperas humanas. Para razonamiento que hay que auditar, Step Functions.

> Recordatorio de Guardrails relevante aquí: las salvaguardas actúan sobre entradas y respuestas **excluyendo los bloques de contenido de razonamiento**. Si el razonamiento intermedio se persiste o se muestra, necesita su propio control.

---

## Skill 2.1.3 — Workflows con salvaguardas y comportamiento controlado

> *Desarrollar workflows de IA con salvaguardas para asegurar comportamiento controlado del FM (por ejemplo, usando Step Functions para implementar stopping conditions, funciones Lambda para implementar mecanismos de timeout, políticas IAM para imponer fronteras de recursos, circuit breakers para mitigar fallos).*

### El marco: alineación de objetivos y prevención de manipulación

De [AGENTSEC04 — Agent goal alignment and manipulation prevention](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec04.html). El planteamiento oficial: un agente puede ser dirigido a perseguir objetivos no previstos o exhibir comportamientos fuera de su alcance definido. Sin mecanismos de alineación, puede tomar acciones que entran en conflicto con las políticas de la organización o con la intención del usuario.

La intención de capacidad del área de foco, que es directamente la estructura de este skill:

| Elemento | Qué exige |
| --- | --- |
| **Fronteras definidas por adelantado** | Los límites operativos y de política de cada agente se definen antes y se imponen con **controles en capas**, no solo con instrucciones de prompt |
| **Dos naturalezas de control, en etapas distintas** | Imposición **determinista** (scoping de IAM, validación de esquema de entrada, motores de política) y controles **probabilísticos** de contenido (filtrado de entrada y salida, evaluación de comportamiento) operan en etapas distintas de la cadena de llamada, para que el fallo de una capa rara vez produzca una violación de frontera |
| **Clasificación de riesgo determinista** | Las operaciones de alto riesgo se derivan a revisión humana antes de ejecutarse; las rutinarias de bajo riesgo proceden de forma autónoma |
| **Contexto suficiente para el revisor** | Los revisores reciben contexto de decisión, políticas de timeout y rutas de escalado para aprobar de forma informada, sin bloquear el workflow ni caer en aprobar por inercia |
| **Trazabilidad de las intervenciones** | Intervenciones de guardrail, decisiones de aprobación y resultados de evaluación se registran, se alertan y se revisan con cadencia definida |

**Los cinco problemas frecuentes** que señala el lens, cada uno un antipatrón reconocible:

1. Tratar la alineación como un ejercicio de prompt engineering en lugar de un problema de imposición en capas: una sola entrada adversaria que influya en el modelo puede colapsar varias fronteras a la vez.
2. Filtrar contenido **solo en la salida** del modelo, dejando la ruta de inferencia abierta a prompt injection y consumiendo capacidad en entradas adversarias que podrían haberse rechazado antes.
3. Un **único perfil de guardrail** para todos los agentes, que o sobre-restringe a los informativos de bajo riesgo o deja infra-restringidos a los operativos de alto riesgo.
4. Workflows de aprobación que o derivan **todas** las acciones a revisión humana (produciendo fatiga del revisor y aprobación por inercia) o se la saltan en operaciones que la merecen.
5. Delegar la **clasificación de riesgo a un LLM expuesto al mismo contenido no confiable** que la petición que evalúa, que puede ser influido para marcar esa petición como de bajo riesgo.

El quinto es el más sutil y el más probable como respuesta correcta en una pregunta de examen: el clasificador de riesgo no puede compartir superficie de ataque con lo que clasifica.

### Capa determinista 1: stopping conditions en Step Functions

Un agente sin condición de parada es un bucle infinito con factura. Los mecanismos:

| Mecanismo | Implementación |
| --- | --- |
| **Presupuesto de iteraciones** | Variable de contador incrementada con `Assign`, evaluada en un `Choice` con `Default` hacia un estado de fallback |
| **Presupuesto de tokens** | Acumular `usage.totalTokens` de cada respuesta `Converse` y cortar al superar el umbral |
| **Presupuesto de tiempo** | `TimeoutSeconds` a nivel de state machine y de `Task` |
| **Presupuesto de coste** | Acumular tokens por modelo y comparar con un límite por ejecución o por tenant |
| **Detección de no progreso** | Comparar la herramienta elegida y sus argumentos con los de iteraciones previas: repetición idéntica es señal de bucle |
| **Terminación explícita** | Estados `Fail` con `Error` y `Cause` nombrados, para que la causa sea legible en el historial |

### Capa determinista 2: timeouts

De [Handling errors in Step Functions workflows](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html). Todos los estados excepto `Pass` y `Wait` pueden encontrar errores de runtime, por problemas de definición (un `Choice` sin regla coincidente), fallos de tarea (una excepción en Lambda) o problemas transitorios (particiones de red). Ante un error, Step Functions **falla la ejecución completa por defecto**.

| Error | Cuándo se reporta |
| --- | --- |
| **`States.Timeout`** | Un `Task` corre más tiempo que `TimeoutSeconds`, o no envía heartbeat durante más de `HeartbeatSeconds`. También cuando la **ejecución completa** de la state machine excede su `TimeoutSeconds` |
| **`States.TaskFailed`** | Un `Task` falló. Como comodín en retry o catch, coincide con cualquier error conocido **excepto `States.Timeout`** |
| **`States.ALL`** | Comodín de cualquier error conocido. Debe aparecer **solo** en un catcher y **no puede** capturar `States.DataLimitExceeded` ni errores de runtime |
| **`States.DataLimitExceeded`** | Error **terminal** no capturable por `States.ALL`; solo capturable nombrándolo explícitamente en `ErrorEquals`. Se produce cuando la salida de un conector o de un estado, o la entrada tras procesar `Parameters`, excede la cuota de tamaño de payload |
| **`States.ExceedToleratedFailureThreshold`** | Un `Map` falló porque el número de items fallidos superó el umbral definido |
| **`Lambda.TooManyRequestsException`** | Lambda excedió el número máximo de invocaciones |

> Detalles de Lambda que la documentación marca explícitamente: los errores no manejados en runtimes de Lambda se reportaban históricamente solo como **`Lambda.Unknown`**; en runtimes más recientes los timeouts se reportan como **`Sandbox.Timedout`**. La recomendación oficial es hacer match en `Lambda.Unknown`, `Sandbox.Timedout` y `States.TaskFailed`. Y asegurar que el código de producción maneja `Lambda.ServiceException` y `Lambda.SdkClientException`.

**Los catchers no cubren fallos de ejecución de nivel superior.** Están disponibles para `Task`, `Parallel` y `Map`, pero no para el fallo de la state machine completa. Las tres alternativas que documenta AWS: que el llamante maneje el error, anidar esas ejecuciones en workflows hijos para capturar desde el padre, o escuchar eventos **`TIMED_OUT`** de workflows Standard con un bus de EventBridge e invocar una acción de manejo.

Los límites de Lambda, que son la otra mitad del mecanismo de timeout del skill, de [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html):

| Recurso | Cuota |
| --- | --- |
| **Timeout de función** | **900 segundos (15 minutos)**. Con AWS Lambda Managed Instances, las invocaciones asíncronas y de event source mapping (excepto Amazon MQ y DocumentDB) admiten hasta **5.400 segundos (90 minutos)** |
| Memoria | 128 MB a 10.240 MB en incrementos de 1 MB. La CPU se asigna **proporcionalmente a la memoria**: a 1.769 MB la función tiene el equivalente de una vCPU |
| Payload de invocación | 6 MB petición y 6 MB respuesta (sincrónico), **200 MB por respuesta en streaming** (sincrónico), 1 MB (asíncrono) |
| Ancho de banda de respuestas en streaming | Sin límite en los primeros 6 MB; **2 MB/s** para el resto |
| Ejecuciones concurrentes | 1.000 por defecto, ampliable a decenas de miles |
| Escalado de concurrencia | 1.000 entornos de ejecución cada 10 segundos por función |
| Imagen de contenedor | 10 GB descomprimida, incluidas todas las capas |

> El timeout de 15 minutos es la razón por la que un agente de razonamiento largo **no cabe en una Lambda**. Las tres salidas documentadas: Step Functions Standard (hasta 1 año), AgentCore Runtime (sesiones de hasta 8 horas, con soporte de ejecución extendida para agentes asíncronos) o ECS/Fargate para procesos sin límite de duración.

### Capa determinista 3: IAM como frontera de recursos

De [AGENTREL02 — Predictable task execution](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel02.html). El planteamiento: los agentes que acotan la estocasticidad del LLM mediante **diseño de tareas atómicas**, **permisos de least privilege** y **protocolos de instrucción claros** entregan resultados predecibles incluso cuando los modelos subyacentes son no deterministas.

La intención de capacidad, que se traduce en cinco best practices:

| Elemento | Best practice |
| --- | --- |
| Cada agente posee **una única capacidad atómica**, con validación explícita de entrada y esquema estructurado de salida, para que la estocasticidad quede acotada por contratos estrechos y testeables | AGENTREL02-BP01 |
| Cada agente opera dentro de un **envoltorio de permisos de least privilege** impuesto en las capas de identidad, política y control de acceso, para que una decisión inesperada del modelo afecte solo a los sistemas explícitamente autorizados | AGENTREL02-BP02 |
| Los agentes emiten **telemetría específica de agente** (prompts, llamadas a herramienta, accesos a memoria, calidad de salida) comparada contra baselines de comportamiento, para detectar drift y anomalías antes de que cascadeen | AGENTREL02-BP03 |
| Las instrucciones llegan mediante **plantillas de prompt canónicas**, configuración versionada y esquemas explícitos de handoff, para que la interpretación de objetivos sea consistente | AGENTREL02-BP04 |
| Las acciones se enrutan al **nivel apropiado de supervisión humana** según riesgo y reversibilidad, para que las decisiones de alta consecuencia reciban revisión sin añadir latencia al trabajo rutinario | AGENTREL02-BP05 |

Los niveles de madurez nombran servicios concretos, y son un mapa de implementación:

| Nivel | Qué se usa |
| --- | --- |
| **1 · Initial** | Agentes de propósito general con system prompts amplios y contratos de entrada/salida ambiguos. Permisos de grano grueso, logging genérico sin puntos de decisión del agente, prompts ad-hoc sin versionar, y la misma revisión humana para todo (o ninguna) |
| **2 · Emerging** | Workflows descompuestos en agentes de propósito único con esquemas de entrada y salida. **Un rol de ejecución IAM dedicado por agente**, AgentCore Observability capturando telemetría por agente, plantillas de prompt en documentación compartida |
| **3 · Defined** | Agentes atómicos en **AgentCore Runtime** con imposición de **structured output** y validación periódica con **AgentCore Evaluations**. Acceso restringido con **AgentCore Identity** y políticas IAM por agente. Baselines de comportamiento que alimentan alertas de **CloudWatch Anomaly Detection**, plantillas versionadas, y un framework de riesgo documentado que enruta acciones a tiers **autonomous, notify y approve** |
| **4 · Proactive** | Fronteras de acceso impuestas con **AgentCore Policy y políticas Cedar en el gateway**, y **Bedrock Guardrails** interceptando salidas que violan política antes de escalar a revisores humanos. Comparación de versiones de prompt con AgentCore Evaluations antes de migrar tráfico, **IAM Access Analyzer** guiando remediaciones de least privilege a partir de datos de **CloudTrail**, y workflows de aprobación con timeouts, rutas de escalado y contexto de auditoría completo |
| **5 · Optimized** | Recalibración continua desde datos de observabilidad. Respuestas automatizadas que **ponen en cuarentena agentes anómalos**, y **tests adversarios de contrato que bloquean regresiones de prompt injection en CI/CD** |

**Problemas frecuentes** de esta área: agentes que acumulan responsabilidades amplias y solapadas con el tiempo, de modo que una sola mala interpretación afecta a varias capacidades; roles de ejecución IAM y fronteras de política escritos **con wildcards o por conveniencia del primer despliegue**, de modo que el alcance de impacto de cualquier acción no prevista es más ancho que la función legítima del agente; monitorización que captura señales de infraestructura pero no puntos de decisión del agente, dejando invisible el drift de comportamiento (salidas más largas, más llamadas a herramienta, cambios en la distribución de salida) hasta que produce un fallo visible.

Traducido a controles concretos de IAM:

| Control | Aplicación en un agente |
| --- | --- |
| **Rol de ejecución por agente** | Nunca un rol compartido: el alcance de impacto de una decisión inesperada queda acotado al agente |
| **Permisos de acción concretos** | `bedrock:InvokeModel` limitado a los ARN de modelo aprobados; `bedrock:Retrieve` limitado a las knowledge bases del dominio del agente |
| **Condiciones de política** | Claves de condición para restringir Región, tags de recurso o valores de petición |
| **Permissions boundaries** | Techo máximo de permisos que el agente no puede exceder aunque su política de identidad se amplíe |
| **ABAC con tags** | Acceso condicionado a que los tags del principal coincidan con los del recurso, útil para aislamiento por tenant |
| **IAM Access Analyzer** | Generar políticas de least privilege a partir de la actividad real registrada en CloudTrail, y detectar acceso externo no previsto |

### Capa determinista 4: AgentCore Policy, imposición fuera del código del agente

De [Policy in Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html). Permite definir e imponer controles de seguridad para las interacciones del agente con herramientas, creando una **frontera protectora alrededor de las operaciones del agente**. El razonamiento oficial: la flexibilidad de los agentes introduce retos de seguridad nuevos, porque pueden malinterpretar reglas de negocio o actuar fuera de su autoridad prevista.

**Cómo funciona**: se crean *policy engines*, se almacenan en ellos políticas deterministas y se asocian los engines a *gateways*. Policy **intercepta todo el tráfico del agente que pasa por AgentCore Gateway** y evalúa cada petición contra las políticas definidas **antes de permitir el acceso a la herramienta**.

| Beneficio clave | Qué aporta |
| --- | --- |
| **Control fino sobre las acciones** | Definir qué acciones puede realizar el agente, qué herramientas puede llamar y bajo qué condiciones precisas |
| **Imposición determinista** | Cada acción se intercepta y evalúa **en la frontera, fuera del código del agente**, con lo que la imposición es consistente independientemente de cómo esté implementado el agente |
| **Autoría accesible con consistencia organizacional** | Políticas en lenguaje natural o directamente en **Cedar**. Los equipos fijan las fronteras una vez y se aplican de forma consistente a todos los agentes y herramientas, con **cada decisión de imposición registrada en métricas y logs de CloudWatch** |

Lenguajes de autoría soportados:

- **Cedar**, el lenguaje open source de AWS para políticas de autorización de grano fino.
- **Lenguaje natural**: se describe la regla en inglés llano; el servicio interpreta la intención, **genera políticas candidatas, las valida contra el esquema de la herramienta y aplica automated reasoning** para comprobar condiciones de seguridad, identificando políticas demasiado permisivas, demasiado restrictivas o con condiciones imposibles de satisfacer, antes de imponerlas.
- **Dogwood**, lenguaje de política open source en el que una sola política puede combinar varios tipos de condición de autorización.

Los tres tipos de condición que compone una política Dogwood, que dan la medida de lo que se puede expresar:

| Tipo de condición | Qué evalúa | Ejemplo oficial |
| --- | --- | --- |
| **Input-based** | La petición actual: quién es el principal, qué herramienta llama, qué recurso está implicado y los parámetros de entrada de esa llamada | Permitir o prohibir una llamada de herramienta según sus argumentos |
| **Temporal, session-aware** | Lo que ya ocurrió antes en la misma sesión | Exigir que se haya concedido una aprobación antes de una transferencia; bloquear una acción tras ejecutarse N veces; mantener un total acumulado bajo un presupuesto |
| **Provider-based** | Señales emitidas en tiempo de evaluación por *information providers*, como Guardrails | Decidir según un score de seguridad de contenido o de prompt attack |

Porque los tres tipos componen dentro de una sola política bajo el mismo modelo `permit` / `forbid`, se pueden apilar para expresar desde una regla de acceso simple hasta una salvaguarda multi-paso consciente de la sesión.

Otras capacidades listadas: integración con **security groups de VPC** y demás infraestructura de seguridad de AWS, **audit logging** detallado de decisiones de política, y **temporal policies** con reglas de alcance de sesión que razonan sobre el histórico de acciones de una conversación.

> El valor arquitectónico que subraya la documentación: **mover los controles de seguridad fuera del código del agente** elimina la necesidad de implementaciones de seguridad propias y reduce el riesgo de **bypass de política por manipulación del agente**. Es la misma lógica que separa Guardrails del prompt en [Task 1.6 · Skill 1.6.1](../domain-1/task-1-6-prompt-engineering-governance.md): lo que el modelo puede ignorar frente a lo que se impone externamente.

### Capa probabilística: Guardrails en la cadena del agente

Los seis tipos de salvaguarda de [Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) están detallados en [Task 1.6 · Skill 1.6.1](../domain-1/task-1-6-prompt-engineering-governance.md). Lo específico de un workflow agentic:

| Punto de la cadena | Control |
| --- | --- |
| Entrada del usuario | Content filters y denied topics, con [tagging de entrada de usuario](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-tagging.html) para evaluar solo lo que escribió el usuario y no las instrucciones de sistema ni los resultados de herramienta |
| Antes de cada llamada de herramienta | AgentCore Policy (determinista) más validación de esquema de los argumentos |
| Resultado de la herramienta | Tratar la salida de la herramienta como **contenido no confiable**: puede traer prompt injection indirecta |
| Respuesta final | Contextual grounding checks y automated reasoning checks |
| Independiente del modelo | La API **`ApplyGuardrail`**, que evalúa contenido sin invocar ningún FM, útil para validar resultados de herramienta en un paso propio del workflow |

### Circuit breaker y degradación elegante

El patrón de circuit breaker sobre Step Functions ya está descrito en [Task 1.2 · Skill 1.2.3](../domain-1/task-1-2-seleccion-y-configuracion-fm.md). Lo que añade el contexto agentic es que el disyuntor protege **cada herramienta**, no solo el modelo:

```
                    ┌──────────────────────────────────────┐
                    │  Estado del disyuntor por herramienta │
                    │  DynamoDB: toolId → estado, fallos,   │
                    │            ventana, abiertoHasta      │
                    └──────────────────────────────────────┘
                                    ▲
                                    │ lectura / escritura
   Task: invocar herramienta        │
        │                           │
        ▼                           │
   ┌─────────────────────────────────────────────┐
   │ Choice: ¿disyuntor CERRADO?                 │
   │   abierto ──► saltar herramienta            │
   │               · devolver toolResult de error│
   │                 al modelo, con explicación  │
   │               · o activar la cadena de      │
   │                 fallback (AGENTREL04-BP03)  │
   └─────────────────────────────────────────────┘
        │ cerrado
        ▼
   ┌─────────────────────────────────────────────┐
   │ Task: Lambda de la herramienta              │
   │   TimeoutSeconds: acotar la espera          │
   │   Retry: ErrorEquals + IntervalSeconds      │
   │          + BackoffRate + MaxDelaySeconds    │
   │          + JitterStrategy: FULL             │
   │   Catch: States.ALL ──► registrar fallo     │
   └─────────────────────────────────────────────┘
        │ éxito                    │ fallo tras reintentos
        ▼                          ▼
   reset del contador       incrementar contador
                            ¿supera umbral? ──► ABRIR disyuntor
                                                (abiertoHasta = ahora + cooldown)
```

Los parámetros del campo `Retry` de Step Functions, que son la base del backoff, de [Handling errors](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html):

| Campo | Obligatoriedad | Valor por defecto | Función |
| --- | --- | --- | --- |
| `ErrorEquals` | **Requerido** | — | Array no vacío de nombres de error que activan este retrier |
| `IntervalSeconds` | Opcional | **1** | Segundos antes del primer reintento. Máximo 99.999.999 |
| `MaxAttempts` | Opcional | **3** | Máximo de reintentos. `0` significa no reintentar nunca. Máximo 99.999.999 |
| `BackoffRate` | Opcional | **2.0** | Multiplicador por el que crece el intervalo en cada reintento |
| `MaxDelaySeconds` | Opcional | Sin límite | Techo del intervalo de reintento, para acotar el crecimiento exponencial. Mayor que 0 y menor que 31.622.401 |
| `JitterStrategy` | Opcional | **`NONE`** | `FULL` o `NONE`. Con `FULL`, cada intervalo se randomiza entre 0 y el valor calculado, repartiendo los reintentos simultáneos |

Ejemplo oficial de la combinación que interesa en un agente, con techo de espera y jitter:

```json
"Retry": [
  {
    "ErrorEquals": ["States.Timeout"],
    "IntervalSeconds": 3,
    "MaxAttempts": 3,
    "BackoffRate": 2,
    "MaxDelaySeconds": 5,
    "JitterStrategy": "FULL"
  }
]
```

Sin `MaxDelaySeconds`, el segundo reintento ocurriría 6 segundos después del primero y el tercero 12 segundos después del segundo. Con el techo en 5, los reintentos segundo y tercero esperan 5 segundos. `JitterStrategy: FULL` randomiza cada intervalo entre 0 y su valor, que es lo que evita que todos los clientes reintenten a la vez tras una incidencia.

Un patrón útil que documenta AWS: **reintentar todo excepto un error concreto**, aprovechando que `States.ALL` debe ir solo y en el último retrier:

```json
"Retry": [
  { "ErrorEquals": ["States.Timeout"], "MaxAttempts": 0 },
  { "ErrorEquals": ["States.ALL"] }
]
```

**Health checking proactivo**: el lens recomienda en AGENTREL04 nivel 4 usar el endpoint **`/ping` de AgentCore Runtime** para activar el fallback sin esperar a que se cumplan los timeouts. Es la diferencia entre un disyuntor reactivo (abre tras N fallos observados) y uno proactivo (abre porque la sonda ya detectó que el destino no está sano).

**Validación de las cadenas de fallback**: el mismo nivel recomienda **AWS Fault Injection Service** para ejercitar las cadenas de fallback de forma programada, precisamente porque el problema frecuente que señala el lens es que las cadenas existen pero nunca se prueban, y sus huecos se descubren en incidentes de producción.

### Resumen: las capas de salvaguarda de un workflow agentic

```
Capa 1 · Alcance         → una capacidad atómica por agente (AGENTREL02-BP01)
                            contrato de entrada validado + structured output
Capa 2 · Identidad       → rol de ejecución IAM propio, permissions boundary
                            AgentCore Identity para autenticación del agente
Capa 3 · Política        → AgentCore Policy (Cedar) en el Gateway:
                            intercepta CADA tool call antes de ejecutarla
                            condiciones input-based + temporales + de provider
Capa 4 · Presupuestos    → stopping conditions en Step Functions:
                            iteraciones, tokens, tiempo, coste, no progreso
Capa 5 · Timeouts        → TimeoutSeconds y HeartbeatSeconds por Task
                            TimeoutSeconds de la ejecución completa
                            15 min de techo en Lambda como restricción de diseño
Capa 6 · Resiliencia     → Retry con BackoffRate, MaxDelaySeconds y jitter FULL
                            Catch por estado + circuit breaker por herramienta
                            cadenas de fallback ordenadas (AGENTREL04-BP03)
Capa 7 · Contenido       → Guardrails en entrada, en resultado de herramienta
                            y en salida; ApplyGuardrail como paso independiente
Capa 8 · Supervisión     → tiers autonomous / notify / approve por riesgo
                            y reversibilidad (AGENTREL02-BP05, Skill 2.1.5)
Capa 9 · Observación     → telemetría por agente contra baselines
                            CloudWatch Anomaly Detection, cuarentena automática
```

Las capas 1 a 6 y 8 son **deterministas**; la 7 es **probabilística**; la 9 es **detectiva**. La tesis del lens es exactamente esa distribución: que el fallo de una capa rara vez produzca una violación de frontera.

---

## Skill 2.1.4 — Coordinación de modelos y optimización entre capacidades

> *Crear sistemas sofisticados de coordinación de modelos para optimizar el rendimiento entre múltiples capacidades (por ejemplo, usando FMs especializados para realizar tareas complejas, lógica de agregación personalizada para ensembles de modelos, frameworks de selección de modelo).*

### El marco: optimizar el cognitive pipeline

De [AGENTPERF02 — Core processing and reasoning pipeline optimization](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentperf02.html). El planteamiento oficial es directo: el reasoning pipeline (percepción, razonamiento, planificación, toma de decisiones y ejecución de acciones) es la **ruta crítica de rendimiento** de todo sistema agentic. Cada iteración del agent loop implica una llamada de inferencia, que suele ser la operación más intensiva en latencia y recursos de toda la pila. Un pipeline mal diseñado produce agentes lentos, caros y poco responsivos **independientemente de cómo esté aprovisionada la infraestructura subyacente**.

La intención de capacidad del área de foco:

| Elemento | Qué exige |
| --- | --- |
| **Acotar el razonamiento** | Iteration caps y terminación temprana basada en confianza, para que las tareas simples se resuelvan en una o dos iteraciones y las complejas reciban las que necesiten |
| **Routing al modelo más pequeño suficiente** | Cada clase de tarea se enruta al **modelo más pequeño que cumple su barra de calidad**, con fallback en cascada a un modelo más capaz cuando el asignado produce salidas de baja confianza |
| **Concurrencia y reutilización** | Las operaciones independientes se ejecutan concurrentemente, las conexiones y runtimes están calientes entre invocaciones, y las búsquedas repetidas dentro de una misma petición se deduplican con cachés de alcance de petición |
| **Streaming con TTFT sub-segundo** | Los agentes de cara al usuario hacen streaming de tokens con **time-to-first-token por debajo del segundo**, el trabajo previo a la inferencia se comprime para preservar el presupuesto de TTFT, y las invocaciones de herramienta a mitad de stream **muestran progreso** en lugar de pausas inexplicadas |
| **Presupuestos de latencia explícitos** | Las estrategias de reintento y las rutas de degradación están acotadas por presupuestos de latencia, para que la recuperación de fallos se mantenga dentro del SLO end-to-end en lugar de erosionarlo en silencio |

**Los cinco problemas frecuentes**, todos reconocibles como distractores:

1. Agentes que razonan **sin iteration caps ni señales de terminación temprana**, produciendo bucles descontrolados que consumen tokens y tiempo sin mejorar la calidad.
2. **Un único modelo grande para todas las tareas**, pagando el sobrecoste de latencia y dinero de un modelo pesado para trabajo que uno pequeño resuelve igual de bien.
3. Operaciones independientes **ejecutadas en secuencia** y conexiones reestablecidas en cada invocación, de modo que la latencia end-to-end es la suma de todas las duraciones más el setup repetido.
4. Agentes que **esperan la respuesta completa** antes de emitir nada, con lo que la latencia percibida iguala el tiempo total de procesado en lugar del TTFT más corto que daría el streaming.
5. Invocaciones de herramienta a mitad de stream que **pausan la salida sin progreso visible**, creando la sensación de cuelgue: salida parcial seguida de silencio durante segundos.

### El marco de coste: right-sizing del modelo

De [AGENTCOST02 — Model invocation and token cost optimization](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentcost02.html). Los costes de FM pueden dominar el presupuesto de un sistema agentic, con agentes que invocan modelos caros para tareas simples o consumen tokens en exceso con razonamiento verboso.

| Elemento de la intención | Qué exige |
| --- | --- |
| **Selección por complejidad** | Clasificación y formateo rutinarios en modelos coste-eficientes; modelos premium reservados para razonamiento que realmente los necesita |
| **Tamaño mínimo de prompt** | Prompts, descripciones de herramienta y restricciones de salida al mínimo necesario para mantener la calidad de decisión, a lo largo de las fases de planificación, ejecución y reflexión |
| **Cachés en lugar de regeneración** | Razonamiento repetido y contexto estable se sirven de caché, para que peticiones equivalentes no paguen dos veces el coste completo de inferencia |
| **Especialización donde amortiza** | Tareas recurrentes de alto volumen en modelos especializados o personalizados, cuyo coste único de entrenamiento amortiza contra el ahorro sostenido por invocación |
| **Métricas por tier** | Cost-per-correct-response, consumo de tokens, cache hit rate y **cascade escalation rate** medidos por tier de modelo y realimentados a las decisiones de routing, caché y customización |

**Problemas frecuentes** de coste: prompts de sistema y catálogos de herramientas que **crecen sin revisión**, de modo que el impuesto fijo de input tokens que se paga en cada invocación sube en silencio aunque el tráfico sea plano; caché tratada como activación puntual y no como disciplina continua, con políticas de invalidación obsoletas o umbrales de similitud débiles que erosionan el hit rate sin que nadie lo note; customización de modelo perseguida en cargas de bajo volumen donde el coste de entrenamiento **nunca amortiza**; y señales de coste solo agregadas, que impiden ver qué tier, qué fase de razonamiento o qué capa de caché impulsa el gasto.

### Frameworks de selección de modelo

Las opciones que documenta AWS, de menos a más dinámicas:

| Framework | Mecanismo | Cuándo |
| --- | --- | --- |
| **Selección en diseño** | El `modelId` fijado en el código o en un parámetro | Un solo caso de uso, sin variación de complejidad. El nivel 2 de madurez de AGENTPERF02 lo marca como insuficiente: la selección debería estar *benchmarked* contra la distribución real de tareas |
| **Configuración externalizada** | **AWS AppConfig** con despliegues progresivos gobernados por alarmas de CloudWatch (nivel 4 de AGENTPERF02) | Cambiar de modelo sin desplegar código. Base en [Task 1.2 · Skill 1.2.2](../domain-1/task-1-2-seleccion-y-configuracion-fm.md) |
| **Pre-clasificador** | Un modelo pequeño clasifica la complejidad y enruta al tier adecuado (nivel 3 de AGENTCOST02) | Distribución de tareas heterogénea, con mayoría de casos simples |
| **Intelligent prompt routing** | [Understanding intelligent prompt routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html), gestionado por Bedrock | Enrutar entre modelos de una misma familia sin construir el clasificador |
| **Application inference profiles** | [Inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html), con tags para atribuir coste y uso | Trazabilidad por aplicación, equipo o entorno, y cross-Region |
| **Model cascading** | Empezar por el modelo pequeño y **escalar solo ante baja confianza** | El patrón por defecto que recomienda AGENTCOST02 nivel 3 para razonamiento no trivial. Detalle en [Skill 2.2.3](./task-2-2-despliegue-de-modelos.md#skill-223--despliegue-optimizado-y-model-cascading) |
| **Routing por métricas** | Decidir según latencia observada, tasa de error o saturación de cuota | Optimización operativa. Detalle en [Skill 2.4.4](./task-2-4-integraciones-api-fm.md#skill-244--routing-inteligente-de-modelos) |

### FMs especializados y lógica de agregación

El skill nombra tres cosas distintas que conviene no mezclar:

| Patrón | Cómo funciona | Qué aporta |
| --- | --- | --- |
| **FMs especializados por capacidad** | Cada subtarea va al modelo que mejor la hace: un modelo multimodal para la imagen, un modelo de embeddings para la búsqueda, un reranker para ordenar, un modelo de razonamiento para la síntesis | Calidad por tarea, sin pagar el modelo grande en todos los pasos. Base de embeddings y reranking en [Task 1.5](../domain-1/task-1-5-retrieval.md) |
| **Ensemble con agregación** | Varios modelos responden **la misma** pregunta y una lógica propia combina los resultados: voto mayoritario, media ponderada por confianza, o un modelo árbitro que elige | Reduce el efecto de la estocasticidad individual. El precio es multiplicar el coste y la latencia por el número de modelos |
| **Cascada** | Un modelo responde; solo si la confianza es baja se escala al siguiente | Coste medio bajo con techo de calidad alto. No mejora la varianza, la acota por abajo |

Implementación de la agregación sobre los servicios documentados:

```
                        ┌──────────────────────────┐
                   ┌───►│ Task: FM A (Converse)    │───┐
                   │    └──────────────────────────┘   │
Parallel state ────┤                                   ├──► Lambda de agregación
                   │    ┌──────────────────────────┐   │      · voto mayoritario
                   └───►│ Task: FM B (Converse)    │───┘      · media ponderada
                        └──────────────────────────┘          · árbitro LLM
                                                                   │
                                                                   ▼
                                                        structured output valida
                                                        el esquema del resultado
```

El `Parallel` state de Step Functions ejecuta las ramas simultáneamente y entrega la salida de todas a la Lambda de agregación. Dos avisos operativos de la documentación de Step Functions aplican aquí: si una rama de un `Parallel` falla con un error no capturado, **las tareas de las otras ramas pueden abortarse**, y con integraciones `.sync` un aborto puede dejar cargos del servicio integrado; y la salida combinada de las ramas cuenta contra la cuota de tamaño de payload, que al excederse produce `States.DataLimitExceeded`, un **error terminal** que `States.ALL` no captura.

Para que la agregación sea fiable, la salida de cada modelo debe ser parseable: [structured output](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html) devuelve JSON validado contra esquema, lo que convierte la agregación en comparación de campos en lugar de parsing de texto libre.

### El arbiter pattern como coordinación de modelos

Cuando la coordinación es entre agentes y no solo entre modelos, el patrón oficial es el **arbiter** de [AGENTREL04-BP01](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel04.html), ya descrito en el Skill 2.1.1: un árbitro dedicado concentra la resolución de conflictos y actúa **solo cuando hace falta coordinación**, y en el nivel de madurez 4 es **event-driven con EventBridge**, activándose para resolver conflictos en lugar de mediar cada mensaje.

La diferencia con un ensemble es de propósito: el ensemble agrega respuestas a la misma pregunta; el árbitro resuelve desacuerdos entre agentes que trabajan en partes distintas del problema y compiten por un recurso o llegan a conclusiones incompatibles.

---

## Skill 2.1.5 — Sistemas colaborativos con expertise humana

> *Desarrollar sistemas de IA colaborativos para enriquecer las capacidades del FM con expertise humana (por ejemplo, usando Step Functions para orquestar procesos de revisión y aprobación, API Gateway para implementar mecanismos de recogida de feedback, patrones de human augmentation).*

### El marco: supervisión escalonada, no uniforme

De [AGENTREL02-BP05 — Establish tiered human oversight and approval workflows](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel02-bp05.html). La tesis en una frase: la supervisión uniforme **o ralentiza cada acción rutinaria o deja pasar sin control una decisión de alta consecuencia**. Escalonar la revisión según el riesgo y la reversibilidad de cada acción equilibra throughput y governance.

**Nivel de riesgo si no se establece esta best practice: alto.**

**Resultado deseado**, según la documentación:

- Acciones del agente clasificadas en tiers (**autonomous, notify y approve**) según impacto y reversibilidad.
- Una **capa automatizada de primera pasada** que filtra las acciones que violan política antes de que las vean los revisores humanos.
- Cada decisión de supervisión registrada con **identidad del revisor, justificación y timestamp** para reporting de compliance y governance.

**Los tres antipatrones que nombra**:

1. Aplicar supervisión uniforme sin considerar el riesgo, creando cuellos de botella en tareas rutinarias o dejando pasar sin control acciones de alta consecuencia.
2. Omitir criterios claros de escalado, de modo que algunas acciones de alto riesgo proceden de forma autónoma mientras algunas de bajo riesgo hacen cola para revisión.
3. Ejecutar workflows de aprobación **sin timeouts ni fallback**, lo que hace que los agentes se queden colgados indefinidamente cuando los revisores no están disponibles.

### Los tres tiers de riesgo

| Tier | Perfil de la acción | Comportamiento |
| --- | --- | --- |
| **Autonomous** | Bajo riesgo y **reversible** | Se ejecuta sin intervención |
| **Notify** | Riesgo medio | Procede, pero con conocimiento del operador |
| **Approve** | Alto riesgo o **irreversible** | Requiere aprobación humana explícita |

> El criterio de clasificación son **dos ejes: impacto y reversibilidad**. Una acción de impacto alto pero trivialmente reversible no es lo mismo que una de impacto medio e irreversible. Esa distinción es el corazón del skill.

### Los cinco pasos de implementación

De la guía oficial de implementación:

**1. Definir el framework de clasificación de riesgo.** Categorizar las acciones en los tres tiers según impacto y reversibilidad, y **codificar la clasificación como políticas Cedar en [AgentCore Policy](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html)**, para que la imposición del tier ocurra en la frontera del gateway antes de que el agente pueda ejecutar. El razonamiento oficial: la imposición basada en política aplica la clasificación **en tiempo de ejecución**, en lugar de confiar solo en documentación de referencia.

**2. Configurar Guardrails como capa automatizada de primera pasada.** [Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) intercepta las salidas del agente antes de que lleguen a los revisores, filtrando contenido que viola políticas predefinidas. La frase clave: lo que llega a la cola humana deberían ser **los casos genuinamente ambiguos**, con las violaciones de política filtradas automáticamente.

**3. Construir workflows de aprobación estructurados.** No basta una pausa. La petición de revisión debe incluir cuatro elementos:

| Elemento | Por qué |
| --- | --- |
| **Descripción de la acción** | Qué se va a hacer |
| **Razonamiento del agente** | Por qué el agente lo propone |
| **Evaluación de impacto** | Qué consecuencias tiene |
| **Historial de ejecución** | Qué ocurrió antes en esta ejecución |

El objetivo declarado es que el revisor pueda **decidir rápido**, que es la contramedida contra la aprobación por inercia.

**4. Configurar timeouts y rutas de escalado.** Manejar la indisponibilidad del revisor sin bloquear indefinidamente, con escalado a revisores secundarios o **fallback a valores por defecto seguros**.

**5. Registrar cada decisión de supervisión.** Identidad del revisor, justificación y timestamp, para que la pista de auditoría soporte compliance y governance. Y **monitorizar la profundidad de la cola de aprobación con CloudWatch** para detectar cuándo las revisiones se están acumulando.

### Implementación: el patrón waitForTaskToken

De [Discover service integration patterns in Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html). Step Functions ofrece tres patrones de integración, controlados por cómo se construye el URI del campo `Resource`:

| Patrón | Sufijo | Comportamiento |
| --- | --- | --- |
| **Request Response** | ninguno | Llama al servicio y avanza al estado siguiente **inmediatamente tras recibir la respuesta HTTP**. No espera a que el trabajo termine |
| **Run a Job** | `.sync` | Llama al servicio y **espera a que el job se complete** antes de avanzar |
| **Wait for Callback** | `.waitForTaskToken` | Llama al servicio con un **task token** y espera hasta que ese token se devuelve con un payload |

> **Restricción decisiva para este skill**: los workflows **Standard y Express soportan las mismas integraciones, pero no los mismos patrones de integración**. Express **solo soporta Request Response**. `.waitForTaskToken` y `.sync` son exclusivos de Standard. Un workflow de aprobación humana **no puede** construirse sobre Express.

Soporte de `waitForTaskToken` en las integraciones relevantes:

| Servicio integrado | Request Response | `.sync` | `.waitForTaskToken` |
| --- | --- | --- | --- |
| Más de doscientos servicios vía **AWS SDK integrations** | Standard y Express | No soportado | **Standard** |
| **Amazon API Gateway** | Standard y Express | No soportado | **Standard** |
| **Amazon Bedrock** | Standard y Express | Standard | **Standard** |
| **Amazon Bedrock AgentCore** | Standard y Express | No soportado | No soportado |
| Amazon Athena | Standard y Express | Standard | No soportado |
| AWS Batch | Standard y Express | Standard | No soportado |

Dos datos de esta tabla merecen atención: **Bedrock soporta los tres patrones** en Standard, y **AgentCore solo soporta Request Response**, lo que significa que una espera humana alrededor de una invocación de AgentCore se construye en el workflow que la envuelve, no en la integración.

**Heartbeat para no colgarse indefinidamente**: de [Configure a Heartbeat Timeout for a Waiting Task](https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html), se establece `HeartbeatSeconds` en el `Task` que espera el callback. Si no llega un task token válido dentro del intervalo, se reporta **`States.Timeout`**. Es la implementación literal del paso 4 de la best practice: el timeout que evita el bloqueo indefinido.

El token se devuelve con **`SendTaskSuccess`** (aprobación) o **`SendTaskFailure`** (rechazo o fallo), que reanudan la ejecución pausada.

### Arquitectura de un workflow de aprobación escalonada

```
Acción propuesta por el agente
   │
   ▼
┌───────────────────────────────────────────────────────────────┐
│ AgentCore Policy (Cedar) en el Gateway                        │  ← paso 1
│   Clasifica el tier por impacto y reversibilidad              │
│   permit / forbid ANTES de que el agente ejecute              │
└───────────────────────────────────────────────────────────────┘
   │
   ├─ tier autonomous ──────────────────────────► ejecutar
   │
   ├─ tier notify ──► SNS / EventBridge al operador ──► ejecutar
   │
   └─ tier approve
        │
        ▼
   ┌────────────────────────────────────────────────────────────┐
   │ Guardrails / ApplyGuardrail: primera pasada automatizada   │  ← paso 2
   │   Filtra violaciones de política antes de la cola humana   │
   └────────────────────────────────────────────────────────────┘
        │ pasa el filtro
        ▼
   ┌────────────────────────────────────────────────────────────┐
   │ Persistir el contexto de decisión en DynamoDB              │  ← paso 3
   │   · descripción de la acción                               │
   │   · razonamiento del agente                                │
   │   · evaluación de impacto                                  │
   │   · historial de ejecución                                 │
   │   (AGENTSEC04 nivel 4: escribir a almacenamiento durable   │
   │    ANTES de notificar al revisor)                          │
   └────────────────────────────────────────────────────────────┘
        │
        ▼
   ┌────────────────────────────────────────────────────────────┐
   │ Task con .waitForTaskToken  (solo Standard)                │
   │   HeartbeatSeconds: techo de espera ──► States.Timeout     │  ← paso 4
   │   Notificación al revisor: SNS, Lambda, API Gateway        │
   └────────────────────────────────────────────────────────────┘
        │
        ├─ SendTaskSuccess ──► ejecutar la acción
        ├─ SendTaskFailure ──► rechazo registrado, no se ejecuta
        └─ States.Timeout  ──► Choice: escalar a revisor secundario
                                       o fallback a default seguro
        │
        ▼
   ┌────────────────────────────────────────────────────────────┐
   │ Registrar la decisión: revisor, justificación, timestamp   │  ← paso 5
   │ CloudWatch: profundidad de la cola de aprobación           │
   └────────────────────────────────────────────────────────────┘
```

### Recogida de feedback con API Gateway

El skill nombra API Gateway explícitamente para los mecanismos de recogida de feedback. Los dos usos que soporta la arquitectura anterior:

| Uso | Cómo |
| --- | --- |
| **Endpoint de decisión del revisor** | La interfaz de revisión llama a API Gateway, que invoca una Lambda que ejecuta `SendTaskSuccess` o `SendTaskFailure` con el task token. API Gateway soporta `.waitForTaskToken` en Standard, de modo que también puede ser el propio destino del `Task` |
| **Endpoint de feedback del usuario final** | Recoger pulgar arriba/abajo y comentarios sobre las respuestas del agente, persistirlos y alimentar el set de evaluación |

El feedback de usuario cierra el bucle que el Generative AI Lens describe en mejora continua, y alimenta lo cubierto en [Task 1.6 · Skill 1.6.4](../domain-1/task-1-6-prompt-engineering-governance.md): las respuestas marcadas como malas son los casos de regresión del set de pruebas.

### Human augmentation: Amazon Augmented AI

De [Using Amazon Augmented AI for Human Review](https://docs.aws.amazon.com/sagemaker/latest/dg/a2i-use-augmented-ai-a2i-human-review-loops.html). Amazon A2I lleva la revisión humana de predicciones de ML a los desarrolladores, eliminando el trabajo pesado de construir sistemas de revisión o gestionar grandes grupos de revisores. Ofrece workflows de revisión integrados para casos comunes (moderación de contenido, extracción de texto de documentos) y permite crear los propios para modelos en SageMaker AI o cualquier otra herramienta.

El patrón que implementa: permitir que los revisores humanos intervengan **cuando el modelo no puede hacer una predicción de alta confianza**, o auditar sus predicciones de forma continua. Los dos disparadores documentados son **baja confianza** y **muestreo aleatorio**.

| Componente de A2I | Función |
| --- | --- |
| **Human review workflow** (flow definition) | Define el workflow: quién revisa, con qué plantilla y con qué condiciones de activación |
| **Human loop** | Una instancia concreta de revisión, creada y arrancada cuando se cumple la condición |
| **Worker task template** | La interfaz que ve el revisor |
| **Output data** | El resultado de la revisión, en S3, utilizable para reentrenar de forma incremental |

Integraciones documentadas: Amazon Textract (pares clave-valor importantes), Amazon Rekognition (imágenes con score bajo), endpoints de SageMaker AI (inferencias en tiempo real de baja confianza, con reentrenamiento incremental a partir de los datos de salida de A2I), Amazon Comprehend, Amazon Transcribe (cuyas revisiones alimentan un vocabulario personalizado), Amazon Translate y datos tabulares. Eventos de CloudWatch y APIs propias completan la integración.

> **Aviso de estado del servicio**: la documentación oficial indica que **Amazon SageMaker A2I ya no está abierto a clientes nuevos**. Los clientes existentes pueden seguir usándolo con normalidad y AWS continúa invirtiendo en mejoras de seguridad y disponibilidad, pero **no hay planes de introducir funcionalidades nuevas**. A2I sigue apareciendo en la lista de [In-Scope AWS Services](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html) del examen, así que conviene conocer el patrón y el vocabulario, y saber que para construir hoy el mecanismo de human-in-the-loop de un agente el camino documentado es el de AGENTREL02-BP05: AgentCore Policy para clasificar, Guardrails como primera pasada y Step Functions con `waitForTaskToken` para la espera. Registrado en [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación).

### Proteger el propio mecanismo de supervisión

El área de foco **AGENTSEC07** del lens cubre *proteger el oversight humano y detectar agentes rogue*, y aparece en la ruta de lectura de "endurecer un despliegue existente". La idea que aporta: el mecanismo de supervisión es él mismo una superficie de ataque. Si un agente puede influir en la clasificación de riesgo, el tier `approve` deja de significar nada. De ahí el quinto problema frecuente de [AGENTSEC04](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec04.html): no delegar la clasificación de riesgo a un LLM expuesto al mismo contenido no confiable que la petición que evalúa.

La contramedida documentada es que la clasificación sea **determinista y externa**: políticas Cedar en AgentCore Policy, evaluadas en la frontera del gateway, fuera del código y del contexto del agente.

---

## Skill 2.1.6 — Integraciones de herramientas y operaciones fiables

> *Implementar integraciones inteligentes de herramientas para extender las capacidades del FM y asegurar operaciones fiables de las herramientas (por ejemplo, usando la Strands API para implementar comportamientos personalizados, definiciones de función estandarizadas, funciones Lambda para implementar manejo de errores y validación de parámetros).*

### Los tres modos de tool use de Bedrock

De [Use a tool to complete an Amazon Bedrock model response](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html). El principio que conviene fijar primero: **en Amazon Bedrock el modelo no llama directamente a la herramienta**. Al enviar un mensaje se aportan también definiciones de una o más herramientas que podrían ayudar; el modelo decide cuándo hace falta una herramienta, y el código de la aplicación (o Bedrock mismo, en modo server-side) la ejecuta y devuelve el resultado para que el modelo lo incorpore a su respuesta final.

| Modo | Quién ejecuta la herramienta | Cuándo usarlo |
| --- | --- | --- |
| **[Client-side tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-client-side.html)** | El código de tu aplicación, después de que el modelo devuelva la petición de llamada | La mayoría de los casos. Disponible con las APIs **Responses, Chat Completions, Converse e InvokeModel** |
| **[Server-side tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-server-side.html)** | **Amazon Bedrock mismo**. Registras una función Lambda o un AgentCore Gateway y Bedrock invoca la herramienta en nombre del modelo | Ejecución de herramientas centralizada y segura, sin gestionar la orquestación en la aplicación. Actualmente disponible en la **Responses API** |
| **[Anthropic Claude tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-tool-use.html)** | El código de tu aplicación, usando tipos de herramienta definidos por Anthropic (`computer_*`, `bash_*`, `text_editor_*`, `memory_*`) y el formato de la Anthropic Messages API | Computer use, ejecución de código, edición de ficheros, memoria persistente o streaming de herramienta de grano fino con modelos Claude |

> Structured output se puede combinar con tool use: ver [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html).

### Definiciones de función estandarizadas: el `toolConfig`

El skill pide "definiciones de función estandarizadas". En la Converse API eso es el `toolConfig`, con un `toolSpec` por herramienta:

```python
tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "top_song",
                "description": "Get the most popular song played on a radio station.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "sign": {
                                "type": "string",
                                "description": "The call sign for the radio station."
                            }
                        },
                        "required": ["sign"]
                    }
                }
            }
        }
    ]
}
```

Los tres campos del `toolSpec` hacen trabajo distinto, y confundirlos es una fuente clásica de herramientas que el modelo no usa bien:

| Campo | Para quién es | Efecto |
| --- | --- | --- |
| `name` | El código y el modelo | El identificador que el modelo devuelve para indicar qué herramienta quiere |
| `description` | **El modelo** | Es el criterio con el que el modelo **decide si esta herramienta sirve**. Una descripción vaga produce selección errónea. Recordar que AGENTCOST02 avisa de que los catálogos de herramientas crecen sin revisión y encarecen cada invocación |
| `inputSchema` | El modelo y la validación | Contrato de los argumentos: tipos, propiedades, campos `required` |

### El bucle de tool use en la Converse API

El flujo completo, del ejemplo oficial de client-side tool use:

```python
messages = [{"role": "user", "content": [{"text": input_text}]}]

response = bedrock_client.converse(
    modelId=model_id,
    messages=messages,
    toolConfig=tool_config
)

output_message = response['output']['message']
messages.append(output_message)              # el turno del modelo entra en el histórico

if response['stopReason'] == 'tool_use':     # el modelo pide herramienta
    for tool_request in output_message['content']:
        if 'toolUse' in tool_request:
            tool = tool_request['toolUse']
            # tool['name']      → qué herramienta
            # tool['toolUseId'] → correlación petición/resultado
            # tool['input']     → argumentos según inputSchema
            ...
```

Las tres piezas que estructuran el contrato de vuelta:

| Pieza | Función |
| --- | --- |
| **`stopReason: 'tool_use'`** | La señal de que el modelo pide una herramienta en lugar de responder. Es la condición del `Choice` en el bucle ReAct del [Skill 2.1.2](#skill-212--razonamiento-estructurado-y-descomposición-de-problemas) |
| **`toolUseId`** | Correlaciona la petición con su resultado. Imprescindible cuando el modelo pide varias herramientas en el mismo turno |
| **`toolResult`** | El resultado se devuelve como un `content` block de un mensaje con **`role: "user"`** |

### Manejo de errores: el campo `status` del `toolResult`

Aquí está el detalle más importante del skill, y el ejemplo oficial lo muestra explícitamente. Cuando la herramienta falla, **no se lanza la excepción al llamante**: se devuelve el error al modelo como resultado de herramienta con `status: 'error'`.

```python
try:
    song, artist = get_top_song(tool['input']['sign'])
    tool_result = {
        "toolUseId": tool['toolUseId'],
        "content": [{"json": {"song": song, "artist": artist}}]
    }
except StationNotFoundError as err:
    tool_result = {
        "toolUseId": tool['toolUseId'],
        "content": [{"text": err.args[0]}],
        "status": 'error'                    # el modelo puede reaccionar
    }

messages.append({"role": "user", "content": [{"toolResult": tool_result}]})

response = bedrock_client.converse(
    modelId=model_id,
    messages=messages,
    toolConfig=tool_config
)
```

> La diferencia de diseño: con `status: 'error'` y un mensaje legible, el modelo puede **corregir el argumento y reintentar**, pedir aclaración al usuario o explicar la limitación. Si en cambio la excepción propaga y rompe la aplicación, el agente pierde la oportunidad de recuperarse. Es la traducción concreta de la *degradación elegante* al nivel de una sola herramienta.

Distinguir dos tipos de error, porque su tratamiento difiere:

| Tipo de error | Tratamiento |
| --- | --- |
| **Error de contrato** (argumento inválido, entidad no encontrada) | `status: 'error'` con mensaje explicativo: el modelo puede corregir |
| **Error de infraestructura** (timeout, throttling, dependencia caída) | Reintento con backoff en la capa de orquestación (`Retry` de Step Functions), y si persiste, circuit breaker y cadena de fallback del [Skill 2.1.3](#skill-213--workflows-con-salvaguardas-y-comportamiento-controlado) |

### Validación de parámetros en Lambda

El `inputSchema` le dice al modelo qué forma tienen los argumentos, pero **el modelo es estocástico**: puede omitir un campo `required`, inventar un valor fuera de rango o pasar un tipo incorrecto. La validación en el lado de la herramienta no es opcional.

| Capa de validación | Qué comprueba |
| --- | --- |
| **Esquema** | Validar los argumentos recibidos contra el `inputSchema` (JSON Schema) antes de ejecutar nada |
| **Dominio** | Rangos, enumeraciones, formatos, existencia de la entidad referenciada |
| **Autorización** | Que el actor de la sesión tiene derecho a esta operación sobre este recurso, no solo que el agente tiene permiso genérico |
| **Idempotencia** | Clave de idempotencia para que un reintento no duplique el efecto. Es lo que recomienda AGENTREL06 para integración con sistemas legacy, ver [Skill 2.3.1](./task-2-3-integracion-empresarial.md#skill-231--conectividad-empresarial-y-acoplamiento-débil) |
| **Límites de recurso** | Acotar el tamaño de la respuesta: la salida de un estado que excede la cuota de payload produce `States.DataLimitExceeded` |

La autorización merece énfasis. Una herramienta que confía en que "el agente tiene permiso" convierte cualquier prompt injection exitosa en acceso a datos de otro tenant. El control correcto es el que describe AGENTREL02-BP02: el envoltorio de least privilege se impone **en las capas de identidad, política y control de acceso**, y AgentCore Policy soporta permisos de grano fino **basados en la identidad del usuario y en los parámetros de entrada de la herramienta**.

### Server-side tool use: ejecución centralizada

De [Server-side tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-server-side.html). Las herramientas se ejecutan en un **entorno backend de confianza**, no en el cliente, lo que mejora la postura de seguridad, fiabilidad y governance de la aplicación.

El dato de seguridad concreto: antes de ejecutar la función Lambda que implementa la herramienta, **Bedrock comprueba que la Lambda tiene la misma política IAM que la aplicación que la llama**. Y no hace falta aportar credenciales de autorización, porque Bedrock usa los mismos roles y políticas IAM de la aplicación que invoca el modelo.

Ventajas que enumera la documentación para la Lambda como herramienta personalizada:

| Ventaja | Detalle |
| --- | --- |
| Extender funcionalidad | Lógica de negocio propia, integraciones de API, procesamiento de datos |
| **Ejecución segura** | Lambda permite que las herramientas accedan a recursos **dentro de una VPC sin conceder acceso completo a la VPC** |
| Arquitectura serverless | Sin gestión de infraestructura; Lambda escala automáticamente |
| Coste | Se paga solo el tiempo de ejecución, no recursos ociosos |
| Integración | Las funciones aparecen junto a las herramientas integradas de forma transparente |

El ciclo de vida que documenta: **1)** crear la Lambda que implementa el protocolo MCP, **2)** Bedrock llama a la Lambda para **descubrir** las herramientas disponibles, **3)** las herramientas se **registran** con Bedrock, **4)** cuando el agente las pide, Bedrock **invoca** la Lambda, **5)** los resultados vuelven al agente por la interfaz estándar.

La Lambda implementa MCP como JSON-RPC, atendiendo dos métodos:

```python
import json

def lambda_handler(event, context):
    method = event.get('method')
    params = event.get('params', {})
    request_id = event.get('id')

    if method == 'tools/list':          # descubrimiento
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [{
                    "name": "my_custom_tool",
                    "description": "My custom business logic tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string", "description": "Input text to process"}
                        },
                        "required": ["input"]
                    }
                }]
            }
        }

    elif method == 'tools/call':        # ejecución
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        if tool_name == 'my_custom_tool':
            result = f"Processed: {arguments.get('input', '')}"
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": result}]}
            }

    return {                            # método no soportado
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": "Method not found"}
    }
```

El registro se hace pasando el **ARN de la Lambda en el campo `connector_id`** del parámetro `mcp` de la Responses API:

```python
resp = client.responses.create(
    model="oss-gpt-120b",
    tools=[{
        "type": "mcp",
        "server_label": "xamzn_arn",
        "connector_id": "arn:aws:lambda:us-west-2:123456789012:function:my-custom-tool",
        "require_approval": "never",
    }],
    input="My custom prompt.",
)
```

Al especificar la Lambda en `tools`, la API intenta obtener la lista de herramientas del servidor; si lo consigue, aparece un item de salida **`mcp_list_tools`** en la respuesta del modelo, cuya propiedad `tools` muestra las herramientas importadas correctamente.

Dos datos operativos: las herramientas server-side con la Responses API están disponibles **a partir de los modelos GPT OSS 20B/120B**, con soporte de otros modelos por llegar (la Models API permite descubrir qué modelos sirven), y la facturación es **solo por tokens** usados al importar definiciones de herramienta o al hacer llamadas, **sin tarifas adicionales por llamada de herramienta**.

> El campo **`require_approval`** del ejemplo es el gancho natural del [Skill 2.1.5](#skill-215--sistemas-colaborativos-con-expertise-humana): el punto donde la ejecución de una herramienta concreta se somete a aprobación.

### Centralizar herramientas con AgentCore Gateway

De [Core concepts for Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-core-concepts.html). Gateway da un **punto de entrada estandarizado y seguro para el tráfico agentic**, donde los agentes descubren e interactúan con herramientas, otros agentes y LLMs.

| Concepto | Definición |
| --- | --- |
| **Gateway** | Punto único y seguro de acceso. Puede tener múltiples **targets** en tres categorías: MCP, HTTP e inference |
| **Gateway Target** | El backend al que se conecta el gateway |
| **Authorizer** | Configuración de autorización **inbound** obligatoria en cada gateway |
| **Credential Provider** | Las credenciales que Gateway usa para llamar a tus APIs o Lambda (autorización **outbound**) |

**Las tres categorías de target**, y la diferencia entre ellas es el examen en una tabla:

| Categoría | Comportamiento | Capability sync y semantic tool search | Tipos |
| --- | --- | --- | --- |
| **MCP target** | **Modo agregación**: el gateway combina las capacidades de todos los MCP targets en un **único MCP server virtual unificado**. Los clientes ven una sola respuesta `tools/list` consolidada | **Sí**. Además soporta **three-legged OAuth (3LO)** a nivel de target | Funciones Lambda, REST APIs de API Gateway, especificaciones OpenAPI, modelos Smithy, MCP servers, plantillas de proveedores de integración y connectors integrados |
| **HTTP target** | Envía el tráfico **directamente al target**, sin agregación ni traducción de protocolo. Los clientes direccionan cada target individualmente por **routing basado en path** | **No** | Agentes de AgentCore Runtime, otros agentes (incluidos servicios **A2A**), MCP servers externos y cualquier endpoint HTTP vía passthrough |
| **Inference target** | Enruta tráfico de LLM a uno o varios proveedores de modelo por un **endpoint unificado**, seleccionando el destino según el campo **`model`** de la petición | — | Amazon Bedrock, OpenAI, Anthropic y otros |

> El **inference target** es exactamente la pieza del *GenAI gateway* que pide el [Skill 2.3.5](./task-2-3-integracion-empresarial.md#skill-235--cicd-y-arquitecturas-de-genai-gateway): una interfaz única y consistente entre proveedores.

**Tipos de autorización inbound** del Authorizer: **OAuth (JWT)** para autorización basada en token, **IAM (AWS Signature Version 4)** para autorización basada en identidad de AWS, **authenticate only** para validar tokens delegando la autorización al target, y **no authorization** para desarrollo y pruebas.

> El modo **no authorization** está documentado explícitamente para escenarios de desarrollo y pruebas. Usarlo en un gateway que expone herramientas con efectos de negocio deja las herramientas accesibles sin control.

**Credenciales outbound**: con targets Smithy o Lambda, Gateway usa el **execution role** adjunto. Con targets OpenAPI o MCP server, se adjunta un **AgentCore credential provider** que almacena la API key o las credenciales OAuth, se configura autorización IAM con firma SigV4, o se usa sin autorización para endpoints públicos.

**Los tipos de herramienta MCP** que soporta Gateway, que es la respuesta a "cómo convierto lo que ya tengo en una herramienta":

| Método | Qué hace |
| --- | --- |
| **OpenAPI specifications** | Transforma REST APIs existentes en herramientas compatibles con MCP; el gateway traduce entre MCP y REST automáticamente |
| **Lambda functions** | Conecta funciones Lambda como herramientas; el gateway las invoca y traduce la respuesta a formato MCP |
| **Smithy models** | Usa modelos Smithy para definir interfaces de API y generar herramientas compatibles con MCP, tanto para servicios de AWS como para APIs propias |
| **MCP servers** | Conecta MCP servers remotos. Soporta **tools** (obligatorio), **prompts** (opcional, plantillas reutilizables con argumentos) y **resources** (opcional, datos contextuales identificados por URI). Durante la sincronización el gateway **descubre todas las capacidades** que anuncia el servidor |
| **Integrations** | Plantillas preconfiguradas de proveedores de integración |
| **Connectors** | Connectors integrados a herramientas |

> Sobre la "Strands API" que nombra el skill: no existe documentación de la API de Strands en `docs.aws.amazon.com`. El equivalente documentado en el portal de AWS para "comportamientos personalizados" de herramienta son los tres modos de tool use de Bedrock y la capa de targets de AgentCore Gateway descritos arriba. Ver [referencias-oficiales.md](./referencias-oficiales.md#notas-sobre-discrepancias-encontradas-en-la-documentación).

---

## Skill 2.1.7 — Frameworks de extensión del modelo

> *Desarrollar frameworks de extensión del modelo para enriquecer las capacidades del FM (por ejemplo, usando funciones Lambda para implementar servidores MCP stateless que proporcionan acceso ligero a herramientas, Amazon ECS para implementar servidores MCP que proporcionan herramientas complejas, librerías cliente MCP para asegurar patrones de acceso consistentes).*

### El contrato de protocolo MCP en AgentCore Runtime

De [MCP protocol contract](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp-protocol-contract.html). Los requisitos que debe cumplir un MCP server para desplegarse en AgentCore Runtime.

**Requisitos de protocolo**

| Requisito | Especificación |
| --- | --- |
| **Transport** | **Streamable-http es obligatorio**. Por defecto, usar modo stateless (`stateless_http=True`) por compatibilidad con la gestión de sesiones y el balanceo de carga de AWS |
| **Session management** | La plataforma añade automáticamente el header **`Mcp-Session-Id`** para aislamiento de sesión. En modo stateless, el servidor debe soportar operación stateless de forma que **no rechace el `Mcp-Session-Id` generado por la plataforma** |

**Requisitos de contenedor**

| Requisito | Valor |
| --- | --- |
| **Host** | `0.0.0.0` |
| **Port** | **`8000`** — puerto estándar para comunicación de MCP server, **distinto del usado por el protocolo HTTP** |
| **Platform** | Contenedor **ARM64**, requerido para compatibilidad con el entorno de ejecución de AgentCore Runtime |

**Requisitos de path**

| Path | Método | Propósito |
| --- | --- | --- |
| **`/mcp`** | `POST` | Recibe mensajes RPC de MCP y los procesa mediante las capacidades de herramienta del agente. **Pass-through completo del payload de la API `InvokeAgentRuntime`** con mensajes RPC estándar de MCP |

Formato de respuesta: request/response basado en JSON-RPC, soportando **tanto `application/json` como `text/event-stream`** como content-types de respuesta. Casos de uso del endpoint `/mcp`: invocación y gestión de herramientas, descubrimiento de capacidades del agente, acceso y manipulación de recursos, y workflows de agente multi-paso.

### Stateless vs stateful, y la adherencia al microVM

Este es el punto técnico más denso del skill, y tiene una consecuencia de rendimiento directa.

MCP usa el header `Mcp-Session-Id` para gestionar el estado de sesión y enrutar peticiones. **AgentCore Runtime usa ese header para enrutar las peticiones al mismo microVM.**

> **MicroVM stickiness**: los clientes deben capturar el `Mcp-Session-Id` devuelto en la respuesta e incluirlo en todas las peticiones siguientes para asegurar afinidad de sesión. **Sin un session ID consistente, cada petición puede enrutarse a un microVM nuevo, lo que puede añadir latencia por cold starts.**

| | **Stateless** (`stateless_http=True`) | **Stateful** (`stateless_http=False`) |
| --- | --- | --- |
| Quién genera el session ID | **La plataforma** lo genera y lo incluye en la petición a tu MCP server | El cliente envía `initialize` **sin** header `Mcp-Session-Id`; la plataforma devuelve el `Mcp-Session-Id` en la respuesta |
| Obligación del servidor | **Debe aceptar** el session ID aportado por la plataforma, no rechazarlo | — |
| Qué garantiza el header | Afinidad de microVM | Afinidad de microVM **y estado de sesión** |
| Dónde vive el estado | En un **backing store que gestiona tu aplicación**, por ejemplo una base de datos, referenciado con **explicit state handles**: el servidor devuelve un identificador de estado en el resultado de la herramienta y el cliente lo devuelve en llamadas posteriores para indexar en el store | Dentro de la sesión MCP, a través de múltiples peticiones |
| Capacidades adicionales | — | **Elicitation** (interacciones multi-turno con el usuario), **sampling** (contenido generado por LLM) y notificaciones de progreso |

> **En ambos modos AgentCore Runtime siempre devuelve un header `Mcp-Session-Id` al cliente.** La recomendación oficial es capturarlo y reutilizarlo siempre, para rendimiento óptimo.

**Matiz de versión del protocolo** que documenta AWS: para la versión de protocolo MCP **2025-11-25 y anteriores**, el modo stateful **es necesario** para elicitation y sampling, porque el servidor entrega esas peticiones sobre una sesión abierta. Para la versión **2026-07-28 y posteriores**, elicitation y sampling usan el patrón **multi round-trip requests (MRTR)**, que **no requiere modo stateful**.

### Manejo de errores: JSON-RPC sobre HTTP 200

Un detalle que rompe la intuición y por eso es buen material de examen. Los MCP servers devuelven errores como respuestas de error JSON-RPC 2.0 estándar. **La mayoría de los errores viajan en el objeto `error` de JSON-RPC con un código de estado HTTP 200**, como exige la especificación de MCP. Solo los errores de **autenticación, autorización y de protocolo** usan códigos HTTP distintos de 200.

| Código JSON-RPC | Excepción de runtime | HTTP | Mensaje |
| --- | --- | --- | --- |
| `-32001` | `UnauthorizedException` | **401** | Error de autenticación: credenciales inválidas |
| `-32002` | `AccessDeniedException` | **403** | Error de autorización: permisos insuficientes |
| `-32601` | Método no encontrado | 200 | `Method not found` (como en el ejemplo de Lambda del skill anterior) |

La consecuencia práctica: un cliente que solo mire el status HTTP concluirá que todo fue bien. La comprobación correcta es inspeccionar el objeto `error` de la respuesta JSON-RPC.

### Construir un MCP server: el ejemplo oficial

De [Deploy MCP servers in AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html). Prerrequisitos: Python 3.10 o superior y una cuenta de AWS con permisos y credenciales locales configuradas.

```python
# my_mcp_server.py
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

mcp = FastMCP(host="0.0.0.0", stateless_http=True)

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b

@mcp.tool()
def greet_user(name: str) -> str:
    """Greet a user by name"""
    return f"Hello, {name}! Nice to meet you."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

Los componentes que explica la documentación: **`FastMCP`** crea el MCP server que hospeda las herramientas, el decorador **`@mcp.tool()`** convierte funciones Python en herramientas MCP, y **`stateless_http=True`** configura el modo stateless, que es el predeterminado para MCP servers básicos.

> Nótese que el **docstring de la función es la descripción de la herramienta** que verá el modelo. Es el mismo `description` del `toolSpec` del skill anterior, con la misma responsabilidad: si es vaga, la selección de herramienta será mala.

### Dónde alojar el MCP server: la tabla de decisión

El skill contrapone explícitamente Lambda para servidores stateless ligeros y ECS para herramientas complejas. Con el tercer destino documentado, AgentCore Runtime, el cuadro completo:

| | **Lambda** | **Amazon ECS / Fargate** | **AgentCore Runtime** |
| --- | --- | --- | --- |
| **Perfil del skill** | MCP servers **stateless** que dan acceso ligero a herramientas | MCP servers que proveen **herramientas complejas** | Alojamiento gestionado de agentes y herramientas |
| **Modelo de ejecución** | Por invocación, sin servidor | Contenedores de larga vida | Contenedor en **microVM** por sesión |
| **Duración máxima** | **900 s (15 min)**; hasta 5.400 s (90 min) con Managed Instances en invocación asíncrona | Sin límite | Sesión de hasta **8 h**; termina a los **15 min** de inactividad |
| **Aislamiento** | Entorno de ejecución por invocación | Tarea/contenedor | **MicroVM dedicado** con CPU, memoria y filesystem aislados; la memoria se sanea al terminar |
| **Estado en proceso** | No fiable entre invocaciones | Sí, mientras viva la tarea | Sí, dentro de la sesión, pero **efímero por diseño** |
| **Registro como herramienta** | `connector_id` con el ARN en server-side tool use, o **Lambda target** en AgentCore Gateway | **MCP server target** en Gateway (aggregation) o **HTTP target** (passthrough) | **MCP server** con el contrato `/mcp`, o **HTTP target** en Gateway |
| **Requisitos de contenedor** | Imagen hasta 10 GB | Los de ECS | **ARM64**, `0.0.0.0:8000`, path `/mcp` |
| **Acceso a VPC** | Sí, **sin conceder acceso completo a la VPC** a la herramienta | Nativo | Configuración de red del runtime |
| **Cuándo elegirlo** | Herramienta de I/O corta: consultar una API, leer DynamoDB, invocar un modelo | Dependencias pesadas, procesos largos, binarios nativos, estado en memoria, GPU | Herramientas que necesitan aislamiento fuerte por sesión, filesystem y shell, o vivir junto al agente |

Lo que decide en la práctica: **el techo de 15 minutos de Lambda** y la necesidad (o no) de estado en proceso y de dependencias que no caben en un paquete de despliegue.

Dos capacidades de AgentCore que compiten con "construir la herramienta" y conviene conocer antes de escribir código: **Code Interpreter**, un sandbox aislado para que los agentes ejecuten código en Python, JavaScript y TypeScript; y **Browser**, un runtime de navegador gestionado en la nube para que los agentes interactúen con aplicaciones web, rellenen formularios, naveguen y extraigan información, compatible con frameworks de automatización como Playwright y BrowserUse.

### Patrones de acceso consistentes: el registro central

El skill pide "librerías cliente MCP para asegurar patrones de acceso consistentes". La consistencia tiene dos mitades: la del protocolo (que MCP resuelve por diseño) y la del **descubrimiento**, que es donde entra el registro.

De [AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html), servicio de descubrimiento totalmente gestionado que provee un catálogo centralizado para organizar, curar y descubrir recursos en la organización. Permite publicar **MCP servers, herramientas, agentes, agent skills y recursos personalizados** en un registro buscable, controlar el acceso con un **workflow de aprobación**, y permitir que tanto personas como agentes descubran lo que necesitan mediante búsqueda híbrida, navegación de catálogo y un **endpoint MCP nativo**.

El problema que declara resolver: a medida que las organizaciones escalan el uso de agentes y herramientas, encontrar el recurso adecuado se vuelve difícil. Los equipos construyen MCP servers, despliegan agentes y crean herramientas especializadas, pero **sin catálogo central esos recursos quedan en silos**, lo que provoca **duplicación de esfuerzo y deuda técnica** porque se reconstruye lo que ya existe simplemente por no poder descubrirlo.

| Capacidad | Detalle |
| --- | --- |
| **Descubrimiento centralizado** | Un único sitio para encontrar todos los recursos publicados, buscable por personas y por agentes |
| **Governance y curación** | Workflow de aprobación que asegura que solo los registros que cumplen los criterios de seguridad, compliance y calidad son descubribles. Los administradores controlan qué pueden descubrir y usar los builders, y **pueden retirar la visibilidad en cualquier momento** |
| **Tipos flexibles de recurso** | MCP servers, agentes, skills y recursos personalizados. **Valida los registros de MCP y de agente contra sus esquemas de protocolo** respectivos, y admite metadatos propios para todos los tipos |
| **Hybrid search** | Combina comprensión **semántica** con coincidencia de **keywords**, para que tanto consultas en lenguaje natural como búsquedas de nombre exacto devuelvan resultados relevantes |
| **Catalog browsing** | Paginar registros aprobados con filtros, o recuperar detalles de muchos a la vez, para construir experiencias de descubrimiento tipo directorio |
| **Acceso MCP-native** | El registro está disponible en un **endpoint MCP remoto**, de modo que clientes compatibles con MCP interactúan con él usando el propio protocolo |
| **Autorización flexible** | **Credenciales IAM** o **JWT** del proveedor de identidad corporativo para controlar quién busca, navega e invoca el endpoint MCP del registro |

**Dos recursos centrales**: los *registries* (catálogos que creas en tu cuenta, cada uno con nombre, descripción, configuración de autorización IAM o JWT, ajustes de aprobación y su conjunto de registros) y los *registry records* (un recurso individual publicado, con los metadatos que describen qué es, qué hace y cómo encontrarlo). Se puede tener un registro único para toda la organización, o registros por tipo de recurso, por etapa de desarrollo (producción, QA, desarrollo), por equipo o por unidad de negocio.

**El workflow típico**, con cuatro personas distintas:

```
Administrador  → crea el registro, configura autorización y aprobación
      │
      ▼
Publisher      → crea registros describiendo sus MCP servers, agentes o herramientas
                 y los somete a aprobación
      │
      ▼
Curator        → revisa los registros pendientes, aprueba o rechaza
                 y deprecia los que ya no se usan
      │
      ▼
Consumer       → busca, navega el catálogo aprobado, o se conecta al endpoint
                 MCP del registro para encontrar lo que necesita
```

Integraciones que documenta: notificaciones con **EventBridge**, uso con **AWS Organizations**, compartición entre cuentas con **AWS RAM**, registro de llamadas de API con **CloudTrail**, y acceso privado con **VPC y AWS PrivateLink**.

> El nivel 4 de madurez de [AGENTREL04](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel04.html) añade el requisito operativo que cierra el círculo: **automatizar el registro de capacidades en CI/CD**, para que el registro se mantenga alineado con lo realmente desplegado. Un catálogo que se actualiza a mano se desincroniza.

### Resumen del task: las piezas de un sistema agentic en AWS

```
┌─────────────────────────────────────────────────────────────────────┐
│ DESCUBRIMIENTO    AWS Agent Registry                                │
│                   catálogo curado de agentes, MCP servers y skills  │
│                   hybrid search + endpoint MCP nativo               │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│ ORQUESTACIÓN      Step Functions Standard (estado durable, 1 año,   │
│                     .waitForTaskToken para esperas humanas)         │
│                   arbiter pattern event-driven con EventBridge      │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│ EJECUCIÓN         AgentCore Runtime: microVM por sesión, 8 h,       │
│                     versiones inmutables, endpoints por entorno     │
│                   Lambda: herramientas cortas, techo de 15 min      │
│                   ECS / Fargate: herramientas complejas y largas    │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│ HERRAMIENTAS      AgentCore Gateway                                 │
│                     MCP targets    → agregación en un MCP virtual   │
│                     HTTP targets    → passthrough, A2A, otros agentes│
│                     Inference targets → routing entre proveedores   │
│                   Bedrock tool use: client-side y server-side       │
│                   Code Interpreter · Browser                        │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│ MEMORIA           AgentCore Memory: short-term + long-term          │
│                     userPreference · semantic · summary · episodic  │
│                   DynamoDB para esquema y auditoría propios         │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│ CONTROL           AgentCore Policy (Cedar): intercepta cada tool    │
│                     call en el Gateway, antes de ejecutarla         │
│                   AgentCore Identity: autenticación del agente      │
│                   IAM: rol por agente + permissions boundary        │
│                   Guardrails: primera pasada antes del revisor      │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│ OBSERVACIÓN       AgentCore Observability (OTEL)                    │
│                   AgentCore Evaluations: sesiones, traces y spans   │
│                   CloudWatch Anomaly Detection sobre baselines      │
└─────────────────────────────────────────────────────────────────────┘
```
