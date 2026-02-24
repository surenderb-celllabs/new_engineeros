**1. Architecture Style**
The solution is built as a *modular micro‑service architecture with an event‑driven backbone* and a dedicated *Backend‑for‑Frontend (BFF)* that exposes a single, mobile‑friendly API surface.

*Why this fits the requirements*

| Requirement | Why the style works |
|-------------|---------------------|
| **Offline, real‑time sync** | Each micro‑service owns its data and publishes events; the BFF streams changes to the mobile client via WebSockets, so the client can replay events after reconnecting. |
| **Real‑time notifications** | The Notification Service listens to events on the bus and pushes to a dedicated Push Service, keeping the notification flow decoupled from business logic. |
| **AI summarization & export jobs** | Background jobs run in separate services (AI Service, Export Service) and are triggered by events, enabling independent scaling and fault isolation. |
| **Audit, encryption, compliance** | The Audit Service is a separate bounded context that receives all change events, writes immutable logs to a tamper‑evident store, and enforces key‑rotation via the KMS integration. |
| **Performance & scalability** | Horizontal scaling of individual services (e.g., Media Service for uploads, Export Service for heavy PDF generation) lets the system meet 10 k concurrent trips, 1 M users, and 10 TB media without bottlenecks. |
| **Team ownership & change frequency** | Each bounded context can be owned by a dedicated team (Trip, Expense, Media, Permission, etc.), allowing rapid iteration on frequently changing features (trip editing, expense splitting) while keeping low‑change services (audit, key‑management) stable. |

**2. Container Boundary Rationale**
The boundaries were drawn to align with *separation of concerns, deployment cadence, and scalability drivers*.

| Boundary | Reasoning |
|----------|-----------|
| **TripSync Mobile App** | The sole consumer of the system; it needs offline storage, local persistence, and a lightweight UI. |
| **BFF (TripSync API Gateway)** | Aggregates calls to multiple services, handles authentication, rate‑limiting, and offers a single JSON contract to the mobile client. |
| **Trip Service** | Owns trip metadata, itinerary, and version history. High change frequency and the most heavily used service; must be highly available. |
| **Expense Service** | Handles expense CRUD, split calculations, and categorisation. Requires strong consistency for balances and auditability. |
| **Media Service** | Stores media metadata and streams uploads to Cloud Storage; isolated to allow aggressive caching and size limits. |
| **Permission Service** | Centralises role assignment, revocation, and real‑time push of permission changes. |
| **Notification Service** | Listens to events and pushes to the Push Service; can scale independently to meet 200 ms latency SLA. |
| **AI & Export Services** | Long‑running, compute‑intensive jobs triggered by scheduled events; isolated to avoid impacting core CRUD performance. |
| **Audit Service** | Immutable log store; decoupled to ensure that audit writes do not affect user‑facing latency. |
| **Auth Service** | External identity provider integration; separate to allow independent security hardening. |
| **KMS Integration** | A thin wrapper that forwards encryption/decryption requests to the external key‑management system. |

These boundaries also map neatly to *team ownership* (Trip & Expense, Media, Permission, Notification, AI, Export, Audit, Security) and to *deployability* – each container can be rolled out without affecting the others.

**3. Data Architecture Strategy**
The data strategy follows *bounded‑context ownership* with *eventual consistency* where appropriate.

- **Ownership** – Each micro‑service owns its domain data (trip DB, expense DB, media metadata DB, permission table, audit log). No shared tables across services, which eliminates cross‑service locks and simplifies scaling.
- **Isolation** – Domain data is stored in the most suitable store (relational for transactional trip/expense data, document for media metadata, object storage for the files).
- **Consistency** –
  - *Strong consistency* for critical paths: creating an expense triggers an immediate balance calculation within the Expense Service, ensuring the UI shows the correct split.
  - *Eventual consistency* for cross‑service reads: the mobile app can query the BFF, which aggregates the latest snapshot from Trip and Expense services; permission changes propagate via events.
- **Data Flow** –
  1. The BFF receives a CRUD request, forwards it to the target service via REST/GRPC.
  2. The target service updates its own store and publishes a domain event to the message bus.
  3. Dependent services (e.g., Notification, AI, Export) consume the event and perform their side‑effects.
  4. The BFF caches the latest state for the mobile client, which can replay events after an offline period.

**4. Communication Model**
The communication strategy is a mix of *synchronous REST/GRPC* for user‑initiated actions and *asynchronous event bus* for background processing, with a *BFF gateway* that hides complexity from the mobile client.

- **Synchronous**
  - Trip creation, expense logging, invite acceptance, permission changes.
  - These actions require an immediate response (e.g., trip ID, updated balances) and are protected by TLS 1.3 and JWT auth.
  - The BFF aggregates calls to reduce round‑trips; for example, creating a trip also creates a default itinerary in one request.

- **Asynchronous**
  - AI summarization, export generation, duplicate detection, push notifications, audit log persistence.
  - Events are published to a Kafka/Kinesis bus; services consume them independently, allowing bursty workloads to be handled without blocking the user.
  - The event payload includes a correlation ID, enabling the mobile client to correlate background updates with UI state.

- **Gateway/BFF**
  - The BFF acts as the sole entry point for the mobile app, handling authentication, rate limiting, and request aggregation.
  - It also serves WebSocket connections for real‑time updates (e.g., new expense, permission change).

**5. NFR Design Decisions**

| NFR | Architectural Decision |
|-----|------------------------|
| **Performance ≤2 s (95 %)** | BFF aggregates calls; critical services use in‑memory caching (Redis) for hot data; database indexes on trip_id, user_id. |
| **Scalability to 10 k trips / 1 M users** | Micro‑services are stateless; each can be autoscaled by cloud platform; media service uses object storage tiering. |
| **Offline sync & conflict resolution** | Client stores changes locally with version vectors; upon reconnection, the Sync Service merges changes and emits conflict events to the UI. |
| **Encryption at rest & in transit** | All data stores are encrypted (AES‑256) via KMS; all API traffic uses TLS 1.3; JWTs signed with RSA‑2048. |
| **Audit trail immutability** | Audit Service writes to an append‑only log store (e.g., Cloud Logging or immutable S3 bucket) and exposes a read‑only API. |
| **Real‑time push latency <200 ms** | Notification Service uses a dedicated Pub/Sub topic; Push Service (Firebase Cloud Messaging / APNs) is invoked directly; WebSocket updates use a low‑latency message broker. |
| **Compliance (GDPR, CCPA, PCI‑DSS)** | Data retention policies are enforced via scheduled clean‑up jobs; user data can be exported or deleted via BFF endpoints; audit logs are retained ≥1 yr. |
| **High availability 99.9 %** | All services run in at least two availability zones; message bus uses partitioning; BFF has a circuit‑breaker fallback. |
| **Unit‑test coverage ≥80 %** | Each service follows a test‑driven development cycle; CI/CD pipelines run coverage reports. |
| **Key‑rotation automation** | KMS integration service triggers rotation every 90 days; services fetch fresh keys on demand; no downtime. |

**6. Risks & Trade‑offs**

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Complexity of multi‑service orchestration** | Increased operational overhead, potential for data inconsistency. | Adopt a lightweight service mesh (e.g., Istio), use automated contract tests, and enforce a strict service‑to‑service API versioning policy. |
| **Conflict resolution in offline sync** | User may lose data or see stale balances. | Implement optimistic concurrency with version vectors, provide a clear conflict‑resolution UI, and log all conflicts for audit. |
| **Latency of push notifications** | Users may miss real‑time updates, affecting trust. | Use a dedicated low‑latency Pub/Sub topic, cache notification payloads, and monitor latency metrics with alerts. |

This narrative captures the key architectural decisions that map the functional and non‑functional requirements to a robust, scalable, and secure containerized system.