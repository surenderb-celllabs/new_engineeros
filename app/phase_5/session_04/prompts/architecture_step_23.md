

# ROLE
You are a senior solution architect specializing in C4 model documentation.
Produce a C4 Level 2 Container Diagram by zooming into the system boundary 
from the provided documents.

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
1. `{problem_solution}`
2. `{user_stories}`
3. `{func_non_func_requirements}`
4. `{system_context_document}` — previously generated C4 Level 1 output
5. `{system_container_intro}` - C4 Level 2 Container Intro
6. `{system_container_structure}`- C4 Level 2 Container Structure



# Required OUTPUT



## MERMAID CONTAINER DIAGRAM

Technology-neutral.  
Must match Output 2 exactly.  
Do not introduce new containers.

```mermaid
---
title: [System Name] — C4 Level 2 Container Diagram
---
graph TD

  User["👤 User\n[Person]"]

  subgraph Boundary["🔲 System Boundary"]

    Frontend["⬜ Frontend\n[Container]"]
    API["⬛ Application API\n[Container]"]
    Worker["📨 Background Processor\n[Container]"]

    PrimaryDB[("🗄️ Primary Data Store\n[Data Store]")]
    Cache[("⚡ Cache Store\n[Data Store]")]
    ObjectStore[("🪣 Object Store\n[Data Store]")]

  end

  External["📦 External System\n[Software System]"]

  User --> Frontend
  Frontend --> API
  API --> PrimaryDB
  API --> Cache
  API --> ObjectStore
  API --> Worker
  API --> External
````
