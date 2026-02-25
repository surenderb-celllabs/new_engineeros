# TripSync — Technical Architecture & Decision Document

---

## Executive Summary
TripSync is a mobile‑first application that consolidates itinerary planning, expense tracking, media capture, and AI‑driven daily summaries into a single, unified workflow. The discovery session clarified that the core pain points for travelers are context switching and fragmented data. The architecture is designed to eliminate these friction points while meeting stringent performance, scalability, and compliance requirements.

**Key Outcomes of the Discovery Session**

| Outcome | Description |
|---------|-------------|
| **Unified Data Model** | Trip, expense, media, and itinerary data are stored in a single, well‑defined schema that supports versioning, audit trails, and conflict resolution. |
| **Real‑time Collaboration** | View‑only and edit permissions are enforced at the API level and propagated instantly via WebSocket events. |
| **Offline First** | All CRUD operations are persisted locally with a version vector; sync occurs automatically on reconnection. |
| **AI Summaries** | A scheduled job aggregates daily activity and calls an external LLM to produce concise summaries, delivered via push/email. |
| **Export & Sharing** | Trips can be exported as PDF/ZIP bundles with custom branding and secure shareable links. |
| **Compliance‑Ready** | AES‑256 encryption at rest, TLS 1.3 in transit, envelope encryption via KMS, immutable audit logs, GDPR/CCPA data‑subject rights. |
| **Scalable & Resilient** | Micro‑service architecture on AWS EKS, managed Kafka, Redis cache, multi‑AZ deployment, automated CI/CD. |

---

## Technical Stack

### Confirmed Decisions

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Mobile Frontend** | **Flutter** | Cross‑platform, native performance, single codebase, hot reload, strong community support. |
| **Backend Language/Framework** | **Node.js + NestJS** | Structured, testable, built‑in GraphQL support for BFF, mature ecosystem. |
| **Container Runtime** | **Docker** | Standardized packaging, consistent dev‑to‑prod workflow. |
| **Orchestration** | **AWS EKS (Kubernetes)** | Managed cluster, auto‑scaling, multi‑AZ HA, native integration with AWS services. |
| **API Gateway / BFF** | **Nginx + NestJS Gateway** | Aggregates micro‑services, enforces auth, rate‑limiting, and caching. |
| **Event Bus** | **Amazon MSK (Kafka)** | Durable, scalable, low‑latency event streaming. |
| **Cache** | **Amazon ElastiCache Redis** | In‑memory cache for trip/expense state, 10 min TTL. |
| **Data Stores** | PostgreSQL (RDS) for core data, DynamoDB for media tags, S3 for blobs & exports. | Relational consistency where needed, NoSQL for high‑write workloads, durable object storage. |
| **CI/CD** | **GitHub Actions + Terraform + Helm** | Git‑centric, IaC, declarative deployments. |
| **Observability** | CloudWatch, Prometheus + Grafana, OpenTelemetry + X‑Ray | Unified metrics, logs, traces, alerts. |
| **Security** | Auth0 (OIDC) for user auth, AWS KMS for envelope encryption, TLS 1.3 + mTLS | Off‑the‑shelf identity, strong encryption, secure inter‑service comms. |
| **Notification** | SNS + FCM/APNs | Low‑latency push to mobile. |
| **Email** | Amazon SES | Cost‑effective, compliant, templated emails. |
| **AI Summaries** | OpenAI / Azure OpenAI | LLM integration, REST API, flexible pricing. |
| **Cloud Provider** | **AWS** (us‑east‑1) | Mature services, global reach, compliance certifications. |

### Alternatives Considered

- **React Native + Go**: Rejected due to higher mobile code maintenance and lack of native performance parity.
- **Azure AKS / GKE**: Evaluated but AWS EKS offers tighter integration with KMS, SNS, SES, and cost‑effective spot instances.
- **Auth0 vs. Cognito**: Chosen Auth0 for rapid onboarding, fallback to Cognito for MFA if needed.
- **AWS OpenAI vs. Azure OpenAI**: OpenAI selected for model flexibility; Azure OpenAI considered for data residency but not required.

### Open Items / TBD

- **Region Selection**: us‑east‑1 chosen; confirm compliance with local data‑resident partners if needed.
- **AI Provider**: Final decision on Azure OpenAI vs. OpenAI pending cost‑benefit analysis.
- **Notification Service**: FCM selected; evaluate AWS SNS push for iOS if needed.

---

## Security Architecture

### Authentication & Authorization

> **Confirmed**: OAuth2/OpenID Connect via Auth0.
> *Scope*: Short‑lived JWTs (15 min) signed with RSA‑2048, refreshed via Auth0’s silent renewal.
> *Roles*: Traveler (owner), Buddy (view/edit), Admin (audit, key‑rotation), Agency Partner (read‑only).
> *Policy*: Permissions are stored in a dedicated Permission Service; changes trigger event to update all clients instantly.

### Data Protection

| Layer | Encryption | Key Management | Rationale |
|-------|------------|----------------|-----------|
| **At Rest** | AES‑256 (column‑level or TDE) | Envelope encryption via AWS KMS | Meets PCI‑DSS, GDPR, ISO 27001 |
| **In Transit** | TLS 1.3 | Mutual TLS for inter‑service traffic | 99.9 % uptime SLA, compliance |
| **Key Rotation** | Quarterly (90 days) | AWS KMS automatic rotation | Zero manual downtime, audit trail |

### Compliance & Regulatory Requirements

| Requirement | Implementation |
|-------------|----------------|
| GDPR / CCPA | Data‑subject rights API (export, delete, portability), 30‑day retention, consent capture |
| PCI‑DSS | Encrypted card data (if any), audit logging, secure key handling |
| ISO 27001 | Documentation, risk assessment, regular penetration testing |
| SOC 2 | Continuous monitoring, access controls, incident response |

### Access Control

| Role | Permissions | Enforcement |
|------|-------------|-------------|
| Traveler | Full CRUD, invite, permission changes | API gatekeeper, UI enable/disable |
| Buddy | Read‑only, view balances | API 403 on edit attempts |
| Admin | Audit view, key rotation, duplicate merge | Separate IAM role, immutable logs |
| Agency Partner | Read‑only usage metrics | API key + rate limiting |

### Open Items / TBD

- **MFA**: Optional for Travelers; evaluate Auth0’s MFA flow.
- **Key‑Admin Role**: Define granular IAM policies for KMS key access.

---

## Infrastructure & Deployment

### Cloud Provider & Region

| Item | Choice | Rationale |
|------|--------|-----------|
| Provider | **AWS** | Mature ecosystem, KMS, SNS, SES, EKS, S3, compliance |
| Region | **us‑east‑1** | Low latency to primary user base, cost‑effective spot instances |

### Containerization & Orchestration

- **Docker** images built from source, signed, immutable tags.
- **AWS EKS** (managed Kubernetes) with 2‑AZ cluster, CNI, CoreDNS.
- **Helm** charts per micro‑service; values per environment.

### CI/CD Pipeline

| Stage | Tool | Description |
|-------|------|-------------|
| **Build** | GitHub Actions | Compile, lint, unit tests, Docker build |
| **Test** | Jest (Node), Cypress (mobile) | 80 %+ coverage |
| **Package** | Docker, ECR | Push signed images |
| **Deploy** | Terraform + Helm | Plan, apply, rollbacks |
| **Monitor** | Prometheus, Grafana, PagerDuty | Alert on SLA breaches |

### Environment Strategy

| Environment | Purpose | Promotion |
|-------------|---------|-----------|
| **Dev** | Rapid iteration | Manual PR merge |
| **Staging** | Integration + load testing | GitHub PR approval |
| **Prod** | Customer traffic | Blue/Green deployment, canary releases |

### Open Items / TBD

- **Canary Strategy**: Define traffic split percentages.
- **Feature Flags**: Evaluate LaunchDarkly or custom flag service.

---

## Stability & Performance

### SLA Targets

| Metric | Target |
|--------|--------|
| BFF 95th percentile latency | **< 400 ms** |
| 99.9 % uptime (prod) | **≥ 99.9 %** |
| Error rate | **< 1 %** |
| Notification delivery | **≤ 200 ms** |
| AI Summary generation | **≤ 30 s** |
| Export generation | **≤ 2 min** for 30‑day trips |

### Caching Strategy

| Layer | Cache | TTL | Invalidation |
|-------|-------|-----|--------------|
| Trip & Expense state | **Redis** (ElastiCache) | 10 min | On write |
| Export assets | **CloudFront CDN** | 7 days | Invalidate on new export |
| Media thumbnails | **S3 Object Cache** | 30 days | Manual purge via API |

### Load Handling

- **Autoscaling**: HPA based on CPU + custom metric (trip creation rate). Target CPU 70 %.
- **Spot Instances**: AI, Export, Media services run on spot with on‑demand fallback.
- **Load Balancing**: ALB for BFF (internal), NLB for external APIs.

### Monitoring & Alerting

| Tool | Role |
|------|------|
| **Prometheus** | Metrics |
| **Grafana** | Dashboards |
| **OpenTelemetry Collector** | Traces to X‑Ray |
| **CloudWatch** | Logs, alarms |
| **PagerDuty** | Incident escalation |

Key metrics: latency percentiles, error rates, queue depths, cache hit ratios, sync success rate.

### Open Items / TBD

- **Tracing Granularity**: Decide which micro‑services expose spans.
- **Chaos Engineering**: Plan for fault injection.

---

## Third‑Party Integrations

### Confirmed Integrations

| Integration | Purpose | API/SDK | Auth Method | Risk Level |
|-------------|---------|---------|-------------|------------|
| **OpenAI** | AI‑generated daily summaries | REST | API Key | Medium |
| **AWS KMS** | Envelope encryption | AWS SDK | IAM | Low |
| **SNS / FCM/APNs** | Push notifications | AWS SDK, Firebase | IAM / API Key | Low |
| **SES** | Email invites & summaries | AWS SDK | IAM | Low |
| **Auth0** | User identity & auth | Auth0 SDK | OAuth2 | Medium |
| **S3** | Media, exports, audit logs | AWS SDK | IAM | Low |
| **MSK** | Event bus | Kafka client | IAM | Low |
| **Agency API** | Usage metrics for partners | REST | API Key | Low |

### Integration Risks & Mitigations

| Integration | Risk | Mitigation |
|-------------|------|------------|
| **OpenAI** | Vendor lock‑in, model cost spikes | Evaluate Azure OpenAI; cache prompts; set budget alerts |
| **Auth0** | Single point of failure, potential downtime | Configure failover to Cognito; health checks |
| **SNS/FCM** | Push delivery delays | Use FCM topic subscriptions; monitor delivery metrics |
| **SES** | Email reputation degradation | DKIM/SPF, bounce handling, throttling |

### Open Items / TBD

- **Azure OpenAI**: Decision pending on data residency.
- **Agency API Auth**: Consider OAuth2 vs API keys.

---

## Appendix

### A. Raw Architecture Notes

- **Offline Sync**: Local SQLite + Conflict Vector; sync triggers on reconnection or manual refresh.
- **Duplicate Detection**: 10‑second window, heuristics on amount, timestamp, location.
- **Audit Trail**: Immutable JSON logs stored in a separate S3 bucket with versioning and WORM.
- **Encryption**: Envelope encryption per record; key ID stored in metadata.
- **Media Validation**: SHA‑256 checksum on upload; corrupted files flagged immediately.
- **Time‑zone Handling**: All timestamps stored UTC; UI converts based on itinerary location metadata.

### B. Glossary

| Term | Definition |
|------|------------|
| **BFF** | Backend‑for‑Frontend; aggregates micro‑services for mobile client. |
| **MSK** | Managed Streaming for Kafka (AWS). |
| **JWT** | JSON Web Token; used for auth & invitation links. |
| **mTLS** | Mutual TLS; used for inter‑service communication. |
| **KMS** | Key Management Service; handles key storage & rotation. |
| **S3** | Amazon Simple Storage Service; object storage. |
| **IAM** | Identity and Access Management; fine‑grained permissions. |
| **Cognito** | AWS managed identity provider (fallback). |
| **FCM** | Firebase Cloud Messaging; push notifications. |
| **SES** | Simple Email Service; transactional email. |