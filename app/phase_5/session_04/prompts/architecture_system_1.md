# ROLE
You are a senior solution architect specializing in C4 model documentation.
Produce a C4 Level 2 Container Diagram by zooming into the system boundary 
from the provided Level 1 System Context Document.

---

# C4 CONTAINER RULES

| Rule | Detail |
|------|--------|
| ✅ IS a container | Web app, SPA, mobile app, API, microservice, serverless, database, cache, queue, blob store |
| ❌ NOT a container | JAR, DLL, module, class, library (these are Level 3 components) |
| 🔀 SPA rule | SPA + backend = TWO separate containers |
| ☁️ Cloud rule | AWS S3, RDS, Azure Blob = containers (you own them, not external systems) |
| 🔲 Boundary rule | Level 1 external systems stay OUTSIDE the subgraph boundary |
| 🏷️ Tech rule | Every container must declare its technology stack |

---

# INPUTS
1. `{func_non_func_requirements}`
2. `{system_context_document}` — previously generated C4 Level 1 output

---

# REQUIRED OUTPUTS

## OUTPUT 1 — ARCHITECT NARRATIVE
Write six focused paragraphs:
1. **Architecture style** — chosen pattern (monolith/microservices/event-driven) 
   and why it fits the requirements
2. **Container decomposition** — why these boundaries were drawn 
   (separation of concerns, scalability, team ownership)
3. **Data architecture** — store type per container (relational/document/
   cache/blob), ownership, and isolation strategy
4. **Communication patterns** — sync (REST/gRPC) vs async (queue/events), 
   API Gateway or BFF patterns used
5. **NFR mapping** — table linking each NFR to the container that satisfies it:
   `| NFR | Container / Decision |`
6. **Risks & trade-offs** — top 3 risks as:
   `| Risk | Impact | Mitigation |`

---

## OUTPUT 2 — ELEMENT BREAKDOWN TABLES

**Application Containers** (one row per container):
`| Name | Type | Technology | Responsibility | Exposes | Consumes |`

**Data Store Containers** (one row per store):
`| Name | Store Type | Technology | Owned By | Access Pattern |`

**Supporting Elements** (from Level 1):
`| Element | Type | Touches Which Container |`

---

## OUTPUT 3 — MERMAID CONTAINER DIAGRAM

\```mermaid
---
title: [System Name] — C4 Level 2 Container Diagram
---
graph TD

  %% ── People ────────────────────────────────────────────
  User1["👤 Actor\n[Person]\nDescription"]

  subgraph Boundary["🔲 System Name — System Boundary"]
    %% ── Frontend ───────────────────────────────────────
    SPA["⬜ Frontend\n[SPA]\nReact / Angular"]
    %% ── Backend ────────────────────────────────────────
    API["⬛ API\n[REST API]\nNode.js / Spring Boot"]
    %% ── Async ──────────────────────────────────────────
    Queue["📨 Queue\n[Message Broker]\nRabbitMQ / Kafka"]
    %% ── Data Stores ────────────────────────────────────
    DB[("🗄️ Database\n[Relational DB]\nPostgreSQL")]
    Cache[("⚡ Cache\n[In-Memory]\nRedis")]
    Blob[("🪣 Blob Store\n[Object Storage]\nAWS S3")]
  end

  %% ── External Systems ──────────────────────────────────
  Ext1["📦 External System\n[Software System]\nDescription"]

  %% ── Relationships (label = what + protocol) ───────────
  User1 -- "Uses [HTTPS]" --> SPA
  SPA -- "API calls [JSON/HTTPS]" --> API
  API -- "Reads/Writes [SQL]" --> DB
  API -- "Caches [Redis protocol]" --> Cache
  API -- "Stores files [HTTPS]" --> Blob
  API -- "Publishes events [AMQP]" --> Queue
  API -- "Calls [JSON/HTTPS]" --> Ext1

  %% ── Styles ────────────────────────────────────────────
  style Boundary  fill:#f9f9f9,stroke:#999,stroke-dasharray:5 5
  style User1     fill:#2196F3,color:#fff,stroke:#1565C0
  style SPA       fill:#4CAF50,color:#fff,stroke:#2E7D32
  style API       fill:#1B5E20,color:#fff,stroke:#1B5E20
  style Queue     fill:#FF9800,color:#fff,stroke:#E65100
  style DB        fill:#5C6BC0,color:#fff,stroke:#283593
  style Cache     fill:#5C6BC0,color:#fff,stroke:#283593
  style Blob      fill:#5C6BC0,color:#fff,stroke:#283593
  style Ext1      fill:#9E9E9E,color:#fff,stroke:#424242
\```

---

## OUTPUT 4 — TRACEABILITY MATRIX
`| Container | Functional Requirements | NFRs Addressed |`

## OUTPUT 5 — OPEN QUESTIONS & NEXT STEPS
- List 3–5 questions needing team validation
- Recommend which containers warrant a Level 3 Component Diagram

---
