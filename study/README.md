# AWS Certified AI Professional (AIP-C01)
## Guía de Estudio Completa

> **Guía integral** para el examen **AWS Certified Generative AI Developer – Professional (AIP-C01)**
> 
> Contenido técnico completo construido a partir de documentación oficial de AWS, organizado por dominios y optimizado para la preparación del examen.

---

## 📋 Acerca del Examen

El **AIP-C01** es la certificación profesional de AWS centrada en desarrollo de aplicaciones con inteligencia artificial generativa (GenAI). Evalúa competencias técnicas en:

- **Foundation Models (FMs)**: Selección, configuración, fine-tuning y despliegue
- **RAG (Retrieval-Augmented Generation)**: Vector stores, embeddings, recuperación de contexto
- **Agentic AI**: Diseño de agentes, orquestación, integración con herramientas
- **Seguridad y Compliance**: Gobernanza de datos, IA responsable, controles de entrada/salida
- **Optimización operacional**: Costes, latencia, observabilidad, troubleshooting

### Datos Clave

| Dato | Valor |
| --- | --- |
| **Duración** | 180 minutos |
| **Preguntas** | 75 (65 puntuadas + 10 no puntuadas) |
| **Formato** | Opción múltiple y respuesta múltiple |
| **Puntuación** | Escala 100–1000 (mínimo 750 para aprobar) |
| **Modelo de scoring** | Compensatorio (no hace falta aprobar cada dominio) |
| **Idiomas** | Inglés, japonés, coreano, chino simplificado |
| **Costo** | USD 300 |

---

## 📚 Estructura del Contenido

Esta guía está organizada en **5 dominios**, siguiendo la estructura oficial del examen:

### **Domain 1** — Foundation Model Integration, Data Management, and Compliance
**31% del contenido puntuado** (≈20 preguntas)

Selección y configuración de FMs, gestión de datos para consumo de modelos, implementación de vector stores, mecanismos de retrieval, prompt engineering y governance.

[📖 Ver Domain 1](/study/domain-1/)

---

### **Domain 2** — Implementation and Integration
**26% del contenido puntuado** (≈17 preguntas)

Soluciones agentic AI, despliegue de modelos, arquitecturas de integración empresarial, integraciones de API de FM, patrones de aplicación y herramientas de desarrollo.

[📖 Ver Domain 2](/study/domain-2/)

---

### **Domain 3** — AI Safety, Security, and Governance
**20% del contenido puntuado** (≈13 preguntas)

Controles de entrada/salida, seguridad y privacidad de datos, governance y compliance, IA responsable (fairness, explainability, toxicity, bias).

[📖 Ver Domain 3](/study/domain-3/)

---

### **Domain 4** — Operational Efficiency and Optimization
**12% del contenido puntuado** (≈8 preguntas)

Gestión de costes, optimización de latencia y throughput, observabilidad y métricas, ajuste de parámetros de retrieval, manejo de fallos.

[📖 Ver Domain 4](/study/domain-4/)

---

### **Domain 5** — Testing, Validation, and Troubleshooting
**11% del contenido puntuado** (≈7 preguntas)

Marcos de evaluación, testing de retrieval y agentes, monitoreo continuo, troubleshooting de prompts, manejo de contexto y integraciones.

[📖 Ver Domain 5](/study/domain-5/)

---

## 📊 Informes Completos por Dominio

Cada dominio cuenta con un **informe técnico integral** que consolida:

- ✅ Todos los skills y tasks del dominio
- ✅ Servicios de AWS involucrados con ejemplos prácticos
- ✅ Patrones de arquitectura y decisión
- ✅ Métricas, límites y cuotas
- ✅ Patrones de pregunta del examen y trampas comunes
- ✅ Checklist operativo por etapa
- ✅ Snippets de código y consultas
- ✅ Plan de repaso específico

### Informes Disponibles

- [📊 Informe Domain 1 — Foundation Model Integration](/study/informes/informe_dominio1_implementation_integration.md)
- [📊 Informe Domain 2 — Implementation and Integration](/study/informes/informe_dominio2_implementation_integration.md)
- [📊 Informe Domain 3 — AI Safety, Security & Governance](/study/informes/informe_dominio3_ai_safety_security_governance.md)
- [📊 Informe Domain 4 — Operational Efficiency & Optimization](/study/informes/informe_dominio4_operational_efficiency_optimization.md)
- [📊 Informe Domain 5 — Testing, Validation & Troubleshooting](/study/informes/informe_dominio5_testing_validation_troubleshooting.md)

---

## 🎯 Cómo Usar Esta Guía

### Para Estudio Inicial (Fase de Aprendizaje)
1. **Lee cada dominio en orden** (Domain 1 → Domain 5)
2. Para cada dominio, revisa primero el **README** del dominio
3. Luego estudia cada **Task** en orden (task-X-1, task-X-2, etc.)
4. Toma notas de conceptos clave y servicios AWS
5. Practica con los ejemplos de código cuando estén disponibles

### Para Repaso Intensivo (Pre-Examen)
1. **Lee los informes completos** de cada dominio
2. Focaliza en las secciones de "Patrones de pregunta y trampas"
3. Revisa los checklists operativos
4. Repasa las tablas de decisión (cuándo usar qué servicio)
5. Practica con escenarios de troubleshooting

### Para Consulta Rápida (Durante el Examen Mental)
1. Usa los **cheat sheets** de cada informe
2. Revisa las tablas de métricas y límites
3. Recuerda los patrones de arquitectura de referencia
4. Ten claros los criterios de selección de servicios

---

## 🔗 Servicios AWS Clave

Los servicios más importantes para el examen incluyen:

### Core GenAI Services
- **Amazon Bedrock** — Acceso a FMs, fine-tuning, RAG, Agents, Guardrails, Model Evaluation
- **Amazon SageMaker** — Entrenamiento, hosting, endpoints, fine-tuning, feature store
- **Amazon Q** — Asistente de IA empresarial
- **Amazon PartyRock** — Prototipado rápido de apps GenAI

### Data & Vector Stores
- **Amazon OpenSearch Service** — Vector search engine
- **Amazon Aurora PostgreSQL** (pgvector) — Vector storage en DB relacional
- **Amazon Kendra** — Enterprise search con ML
- **Amazon DocumentDB** — Soporte para vector search
- **Amazon DynamoDB** — NoSQL con integración de vector embeddings
- **Amazon MemoryDB for Redis** — In-memory vector search

### Data Processing & Ingestion
- **AWS Glue** — ETL y data catalog
- **Amazon Textract** — OCR y extracción de texto
- **Amazon Comprehend** — NLP y análisis de sentimiento
- **Amazon Transcribe** — Speech-to-text
- **Amazon Rekognition** — Computer vision

### Security & Governance
- **AWS IAM** — Control de acceso
- **AWS KMS** — Gestión de claves de cifrado
- **AWS Secrets Manager** — Gestión de credenciales
- **AWS CloudTrail** — Auditoría de API calls
- **AWS Config** — Compliance y configuración
- **Amazon Macie** — Detección de PII y datos sensibles

### Monitoring & Optimization
- **Amazon CloudWatch** — Logs, métricas, alarmas
- **AWS X-Ray** — Distributed tracing
- **AWS Cost Explorer** — Análisis de costes
- **AWS Trusted Advisor** — Recomendaciones de optimización

### Integration & Orchestration
- **AWS Step Functions** — Orquestación de workflows
- **AWS Lambda** — Compute serverless
- **Amazon API Gateway** — Gestión de APIs
- **Amazon EventBridge** — Event bus
- **Amazon SNS/SQS** — Mensajería

---

## 📖 Fuentes y Referencias

Todo el contenido de esta guía fue construido a partir de:

- [**AWS Exam Guide (AIP-C01)**](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html) — Guía oficial del examen
- **AWS Documentation** — Documentación técnica oficial de cada servicio
- [**AWS Whitepapers**](https://aws.amazon.com/whitepapers/) — Arquitecturas de referencia y best practices
- [**AWS Well-Architected Framework**](https://aws.amazon.com/architecture/well-architected/) — Principios de diseño

> ⚠️ **Nota sobre Licencias**: El contenido de las fuentes AWS fue parafraseado y resumido para cumplir con restricciones de licencia. Cada sección incluye enlaces a las páginas oficiales correspondientes.

---

## 🚀 Siguientes Pasos

1. **Empieza con Domain 1** — Es el más pesado (31%) y establece fundamentos
2. **Practica con la consola AWS** — Crea recursos reales (usa Free Tier cuando sea posible)
3. **Explora Amazon Bedrock** — Familiarízate con los FMs disponibles y sus capacidades
4. **Configura un proyecto RAG** — Implementa vector store + retrieval + FM
5. **Lee los whitepapers clave** — Especialmente sobre arquitecturas GenAI
6. **Toma notas de límites y cuotas** — Son preguntados en el examen
7. **Repasa los informes completos** una semana antes del examen

---

## 💡 Consejos para el Examen

- ✅ El examen es **compensatorio**: no necesitas aprobar cada dominio, solo alcanzar 750/1000 global
- ✅ Hay **10 preguntas no puntuadas** que no sabrás cuáles son (se usan para calibración)
- ✅ **Lee las preguntas dos veces**: las opciones suelen ser técnicamente correctas pero solo una es la "mejor" respuesta
- ✅ **Identifica las palabras clave**: "más rentable", "menor latencia", "más seguro", "más escalable"
- ✅ **Descarta opciones imposibles** primero, luego elige entre las restantes
- ✅ **Gestiona el tiempo**: 180 minutos / 75 preguntas = ~2.4 minutos por pregunta
- ✅ **Marca preguntas difíciles** para revisarlas al final si hay tiempo
- ✅ **No dejes preguntas en blanco**: no hay penalización por respuestas incorrectas

---

## 📝 Licencia y Uso

Este contenido es material de estudio personal. Las fuentes oficiales de AWS están sujetas a sus propias licencias. Consulta siempre la documentación oficial de AWS para información autorizada.

---

**¡Buena suerte en tu preparación! 🎓**
