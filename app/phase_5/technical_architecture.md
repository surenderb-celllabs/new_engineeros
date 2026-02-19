**Architecture Decision Document**
*Prepared by: Senior Technical Architect*
*Date: 2026‑02‑18*

---

## 1. Tech Stack Decisions

| Layer | Recommendation | Rationale (tied to retrieved artefacts) |
|-------|----------------|----------------------------------------|
| **Languages** | **Go (v1.22+)** for the **Scheduling & Conflict‑Resolution Engine** – low‑latency, strong concurrency model. <br> **Node.js (v20) / TypeScript** for **Auth Service**, **Training‑Content Service**, and **API Gateway** – fast development, rich ecosystem for OAuth2/OIDC, media handling, and UI tooling. <br> **Python (3.12)** for **Notification Workers** – mature libraries for email/SMS/webhook delivery and easy scripting of retry/back‑off logic. | • The functional fragments repeatedly reference a **high‑performance conflict engine** that must fetch live availability and historical patterns within **≤5 s** (see FR‑0078). Go’s goroutine model is ideal for this. <br> • The **patient‑portal UI** and **magic‑link login** require rapid iteration and strong typing; TypeScript on a React/Next.js front‑end satisfies the “secure, password‑less login” user story (USER_STORY‑0001). <br> • Notification requirements (email/SMS/webhook) are described in several FRs (e.g., FR‑0082) and benefit from Python’s rich async libraries (aiohttp, Twilio, SendGrid). |
| **Frameworks** | • **React + Next.js** (SSR for SEO, fast initial load, built‑in routing). <br> • **NestJS** (Node.js) for Auth & Training services – opinionated, supports GraphQL/REST, built‑in validation, and easy integration with OpenID Connect. <br> • **Gin** (Go) for the Scheduling Engine – lightweight, high‑throughput HTTP/gRPC server. <br> • **FastAPI** (Python) for Notification Workers – async‑first, automatic OpenAPI docs. | The user‑story “secure, password‑less login” and the non‑functional requirement for **accessibility (WCAG 2.1 AA)** demand a UI framework with strong component libraries (Material‑UI) and server‑side rendering for performance. NestJS provides a modular monorepo that aligns with the micro‑service approach. |
| **Databases** | **PostgreSQL 15** (primary transactional store) – ACID guarantees for appointments, user accounts, and audit logs. <br> **Redis 7** (in‑memory cache) – session store, token revocation list, and fast lookup of live availability. <br> **Elasticsearch 8** (search & analytics) – full‑text search of training content, log aggregation, and compliance reporting. <br> **Object Store (AWS S3 / Azure Blob)** – encrypted storage for video/slide assets, audit‑log archives, and backup snapshots. | • FR‑0078 & FR‑0080 require **sub‑second reads** of live availability → Redis cache. <br> • NFR‑0000 mandates **TLS 1.3 in‑flight encryption** and **AES‑256 at rest** – PostgreSQL with Transparent Data Encryption (TDE) and S3 with HSM‑managed keys meet this. <br> • Training‑module delivery (FR‑0231) and the need for “searchable” content justify Elasticsearch. |

---

## 2. Data Architecture

| Aspect | Design | Why (document‑driven) |
|--------|--------|-----------------------|
| **Storage Strategy** | • **Transactional data** (appointments, user profiles, audit logs) → PostgreSQL. <br> • **Ephemeral/fast‑lookup data** (live calendar slots, JWT revocation, rate‑limit counters) → Redis. <br> • **Binary assets** (videos, slides, PDFs) → S3 (encrypted, CDN‑fronted). <br> • **Searchable metadata** (training titles, tags, transcript) → Elasticsearch. | The functional set lists **“live availability”**, **“conflict resolution”**, and **“training content delivery”** as core capabilities. Each storage tier is matched to its performance & durability needs. |
| **Data Modeling** | **Core entities**: <br> • **User** (patient, staff, admin) – UUID, email/phone, MFA status, roles. <br> • **Appointment** – ID, patient_id, provider_id, start_ts, end_ts, status, audit_id. <br> • **Rule** – rule_id, description, priority, trigger_event, action. <br> • **TrainingModule** – module_id, title, type (video/slide/widget), asset_refs, accessibility_meta. <br> **Relationships**: One‑to‑many (User → Appointments), many‑to‑many (User ↔ Role), one‑to‑many (TrainingModule → Assets). | The **user‑story** “Secure patient portal login” and the **functional requirement** “The engine must fetch live availability data … within 5 s” imply a tight coupling between Users, Appointments, and Rules. The **training‑module FRs** (FR‑0231, FR‑0237) require explicit module‑asset linkage. |
| **Data Flow** | 1. **Login** – Patient enters email/phone → Auth Service sends magic‑link → OIDC token issued → Front‑end stores short‑lived JWT. <br> 2. **Appointment CRUD** – UI → API Gateway → Scheduling Service (Go) → reads live slots from Redis, validates against Rules (PostgreSQL) → writes appointment & audit log to PostgreSQL (transactional). <br> 3. **Conflict Engine** – Triggered by appointment create/update → reads live & historic patterns (Redis + PostgreSQL) → applies rule engine → publishes resolution event to Kafka. <br> 4. **Training Content** – UI requests module → Training Service fetches metadata from PostgreSQL, assets from S3 (via signed URLs), and search results from Elasticsearch. <br> 5. **Notifications** – Resolution event → Kafka → Notification Workers (Python) → SendGrid/Twilio → store delivery status in PostgreSQL. | This flow directly satisfies the **acceptance criteria** for login, scheduling, and notification FRs (e.g., “success toast appears with a download link”, “error toast appears with a user‑readable error message”). |

---

## 3. Infrastructure & Deployment

| Component | Decision | Justification |
|-----------|----------|----------------|
| **Cloud Provider** | **AWS (or Azure/GCP as equivalent)** – primary because of native services: EKS (Kubernetes), RDS (PostgreSQL), ElastiCache (Redis), S3 with **AWS KMS/HSM**, SNS/SQS for event bus, and **Amazon Cognito** (optional OIDC provider). | The non‑functional requirement **“All data in transit must be encrypted using TLS 1.3”** and **“AES‑256 at rest with HSM‑managed keys”** map cleanly to AWS KMS‑backed encryption. The architecture already references **CDN** (CloudFront) for video delivery. |
| **Containerization** | All services packaged as **Docker images** and deployed on **Amazon EKS** (managed Kubernetes). Helm charts for each micro‑service, with separate namespaces for **dev / staging / prod**. | Enables **zero‑downtime deployments**, **horizontal scaling** for the high‑throughput scheduling engine, and isolates workloads per the **micro‑service** approach. |
| **CI/CD Pipeline** | **GitHub Actions** (or Azure DevOps) → lint → unit/integration tests → build Docker images → push to **Amazon ECR** → **ArgoCD** (GitOps) to sync Helm releases to EKS. Gate with **OPA** policies for security compliance (e.g., no privileged containers). | The document’s “CI/CD – GitHub Actions or Azure DevOps pipelines, using OPA for policy checks” matches this choice. |
| **Observability Stack** | **OpenTelemetry** instrumentation in all services → **Jaeger** for distributed tracing → **Prometheus** + **Grafana** for metrics → **Loki** for log aggregation. Alerts via **PagerDuty**. | Aligns with the **observability** section of the earlier answer and satisfies the SLA‑based alerting (e.g., “5 s availability fetch”). |
| **Message Bus** | **Kafka (MSK)** for event streaming (conflict events, notification jobs). | Guarantees **at‑least‑once** delivery needed for audit‑log consistency and decoupled notification processing. |
| **Secrets Management** | **HashiCorp Vault** (or AWS Secrets Manager) → integrated with Kubernetes via **External Secrets Operator**. | Meets the **key‑management** requirement (HSM‑managed keys) and allows rotation without redeploy. |

---

## 4. Security

| Area | Decision | Rationale |
|------|----------|-----------|
| **Transport Encryption** | Enforce **TLS 1.3** on all inbound/outbound connections (ALB/Ingress, API Gateway, service‑to‑service). | Directly satisfies **NFR‑0000** (“TLS 1.3 in‑flight encryption”). |
| **Data‑at‑Rest Encryption** | PostgreSQL tables encrypted with **AWS RDS Transparent Data Encryption**; S3 objects encrypted with **AES‑256** using **KMS‑managed keys**; Redis encrypted via **in‑transit TLS** and **at‑rest encryption** (EKS‑sidecar). | Matches the “AES‑256 at rest” requirement. |
| **Identity & Access Management** | Central **OIDC provider** (Cognito) issuing short‑lived JWTs (15 min) for magic‑link flow; **RBAC** enforced via **OPA** policies on the API Gateway and within services. | The user‑story for “secure, password‑less login” and the functional requirement for “role‑based access for staff” drive this. |
| **Threat Model & Mitigations** | • **Injection & XSS** – Input validation via NestJS/Go validators, Content‑Security‑Policy on UI. <br> • **Broken Authentication** – One‑time magic links, token revocation list in Redis, MFA optional for staff. <br> • **Data Leakage** – Least‑privilege IAM roles, bucket policies restricting public access, audit logs for every privileged action. <br> • **Denial‑of‑Service** – Rate‑limiting at API Gateway, auto‑scaling K8s pods, circuit‑breaker patterns in Go services. | These mitigations directly address the **OWASP Top 10** and the non‑functional security expectations mentioned in the earlier summary. |
| **Compliance** | **HIPAA‑Ready** – BAA signed with cloud provider, audit logging of all PHI accesses, encryption as above, regular **HIPAA risk assessments**. | The overall problem statement is a **HIPAA‑compliant patient portal**. |

---

## 5. Observability

| Concern | Tooling | Details |
|---------|---------|---------|
| **Logging** | **Loki** + **Fluent Bit** sidecar → structured JSON logs (requestId, userId, correlationId). | Enables log correlation across micro‑services for the “audit log entry” FRs. |
| **Metrics** | **Prometheus** exporters in each service (Go `promhttp`, Node `prom-client`, Python `prometheus_client`). Key metrics: login success rate, appointment creation latency, conflict‑engine processing time, notification delivery success. | Aligns with acceptance criteria like “99 % of login attempts succeed without error”. |
| **Tracing** | **OpenTelemetry** → **Jaeger** backend. Propagate `trace‑id` through API Gateway, Kafka headers, and downstream services. | Provides end‑to‑end visibility for the **5 s availability fetch** SLA. |
| **Dashboards** | **Grafana** dashboards per domain (Auth, Scheduling, Notifications). | Allows product owners to monitor **SLAs** and **security events**. |
| **Alerting** | **Prometheus Alertmanager** → **PagerDuty** / **Slack**. Sample alerts: <br> • “Auth service error rate > 2 % over 5 min”. <br> • “Scheduling engine latency > 5 s”. <br> • “Failed notification delivery > 1 %”. | Directly derived from the **acceptance criteria** and the **performance NFRs**. |

---

## 6. Authentication & Authorization

| Component | Decision | Rationale |
|-----------|----------|-----------|
| **Identity Provider** | **AWS Cognito** (or Auth0) with **OpenID Connect**. Supports **magic‑link** flow (email/SMS) and can issue short‑lived JWTs. | Mirrors the “magic‑link login” described in USER_STORY‑0001 and satisfies the “OAuth 2.0 + OpenID Connect” requirement. |
| **Token Strategy** | **JWT** signed with RS256 (private key stored in Vault). **Refresh tokens** are **single‑use** and stored in Redis with TTL (15 min). | Guarantees stateless auth for the front‑end while allowing immediate revocation (via Redis revocation list). |
| **Access Control** | **RBAC** (roles: Patient, Clinician, Scheduler, Admin) enforced by **OPA** policies at the API Gateway and within services. **ABAC** extensions for context‑based rules (e.g., “only appointments belonging to the same clinic can be edited”). | The functional spec lists **role‑based access** for staff and **fine‑grained permissions** for scheduling. |
| **Session Management** | Sessions stored in **Redis** (encrypted) with idle timeout of **30 min**. | Provides fast lookup for token revocation and aligns with the **performance** requirement for low latency. |
| **Multi‑Factor** | Optional **TOTP** for staff accounts; enforced via Cognito’s MFA settings. | Enhances security for privileged users, complying with HIPAA’s “reasonable and appropriate” safeguards. |

---

## 7. Third‑Party Integrations

| Integration | Purpose | Selected Provider / Reason |
|-------------|---------|----------------------------|
| **Electronic Health Record (EHR) – FHIR API** | Pull patient demographic & clinical data for portal display. | **FHIR‑compatible EHR** (e.g., Epic, Cerner) via OAuth 2.0 scopes – aligns with HIPAA and ensures standardized data exchange. |
| **Messaging** | Email (appointment confirmations, error toasts) & SMS (magic‑link delivery, reminders). | **SendGrid** (email) & **Twilio** (SMS) – robust APIs, high deliverability, easy webhook integration for delivery status. |
| **Video Streaming / CDN** | Serve training videos & fallback MP4 download. | **Amazon CloudFront** + **S3** – low latency edge delivery, signed URLs for secure access, automatic fallback to MP4 per FR‑0231. |
| **Search / Analytics** | Full‑text search of training modules, log analytics for compliance reporting. | **Elasticsearch Service** (managed) – integrates with Kibana for audit‑log queries and supports the “searchable training content” requirement. |
| **Payments (optional)** | If future billing is added (e.g., for premium modules). | **Stripe** – PCI‑DSS‑compliant, easy to integrate, but **not required** for the current MVP. |
| **Monitoring / Alerting** | Centralized alert routing. | **PagerDuty** (or AWS SNS) – integrates with Prometheus Alertmanager, ensures 24/7 on‑call coverage. |

> **Assumptions** (where source documents were ambiguous)
> 1. The **cloud provider** is not explicitly mandated; AWS is chosen for its breadth of managed services that map directly to the security & compliance requirements.
> 2. **OAuth 2.0 / OIDC** is the preferred authentication protocol, inferred from the “OAuth 2.0 Authorization Server + OpenID Connect” mention.
> 3. The **rule engine** for conflict resolution will be a custom Go library (or open‑source Drools‑like engine) – the documents reference “rules repository” and “engine must load all rules”.
> 4. **Kafka** is assumed as the event bus because the FRs speak of “publish events” and “notification workers”. If the organization prefers a serverless alternative, AWS EventBridge could replace Kafka with minimal changes.

---

### Conclusion

The proposed architecture satisfies all seven focus areas—**tech stack, data architecture, infrastructure & deployment, security, observability, authentication & authorization, and third‑party integrations**—while directly reflecting the functional and non‑functional requirements extracted from *problem.yaml*, *user_stories.yaml*, and *func_nonfunc.yaml*. It delivers a **scalable, secure, and observable** platform ready for HIPAA‑compliant patient portal operations, robust scheduling with conflict resolution, and accessible training‑module delivery.

**Next Steps**

1. **Kick‑off meeting** – align engineering, security, and compliance teams (agenda: timeline, responsibilities, BAA sign‑off).
2. **Create detailed design artifacts** – component diagrams, data‑model ERD, API contracts (OpenAPI).
3. **Prototype** – implement the Auth Service + Magic‑Link flow and the Scheduling Engine stub to validate latency targets.

*Prepared by:* Senior Technical Architect – **[Your Name]**
*Contact:* [email | Slack]