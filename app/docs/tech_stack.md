# TripSync — Technical Architecture & Decision Document

## Executive Summary
TripSync is a mobile‑first travel companion that unifies itinerary planning, expense tracking, media capture, and real‑time collaboration. The discovery session confirmed a **micro‑service, event‑driven architecture** on AWS that satisfies all functional and non‑functional requirements, including stringent security, compliance, offline sync, and AI‑driven summarisation. The chosen stack delivers **≤2 s CRUD latency (95 % of requests)**, **99.9 % availability**, and **≤200 ms push‑notification latency** while scaling to 10 k concurrent trips, 1 M active users, and 10 TB of media.

---

## Technical Stack

### Confirmed Decisions
| Layer | Technology | Justification |
|-------|------------|---------------|
| **Mobile Front‑end** | React‑Native + Realm | Cross‑platform UI + local persistence for offline sync |
| **API Gateway (BFF)** | Node.js / TypeScript (REST/GraphQL) | Aggregates micro‑services, handles auth, rate‑limiting, WebSocket for real‑time |
| **Core Services** | Go micro‑services (Trip, Expense, Media, Permission, Audit, AI, Export) | High throughput, minimal runtime, stateless, easy autoscaling |
| **Relational DB** | Amazon RDS PostgreSQL | ACID guarantees for trip/expense/permission/user data |
| **Document DB** | MongoDB (Atlas) | Flexible media metadata schema |
| **Object Store** | Amazon S3 + CloudFront | Durable media storage, lifecycle tiering, CDN for export links |
| **Message Bus** | Amazon EventBridge | Serverless pub/sub for event‑driven workflows |
| **Cache** | Amazon ElastiCache Redis | Hot data (trip lists, user metadata) & token blacklist |
| **CI/CD** | GitHub Actions → Docker → Amazon ECR → Helm/Argo CD | Automated build, test, and deploy pipeline |
| **Observability** | OpenTelemetry → Prometheus + Grafana + CloudWatch Logs/X‑Ray | Metrics, traces, logs, alerting |
| **Container Orchestration** | Amazon EKS (Kubernetes) | Managed cluster, autoscaling, service mesh (Istio) |

### Alternatives Considered
| Layer | Alternative | Reason for Rejection |
|-------|-------------|----------------------|
| Front‑end | Native Swift/Kotlin | Slower cross‑platform delivery |
| Backend | Java/Spring | Larger footprint, slower startup |
| DB | MySQL, DynamoDB | MySQL lacks advanced indexing; DynamoDB not ideal for relational joins |
| Cache | Memcached | Less feature‑rich than Redis (e.g., pub/sub) |
| Orchestration | ECS/Fargate | Limited service mesh integration, less granular autoscaling |

### Open Items / TBD
- **AI summarisation provider** – Bedrock (OpenAI GPT‑4) chosen; optional OpenAI API fallback for cost optimization.
- **Auth provider** – Cognito selected; potential switch to Auth0 if advanced federation needed.

---

## Security Architecture

### Authentication & Authorization
- **JWT (RSA‑2048, 24 h expiry)** for API calls; short‑lived session tokens, long‑lived invite tokens (24 h).
- **OAuth2/OIDC** via Amazon Cognito for user sign‑in, MFA, and “forgotten password” flows.
- **Permission Service** enforces RBAC: *owner*, *edit*, *view‑only*. View‑only users receive 403 on write attempts.

### Data Protection
- **Encryption at rest**: AES‑256 via AWS KMS. Each table/column that stores PII is encrypted; KMS keys are rotated quarterly.
- **Encryption in transit**: TLS 1.3 enforced on all public and internal endpoints.
- **Audit Trail**: Immutable append‑only logs stored in S3 with server‑side encryption and versioning; access restricted to Admin role.

### Compliance & Regulatory Requirements
| Framework | Implementation |
|-----------|----------------|
| GDPR / CCPA | Right‑to‑be‑forgotten via self‑service deletion endpoint; data subject export via BFF; retention policy (30 days for session data, 5 years for user data). |
| PCI‑DSS | Encryption of all card‑related fields; no card data stored in plaintext; audit logs meet 1‑year retention. |
| ISO 27001 | Security controls mapped to Annex A; regular penetration testing; key‑management audit. |
| SOC 2 | Controls for availability, confidentiality, processing integrity documented. |

### Access Control
- **RBAC**: Trip owner → full CRUD; edit buddies → CRUD on trip components; view‑only buddies → read‑only.
- **ABAC**: Fine‑grained attributes (trip_id, user_id, action) enforced by Permission Service.
- **Admin**: Full read/write, audit log access, key‑rotation trigger.

### Open Items / TBD
- **Key‑rotation policy**: Automate via EventBridge every 90 days; manual override via Admin console.

---

## Infrastructure & Deployment

### Cloud Provider & Region
- **AWS (us‑east‑1)** selected for mature managed services (EKS, RDS, S3, KMS, EventBridge) and compliance certifications.

### Containerization & Orchestration
- **Docker** images built per service, pushed to Amazon ECR.
- **EKS** cluster with separate namespaces: *dev*, *staging*, *prod*.
- **Helm charts** for each micro‑service; versioned with Git tags.
- **Service Mesh**: Istio for mTLS, traffic shaping, and observability.

### CI/CD Pipeline
| Stage | Tool | Description |
|-------|------|-------------|
| **Source** | GitHub | Code repo with protected branches |
| **Build** | GitHub Actions | Unit tests, lint, Docker build |
| **Test** | Docker + Kubernetes | Integration tests against a test EKS cluster |
| **Deploy** | Argo CD | GitOps; sync Helm charts to target namespace |
| **Smoke** | Custom scripts | Verify endpoints, health checks |
| **Canary** | Argo Rollouts | Gradual traffic shift, rollback on failure |
| **Release** | Manual approval | Promote to production |

### Environment Strategy
- **Dev**: Unlimited resources, mock external services.
- **Staging**: Full stack, real AWS services, data‑masking.
- **Prod**: Autoscaling, read‑replicas, S3 lifecycle, CloudFront caching.
- **Promotion**: Git tags → Helm chart bump → Argo CD sync → canary → full rollout.

### Open Items / TBD
- **Blue/Green** vs **Canary**: Current plan uses canary; blue/green considered for future releases.

---

## Stability & Performance

### SLA Targets

| Metric | Target | Description |
|--------|--------|-------------|
| **Uptime** | 99.9 % | Excluding 2 h scheduled maintenance |
| **CRUD Response Time** | ≤2 s (95 %), ≤5 s (99 %) | Measured under peak load |
| **Push Notification Latency** | ≤200 ms | End‑to‑end from event to device |
| **AI Summary Generation** | ≤30 s | From payload creation to persistence |
| **Export Generation** | ≤2 min | For trips up to 30 days |
| **Sync Completion** | ≤5 min | After reconnection |
| **Duplicate Detection** | ≤10 s | On entry creation |

### Caching Strategy
- **Redis (ElastiCache)**: Hot trip lists, user metadata, token blacklist.
- **S3/CloudFront**: Public export links cached for 7 days.
- **In‑app Local Cache**: Realm persists data offline; sync queue.

### Load Handling
- **Autoscaling**: HPA on CPU/memory thresholds; cluster autoscaler for node scaling.
- **Read‑replicas**: PostgreSQL read replicas for trip/expense queries.
- **Load Balancer**: AWS ALB with path‑based routing to BFF.
- **EventBridge**: Scales automatically for event throughput.

### Monitoring & Alerting
- **Prometheus + Grafana**: Metrics for latency, error rate, queue depth.
- **OpenTelemetry**: Distributed tracing across services.
- **CloudWatch**: Logs, metrics, and X‑Ray traces.
- **PagerDuty**: Alert routing for SLA breaches (latency, error rate).
- **Dashboards**: Real‑time view of API latency, push success rate, AI job status.

### Open Items / TBD
- **Cold‑start latency** for Go services: target <200 ms; monitor via CloudWatch.

---

## Third‑Party Integrations

### Confirmed Integrations

| Integration | Purpose | API/SDK | Auth Method | Risk Level |
|-------------|---------|---------|-------------|------------|
| **Amazon Bedrock / OpenAI** | AI summarisation | REST | IAM role | Medium |
| **Amazon SNS** | Push notifications | AWS SDK | IAM | Low |
| **Amazon SES** | Email alerts | AWS SDK | IAM | Low |
| **Amazon S3 / CloudFront** | Media & export storage | S3 SDK | IAM | Low |
| **Amazon Cognito** | User auth, MFA, GDPR flows | Cognito SDK | OIDC | Medium |
| **AWS KMS** | Key‑management, rotation | KMS SDK | IAM | Low |
| **EventBridge** | Event bus between services | EventBridge SDK | IAM | Low |
| **CloudWatch / X‑Ray** | Observability | CloudWatch SDK | IAM | Low |

### Integration Risks & Mitigations
| Integration | Risk | Mitigation |
|-------------|------|------------|
| Bedrock/OpenAI | Vendor lock‑in, cost spikes | Use API‑gateway rate‑limit; fallback to local summariser if needed |
| SNS | Message delivery failure | Retry policy, dead‑letter queue |
| Cognito | Identity federation complexity | Thorough testing of OIDC flow, MFA enforcement |
| KMS | Key access breach | Strict IAM policies, audit logging, quarterly rotation |
| EventBridge | Event loss | CloudWatch metrics, retry on failure |

### Open Items / TBD
- **Alternative AI**: Evaluate Anthropic Claude via Bedrock for cost/latency trade‑off.
- **Email Service**: Consider SendGrid if SES limits are reached.

---

## Appendix

### A. Raw Architecture Notes
- **Event‑driven flow**: CRUD actions emit domain events (e.g., `ExpenseCreated`, `TripUpdated`) that are consumed by Notification, AI, Export, and Audit services.
- **Offline sync**: Client records changes with a **vector clock**; on reconnection, Sync Service merges changes, resolves conflicts via version vectors, and emits conflict events if manual resolution required.
- **Duplicate detection**: Service runs a 10‑second window scan; if criteria match, it emits `DuplicateCandidate` event for UI prompt.
- **Timestamp handling**: All timestamps stored in UTC; UI converts to itinerary location’s time zone using `moment-timezone`.
- **Media corruption**: On upload, a SHA‑256 checksum is verified; corrupted files are flagged and an error dialog is shown.

### B. Glossary
| Term | Definition |
|------|------------|
| **BFF** | Backend‑for‑Frontend; API gateway tailored to mobile client. |
| **JWT** | JSON Web Token; used for stateless auth. |
| **KMS** | Key Management Service; stores encryption keys. |
| **S3** | Amazon Simple Storage Service; object storage. |
| **EventBridge** | Serverless event bus for micro‑service communication. |
| **Istio** | Service mesh providing mTLS, traffic management, and observability. |
| **Audit Trail** | Immutable log of all data changes, key events, and security actions. |
| **Vector Clock** | Logical clock for conflict detection in offline sync. |
| **Push Notification** | Real‑time alert sent via Firebase/APNs through SNS. |
| **CDN** | Content Delivery Network; used via CloudFront for export links. |
| **IAM** | Identity and Access Management; controls AWS resource permissions. |

> **Critical Decision:** The entire architecture is **micro‑service + event‑driven**; this design is essential for meeting the 200 ms push‑latency, 30 s AI summarisation, and 2 min export NFRs while providing isolation for future feature extensions.