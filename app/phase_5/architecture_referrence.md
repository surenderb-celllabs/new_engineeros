# Agentic Spec Builder - Technical Architecture

## Document Overview

This architecture document provides a comprehensive technical blueprint for building the Agentic Spec Builder system. It details the high-level architecture, component design, data flow, technology stack, and infrastructure requirements needed to implement the system described in the engineering specification.

---

## 1. High-Level Architecture

The Agentic Spec Builder follows a microservices-inspired architecture with clearly defined service boundaries. While the initial implementation may consolidate some services, the architecture is designed to support independent scaling and deployment of each functional area.

### 1.1 System Context

The system operates as a web-based application serving multiple user personas:

- **Founders/Product Owners** who need to translate ideas into actionable specifications
- **Engineering Leads/Architects** requiring precise, traceable requirements
- **AI Coding Agent Operators** needing atomic, unambiguous instructions
- **Legacy System Maintainers** requiring safe change plans with rollback procedures

### 1.2 Architectural Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────────────────┐  │
│  │  React Web App  │  │  Mobile Web App  │  │  Admin Dashboard         │  │
│  │  - Conversation │  │  (PWA)           │  │  - Workspace Management  │  │
│  │  - Decision     │  │                  │  │  - Analytics             │  │
│  │    Graph View   │  │                  │  │  - System Health         │  │
│  │  - Artifact     │  │                  │  │                           │  │
│  │    Viewer       │  │                  │  │                           │  │
│  └────────┬────────┘  └────────┬─────────┘  └────────────┬────────────┘  │
└───────────┼─────────────────────┼──────────────────────────┼───────────────┘
            │                     │                          │
            ▼                     ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY LAYER                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    API Gateway / Load Balancer                        │   │
│  │  - Rate Limiting                    - Request Routing                │   │
│  │  - Authentication                   - SSL Termination               │   │
│  │  - Request Validation               - Circuit Breaker                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATION LAYER                                │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Orchestration Service                              │   │
│  │  - Agent Dispatch                - Workflow State Machine             │   │
│  │  - Request Queueing              - Rate Limit Enforcement             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
┌─────────────────────────┐ ┌─────────────────┐ ┌─────────────────────────────┐
│     AGENT LAYER         │ │  EXTERNAL      │ │     CODEBASE ANALYSIS       │
│                         │ │  SERVICES       │ │     SERVICE                 │
│ ┌───────────────────┐   │ │                 │ │                             │ │
│ │ Interrogation     │   │ │ ┌─────────────┐ │ │ ┌────────────────────────┐ │ │
│ │ Agent             │   │ │ │ Anthropic   │ │ │ │ - GitHub/GitLab OAuth  │ │ │
│ │ - Question Gen   │   │ │ │ Claude API  │ │ │ │ - Git Clone Worker     │ │ │
│ │ - Option Pres.   │   │ │ └─────────────┘ │ │ │ - Multi-lang Parsers   │ │ │
│ └───────────────────┘   │ │ ┌─────────────┐ │ │ │ - Dependency Graph     │ │ │
│ ┌───────────────────┐   │ │ │ OpenAI      │ │ │ │   Builder              │ │ │
│ │ Specification     │   │ │ │ GPT-4 API   │ │ │ └────────────────────────┘ │ │
│ │ Agent             │   │ │ └─────────────┘ │ │                             │ │
│ │ - PRD Generation │   │ │ ┌─────────────┐ │ │                             │ │
│ │ - Schema Gen.    │   │ │ │ Replicate   │ │ │                             │ │
│ │ - Ticket Gen.    │   │ │ │ (Open Source│ │ │                             │ │
│ └───────────────────┘   │ │ │ Models)     │ │ │                             │ │
│ ┌───────────────────┐   │ │ └─────────────┘ │ │                             │ │
│ │ Validation Agent  │   │ └─────────────────┘ │ │                             │ │
│ │ - Contradiction  │   │                       │ │                             │ │
│ │   Detection      │   │                       │ │                             │ │
│ │ - Consistency     │   │                       │ │                             │ │
│ └───────────────────┘   │                       │ │                             │ │
│ ┌───────────────────┐   │                       │ │                             │ │
│ │ Context Memory    │   │                       │ │                             │ │
│ │ Agent             │   │                       │ │                             │ │
│ │ - RAG Retrieval   │   │                       │ │                             │ │
│ │ - Decision Graph  │   │                       │ │                             │ │
│ └───────────────────┘   │                       │ │                             │ │
│ ┌───────────────────┐   │                       │ │                             │ │
│ │ Delivery Agent    │   │                       │ │                             │ │
│ │ - Format Convert  │   │                       │ │                             │ │
│ │ - Export          │   │                       │ │                             │ │
│ └───────────────────┘   │                       │ │                             │ │
└─────────────────────────┘                       └─────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐              │
│  │ PostgreSQL     │  │ Vector Database │  │ Redis          │              │
│  │ (Primary)      │  │ (Embeddings)    │  │ (Cache/Session)│              │
│  │                │  │                 │  │                │              │
│  │ - Decisions    │  │ - Decision      │  │ - Sessions     │              │
│  │ - Artifacts    │  │   Embeddings    │  │ - Rate Limits  │              │
│  │ - Projects     │  │ - Conversation  │  │ - Job Queue    │              │
│  │ - Users        │  │   History       │  │ - Cache        │              │
│  │ - Workspace    │  │                 │  │                │              │
│  └────────────────┘  └────────────────┘  └────────────────┘              │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────┐          │
│  │                    Blob Storage (S3/GCS)                      │          │
│  │  - Uploaded Files (docs, images, audio)                       │          │
│  │  - Generated Artifacts (large files)                          │          │
│  │  - Exported Downloads                                         │          │
│  └────────────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

### 2.1 Presentation Layer

#### 2.1.1 React Web Application

The primary user interface built with React and TypeScript.

**Responsibilities:**
- Render conversation interface with real-time updates via WebSocket
- Display interactive decision graph using D3.js or similar visualization library
- Provide artifact viewer with diff capabilities
- Handle user authentication flow
- Manage local state and caching

**Key Features:**
- Conversation Interface: Chat-style interaction with question/answer flow
- Decision Graph Visualizer: Interactive node-based graph showing decision dependencies
- Artifact Viewer/Editor: View, edit, and compare generated artifacts
- Diff Viewer: Side-by-side comparison with syntax highlighting
- Project Dashboard: Overview of all projects with status indicators

**Technology Stack:**
- React 18+ with TypeScript
- Next.js for SSR and routing
- D3.js or React Flow for graph visualization
- Zustand or TanStack Query for state management
- Tailwind CSS for styling

#### 2.1.2 Mobile Web App (PWA)

Progressive Web App providing mobile access to core features.

**Responsibilities:**
- Responsive design for mobile devices
- Offline capability for viewing cached projects
- Push notifications for important updates

### 2.2 API Gateway Layer

The entry point for all client requests, providing cross-cutting concerns.

**Responsibilities:**
- Authentication and authorization enforcement
- Rate limiting per user and per IP
- Request validation and transformation
- SSL/TLS termination
- Service routing to appropriate backend services
- Circuit breaker pattern for fault tolerance
- Request logging and metrics collection

**Technology Stack:**
- AWS API Gateway or Kong
- Or custom Nginx with Lua scripting
- JWT validation and refresh token handling

**Key Configuration:**
- Request timeout: 30 seconds for sync, 120 seconds for async
- Max request size: 10MB
- Rate limit: 100 requests/minute per IP
- Circuit breaker: 5 failures triggers 30-second cooldown

### 2.3 Orchestration Service

The central coordinator for all agent interactions and workflow management.

**Responsibilities:**
- Agent dispatch and workflow orchestration
- Workflow state machine management
- Request queueing for long-running operations
- Rate limit enforcement at application level
- Job scheduling and status tracking
- Error handling and retry logic

**Architecture:**
- Event-driven design using message queue
- Workflow engine for multi-step processes
- Job queue with priority support
- Checkpoint system for long-running tasks

**Key Workflows:**
1. Project Creation → triggers Interrogation Agent
2. Answer Submission → triggers Validation Agent → triggers next question
3. Artifact Request → triggers Specification Agent → triggers Delivery Agent
4. Branch Merge → triggers Validation Agent → updates decision graph

### 2.4 Agent Layer

The core intelligence layer powered by Large Language Models.

#### 2.4.1 Interrogation Agent

Generates questions to resolve ambiguity and gather required information.

**Inputs:**
- Current project context (decision graph)
- Target artifacts to generate
- User's time investment setting
- Question templates for project type

**Process:**
1. Load decision graph from Context Memory Agent
2. Identify gaps via dependency analysis for target artifacts
3. Select appropriate question template
4. Generate question with 3-4 concrete options
5. Adapt format (radio, checkbox, form, free text)

**Outputs:**
- Question with options
- Context/rationale for the question
- Metadata about question category and dependencies

**LLM Configuration:**
- Primary: Claude Sonnet 4 (goal-oriented reasoning)
- Fallback: GPT-4 (simpler prompts)

**Performance Target:**
- Question presentation within 3-5 seconds
- Options are mutually exclusive and exhaustive
- No duplicate questions across project lifetime

#### 2.4.2 Specification Agent

Converts decisions into formal artifacts (PRD, schema, tickets, etc.).

**Inputs:**
- Decision graph
- Artifact type requested
- Tech stack information
- Export format requirements

**Process:**
1. Check dependencies: "Can we generate this artifact?"
2. If missing dependencies → return blockers
3. Generate artifact using Claude (primary)
4. Use hybrid approach for large artifacts (Claude + open-source)
5. Validate output against decision graph
6. Checkpoint progress every logical section
7. Return partial artifact on failure with clear gaps

**Outputs:**
- Generated artifact in requested format
- Metadata: generated_at, based_on_decisions[], tech_stack
- Checkpoint data for resume capability

**Artifact Types:**
- Product Requirements Document (PRD)
- Database Schema (SQL DDL, ER diagrams)
- API Contracts (OpenAPI, GraphQL SDL, gRPC protobuf)
- Engineering Tickets (GitHub Issues, Linear, Jira)
- Architecture Diagrams (C4 model in Mermaid)
- Test Cases (Gherkin format)
- Deployment Plans

**Performance Target:**
- Standard PRD within 30 seconds
- Checkpoints prevent total loss on failure

#### 2.4.3 Validation Agent

Ensures consistency and detects contradictions in decisions.

**Inputs:**
- User's answer to a question
- Current decision graph
- Project context

**Process:**
1. Parse user's answer
2. Check against existing decisions for contradictions
3. If conflict detected:
   - Flag immediately
   - Show conflicting decisions side-by-side
   - Ask user to resolve
4. If no conflict, store decision
5. Validate artifact consistency when requested

**Validation Types:**
- Contradiction Detection: Real-time checking of new answers
- Dependency Validation: Ensuring all required decisions exist
- Artifact Consistency: Validating generated artifacts match decisions
- Breaking Change Detection: For brownfield projects

**Performance Target:**
- Validation completes in <1 second

#### 2.4.4 Context Memory Agent

Maintains long-lived project state and provides semantic retrieval.

**Inputs:**
- Conversation turns
- Decisions
- Artifacts generated
- User queries

**Process:**
1. Store structured decision graph (not raw text)
2. Embed all decisions in vector DB for semantic retrieval
3. When context window limit approached:
   - Retrieve relevant context via RAG
   - Reconstruct structured summary from decision graph
4. Track dependencies between decisions

**Outputs:**
- Queryable decision graph
- Relevant context for agent prompts
- Decision dependency mapping

**Technology Stack:**
- Vector Database: Pinecone, Weaviate, or pgvector
- Embedding Model: OpenAI text-embedding-3 or similar
- Graph Database (optional): Neo4j for complex dependency tracking

**Performance Target:**
- Context retrieval <500ms
- Supports projects with >1000 decisions

#### 2.4.5 Delivery Agent

Formats and exports artifacts for consumption by various targets.

**Inputs:**
- Generated artifact
- Target format (Markdown, PDF, JSON, etc.)
- Target system (AI agent format, Git, download)

**Process:**
1. Detect artifact type
2. Use GPT-4 + open-source models for formatting
3. Generate requested formats:
   - PRD: Markdown, HTML, PDF, JSON
   - Database Schema: SQL DDL, Mermaid ER diagram
   - API Contracts: OpenAPI, GraphQL SDL, gRPC protobuf
   - Tickets: GitHub Issues, Linear, Markdown, custom formats (Cursor, Claude Code, Devin)
   - Architecture: C4 model in Mermaid
   - Test Cases: Gherkin format
4. Generate AI agent-specific formats

**Outputs:**
- Downloadable files (zip if multiple formats)
- Presigned URLs for user access
- Direct push to GitHub (if authorized)

**Performance Target:**
- Export completes in <10 seconds
- All formats valid and parseable

### 2.5 Codebase Analysis Service

Handles brownfield (existing codebase) project ingestion and analysis.

**Responsibilities:**
- OAuth integration with GitHub/GitLab
- Repository cloning with size handling
- Multi-language code parsing using Tree-sitter
- Static analysis and dependency graph building
- Architecture inference from code patterns
- Breaking change detection

**Process:**
1. **Import Phase:**
   - Authenticate via OAuth or accept Git URL
   - Clone repository (handle large repos with shallow clone)
   - Parse supported languages via Tree-sitter

2. **Analysis Phase:**
   - Build AST for each supported file
   - Identify dependencies (imports, requires, uses)
   - Detect entry points and main modules
   - Infer architecture patterns

3. **Inference Phase:**
   - Use LLM to analyze patterns
   - Generate C4 model (Context, Container, Component)
   - Present to user for confirmation/correction

**Supported Languages:**
- TypeScript/JavaScript
- Python
- Go
- Java
- C#
- PHP
- Ruby

**Performance Target:**
- Analysis within 5 minutes for repos <500K LOC

### 2.6 Authentication Service

Manages user identity and access control.

**Responsibilities:**
- Email/password authentication with secure hashing
- Magic link authentication
- OAuth 2.0 (Google, GitHub, Microsoft)
- Two-Factor Authentication (TOTP)
- Session management with JWT
- Role-based access control (RBAC)
- Workspace-level permissions

**Authentication Methods:**
1. **Email/Password:** bcrypt hashing, cost factor 12
2. **Magic Links:** One-time links valid 15 minutes
3. **OAuth:** Standard OAuth 2.0 flow
4. **2FA:** TOTP-compatible (Google Authenticator, Authy)

**Session Management:**
- JWT tokens with 7-day expiry
- HTTP-only cookies
- CSRF token rotation
- Refresh token rotation

**RBAC Model:**
- Owner: Full access + billing + delete workspace
- Admin: Manage members + all project actions
- Editor: Create/edit projects + answer questions + generate artifacts
- Viewer: Read-only access

### 2.7 File Storage Service

Manages uploaded files and generated artifacts.

**Responsibilities:**
- Store user uploads (documents, images, audio)
- Store generated artifacts (versioned)
- Serve download links with expiration
- Handle file type validation
- Enforce size limits

**Storage Tiers:**
- User uploads: Original files preserved
- Generated artifacts: Last 10 versions
- Exports: 7-day expiration on download URLs

**Supported File Types:**
- Documents: .pdf, .docx, .md, .txt
- Images: .png, .jpg, .jpeg, .gif
- Data: .csv, .json, .yaml
- Code: .sql, .proto (for imports)

---

## 3. Data Architecture

### 3.1 Database Schema (PostgreSQL)

The primary relational database for storing all structured data.

#### Core Tables

```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    totp_secret VARCHAR(255),
    totp_enabled BOOLEAN DEFAULT FALSE,
    oauth_providers JSONB DEFAULT '[]',
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Workspaces table
CREATE TABLE workspaces (
    workspace_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_user_id UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}',
    plan_tier VARCHAR(50) DEFAULT 'free'
);

-- Workspace members
CREATE TABLE workspace_members (
    member_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(workspace_id),
    user_id UUID REFERENCES users(user_id),
    role VARCHAR(50) NOT NULL,
    invited_by UUID REFERENCES users(user_id),
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    joined_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(workspace_id, user_id)
);

-- Projects table
CREATE TABLE projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(workspace_id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- greenfield, brownfield
    status VARCHAR(50) DEFAULT 'active',
    time_investment VARCHAR(50),
    template_id UUID,
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}'
);

-- Branches table
CREATE TABLE branches (
    branch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id),
    name VARCHAR(255) NOT NULL,
    parent_branch_id UUID REFERENCES branches(branch_id),
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    merged_at TIMESTAMP WITH TIME ZONE,
    merged_by UUID REFERENCES users(user_id),
    is_protected BOOLEAN DEFAULT FALSE,
    UNIQUE(project_id, name)
);

-- Decisions table (core entity)
CREATE TABLE decisions (
    decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id),
    branch_id UUID REFERENCES branches(branch_id),
    question_text TEXT NOT NULL,
    answer_text TEXT,
    options_presented JSONB,
    category VARCHAR(100),
    is_assumption BOOLEAN DEFAULT FALSE,
    assumption_reasoning TEXT,
    dependencies JSONB DEFAULT '[]',
    answered_by UUID REFERENCES users(user_id),
    answered_at TIMESTAMP WITH TIME ZONE,
    version INT DEFAULT 1,
    is_locked BOOLEAN DEFAULT FALSE
);

-- Artifacts table
CREATE TABLE artifacts (
    artifact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id),
    branch_id UUID REFERENCES branches(branch_id),
    type VARCHAR(100) NOT NULL,
    content TEXT,
    blob_storage_key VARCHAR(500),
    format VARCHAR(50),
    version INT DEFAULT 1,
    based_on_decisions JSONB DEFAULT '[]',
    generated_by VARCHAR(50),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_stale BOOLEAN DEFAULT FALSE,
    tech_stack JSONB
);

-- Artifact versions
CREATE TABLE artifact_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artifact_id UUID REFERENCES artifacts(artifact_id),
    content TEXT,
    version INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comments table
CREATE TABLE comments (
    comment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artifact_id UUID REFERENCES artifacts(artifact_id),
    section VARCHAR(255),
    user_id UUID REFERENCES users(user_id),
    comment_type VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    parent_comment_id UUID REFERENCES comments(comment_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(user_id)
);

-- Conversation turns
CREATE TABLE conversation_turns (
    turn_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id),
    branch_id UUID REFERENCES branches(branch_id),
    turn_number INT NOT NULL,
    agent VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    user_response TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, branch_id, turn_number)
);

-- Codebase analysis results
CREATE TABLE codebase_analyses (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id),
    codebase_url VARCHAR(500),
    codebase_size_loc INT,
    languages_detected JSONB,
    architecture_derived TEXT,
    architecture_diagram TEXT,
    dependency_graph JSONB,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_duration_seconds INT
);

-- Templates table
CREATE TABLE templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    workspace_id UUID REFERENCES workspaces(workspace_id),
    description TEXT,
    question_flow JSONB NOT NULL,
    default_tech_stack JSONB,
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(workspace_id),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- Indexes for performance
CREATE INDEX idx_projects_workspace ON projects(workspace_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_decisions_project ON decisions(project_id);
CREATE INDEX idx_decisions_branch ON decisions(branch_id);
CREATE INDEX idx_artifacts_project ON artifacts(project_id);
CREATE INDEX idx_artifacts_type ON artifacts(type);
CREATE INDEX idx_conversation_project ON conversation_turns(project_id, branch_id);
CREATE INDEX idx_audit_workspace_time ON audit_logs(workspace_id, timestamp);
```

### 3.2 Vector Database Schema

For semantic search and context retrieval.

**Collections:**

1. **decisions_embedding**
   - decision_id: UUID
   - project_id: UUID
   - question_text: string
   - answer_text: string
   - category: string
   - embedding: vector (1536 dimensions)

2. **conversation_history**
   - turn_id: UUID
   - project_id: UUID
   - message: string
   - embedding: vector (1536 dimensions)
   - timestamp: datetime

3. **artifacts_content**
   - artifact_id: UUID
   - project_id: UUID
   - content: string
   - artifact_type: string
   - embedding: vector (1536 dimensions)

### 3.3 Redis Data Structures

```redis
# Session storage
session:{user_id} -> JWT token data (TTL: 7 days)

# Rate limiting
rate_limit:{user_id}:{action} -> counter (TTL: 24 hours)
rate_limit:ip:{ip_address} -> counter (TTL: 1 minute)

# Job queue
job:{job_id} -> JSON job status
job_queue:pending -> list of job IDs
job_queue:processing -> list of job IDs

# Cache
cache:project:{project_id} -> project summary
cache:decision_graph:{project_id} -> graph data

# WebSocket sessions
ws:session:{session_id} -> user_id and metadata
```

### 3.4 Blob Storage Structure

```
s3://agentic-spec-builder/
├── user-uploads/
│   └── {workspace_id}/
│       └── {project_id}/
│           └── {timestamp}_{filename}
│
├── artifacts/
│   └── {workspace_id}/
│       └── {project_id}/
│           └── {artifact_id}/
│               ├── v1/
│               │   ├── content.md
│               │   └── metadata.json
│               └── v2/
│                   ├── content.md
│                   └── metadata.json
│
└── exports/
    └── {workspace_id}/
        └── {project_id}/
            └── {export_id}/
                └── {filename} (7-day TTL)
```

---

## 4. API Design

### 4.1 REST API Endpoints

#### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Authenticate user
- `POST /auth/logout` - Invalidate session
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/magic-link` - Send magic link
- `POST /auth/verify-magic-link` - Verify magic link
- `POST /auth/2fa/enable` - Enable 2FA
- `POST /auth/2fa/verify` - Verify 2FA code

#### Workspaces
- `GET /workspaces` - List user's workspaces
- `POST /workspaces` - Create workspace
- `GET /workspaces/{workspace_id}` - Get workspace details
- `PATCH /workspaces/{workspace_id}` - Update workspace
- `DELETE /workspaces/{workspace_id}` - Delete workspace
- `POST /workspaces/{workspace_id}/members` - Invite member
- `DELETE /workspaces/{workspace_id}/members/{member_id}` - Remove member
- `PATCH /workspaces/{workspace_id}/members/{member_id}` - Update member role

#### Projects
- `GET /workspaces/{workspace_id}/projects` - List projects
- `POST /workspaces/{workspace_id}/projects` - Create project
- `GET /projects/{project_id}` - Get project details
- `PATCH /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project
- `POST /projects/{project_id}/archive` - Archive project
- `POST /projects/{project_id}/restore` - Restore project

#### Questions & Decisions
- `GET /projects/{project_id}/questions` - Get current question
- `POST /projects/{project_id}/answers` - Submit answer
- `POST /projects/{project_id}/defer-question` - Defer question
- `GET /projects/{project_id}/decisions` - Get all decisions
- `GET /projects/{project_id}/decisions/{decision_id}` - Get decision details
- `PATCH /projects/{project_id}/decisions/{decision_id}` - Update decision

#### Artifacts
- `GET /projects/{project_id}/artifacts` - List artifacts
- `POST /projects/{project_id}/artifacts` - Generate artifact
- `GET /artifacts/{artifact_id}` - Get artifact details
- `GET /artifacts/{artifact_id}/versions` - Get artifact versions
- `GET /artifacts/{artifact_id}/diff` - Compare versions
- `POST /artifacts/{artifact_id}/regenerate` - Regenerate artifact

#### Comments
- `GET /artifacts/{artifact_id}/comments` - Get comments
- `POST /artifacts/{artifact_id}/comments` - Add comment
- `PATCH /comments/{comment_id}` - Update comment
- `DELETE /comments/{comment_id}` - Delete comment
- `POST /comments/{comment_id}/resolve` - Resolve comment

#### Branches
- `GET /projects/{project_id}/branches` - List branches
- `POST /projects/{project_id}/branches` - Create branch
- `GET /branches/{branch_id}` - Get branch details
- `POST /branches/{branch_id}/merge` - Merge branch
- `POST /branches/{branch_id}/resolve-conflicts` - Resolve conflicts

#### Codebase Analysis (Brownfield)
- `POST /projects/{project_id}/analyze` - Trigger analysis
- `GET /projects/{project_id}/analysis` - Get analysis results
- `GET /projects/{project_id}/impact` - Get impact analysis
- `POST /projects/{project_id}/change-plan` - Generate change plan

#### Jobs
- `GET /jobs/{job_id}` - Get job status
- `POST /jobs/{job_id}/cancel` - Cancel job

### 4.2 WebSocket Events

**Connection:** `wss://api.agenticspecbuilder.com/v1/ws`

**Client → Server:**
```json
{
  "type": "subscribe",
  "project_id": "uuid"
}
```

**Server → Client:**

```json
// Question ready
{
  "event": "question_ready",
  "project_id": "uuid",
  "question": {
    "question_id": "uuid",
    "text": "Who can create an account?",
    "options": [...],
    "format": "radio"
  }
}

// Artifact progress
{
  "event": "artifact_progress",
  "artifact_id": "uuid",
  "progress": 75,
  "status": "generating"
}

// Artifact complete
{
  "event": "artifact_complete",
  "artifact_id": "uuid",
  "download_urls": {...}
}

// Comment added
{
  "event": "comment_added",
  "artifact_id": "uuid",
  "comment": {...}
}

// Branch merged
{
  "event": "branch_merged",
  "branch_id": "uuid",
  "project_id": "uuid"
}

// Contradiction detected
{
  "event": "contradiction_detected",
  "decision_id": "uuid",
  "conflict": {...}
}
```

---

## 5. Technology Stack

### 5.1 Frontend

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | React | 18+ |
| Language | TypeScript | 5+ |
| Meta-framework | Next.js | 14+ |
| State Management | Zustand | 4+ |
| Data Fetching | TanStack Query | 5+ |
| Graph Visualization | D3.js / React Flow | 7+ / 11+ |
| Styling | Tailwind CSS | 3+ |
| UI Components | shadcn/ui | Latest |
| Forms | React Hook Form + Zod | 7+ / 3+ |
| WebSocket Client | Socket.io-client | 4+ |

### 5.2 Backend

| Component | Technology | Version |
|-----------|------------|---------|
| API Framework | FastAPI | 0.100+ |
| Language | Python | 3.11+ |
| ORM | SQLAlchemy 2.0 | 2.0+ |
| Database | PostgreSQL | 15+ |
| Vector DB | Pinecone/Weaviate/pgvector | Latest |
| Cache | Redis | 7+ |
| Message Queue | Celery + RabbitMQ | 5+ |
| LLM Clients | Anthropic SDK, OpenAI SDK | Latest |
| Authentication | Python-Jose | 3+ |
| Validation | Pydantic | 2.0+ |

### 5.3 Infrastructure

| Component | Technology |
|-----------|------------|
| Cloud Provider | AWS or GCP |
| Container | Docker |
| Orchestration | Kubernetes (EKS/GKE) |
| API Gateway | AWS API Gateway or Kong |
| CDN | CloudFront |
| File Storage | S3 or GCS |
| Email | SendGrid or AWS SES |
| Monitoring | Prometheus + Grafana |
| Logging | CloudWatch/Stackdriver |
| CI/CD | GitHub Actions |
| Secrets | AWS Secrets Manager |

---

## 6. Security Architecture

### 6.1 Authentication Flow

```
┌─────────┐     ┌─────────────┐     ┌────────────────┐     ┌─────────────┐
│  User   │────▶│   Client    │────▶│  API Gateway   │────▶│   Auth      │
│         │     │             │     │                │     │   Service   │
└─────────┘     └─────────────┘     └────────────────┘     └──────┬──────┘
                                                                    │
      ┌─────────────────────────────────────────────────────────────┘
      │                    JWT Token Generation
      │
      ▼
┌─────────────┐     ┌────────────────┐
│  Validate   │────▶│  Issue JWT     │
│  Creds      │     │  (7 days)     │
└─────────────┘     └────────────────┘
```

### 6.2 Authorization Model

```
┌─────────────────────────────────────────────────────────────────┐
│                        Request Flow                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Request ──▶ API Gateway ──▶ Auth Middleware ──▶ Permission    │
│                           │                      Check           │
│                           │                          │           │
│                           ▼                          ▼           │
│                    Validate JWT              Check Resource     │
│                           │                      Ownership       │
│                           │                          │           │
│                           ▼                          ▼           │
│                    Return 401 if           Return 403 if        │
│                    Invalid                 Unauthorized          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Security Measures

| Layer | Protection |
|-------|------------|
| Transport | TLS 1.3 for all connections |
| API | Rate limiting (per user + per IP), JWT validation |
| Application | Input validation with Pydantic, CSRF protection |
| Database | Parameterized queries, ORM with escaping, least privilege |
| Secrets | AWS Secrets Manager, environment variables |
| Sensitive Data | Auto-detect secrets, encrypt at rest, redact from logs |

---

## 7. Deployment Architecture

### 7.1 Production Environment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS / GCP Cloud                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        CDN (CloudFront)                              │    │
│  │                   (Static assets, API caching)                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    API Gateway / Load Balancer                      │    │
│  │              (SSL termination, Rate limiting, Auth)                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐          │
│         │                          │                          │          │
│         ▼                          ▼                          ▼          │
│  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐   │
│  │ Web Server │            │ Web Server  │            │ Web Server  │   │
│  │  (ECS/EKS) │            │  (ECS/EKS)  │            │  (ECS/EKS)  │   │
│  └──────┬──────┘            └──────┬──────┘            └──────┬──────┘   │
│         │                          │                          │          │
│         └──────────────────────────┼──────────────────────────┘          │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Internal Network (VPC)                           │  │
│  │                                                                     │  │
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │  │
│  │   │  PostgreSQL │   │    Redis    │   │   Vector Database   │   │  │
│  │   │   (Primary)  │   │   Cluster   │   │    (Pinecone)        │   │  │
│  │   │   + Replica  │   │             │   │                      │   │  │
│  │   └─────────────┘   └─────────────┘   └─────────────────────┘   │  │
│  │                                                                     │  │
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │  │
│  │   │    Celery    │   │   Worker    │   │   File Storage     │   │  │
│  │   │   (Queue)    │   │   Pool      │   │   (S3/GCS)          │   │  │
│  │   └─────────────┘   └─────────────┘   └─────────────────────┘   │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    External Services                               │  │
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │  │
│  │   │  Anthropic   │   │   OpenAI    │   │   GitHub/GitLab     │   │  │
│  │   │   (Claude)   │   │   (GPT-4)   │   │      API            │   │  │
│  │   └─────────────┘   └─────────────┘   └─────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Multi-Region Setup (Enterprise)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Global Traffic Management                            │
│                         (Route 53 / Cloud DNS)                               │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│   US Region    │    │   EU Region    │    │  Asia Region   │
│                │    │                │    │                │
│ - Primary DB   │    │ - Read Replica│    │ - Read Replica│
│ - All Services │    │ - All Services │    │ - All Services│
│ - Cache        │    │ - Cache         │    │ - Cache        │
└────────────────┘    └────────────────┘    └────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Synchronous Replica   │
                    │  (PostgreSQL + Redis)  │
                    └────────────────────────┘
```

---

## 8. Scalability Considerations

### 8.1 Horizontal Scaling Strategy

| Component | Scaling Approach |
|-----------|-----------------|
| Web Servers | Auto-scaling based on CPU (70% threshold), max 10 instances |
| Celery Workers | Queue depth-based scaling, max 20 workers |
| Database | Read replicas for read-heavy operations |
| Vector DB | Managed service with automatic scaling |
| Redis | Cluster mode for high availability |
| LLM API | Rate limiting + request queuing |

### 8.2 Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time (P95) | < 500ms |
| Question Generation | < 5s |
| Answer Validation | < 1s |
| Artifact Generation | < 30s (standard PRD) |
| Decision Graph Render | < 3s (1000 nodes) |
| Concurrent Users | 100 per workspace |
| Questions per Hour | 1000 per project |

### 8.3 Rate Limits (MVP)

| Action | Limit |
|--------|-------|
| Questions per day | 50 |
| Projects | 10 |
| Active conversations | 5 |
| Artifact generations per day | 10 |
| API requests per minute (per IP) | 100 |

---

## 9. Implementation Phases

### Phase 1: MVP (3-4 months)

**Goal:** Prove core value proposition

**Scope:**
- Greenfield mode only
- Simple question flow (templates, no dynamic reasoning)
- Generate: PRD, basic tickets (markdown)
- Single user per project (no collaboration)
- Email/password auth only
- Download exports only
- US-only hosting

**Deliverables:**
- Functional web application
- Interrogation Agent with template-based questions
- Specification Agent for PRD generation
- Basic authentication
- Project management

### Phase 2: Collaboration & Quality (2-3 months)

**Goal:** Enable teams, improve artifact quality

**Scope:**
- Workspaces & members
- Branching & merging
- Comments on artifacts
- Improved artifact generation
- Export to GitHub Issues, Linear
- Magic links auth
- Decision graph visualization
- Auto-archiving

### Phase 3: Brownfield & Enterprise (3-4 months)

**Goal:** Support legacy systems, attract enterprise

**Scope:**
- Brownfield mode (codebase ingestion)
- Multi-language support
- Impact analysis & test requirements
- SSO (Google Workspace, Okta)
- 2FA
- Multi-region data residency
- GDPR compliance
- Paid tier launch

### Phase 4: Scale & Intelligence (Ongoing)

**Goal:** Handle large projects, smarter agents

**Scope:**
- Dynamic question generation
- Enhanced context management
- Templates marketplace
- Self-hosted option
- Advanced observability
- Cost optimization

---

## 10. Key Architectural Decisions

### 10.1 Event-Driven vs. Synchronous

**Decision:** Hybrid approach

**Rationale:**
- Question answering and validation must be synchronous (< 1s)
- Artifact generation is inherently asynchronous (30-120s)
- Web updates toSocket for real-time maintain engagement
- Celery for background job processing

### 10.2 Database Choice

**Decision:** PostgreSQL as primary, Vector DB for embeddings

**Rationale:**
- PostgreSQL: ACID compliance, complex queries, mature ecosystem
- Vector DB: Efficient similarity search for RAG
- Redis: Session management, caching, job queue

### 10.3 LLM Strategy

**Decision:** Claude as primary, GPT-4 as fallback, open-source for cost optimization

**Rationale:**
- Claude: Best for reasoning, structured output
- GPT-4: Reliable fallback, good formatting
- Open-source: Cost-effective for simple transformations

### 10.4 Microservices vs. Monolith

**Decision:** Modular monolith with clear service boundaries

**Rationale:**
- Faster initial development
- Clear boundaries allow future decomposition
- Simpler deployment and operations
- Team can start with single deployable unit

---

## 11. Monitoring & Observability

### 11.1 Metrics

| Category | Metrics |
|----------|---------|
| System | CPU, Memory, Disk, Network |
| Application | Request rate, Error rate, Latency (P50, P95, P99) |
| Business | Questions asked, Artifacts generated, Projects created |
| LLM | Token usage, Cost per request, Provider uptime |

### 11.2 Logging

- Structured JSON logging
- Request IDs for tracing
- User IDs for audit
- Log levels: ERROR, WARNING, INFO, DEBUG
- Retention: 30 days (free), 1 year (paid), indefinite (enterprise)

### 11.3 Alerts

| Severity | Condition |
|----------|-----------|
| Critical | LLM provider down > 5 minutes |
| Critical | Database unavailable |
| Warning | Error rate > 5% |
| Warning | Queue depth > 1000 |
| Info | Rate limit approaching |

---

## 12. Disaster Recovery

### 12.1 Backup Strategy

| Data Type | Frequency | Retention |
|-----------|-----------|-----------|
| Database (full) | Daily | 30 days |
| Database (incremental) | Hourly | 7 days |
| File storage | Daily | 30 days |
| Config | On change | 90 days |

### 12.2 Recovery Procedures

1. **Database Failure:** Promote read replica to primary
2. **Application Failure:** Deploy previous version (blue/green)
3. **Region Failure:** DNS failover to secondary region
4. **Data Corruption:** Restore from backup + replay from audit log

### 12.3 RTO/RPO

- **Recovery Time Objective (RTO):** 1 hour
- **Recovery Point Objective (RPO):** 1 hour

---

## 13. Conclusion

This architecture provides a comprehensive blueprint for building the Agentic Spec Builder system. The design emphasizes:

1. **Scalability:** Horizontal scaling with managed services
2. **Reliability:** Multi-layer fault tolerance and graceful degradation
3. **Security:** Defense in depth with proper authentication and authorization
4. **Maintainability:** Clear component boundaries and modular design
5. **Observability:** Comprehensive monitoring and logging

The phased implementation approach allows for incremental delivery of value while managing risk and complexity.

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-12  
**Status:** Architecture Ready for Implementation