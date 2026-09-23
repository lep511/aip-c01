# Dominio 4 — Operational Efficiency & Optimization for GenAI Applications
## Informe técnico completo y guía de estudio orientada al examen **AWS Certified Generative AI Developer – Professional (AIP-C01)**

> **Fecha de elaboración:** 23 de septiembre de 2026
> **Alcance:** Content Domain 4 completo (Task 4.1, Skills 4.1.1–4.1.4; Task 4.2, Skills 4.2.1–4.2.6; Task 4.3, Skills 4.3.1–4.3.6)
> **Enfoque:** qué exige el examen, qué servicios de AWS lo resuelven, cómo se implementa, con qué métricas y umbrales, y qué trampas aparecen en las preguntas.
> **Advertencia sobre precios:** todas las tarifas citadas son **referencias de EE. UU. vigentes a septiembre de 2026** y cambian con frecuencia. Sirven para razonar el *modelo mental* de costos, no para presupuestar. Verificá siempre la página de precios de Amazon Bedrock.

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [El Dominio 4 en el contexto del examen AIP-C01](#2-el-dominio-4-en-el-contexto-del-examen-aip-c01)
3. [Marco conceptual: las tres ecuaciones de la eficiencia GenAI](#3-marco-conceptual-las-tres-ecuaciones-de-la-eficiencia-genai)
4. [Task 4.1 — Optimización de costos y eficiencia de recursos](#4-task-41--optimización-de-costos-y-eficiencia-de-recursos)
   - 4.1 [4.1.1 Sistemas de eficiencia de tokens](#41-skill-411--sistemas-de-eficiencia-de-tokens)
   - 4.2 [4.1.2 Marcos de selección de modelos costo-efectivos](#42-skill-412--marcos-de-selección-de-modelos-costo-efectivos)
   - 4.3 [4.1.3 Sistemas de alto rendimiento (batching, capacidad, auto-scaling, PT)](#43-skill-413--sistemas-de-alto-rendimiento)
   - 4.4 [4.1.4 Sistemas de caché inteligente](#44-skill-414--sistemas-de-caché-inteligente)
5. [Task 4.2 — Optimización del desempeño de la aplicación](#5-task-42--optimización-del-desempeño-de-la-aplicación)
   - 5.1 [4.2.1 Sistemas responsivos: latencia vs. costo](#51-skill-421--sistemas-responsivos-latencia-vs-costo)
   - 5.2 [4.2.2 Desempeño de recuperación](#52-skill-422--desempeño-de-recuperación)
   - 5.3 [4.2.3 Optimización de throughput](#53-skill-423--optimización-de-throughput)
   - 5.4 [4.2.4 Mejora del desempeño del FM (parámetros y A/B)](#54-skill-424--mejora-del-desempeño-del-fm)
   - 5.5 [4.2.5 Asignación eficiente de recursos](#55-skill-425--asignación-eficiente-de-recursos-para-cargas-fm)
   - 5.6 [4.2.6 Optimización de workflows GenAI](#56-skill-426--optimización-de-workflows-genai)
6. [Task 4.3 — Sistemas de monitoreo](#6-task-43--sistemas-de-monitoreo-para-aplicaciones-genai)
   - 6.1 [4.3.1 Observabilidad holística](#61-skill-431--observabilidad-holística)
   - 6.2 [4.3.2 Monitoreo proactivo y KPIs de GenAI](#62-skill-432--monitoreo-proactivo-y-kpis-de-genai)
   - 6.3 [4.3.3 Observabilidad integrada y trazabilidad forense](#63-skill-433--observabilidad-integrada-y-trazabilidad-forense)
   - 6.4 [4.3.4 Frameworks de desempeño de herramientas](#64-skill-434--frameworks-de-desempeño-de-herramientas)
   - 6.5 [4.3.5 Gestión operativa de vector stores](#65-skill-435--gestión-operativa-de-vector-stores)
   - 6.6 [4.3.6 Frameworks de troubleshooting específicos de FM](#66-skill-436--frameworks-de-troubleshooting-específicos-de-fm)
7. [Arquitectura de referencia: el plano de control de eficiencia y observabilidad](#7-arquitectura-de-referencia)
8. [Cheat sheet: tablas de decisión para el examen](#8-cheat-sheet-tablas-de-decisión-para-el-examen)
9. [Patrones de pregunta y trampas frecuentes](#9-patrones-de-pregunta-y-trampas-frecuentes)
10. [Checklists operativos](#10-checklists-operativos)
11. [Anexos](#11-anexos)
    - A. [Snippets de código](#anexo-a-snippets-de-código)
    - B. [Consultas CloudWatch Logs Insights y Athena](#anexo-b-consultas-cloudwatch-logs-insights-y-athena)
    - C. [Glosario](#anexo-c-glosario)
    - D. [Fuentes consultadas](#anexo-d-fuentes-consultadas)
12. [Plan de repaso y práctica (5 días)](#12-plan-de-repaso-y-práctica-5-días)

---

## 1. Resumen ejecutivo

El Dominio 4 pesa **12 % del contenido puntuado** (≈8 de las 65 preguntas puntuadas). Es el dominio donde el examen comprueba si sabés convertir un prototipo que funciona en un sistema que **sigue funcionando cuando la factura y los usuarios crecen**.

Las seis ideas fuerza:

| # | Idea fuerza | Consecuencia práctica |
|---|---|---|
| 1 | **La factura de GenAI tiene cuatro capas, no una**: (1) tokens de inferencia, (2) *modo de facturación* (Standard/Flex/Priority/Batch/Reserved/PT), (3) infraestructura alrededor (vector store, guardrails, logging, flows) y (4) el costo del propio sistema de evaluación. | Optimizar solo el precio por token es optimizar la capa más chica del problema. |
| 2 | **El lever #1 es la selección y el routing de modelo**, no el prompt. Enrutar cada consulta al modelo adecuado rinde 30–50 % de ahorro. | Frameworks de "cost-capability tradeoff" + Intelligent Prompt Routing + cascade routing + destilación. |
| 3 | **La latencia se descompone**: TTFT (tiempo al primer token) + OTPS (tokens de salida por segundo) × longitud de la respuesta. Se optimizan por separado, con palancas distintas. | Streaming y prompt caching atacan TTFT; tamaño de salida y modelo atacan la generación. |
| 4 | **El throughput es un problema de cuota, no de hardware**. Bedrock aplica RPM y TPM por modelo/región/cuenta, con **reserva previa según `maxTokens`** y **multiplicador de consumo (burndown) sobre los tokens de salida**. | Un `maxTokens` alto "regala" cuota; el paralelismo descontrolado provoca throttling aunque el consumo real sea bajo. |
| 5 | **La observabilidad GenAI es de cuatro señales**: métricas operativas, logs, trazas y **evaluaciones de calidad**. Las tres primeras no detectan una respuesta plausiblemente incorrecta. | CloudWatch GenAI Observability + Model Invocation Logging + X-Ray/ADOT + evaluación continua muestreada. |
| 6 | **Monitorear no es solo medir el sistema: es medir el negocio** (costo por tarea resuelta, deflexión, tiempo ahorrado) y poder atribuir el gasto (inference profiles + tags, IAM principal, CUR 2.0). | Sin atribución no hay FinOps; sin métricas de negocio no hay financiamiento. |

**Mapa mínimo de servicios AWS para este dominio:**

- **Palancas de costo:** Intelligent Prompt Routing, prompt caching, Batch/Flex, Reserved tier, Provisioned Throughput, Model Distillation, Advanced Prompt Optimization.
- **Palancas de latencia/throughput:** ConverseStream, latency-optimized inference, Priority tier, cross-region inference (CRIS), conexiones reutilizadas, paralelización con Step Functions.
- **Caché:** prompt caching (nativo) + caché de respuesta exacta y semántica en ElastiCache/Redis, API Gateway caching, CloudFront para activos.
- **Observabilidad:** CloudWatch (namespace `AWS/Bedrock`, `bedrock-agentcore`, `AWS/Bedrock/KnowledgeBases`, guardrails), Model Invocation Logging, X-Ray + ADOT, GenAI Observability dashboards, CloudWatch Synthetics, Transaction Search.
- **Control de costos:** Cost Explorer, AWS Budgets, Cost Anomaly Detection, application inference profiles + cost allocation tags, CUR 2.0 + Athena, IAM principal cost allocation.
- **Calidad como parte de la observabilidad:** AgentCore Evaluations (online), Guardrails (grounding/reasoning), golden datasets y output diffing.

---

## 2. El Dominio 4 en el contexto del examen AIP-C01

### 2.1 Datos del examen

| Dato | Valor |
|---|---|
| Código | AIP-C01 · Nivel Professional |
| Pesos | D1 **31 %** · D2 **26 %** · D3 **20 %** · **D4 12 %** · D5 11 % |
| Preguntas | 65 puntuadas + ~10 no puntuadas |
| Aprobación | 750/1000, modelo compensatorio (no hay mínimos por dominio) |
| Tipo de pregunta | Elección múltiple (1 correcta de 4) y respuesta múltiple (2+ de 5+, hay que acertar todas) |
| Perfil objetivo | 2+ años en aplicaciones productivas en AWS, ≈1 año hands-on en GenAI |

### 2.2 Qué evalúa el Dominio 4 (enunciado oficial agrupado)

**Task 4.1 — Implementar optimización de costos y eficiencia de recursos.** Eficiencia de tokens (estimación y tracking, optimización de la ventana de contexto, control del tamaño de respuesta, compresión de prompts, poda de contexto, limitación de respuestas); marcos de selección de modelo costo-efectivos (trade-off capacidad/costo, uso por niveles según complejidad, balance costo/calidad, ratio precio-rendimiento, patrones de inferencia eficientes); sistemas de alto rendimiento (batching, planificación de capacidad, monitoreo de utilización, auto-scaling, optimización de provisioned throughput); caching inteligente (semántico, *fingerprinting*, en el borde, hashing determinista, prompt caching).

**Task 4.2 — Optimizar el desempeño de la aplicación.** Latencia vs. costo (pre-cómputo, modelos optimizados para latencia, requests en paralelo, streaming, benchmarks); desempeño de recuperación (optimización de índices, preprocesamiento de consultas, búsqueda híbrida con scoring propio); throughput (optimización de procesamiento de tokens, batch, gestión de invocaciones concurrentes); desempeño del FM (parámetros específicos del modelo, A/B testing, selección de temperatura/top-k/top-p); asignación de recursos (planificación por patrones de prompt/completado, monitoreo de utilización, auto-scaling adaptado a tráfico GenAI); optimización de workflows (profiling de la API, optimización de consultas al vector DB, técnicas de reducción de latencia, patrones de comunicación eficientes).

**Task 4.3 — Implementar sistemas de monitoreo para aplicaciones GenAI.** Observabilidad holística (métricas operativas, trazas de desempeño, trazas de interacción con el FM, métricas de impacto de negocio, dashboards propios); monitoreo proactivo y KPIs específicos (CloudWatch para tokens, efectividad de prompts, tasas de alucinación, calidad de respuesta; detección de anomalías para picos de tokens y *response drift*; Model Invocation Logs para análisis de request/response; benchmarks; detección de anomalías de costo); observabilidad integrada (dashboards operativos, visualizaciones de impacto de negocio, monitoreo de cumplimiento, trazabilidad forense y auditoría, tracking de interacción de usuario, tracking de patrones de comportamiento del modelo); desempeño de herramientas (patrones de llamada, recolección de métricas, observabilidad de tool calling y coordinación multi-agente, líneas base de uso para detección de anomalías); gestión operativa de vector stores (monitoreo de desempeño, optimización automatizada de índices, validación de calidad de datos); frameworks de troubleshooting específicos de FM (golden datasets, *output diffing*, trazas de rutas de razonamiento, pipelines de observabilidad especializados).

### 2.3 Servicios en alcance relevantes a este dominio

| Categoría | Servicios | Uso en D4 |
|---|---|---|
| **Machine Learning** | Bedrock (todas las capacidades), **AgentCore** (Runtime, Gateway, Memory, Observability, Evaluations), Knowledge Bases, Prompt Management/Flows, SageMaker AI (endpoints, Serverless, Inference Components), SageMaker Model Monitor, JumpStart, Titan | Inferencia, caché, batch, PT, destilación, auto-scaling, monitoreo de endpoints |
| **Management & Governance** | **CloudWatch** (+ Logs, Synthetics, Application Signals, Transaction Search, Metric Streams), **CloudTrail**, **AWS Budgets / Cost Explorer / Cost Anomaly Detection**, AWS AppConfig, Managed Grafana, Well-Architected Tool | Observabilidad, alarmas, anomalías de costo, control de flags |
| **Application Integration** | **Step Functions** (Map, paralelismo, reintentos), EventBridge, SNS, SQS | Orquestación de concurrencia, colas, fan-out, notificaciones |
| **Compute** | **Lambda** (+ alias ponderados, provisioned concurrency), ECS/EKS/Fargate, EC2 | Ejecución de la aplicación, cachés, MCP servers |
| **Analytics** | **OpenSearch**, **Quick Sight**, Athena, Glue, Kinesis/MSK | Vector store, dashboards de negocio, análisis de logs y CUR |
| **Database** | **ElastiCache (Valkey/Redis)**, Aurora (pgvector), DynamoDB, Neptune Analytics, MemoryDB | Caché semántica y de sesión, vector store, memoria de agentes |
| **Storage / Network** | **S3** (+ lifecycle, Intelligent-Tiering, S3 Vectors), **CloudFront**, API Gateway, PrivateLink, VPC | Resultados de batch, logs, activos en el borde, endpoints privados |
| **Developer Tools** | **X-Ray**, CodePipeline/CodeBuild/CodeDeploy, CDK/CloudFormation | Trazas, pipelines de despliegue y gates |

> **Lectura estratégica:** muchas respuestas correctas del D4 no son "un servicio de IA" sino **el servicio de plataforma correcto**: `ElastiCache` para caché semántica, `Step Functions Map` para controlar concurrencia, `AppConfig` para conmutar modelos, `Cost Anomaly Detection` para detectar picos, `CloudWatch Synthetics` para tráfico sintético, `Athena` sobre CUR para atribución. No perder ese inventario de vista al elegir opción.

---

## 3. Marco conceptual: las tres ecuaciones de la eficiencia GenAI

### 3.1 Ecuaciones de costo, latencia y throughput

**Costo (mensual):**
```
Costo = Σ_modelos [ (tok_in × P_in) + (tok_out × P_out) ] × volumen
        + costo de infraestructura alrededor
        + costo del sistema de calidad (jueces, evaluaciones, anotación)
```
Tres observaciones que casi todo el mundo descubre tarde:

1. **Los tokens de salida cuestan 3–5× los de entrada.** Cortar 200 tokens de respuesta suele rendir más que recortar 1.000 tokens de contexto.
2. **El volumen no crece linealmente**: los agentes amplifican cada consulta de usuario **5–10×** respecto del prompt/respuesta visible (razonamiento multi-paso, llamadas de herramientas, reintentos).
3. **La infraestructura alrededor puede superar a la inferencia**: un vector store administrado con piso mensual, re-ranking, guardrails, logging y transiciones de Flows se suman como líneas propias.

**Latencia (percibida por el usuario):**
```
Latencia total = Latencia de red + TTFT + (n_tokens_salida ÷ OTPS) + overhead de post-proceso
                 └─ visible ─┘   └──────── generación ────────┘
```
- **TTFT (Time To First Token)** es lo que siente el usuario en una app de streaming; se ataca con caching de prefijo, modelo más chico, CRIS y conexiones reutilizadas.
- **OTPS** domina cuando la respuesta es larga; se ataca limitando la salida y eligiendo un modelo con mejor velocidad de generación.

**Throughput (capacidad):**
```
Throughput efectivo = min( RPM_reservado , TPM_reservado , concurrencia del cliente , capacidad del modelo )
```
Bedrock resuelve cuotas **por modelo, por región y por cuenta**, y aplica:
- **Reserva previa de cuota** en función de `maxTokens` (reserva "input + max" antes de generar).
- **Multiplicador de burndown** sobre los tokens de salida (históricamente 1 token de salida consume ~5 unidades de cuota).

Consecuencia: **`maxTokens` desproporcionado y picos de concurrencia causan throttling aunque el consumo total esté muy por debajo de la cuota**. Es un patrón de examen.

### 3.2 Las seis palancas, ordenadas por relación beneficio/esfuerzo

| # | Palanca | Impacto típico | Esfuerzo | Riesgo |
|---|---|---|---|---|
| 1 | **Selección/routing de modelo** (incluye IPR, escalado en cascada, destilación) | 30–50 % de ahorro en gasto de modelos | Medio | Bajo si se valida calidad con dataset dorado |
| 2 | **Prompt caching** para prefijos estables | hasta 90 % de descuento en la porción cacheada; latencia hasta −85 % | Bajo (configuración) | Muy bajo |
| 3 | **Batch / Flex** para trabajo no interactivo | −50 % | Medio (arquitectura por colas) | Muy bajo |
| 4 | **Reducción de tokens de salida** (formato, límites, structured outputs) | Medio (y ataca lo más caro por token) | Bajo (prompt engineering) | Bajo |
| 5 | **Reserved / Provisioned Throughput** para carga sostenida | 20–50 % según compromiso y utilización | Medio (planificación) | **Medio-alto: el recurso se paga ocioso** |
| 6 | **Optimización del vector store** (store correcto, dimensiones, cuantización, filtros) | Hasta 90 % en storage/consulta según elección | Medio | Bajo, con tradeoff de latencia |

### 3.3 El árbol de decisión que conviene tener memorizado

```
¿La latencia importa (usuario esperando)?
├─ SÍ → ¿Es interactivo y crítico?      → Priority + streaming + modelo pequeño/rápido + prompt caching
│        ¿Es interactivo y normal?      → Standard + streaming + prompt caching + CRIS
└─ NO → ¿Puede esperar hasta 24 h?      → Batch (−50 %)  ·  ¿Tolera latencia variable? → Flex (−50 %)
         ¿Es carga sostenida y predecible? → Reserved (modelos estándar) o PT (modelos custom/fine-tuned)
```

---

## 4. Task 4.1 — Optimización de costos y eficiencia de recursos

### 4.1 Skill 4.1.1 — Sistemas de eficiencia de tokens

> *"Reducir el costo de FM manteniendo efectividad: estimación y tracking de tokens, optimización de la ventana de contexto, control del tamaño de respuesta, compresión de prompts, poda de contexto, limitación de respuestas."*

#### 4.1.1.1 Medición primero: no se puede optimizar lo que no se mide

**`CountTokens` API (Bedrock Runtime)** — la pieza central:

| Característica | Detalle |
|---|---|
| Qué hace | Devuelve el número de tokens **según la tokenización del modelo indicado**, para el request que se enviaría |
| Precisión | **Coincide con lo que se facturaría** en `InvokeModel`/`Converse` |
| Formatos | Acepta los mismos formatos que `InvokeModel` y `Converse` (texto plano y conversación estructurada, incluyendo `system` y `toolConfig`) |
| Costo | **Sin cargo** |
| Usos | Estimar costo antes de invocar, verificar que el prompt entra en la ventana, planificar presupuesto |
| Limitaciones | No soporta entradas de documento (PDF); no acepta IDs de *inference profile* directamente (hay que resolver al modelo base) |
| Alternativa aproximada | `caracteres ÷ 4` (o ÷ 6 en algunas guías de AWS) — sirve para pre-chequeos, **no** para facturación |

**Dónde medir de verdad:** las respuestas de Bedrock incluyen `usage` con `inputTokens`, `outputTokens`, `cacheReadInputTokens`, `cacheWriteInputTokens`. A nivel plataforma, **Model Invocation Logging** (apagado por defecto) publica request/response/metadata a CloudWatch Logs o S3, y CloudWatch expone `InputTokenCount`/`OutputTokenCount` por modelo.

**Taxonomía de tokens que conviene trackear por workflow:**

| Métrica | Fórmula | Qué delata |
|---|---|---|
| Tokens por request | in + out | Tamaño base del prompt |
| Tokens de entrada por sección | system / tools / RAG / historial / usuario | Dónde está el "prompt bloat" |
| Ratio salida:entrada | out ÷ in | Prompts que producen respuestas demasiado largas |
| Tokens por sesión / tarea | Σ por sesión | Amplificación por agentes y multi-turno |
| Crecimiento semanal por versión de prompt | Δ% vs. baseline | Deriva silenciosa de plantillas |
| Tokens por intent de herramienta | por tool call | Herramientas que devuelven payloads enormes |

#### 4.1.1.2 Optimización de la ventana de contexto

El presupuesto debe ser **explícito y calculado**, no implícito:

```
Ventana del modelo
 − definiciones de tools (se pagan en cada request)
 − presupuesto de razonamiento (si el modelo usa thinking)
 − maxTokens de salida reservado
 − buffer de seguridad (5–10 %)
 ─────────────────────────────────────────
 = presupuesto para system + historial + contexto RAG + mensaje de usuario
```

Técnicas de **poda y compresión de contexto**:

| Técnica | Cómo | Cuándo usar | Riesgo |
|---|---|---|---|
| **Ventana deslizante** | Descartar los turnos más antiguos | Chat donde lo reciente pesa más | Pierde compromisos previos |
| **Resumen incremental** | Un modelo económico comprime el historial | Sesiones largas con estado acumulado | Pérdida (lossy) de detalles |
| **Extracción de campos** | Enviar solo los campos necesarios de un JSON, no el objeto completo | Tool outputs grandes | Requiere contrato de datos |
| **Deduplicación** | Eliminar contexto inyectado dos veces (RAG + memoria + archivos) | Casi siempre | Ninguno |
| **Recorte de tool outputs** | Truncar/resumir resultados antes de reinyectarlos | Agentes con APIs verbosas | Puede cortar la evidencia |
| **Compresión de prompts** | Reescribir plantillas con Advanced Prompt Optimization | System prompts que crecieron | Revalidar calidad |
| **Selección de k** | Menos chunks, mejor rankeados (rerank) | RAG con ruido | Recall si se recorta de más |
| **Caching de prefijo** | Convertir contexto estable en tokens cacheados | System prompt y documentos fijos | Ninguno (ver 4.1.4) |

> **Regla de oro contra el "más contexto es mejor":** contexto adicional tiene rendimiento decreciente y puede empeorar la calidad (*lost in the middle*), además de encarecer cada request. La métrica correcta no es "cuánto contexto entra", sino **"cuánto contexto se usa"**.

#### 4.1.1.3 Control del tamaño y formato de la respuesta

Como los tokens de salida son los más caros y los que dominan la latencia de generación:

- **`maxTokens` ajustado por caso de uso** (no por miedo): un valor excesivo reserva cuota (burndown) y habilita respuestas kilométricas.
- **`stopSequences`** para cortar patrones indeseados (por ejemplo, evitar que el modelo siga generando ejemplos tras la respuesta).
- **Instrucciones de longitud explícitas** ("responde en ≤120 palabras", "devuelve solo la tabla").
- **Rúbricas del juez que penalicen la verbosidad** (la verbosidad contamina también la evaluación).
- **Structured outputs / constrained decoding** (ver abajo): evita texto ceremonial, reintentos por JSON inválido y post-procesamiento.

#### 4.1.1.4 Structured outputs: menos tokens, menos reintentos, menos errores

Disponible desde **febrero de 2026** vía `outputConfig.textFormat` con `type: json_schema`:

| Aspecto | Detalle |
|---|---|
| Mecanismo | **Decodificación restringida**: el esquema se compila a una gramática y se **enmascaran los tokens inválidos** durante la generación |
| Garantía | La salida **no puede** violar el esquema (no es "generar y validar") |
| Requisitos | Subconjunto de **JSON Schema Draft 2020-12**; `additionalProperties: false` obligatorio en cada objeto; sin recursión ni referencias externas |
| Rendimiento | La gramática se **compila y se cachea 24 h** por cuenta (primer uso puede tardar) |
| Variante agéntica | *Strict tool use* con `toolChoice` forzado |
| Beneficios de costo | Elimina reintentos, elimina post-procesamiento, reduce texto superfluo, **reduce tokens de salida** |
| Trampa | Si `maxTokens` se queda corto, el JSON se trunca ⇒ **revisar `stopReason`** (`max_tokens` indica truncamiento) |

#### 4.1.1.5 Herramientas de optimización automática de prompts

- **Prompt Optimization (dentro de Prompt Management):** reescribe prompts automáticamente; ~**USD 0,03 por 1.000 tokens** procesados; el costo único se recupera con los ahorros de entrada.
- **Advanced Prompt Optimization (GA mayo 2026):** loop de feedback guiado por métrica que optimiza la plantilla y **compara el prompt original vs. optimizado en hasta 5 modelos** en un solo job, reportando **score, estimación de costo y latencia (TTFT)**. Métricas de guía: Lambda propia, LLM-as-a-Judge con rúbrica o *steering criteria*.

---

### 4.2 Skill 4.1.2 — Marcos de selección de modelos costo-efectivos

> *"Trade-off capacidad/costo, uso por niveles según complejidad de consulta, balance costo/calidad, ratio precio-rendimiento, patrones de inferencia eficientes."*

#### 4.2.1 El marco de decisión en cuatro pasos

```
1. Definir el piso de calidad   → métrica ancla + umbral (p. ej. correctness ≥ 0,90 en el dataset dorado)
2. Medir candidatos             → mismo dataset, mismas condiciones, un juez fijo
3. Comparar en tres ejes        → calidad | costo por tarea resuelta | p95 de latencia (TTFT y total)
4. Elegir el más barato que PASA el piso, no el mejor absoluto
```

**Ratio precio–rendimiento (una forma útil de tabularlo):**

| Modelo | Calidad (0–1) | Costo por 1.000 tareas resueltas | p95 latencia | Costo por punto de calidad |
|---|---|---|---|---|
| Grande | 0,94 | $48 | 4,2 s | $51 |
| Mediano | 0,89 | $9 | 1,8 s | $10 |
| Pequeño | 0,81 | $1,4 | 0,9 s | $1,7 |
| **Mediano + escalado en cascada** | **0,93** | **$13** | 2,1 s | **$14** |

La última fila es la conclusión típica: **la combinación gana a la elección única**.

#### 4.2.2 Patrones de enrutamiento por complejidad

| Patrón | Mecanismo | Ahorro típico | Notas |
|---|---|---|---|
| **Tiering estático** | Reglas de negocio (tipo de tarea, tenant, longitud) deciden el modelo | 20–40 % | Simple, predecible, sin ML extra |
| **Intelligent Prompt Routing (IPR)** | Bedrock predice, por request, qué modelo de la **misma familia** da la respuesta deseada al menor costo | **hasta 30 %** sin perder precisión | **USD 1,00 por 1.000 routing requests** + inferencia del modelo elegido; pares soportados por familia (p. ej. Haiku/Sonnet, Nova Lite/Pro, Llama); requests trazables para debug |
| **Cascade / escalado** | Modelo chico responde; si falla un chequeo de confianza, se escala al grande | 40–60 % del costo mezclado | El chequeo de confianza es la pieza clave (reglas, validador, juez barato) |
| **Routing por clasificador propio** | Un modelo pequeño (o distilado) clasifica la intención y enruta | 30–50 % | Requiere dataset y mantenimiento |
| **Caching semántico** (ver 4.1.4) | No enruta: evita la llamada | 20–45 % de requests sin tocar el modelo | Complementario a todo lo anterior |

> **Advertencia de examen:** IPR **no cruza familias** de modelos. Si el escenario pide "enrutar entre Claude y Llama", la respuesta correcta no es IPR, sino routing propio (o cascade) con AppConfig/Lambda.

#### 4.2.3 Destilación de modelos: la palanca estructural

**Model Distillation en Bedrock** permite destilar un modelo "maestro" (p. ej. Nova Premier, Claude) en un "estudiante" pequeño con datos sintéticos generados a partir de tus prompts (y opcionalmente tus datos de producción).

| Métrica | Valor reportado por AWS |
|---|---|
| Velocidad | hasta **500 % más rápido** |
| Costo | hasta **75 % menos costoso** |
| Pérdida de precisión | **< 2 %** en casos de uso tipo RAG |

**Punto crítico para el examen:** los modelos personalizados (fine-tuned o destilados) **no corren en on-demand**: requieren **Provisioned Throughput**. Un destilado que ahorra 75 % en inferencia pero se sirve en PT ocioso puede ser *más caro*. El análisis debe incluir la utilización del compromiso.

#### 4.2.4 Los modos de facturación como parte de la selección

| Modo | Precio vs. Standard | Compromiso | Ideal para | Trampa |
|---|---|---|---|---|
| **Standard (on-demand)** | base | ninguno | Tráfico variable, la mayoría de producción | Sin garantía de capacidad |
| **Priority** | ~**+75 %** | ninguno | Solicitudes críticas del usuario donde la latencia manda | Pagar premium sin medir el beneficio |
| **Flex** | **−50 %** | ninguno | Trabajo tolerable a latencia variable; dev/test | Sin SLA; puede haber throttling |
| **Batch** | **−50 %** | ninguno; asíncrono vía S3, hasta 24 h | Resúmenes nocturnos, clasificación, backfills, evaluaciones | No sirve para tiempo real; cuotas de jobs concurrentes |
| **Reserved** (nov. 2025) | precio fijo mensual por TPM reservado | 1 o 3 meses | Tráfico predecible con objetivo de **99,5 % de disponibilidad** | Se paga la reserva aunque no se use; el excedente desborda a Standard |
| **Provisioned Throughput (PT)** | por hora, **por model unit** | sin compromiso / 1 mes / 6 meses | Carga sostenida y **obligatorio para modelos custom** | Se factura 24/7 aunque esté ocioso |

**Regla de decisión práctica:** empezar en Standard o Flex; mover a **Batch** todo lo que no sea interactivo; pasar a **Reserved** cuando haya 2–4 semanas de tráfico estable que permita dimensionar; reservar **PT** para modelos personalizados o para cargas donde la cuota on-demand sea insuficiente. El punto de equilibrio de PT suele citarse en ~**80–85 % de utilización sostenida**; por debajo de ~60 %, on-demand o batch casi siempre ganan.

#### 4.2.5 Costos ocultos que hay que presupuestar (y que el examen pregunta)

| Componente | Referencia de precio | Mitigación |
|---|---|---|
| Vector store administrado | OpenSearch Serverless **Classic**: piso de ~USD 350–700/mes según configuración; **NextGen** (GA mayo 2026): escalado a cero, sin piso de OCU; S3 Vectors: desde ~USD 0,06/GB-mes | Elegir el store según latencia requerida: S3 Vectors para dev/baja QPS, NextGen para bursty, OpenSearch provisionado para QPS alto sostenido |
| Amplificación por agentes | 5–10× los tokens "visibles" | Agentes de propósito único, límite de iteraciones, herramientas que devuelvan poco |
| Guardrails | ~USD 0,15/1.000 text units por filtro de contenido/tema; ~USD 0,10 grounding | Habilitar solo los filtros necesarios |
| Reranking | ~USD 1,00/1.000 consultas | Sólo cuando el problema es de *ranking* (no de recall) |
| Flows | ~USD 0,035/1.000 transiciones de nodo | Menos nodos por workflow |
| Logging | CloudWatch ~USD 0,50/GB ingerido | No loguear prompts completos en producción sin necesidad; retención corta; S3 para payloads grandes |
| Evaluación | Tokens del modelo evaluado **+** del juez; humano ~USD 0,21 por tarea | Muestreo, caché de evaluaciones, jueces económicos en producción |
| Egreso de datos | Transferencia saliente | Mantener tráfico dentro de la región/VPC |

---

### 4.3 Skill 4.1.3 — Sistemas de alto rendimiento

> *"Batching, planificación de capacidad, monitoreo de utilización, auto-scaling, optimización de provisioned throughput."*

#### 4.3.1 Batch inference: la palanca más simple

| Característica | Valor de referencia |
|---|---|
| Descuento | **50 %** sobre on-demand (tanto entrada como salida) |
| Entrada | **JSONL en S3**, un request por línea (mismo formato que la API) |
| Salida | Archivo en S3 (JSONL); cada resultado se correlaciona por **`inferenceId`** |
| Registros por job | **mínimo 1.000 – máximo 50.000** (cuotas ajustables) |
| Tamaño | ~200 MB por archivo, ~1 GB por job |
| Ventana | Hasta **24 horas** (habitualmente bastante menos) |
| Límites | Cuotas de **jobs concurrentes por modelo/región**; procesamiento asíncrono fuera de los límites de RPM/TPM on-demand |
| Errores | Se reportan **por registro**, no abortan el job completo; revisar logs `/aws/bedrock/batch-inference` |
| Consejo operativo | Job #N+1 puede quedar **en cola silenciosa** si se supera el límite de jobs concurrentes; orquestar con Step Functions (Map) y backoff al hacer polling (30 s → 300 s) |

**Cuándo NO usar batch:** cualquier cosa con usuario esperando; flujos con dependencia de resultados intermedios; modelos sin soporte batch; modelos con PT.

#### 4.3.2 Planificación de capacidad

```
Paso 1. Inventariar: por workflow → tokens in/out P50 y P95, requests/día, estacionalidad
Paso 2. Convertir a cuota: TPM pico = requests_pico/min × (tokens_in_p95 + maxTokens_reservado)
Paso 3. Comparar con la cuota del modelo/región (Service Quotas) y con los picos de concurrencia
Paso 4. Decidir por capa:
        · base estable        → Reserved (estándar) o PT (custom)
        · picos                → Standard on-demand / CRIS
        · críticos             → Priority
        · no interactivo       → Batch / Flex
Paso 5. Instrumentar utilización (invocaciones vs. capacidad reservada) y revisar mensualmente
```

**Errores clásicos de capacidad:**
- Dimensionar por el **promedio** en lugar del **pico**.
- Comprar PT durante un incidente de throttling y no liberarlo cuando la cuota on-demand alcanza.
- Olvidar que **PT y Reserved se pagan ociosos**: una reserva para un lanzamiento que se estanca es gasto puro.
- Ignorar el **burndown** de tokens de salida: dimensionar en TPM "reales" y descubrir que la cuota se consume 5×.

#### 4.3.3 Auto-scaling y patrones de tráfico GenAI

| Escenario | Qué escala | Cómo |
|---|---|---|
| **Bedrock on-demand** | Capacidad compartida, autoescala del lado de AWS | No se configura; se gestiona **cuota** y se usa CRIS para distribución |
| **Reserved / PT** | Capacidad dedicada | **No autoescala**: la decisión es de compra, no de configuración |
| **Aplicación cliente** (Lambda/ECS/EKS) | Concurrencia | Concurrency reservada/provisioned, límites por workflow, colas SQS, `Map` de Step Functions con `MaxConcurrency` |
| **Agentes en AgentCore Runtime** | Sesiones concurrentes | Escalado administrado del runtime; **aislamiento por sesión** en microVM (no requiere tuning de instancias) |
| **Modelos self-hosted (SageMaker)** | Instancias/componentes | Autoscaling con métricas **custom** (`ConcurrentRequestsPerModel`, `ModelLatency`, `InvocationsPerInstance`), Inference Components, escalado a cero en Serverless |
| **Self-hosted en EKS** | Pods | HPA por métricas custom (cola, latencia) + KEDA; considerar KV-cache reuse si el motor lo soporta |

**Patrón de tráfico que define GenAI:** picos muy cortos y muy altos (un agente dispara 20 llamadas en paralelo y luego silencio), con picos de *reserva* de cuota por encima del consumo real. El auto-scaling debe ser **por concurrencia y por cola**, no por CPU.

#### 4.3.4 Configuraciones y patrones de uso eficiente

- **Conexiones reutilizadas:** `tcp_keepalive=True` en el cliente boto3 redujo TTFT ~25 % en benchmarks; evitar crear un cliente por request.
- **Retries bien configurados:** modo `adaptive` de boto3 (backoff + jitter) en lugar de reintentos fijos; los reintentos mal configurados multiplican el consumo de cuota.
- **Concurrencia acotada:** semáforo/cola por modelo; evitar "fire-and-forget" masivo.
- **Structured outputs** para eliminar reintentos por formato.
- **Prompt caching** para prefijos estables (baja tanto costo como presión sobre la cuota de entrada en modelos que excluyen tokens cacheados).
- **CRIS (cross-region inference):** distribuye carga entre regiones y, en perfiles US, puede multiplicar el throughput efectivo (~3×) y suavizar *cold starts*; los perfiles **globales** además reducen precio en modelos selectos (~10 %).

---

### 4.4 Skill 4.1.4 — Sistemas de caché inteligente

> *"Caché semántica, fingerprinting de resultados, caché en el borde, hashing determinista de requests, prompt caching."*

#### 4.4.1 Las cuatro capas de caché (y qué resuelve cada una)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Capa 4 · CACHÉ SEMÁNTICA (a nivel aplicación)                            │
│   "Ya respondí una pregunta equivalente" → devuelve respuesta guardada    │
│   Latencia ~10–80 ms · Evita 100 % de la llamada al modelo               │
├──────────────────────────────────────────────────────────────────────────┤
│ Capa 3 · CACHÉ DE RESPUESTA EXACTA (hashing determinista)                │
│   Fingerprint de (modelo, parámetros, versión de prompt, input normalizado)│
│   Latencia <1–5 ms · Captura reintentos, jobs duplicados, refrescos       │
├──────────────────────────────────────────────────────────────────────────┤
│ Capa 2 · PROMPT CACHING (nativo de Bedrock)                              │
│   Reutiliza el cómputo del PREFIJO estable → descuenta tokens de entrada  │
│   hasta −90 % costo / −85 % latencia en la porción cacheada               │
├──────────────────────────────────────────────────────────────────────────┤
│ Capa 1 · CACHÉ EN EL BORDE / HTTP (CloudFront, API Gateway, ALB)          │
│   Respuestas estáticas o deterministas sin personalización                │
│   Elimina la llamada antes de entrar a la aplicación                      │
└──────────────────────────────────────────────────────────────────────────┘
```

#### 4.4.2 Prompt caching (Bedrock) — el detalle que se pregunta

| Aspecto | Detalle |
|---|---|
| **Qué cachea** | El **cómputo del prefijo** del prompt (estado interno), no la respuesta |
| **Tipos** | **Explícito** (con *cache checkpoints*) e **implícito** (según modelo; en Nova el runtime intenta reusar prefijos comunes pero sin garantía de ahorro) |
| **Orden de evaluación** | Los checkpoints se procesan **tools → system → messages**; cambiar contenido anterior **invalida** los posteriores ⇒ **poner lo estable primero** |
| **Mínimo por checkpoint** | Varía por modelo: ~**512–1.024** tokens en modelos Claude nuevos, **2.048** en Haiku 3.5, **4.096** en Haiku 4.5 y algunos Opus/Sonnet en Bedrock, ~**1.000** en Amazon Nova |
| **Máximos** | Hasta **4 checkpoints** por request; hasta ~**32.000 tokens** cacheados (Claude) / ~20.000 (Nova) |
| **TTL** | Por defecto **5 minutos** en Bedrock (fijo en varias configuraciones); desde **enero 2026** hay **TTL de 1 hora** para Sonnet 4.5 / Haiku 4.5 / Opus 4.5 |
| **Precios** | Escritura de caché ~**1,25×** la tarifa de entrada (TTL 5 min) o **2×** (TTL 1 h); lectura ~**0,1×** (≈90 % de descuento) |
| **Punto de equilibrio** | Con TTL de 5 min, caché rentable desde **2 usos** del mismo prefijo dentro de la ventana. Con **hit ratio < ~30 %**, las escrituras cuestan más de lo que ahorran las lecturas |
| **Métricas** | `cacheReadInputTokens` y `cacheWriteInputTokens` en la respuesta (`usage`); exportables como métrica de **cache hit rate** |
| **Beneficio extra** | En algunos modelos, los tokens leídos de caché **no consumen cuota de TPM** |
| **Dónde brilla** | System prompts largos, catálogos de herramientas, documentos fijos, few-shot, contexto RAG estable, agentes con muchas llamadas seguidas |
| **Dónde NO rinde** | Tráfico *bursty* con huecos > TTL (el clásico "14 % de hit ratio"); prefijos que cambian en cada request; salidas largas (la caché no acelera la generación) |

> **Historia real que resume el punto:** un equipo con tráfico disperso tenía 14 % de hit ratio y estaba **pagando impuesto de caché**; al agrupar las solicitudes en ventanas más densas subió a ~71 % y el costo cayó ~95 % respecto del baseline sin caché.

#### 4.4.3 Caché de respuesta exacta y hashing determinista

**Fingerprint recomendado:**
```
key = sha256(
   model_id + "|" + inference_params_canónicos + "|" + prompt_template_version +
   "|" + tools_version + "|" + normalizar(input_usuario) + "|" + tenant_id
)
```
Reglas:
- **Normalizar** el input (espacios, mayúsculas si el caso de uso no es case-sensitive, emojis).
- **Incluir la versión del prompt y del modelo**: si no, servís respuestas de una configuración vieja.
- **Incluir el tenant** para evitar fuga entre clientes.
- **TTL según volatilidad del dato**, no según carga del sistema.
- Watch out: `temperature > 0` hace que la misma key pueda producir respuestas distintas; para caché exacta conviene `temperature = 0` y el mismo conjunto de parámetros.

#### 4.4.4 Caché semántica

| Aspecto | Detalle |
|---|---|
| **Mecanismo** | Embeber la consulta → buscar vecino más cercano en un índice vectorial → si la similitud ≥ umbral, devolver la respuesta guardada **sin llamar al modelo** |
| **Umbral típico** | **0,92–0,97** en producción (por plantilla, no global); por debajo de 0,90 aumentan los falsos positivos; por encima de 0,98 el caché casi nunca acierta |
| **Latencia en hit** | Embedding (~10–30 ms) + búsqueda (~1–5 ms) ≈ **< 50 ms**, frente a 500–2.000 ms de una llamada real |
| **Hit rate realista** | Exact-match suma **15–30 %**; semántico suma **20–45 %** en dominios parafraseables (soporte, FAQ, docs); **~0–15 %** en chat abierto, creativo o agéntico dependiente de estado |
| **Implementación en AWS** | **ElastiCache (Valkey/Redis) con búsqueda vectorial** + modelos de embedding de Bedrock; AWS publicó un caso con ~63.800 consultas reales con reducción de costo ~86 % y mejora de latencia ~88 % a umbrales óptimos |
| **Riesgos** | Falsos positivos (respuesta casi-correcta para pregunta distinta), **fuga entre tenants**, envenenamiento del caché, deriva de umbral, deriva del modelo de embeddings al cambiarlo |
| **Métrica correcta** | No el hit rate, sino **costo ahorrado atribuido** por tenant/plantilla (un hit rate de 41 % con 8 % de ahorro es un bug de medición) |
| **Buenas prácticas** | Exacto primero, semántico después; aislamiento por tenant en el *namespace*; versionar el caché junto con el prompt; TTL por volatilidad; muestreo y revisión humana de hits |

**Patrón potente en agentes:** aplicar caché semántica a **sub-consultas** (las que descompone el agente), no solo a la consulta del usuario. En la práctica, 3 de cada 4 sub-preguntas pueden servirse de caché, reduciendo llamadas por tarea y recortando la latencia extremo a extremo.

#### 4.4.5 Caché en el borde

- **CloudFront** para activos estáticos, respuestas deterministas y catálogos (jamás para contenido personalizado sin `Vary`/cache key correcta).
- **API Gateway caching** para endpoints idempotentes (p. ej. `GET /catalogos`), con TTL por ruta.
- **Cuidado con PII y personalización:** una cache key mal definida convierte el caché en una fuga de datos. Siempre incluir identidad/tenant cuando la respuesta sea personalizada.
- **Caché de embeddings de consulta** (no de respuestas): la misma consulta repetida no necesita re-embeber; ahorra 10–30 ms y tokens de embedding.

---

## 5. Task 4.2 — Optimización del desempeño de la aplicación

### 5.1 Skill 4.2.1 — Sistemas responsivos: latencia vs. costo

> *"Pre-cómputo de consultas predecibles, modelos optimizados para latencia, requests en paralelo, streaming de respuestas, benchmarking."*

#### 5.1.1 Descomponer la latencia antes de optimizarla

| Componente | Cómo se mide | Palancas |
|---|---|---|
| **TTFT** | Métrica CloudWatch `TimeToFirstToken` (GA marzo 2026) o medición cliente con `converse_stream` | Prompt caching, modelo más chico, CRIS, conexión reutilizada, Priority, latency-optimized inference, menos tokens de entrada |
| **OTPS/ITL** | Tokens de salida ÷ (tiempo total − TTFT) | Modelo, tamaño de salida, maxTokens, streaming |
| **Overhead de agente** | Span de cada tool call | Paralelizar tools, timeouts agresivos, evitar pasos redundantes |
| **Overhead de retrieval** | Span de `Retrieve` | Índice, filtros, número de resultados, reranking selectivo |
| **Post-proceso** | Código propio | Validaciones baratas, evitar validaciones redundantes en el camino crítico |

**Datos de referencia (benchmark público 2026, agrupado):** TTFT promedio de ~**340–610 ms** en modelos chicos con CRIS y caché; ~**1.500 ms** en Claude Haiku 4.5; modelos sin CRIS mostraron **varianza de hasta 14×** entre corridas por *cold start* (17,6 s vs. 1,2 s). El **piso práctico de on-demand ronda 340–400 ms**; para bajar de ahí hay que ir a **latency-optimized inference** (preview, modelos selectos) o **Provisioned Throughput**.

#### 5.1.2 Pre-cómputo: la optimización más subestimada

Si una parte de la respuesta es **predecible**, calculala antes de que la pidan:

| Patrón | Descripción | Ejemplo |
|---|---|---|
| **Pre-computación programada** | Job batch nocturno que genera resúmenes, clasificaciones o embeddings | Resumen diario de tickets por cuenta |
| **Calentamiento de caché (cache warming)** | Pre-cargar el caché semántico con las consultas más frecuentes antes del pico | FAQ de soporte a las 8:00 |
| **Materialización de respuestas** | Tabla/índice con respuestas listas (DynamoDB/ElastiCache) y refresco por evento | Estado de pedido típico |
| **Escritura anticipada de prompts cacheados** | Emitir la primera request que "escribe" el prefijo antes de la ráfaga real | Antes de un lanzamiento |
| **Warm pools de conexión / clientes** | Reutilizar cliente boto3 y conexiones HTTP/2 | Reduce ~25 % de TTFT |

**Costo–beneficio:** el pre-cómputo gasta tokens en batch (mitad de precio) para ahorrar latencia (y a veces tokens) en el momento crítico. La decisión es explícita: **pagar por adelantado, más barato, para no pagar en caliente**.

#### 5.1.3 Modelos y modos optimizados para latencia

| Opción | Qué hace | Disponibilidad / nota |
|---|---|---|
| **Modelos "pequeños y rápidos"** | Menos cómputo por token | Nova Micro, Claude Haiku, modelos destilados |
| **Latency-optimized inference** | `performanceConfig.latency = "optimized"`: reduce TTFT y acelera OTPS para el mismo modelo | **Preview**; modelos selectos (Nova Pro, Claude 3.5 Haiku, Llama 3.1 70B/405B), vía CRIS; verificar vigencia |
| **Priority tier** | Capacidad priorizada, menos throttling, SLA mejorado | +~75 % de precio; para lo crítico |
| **CRIS** | Enruta a la región con capacidad disponible; suaviza cold starts | Sin costo extra de routing; global profiles ~10 % más baratos en modelos selectos |
| **Provisioned Throughput** | Capacidad dedicada: elimina la espera de scheduling | Requiere dimensionar bien |
| **Streaming** | No reduce el tiempo total, **sí** el tiempo hasta ver contenido | Ver abajo |

#### 5.1.4 Streaming: barato, fácil y de alto impacto

- `ConverseStream` / `InvokeModelWithResponseStream` hacen que el usuario vea texto en **~200–500 ms** en lugar de esperar 2–5 s.
- **No reduce el costo** (se paga por token igual) y **no reduce el tiempo total**; cambia la *percepción*.
- Requisito de UX: manejar correctamente errores de stream, cancelación y reconexión.
- Precaución de observabilidad: X-Ray captura la llamada inicial, no cada chunk; medir TTFT en el cliente o usar la métrica nativa.
- **Anti-patrón:** streamear y luego procesar en el cliente de forma bloqueante antes de mostrar (anula el beneficio).

#### 5.1.5 Paralelización

| Técnica | Cuándo | Herramienta |
|---|---|---|
| **Fan-out de tareas independientes** | Comparar 3 modelos, resumir 20 documentos, evaluar N variantes | `Map` de Step Functions, Lambda con semáforo, asyncio con límite |
| **Paralelizar tool calls** | El agente necesita clima + horario + tipo de cambio | Ejecución concurrente en el runtime del agente (cuidado con cuota) |
| **Pipelines solapados** | Retrieval de la pregunta 2 mientras se genera la respuesta 1 | Colas/streams |
| **Hedge requests** | Enviar la misma consulta a dos rutas y quedarse con la primera | Solo si la duplicación de costo se justifica por el SLA |
| **Evitar serialización innecesaria** | Pasos que podrían ser concurrentes | Revisar el grafo del workflow |

> **Advertencia:** la paralelización es la causa #1 de `ThrottlingException` por **picos de reserva de cuota**, incluso cuando el consumo total del minuto está muy por debajo del límite. Acotar concurrencia, no solo volumen.

#### 5.1.6 Benchmarking (para poder comparar decisiones)

Un benchmark útil es **repetible** y **representativo**:

```
1. Set de N prompts reales (no de juguete), con distribución de longitudes parecida a producción
2. Mismo hardware/cliente, conexiones calientes, mismo tiempo de ejecución (evitar cruzar picos)
3. Medir: TTFT P50/P90/P99, latencia total, OTPS, tokens in/out, costo estimado, tasa de error
4. Correr cada configuración ≥3 veces (la varianza de cold start es enorme)
5. Reportar percentiles, no promedios
6. Congelar el resultado como baseline para comparar cambios futuros
```

**Herramientas:** scripts propios con `perf_counter` y `converse_stream`, ADOT/X-Ray para spans, CloudWatch para agregados. Para modelos self-hosted: NVIDIA GenAI-Perf (TTFT, ITL, TPS, RPS).

---

### 5.2 Skill 4.2.2 — Desempeño de recuperación

> *"Optimización de índices, preprocesamiento de consultas, búsqueda híbrida con scoring propio."*

#### 5.2.1 Optimización de índices

| Palanca | Qué se gana | Costo / límite |
|---|---|---|
| **Elección del vector store** | S3 Vectors: ~90 % más barato, sub-segundo de latencia. OpenSearch Serverless NextGen: escala a cero, ~10–100 ms, hybrid search. Aurora pgvector: barato si ya tenés Aurora. MemoryDB/ElastiCache: latencia de un dígito de ms | Feature parity desigual (S3 Vectors: sólo semántica, filtrado post-búsqueda, sin hybrid) |
| **Dimensiones del embedding** | Titan Text Embeddings v2 permite 256/512/1024 dimensiones y vectores binarios o float: 256 dim. reduce almacenamiento y tiempos | Menos precisión a menos dimensiones |
| **Cuantización** | Escalar/producto/binaria: reducción de almacenamiento de 4–64× | Requiere medir recall |
| **Estructura del índice** | HNSW vs. IVF: trade-off recall–latencia–memoria; `derived source` recorta almacenamiento hasta 3× | Tuning específico del motor |
| **Particionado/sharding** | Evitar *over-sharding* (coordinación y heap desperdiciados) | Reindexar si hace falta |
| **Filtrado pre-búsqueda vs. post** | Pre-filtrado reduce el espacio y la latencia | Depende del store (S3 Vectors filtra post-búsqueda) |
| **Indexación incremental** | Evita reindexar todo al cambiar embeddings o chunking | Requiere estrategia de cut-over |

#### 5.2.2 Preprocesamiento de consultas (el ROI más alto por línea de código)

| Técnica | Qué resuelve | Impacto |
|---|---|---|
| **Corrección de erratas / normalización** | Consultas con typos que no matchean | Alto en chat libre |
| **Reescritura de consulta** | Consultas conversacionales ("¿y eso cuánto sale?") | Alto en multi-turno |
| **Descomposición de consultas multi-parte** | Preguntas comparativas que un solo embedding "promedia" | Alto en consultas complejas |
| **Expansión / HyDE** | Vocabulario del usuario ≠ vocabulario del corpus | Medio |
| **Extracción de filtros** | Convertir "del año pasado" en un filtro de metadata | Alto en datos con particiones |
| **Detección de idioma** | Corpus y consulta en idiomas distintos | Crítico en multilingüe |
| **Cacheo del embedding de la consulta** | Repeticiones frecuentes | Bajo esfuerzo, ahorro directo |

#### 5.2.3 Búsqueda híbrida con scoring propio

- **Por qué:** la búsqueda semántica no tiene señal para identificadores, SKU, nombres propios ni códigos; la búsqueda léxica no entiende paráfrasis. La híbrida combina ambas.
- **Soporte:** OpenSearch Serverless (con campo de texto filtrable), Aurora PostgreSQL, MongoDB Atlas. Si el store no lo soporta, **cae silenciosamente a semántica pura** (causa frecuente de "activé hybrid y no cambió nada").
- **Fusión de scores:** dos enfoques habituales — **RRF (Reciprocal Rank Fusion)**, robusto y sin normalización, o **suma ponderada normalizada** (`α · sim_semántica + (1−α) · score_léxico`), que permite ajustar el peso por tipo de consulta.
- **Cuándo personalizar el scoring:** cuando hay metadatos que deben pesar (recencia, popularidad, jerarquía de documentos) o cuando el corpus mezcla idiomas.
- **Reranking:** recuperar amplio (k alto) y reordenar con un reranker para quedarse con pocos. Regla: **si el pasaje correcto no está en el set amplio, el reranker no puede arreglarlo** (eso es un problema de recall: chunking, hybrid o filtros). Costo de referencia ~USD 1/1.000 consultas.

---

### 5.3 Skill 4.2.3 — Optimización de throughput

> *"Optimización del procesamiento de tokens, estrategias de batch inference, gestión de invocaciones concurrentes."*

#### 5.3.1 Cómo funciona realmente la cuota de Bedrock (memorizar)

| Concepto | Detalle |
|---|---|
| **Dimensiones** | RPM y TPM **por modelo, por región y por cuenta** |
| **Reserva previa** | La cuota se **reserva al iniciar** la request en función de `input + maxTokens`, no del consumo final |
| **Burndown de salida** | Los tokens de salida consumen cuota con **multiplicador** (históricamente 1 token de salida ≈ 5 unidades) |
| **Estimación disponible** | Métrica **`EstimatedTPMQuotaUsage`** (GA marzo 2026), que incluye tokens de escritura de caché y multiplicadores |
| **Perfiles** | **CRIS** reparte carga entre regiones (perfiles US pueden dar ~3× throughput efectivo); **global profiles** además reducen precio en modelos selectos |
| **Capacidad dedicada** | **Reserved** y **PT** quedan fuera de las cuotas on-demand |
| **Excepción útil** | En algunos modelos, los tokens leídos de caché **no cuentan** contra TPM |

**Diagnóstico de un `ThrottlingException` (429):**
```
1. ¿Es RPM o TPM? → comparar Invocations y tokens vs. cuota del modelo en Service Quotas
2. ¿Es un pico de concurrencia? → buscar simultaneidad de starts, no volumen del minuto
3. ¿maxTokens sobredimensionado? → la reserva por request infla el TPM efectivo
4. ¿Respuestas largas? → burndown ×5 sobre salida
5. ¿Región con cuota baja? → CRIS o cambio de región
6. ¿Sostenido? → aumento de cuota, Reserved o PT
```

#### 5.3.2 Gestión de concurrencia (patrón recomendado)

```
Cola (SQS)  →  Workers con semáforo por modelo (p. ej. N=8)  →  Bedrock
                    │
                    ├─ retry adaptativo (backoff + jitter) sobre 429/5xx
                    ├─ fallback: modelo alterno de la misma familia / otra región
                    └─ dead-letter queue + alerta para fallos persistentes
```
Reglas prácticas:
- **Limitar la concurrencia por modelo**, no la global (los modelos tienen cuotas distintas).
- **Nunca reintentar sin jitter**: los reintentos sincronizados recrean el pico.
- **Ajustar `maxTokens` al caso de uso**: es la palanca de cuota más olvidada.
- **Separar pools** para cargas críticas y no críticas (batch vs. interactivo) por riesgo y prioridad.
- **Instrumentar** `InvocationThrottles` por modelo y alarma cuando supere un % del tráfico.

#### 5.3.3 Optimización del procesamiento de tokens

- Reducir tokens de entrada (poda, compresión, caching) ⇒ menos TPM y menos costo.
- Reducir tokens de salida (formato, límites) ⇒ menos burndown y menos latencia.
- Evitar prompts que se reenvían completos en cada turno de un agente: usar referencias/punteros (por ejemplo, pasar el resultado de la herramienta resumido).
- Aprovechar **batch** para todo lo no interactivo (también descarga las cuotas on-demand).
- Para self-hosted: **batching dinámico** del motor de inferencia, KV-cache reuse (SGLang/RadixAttention, vLLM), speculative decoding con modelo *draft*.

---

### 5.4 Skill 4.2.4 — Mejora del desempeño del FM

> *"Configuraciones de parámetros específicas del modelo, A/B testing para evaluar mejoras, selección adecuada de temperatura y top-k/top-p."*

#### 5.4.1 Parámetros: qué hace cada uno y cuándo usarlo

| Parámetro | Efecto | Valores típicos por caso de uso | Cuidado |
|---|---|---|---|
| **`temperature`** | Aleatoriedad del muestreo. 0 = casi determinista | 0 para extracción/clasificación/código; 0,2–0,4 para análisis/resúmenes; 0,7–1,0 para creatividad | Valores altos aumentan alucinación y varianza de costo/latencia |
| **`top_p`** (núcleo) | Muestrea sobre el conjunto de tokens cuya probabilidad acumulada llega a p | 0,8–0,95 habitualmente | **Ajustar temperatura *o* top_p, no ambos agresivamente** |
| **`top_k`** | Limita a los k tokens más probables | Se usa sobre todo en modelos abiertos | No todos los modelos/APIs lo soportan |
| **`maxTokens`** | Máximo de tokens de salida | Ajustado al caso de uso + margen para no truncar JSON | Afecta costo, latencia **y reserva de cuota** |
| **`stopSequences`** | Detiene la generación | Patrones que no querés ver (firmas, ejemplos extra) | Puede cortar contenido válido |
| **Penalizaciones** | Desalientan repetición | Poco usadas en modelos modernos | Pueden degradar calidad |

> **Punto de examen:** los parámetros **no son universales**. Cada modelo acepta un subconjunto y algunos los ignoran silenciosamente. La configuración debe validarse por modelo y documentarse; en la API `Converse` van dentro de `inferenceConfig`, y parámetros específicos del proveedor pueden requerir `additionalModelRequestFields`.

#### 5.4.2 A/B testing de cambios de desempeño

Metodología mínima (igual que en evaluación, pero enfocada en latencia/costo):
1. **Hipótesis explícita:** "bajar top_p a 0,8 reduce tokens de salida 15 % sin bajar correctness".
2. **Un cambio a la vez** (parámetro, modelo o prompt).
3. **Mismo set de entrada, mismas condiciones**, ≥3 repeticiones.
4. **Métricas de decisión:** calidad (dataset dorado) + tokens + latencia P95 + costo por tarea + tasa de error.
5. **Regla de promoción:** la mejora debe superar el umbral y **no** regresar ninguna métrica más allá del delta permitido.
6. **Canary** antes del 100 % del tráfico (ver D5 §4.9).

#### 5.4.3 Mejoras estructurales (no de parámetros)

| Mejora | Efecto |
|---|---|
| **Fine-tuning / continued pre-training** | Mejor calidad en dominio ⇒ permite usar un modelo más chico ⇒ menos costo por tarea |
| **Destilación** | Hasta 500 % más rápido y 75 % más barato con <2 % de pérdida (casos RAG) |
| **Prompt engineering + optimización automática** | Menos tokens para el mismo resultado |
| **Structured outputs** | Elimina reintentos y texto superfluo |
| **RAG bien afinado** | Evita depender de un modelo grande para "memorizar" el dominio |
| **Modelos de razonamiento vs. rápidos** | Elegir según si la tarea necesita cadena de pensamiento (más lento y caro) o no |

---

### 5.5 Skill 4.2.5 — Asignación eficiente de recursos para cargas FM

> *"Planificación de capacidad según requerimientos de procesamiento de tokens, monitoreo de utilización de patrones de prompt/completado, auto-scaling optimizado para patrones de tráfico GenAI."*

#### 5.5.1 Dimensionar por patrón de prompt/completado, no por RPS

Un sistema GenAI se dimensiona con **cuatro perfiles**, no con un promedio:

| Perfil | Firma | Qué implica |
|---|---|---|
| **Entrada dominante (RAG/summarization)** | in ≫ out | Optimizar recuperación y caché de prefijo; la cuota TPM de entrada es el límite |
| **Salida dominante (generación/código)** | out ≫ in | Optimizar maxTokens y modelo; el burndown de salida domina la cuota |
| **Simétrico (chat)** | in ≈ out | Balance; el historial crece con la sesión |
| **Agéntico** | N llamadas por tarea, mixto | Costo y latencia se multiplican por pasos; instrumentar **por paso** |

#### 5.5.2 Monitoreo de utilización

| Recurso | Métrica de utilización | Alarma sugerida |
|---|---|---|
| **Provisioned Throughput** | Invocaciones/tokens reales vs. capacidad de las MU adquiridas | Utilización < 60 % sostenida ⇒ revisar compra |
| **Reserved tier** | TPM consumido vs. TPM reservado (y cuánto desborda a Standard) | Desborde > X % ⇒ recalibrar reserva |
| **Endpoints SageMaker** | `InvocationsPerInstance`, `ModelLatency`, GPU util | Infrautilización < 40 % ⇒ downsizing/auto-scaling |
| **Vector store** | OCU-hour, latencia P95, QPS | Picos de OCU, latencia en alza |
| **Concurrencia cliente** | In-flight requests, cola, espera | Crecimiento de cola sin caída de latencia upstream |

#### 5.5.3 Auto-scaling adaptado a tráfico GenAI

Reglas que se derivan de los patrones de tokens:
- Escalar por **tokens en vuelo** o **concurrencia**, no por CPU (la carga llega en ráfagas cortas).
- **Pre-escalar por horario** (el asistente de soporte tiene picos conocidos: 9–11 y 15–18).
- **Escalar a cero** sólo si el cold start es tolerable (dev/test, jobsBatch); en interactivo, mantener un mínimo caliente.
- **Alarmas compuestas** (latencia + throttles + errores) para evitar oscilaciones.
- Recordar que **el modelo no escala desde tu lado**: escalar la aplicación no aumenta la cuota; hay que combinar con CRIS/Reserved/PT.

---

### 5.6 Skill 4.2.6 — Optimización de workflows GenAI

> *"API call profiling para patrones prompt-completion, optimización de consultas al vector DB, técnicas de reducción de latencia específicas de inferencia LLM, patrones de comunicación eficientes entre servicios."*

#### 5.6.1 Profiling de llamadas

Objetivo: saber **dónde se va el tiempo y el dinero** en un workflow de N pasos.

```
Traza (CloudWatch Transaction Search / X-Ray)
└─ span: request_usuario                      2.480 ms
   ├─ span: retrieve_context (Knowledge Base)   260 ms   ← 10 % tiempo
   ├─ span: rerank                               90 ms
   ├─ span: llm_planificación (tool selection)  610 ms   ← 25 % tiempo
   ├─ span: tool_1 (Lambda)                     180 ms
   ├─ span: tool_2 (API externa, timeout 3 s)  1.050 ms  ← 42 % tiempo  ⚠
   ├─ span: llm_síntesis                        430 ms
   └─ span: guardrail_check                      60 ms
```
El profiling revela los dos patrones clásicos: **una herramienta externa lenta** que domina la latencia y **una llamada de planificación** cuya necesidad se puede eliminar (por ejemplo, con un prompt que seleccione la herramienta directamente).

#### 5.6.2 Optimización de consultas al vector DB

| Técnica | Efecto |
|---|---|
| **Reducir `numberOfResults`** a lo necesario (+reranker si hace falta) | Menos latencia y menos tokens inyectados |
| **Filtros de metadata** para achicar el espacio de búsqueda | Menos latencia en índices grandes |
| **Pre-filtrado** (donde el store lo permita) | Evita traer vecinos que luego se descartan |
| **Proyección de campos** (traer el texto del chunk y su id, no todo el documento) | Menos payload y menos tokens |
| **Caché de embeddings de consulta** | Evita re-embeber |
| **Caché del resultado de retrieval** para consultas repetidas | Elimina la búsqueda completa |
| **Evitar búsquedas duplicadas** en el mismo turno (agente que recupera dos veces lo mismo) | Ahorro directo |
| **Timeouts y circuit breakers** en el cliente | Evita que un índice lento bloquee el workflow |

#### 5.6.3 Patrones de comunicación eficientes

| Anti-patrón | Alternativa |
|---|---|
| Muchas llamadas chicas entre servicios por cada token del agente | **Agrupar** en una llamada; pasar contexto estructurado |
| Reenviar todo el historial entre servicios | Pasar un **id de sesión** y recuperar estado del store |
| Sincrónico en el camino crítico para cosas no bloqueantes | **Asíncrono** (SQS/EventBridge): evaluación, logging, analítica |
| Cliente nuevo por request | Cliente/`keep-alive` reutilizado, connection pooling |
| Llamar al modelo para algo determinista (formato, cálculo, plantilla) | Código determinista |
| Modelo grande para planificación trivial | Modelo chico, o reglas |
| Retries agresivos entre servicios | Backoff con jitter + idempotencia |

---

## 6. Task 4.3 — Sistemas de monitoreo para aplicaciones GenAI

### 6.1 Skill 4.3.1 — Observabilidad holística

> *"Visibilidad completa: métricas operativas, tracing de desempeño, tracing de interacción con el FM, métricas de impacto de negocio, dashboards propios."*

#### 6.1.1 El modelo de cuatro señales

| Señal | Fuente | Pregunta que responde | Dónde mirar |
|---|---|---|---|
| **Métricas operativas** | CloudWatch (namespaces `AWS/Bedrock`, `bedrock-agentcore`, `AWS/Bedrock/KnowledgeBases`, guardrails) | ¿El sistema está sano **ahora**? | GenAI Observability, dashboards propios, alarmas |
| **Logs** | Model Invocation Logging (CloudWatch/S3), logs de agentes/KB, Application Signals | ¿Qué se envió y qué volvió? ¿Qué imprimió el agente? | Logs Insights, Athena, Live Tail |
| **Trazas** | X-Ray, ADOT/OpenTelemetry, Transaction Search (`aws/spans`) | ¿Por qué **esta** sesión se comportó así? | Waterfall de spans, Trace View |
| **Evaluaciones de calidad** | AgentCore Evaluations online, Guardrails, jueces propios | ¿Sigue siendo **correcta** la respuesta después del último cambio? | Métricas de evaluación en CloudWatch |

> **El punto que separa un dashboard de un observatorio:** las tres primeras señales **no detectan alucinaciones ni degradación silenciosa**. Un sistema puede tener 100 % de disponibilidad, latencia excelente, cero errores… y estar respondiendo mal. La cuarta señal es obligatoria.

#### 6.1.2 Instrumentación mínima obligatoria

Cada llamada al modelo debería llevar (como atributos de span y dimensiones de métrica):
```
service · route/feature · environment · deployment version
model_id · model_version · prompt_version · temperature/maxTokens
tenant/user_segment · trace_id · session_id
tokens_in · tokens_out · cache_read · cache_write
ttft_ms · total_ms · retries · stop_reason · guardrail_interventions
```
Sin **modelo + versión de prompt** en las trazas, no podés atribuir una regresión a un cambio; sin **tenant**, no podés hacer FinOps ni aislar incidentes.

#### 6.1.3 Métricas de negocio (las que consiguen presupuesto)

| Métrica | Definición | Por qué importa |
|---|---|---|
| **Costo por tarea resuelta** | Costo ÷ tareas completadas (no intentadas) | Evita premiar al modelo barato que falla y reintenta |
| **Tasa de deflexión / resolución sin humano** | % resuelto sin escalar | Valor directo en soporte |
| **Tiempo ahorrado por usuario/ticket** | Minutos × volumen | Traducción a dinero |
| **CSAT / thumbs-up rate** | Satisfacción | La única señal "de verdad" del usuario |
| **Adopción por feature** | Uso por workflow | Prioriza inversión |
| **Costo por sesión / por usuario activo** | Unit economics | Detecta abuso y fugas |

---

### 6.2 Skill 4.3.2 — Monitoreo proactivo y KPIs de GenAI

> *"CloudWatch para tokens, efectividad de prompt, tasas de alucinación, calidad de respuesta; detección de anomalías para picos de tokens y response drift; Model Invocation Logs; benchmarks; detección de anomalías de costo."*

#### 6.2.1 Catálogo de métricas CloudWatch de Bedrock

**Runtime de modelos (`AWS/Bedrock`):**

| Métrica | Qué es | Uso |
|---|---|---|
| `Invocations` | Nº de requests a InvokeModel/Converse | Volumen |
| `InvocationLatency` | Latencia de la invocación (ms) | SLO para flujos de respuesta completa |
| `TimeToFirstToken` | Latencia hasta el primer token (streaming) | **La métrica de UX percibida** |
| `InputTokenCount` / `OutputTokenCount` | Tokens procesados/generados | Costo y detección de *prompt bloat* |
| `InvocationClientErrors` | 4xx | Requests mal formados, ventana excedida |
| `InvocationServerErrors` | 5xx | Salud del servicio |
| `InvocationThrottles` | 429 | Presión de cuota |
| `EstimatedTPMQuotaUsage` | Consumo estimado de cuota TPM (incluye cache write y multiplicadores) | **Planificación y alertas tempranas** |
| `OutputImageCount` | Imágenes generadas | Costos multimodales |

**Agentes (AgentCore):** sesiones, invocaciones, errores (sistema vs. usuario), throttles, latencia, duración, uso de tokens, por agente y por endpoint.

**Gateway (herramientas):** `Invocations`, `Throttles`, `SystemErrors`, `UserErrors`, `Latency`, `Duration`, **`TargetExecutionTime`** (tiempo del target, p. ej. Lambda/API) — permite separar latencia de la plataforma vs. del target.

**Knowledge Bases:** `Invocations`, `ClientErrors`, `ServerErrors`, `Throttles`, `RawDataSize` (tamaño indexado por job de ingesta), `TotalIterationCount` (retrieval agéntico). ⚠️ El envío de métricas de KB es *best effort*: sin permiso `cloudwatch:PutMetricData` se descartan silenciosamente.

**Guardrails:** `InvocationsIntervened` (con dimensión `GuardrailPolicyType`), `InvocationLatency`, `TextUnitCount`, `InvocationThrottles`.

#### 6.2.2 KPIs específicos de GenAI: qué significa "efectividad de prompt"

| KPI | Cómo se calcula | Umbral de ejemplo |
|---|---|---|
| **Tasa de alucinación** | % de respuestas no soportadas por el contexto (juez con faithfulness, grounding check o sampling humano) | > 5 % en soporte ⇒ investigar; < 1–2 % en dominios regulados |
| **Efectividad de prompt** | Frecuencia con que la respuesta cumple formato + instrucciones + longitud esperada, por versión de prompt | ≥ 98 % de esquema válido |
| **Calidad de respuesta** | Score del juez (correctness/helpfulness) muestreado | ≥ umbral del dataset dorado |
| **Tasa de rechazo (refusal)** | % de declines | Subidas ⇒ prompt demasiado restrictivo o consultas fuera de alcance |
| **Tasa de intervención de guardrail** | Intervenciones ÷ invocaciones | Picos ⇒ ataque o contenido legítimo bloqueado |
| **Cache hit ratio** | `cacheRead ÷ (cacheRead + input)` | < 30 % ⇒ revisar estructura/TTL del prompt |
| **Tokens por tarea** | Σ tokens ÷ tareas | Deriva ascendente ⇒ prompt bloat o tool outputs grandes |
| **Reintentos por request** | retries ÷ requests | Aumento ⇒ degradación del proveedor o cuota |

#### 6.2.3 Detección de anomalías y drift

| Anomalía | Detector | Acción |
|---|---|---|
| **Pico de tokens** sin subida de tráfico | CloudWatch **anomaly detection** sobre `InputTokenCount`/`OutputTokenCount` y tokens por sesión | Revisar la última versión de prompt; verificar tool outputs; posible bucle del agente |
| **Response drift** (distribución de salidas cambia) | Comparar embeddings/longitudes/refusal rate contra una ventana de referencia (PSI, KS) | Shadow evaluation, revisión de cambios del proveedor |
| **Deriva de calidad** | Evaluación online muestreada + canary suite diaria | Investigar prompt/modelo/retrieval |
| **Crecimiento de costo** | **AWS Cost Anomaly Detection** con monitor acotado a Bedrock (o por tag) + AWS Budgets al 80 % y 100 % | Atribuir por inference profile/tag; cortar la fuente |
| **Latencia en alza** | Alarmas sobre `p95 InvocationLatency` y `TimeToFirstToken` | Separar TTFT vs. OTPS; revisar toolkit externo |
| **Throttling** | Alarma sobre `InvocationThrottles` y `EstimatedTPMQuotaUsage` | Reducir `maxTokens`, acotar concurrencia, CRIS, cuota o Reserved/PT |
| **Retrieval degradado** | Tasa de resultados vacíos, scores de relevancia, `RawDataSize` anómalo | Revisar ingestas, filtros, drift del corpus |

**Patrón de *canary* de calidad (el más rentable):** un set fijo de 50–200 prompts con resultados "buenos conocidos", ejecutado **a diario** contra producción, con *diff* de resultados. Es el único método que detecta un cambio silencioso del proveedor el mismo día que ocurre.

#### 6.2.4 Model Invocation Logging: configuración y cuidados

| Aspecto | Detalle |
|---|---|
| Estado por defecto | **Deshabilitado** |
| Destinos | CloudWatch Logs y/o S3 |
| Contenido | Metadata, request y response (según modalidades elegidas: texto, imagen, embedding, vídeo) |
| Límite importante | En CloudWatch Logs el *body* de salida se limita (~100 KB); para payloads grandes **usar S3** |
| Privacidad | Los prompts pueden contener PII: restringir acceso, definir retención, usar **Data Protection** (enmascaramiento) en los log groups |
| Costo | Ingesta de CloudWatch Logs (~USD 0,50/GB) puede crecer; elegir destinos y retención conscientemente |
| Sinergia | Habilitarlo permite el drill-down desde GenAI Observability ("ver en Logs Insights") y el análisis por Athena sobre S3 |

---

### 6.3 Skill 4.3.3 — Observabilidad integrada y trazabilidad forense

> *"Dashboards de métricas operativas, visualizaciones de impacto de negocio, monitoreo de cumplimiento, trazabilidad forense y auditoría, tracking de interacción de usuario, tracking de patrones de comportamiento del modelo."*

#### 6.3.1 Un dashboard por audiencia

| Audiencia | Panel | Contenido clave |
|---|---|---|
| **On-call / ingeniería** | Operaciones | Sesiones/5 min, p50/p95/p99 por agente, tasa de error por clase, tokens por sesión (distribución), tool invocations por sesión, throttles, score de evaluación online (rolling 24 h) |
| **Producto** | Experiencia y valor | CSAT/thumbs, tasa de resolución, deflexión, tiempo a resolución, adopción por feature |
| **Finanzas / FinOps** | Costo | Gasto por modelo, por inference profile/tag, costo por tarea resuelta, hit ratio de caché, ahorro estimado por optimización |
| **Riesgo / cumplimiento** | Control | Intervenciones de guardrail por política, PII redactada, refusal rate, verificación formal (Automated Reasoning), evidencia de auditoría |

**Buena práctica:** mantener el dashboard de on-call corto (5–8 indicadores). Forzar al on-call a leer métricas que no puede interpretar es tan malo como no tener dashboard.

#### 6.3.2 Trazabilidad forense y auditoría

| Requisito | Implementación |
|---|---|
| Saber **quién** invocó | **CloudTrail**: las operaciones de Bedrock Runtime son *management events* (registradas por defecto); las de agentes (`InvokeAgent`, `RetrieveAndGenerate`, `InvokeFlow`) son **data events** y **no** se registran por defecto |
| Saber **qué** se envió y volvió | Model Invocation Logging (S3 para payloads grandes y retención larga) |
| Reconstruir una sesión completa | Trazas con `session.id`, `user.id` y `prompt_version`; Logs Insights sobre `aws/spans` |
| Evidencia de control | Findings de Automated Reasoning, trazas de guardrail, resultados de evaluación archivados en S3 |
| Cumplimiento | Retención por política, cifrado KMS, acceso por rol, VPC endpoints/PrivateLink |
| Detección de uso indebido | IAM Access Analyzer sobre políticas de Bedrock; alarmas sobre intentos de jailbreak (`InvocationsIntervened` por política) |

#### 6.3.3 Tracking de interacción de usuario y comportamiento del modelo

- **Sesiones:** duración, número de turnos, abandono (indicador adelantado de insatisfacción), cambios de modelo intra-sesión (bug de sticky routing).
- **Comportamiento del modelo:** distribución de longitudes de respuesta, mix de tool calls, tasa de refusal, formato válido, "personalidad" (tono, longitud, estructura) — todos detectables sin ground truth.
- **Comportamiento del usuario:** patrones de reformulación (señal de fallo), consultas fuera de alcance, picos por evento de negocio.
- **Coordinación multi-agente:** spans de delegación (agente → agente) con la tarea delegada, para saber dónde se pierde el objetivo.

---

### 6.4 Skill 4.3.4 — Frameworks de desempeño de herramientas

> *"Tracking de patrones de llamada, recolección de métricas, observabilidad de tool calling y coordinación multi-agente, líneas base de uso para detección de anomalías."*

#### 6.4.1 Qué medir por herramienta

| Métrica | Definición | Para qué |
|---|---|---|
| **Volumen de invocación** | Llamadas por tool / por sesión | Detectar herramientas mal descritas o redundantes |
| **Tasa de éxito / error por tipo** | 4xx (parámetros malos) vs. 5xx (fallo del target) | Separar problema del agente vs. del backend |
| **Latencia** | `Latency` (primer token de respuesta), `Duration` (total), **`TargetExecutionTime`** | Aislar overhead de plataforma vs. del target |
| **Selección correcta** | ¿Era la herramienta adecuada? (evaluador `ToolSelectionAccuracy`) | Calidad de la descripción de tools |
| **Precisión de parámetros** | ¿Los argumentos provienen del contexto o están inventados? (`ToolParameterAccuracy`) | Errores silenciosos que producen respuestas plausibles y falsas |
| **Reintentos / tormentas** | Llamadas repetidas dentro de una sesión | Bucles del agente; costo oculto |
| **Tool calls por tarea** | Distribución | Eficiencia del diseño agéntico |

#### 6.4.2 Líneas base y detección de anomalías

- Establecer baseline por herramienta y por workflow (llamadas/tarea, latencia P95, tasa de error).
- Alarmar con **desvío relativo** respecto del baseline, no con un valor absoluto (los patrones de uso cambian con el tiempo).
- Alertas típicas: "tool X duplica sus llamadas por sesión" (bucle), "latencia del target +200 %" (dependencia degradada), "tasa de errores 4xx sube" (descripción de herramienta o contrato roto).
- **AgentCore Gateway** da la observabilidad de herramientas (invocaciones, throttles, errores, latencias) con dimensiones por target y por tool; útil incluso para agentes que no corren en AgentCore Runtime.

#### 6.4.3 Coordinación multi-agente

- Trazas con relación padre-hijo entre agentes (quién delegó a quién y con qué tarea).
- Métricas: **handoffs por tarea**, pasos totales, tasa de delegación fallida, costo por tarea del sistema completo (no por agente).
- Anti-patrón medible: dos agentes repitiendo la misma llamada de herramienta (se detecta como duplicados dentro de la misma traza).

---

### 6.5 Skill 4.3.5 — Gestión operativa de vector stores

> *"Performance monitoring de bases vectoriales, rutinas automatizadas de optimización de índices, procesos de validación de calidad de datos."*

#### 6.5.1 Qué monitorear

| Dimensión | Métrica | Alarma típica |
|---|---|---|
| **Latencia** | p50/p95/p99 de consulta (y separada de la latencia de embedding) | p95 > objetivo de SLO |
| **Throughput** | QPS, OCU utilizados, saturación | OCU cerca del máximo configurado |
| **Calidad de recuperación** | Hit rate, MRR, context relevance, **tasa de resultados vacíos** | Caída de hit rate o subida de vacíos |
| **Ingesta** | Duración del job de sync, `RawDataSize`, documentos fallidos, lag de indexación | Ingesta que no termina o tamaño anómalo |
| **Costo** | OCU-horas, GB almacenados, consultas facturables | Deriva sin cambio de tráfico |
| **Salud del índice** | Fragmentation, shards, versión de motor | Shards mal dimensionados, versiones en fin de soporte |

#### 6.5.2 Optimización automatizada de índices (rutinas programadas)

| Rutina | Frecuencia | Qué hace |
|---|---|---|
| **Reindexado por cambio de configuración** | Al cambiar chunking/embeddings | Construir el nuevo índice en paralelo, validar con el set de consultas de referencia, cut-over |
| **Compactación / merge de segmentos** | Semanal / según motor | Reduce latencia de búsqueda |
| **Re-cuantización o reducción de dimensiones** | Cuando storage/latencia lo justifican | Re-medir recall antes de promover |
| **Tiering de vectores fríos** | Mensual | Mover vectores de baja consulta a almacenamiento más barato (p. ej. S3 Vectors) |
| **Limpieza de duplicados y obsoletos** | Semanal | Evita que el top-k se llene de copias |
| **Sincronización incremental** | Continuo | Evita "reindexar todo" (caro y riesgoso) |

#### 6.5.3 Validación de calidad de datos (antes de indexar y en producción)

- **Completitud de metadata** (los filtros dependen de ella; metadata ausente rompe filtros).
- **Consistencia de chunking** (tamaños anómalos, chunks vacíos, tablas partidas).
- **Duplicados y versiones** (el mismo documento dos veces ⇒ respuestas contradictorias).
- **Frescura** (documentos obsoletos que siguen respondiendo).
- **Modelo de embeddings único por índice** (mezclar versiones degrada la recuperación de forma difícil de diagnosticar).
- **Prueba de recuperación por documento** (para cada documento clave, una consulta conocida debe recuperarlo): es una prueba de integridad de la ingesta, no de la calidad del modelo.

---

### 6.6 Skill 4.3.6 — Frameworks de troubleshooting específicos de FM

> *"Golden datasets para detectar alucinaciones, output diffing para consistencia de respuestas, reasoning path tracing para errores lógicos, pipelines de observabilidad especializados."*

#### 6.6.1 Los modos de falla que *no* existen en ML tradicional

| Modo de falla | Firma | Detección |
|---|---|---|
| **Alucinación** | Respuesta fluida, confiada, incorrecta; `200 OK` | Grounding checks, faithfulness del juez, golden dataset |
| **Degradación silenciosa de calidad** | Métricas operativas perfectas, respuestas peores | Evaluación continua muestreada + canary diario |
| **No-determinismo** | La misma entrada da resultados distintos | Repetición n veces y análisis de distribución (Pass^k) |
| **Deriva de prompt** | Alguien editó una plantilla fuera del pipeline | Versionado de prompts + diff de plantillas en el repo |
| **Cambio del proveedor** | El modelo "de siempre" cambia su comportamiento | Canary suite diaria, `model_version` en trazas |
| **Amplificación de costo** | Tokens por tarea crecen sin cambio visible | Métrica de tokens por sesión/tarea + anomalías |
| **Bucle agéntico** | Reintentos y tool calls repetidos | Tool invocations por sesión, alarmas de patrón |
| **Deriva semántica del corpus** | La recuperación empeora gradualmente | Monitoreo de hit rate y distribución de embeddings |

#### 6.6.2 Las cuatro técnicas del enunciado, aplicadas

**1) Golden dataset (detección de alucinaciones).**
Set congelado de 50–200 casos con respuestas correctas acordadas, **nunca usado para tuning**, ejecutado en cada cambio y semanalmente en producción. Es la única medición comparable en el tiempo. Se complementa con **grounding checks** (Guardrails) sobre tráfico real muestreado.

**2) Output diffing (consistencia de respuestas).**

```python
# Ejecutar el mismo prompt N veces y comparar
resultados = [invoke(prompt, temperature=t) for _ in range(5)]
similitudes = pairwise_cosine(embeddings(resultados))
variabilidad = 1 - mean(similitudes)          # métrica de inestabilidad
diff_estructural = comparar_campos(json.loads(r) for r in resultados)  # campos que cambian
```
Se aplica a tres niveles: **entre versiones** (baseline vs. candidato), **entre corridas** (estabilidad) y **entre modelos** (migraciones).

**3) Reasoning path tracing (errores lógicos).**
Con trazas de spans por paso (planificación → herramienta → validación → síntesis), se identifica **en qué paso** se rompió la lógica: ¿la herramienta devolvió mal?, ¿el agente eligió mal la herramienta?, ¿la síntesis ignoró la evidencia? Los evaluadores de trayectoria (¿se llamó a la herramienta esperada, en el orden esperado?) convierten esto en una prueba automática.

**4) Pipelines de observabilidad especializados.**
Combinar: Model Invocation Logging → S3 (retención) → Athena (análisis) con guardrails y evaluación continua como señales de calidad. La fragmentación (logs en un lado, evaluaciones en otro, costos en un tercero) es el fallo más común de las implementaciones de observabilidad GenAI.

---

## 7. Arquitectura de referencia

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 0 · CONTROL DE COSTO Y ATRIBUCIÓN                                             │
│  · Application inference profiles + cost allocation tags (Team/App/Env)            │
│  · IAM principal cost allocation (CUR 2.0) para atribución por rol/usuario SSO     │
│  · AWS Budgets (80 %/100 %) + Cost Anomaly Detection acotado a Bedrock             │
└────────────────────────────────────────────────────────────────────────────────────┘
                                     ▲
┌────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 1 · ENTRADA: caché y routing (antes de gastar tokens)                         │
│  CloudFront / API Gateway cache → Caché exacta (hash determinista) →               │
│  Caché semántica (ElastiCache vectorial, umbral 0.92–0.97, por tenant) →           │
│  Clasificador de complejidad → IPR / cascade / tier estático                       │
└────────────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 2 · CONTEXTO: recuperación eficiente                                          │
│  Preprocesamiento de consulta (reescritura, filtros, descomposición) →             │
│  Búsqueda híbrida (RRF / scoring propio) → Reranking selectivo →                   │
│  Presupuesto de contexto explícito (poda, dedupe, proyección de campos)            │
└────────────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 3 · GENERACIÓN: tokens bajo control                                           │
│  Prompt caching (prefijo estable primero) · Structured outputs · maxTokens/stop    │
│  Streaming · paralelización acotada · CRIS/Reserved/PT según carga                 │
└────────────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 4 · OBSERVABILIDAD (4 señales)                                                │
│  Métricas (CloudWatch/Bedrock, AgentCore, KB, Guardrails) + Logs (invocation       │
│  logging) + Trazas (X-Ray/ADOT/Transaction Search) + Evaluaciones (online/dorado)  │
└────────────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────────────────────────────────────────────────────┐
│ CAPA 5 · MEJORA CONTINUA                                                           │
│  Anomalías de costo/tokens → Insights → Recommendations → batch eval / A-B →       │
│  promoción con aprobación · Los fallos vuelven al dataset dorado                   │
└────────────────────────────────────────────────────────────────────────────────────┘
```

**Cómo se cierra el ciclo (una vuelta completa):**
1. Una alarma de costo/tokens dispara (capa 4).
2. Se atribuye el gasto por inference profile/tag (capa 0).
3. Se descubre que la versión v7 del prompt duplicó los tokens de entrada (log + traza).
4. Se aplica poda de contexto + prompt caching al prefijo nuevo (capas 2–3).
5. Se valida la calidad con el dataset dorado y en canary (capa 5).
6. Se mide la mejora en costo por tarea resuelta y se documenta como baseline.

---

## 8. Cheat sheet: tablas de decisión para el examen

### 8.1 "Si el escenario dice… → elegí…"

| El escenario dice | Respuesta esperada |
|---|---|
| Necesito saber cuántos tokens tiene un prompt **antes** de invocar el modelo | API **`CountTokens`** (gratuita, específica del modelo, coincide con lo facturable) |
| Tengo un system prompt de 4.000 tokens repetido en cada request | **Prompt caching** (prefijo estable primero; breakeven ~2 usos dentro del TTL) |
| Mi tráfico es disperso y el cache hit ratio es del 14 % | Reestructurar para **densificar** las ventanas (TTL de 5 min) o pasar a TTL de 1 hora |
| Mismo prefijo debe sobrevivir más de 5 minutos entre llamadas | **TTL de 1 hora** (modelos soportados: Sonnet 4.5, Haiku 4.5, Opus 4.5) |
| Quiero ahorrar 50 % en un pipeline de resúmenes nocturnos | **Batch inference** (−50 %, JSONL en S3, hasta 24 h) |
| El trabajo tolera latencia variable pero no puede esperar 24 h | **Flex tier** (−50 %) |
| Necesito capacidad garantizada y 99,5 % de disponibilidad con compromiso mensual | **Reserved tier** (1 o 3 meses; overflow automático a Standard) |
| Uso un modelo **fine-tuned/destilado** y necesito servirlo | **Provisioned Throughput** (obligatorio para modelos custom) |
| Debo elegir entre modelos de la misma familia automáticamente por costo | **Intelligent Prompt Routing** (hasta 30 % de ahorro; ~USD 1/1.000 routing requests) |
| Quiero enrutar entre **familias distintas** | **Routing propio/cascade** (IPR no cruza familias) |
| Necesito consultas repetitivas resueltas sin llamar al modelo (~25–45 % del tráfico) | **Caché semántica** (ElastiCache + embeddings, umbral 0.92–0.97) |
| Consultas con repeticiones **idénticas** y deterministas | **Hash determinista** del request (modelo + params + versión de prompt + input normalizado + tenant) |
| Contenido idéntico para todos los usuarios, estático | **Caché en el borde** (CloudFront/API Gateway) |
| Los usuarios se quejan de que la respuesta "tarda en aparecer" | **Streaming** (`ConverseStream`) → TTFT percibido 200–500 ms |
| Necesito la menor latencia posible por request para un modelo soportado | **Latency-optimized inference** (preview) o **Priority tier** |
| Los picos de latencia vienen de *cold start* en modelos sin CRIS | **Cross-region inference** (distribuye y suaviza) |
| Hay `ThrottlingException` con consumo total por debajo de la cuota | Revisar **`maxTokens` (reserva previa)** y **picos de concurrencia**; acotar paralelismo; alarma con `EstimatedTPMQuotaUsage` |
| Los tokens de salida son el 80 % del gasto | Limitar salida (`maxTokens`, `stopSequences`, instrucciones), **structured outputs**, modelo más chico |
| Quiero que el modelo devuelva JSON siempre válido y sin reintentos | **Structured outputs** (`outputConfig.textFormat` con JSON Schema; `additionalProperties: false`) |
| La búsqueda no encuentra códigos/SKU/nombres propios | **Búsqueda híbrida** (semántica + léxica) |
| Los resultados están bien pero mal ordenados | **Reranking** (recuperar amplio, rerankear angosto) |
| El vector store tiene piso mensual alto y poco tráfico | **S3 Vectors** o **OpenSearch Serverless NextGen** (escala a cero) |
| Necesito baja latencia y hybrid search en producción de alto QPS | **OpenSearch** (provisionado o Serverless) |
| Quiero monitorear la latencia que **percibe** el usuario en streaming | Métrica **`TimeToFirstToken`** |
| Quiero saber cuánta cuota TPM estoy consumiendo realmente | Métrica **`EstimatedTPMQuotaUsage`** |
| Necesito ver prompts y respuestas completas para depurar | **Model Invocation Logging** (habilitar; S3 si el payload es grande) |
| Necesito saber quién invocó el modelo | **CloudTrail** (y recordar que las acciones de agentes son *data events*, apagadas por defecto) |
| Quiero atribuir costo por equipo o aplicación | **Application inference profiles** + cost allocation tags (activar el tag en Billing) |
| Necesito detectar un pico de gasto anómalo | **Cost Anomaly Detection** (monitor acotado a Bedrock) + AWS Budgets |
| Debo detectar degradación de calidad silenciosa | **Evaluación online muestreada** + **canary diario** con golden set |
| Debo detectar que el modelo del proveedor cambió | **Canary suite diaria** con prompts y resultados conocidos |
| Debo detectar errores lógicos en un agente multi-paso | **Reasoning path tracing** (spans por paso) + evaluadores de trayectoria |
| Quiero medir consistencia entre corridas | **Output diffing** (repetición n veces, similitud semántica y diff estructural) |
| Una herramienta domina la latencia del agente | Usar `TargetExecutionTime` del **Gateway** para separar plataforma vs. target |
| El agente se queda en bucle con herramientas | Línea base de **tool calls por sesión** + alarma por desvío |
| El índice de vectores fue cambiando y la recuperación empeora | Monitoreo de **hit rate y distribución de embeddings** (deriva del corpus) |
| Subí 20.000 documentos y quiero validar que se indexaron bien | Índice de **`RawDataSize`** + prueba de recuperación por documento + tasa de resultados vacíos |

### 8.2 Dirección de las métricas (orientación)

| Métrica | Orientación |
|---|---|
| TTFT, latencia P95 (modelo y retrieval), hit rate de caché, OTPS, tasa de resolución | **Más bajo** (latencia) / **más alto** (el resto) |
| Costo por tarea resuelta, costo por sesión, tokens por tarea, tool calls por tarea | **Más bajo = mejor** |
| Tokens de entrada/salida por request | Más bajo es mejor **si la calidad se mantiene** (no es un objetivo absoluto) |
| Tasa de alucinación, refusal rate, tasa de intervención de guardrail (cuando el contenido es legítimo) | Más bajo es mejor |
| Throttles, reintentos, errores 4xx/5xx, resultados de retrieval vacíos | Más bajo es mejor |
| Utilización de PT/Reserved, GPU/OCU utilization | **Más alto = mejor** (hasta ~85 %) |
| Score de calidad (faithfulness, correctness), CSAT, deflexión | Más alto es mejor |

### 8.3 Modos de facturación de un vistazo

| Modo | Precio vs. Standard | Compromiso | Latencia | Cuota |
|---|---|---|---|---|
| Standard | base | — | normal | RPM/TPM on-demand |
| Priority | ~+75 % | — | mejor, priorizada | mejor protegida |
| Flex | ~−50 % | — | variable, best-effort | puede throttlear |
| Batch | −50 % | — | hasta 24 h | fuera de RPM/TPM on-demand |
| Reserved | fijo mensual | 1–3 meses | garantizada (99,5 %) | propia |
| PT | por hora/MU | 0/1/6 meses | dedicada | propia |

---

## 9. Patrones de pregunta y trampas frecuentes

### 9.1 Trampas

1. **Optimizar solo el precio por token.** El escenario típico describe un vector store carísimo o agentes amplificando 5–10×, y la respuesta "usar un modelo más barato" es un distractor.
2. **Olvidar que `maxTokens` consume cuota.** En preguntas de throttling con consumo "por debajo del límite", la respuesta correcta suele ser ajustar `maxTokens`/concurrencia, no comprar más cuota.
3. **Confundir prompt caching con caché semántica.** Prompt caching reutiliza **prefijo** (descuenta tokens de entrada); la caché semántica **evita la llamada** (devuelve una respuesta guardada). Preguntan esto seguido.
4. **Asumir que prompt caching siempre ahorra.** Con hit ratio bajo (~<30 %) se paga más: el costo de escritura (1,25×–2×) supera el ahorro de lecturas.
5. **Creer que streaming reduce el costo o el tiempo total.** No hace ninguna de las dos cosas: mejora la latencia **percibida**.
6. **Elegir PT para un modelo estándar con tráfico moderado.** PT y Reserved se pagan ociosos; y los modelos custom **sí o sí** requieren PT (ese es el caso legítimo).
7. **Usar IPR entre familias distintas de modelos.** No está soportado.
8. **Confundir Flex con Batch.** Ambos son −50 %, pero Flex es síncrono con latencia variable; Batch es asíncrono por S3 con ventana de 24 h.
9. **Creer que el auto-scaling de la aplicación resuelve el throttling.** La cuota la fija AWS por modelo/región; escalar la app no la aumenta.
10. **Pensar que las métricas operativas detectan degradación de calidad.** No lo hacen: hacen falta evaluaciones (juez, golden set, grounding).
11. **Monitorear solo promedios de latencia.** Con cold starts de hasta 14× de varianza, el promedio oculta el problema; hay que usar **percentiles**.
12. **Activar tags de inference profile y no activarlos en Billing.** El paso de "activar el cost allocation tag" es el que más se olvida y hace invisible toda la atribución.
13. **Habilitar Model Invocation Logging sin política de datos.** Costo de ingestión y riesgo de PII; y en CloudWatch el body se trunca (~100 KB) — usar S3 para payloads grandes.
14. **Suponer que CloudTrail registra las invocaciones de agentes.** Son *data events*: hay que habilitarlos.
15. **Aplicar caché semántica a flujos no repetitivos** (chat abierto, agentes dependientes de estado): hit rate ~0 y se agrega latencia/complejidad sin beneficio.

### 9.2 Frases que suelen indicar la respuesta correcta

- **"costo por tarea resuelta"** → métrica de FinOps que el examen premia frente a "costo por token".
- **"percentiles p95/p99"** → siempre que se hable de SLO y varianza.
- **"el prefijo estable va primero"** → prompt caching bien configurado.
- **"atribuir por equipo/aplicación"** → application inference profiles + tags.
- **"detectar antes de que el usuario lo note"** → alarmas/anomalías + canary suite.
- **"el modelo correcto para cada consulta"** → routing/cascada, no un modelo único.
- **"dato sintético / maestro-estudiante"** → destilación.
- **"el patrón de tráfico es discontinuo (ráfagas + silencio)"** → escala a cero o PT según latencia tolerable.

---

## 10. Checklists operativos

### 10.1 Diseño (antes de codificar)
- [ ] Definir SLOs: p95 de latencia total, **TTFT**, tasa de error, disponibilidad.
- [ ] Definir presupuesto de costo por tarea resuelta y por usuario/mes.
- [ ] Elegir el **piso de calidad** (métrica ancla + umbral) que ningún ahorro puede violar.
- [ ] Decidir el mapa de modelos: qué tarea va a qué modelo/modo (Standard/Flex/Batch/Reserved/PT).
- [ ] Decidir el vector store según QPS y latencia requerida (S3 Vectors / OpenSearch NextGen / provisionado / Aurora pgvector).
- [ ] Diseñar la estrategia de caché en cuatro capas y la política de TTL e invalidación.
- [ ] Definir el esquema de atribución de costos (tags, inference profiles, CUR).

### 10.2 Eficiencia de tokens
- [ ] `CountTokens` en la ruta de pre-validación (antes de invocar).
- [ ] Presupuesto de contexto explícito y versionado por workflow.
- [ ] `maxTokens` dimensionado por caso de uso, no por default.
- [ ] Structured outputs donde haya contrato de datos.
- [ ] Prefijos estables primero + cache checkpoints donde el prefijo ≥ mínimo del modelo.
- [ ] Revisión mensual de tokens por tarea (deriva creciente = bug).

### 10.3 Throughput y capacidad
- [ ] Inventario de RPM/TPM por modelo y región; `EstimatedTPMQuotaUsage` en el dashboard.
- [ ] Concurrencia acotada por modelo (semáforos) y retries con backoff+jitter.
- [ ] Toda carga no interactiva movida a Batch o Flex.
- [ ] Reserva (Reserved/PT) dimensionada sobre tráfico medido, con revisión de utilización mensual.
- [ ] CRIS habilitado donde la residencia de datos lo permita.

### 10.4 Latencia
- [ ] Benchmark reproducible con P50/P90/P99 y ≥3 repeticiones, congelado como baseline.
- [ ] Streaming en todos los flujos interactivos; TTFT medido en cliente o vía métrica nativa.
- [ ] Pre-cómputo para consultas predecibles y cache warming antes de picos.
- [ ] Paralelización de tareas independientes con límite de concurrencia.
- [ ] Timeouts y circuit breakers en cada dependencia externa (tools, APIs).

### 10.5 Observabilidad
- [ ] Model invocation logging habilitado con destino y retención decididos (S3 para payloads grandes).
- [ ] Trazas con `trace_id`/`session_id`/`model_version`/`prompt_version`.
- [ ] Dashboard de on-call corto (5–8 indicadores) + dashboard de negocio.
- [ ] Alarmas accionables: throttles, errores, TTFT, latencia, picos de tokens, costo.
- [ ] Cost Anomaly Detection + Budgets configurados desde el día 1.
- [ ] Evaluación online muestreada (con presupuesto del juez controlado).
- [ ] Canary suite diaria con golden set.

### 10.6 Operación de vector store y herramientas
- [ ] Monitoreo de latencia de consulta, tasa de resultados vacíos, lag de ingesta y tamaño indexado.
- [ ] Rutina de reindexado y compactación calendarizada.
- [ ] Validación de calidad de datos antes de cada ingesta masiva.
- [ ] Baseline de tool calls por tarea y latencia por herramienta (Gateway/`TargetExecutionTime`).
- [ ] Alarmas por desvío relativo de patrones de herramientas.

---

## 11. Anexos

### Anexo A. Snippets de código

**A.1 — Medir tokens antes de invocar (CountTokens) y calcular costo**

```python
import boto3, json
rt = boto3.client("bedrock-runtime")

def contar_tokens(model_id, system, messages, tools=None):
    req = {"modelId": model_id, "system": system, "messages": messages}
    if tools:
        req["toolConfig"] = {"tools": tools}
    return rt.count_tokens(**req)["inputTokens"]

PRECIOS = {                       # USD por 1.000 tokens (referencia; verificar)
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0": {"in": 0.003,  "out": 0.015},
    "us.amazon.nova-lite-v1:0":                     {"in": 0.00006, "out": 0.00024},
}

def costo_estimado(model_id, tok_in, max_tok_out):
    p = PRECIOS[model_id]
    return tok_in / 1000 * p["in"] + max_tok_out / 1000 * p["out"]
```

**A.2 — Converse con streaming, prompt caching y métricas de caché**

```python
resp = rt.converse_stream(
    modelId="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    system=[{"text": SYSTEM_PROMPT},
            {"cachePoint": {"type": "default"}}],          # checkpoint tras el prefijo estable
    messages=messages,
    inferenceConfig={"maxTokens": 800, "temperature": 0.2},
)
# Al final del stream llega el evento 'metadata' con usage:
# {'inputTokens', 'outputTokens', 'cacheReadInputTokens', 'cacheWriteInputTokens'}
```
Buena práctica: **todo el contenido estable (tools + system + documentos fijos) primero, y el checkpoint después**; el contenido variable (mensaje del usuario) al final. Cambiar algo antes del checkpoint invalida el caché.

**A.3 — Caché en dos capas (exacta + semántica) con Redis vectorial**

```python
import hashlib, json, redis
from redis.commands.search.query import Query

def fingerprint(model_id, params, prompt_version, user_input, tenant):
    norm = " ".join(user_input.lower().split())
    payload = f"{model_id}|{json.dumps(params, sort_keys=True)}|{prompt_version}|{norm}|{tenant}"
    return hashlib.sha256(payload.encode()).hexdigest()

def get_or_generate(user_input, model_id, params, prompt_version, tenant, generate):
    # 1) exacta
    key = f"resp:{fingerprint(model_id, params, prompt_version, user_input, tenant)}"
    hit = r.get(key)
    if hit:
        metric("cache_hit", layer="exact", saved_usd=estimate_saved())
        return json.loads(hit)

    # 2) semántica (namespace por tenant)
    vec = embed(user_input)
    q = (Query(f"(@tenant:{{{tenant}}})=>[KNN 1 @v $vec AS score]")
         .sort_by("score").return_fields("response", "score").dialect(2))
    res = r.ft("semcache").search(q, query_params={"vec": vec.tobytes()})
    if res.docs and float(res.docs[0].score) >= THRESHOLD:      # 0.92–0.97 según plantilla
        metric("cache_hit", layer="semantic", similarity=float(res.docs[0].score),
               saved_usd=estimate_saved())
        return json.loads(res.docs[0].response)

    # 3) miss → generar y guardar en ambas capas
    out = generate(user_input)
    r.setex(key, TTL_EXACT, json.dumps(out))
    store_semantic(tenant, vec, out, ttl=TTL_SEM)
    metric("cache_miss")
    return out
```
⚠️ Guardar siempre `prompt_version` con la respuesta y **invalidar el caché cuando cambie el prompt o el modelo**.

**A.4 — Job de batch inference (JSONL → S3 → job)**

```python
# 1) Preparar el JSONL: un request por línea, con inferenceId único
with open("input.jsonl", "w") as f:
    for i, prompt in enumerate(prompts):
        f.write(json.dumps({
            "recordId": f"rec-{i}",
            "modelInput": {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "messages": [{"role": "user", "content": prompt}],
            },
        }) + "\n")

s3.upload_file("input.jsonl", BUCKET, "batch/input.jsonl")
job = bedrock.create_model_invocation_job(
    jobName="nightly-summaries",
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    roleArn=ROLE_ARN,
    inputDataConfig={"s3InputDataConfig": {"s3Uri": f"s3://{BUCKET}/batch/input.jsonl"}},
    outputDataConfig={"s3OutputDataConfig": {"s3Uri": f"s3://{BUCKET}/batch/output/"}},
)
```
Buenas prácticas: 1.000–50.000 registros por job, `inferenceId`/`recordId` único y trazable, orquestación con Step Functions `Map` para respetar la cuota de jobs concurrentes, y polling con backoff.

**A.5 — Structured output con esquema**

```python
schema = {
  "type": "object",
  "properties": {
    "categoria": {"type": "string", "enum": ["facturacion", "tecnico", "otro"]},
    "prioridad": {"type": "integer", "minimum": 1, "maximum": 5},
    "resumen":   {"type": "string"}
  },
  "required": ["categoria", "prioridad", "resumen"],
  "additionalProperties": False,        # obligatorio en Bedrock
}
resp = rt.converse(
    modelId=MODEL_ID,
    messages=[{"role": "user", "content": [{"text": ticket}]}],
    inferenceConfig={"maxTokens": 512, "temperature": 0},
    outputConfig={"textFormat": {"type": "json_schema",
                                 "structure": {"jsonSchema": {
                                     "schema": json.dumps(schema),
                                     "name": "clasificacion"}}}},
)
if resp["stopReason"] == "max_tokens":
    raise RuntimeError("Truncado: la salida no está completa")
```

**A.6 — Cliente con reintentos adaptativos, keep-alive y semáforo de concurrencia**

```python
from botocore.config import Config
import asyncio

CFG = Config(
    retries={"max_attempts": 5, "mode": "adaptive"},   # backoff exponencial + jitter
    tcp_keepalive=True,                                 # reutiliza conexiones (~−25 % TTFT)
    max_pool_connections=50,
    read_timeout=120,
)
rt = boto3.client("bedrock-runtime", config=CFG)

SEM = asyncio.Semaphore(8)          # límite de concurrencia POR MODELO

async def invocar(payload):
    async with SEM:
        return await asyncio.to_thread(rt.converse, **payload)
```

**A.7 — Instrumentación con métricas custom (EMF)**

```python
print(json.dumps({
    "_aws": {"Timestamp": int(time.time()*1000),
             "CloudWatchMetrics": [{
                 "Namespace": "GenAI/App",
                 "Dimensions": [["service", "environment", "model_id", "prompt_version"]],
                 "Metrics": [{"Name": "tokens_in"}, {"Name": "tokens_out"},
                             {"Name": "cache_read_tokens"}, {"Name": "ttft_ms"},
                             {"Name": "cost_usd"}, {"Name": "retries"}]}]},
    "service": "soporte-api", "environment": "prod",
    "model_id": model_id, "prompt_version": "v7",
    "tokens_in": u["inputTokens"], "tokens_out": u["outputTokens"],
    "cache_read_tokens": u.get("cacheReadInputTokens", 0),
    "ttft_ms": ttft, "cost_usd": costo, "retries": retries,
}))
```
⚠️ **No usar dimensiones de alta cardinalidad** (request_id, user_id) en métricas: multiplican el costo de CloudWatch. Enviar esas etiquetas a los **logs** y correlacionar por `trace_id`.

**A.8 — Script de benchmark de latencia (TTFT + total, P50/P90/P99)**

```python
import statistics, time
def medir(prompt, n=20):
    ttfts, totales = [], []
    for _ in range(n):
        t0 = time.perf_counter(); ttft = None
        stream = rt.converse_stream(modelId=MODEL_ID,
                    messages=[{"role":"user","content":[{"text":prompt}]}],
                    inferenceConfig={"maxTokens":256,"temperature":0.1})["stream"]
        for ev in stream:
            if "contentBlockDelta" in ev and ttft is None:
                ttft = (time.perf_counter()-t0)*1000
            elif "metadata" in ev:
                totales.append((time.perf_counter()-t0)*1000)
        ttfts.append(ttft)
    p = lambda xs, q: statistics.quantiles(xs, n=100)[q-1]
    return {"ttft_p50": p(ttfts,50), "ttft_p90": p(ttfts,90), "ttft_p99": p(ttfts,99),
            "total_p50": p(totales,50), "total_p99": p(totales,99)}
```

### Anexo B. Consultas CloudWatch Logs Insights y Athena

```sql
-- B.1 Tokens y latencia por modelo (última hora), desde métricas derivadas de logs
fields @timestamp, modelId, operation, input.inputTokenCount, output.outputTokenCount
| filter schemaType = "ModelInvocationLog"
| stats count() as invocaciones,
        sum(input.inputTokenCount) as tok_in,
        sum(output.outputTokenCount) as tok_out,
        avg(input.inputTokenCount) as tok_in_medio,
        pct(output.outputTokenCount, 95) as tok_out_p95
        by modelId, operation
| sort tok_in desc

-- B.2 Requests con prompts anómalamente grandes (candidatos a prompt bloat)
fields @timestamp, modelId, requestId, input.inputTokenCount
| filter schemaType = "ModelInvocationLog" and input.inputTokenCount > 15000
| sort input.inputTokenCount desc
| limit 50

-- B.3 Errores y throttles agrupados por modelo
fields @timestamp, modelId, errorCode, errorMessage
| filter ispresent(errorCode)
| stats count() by modelId, errorCode
| sort count() desc

-- B.4 Sesiones más costosas del día (requiere spans con atributos OTel)
fields resource.attributes.service.name as serviceName,
       attributes.session.id as sessionId,
       attributes.user.Id as userId,
       traceId, durationNano/1000000 as durMs
| filter resource.attributes.aws.service.type = "gen_ai_agent"
| stats sum(attributes.gen_ai.usage.input_tokens) as tok_in,
        sum(attributes.gen_ai.usage.output_tokens) as tok_out,
        count(spanId) as spans,
        pct(durMs, 95) as p95_ms
        by sessionId, userId
| sort tok_out desc
| limit 20
```

```sql
-- B.5 Costo y tokens por equipo, desde CUR 2.0 en Athena
SELECT line_item_usage_account_id,
       line_item_resource_id                              AS inference_profile,
       SUM(line_item_usage_amount)                        AS unidades,
       SUM(line_item_unblended_cost)                      AS costo_usd
FROM cur2
WHERE line_item_product_code = 'AmazonBedrock'
  AND line_item_usage_start_date >= current_date - interval '30' day
GROUP BY 1, 2
ORDER BY costo_usd DESC;
```

```bash
# B.6 Alarmas esenciales (resumen de comandos)
# Throttles por modelo
aws cloudwatch put-metric-alarm --alarm-name bedrock-throttles \
  --metric-name InvocationThrottles --namespace AWS/Bedrock \
  --statistic Sum --period 300 --threshold 10 --comparison-operator GreaterThanThreshold

# Presión de cuota TPM
aws cloudwatch put-metric-alarm --alarm-name bedrock-tpm-quota \
  --metric-name EstimatedTPMQuotaUsage --namespace AWS/Bedrock \
  --statistic Average --period 60 --threshold 80 --comparison-operator GreaterThanThreshold

# Budget con alerta al 80 %
aws budgets create-budget --account-id "$ACCT" --budget file://budget.json
```

### Anexo C. Glosario

| Término | Definición |
|---|---|
| **TTFT** | Time To First Token: latencia hasta el primer token; métrica clave de UX en streaming |
| **OTPS / ITL** | Tokens de salida por segundo / latencia entre tokens |
| **Burndown multiplier** | Factor con que los tokens de salida consumen cuota TPM en Bedrock |
| **Reserva previa de cuota** | La cuota se descuenta al iniciar la request según `input + maxTokens` |
| **Prompt caching** | Reutilización del cómputo del prefijo; descuenta tokens de entrada y baja TTFT |
| **Caché semántica** | Caché de respuestas indexado por similitud de embeddings; evita la llamada al modelo |
| **Hash determinista / fingerprint** | Clave de caché derivada del modelo, parámetros, versión de prompt e input normalizado |
| **Intelligent Prompt Routing (IPR)** | Routing administrado entre dos modelos de la misma familia por costo/calidad |
| **Cascade routing** | Escalado de un modelo chico a uno grande según un chequeo de confianza |
| **Distillation** | Entrenar un modelo estudiante a partir de un maestro; menor costo y latencia |
| **Reserved tier** | Capacidad TPM reservada por 1–3 meses a precio fijo, con desborde a Standard |
| **Provisioned Throughput (MU)** | Capacidad dedicada facturada por hora; **obligatoria** para modelos custom |
| **Batch inference** | Procesamiento asíncrono desde/hacia S3 al 50 % del precio |
| **Flex / Priority** | Niveles on-demand con −50 % / +75 % de precio |
| **CRIS** | Cross-Region Inference: enrutamiento entre regiones del perfil |
| **RRF** | Reciprocal Rank Fusion: técnica de fusión de resultados de búsqueda híbrida |
| **EMF** | CloudWatch Embedded Metric Format: publicar métricas a través de logs estructurados |
| **Golden dataset** | Set congelado de casos con resultados correctos conocidos |
| **Output diffing** | Comparación de salidas entre versiones/corridas para detectar cambios |
| **Reasoning path tracing** | Trazar el razonamiento por pasos de un agente para localizar errores lógicos |
| **Semantic drift** | Cambio gradual en la distribución semántica de consultas o respuestas |
| **Costo por tarea resuelta** | Métrica de FinOps que divide el gasto por tareas efectivamente completadas |

### Anexo D. Fuentes consultadas

**Documentación oficial de AWS**
- Capacity and Performance de Bedrock (tiers, límites y marco de decisión) — https://docs.aws.amazon.com/bedrock/latest/userguide/capacity-limits-cost-optimization.html
- Prompt caching — https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html y https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.md
- `CountTokens` — https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_CountTokens.html y https://docs.aws.amazon.com/boto3/latest/reference/services/bedrock-runtime/client/count_tokens.html
- Cómo se cuentan los tokens (burndown) — https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html
- Optimización de costos de Bedrock (caching, IPR, destilación, Prompt Management) — https://aws.amazon.com/bedrock/cost-optimization/
- Intelligent Prompt Routing — https://aws.amazon.com/bedrock/intelligent-prompt-routing/
- CloudWatch: observabilidad GenAI — https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/GenAI-observability.html
- CloudWatch: Model Invocations — https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/model-invocations.html
- AgentCore: datos de observabilidad del Gateway — https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-gateway-metrics.html
- AgentCore: ver datos de observabilidad — https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-view.html
- AgentCore: precios (evaluaciones, runtime, gateway, memoria) — https://aws.amazon.com/bedrock/agentcore/pricing/
- Prescriptive Guidance: observabilidad y monitoreo de agentes — https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-serverless/observability-and-monitoring.html
- Well-Architected Agentic AI Lens: planificación y medición de performance — https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentperf01.html
- Lambda: canary con alias ponderados — https://docs.aws.amazon.com/lambda/latest/dg/configuring-alias-routing.html
- In-scope services AIP-C01 — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html

**Anuncios y blogs de AWS**
- Observabilidad de First Token Latency y Quota Consumption (marzo 2026) — https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-bedrock-observability-ttft-quota/
- Reserved tier para Claude Opus 4.5 y Haiku 4.5 — https://aws.amazon.com/about-aws/whats-new/2026/01/amazon-bedrock-reserved-tier-claude-opus-haiku/
- Uso efectivo de prompt caching — https://aws.amazon.com/blogs/machine-learning/effectively-use-prompt-caching-on-amazon-bedrock/
- Structured outputs en Bedrock (constrained decoding) — https://aws-news.com/article/2026-02-06-structured-outputs-on-amazon-bedrock-schema-compliant-ai-responses
- Destilación para routing de búsqueda semántica de vídeo (>95 % de ahorro) — https://aws.amazon.com/blogs/machine-learning/optimize-video-semantic-search-intent-with-amazon-nova-model-distillation-on-amazon-bedrock/
- Orquestación de batch jobs con Step Functions — https://aws.amazon.com/blogs/machine-learning/build-a-serverless-amazon-bedrock-batch-job-orchestration-workflow-using-aws-step-functions/
- Atribución de costos con application inference profiles — https://aws-news.com/article/2026-08-13-track-generative-ai-costs-with-amazon-bedrock-inference-profiles
- Búsqueda vectorial optimizada en costo con OpenSearch y S3 Vectors — https://builder.aws.com/content/33rpGPf5mEUHxsGxnmXPZ5yI7li/cost-optimized-vector-search-with-amazon-opensearch-service-and-s3-vectors
- Monitoreo de Guardrails con CloudWatch — https://repost.aws/articles/AR-ZBYACEoSSeYSLhKzu83uQ/
- Lanzamiento de CloudWatch GenAI Observability — https://aws.amazon.com/blogs/mt/launching-amazon-cloudwatch-generative-ai-observability-preview/

**Referencia técnica y análisis de terceros**
- Guía de throughput y latencia en Bedrock (cuotas, PT, Reserved, latency-optimized, IPR) — https://hidekazu-konishi.com/entry/amazon_bedrock_inference_throughput_and_latency_optimization.html
- Guía de operaciones de producción de AgentCore (las cuatro señales, dashboards) — https://hidekazu-konishi.com/entry/amazon_bedrock_agentcore_production_guide.html
- Monitoreo de Bedrock: métricas, desafíos y buenas prácticas — https://www.groundcover.com/learn/observability/aws-bedrock-monitoring
- Benchmark multi-modelo de latencia (TTFT, CRIS, caché, cold starts) — https://builder.aws.com/content/3Bo5naX7p1ncmB4FOoy3dJ4SD5M/benchmarking-amazon-bedrock-llm-latency-a-multi-model-comparison
- Prompt caching en Bedrock con Amazon Nova (benchmarks de latencia y cost) — https://builder.aws.com/content/33zsO2Bc7UbsnLb9XTOBcuv1O2c/amazon-bedrock-prompt-caching-with-the-amazon-nova-model
- Análisis de precio de Bedrock y costos ocultos — https://cloudburn.io/blog/amazon-bedrock-pricing y https://caylent.com/blog/amazon-bedrock-pricing-explained
- Costo real de almacenamiento vectorial (S3 Vectors vs. OpenSearch vs. pgvector) — https://darryl-ruggles.cloud/the-real-cost-of-vector-storage-s3-vectors-vs-opensearch-vs-pgvector-vs-pinecone/
- OpenSearch Serverless NextGen (scale-to-zero, OCU) — https://caylent.com/blog/amazon-open-search-serverless-next-gen-whats-new
- Caché semántica en producción (umbrales, hit rates, arquitectura) — https://futureagi.com/blog/what-is-semantic-caching-llms-2026/ y https://tianpan.co/blog/2026-04-09-semantic-caching-llm-production
- FinOps para GenAI (costo, performance, impacto de negocio) — https://www.finops.org/wg/optimizing-genai-usage/
- Métricas de eficiencia de tokens y costo por tarea resuelta — https://www.glean.com/perspectives/key-metrics-for-evaluating-token-efficiency-in-ai-systems
- Monitoreo de alucinaciones y drift (señales, canary suites, golden sets) — https://www.progressiverobot.com/2026/08/09/hallucination-monitoring-model-drift/

---

## 12. Plan de repaso y práctica (5 días)

| Día | Foco | Lectura | Práctica hands-on |
|---|---|---|---|
| **1** | Medición y eficiencia de tokens | §3, §4.1 | Habilitar **Model Invocation Logging**; invocar 5 modelos con el mismo prompt; medir tokens con `CountTokens`, comparar con la estimación `len/4` y calcular costo por request con `usage` |
| **2** | Caching | §4.4 | Configurar **prompt caching** con un system prompt > mínimo del modelo; medir `cacheRead/WriteInputTokens` en 20 requests seguidos y calcular el hit ratio. Luego montar una **caché exacta** con Redis y medir el ahorro |
| **3** | Latencia y throughput | §5.1, §5.3, §5.5 | Benchmark de TTFT P50/P90/P99 con `converse_stream` (frío vs. caliente, con y sin caché); provocar un `ThrottlingException` con paralelismo y diagnosticarlo con `maxTokens` + concurrencia |
| **4** | Observabilidad | §6.1–§6.3 | Armar un dashboard con `Invocations`, `InvocationLatency`, `TimeToFirstToken`, `InputTokenCount`, `OutputTokenCount`, `InvocationThrottles`, `EstimatedTPMQuotaUsage`; crear 3 alarmas accionables y una consulta de Logs Insights |
| **5** | Costos, retrieval y repaso | §4.2, §5.2, §6.4–§6.6, §8 | Crear dos **application inference profiles** con tags distintos, activar el tag en Billing y verificar la separación en Cost Explorer (esperar la propagación); configurar `Cost Anomaly Detection`; repasar la cheat sheet §8 en voz alta |

**Ejercicio de cierre (el más rentable):** tomá un caso de uso propio y escribí, en una página: (1) SLO de latencia con TTFT y p95; (2) presupuesto de tokens por tarea y por sección del prompt; (3) mapa de modelos/modos (qué va a chico, qué a grande, qué a Batch); (4) estrategia de caché en cuatro capas con TTL; (5) el dashboard de 6 indicadores y sus 3 alarmas; (6) el esquema de atribución de costos. Si podés escribir esa página sin dudar, el Dominio 4 está cerrado.

### Cierre

En una frase: **medí tokens y latencia por workflow, enrutá cada consulta al modelo más barato que pase tu piso de calidad, cacheá agresivamente lo repetitivo (prefijo, respuesta y semántica), mové todo lo que no sea interactivo a Batch o Flex, reservá capacidad sólo cuando la utilización la justifique, y observá las cuatro señales —métricas, logs, trazas y evaluaciones— porque las tres primeras nunca te van a avisar que la respuesta está mal.**
