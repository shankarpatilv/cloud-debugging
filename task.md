# Take-Home Assignment: AWS Data Processing Service with LLM Ops Assistant

## Objective

Build a small cloud-based data processing service on AWS.

The system should:
1. Run on a **CPU-only AWS instance**
2. Have access to a **bundled or remote dataset**
3. Expose an **API** that accepts simple pandas processing requests
4. Track processing state and logs
5. Provide a local **LLM-powered tool** that summarizes system state and explains failures (a UI for this tool is optional)

The data processing service is intentionally simple — the core of this task is building the **LLM-powered debugging tool** that can quickly diagnose failures and summarize system state. The service exists to give the debugging tool something real to operate on.

The goal is to evaluate your ability to design and build a realistic system spanning cloud infrastructure, backend engineering, data processing, observability, and practical LLM integration.

---

## 1. AWS Deployment

Deploy the service on a CPU-only AWS instance so the API is reachable remotely.

### Requirements
- Deploy on EC2 (or another CPU-only AWS compute service)
- API must be reachable remotely
- Setup should be reproducible and documented

### Potential Tools
- EC2, Docker, S3, CloudWatch
- Any Python web framework (e.g. FastAPI)

You do **not** need production infra (e.g., Terraform), but clean setup is valued.

---

## 2. Dataset

The service must load a tabular dataset (CSV or Parquet) with at least a few thousand rows.

We provide an example dataset (`churn-bigml-full.xlsx`) that you can use, or you can bring your own. You can bundle it with the app, store it in S3, or download it on startup. Document the schema (columns + types) and where it lives.

Any tabular dataset works — transactions, logs, customer records, or synthetic data.

---

## 3. Processing API

Expose an API that lets users submit simple pandas processing jobs.

### Endpoints
- `POST /jobs` — submit a processing job
- `GET /jobs/{job_id}` — get job status and result
- `GET /jobs` — list all jobs
- `GET /health` — health check

### Supported Operations

Your API should accept a JSON job spec and apply **simple pandas operations** to the dataset. Support the following:

| Operation | Description | Example |
|-----------|-------------|---------|
| **filter** | Filter rows by a condition | `column == value`, `column > value` |
| **select** | Select a subset of columns | `["col_a", "col_b"]` |
| **groupby** | Group by column(s) and aggregate | `groupby("region").agg({"sales": "sum"})` |
| **sort** | Sort by column(s) | `sort_values("date", ascending=False)` |

That's it — just these four. You do **not** need to support arbitrary pandas expressions, derived columns, or complex transformations. Focus on clean API design and correct execution for these core operations.

### Job Behavior
- Each request creates a job with a unique ID
- Job status is tracked (`pending`, `running`, `completed`, `failed`)
- Results include a summary (e.g., row count, first N rows) — you do not need to return the full output dataset
- Async processing is a plus but not required

---

## 4. State Tracking and Logging

Track and expose operational state so the system is debuggable.

### Must Answer
- What jobs have run? Which are pending / running / completed / failed?
- What errors occurred and when?
- What dataset is loaded?

### Requirements
- Structured logs (not just print statements)
- Failure details captured

Use any lightweight storage: SQLite, JSON file, or in-memory with persisted logs.

---

## 5. LLM-Powered Ops Tool

Build a tool that uses an LLM to analyze system state and help debug issues.

### Capabilities
1. Summarize the current system state (jobs, errors, health)
2. Explain why a specific job failed
3. Surface patterns (e.g., repeated failures, stuck jobs)

### Example Queries
- "What is the system doing right now?"
- "Why did job 17 fail?"
- "What are recent errors?"

### How We'll Test It
We will send a bad API request that produces an error, then run your LLM debugging tool locally to see if it can quickly diagnose what went wrong. The tool should be able to pull logs/state from the remote service and produce a clear, useful explanation locally.

### Implementation
- Can be a CLI tool (`python debug.py`), an API endpoint (`POST /debug`), or a simple script
- Use real system data (logs, job states) — not raw log dumps
- Structure LLM inputs thoughtfully (this is what we're evaluating)

---

## Deliverables

### 1. Code Repository
- All source code, clearly structured

### 2. README
- Setup instructions
- How to deploy to AWS
- How to call the API (sample requests)
- How to use the LLM tool
- Architecture overview
- Key design decisions and tradeoffs

### 3. Example Usage
- Sample API requests and responses
- Example LLM debugging output

---

## Time Expectation

Target: 2–4 hours

We are not evaluating polish or completeness. Focus on clarity, correctness, and thoughtful design. If you have additional time, you're welcome to extend the system in any direction you find interesting.

You are welcome to use AI coding tools (e.g., Windsurf, Claude Code, Codex, Cursor, etc.). 

---


## Submission

Share a GitHub repo link and any deployment details (e.g., public endpoint if still running).