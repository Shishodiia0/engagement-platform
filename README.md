# User Engagement Analytics Platform

A scalable full-stack analytics platform that tracks user engagement events in real time, stores transactional data in PostgreSQL, and syncs it to Snowflake for analytical processing via an incremental ETL pipeline.

**Live Dashboard:** https://engagement-platform.streamlit.app
**API:** http://98.93.13.233
**API Docs:** http://98.93.13.233/docs

---

## Architecture

```
User Actions
     │
     ▼
FastAPI Backend ──────────────► PostgreSQL (Transactional DB)
     │                                      │
     │                              ETL Pipeline (Python)
     │                                      │
     │                                      ▼
     │                            Snowflake (Analytics DW)
     │                                      │
     ▼                                      ▼
JWT Auth                         Streamlit Dashboard (UI)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Operational Database | PostgreSQL |
| Data Warehouse | Snowflake |
| ETL Pipeline | Python + APScheduler |
| Dashboard | Streamlit + Plotly |
| Authentication | JWT + bcrypt |
| Rate Limiting | SlowAPI |
| Testing | Pytest + HTTPX |
| Deployment | AWS EC2 + Docker + Nginx |
| CI/CD | GitHub Actions |

---

## Key Features

- **OLTP/OLAP Separation** — PostgreSQL handles live traffic, Snowflake handles analytics
- **Incremental ETL** — Watermark strategy syncs only new records every 10 minutes
- **Zero Duplicates** — Snowflake MERGE prevents duplicate records across ETL runs
- **12 REST API Endpoints** — JWT secured with rate limiting (30 req/min)
- **49 Automated Tests** — 100% pass rate with SQLite in-memory test isolation
- **CI/CD Pipeline** — Tests run automatically on every push before deployment
- **Interactive Dashboard** — 5 pages with date range filters, CSV export, live event feed

---

## Benchmark Results

| Query | 1,500 events | 10,000 events | 100,000 events |
|---|---|---|---|
| Daily Active Users | 6.49 ms | 3.91 ms | 23.84 ms |
| Event Breakdown | 0.96 ms | 1.27 ms | 10.71 ms |
| Top Content | 0.59 ms | 1.36 ms | 11.50 ms |

DAU query degrades **3.67x** from small to large dataset — validating OLTP/OLAP separation.

---

## Project Structure

```
engagement_platform/
├── backend/
│   ├── auth/utils.py
│   ├── routes/
│   ├── config.py
│   ├── database.py
│   └── main.py
├── etl/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── audit.py
│   └── scheduler.py
├── snowflake/schema.sql
├── dashboard/
│   ├── app.py
│   └── views/
├── tests/
├── Dockerfile.backend
├── Dockerfile.etl
├── docker-compose.yml
├── nginx.conf
└── .github/workflows/deploy.yml
```

---

## Setup & Installation

### 1. Clone and create virtual environment
```bash
git clone https://github.com/Shishodiia0/engagement-platform.git
cd engagement-platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables
Fill in `.env`:
```
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=engagement_db
PG_USER=postgres
PG_PASSWORD=your_password

SF_ACCOUNT=your_snowflake_account
SF_USER=your_snowflake_user
SF_PASSWORD=your_snowflake_password
SF_WAREHOUSE=COMPUTE_WH
SF_DATABASE=ANALYTICS_DB
SF_SCHEMA=PUBLIC

JWT_SECRET=your_secret_key
JWT_EXPIRY_MINUTES=60
ETL_INTERVAL_MINUTES=10
```

### 3. Run Snowflake schema
Run `snowflake/schema.sql` in your Snowflake worksheet.

### 4. Insert demo data
```bash
python seed.py
```

---

## Running Locally

```bash
# Terminal 1 - Backend
uvicorn backend.main:app --reload

# Terminal 2 - ETL
python -m etl.scheduler

# Terminal 3 - Dashboard
streamlit run dashboard/app.py
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

**49 tests | 100% pass rate**

---

## Running with Docker

```bash
docker-compose up -d --build
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login, get JWT |
| GET | `/users/me` | Get profile |
| POST | `/content/create` | Create content |
| POST | `/events/track` | Track event (rate limited) |
| GET | `/events/recent` | Live event feed |
| GET | `/analytics/dau` | Daily active users |
| GET | `/analytics/event-breakdown` | Event type counts |
| GET | `/analytics/top-content` | Top 10 content |
| GET | `/analytics/user-growth` | User growth |
| GET | `/analytics/etl-status` | ETL status |
| POST | `/etl/trigger` | Manual ETL sync |

---

## Demo Login
```
Email:    alice@example.com
Password: password123
```
