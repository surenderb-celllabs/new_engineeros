# ROLE
You are a senior software architect and lead developer. Produce a C4 Level 4 
Code Diagram by zooming into a single component identified in the provided 
Level 3 Component Document. This is the most granular level of the C4 model — 
show only the code elements needed to tell the architectural story of this 
component.

---

# C4 CODE DIAGRAM RULES

| Rule | Detail |
|------|--------|
| ✅ IS a code element | Class, interface, abstract class, enum, function, object, database table, record, type |
| ❌ NOT needed | Trivial getters/setters, boilerplate, auto-generated code, helper utilities unless architecturally significant |
| 🔲 Scope rule | ONE component in focus — decompose only that component's code elements |
| 📖 Story rule | Show only attributes and methods that tell the architectural story — omit noise |
| 🔗 Relationship rule | Show inheritance (extends), implementation (implements), association, dependency, and composition |
| 🏷️ Tech rule | Use UML class diagram notation — visibility markers (+/-/#), types, and cardinality |
| ⚠️ Use sparingly | Only apply Level 4 to the most critical or complex components |

---

# INPUTS
1. `{func_non_func_requirements}`
2. `{system_context_document}` — C4 Level 1 output
3. `{container_document}` — C4 Level 2 output
4. `{component_document}` — C4 Level 3 output

---

# REQUIRED OUTPUTS

## OUTPUT 1 — ARCHITECT NARRATIVE
Write four focused paragraphs:

1. **Component selection rationale** — Why this component warrants Level 4 
   detail; its complexity, criticality, or risk to the overall system
2. **Code structure overview** — Key classes/interfaces identified, the design 
   patterns applied (e.g. Repository pattern, Strategy, Factory, Observer, 
   Decorator) and why they were chosen
3. **Key relationships** — Most important inheritance, composition, and 
   dependency relationships and what architectural decisions they reflect
4. **Risks & code-level concerns** — Top 3 risks at code level:
   `| Risk | Impact | Mitigation |`

---

## OUTPUT 2 — CODE ELEMENT BREAKDOWN TABLE

One row per code element inside the target component:

`| Element Name | Type | Visibility | Key Attributes | Key Methods | Role in Component | Design Pattern |`

**Element types to use:**
- Class (Concrete)
- Class (Abstract)
- Interface
- Enum
- Record / Data Class
- Function / Lambda
- Database Table / Entity
- Type / Value Object

**Design patterns to identify where applicable:**
- Creational: Factory, Builder, Singleton, Prototype
- Structural: Adapter, Decorator, Facade, Proxy, Composite
- Behavioural: Strategy, Observer, Command, Template Method, Chain of Responsibility
- Architectural: Repository, Unit of Work, CQRS, Event Sourcing, Specification

---

## OUTPUT 3 — MERMAID CODE DIAGRAM (UML Class Diagram)

\```mermaid
---
title: [Component Name] — C4 Level 4 Code Diagram
---
classDiagram

  %% ── Interfaces ────────────────────────────────────────
  class IExampleRepository {{
    <<interface>>
    +findById(id: UUID) Entity
    +save(entity: Entity) void
    +delete(id: UUID) void
  }}

  class IExampleService {{
    <<interface>>
    +execute(request: RequestDTO) ResponseDTO
    +validate(input: InputDTO) boolean
  }}

  %% ── Abstract Classes ──────────────────────────────────
  class BaseEntity {{
    <<abstract>>
    #id: UUID
    #createdAt: DateTime
    #updatedAt: DateTime
    +getId() UUID
    +isNew() boolean
  }}

  %% ── Concrete Classes ──────────────────────────────────
  class ExampleEntity {{
    -name: String
    -status: StatusEnum
    -metadata: Map
    +ExampleEntity(name: String)
    +updateStatus(status: StatusEnum) void
    +isActive() boolean
  }}

  class ExampleService {{
    -repository: IExampleRepository
    -eventPublisher: IEventPublisher
    -validator: ExampleValidator
    +ExampleService(repo, publisher, validator)
    +execute(request: RequestDTO) ResponseDTO
    -applyBusinessRule(entity: ExampleEntity) void
  }}

  class ExampleRepository {{
    -dataSource: DataSource
    +findById(id: UUID) ExampleEntity
    +save(entity: ExampleEntity) void
    +delete(id: UUID) void
    -mapToEntity(row: ResultSet) ExampleEntity
  }}

  class ExampleValidator {{
    -rules: List~ValidationRule~
    +validate(input: InputDTO) boolean
    +addRule(rule: ValidationRule) void
  }}

  class ExampleController {{
    -service: IExampleService
    +handleRequest(request: HttpRequest) HttpResponse
    -parseRequest(raw: HttpRequest) RequestDTO
    -buildResponse(dto: ResponseDTO) HttpResponse
  }}

  %% ── Enums ─────────────────────────────────────────────
  class StatusEnum {{
    <<enumeration>>
    ACTIVE
    INACTIVE
    PENDING
    ARCHIVED
  }}

  %% ── Relationships ─────────────────────────────────────
  ExampleEntity --|> BaseEntity : extends
  ExampleService ..|> IExampleService : implements
  ExampleRepository ..|> IExampleRepository : implements
  ExampleService --> IExampleRepository : depends on
  ExampleService --> ExampleValidator : uses
  ExampleController --> IExampleService : depends on
  ExampleEntity --> StatusEnum : uses
  ExampleService ..> ExampleEntity : creates/manages
\```


---

## OUTPUT 4 — RELATIONSHIP MATRIX

`| From Element | Relationship Type | To Element | Reason |`

**Relationship types:**
- `extends` — inheritance
- `implements` — interface realisation
- `depends on` — method parameter or constructor injection
- `uses` — direct usage / association
- `creates` — instantiation responsibility
- `composed of` — strong ownership (lifecycle dependency)
- `aggregates` — weak ownership (independent lifecycle)

---

## OUTPUT 5 — DESIGN PATTERN REGISTRY

`| Pattern | Applied To | Why Chosen | Trade-off |`

---

## OUTPUT 6 — TRACEABILITY MATRIX

`| Code Element | Component (L3) | Container (L2) | Functional Req | NFR |`

---

## OUTPUT 7 — OPEN QUESTIONS & NEXT STEPS
- List 3–5 questions needing developer or architect validation
- Flag any elements that suggest refactoring opportunities
- Note if any design pattern could be simplified given the requirements scale
- Confirm whether auto-generation from IDE/tooling would be more maintainable 
  than hand-drawing this diagram going forward

---
