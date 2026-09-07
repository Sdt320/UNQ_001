# FieldMind AI — Autonomous Multi-Agent Field Workforce Marketplace

FieldMind AI is a production-grade, multi-agent on-demand home repair and field operations dispatching platform. It automates the entire lifecycle of emergency home repairs (plumbing, electrical, AC repair, carpentry, masonry)—from multimodal voice/text customer intake, PostGIS proximity matchmaking, and WhatsApp interactive dispatch, to Redis atomic mutex locks, Stripe escrow pre-authorizations, vision-based photo audits, and ReportLab PDF invoicing.

---

## 🏗️ System Architecture & Workflow

```
                   +-----------------------------------------------+
                   |           CUSTOMER INTAKE (VOICE/TEXT)        |
                   |      (WhatsApp Audio / Web Portal Modal)      |
                   +-----------------------+-----------------------+
                                           |
                                           v
                   +-----------------------------------------------+
                   |           1. INTAKE & INTENT AGENT            |
                   |       (Whisper API + GPT-4o-mini Schema)      |
                   +-----------------------+-----------------------+
                                           |
                                           v
                   +-----------------------------------------------+
                   |          2. SPATIAL MATCHMAKER AGENT          |
                   |  (PostGIS ST_DWithin 10km Proximity Filtering) |
                   +-----------------------+-----------------------+
                                           |
                                           v
                   +-----------------------------------------------+
                   |              3. DISPATCH AGENT                |
                   |     (WhatsApp Interactive Reply Buttons)      |
                   +-----------------------+-----------------------+
                                           |
                          +----------------+----------------+
                          |                                 |
                          v                                 v
              [Technician Taps Accept]            [180s Expired / Declines]
                          |                                 |
                          v                                 v
        +-----------------------------------+    +--------------------+
        |    REDIS SETNX ATOMIC MUTEX       |    |  DYNAMIC FALLBACK  |
        | lock:job_claim:{id} {officer} 15s |    |  (Expands to 20km) |
        +-----------------+-----------------+    +---------+----------+
                          |                                |
                +---------+---------+                      +--> (Loop to 2)
                |                   |
           [Lock Won]          [Lock Lost]
                |                   |
                v                   v
+-------------------------------+ +--------------------------------+
|     4. ESCROW PRE-AUTH        | | WhatsApp: "Job Already Claimed"|
| (Stripe Manual Capture Hold)  | +--------------------------------+
+---------------+---------------+
                |
                v
+-------------------------------+
|      5. DISPATCH & GPS        |
|  (WhatsApp Location Pin Sent) |
+---------------+---------------+
                |
                v
+-------------------------------+
|   6. CLOSURE & VISION AUDIT   |
|   (Photo Verification Check)  |
+---------------+---------------+
                |
                v
+-------------------------------+
|    7. SETTLEMENT & INVOICE    |
| (85% Officer / 15% Platform)  |
| (ReportLab Dynamic PDF Sent)  |
+---------------+---------------+
                |
                v
+-------------------------------+
|   8. CELERY MONTH-END AUDIT   |
| (100-Job / 4.5+ Rating Bonus) |
+-------------------------------+
```

---

## 👥 6-Member Engineering Team Role Matrix & Allocation

| Member & Role | Primary Specialization | Core Responsibilities & Modules | Assigned Epics / Stories |
| :--- | :--- | :--- | :--- |
| **Member 1: AI Systems Architect & Tech Lead** | LangGraph, LLM Models, System Design | Multi-agent state graph orchestration, Pydantic schemas, Whisper audio ingestion, GPT-4o-mini intent parsing, vision verification model, code reviews. | `FM-EPIC-2` (FM-201, FM-202), `FM-EPIC-3` (FM-302), `FM-EPIC-5` (FM-502) |
| **Member 2: Senior Backend Engineer (Data/Geo)** | PostGIS, PostgreSQL, Redis, Concurrency | PostgreSQL + PostGIS database DDL & migrations, `ST_DWithin` spatial distance queries, atomic Redis SETNX distributed locking, Celery crontab setup. | `FM-EPIC-1` (FM-101), `FM-EPIC-3` (FM-301), `FM-EPIC-4` (FM-402), `FM-EPIC-6` (FM-602) |
| **Member 3: Senior Backend Engineer (Integrations)** | FastAPI, Webhooks, Payments, External APIs | WhatsApp Meta Cloud API webhooks & interactive template senders, Stripe Connect escrow manual holds & 85/15 payout split transfers, ReportLab PDF generation. | `FM-EPIC-1` (FM-102), `FM-EPIC-4` (FM-401), `FM-EPIC-5` (FM-501) |
| **Member 4: Frontend Engineer (React/UI)** | React (Vite), Tailwind CSS, UI/UX | Admin Operations Dashboard (pending worker approvals, 100-job reward leaderboard, live agent tracker), Worker registration onboarding, Customer intake UI. | `FM-EPIC-6` (FM-601) |
| **Member 5: QA & Test Automation Engineer** | Pytest, Concurrency Simulation, Locust | Step-by-step test suites (`test_step1` to `test_step6`), 50-worker concurrent claim simulation, geospatial accuracy validation (<0.5% margin). | Step-by-Step Test Protocol (1-6) |
| **Member 6: DevOps & Cloud Infrastructure Engineer** | Docker, Kubernetes, AWS/MinIO, CI/CD | Docker Compose orchestration, PostgreSQL/PostGIS container tuning, Redis caching, MinIO / S3 invoice storage, environment configs. | Infrastructure & Docker Deployment |

---

## 📅 12-Week / 6-Sprint Production Roadmap (Jira)

```
Sprint 1 (W1-W2)  : [FM-101] DB Schema & Auth | [FM-301] PostGIS Spatial Function
Sprint 2 (W3-W4)  : [FM-201] Whisper Transcription | [FM-202] Pydantic Parser | [FM-302] Dynamic Loop
Sprint 3 (W5-W6)  : [FM-401] WhatsApp Cloud API | [FM-402] Redis Mutex Lock | [FM-102] Admin Endpoint
Sprint 4 (W7-W8)  : [FM-501] Stripe Connect Escrow | [FM-502] Vision Proof & PDF Invoicing
Sprint 5 (W9-W10) : [FM-601] React Admin Console | [FM-602] Celery Monthly Reward Task
Sprint 6 (W11-W12): Automated Stress Testing (50-Pro Race Conditions), Security & Production Go-Live
```

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.11+ / 3.12+ / 3.13+
- Node.js 18+ and npm
- Docker and Docker Compose (optional for local running)

### Option A: Running with Docker Compose
```bash
# Clone the repository
git clone <repo-url>
cd UNQ_001

# Copy environment template
cp .env.example .env

# Build and start all services (PostGIS, Redis, Backend, Celery, Frontend)
docker-compose up --build
```
- **Backend Swagger UI**: `http://localhost:8000/docs`
- **Frontend Dashboard**: `http://localhost:5173`

### Option B: Local Development Setup

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Step-by-Step Test Suite

The test suite validates the system following the 6-phase test protocol:

```bash
# Run full suite
pytest backend/tests -v

# Or run step-by-step:
# Step 1: Database schema, connection pool & geodesic distance accuracy (<0.5% margin)
pytest backend/tests/test_step1_database.py -v

# Step 2: Spatial matchmaking (ST_DWithin 10km radius & rating sorting)
pytest backend/tests/test_step2_matchmaking.py -v

# Step 3: Multimodal audio transcription & Pydantic structured intent parsing
pytest backend/tests/test_step3_intent.py -v

# Step 4: LangGraph multi-agent flow, dispatch broadcasting & pause/interrupt states
pytest backend/tests/test_step4_agent_flow.py -v

# Step 5: Concurrency race condition test (50 concurrent claims -> exactly 1 lock winner)
pytest backend/tests/test_step5_webhook_locks.py -v

# Step 6: Stripe escrow hold, photo vision verification & ReportLab PDF invoice generation (85/15 split)
pytest backend/tests/test_step6_payments.py -v
```

---

## 📡 API Endpoint Overview

| Method | Endpoint | Description | Auth / Guard |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/customer` | Customer registration | Public |
| `POST` | `/api/v1/auth/register/employee` | Field officer registration (pending approval) | Public |
| `POST` | `/api/v1/auth/login` | OAuth2 / JWT login with RBAC claims | Public |
| `GET` | `/api/v1/admin/pending-workers` | List unapproved worker applications | ADMIN Role |
| `PATCH`| `/api/v1/admin/approve-worker/{user_id}`| Approve technician for active dispatch | ADMIN Role |
| `POST` | `/api/v1/requests/create` | Submit customer repair request (text/audio) | CUSTOMER Role |
| `GET` | `/api/v1/requests/{job_id}` | Retrieve request lifecycle status & state | Authenticated |
| `GET` | `/webhooks/whatsapp` | Meta challenge verification handshake | Public / Token |
| `POST` | `/webhooks/whatsapp` | Process interactive button responses (`ACCEPT_{id}`) | Public / Meta |
| `POST` | `/api/v1/payments/escrow-hold` | Authorize pre-auth hold on customer card | Internal / Admin |
| `POST` | `/api/v1/payments/release-payout` | Release escrow funds with 85/15 split | Internal / Admin |
| `GET` | `/api/v1/rewards/leaderboard` | Top performers & 100-job bonus leaderboard | Authenticated |
| `POST` | `/api/v1/rewards/reviews` | Submit post-service customer rating & feedback | CUSTOMER Role |

---

## 🔒 Security & Concurrency Design
- **Atomic Mutex**: Redis distributed key `lock:job_claim:{job_id}` using `SETNX` with 15s TTL prevents double-booking across thousands of concurrent webhook callbacks.
- **State Checkpointing**: LangGraph utilizes persistence checkpoints to pause during technician dispatch and cleanly resume upon webhook delivery.
- **PCI-DSS Compliance**: No raw credit cards stored on server; Stripe pre-authorization holds and transfers handle financial compliance.
