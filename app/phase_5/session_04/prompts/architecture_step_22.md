
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
5. `{system_container_intro}`



# Required OUTPUT


## STRUCTURAL DEFINITION TABLES (Factual Only)

No explanations. No reasoning. No duplication of Output 1 narrative.

### Application Containers

`| Name | Type | Responsibility | Exposes | Consumes |`

---

### Data Store Containers

`| Name | Store Type | Owned By | Access Pattern |`

---

### Supporting Elements (from Level 1)

`| Element | Type | Touches Which Container |`

---
