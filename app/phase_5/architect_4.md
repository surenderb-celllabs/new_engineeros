## OUTPUT 1 – ARCHITECT NARRATIVE

### 1. Component selection rationale
The **Appointment Service** is the single point that turns a user‑initiated “book / reschedule / cancel” request into a durable state change. It must coordinate three external systems (Scheduling API, EHR, Billing), enforce a large set of business rules (no‑show window, reschedule window, crowd limits), and publish audit events that are required for HIPAA compliance. Because the component is the “core of the value chain” and its failure would render the portal unusable, it is the only candidate that justifies a Level 4 view.

### 2. Code structure overview
| Element | Type | Design Pattern | Reason |
|--------|------|----------------|--------|
| **BookingController** | Concrete Class | *Facade* (simplifies REST API) | Keeps the REST layer thin and delegates to the service. |
| **BookingService** | Concrete Class | *Service* + *Unit‑of‑Work* | Orchestrates the whole flow, manages transactions, and publishes events. |
| **AppointmentAggregate** | Concrete Class | *Aggregate* (DDD) | Encapsulates invariants (no double‑booking, time‑zone conversion) and exposes business behaviour. |
| **ConflictChecker** | Concrete Class | *Strategy* (policy per provider) | Allows different conflict‑check algorithms without changing the service. |
| **RuleEngine** | Concrete Class | *Specification* | Evaluates admin‑defined rules (crowd limits, session length) in a declarative way. |
| **AppointmentRepository** | Concrete Class | *Repository* | Provides persistence abstraction over JPA/Hibernate. |
| **EventPublisher** | Concrete Class | *Publisher* (Observer) | Publishes domain events to Kafka before the transaction commits. |
| **EventListener** | Concrete Class | *Observer* | Consumes events to update read‑model & trigger notifications. |
| **SchedulingGateway** | Concrete Class | *Adapter* | Wraps the external Scheduling API behind a stable interface. |
| **EHRGateway** | Concrete Class | *Adapter* | Same as above for the EHR. |
| **BillingGateway** | Concrete Class | *Adapter* | Same as above for Billing. |
| **NotificationGateway** | Concrete Class | *Adapter* | Same as above for the Notification service. |
| **Validator** | Concrete Class | *Decorator* (Bean‑Validation) | Adds domain‑specific validation on top of JSR‑380. |
| **Cache** | Concrete Class | *Singleton* (Redis client) | Provides a shared cache for slot lists and rate‑limit counters. |

All of these classes are wired via Spring’s dependency injection, ensuring that the Appointment Service remains a pure business component while the infrastructure is injected.

### 3. Key relationships
| From | Relationship | To | Architectural implication |
|------|--------------|----|---------------------------|
| **BookingService → AppointmentAggregate** | composition | – | The service owns the aggregate and performs state changes. |
| **BookingService → ConflictChecker** | dependency | – | The service delegates conflict logic, enabling strategy switching. |
| **BookingService → RuleEngine** | dependency | – | Business rules are applied before persistence. |
| **BookingService → AppointmentRepository** | dependency | – | Persistence is abstracted, allowing unit tests to use an in‑memory repository. |
| **BookingService → EventPublisher** | dependency | – | Events are published *after* the aggregate is mutated, guaranteeing audit order. |
| **EventPublisher → Kafka** | integration | – | Decouples the service from the messaging platform. |
| **EventListener → AppointmentReadModel** | dependency | – | Keeps the read side in sync via event sourcing. |
| **EventListener → NotificationGateway** | dependency | – | Side‑effects (reminders, cancellation emails) are triggered asynchronously. |
| **SchedulingGateway / EHRGateway / BillingGateway / NotificationGateway → External APIs** | integration | – | These adapters hide the protocol details and allow retry/back‑off logic to be centralised. |
| **Validator → BookingService** | decorator | – | Validation is applied before business logic executes. |
| **Cache → BookingService / ConflictChecker** | dependency | – | Shared cache reduces round‑trips to external services. |

These relationships illustrate a clean separation of concerns: orchestration, domain logic, persistence, side‑effects, and external integration.

### 4. Risks & code‑level concerns

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Event ordering** – audit event may be published after the external EHR update, breaking the “audit before state change” guarantee. | Compliance violations, audit trail gaps. | Use a transactional outbox: write the audit event into the same transaction as the aggregate; publish after commit. |
| **External API flakiness** – Scheduling API or EHR may time‑out, causing booking failures or stale slot data. | Poor user experience, double‑booking. | Implement retry with exponential back‑off and circuit‑breaker; cache slot lists for a short TTL. |
| **Cache staleness** – Redis cache may return outdated slot lists during high‑concurrency booking. | Race conditions, overbooking. | Use optimistic locking on the aggregate; fallback to direct API call when cache is stale. |

---

## OUTPUT 2 – CODE ELEMENT BREAKDOWN TABLE

| Element Name | Type | Visibility | Key Attributes | Key Methods | Role in Component | Design Pattern |
|--------------|------|------------|----------------|-------------|-------------------|----------------|
| `BookingController` | Class (Concrete) | `public` | `BookingService bookingService` | `book(request)`, `reschedule(request)`, `cancel(id)` | Exposes REST endpoints | Facade |
| `BookingService` | Class (Concrete) | `public` | `AppointmentRepository repo`, `ConflictChecker checker`, `RuleEngine rules`, `EventPublisher publisher`, `Validator validator` | `execute(request)`, `applyBusinessRules(agg)`, `persist(agg)` | Orchestrates booking flow | Service / Unit‑of‑Work |
| `AppointmentAggregate` | Class (Concrete) | `public` | `UUID id`, `LocalDateTime start`, `LocalDateTime end`, `Status status`, `Patient patient` | `create(start, end, patient)`, `reschedule(newStart, newEnd)`, `cancel(reason)` | Domain entity | Aggregate |
| `ConflictChecker` | Class (Concrete) | `public` | `SchedulingGateway scheduler`, `EHRGateway ehr` | `checkConflict(start, end)` | Determines slot availability | Strategy |
| `RuleEngine` | Class (Concrete) | `public` | `List<Specification<AppointmentAggregate>> specs` | `apply(agg)` | Enforces admin rules | Specification |
| `AppointmentRepository` | Class (Concrete) | `public` | `EntityManager em` | `findById(id)`, `save(agg)`, `delete(id)` | Persistence abstraction | Repository |
| `EventPublisher` | Class (Concrete) | `public` | `KafkaTemplate<String, Event> template` | `publish(event)` | Publishes domain events | Publisher |
| `EventListener` | Class (Concrete) | `public` | `AppointmentReadModel repo`, `NotificationGateway notifier` | `onAppointmentBooked(event)`, `onAppointmentCancelled(event)` | Updates read‑model & triggers side‑effects | Observer |
| `SchedulingGateway` | Class (Concrete) | `public` | `RestTemplate rest` | `getAvailableSlots(provider, date)` | Calls external Scheduling API | Adapter |
| `EHRGateway` | Class (Concrete) | `public` | `RestTemplate rest` | `syncAppointment(agg)` | Calls external EHR | Adapter |
| `BillingGateway` | Class (Concrete) | `public` | `RestTemplate rest` | `notifyAppointment(agg)` | Calls external Billing | Adapter |
| `NotificationGateway` | Class (Concrete) | `public` | `RestTemplate rest` | `sendReminder(event)` | Calls external Notification service | Adapter |
| `Validator` | Class (Concrete) | `public` | `List<ValidationRule> rules` | `validate(request)` | Validates incoming DTOs | Decorator |
| `Cache` | Class (Singleton) | `public` | `RedisTemplate redis` | `get(key)`, `set(key, value)` | Shared cache for slots & rate‑limits | Singleton |

---


## OUTPUT 3 – REQUIRED OUTPUTS
---
title: Appointment Service — C4 Level 4 Code Diagram
---
classDiagram

  %% ── Interfaces ───────────────────────────────────────
  class IAppointmentRepository {
    <<interface>>
    +findById(id: UUID) : Appointment
    +save(appointment: Appointment) : void
    +delete(id: UUID) : void
  }

  class IEventPublisher {
    <<interface>>
    +publish(event: DomainEvent) : void
  }

  class IEventListener {
    <<interface>>
    +on(event: DomainEvent) : void
  }

  class ISchedulingGateway {
    <<interface>>
    +getAvailableSlots(providerId: UUID, date: LocalDate) : List~Slot~
    +reserveSlot(slot: Slot) : void
  }

  class IEHRGateway {
    <<interface>>
    +syncAppointment(appointment: Appointment) : void
  }

  class IBillingGateway {
    <<interface>>
    +notifyAppointment(appointment: Appointment) : void
  }

  class INotificationGateway {
    <<interface>>
    +sendReminder(event: ReminderEvent) : void
  }

  class IValidator {
    <<interface>>
    +validate(input: BookingRequest) : ValidationResult
  }

  %% ── Abstract Classes ──────────────────────────────────
  class BaseEntity {
    <<abstract>>
    #id: UUID
    #createdAt: DateTime
    #updatedAt: DateTime
    +getId() : UUID
    +isNew() : boolean
  }

  class BaseRepository {
    <<abstract>>
    -dataSource: DataSource
    +find(id: UUID) : BaseEntity
    +save(entity: BaseEntity) : void
    +delete(id: UUID) : void
  }

  %% ── Concrete Domain Classes ───────────────────────────
  class Appointment {
    -patientId: UUID
    -providerId: UUID
    -startTime: LocalDateTime
    -endTime: LocalDateTime
    -status: AppointmentStatus
    -metadata: Map~String,String~
    +Appointment(patientId: UUID, providerId: UUID, start: LocalDateTime, end: LocalDateTime)
    +updateStatus(status: AppointmentStatus) : void
    +isActive() : boolean
  }

  class AppointmentReadModel {
    -id: UUID
    -patientId: UUID
    -providerId: UUID
    -startTime: LocalDateTime
    -endTime: LocalDateTime
    -status: AppointmentStatus
    +fromDomain(appointment: Appointment) : AppointmentReadModel
  }

  class AppointmentBookedEvent {
    -appointmentId: UUID
    -patientId: UUID
    -providerId: UUID
    -startTime: LocalDateTime
    -endTime: LocalDateTime
    +AppointmentBookedEvent(appointment: Appointment)
  }

  class AppointmentRescheduledEvent {
    -appointmentId: UUID
    -oldStart: LocalDateTime
    -newStart: LocalDateTime
    +AppointmentRescheduledEvent(appointment: Appointment, old: LocalDateTime, new: LocalDateTime)
  }

  class AppointmentCancelledEvent {
    -appointmentId: UUID
    -cancellationReason: String
    +AppointmentCancelledEvent(appointment: Appointment, reason: String)
  }

  class ReminderEvent {
    -appointmentId: UUID
    -patientContact: ContactInfo
    -messageTemplate: String
    +ReminderEvent(appointment: Appointment, contact: ContactInfo)
  }

  %% ── Concrete Service Classes ──────────────────────────
  class AppointmentService {
    -repo: IAppointmentRepository
    -publisher: IEventPublisher
    -validator: IValidator
    -conflictChecker: ConflictChecker
    -ruleEngine: RuleEngine
    -schedulingGateway: ISchedulingGateway
    -ehrGateway: IEHRGateway
    -billingGateway: IBillingGateway
    -notificationGateway: INotificationGateway
    +bookAppointment(request: BookingRequest) : Appointment
    +rescheduleAppointment(id: UUID, request: RescheduleRequest) : Appointment
    +cancelAppointment(id: UUID, reason: String) : void
  }

  class ConflictChecker {
    -schedulingGateway: ISchedulingGateway
    -ehrGateway: IEHRGateway
    +checkConflict(providerId: UUID, start: LocalDateTime, end: LocalDateTime) : ConflictResult
  }

  class RuleEngine {
    -config: RuleConfig
    +evaluate(appointment: Appointment) : boolean
  }

  class AppointmentRepositoryImpl {
    -dataSource: DataSource
    +findById(id: UUID) : Appointment
    +save(appointment: Appointment) : void
    +delete(id: UUID) : void
  }

  class EventPublisher {
    -kafkaTemplate: KafkaTemplate
    +publish(event: DomainEvent) : void
  }

  class EventListener {
    -readModelRepo: AppointmentReadModelRepository
    -notificationGateway: INotificationGateway
    +on(event: DomainEvent) : void
  }

  class SchedulingGateway {
    -httpClient: HttpClient
    +getAvailableSlots(providerId: UUID, date: LocalDate) : List~Slot~
    +reserveSlot(slot: Slot) : void
  }

  class EHRGateway {
    -httpClient: HttpClient
    +syncAppointment(appointment: Appointment) : void
  }

  class BillingGateway {
    -httpClient: HttpClient
    +notifyAppointment(appointment: Appointment) : void
  }

  class NotificationGateway {
    -httpClient: HttpClient
    +sendReminder(event: ReminderEvent) : void
  }

  class AppointmentValidator {
    -rules: List~ValidationRule~
    +validate(input: BookingRequest) : ValidationResult
  }

  class Cache {
    -redisTemplate: RedisTemplate
    +get(key: String) : Object
    +put(key: String, value: Object, ttl: Duration) : void
  }

  %% ── Enums ─────────────────────────────────────────────
  class AppointmentStatus {
    <<enumeration>>
    SCHEDULED
    CONFIRMED
    COMPLETED
    CANCELLED
    NO_SHOW
  }

  class ConflictResult {
    <<enumeration>>
    PASS
    FAIL
  }

  %% ── Relationships ─────────────────────────────────────
  Appointment --|> BaseEntity : extends
  AppointmentRepositoryImpl ..|> IAppointmentRepository : implements
  AppointmentService --> IAppointmentRepository : depends on
  AppointmentService --> IEventPublisher : depends on
  AppointmentService --> IValidator : depends on
  AppointmentService --> ConflictChecker : composes
  AppointmentService --> RuleEngine : composes
  AppointmentService --> ISchedulingGateway : depends on
  AppointmentService --> IEHRGateway : depends on
  AppointmentService --> IBillingGateway : depends on
  AppointmentService --> INotificationGateway : depends on
  ConflictChecker --> ISchedulingGateway : uses
  ConflictChecker --> IEHRGateway : uses
  EventPublisher ..|> IEventPublisher : implements
  EventListener ..|> IEventListener : implements
  EventListener --> AppointmentReadModelRepository : updates
  EventListener --> INotificationGateway : triggers
  SchedulingGateway ..|> ISchedulingGateway : implements
  EHRGateway ..|> IEHRGateway : implements
  BillingGateway ..|> IBillingGateway : implements
  NotificationGateway ..|> INotificationGateway : implements
  AppointmentValidator ..|> IValidator : implements
  AppointmentService --> Cache : uses
  AppointmentReadModel --> Appointment : aggregates




---

## OUTPUT 4 – RELATIONSHIP MATRIX

| From Element | Relationship Type | To Element | Reason |
|--------------|-------------------|------------|--------|
| `BookingService` | depends on | `AppointmentAggregate` | Creates and mutates the aggregate. |
| `BookingService` | depends on | `ConflictChecker` | Delegates conflict‑checking. |
| `BookingService` | depends on | `RuleEngine` | Applies admin rules. |
| `BookingService` | depends on | `IAppointmentRepository` | Persists aggregate. |
| `BookingService` | depends on | `IEventPublisher` | Publishes domain events. |
| `BookingService` | depends on | `Validator` | Validates incoming requests. |
| `ConflictChecker` | depends on | `SchedulingGateway` | Calls external slot API. |
| `ConflictChecker` | depends on | `EHRGateway` | Calls external EHR for live status. |
| `EventPublisher` | implements | `IEventPublisher` | Provides Kafka publishing. |
| `EventListener` | implements | `IEventListener` | Consumes events. |
| `EventListener` | depends on | `AppointmentReadModel` | Updates read‑model. |
| `EventListener` | depends on | `NotificationGateway` | Triggers side‑effects. |
| `AppointmentRepository` | implements | `IAppointmentRepository` | JPA persistence. |
| `Validator` | uses | `ValidationRule` | Encapsulates individual validation checks. |
| `Cache` | uses | `RedisTemplate` | Provides shared caching. |
| `BookingController` | depends on | `BookingService` | REST layer. |
| `AppointmentAggregate` | extends | `BaseEntity` | Reuses common fields. |

---

## OUTPUT 5 – DESIGN PATTERN REGISTRY

| Pattern | Applied To | Why Chosen | Trade‑off |
|---------|------------|------------|-----------|
| **Facade** | `BookingController` | Simplifies REST API; hides orchestration logic | Adds a thin wrapper that may become a bottleneck if overused. |
| **Service** + **Unit‑of‑Work** | `BookingService` | Centralises transaction boundaries; keeps business logic pure | Requires careful transaction management to avoid long‑running transactions. |
| **Aggregate** | `AppointmentAggregate` | Encapsulates invariants and ensures consistency | Increases object size; needs careful domain modelling. |
| **Strategy** | `ConflictChecker` | Allows swapping of conflict‑check algorithms (e.g., in‑memory vs external) | Adds an interface layer that can be overkill if only one algorithm is used. |
| **Specification** | `RuleEngine` | Declaratively applies admin rules | Requires a rule engine or DSL; may add complexity for simple rules. |
| **Repository** | `AppointmentRepository` | Decouples persistence from domain | Adds boilerplate; may hide performance nuances. |
| **Publisher / Observer** | `EventPublisher` / `EventListener` | Decouples side‑effects from core flow | Requires eventual consistency; introduces latency. |
| **Adapter** | All *Gateway* classes | Wraps external APIs behind stable interfaces | Adds indirection; extra maintenance for adapters. |
| **Decorator** | `Validator` | Adds validation without modifying service | Increases call depth; may obscure flow. |
| **Singleton** | `Cache` | Provides shared Redis client | Global state can hinder testability. |

---