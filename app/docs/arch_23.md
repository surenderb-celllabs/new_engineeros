---
title: TripSync — C4 Level 2 Container Diagram
---
graph TD

  %% ---------- System Boundary ----------
  subgraph Boundary["🔲 TripSync System"]
    %% Application Containers
    MobileApp["TripSync Mobile App\n[Container]"]
    BFF["TripSync Backend API Gateway (BFF)\n[Container]"]
    TripService["Trip Service\n[Container]"]
    ExpenseService["Expense Service\n[Container]"]
    MediaService["Media Service\n[Container]"]
    PermissionService["Permission Service\n[Container]"]
    NotificationService["Notification Service\n[Container]"]
    AIService["AI Summarisation Service\n[Container]"]
    ExportService["Export Service\n[Container]"]
    AuditService["Audit Service\n[Container]"]
    AuthService["Auth Service\n[Container]"]
    KMSIntegration["KMS Integration\n[Container]"]

    %% Data Store Containers
    TripDB["Trip DB\n[Data Store]"]
    ExpenseDB["Expense DB\n[Data Store]"]
    MediaMetaDB["Media Metadata DB\n[Data Store]"]
    PermissionDB["Permission DB\n[Data Store]"]
    AuditLogStore["Audit Log Store\n[Data Store]"]
    UserDB["User DB\n[Data Store]"]
    KMSKeyStore["KMS Key Store\n[Data Store]"]
    CloudStorage["Cloud Storage\n[Data Store]"]
  end

  %% ---------- External Systems ----------
  ExternalAI["🤖 External AI Service\n[Software System]"]
  ExternalPush["📲 Push Notification Service\n[Software System]"]
  ExternalEmail["✉️ Email Service\n[Software System]"]
  ExternalAuth["🔑 External Authentication Service\n[Software System]"]
  ExternalKMS["🔐 External Key‑Management Service\n[Software System]"]
  ExternalTravelAgency["🏢 Travel Agency API\n[Software System]"]

  %% ---------- Interactions ----------
  MobileApp --> BFF

  BFF --> TripService
  BFF --> ExpenseService
  BFF --> MediaService
  BFF --> PermissionService
  BFF --> NotificationService
  BFF --> ExportService
  BFF --> AuditService
  BFF --> AuthService
  BFF --> KMSIntegration
  BFF --> ExternalTravelAgency

  TripService --> TripDB
  ExpenseService --> ExpenseDB
  MediaService --> MediaMetaDB
  MediaService --> CloudStorage
  PermissionService --> PermissionDB
  AuditService --> AuditLogStore
  AuthService --> UserDB
  KMSIntegration --> KMSKeyStore

  NotificationService --> ExternalPush
  NotificationService --> ExternalEmail
  AIService --> ExternalAI
  ExportService --> CloudStorage
  AuthService --> ExternalAuth
  KMSIntegration --> ExternalKMS