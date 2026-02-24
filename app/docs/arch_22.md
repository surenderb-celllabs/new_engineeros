### Application Containers

| Name | Type | Responsibility | Exposes | Consumes |
|------|------|----------------|---------|----------|
| TripSync Mobile App | Mobile App (iOS/Android) | Unified UI, offline storage, sync, push & email handling | HTTP/REST + WebSocket API to BFF | BFF, local cache, WebSocket, Push & Email services |
| TripSync Backend API Gateway (BFF) | API Gateway | Request aggregation, auth, rate‑limiting, single mobile contract | REST/GraphQL to Mobile App | Trip Service, Expense Service, Media Service, Permission Service, Notification Service, Export Service, Audit Service, Auth Service, KMS Integration |
| Trip Service | Microservice | Trip metadata, itinerary, version history | REST/GRPC endpoints | Trip DB, Event Bus, KMS |
| Expense Service | Microservice | Expense CRUD, split calculation, categorisation | REST/GRPC endpoints | Expense DB, Event Bus, Trip Service, KMS |
| Media Service | Microservice | Media upload, metadata, size‑limit enforcement | REST/GRPC endpoints | Media Metadata DB, Cloud Storage, Event Bus, KMS |
| Permission Service | Microservice | Role assignment, revocation, real‑time updates | REST/GRPC endpoints | Permission DB, Event Bus, Auth Service |
| Notification Service | Microservice | Push & email notifications for events | REST/GRPC endpoints | Push Notification Service, Email Service, Event Bus |
| AI Summarisation Service | Microservice | Daily summary scheduling, LLM integration | REST/GRPC endpoints | External AI LLM, Event Bus, Trip/Expense data |
| Export Service | Microservice | PDF/ZIP export generation | REST/GRPC endpoints | Cloud Storage, Trip/Expense data, Event Bus |
| Audit Service | Microservice | Immutable audit trail, key‑rotation logging | REST/GRPC endpoints | Event Bus, Immutable Log Store |
| Auth Service | Microservice | User authentication, JWT issuance | REST/GRPC endpoints | User DB, KMS |
| KMS Integration | Microservice | Encryption key retrieval & rotation | Internal API | External KMS (AWS KMS / Azure Key Vault / GCP KMS) |

---

### Data Store Containers

| Name | Store Type | Owned By | Access Pattern |
|------|------------|----------|----------------|
| Trip DB | Relational (PostgreSQL) | Trip Service | CRUD, frequent reads |
| Expense DB | Relational (PostgreSQL) | Expense Service | CRUD, frequent reads |
| Media Metadata DB | Document (MongoDB / DynamoDB) | Media Service | CRUD, index on trip_id |
| Permission DB | Relational (PostgreSQL) | Permission Service | CRUD, frequent reads |
| Audit Log Store | Immutable append‑only (S3 / Cloud Logging) | Audit Service | Append‑only writes, read‑only queries |
| User DB | Relational (PostgreSQL) | Auth Service | CRUD, authentication look‑ups |
| KMS Key Store | External (AWS KMS / Azure Key Vault / GCP KMS) | KMS Integration | Key retrieval, rotation |
| Cloud Storage | Object Storage (S3 / GCS / Azure Blob) | Media Service, Export Service | Store media files, PDFs, ZIPs |

---

### Supporting Elements (from Level 1)

| Element | Type | Touches Which Container |
|---------|------|------------------------|
| Traveler | Actor (Person) | TripSync Mobile App |
| Buddy | Actor (Person) | TripSync Mobile App |
| Product Marketing Lead | Actor (Person) | TripSync Mobile App |
| Travel Agency Partner | Actor (Person) | TripSync Mobile App |
| Admin | Actor (Person) | TripSync Mobile App |
| AI Service (External LLM) | External Software System | AI Summarisation Service |
| Key‑Management Service (AWS KMS / Azure Key Vault / GCP KMS) | External Software System | KMS Integration |
| Push Notification Service | External Software System | Notification Service |
| Email Service | External Software System | Notification Service |
| Cloud Storage (S3 / GCS / Azure Blob) | External Software System | Media Service, Export Service |
| Authentication Service (OAuth / OpenID) | External Software System | Auth Service |
| Travel Agency API | External Software System | TripSync Backend API Gateway (BFF) |