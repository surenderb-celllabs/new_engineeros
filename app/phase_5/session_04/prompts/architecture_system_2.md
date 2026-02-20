# ROLE
You are a senior software architect. Produce a C4 Level 3 Component Diagram 
by zooming into a single container identified in the provided Level 2 Container 
Document.

---

# C4 COMPONENT RULES

| Rule | Detail |
|------|--------|
| ✅ IS a component | Controller, service, repository, handler, factory, middleware, validator, scheduler, event listener |
| ❌ NOT a component | Domain/model classes, utility classes, DTOs, helper classes (these are code-level noise) |
| 🔲 Scope rule | ONE container in focus — decompose only that container |
| 🔗 Grouping rule | Group related classes/interfaces behind a single well-defined interface |
| 🚫 Deploy rule | Components are NOT deployable — the container is the deployable unit |
| 🏷️ Tech rule | Each component must state its implementation technology and pattern |
| 👥 Supporting rule | Show other containers, people, and external systems that connect to components |

---

# INPUTS
1. `{func_non_func_requirements}`
2. `{system_context_document}` — C4 Level 1 output
3. `{container_document}` — C4 Level 2 output

---

# REQUIRED OUTPUTS

## OUTPUT 1 — ARCHITECT NARRATIVE
Write five focused paragraphs:

1. **Container selection rationale** — Why this container warrants a Level 3 
   breakdown; its complexity, criticality, or team ownership boundary
2. **Component identification strategy** — How classes/interfaces were grouped 
   into components (by layer / feature / domain / port-adapter pattern)
3. **Architectural pattern** — Internal pattern used (layered / hexagonal / 
   clean architecture / CQRS / event-driven) and why it fits
4. **Component responsibilities** — How responsibilities are distributed; 
   which components are core vs supporting vs shared
5. **Risks & coupling concerns** — Top 3 risks:
   `| Risk | Impact | Mitigation |`

---

## OUTPUT 2 — COMPONENT BREAKDOWN TABLE

One row per component inside the target container:

`| Component Name | Type | Technology/Pattern | Responsibility | Interfaces Exposed | Dependencies |`

**Component types to use:**
- Controller / Route Handler
- Service / Business Logic
- Repository / Data Access
- Event Listener / Consumer
- Event Publisher / Producer
- Scheduler / Job
- Validator / Guard
- Factory / Builder
- Gateway / Adapter (to external system)
- Shared / Cross-cutting (logging, auth, caching)

---

## OUTPUT 3 — MERMAID COMPONENT DIAGRAM

\```mermaid
---
title: [Container Name] — C4 Level 3 Component Diagram
---
graph TD

  %% ── People (Supporting — from Level 1) ───────────────
  User1["👤 Actor\n[Person]\nDescription"]

  %% ── Other Containers (Supporting — from Level 2) ──────
  OtherContainer["⬛ Other Container\n[Container]\nTechnology"]
  DB[("🗄️ Database\n[Relational DB]\nPostgreSQL")]

  %% ── External Systems (Supporting — from Level 1) ──────
  ExtSystem["📦 External System\n[Software System]\nDescription"]

  subgraph ContainerBoundary["🔲 [Target Container Name] — [Technology]"]

    %% ── Controllers / Entry Points ────────────────────
    Controller["[Component]\n[Controller]\nHandles incoming requests"]

    %% ── Services / Business Logic ─────────────────────
    Service["[Component]\n[Service]\nCore business logic"]

    %% ── Repositories / Data Access ────────────────────
    Repository["[Component]\n[Repository]\nData access and queries"]

    %% ── Gateways / Adapters ───────────────────────────
    Gateway["[Component]\n[Gateway]\nExternal system adapter"]

    %% ── Event Handling ────────────────────────────────
    EventPublisher["[Component]\n[Event Publisher]\nPublishes domain events"]
    EventListener["[Component]\n[Event Listener]\nConsumes domain events"]

    %% ── Cross-cutting ─────────────────────────────────
    AuthMiddleware["[Component]\n[Middleware]\nAuthentication and authorisation"]

  end

  %% ── Relationships ─────────────────────────────────────
  User1 -- "Sends requests [HTTPS]" --> Controller
  OtherContainer -- "Calls [JSON/HTTPS]" --> Controller
  Controller -- "Validates + delegates" --> AuthMiddleware
  AuthMiddleware -- "Passes to" --> Service
  Service -- "Reads/Writes via" --> Repository
  Service -- "Calls external via" --> Gateway
  Service -- "Emits events via" --> EventPublisher
  EventListener -- "Triggers" --> Service
  Repository -- "Queries [SQL]" --> DB
  Gateway -- "Calls [JSON/HTTPS]" --> ExtSystem

  %% ── Styles ────────────────────────────────────────────
  style ContainerBoundary fill:#f9f9f9,stroke:#999,stroke-dasharray:5 5

  style User1          fill:#2196F3,color:#fff,stroke:#1565C0
  style OtherContainer fill:#1B5E20,color:#fff,stroke:#1B5E20
  style DB             fill:#5C6BC0,color:#fff,stroke:#283593
  style ExtSystem      fill:#9E9E9E,color:#fff,stroke:#424242

  style Controller     fill:#4CAF50,color:#fff,stroke:#2E7D32
  style Service        fill:#4CAF50,color:#fff,stroke:#2E7D32
  style Repository     fill:#4CAF50,color:#fff,stroke:#2E7D32
  style Gateway        fill:#4CAF50,color:#fff,stroke:#2E7D32
  style EventPublisher fill:#FF9800,color:#fff,stroke:#E65100
  style EventListener  fill:#FF9800,color:#fff,stroke:#E65100
  style AuthMiddleware fill:#F44336,color:#fff,stroke:#B71C1C
\```

---

## OUTPUT 4 — TRACEABILITY MATRIX

`| Component | Functional Requirements | NFRs Addressed | Level 2 Container |`

## OUTPUT 5 — OPEN QUESTIONS & NEXT STEPS
- List 3–5 questions needing developer validation
- Flag any components complex enough to warrant a Level 4 Code diagram
- Recommend refactoring opportunities if coupling or responsibility issues found

---
