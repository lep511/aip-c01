# Task 2.3 — Arquitecturas de integración empresarial

[← Volver al índice](./README.md)

Skills cubiertos: **2.3.1**, **2.3.2**, **2.3.3**, **2.3.4**, **2.3.5**.

---

## Skill 2.3.1 — Conectividad empresarial y acoplamiento débil

> *Crear soluciones de conectividad empresarial para incorporar sin fricción capacidades de FM en entornos empresariales existentes (por ejemplo, usando integraciones basadas en API con sistemas legacy, arquitecturas event-driven para implementar acoplamiento débil, patrones de sincronización de datos).*

### El marco: integrar sin desestabilizar lo que ya funciona

De [AGENTREL06 — Legacy system integration](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel06.html). El planteamiento oficial da la clave del skill: los sistemas existentes **pueden no estar optimizados para interacciones de agente** y pueden necesitar soporte de protocolos como MCP o A2A. La pregunta que formula el área de foco es cómo integran los agentes de forma efectiva **sin impactar la fiabilidad de los procesos establecidos**.

La intención de capacidad, que son los seis requisitos de una integración correcta:

| Requisito | Detalle |
| --- | --- |
| **Adapter interfaces** | Los sistemas legacy se alcanzan a través de adaptadores que exponen **contratos de herramienta agent-native**, de modo que los agentes no necesitan entender los protocolos que hay detrás |
| **Protección del legacy** | Los sistemas legacy se protegen de los patrones de invocación agent-native mediante **rate limiting y control de acceso aplicados en la capa del adaptador** |
| **Fallback por dependencia** | Cada dependencia legacy tiene una ruta de fallback definida, para que una caída del legacy produzca **capacidad reducida en lugar de fallo completo** del agente |
| **Idempotencia** | Las operaciones con efectos colaterales son idempotentes, de forma que la recuperación basada en reintentos sea segura y no produzca **transacciones duplicadas ni estado inconsistente** |
| **Capability toggling** | Los operadores pueden **deshabilitar y rehabilitar capacidades individuales en tiempo de ejecución sin redespliegue**, y cada capacidad tiene un comportamiento de fallback probado que se activa al apagarla |
| **Ejercicio de la resiliencia** | Los mecanismos se ejercitan con **fault injection y game days**, para descubrir huecos en pruebas y no en incidentes de producción |

**Los seis problemas frecuentes** del área de foco, que son el mejor inventario de antipatrones de este skill:

1. Agentes **acoplados directamente** a las interfaces legacy sin capa de adaptador, de modo que los cambios de protocolo del legacy se propagan al código del agente y **cada agente maneja los códigos de error legacy a su manera**.
2. Asumir que las dependencias legacy tienen la fiabilidad de un servicio cloud, de modo que **no existen rutas de fallback** y una sola caída provoca el fallo completo del agente.
3. Reintentos **sin garantías de idempotencia**, de modo que recuperarse de un fallo transitorio crea transacciones duplicadas, estado corrupto o inconsistencia silenciosa.
4. Deshabilitar una capacidad problemática requiere **cambios de código y redespliegue**, lo que alarga el tiempo de remediación durante un incidente y **desincentiva cortar funcionalidades que se portan mal**.
5. Los cortes automáticos **abren ante el fallo pero nunca cierran tras la recuperación**, porque no hay ninguna sonda que rehabilite el acceso, dejando la capacidad degradada mucho después de que el legacy vuelva a estar sano.
6. Los mecanismos de resiliencia **nunca se ejercitan**, con lo que rutas de fallback, runbooks y alertas se prueban por primera vez en un incidente real.

### Las cinco best practices y su implementación documentada

| Best practice | Implementación que nombra el lens |
| --- | --- |
| **AGENTREL06-BP01** Desarrollar integraciones de agente con sistemas existentes o legacy | Adaptadores registrados en **AgentCore Gateway** con una **taxonomía canónica de errores**, para que los agentes manejen los fallos del legacy de forma consistente |
| **AGENTREL06-BP02** Establecer mecanismos de fallback ante degradación del legacy | Estrategia **emparejada a cada tipo de dependencia** (ver tabla siguiente) |
| **AGENTREL06-BP03** Probar regularmente el rendimiento en sistemas degradados | **AWS Fault Injection Service** con experimentos en calendario definido; en nivel 4, FIS **dentro de CI/CD** y game days trimestrales validando runbooks |
| **AGENTREL06-BP04** Implementar patrones de ejecución idempotente | **Escrituras condicionales de DynamoDB** con expiración basada en **TTL**; en nivel 4, las claves de idempotencia **se propagan por workflows multi-paso** y se pasan a sistemas externos que soportan idempotencia nativa |
| **AGENTREL06-BP05** Implementar capability toggling dinámico | Políticas **Cedar de AgentCore Policy**, que permiten control en tiempo de ejecución sin redespliegue |

**La estrategia de fallback emparejada al tipo de dependencia** es el detalle más aprovechable del área de foco:

| Tipo de dato o operación | Estrategia de fallback |
| --- | --- |
| **Datos de referencia** | **Basada en caché**: servir la última copia buena conocida |
| **Operaciones transaccionales** | **Basada en cola** con **Amazon SQS**: aceptar la intención ahora, ejecutar cuando el legacy vuelva |
| **Datos en tiempo real** | **Degradación elegante**: responder sin ese dato, indicándolo |

Y el nivel 4 añade el mecanismo que resuelve el problema frecuente número 5: alarmas sobre **AgentCore Observability** que disparan **cortes automáticos con lógica de circuit breaker en Lambda**, más **sondas de recuperación que rehabilitan el acceso cuando los sistemas se recuperan**.

### Integraciones basadas en API

| Servicio | Papel en la integración con legacy |
| --- | --- |
| **Amazon API Gateway** | La fachada REST o HTTP delante del sistema legacy o delante del FM. Aporta **request validation**, throttling y usage plans (la parte de *rate limiting en la capa del adaptador* que pide AGENTREL06), autorización y transformaciones de petición. Detalle en [Task 2.4](./task-2-4-integraciones-api-fm.md) |
| **AWS AppSync** | Fachada GraphQL, útil cuando varios sistemas de origen alimentan una sola vista y el cliente decide qué campos necesita |
| **AgentCore Gateway** | Convierte APIs existentes, funciones Lambda y servicios en **herramientas compatibles con MCP**. Es literalmente la *adapter interface que expone contratos agent-native* de AGENTREL06-BP01. Los tipos de target y la mecánica están en [Task 2.1 · Skill 2.1.6](./task-2-1-agentic-ai-y-herramientas.md#skill-216--integraciones-de-herramientas-y-operaciones-fiables) |
| **Lambda** | El adaptador en sí: traduce el protocolo legacy (SOAP, ficheros de posiciones fijas, colas propietarias) al contrato de herramienta, y normaliza los errores a la taxonomía canónica |

### Arquitecturas event-driven: buses frente a pipes

De [Amazon EventBridge Pipes](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes.html). La documentación distingue con claridad los dos mecanismos, y elegir mal es un error de diseño clásico:

| Mecanismo | Topología | Cuándo |
| --- | --- | --- |
| **Event buses** | **Many-to-many**: routing de eventos entre servicios event-driven | Cuando varios productores y varios consumidores deben desacoplarse |
| **EventBridge Pipes** | **Point-to-point**: conecta una fuente con un destino | Integraciones punto a punto, con **transformaciones avanzadas y enrichment** |

Pipes **reduce la necesidad de conocimiento especializado y de código de integración** al desarrollar arquitecturas event-driven, fomentando consistencia entre las aplicaciones de la organización. Para configurar un pipe se elige la fuente, se añade filtrado opcional, se define enrichment opcional y se elige el destino.

Cómo funciona, según la documentación:

```
Fuente ──► [ filtro (opcional) ] ──► [ enrichment (opcional) ] ──► Destino
             │                          │
             │                          └─ si los eventos van en lote,
             │                             el enrichment MANTIENE EL ORDEN
             │                             de los eventos del lote
             └─ solo se factura por los eventos que coinciden con el filtro
```

El ejemplo oficial, aplicable casi literalmente a un pipeline GenAI:

1. Una cola de **Amazon SQS** de "pedido recibido" como fuente de eventos.
2. Un **EventBridge API Destination** como enrichment, que devuelve la información del cliente para ese pedido.
3. Una máquina de estados de **AWS Step Functions** como destino, que procesa el pedido.

> El detalle de facturación (**solo se paga por los eventos que coinciden con el filtro**) convierte el filtrado en una decisión de coste, no solo de corrección.

### Patrones de sincronización de datos

| Servicio | Patrón | Cuándo |
| --- | --- | --- |
| **Amazon AppFlow** | Transferencia de datos gestionada entre SaaS y AWS | Sincronizar desde Salesforce, ServiceNow, Zendesk y similares sin escribir código de integración |
| **AWS DataSync** | Transferencia de ficheros a escala entre on-premises y AWS | Poblar el corpus de una knowledge base desde un NAS o file share. Base en [Task 1.4 · Skill 1.4.4](../domain-1/task-1-4-vector-stores.md) |
| **AWS Transfer Family** | SFTP, FTPS y FTP gestionados hacia S3 | Cuando el sistema de origen solo sabe dejar ficheros por SFTP |
| **DynamoDB Streams** | Captura de cambios | Disparar reindexado o actualización de memoria cuando cambia un registro |
| **EventBridge Pipes** | Punto a punto con filtrado y enrichment | Mover cambios de un origen a un destino, enriqueciéndolos en tránsito |
| **Ingestion jobs de knowledge base** | Sincronización incremental del corpus | Detalle en [Task 1.4 · Skill 1.4.5](../domain-1/task-1-4-vector-stores.md) |

### Arquitectura de referencia de la integración

```
┌──────────────────────────────────────────────────────────────────────┐
│ SISTEMAS EXISTENTES                                                  │
│   ERP · CRM · mainframe · file shares · SaaS                          │
└──────────────────────────────────────────────────────────────────────┘
        ▲                    ▲                          ▲
        │ API                │ ficheros                 │ SaaS
        │                    │                          │
┌───────┴────────┐  ┌────────┴────────┐      ┌──────────┴──────────┐
│ Lambda adapter │  │ DataSync /      │      │ Amazon AppFlow      │
│  · traduce     │  │ Transfer Family │      │                     │
│    protocolo   │  └────────┬────────┘      └──────────┬──────────┘
│  · normaliza   │           │                          │
│    errores a   │           ▼                          ▼
│    taxonomía   │      ┌─────────────────────────────────────┐
│    canónica    │      │ Amazon S3 (corpus)                  │
│  · rate limit  │      └──────────────┬──────────────────────┘
│  · idempotencia│                     │
│    (DynamoDB   │                     ▼
│    conditional │      ┌─────────────────────────────────────┐
│    write + TTL)│      │ Knowledge base · ingestion job      │
└───────┬────────┘      └─────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────────────┐
│ AgentCore Gateway  ·  adapter registrado como herramienta MCP        │
│   taxonomía canónica de errores · AgentCore Policy para toggling     │
└──────────────────────────────────────────────────────────────────────┘
        ▲
        │
┌───────┴──────────────────────────────────────────────────────────────┐
│ Agente / aplicación GenAI                                            │
│   fallback por dependencia: caché · cola SQS · degradación elegante  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Skill 2.3.2 — Enriquecer aplicaciones existentes con funcionalidad GenAI

> *Desarrollar capacidades de IA integradas para enriquecer aplicaciones existentes con funcionalidad GenAI (por ejemplo, usando API Gateway para implementar integraciones de microservicios, funciones Lambda para webhook handlers, Amazon EventBridge para implementar integraciones event-driven).*

### Los tres modos de inserción

La diferencia entre este skill y el anterior es la dirección: el 2.3.1 trata de que el agente **alcance** los sistemas existentes; el 2.3.2 trata de que las aplicaciones existentes **consuman** capacidades GenAI.

| Modo | Mecanismo | Perfil |
| --- | --- | --- |
| **Sincrónico** | La aplicación llama a API Gateway, que invoca una Lambda que llama a Bedrock, y espera la respuesta | El usuario está esperando: chat, autocompletado, clasificación en el formulario |
| **Webhook** | Un sistema externo notifica un evento a un endpoint de API Gateway que invoca una Lambda handler | El sistema de origen ya sabe emitir webhooks: un CRM, un repositorio, un ITSM |
| **Event-driven** | El cambio publica un evento en EventBridge y una regla dispara el procesamiento GenAI | Desacoplado por completo: el productor no sabe que existe el consumidor GenAI |

### Microservicio GenAI detrás de API Gateway

El patrón que pide el skill, con las piezas que aportan valor en cada capa:

```
Aplicación existente
   │  HTTPS
   ▼
┌──────────────────────────────────────────────────────────┐
│ Amazon API Gateway                                       │
│   · authorizer (Cognito / IAM / JWT / Lambda)            │
│   · request validation: rechaza antes de gastar tokens   │
│   · usage plans + API keys: cuota por consumidor          │
│   · throttling: protege el backend y la cuota de Bedrock │
│   · transformaciones de petición y respuesta             │
└──────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────┐
│ AWS Lambda                                               │
│   · resuelve configuración (AppConfig): modelo, prompt,  │
│     versión de guardrail                                 │
│   · invoca Bedrock con reintentos y backoff              │
│   · normaliza la respuesta al contrato del microservicio │
│   · emite métricas y trazas (X-Ray)                      │
└──────────────────────────────────────────────────────────┘
   │
   ▼
Amazon Bedrock  /  endpoint de SageMaker AI  /  AgentCore
```

La **request validation** de API Gateway merece énfasis en un contexto GenAI: rechazar una petición mal formada en el borde cuesta casi nada; dejarla pasar hasta el modelo cuesta tokens. Es el mismo razonamiento que el segundo problema frecuente de [AGENTSEC04](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec04.html), visto en [Task 2.1 · Skill 2.1.3](./task-2-1-agentic-ai-y-herramientas.md#skill-213--workflows-con-salvaguardas-y-comportamiento-controlado): filtrar solo en la salida deja la ruta de inferencia abierta y **consume capacidad en entradas adversarias que podían rechazarse por adelantado**.

### Webhook handlers en Lambda

Las consideraciones específicas de un handler de webhook que dispara trabajo GenAI:

| Consideración | Tratamiento |
| --- | --- |
| **Verificación de firma** | Validar la firma HMAC del emisor antes de procesar. El secreto en **Secrets Manager** |
| **Responder rápido** | El emisor suele tener un timeout corto: aceptar (`202`), encolar en **SQS** y procesar aparte. La generación de un FM no cabe en la ventana del webhook |
| **Idempotencia** | Los webhooks se reentregan. Clave de idempotencia con **escritura condicional de DynamoDB y TTL**, tal como recomienda AGENTREL06-BP04 |
| **Orden** | Si el orden importa, cola FIFO de SQS con `MessageGroupId` |
| **Payload grande** | El límite de payload sincrónico de Lambda es de **6 MB**: el contenido grande va por S3 con referencia |
| **Fallo del downstream** | DLQ en SQS y alarma; no perder el evento por un throttling de Bedrock |

### Integración event-driven con EventBridge

```
Cambio en la aplicación existente
   │
   ▼
┌───────────────────────────────────────────────────────────────┐
│ EventBridge event bus                                         │
│   El productor publica el hecho; no conoce a los consumidores │
└───────────────────────────────────────────────────────────────┘
   │                    │                          │
   │ regla 1            │ regla 2                  │ regla 3
   ▼                    ▼                          ▼
Lambda: resumir    Step Functions:          Lambda: reindexar
con Bedrock        clasificar y enrutar     la knowledge base
   │
   ▼
Persistir / notificar / actualizar el sistema de origen
```

Lo que aporta el bus frente a llamar directamente: se pueden **añadir consumidores GenAI sin tocar el productor**, y si el consumidor falla o está throttled, el evento no se pierde (reintentos de la regla más DLQ). Es el *acoplamiento débil* que pide literalmente el skill 2.3.1 aplicado a la inserción de capacidades.

Cuándo usar **Pipes** en lugar de un bus, según la documentación: cuando la integración es punto a punto y hace falta transformación o enrichment antes de entregar al destino.

### Otros puntos de inserción en alcance

| Servicio | Inserción |
| --- | --- |
| **AWS AppSync** | Subscriptions de GraphQL para empujar el resultado GenAI a la UI cuando esté listo |
| **Amazon Connect** | Añadir capacidades GenAI a un contact center; está en la lista de servicios en alcance (Customer Engagement) |
| **Amazon Lex** | Interfaz conversacional con intents y slots, integrable como nodo en un flow de Bedrock. Ver [Task 1.6 · Skill 1.6.2](../domain-1/task-1-6-prompt-engineering-governance.md) |
| **Amazon Q Business** | Asistente sobre el contenido corporativo, sin construir el pipeline RAG. Ver [Task 1.4 · Skill 1.4.4](../domain-1/task-1-4-vector-stores.md) |
| **CloudFront y Lambda@Edge** | Terminación y lógica en el borde delante de la API |

---

## Skill 2.3.3 — Frameworks de acceso seguro

> *Crear frameworks de acceso seguro para asegurar controles de seguridad apropiados (por ejemplo, usando federación de identidad entre servicios de FM y sistemas empresariales, control de acceso basado en rol para acceso a modelo y datos, acceso de least privilege a las APIs de FM).*

### El marco: los dos patrones de acceso de un agente

De [AGENTSEC03 — Agent identity and permission management](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentsec03.html). El planteamiento oficial empieza distinguiendo dos patrones, y esa distinción organiza todo el skill:

| Patrón | Descripción |
| --- | --- |
| **En nombre de un usuario** | Un humano inició la petición, y **las acciones del agente deben estar acotadas por los permisos de ese usuario** |
| **De forma autónoma** | El agente actúa **sin humano en el bucle**: disparado por un calendario, un evento, una alarma u otro agente |

La gestión de identidad y permisos tiene que cubrir **ambos**. Sin ella, los permisos del agente pueden derivar en acceso no autorizado a recursos y datos. Las tres medidas que enuncia: aplicar principios de least privilege, **separar permisos de agente y de humano**, y establecer autenticación fuerte para las identidades de agente.

La intención de capacidad:

| Elemento | Qué exige |
| --- | --- |
| **Autenticación verificable** | Toda comunicación agente-a-agente y agente-a-servicio se autentica mediante mecanismos verificables: **mutual TLS basado en certificado, tokens OAuth firmados o workload identity gestionada por la plataforma** |
| **Identidades separadas** | Los agentes operan bajo **identidades de servicio distintas de las humanas**, y las pistas de auditoría atribuyen cada acción sin ambigüedad a un agente o a un humano |
| **Propagación del contexto de usuario** | Cuando el agente actúa en nombre de un usuario, el contexto se propaga como **claims de token firmado** por la cadena de llamada, **sin que el agente asuma nunca las credenciales del usuario** |
| **Permisos mínimos** | Credenciales de corta vida, **permission boundaries** e **IAM Conditions** |
| **Validación continua** | Detección automática de drift, hallazgos de acceso no usado y revisiones periódicas documentadas |

### Los cuatro problemas frecuentes

1. **API keys compartidas o tokens estáticos** para autenticación de agentes, sin cadencia de rotación ni ruta de revocación. La credencial se convierte en un secreto de larga vida distribuido entre entornos, y **cualquier filtración expone a todos los agentes que la tienen** hasta rotarlos uno a uno.
2. **Roles de agente y de humano difuminados**, por reutilización de rol, role chaining o falta de guardrails de trust policy y SCP, de modo que las pistas de auditoría **no distinguen acciones de agente de acciones humanas** durante la investigación de un incidente.
3. Permisos **ampliados de forma reactiva ante errores de access-denied** sin investigar si el patrón de acceso es coherente con el alcance previsto del agente, produciendo un **privilege creep** constante que ninguna revisión individual detecta.
4. Revisiones de acceso de identidades de agente **con la cadencia heredada de las revisiones de usuarios humanos** (anual o post-incidente), aunque los permisos de agente **derivan mucho más rápido** a medida que se añaden herramientas, prompts y patrones de orquestación.

> El cuarto es el más específico del dominio agentic: la cadencia de revisión tiene que ir al ritmo de los cambios del agente, no al del ciclo de RRHH.

### La progresión de madurez y sus servicios

| Nivel | Qué se usa |
| --- | --- |
| **1 · Initial** | API keys compartidas o tokens estáticos; roles reutilizados entre agentes y humanos; permisos amplios, credenciales de larga vida, auditoría que no distingue actor. **Sin permission boundary, sin ruta de revocación, sin cadencia de revisión** |
| **2 · Emerging** | **Un rol IAM dedicado por agente** con convención consistente de nombres y tags. Certificados de **AWS Private CA** donde se requiere mutual TLS, rotación por **Secrets Manager**, y **CloudTrail** registrando actividad de agente separada de la humana |
| **3 · Defined** | **AgentCore Identity** centraliza workload identities, emisión de tokens y el **token vault**, con claves **KMS gestionadas por el cliente** protegiendo secretos. Los operadores humanos entran por **IAM Identity Center**, y **SCPs en AWS Organizations** evitan que los agentes asuman roles humanos. **AWS STS `AssumeRole`** emite credenciales de corta vida con session policies, e **IAM Access Analyzer** aporta hallazgos de baseline |
| **4 · Proactive** | **`GetWorkloadAccessTokenForJWT`** embute el contexto de usuario como claims, para que los servicios downstream apliquen autorización a nivel de usuario **sin que el agente tenga las credenciales del usuario**. **IAM permission boundaries** limitan cada rol de agente, las **IAM Conditions** restringen por **Región, tag, ventana temporal y VPC de origen**, y hay elevación just-in-time con revocación automática. **AWS Config** y **EventBridge** alertan de cambios de política casi en tiempo real |
| **5 · Optimized** | Governance codificada, baselines de least privilege derivados de datos de **CloudTrail** y hallazgos agregados en **Security Hub CSPM**. Hallazgos de acceso no usado y autenticación inusual alimentan remediación automática, y los controles se validan con **ejercicios de red team contra rutas de impersonación y escalada de privilegios** |

### AgentCore Identity

De [Provide identity and credential management for agent applications](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html) y su [overview](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity-overview.html). Servicio de gestión de identidad y credenciales **diseñado específicamente para agentes de IA y cargas automatizadas**. Provee autenticación, autorización y gestión de credenciales para que agentes y herramientas accedan a recursos de AWS y a servicios de terceros **en nombre de los usuarios**, manteniendo controles de seguridad estrictos y pistas de auditoría.

Las identidades de agente se implementan como **workload identities con atributos especializados**, manteniendo compatibilidad con los patrones estándar de industria de workload identity. La integración es nativa con **AgentCore Runtime** y **AgentCore Gateway**, y soporta **SigV4, flujos OAuth 2.0 estandarizados y API keys**.

> El principio de diseño que declara: implementa controles que **verifican cada petición de forma independiente**, exigiendo verificación explícita para todo intento de acceso **independientemente del origen**.

Las [features de AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/key-features-and-benefits.html):

| Feature | Detalle |
| --- | --- |
| **Gestión centralizada de identidad** | Directorio unificado que actúa como **única fuente de verdad** para todas las identidades de agente. Cada agente recibe identidad única con metadatos (nombre, ARN, OAuth return URLs, fechas de creación y actualización). **El directorio funciona de forma similar a los Cognito User Pools**, como unidad de governance para configurar políticas sobre un conjunto común de identidades |
| **ARN jerárquico** | `arn:aws:bedrock-agentcore:region:account:workload-identity/directory/default/workload-identity/agent-name`. La **estructura jerárquica del path** permite organizar agentes lógicamente y **aplicar políticas a distintos niveles** (por ejemplo, a todos los agentes de un directorio) sin gestionar cada identidad individualmente |
| **Token vault** | Almacena **tokens OAuth 2.0, credenciales de cliente OAuth y API keys** con cifrado en reposo y en tránsito, usando claves KMS **gestionadas por el cliente o por el servicio**. Las credenciales solo son accesibles por agentes autorizados, para propósitos específicos, y **solo cuando presentan prueba verificable de workload identity** |
| **Validación independiente** | Sobre el modelo de scopes de OAuth 2.0, el vault **valida cada petición de acceso de forma independiente, incluso desde llamantes del mismo dominio de confianza**. La razón declarada: proteger los datos del usuario final de **código de agente malicioso o que se comporta mal** |
| **Flujos OAuth 2.0** | Soporte nativo de **client credentials grant (máquina a máquina, 2LO)** y **authorization code grant (acceso delegado por usuario, 3LO)**. Con 2LO los agentes se autentican directamente contra los resource servers sin interacción del usuario; con 3LO hay **consentimiento y autorización explícitos del usuario** |
| **Credential providers integrados** | Proveedores OAuth 2.0 preconfigurados para **Google, GitHub, Slack, Salesforce y Atlassian (Jira)**, con endpoints del servidor de autorización y parámetros específicos rellenados. Para integraciones propias, proveedores configurables compatibles con cualquier resource server OAuth 2.0 |
| **Impersonation flow** | Los agentes pueden acceder a recursos usando credenciales que se les proporcionan, realizando acciones en nombre de usuarios **manteniendo pistas de auditoría y controles de acceso** |
| **Integración con el SDK** | Anotaciones declarativas **`@requires_access_token`** y **`@requires_api_key`** que manejan automáticamente la obtención e inyección de credenciales. Gestionan además **expiración de token y requisitos de consentimiento**, generando las URLs de autorización y orquestando el flujo OAuth |

Capacidades complementarias documentadas: [inbound JWT authorizer](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/inbound-jwt-authorizer.html), [credential providers de salida](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity-outbound-credential-provider.html), [consent portal](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity-consent-portal.html) y [conexión a proveedores de identidad privados](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity-private-idp.html).

> La distinción **inbound / outbound** es la que conviene fijar: *inbound auth* controla quién puede invocar al agente o al gateway (OAuth JWT, IAM SigV4); *outbound auth* son las credenciales con las que el agente alcanza APIs y servicios de terceros (token vault, credential providers).

### Federación de identidad

| Mecanismo | Uso |
| --- | --- |
| **IAM Identity Center** | Acceso de **operadores humanos** a AWS, federado desde el IdP corporativo. Es el nivel 3 de AGENTSEC03 |
| **Amazon Cognito** | Identidad de los **usuarios de la aplicación**: user pools para autenticación y federación SAML/OIDC, identity pools para credenciales de AWS temporales |
| **AgentCore Identity** | Identidad de los **agentes** (workload identity), compatible con cualquier IdP y con proveedores de credenciales |
| **Inbound JWT authorizer** | Validación del token del usuario en la entrada del agente o del gateway, para que el contexto llegue como claims |
| **`GetWorkloadAccessTokenForJWT`** | Embute el contexto de usuario como claims para que **los servicios downstream apliquen autorización a nivel de usuario** sin que el agente tenga las credenciales del usuario |

Las tres identidades no se mezclan: el usuario final en Cognito, el operador en Identity Center, el agente en AgentCore Identity. Difuminarlas es el problema frecuente número 2 de AGENTSEC03.

### RBAC y least privilege sobre las APIs de FM

| Control | Aplicación concreta |
| --- | --- |
| **Rol por agente o por aplicación** | Nunca compartido, con convención consistente de nombres y tags (nivel 2 de AGENTSEC03) |
| **Acciones concretas** | `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`, `bedrock:Converse`, `bedrock:Retrieve`, `bedrock:ApplyGuardrail`, limitadas a los ARN aprobados |
| **Permission boundaries** | Techo de permisos que el rol no puede exceder aunque se amplíe su política de identidad. [Documentación](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html) |
| **IAM Conditions** | Restringir por **Región, tag, ventana temporal y VPC de origen**, según el nivel 4. [Claves de condición](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html) |
| **ABAC con tags** | Acceso condicionado a que los tags del principal coincidan con los del recurso: aislamiento por tenant sin una política por tenant |
| **Credenciales de corta vida** | **STS `AssumeRole`** con session policies |
| **Elevación just-in-time** | Con revocación automática, para operaciones de privilegio alto |
| **SCPs en Organizations** | Evitar que los agentes asuman roles humanos; restringir Regiones de procesamiento |
| **IAM Access Analyzer** | Hallazgos de baseline, generación de políticas de least privilege **a partir de la actividad real de CloudTrail**, y hallazgos de acceso externo no previsto |
| **AWS Config + EventBridge** | Alertas de cambios de política **casi en tiempo real** |
| **Security Hub CSPM** | Agregación de hallazgos en el nivel 5 |

**Protección de datos** complementaria, ya tratada en [Task 1.4](../domain-1/task-1-4-vector-stores.md) y [Task 1.6 · Skill 1.6.3](../domain-1/task-1-6-prompt-engineering-governance.md): **KMS** con claves gestionadas por el cliente, **Secrets Manager** para credenciales, **Macie** para descubrir PII en los buckets de origen, **AWS WAF** delante de la API, y el **AWS Encryption SDK** para cifrado en cliente.

> Recordatorio de la advertencia de Knowledge Bases que conviene repetir aquí: todo lo que se sincroniza desde un data source queda disponible para cualquiera con permisos `bedrock:Retrieve`, **incluidos datos con permisos controlados en el sistema de origen**. El RBAC del origen **no se hereda** en el retrieval; hay que reconstruirlo con filtros de metadatos o con [ACL awareness](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-acl.html).

---

## Skill 2.3.4 — Soluciones cross-environment y compliance entre jurisdicciones

> *Desarrollar soluciones de IA cross-environment para asegurar compliance de datos entre jurisdicciones habilitando el acceso a FMs (por ejemplo, usando AWS Outposts para integración de datos on-premises, AWS Wavelength para realizar despliegues de borde, routing seguro entre recursos cloud y on-premises).*

### Dos problemas distintos que el skill mezcla

Conviene separarlos desde el principio, porque las soluciones no son las mismas:

| Problema | Naturaleza | Herramientas |
| --- | --- | --- |
| **Residencia y soberanía de datos** | **Jurisdiccional**: el dato no puede salir de un territorio o de las instalaciones | Outposts, cross-Region inference **geográfica**, SCPs, PrivateLink |
| **Latencia de borde** | **Física**: la distancia al usuario o al dispositivo | Wavelength, Local Zones, CloudFront, Lambda@Edge, Global Accelerator |

Un despliegue en Wavelength no resuelve un requisito de residencia, y un Outpost no resuelve latencia de última milla móvil. El examen puede explotar esa confusión.

### AWS Outposts: la Región extendida a tus instalaciones

De [What is AWS Outposts?](https://docs.aws.amazon.com/outposts/latest/userguide/what-is-outposts.html). Servicio totalmente gestionado que **extiende infraestructura, servicios, APIs y herramientas de AWS a las instalaciones del cliente**. Da acceso local a infraestructura gestionada por AWS, permitiendo construir y ejecutar aplicaciones on-premises **con las mismas interfaces de programación que en las Regiones de AWS**, usando cómputo y almacenamiento locales para **latencia más baja y necesidades de procesamiento local de datos**.

Un Outpost es un pool de capacidad de cómputo y almacenamiento desplegado en la sede del cliente. **AWS opera, monitoriza y gestiona esa capacidad como parte de una Región de AWS.** Se crean subredes en el Outpost y se especifican al crear recursos como instancias EC2, volúmenes EBS, clústeres ECS e instancias RDS. Las instancias en subredes de Outpost **se comunican con otras instancias de la Región usando direcciones IP privadas, todo dentro de la misma VPC**.

Conceptos clave que conviene reconocer:

| Concepto | Definición |
| --- | --- |
| **Outpost site** | El edificio físico gestionado por el cliente donde AWS instala el Outpost. Debe cumplir requisitos de instalación, red y alimentación |
| **Outposts racks** | Form factor de rack estándar de industria de 42U, con servidores, switches, panel de parcheo, estante de alimentación y paneles ciegos |
| **Outposts ACE racks** | El rack de **Aggregation, Core, Edge** actúa como punto de agregación de red en despliegues multi-rack. **Obligatorio con cuatro o más racks de cómputo**; recomendado instalarlo pronto si se planea llegar a cuatro |
| **Outposts servers** | Form factor de servidor 1U o 2U instalable en rack estándar EIA-310D de 19 pulgadas y 4 postes. Para sedes con espacio limitado o menor capacidad |
| **Service link** | Ruta de red que permite la comunicación entre el Outpost y su Región asociada. **Cada Outpost es una extensión de una Availability Zone** y de su Región |
| **Local gateway (LGW)** | Router virtual de interconexión lógica que permite comunicación entre un **Outposts rack** y la red on-premises |
| **Local network interface** | Interfaz de red que permite comunicación desde un **Outposts server** y la red on-premises |

> **Restricción explícita**: **no se puede conectar un Outpost a otro Outpost o Local Zone que esté dentro de la misma VPC.**

La distinción **local gateway (racks) frente a local network interface (servers)** es el tipo de detalle que el examen puede preguntar: el mecanismo de conexión a la red local depende del form factor.

### AWS Wavelength: el borde de la red del operador

De [What is AWS Wavelength?](https://docs.aws.amazon.com/wavelength/latest/developerguide/what-is-wavelength.html). Permite construir aplicaciones que requieren **infraestructura de edge computing para entregar latencia baja a dispositivos móviles y usuarios finales**, o para aumentar la resiliencia de aplicaciones de borde existentes. Despliega cómputo y almacenamiento estándar de AWS **en el borde de las redes de los proveedores de servicios de comunicaciones (CSP)**.

Se extiende una VPC a una o más **Wavelength Zones** y se usan recursos como instancias EC2 para ejecutar las aplicaciones que requieren latencia baja o resiliencia de borde dentro de la zona, **comunicando sin fricción con los servicios de AWS desplegados en la Región padre**.

| Concepto | Definición |
| --- | --- |
| **Wavelength Zone** | Zona en la ubicación del operador donde se despliega la infraestructura. **Extensión lógica de la Región, gestionada por el control plane de la Región** |
| **VPC** | Abarca Availability Zones, **Local Zones y Wavelength Zones** |
| **Wavelength subnet** | Subred creada en una Wavelength Zone |
| **Carrier gateway** | Sirve dos propósitos: permite **tráfico entrante desde la red del operador** en una ubicación concreta, y **tráfico saliente hacia la red del operador y hacia internet** |
| **Network Border Group** | Conjunto único de Availability Zones, Local Zones o Wavelength Zones desde el que AWS anuncia direcciones IP |

**Recursos disponibles en Wavelength Zones**: instancias EC2, volúmenes EBS, subredes de VPC y carrier gateways. Además: EC2 Auto Scaling, clústeres de **EKS** y **ECS**, EC2 Systems Manager, **CloudWatch**, **CloudTrail**, **CloudFormation**, y **Application Load Balancer en zonas seleccionadas**.

> Detalle operativo que documenta AWS: al usar cualquiera de las interfaces (consola, CLI, SDKs) para las Wavelength Zones, **se usa la Región padre**. Los servicios mantienen sus propios namespaces (`ec2`, `ebs`).

**La consecuencia de diseño para GenAI**: la lista de servicios disponibles en Wavelength **no incluye Bedrock**. El patrón viable es preprocesamiento y postprocesamiento sensible a latencia en la Wavelength Zone, con la inferencia en la Región padre, o un modelo pequeño servido en EC2 o EKS dentro de la zona.

### Conectividad privada: PrivateLink y VPC

De [Protect your data using Amazon VPC and AWS PrivateLink](https://docs.aws.amazon.com/bedrock/latest/userguide/usingVPC.html). La recomendación oficial es usar una VPC para controlar el acceso a los datos: protege los datos y permite **monitorizar todo el tráfico de red de entrada y salida de los contenedores de job usando VPC Flow Logs**.

La protección adicional consiste en configurar la VPC **para que los datos no estén disponibles por internet**, creando un **VPC interface endpoint con AWS PrivateLink** para establecer una conexión privada.

Las funcionalidades de Bedrock donde se puede usar VPC según la documentación:

| Funcionalidad | Página |
| --- | --- |
| **Model customization** | [Proteger jobs de customización con una VPC](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-job-access-security.html) |
| **Batch inference** | [Proteger jobs de batch inference con una VPC](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-vpc.html) |
| **Knowledge Bases** | [Acceder a OpenSearch Serverless con interface endpoint](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vpc.html) |

Y las dos páginas de detalle: [interface VPC endpoints para Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html) y [restringir acceso a datos de S3 usando VPC](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-s3.html).

> Recomendación concreta al crear la VPC: usar **los ajustes DNS por defecto** para la tabla de rutas del endpoint, de modo que las URLs estándar de S3 resuelvan correctamente.

### Residencia de datos y la elección del inference profile

El mecanismo que decide dónde se procesa la inferencia es el inference profile, cubierto en [Task 1.2 · Skill 1.2.3](../domain-1/task-1-2-seleccion-y-configuracion-fm.md). El resumen aplicable a compliance:

| Opción | Dónde se procesa | Uso en compliance |
| --- | --- | --- |
| **Modelo en una sola Región** | Solo esa Región | Máximo control jurisdiccional, sin resiliencia cross-Region |
| **Cross-Region inference geográfica** (prefijo `us.`, `eu.`, `apac.`) | Entre las Regiones de **esa geografía** | Resiliencia manteniendo el dato dentro del área geográfica |
| **Cross-Region inference global** | Potencialmente cualquier Región del perfil | **Puede reducir costes de token**, pero pierde la garantía geográfica |

Los controles que imponen la elección:

| Control | Efecto |
| --- | --- |
| **SCPs en Organizations** | Restringir las Regiones de procesamiento a nivel organizativo |
| **IAM Conditions** | Restringir por Región, tag, ventana temporal y VPC de origen (nivel 4 de AGENTSEC03) |
| **CloudTrail** | El campo **`additionalEventData.inferenceRegion`** revela la Región real de procesamiento en cross-Region inference |
| **Guardrails cross-Region** | [Distribución de inferencia de guardrail entre Regiones](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region.html), que también tiene implicación jurisdiccional |

### Routing seguro entre cloud y on-premises

| Mecanismo | Papel |
| --- | --- |
| **AWS Direct Connect** | Conexión dedicada, con ancho de banda y latencia predecibles |
| **Site-to-Site VPN** | Túnel cifrado sobre internet, como respaldo o para menor volumen |
| **PrivateLink / interface endpoints** | Alcanzar las APIs de AWS **sin salir a internet** |
| **Outposts service link** | Comunicación entre el Outpost y su Región asociada |
| **Local gateway / local network interface** | Comunicación entre el Outpost y la red on-premises, según el form factor |
| **Route 53 Resolver** | Resolución DNS híbrida en ambos sentidos |
| **Global Accelerator** | Entrada a la red de AWS por el punto de presencia más cercano, con IPs estáticas |
| **VPC Flow Logs** | Monitorizar todo el tráfico de entrada y salida, según recomienda la documentación de Bedrock |

### Arquitectura de referencia por jurisdicción

```
┌─────────────────────────────────────────────────────────────────────┐
│ JURISDICCIÓN A · Región de AWS eu-central-1                          │
│   Bedrock con inference profile GEOGRÁFICO (eu.)                     │
│   Knowledge base + vector store en la Región                         │
│   SCP: restringe aws:RequestedRegion al conjunto europeo             │
│   CloudTrail: verificar additionalEventData.inferenceRegion          │
└─────────────────────────────────────────────────────────────────────┘
        ▲ PrivateLink (sin internet)
        │
┌───────┴─────────────────────────────────────────────────────────────┐
│ ON-PREMISES · AWS Outposts (extensión de una AZ de la Región)        │
│   Dato regulado que no puede salir de las instalaciones              │
│   EC2 / ECS / RDS en subredes del Outpost                            │
│   service link ──► Región      local gateway ──► red corporativa     │
│   Preprocesado, tokenización o anonimización ANTES de enviar a la    │
│   Región lo que sí puede salir                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ BORDE MÓVIL · AWS Wavelength Zone (red del operador)                 │
│   EC2 / EKS / ECS con ALB en zonas seleccionadas                     │
│   carrier gateway: entrada desde la red del operador                 │
│   Latencia baja al dispositivo; la inferencia de Bedrock sigue en    │
│   la Región padre (Bedrock no figura entre los servicios de la zona) │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Skill 2.3.5 — CI/CD y arquitecturas de GenAI gateway

> *Implementar pipelines CI/CD y arquitecturas de GenAI gateway para implementar patrones de consumo seguros y conformes en entornos empresariales (por ejemplo, usando AWS CodePipeline, AWS CodeBuild, frameworks de testing automatizado para despliegue y testing continuos de componentes GenAI con security scans y soporte de rollback, capas de abstracción centralizadas, mecanismos de observabilidad y control).*

### CodePipeline como modelo del proceso de release

De [What is AWS CodePipeline?](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html). Servicio de entrega continua para **modelar, visualizar y automatizar** los pasos necesarios para liberar software. Permite modelar y configurar rápidamente las distintas etapas de un proceso de release, y automatiza los pasos para liberar cambios de forma continua.

Conceptos que documenta y conviene conocer: [entrega e integración continuas](https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts-continuous-delivery-integration.html), [conceptos de CodePipeline](https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts.html), [cómo funcionan las ejecuciones](https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts-how-it-works.html), [artefactos de entrada y salida](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome-introducing-artifacts.html), [stage conditions](https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts-how-it-works-conditions.html) y [tipos de pipeline](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipeline-types.html).

> Las **stage conditions** son la pieza que hace de puerta de calidad: condiciones que deben cumplirse para que una etapa entre, tenga éxito o falle, lo que permite bloquear la promoción sin escribir lógica propia.

### Las herramientas de Developer Tools en alcance

| Servicio | Papel en el pipeline de un componente GenAI |
| --- | --- |
| **AWS CodePipeline** | Orquesta las etapas del release |
| **AWS CodeBuild** | Ejecuta build, tests y **security scans** |
| **AWS CodeDeploy** | Despliegue con estrategias controladas y **rollback** |
| **AWS CodeArtifact** | Repositorio de artefactos y dependencias, con control de procedencia |
| **AWS CloudFormation** y **AWS CDK** | La infraestructura como código: knowledge bases, guardrails, gateways, endpoints |
| **AWS Service Catalog** | Productos aprobados y parametrizados para que los equipos despliguen patrones GenAI conformes |
| **AWS X-Ray** | Trazas distribuidas del componente desplegado. Detalle en [Task 2.4 · Skill 2.4.3](./task-2-4-integraciones-api-fm.md#skill-243--sistemas-de-fm-resilientes) |
| **Kiro** | IDE agentic con workflows spec-driven, **steering files** para estándares de equipo y **hooks** para comprobaciones automatizadas de calidad, según lo nombra el [Agentic AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html) |

> Recordatorio de [Task 2.2 · Skill 2.2.2](./task-2-2-despliegue-de-modelos.md#skill-222--retos-propios-de-los-llms-frente-a-despliegues-ml-tradicionales): **Custom Model Import no se puede usar con CloudFormation**. Un pipeline que despliega un modelo importado necesita un paso de SDK o CLI, no una plantilla.

### Qué se prueba en un pipeline de componente GenAI

Lo que diferencia este pipeline de uno convencional es que el artefacto no es determinista. Las capas de prueba, con lo cubierto en [Task 1.6 · Skill 1.6.4](../domain-1/task-1-6-prompt-engineering-governance.md) como base:

| Etapa | Qué valida | Herramienta |
| --- | --- | --- |
| **Build** | Compilación, dependencias, linting | CodeBuild |
| **Security scan** | Vulnerabilidades en dependencias y código | CodeBuild con el escáner elegido; Amazon Q Developer para escaneo de código |
| **Validación de IaC** | Que la plantilla es correcta y cumple las políticas | CloudFormation, CDK, Service Catalog |
| **Aserciones deterministas** | Esquema JSON de salida, presencia de citas, longitud, términos prohibidos | Lambda |
| **Evaluación de calidad** | Scores sobre un dataset de regresión, judge model | [Bedrock evaluations](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html), **AgentCore Evaluations** |
| **Tests adversarios de contrato** | **Bloquear regresiones de prompt injection**, tal como pide el nivel 5 de [AGENTREL02](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel02.html) | Suite propia en CodeBuild |
| **Fault injection** | Que las cadenas de fallback funcionan. El nivel 4 de [AGENTREL06](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel06.html) pone **FIS dentro de CI/CD** | AWS Fault Injection Service |
| **Registro de capacidades** | Que el catálogo refleja lo desplegado: el nivel 4 de [AGENTREL04](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentrel04.html) **automatiza el registro en CI/CD** | AWS Agent Registry |
| **Comparación de versiones de prompt** | Antes de migrar tráfico, según el nivel 4 de AGENTREL02 | AgentCore Evaluations |

### Pipeline de referencia con rollback

```
Commit (prompt, código de agente, plantilla de IaC, esquema de herramienta)
   │
   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ CodeBuild · build + tests unitarios + SECURITY SCAN                  │
│   dependencias desde CodeArtifact (procedencia controlada)            │
└──────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ CloudFormation / CDK · despliegue a preproducción                    │
│   knowledge base · guardrail · gateway · endpoint · versión de prompt │
└──────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Suite de calidad GenAI                                               │
│   Lambda: aserciones deterministas                                    │
│   Bedrock / AgentCore Evaluations: score sobre dataset de regresión   │
│   tests adversarios: prompt injection                                 │
│   FIS: valida cadenas de fallback                                     │
└──────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Stage condition: ¿supera el umbral de la versión en producción?      │
│   no ──► no se promueve · notificación SNS                            │
└──────────────────────────────────────────────────────────────────────┘
   │ sí
   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Promoción gradual                                                    │
│   AppConfig publica la versión activa de prompt y de modelo           │
│     · validators comprueban la configuración                          │
│     · deployment strategy gradual                                     │
│   AgentCore Runtime: endpoint apunta a la nueva versión inmutable     │
│   CodeDeploy: despliegue del cómputo con estrategia controlada        │
│   AgentCore Gateway: traffic splitting para A/B (AgentCore            │
│     Optimization usa este mecanismo)                                  │
│   Agent Registry: registro de capacidades actualizado automáticamente │
└──────────────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Alarmas de CloudWatch vigilando en producción                        │
│   PassRate · score del judge · groundedness · p95 · throttling        │
│   intervenciones de guardrail · profundidad de cola de aprobación     │
│      │                                                                │
│      └─ se dispara ──► ROLLBACK AUTOMÁTICO                            │
│                         · AppConfig revierte a la versión anterior    │
│                         · endpoint de AgentCore a la versión previa   │
│                         · CodeDeploy revierte el despliegue           │
└──────────────────────────────────────────────────────────────────────┘
```

Los tres mecanismos de rollback son independientes y conviene no confundirlos: **AppConfig** revierte configuración (qué prompt, qué modelo, qué versión de guardrail); **los endpoints versionados de AgentCore Runtime** revierten el código del agente **sin downtime**; **CodeDeploy** revierte el cómputo. Las **versiones inmutables** de AgentCore Runtime y de Prompt Management son lo que hace posible el rollback: se apunta a una versión anterior, no se reconstruye.

### La capa de abstracción centralizada: el GenAI gateway

El skill pide "capas de abstracción centralizadas, observabilidad y mecanismos de control". El servicio que AWS documenta para esto es **AgentCore Gateway**, cuya mecánica completa está en [Task 2.1 · Skill 2.1.6](./task-2-1-agentic-ai-y-herramientas.md#skill-216--integraciones-de-herramientas-y-operaciones-fiables). Lo que aporta a cada requisito del skill:

| Requisito del skill | Qué lo cubre |
| --- | --- |
| **Capa de abstracción centralizada** | **Inference targets**: enrutan tráfico de LLM a uno o varios proveedores por un **endpoint unificado**, seleccionando destino según el campo `model` de la petición, dando a los agentes **una interfaz única y consistente** entre Bedrock, OpenAI, Anthropic y otros |
| **Punto de entrada único** | El gateway es un **punto único y seguro de acceso** para alcanzar herramientas, otros agentes y modelos |
| **Control de consumo** | **Inbound authorizer** obligatorio (OAuth JWT, IAM SigV4, authenticate only) y **AgentCore Policy** interceptando cada llamada de herramienta antes de ejecutarla |
| **Credenciales centralizadas** | **Credential providers** y el **token vault** de AgentCore Identity, en lugar de secretos repartidos por aplicación |
| **Catálogo y descubrimiento** | **AWS Agent Registry** con workflow de aprobación, de modo que solo los recursos que cumplen los criterios de seguridad, compliance y calidad son descubribles |
| **Observabilidad** | **AgentCore Observability** con telemetría **OpenTelemetry**, más las métricas y logs de decisiones de **AgentCore Policy** en CloudWatch |
| **A/B testing y promoción** | **Traffic splitting a través de Gateway**, el mecanismo que usa **AgentCore Optimization** para validar cambios de configuración con experimentos controlados |

```
        Aplicaciones · agentes · equipos
                │
                ▼
┌───────────────────────────────────────────────────────────────────┐
│                      GenAI GATEWAY                                │
│                                                                   │
│  ENTRADA    inbound authorizer: OAuth JWT · IAM SigV4             │
│             AWS WAF delante de la API expuesta                    │
│  ───────────────────────────────────────────────────────────────  │
│  CONTROL    AgentCore Policy (Cedar): permit/forbid por tool call │
│             condiciones input-based · temporales · de provider    │
│             capability toggling en runtime, sin redespliegue      │
│  ───────────────────────────────────────────────────────────────  │
│  RUTEO      inference targets  → Bedrock · otros proveedores      │
│             MCP targets        → herramientas agregadas           │
│             HTTP targets       → agentes y servicios A2A          │
│  ───────────────────────────────────────────────────────────────  │
│  CREDENCIAL credential providers + token vault (KMS del cliente)  │
│  ───────────────────────────────────────────────────────────────  │
│  OBSERVA    AgentCore Observability (OTEL) · CloudWatch           │
│             métricas y logs de decisiones de política             │
│             traffic splitting para A/B                            │
└───────────────────────────────────────────────────────────────────┘
                │
                ▼
   Bedrock · SageMaker AI · AgentCore Runtime · APIs · Lambda · legacy
```

### Observabilidad y control transversales

| Necesidad | Mecanismo |
| --- | --- |
| **Quién creó o cambió qué** | **CloudTrail**: eventos de management de las APIs de Bedrock, AgentCore y Agent Registry |
| **Qué se envió y qué se recibió** | [Model invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) a CloudWatch Logs y S3 |
| **Coste por aplicación o equipo** | Tags en **application inference profiles** con [cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html) |
| **Trazas distribuidas** | **X-Ray** y **AgentCore Observability** con OTEL |
| **Cambios de política casi en tiempo real** | **AWS Config** y **EventBridge**, según el nivel 4 de AGENTSEC03 |
| **Postura agregada de seguridad** | **Security Hub CSPM**, nivel 5 de AGENTSEC03 |
| **Anomalías de comportamiento** | **CloudWatch Anomaly Detection** sobre baselines por agente, nivel 3 de AGENTREL02 |
| **Hotspots de contención** | **CloudWatch Contributor Insights**, nivel 5 de AGENTREL04 |
| **Monitorización sintética** | **CloudWatch Synthetics** para comprobar el endpoint de forma continua |
| **Dashboards** | **Amazon Managed Grafana** |

### Consumo conforme: el conjunto de controles

```
GOVERNANCE   Service Catalog: solo patrones aprobados y parametrizados
             SCPs: Regiones permitidas, servicios permitidos
             Agent Registry: workflow de aprobación de lo descubrible
             Guardrails enforcements cross-account desde una cuenta
               de governance
IDENTIDAD    IAM Identity Center (operadores) · Cognito (usuarios)
             AgentCore Identity (agentes) · rol por agente
             permission boundaries + IAM Conditions
RED          PrivateLink · VPC endpoints · VPC Flow Logs
             Direct Connect / VPN para on-premises
             WAF delante de la API
DATOS        KMS con claves del cliente · Secrets Manager
             Macie sobre los buckets de origen
             inference profile geográfico para residencia
ENTREGA      CodePipeline con stage conditions
             security scans en CodeBuild
             evaluaciones de calidad como puerta de promoción
             rollback por AppConfig, versiones de AgentCore y CodeDeploy
OPERACIÓN    AgentCore Policy para control en runtime
             AgentCore Observability + CloudWatch + X-Ray
             CloudTrail para auditoría
```
