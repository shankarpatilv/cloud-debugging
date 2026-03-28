# CLAUDE.md - Cloud Debugging Task Project

This file provides guidance to Claude Code when working with this take-home assignment.

## WHY - Purpose & Goals

Building an AWS data processing service with an LLM-powered debugging tool for a take-home assignment. The service processes pandas operations on a dataset, while the debug tool uses LLM to analyze failures.

## WHAT - Tech Stack & Architecture

### Service (Deployed to EC2)

- **API**: FastAPI with synchronous processing
- **Database**: SQLite for job metadata (NOT the CSV data)
- **Data**: CSV file (5000 rows) processed with pandas
- **Logging**: JSON structured logs
- **Container**: Docker on AWS EC2

### Debug Tool (Runs Locally)

- **CLI**: Python with argparse
- **LLM**: OpenAI GPT-3.5/4 or Claude API
- **Parser**: Rule-based query parsing
- **Communication**: HTTP REST to EC2 API

## HOW - Development Workflow

### Quick Start Commands

```bash
# Service setup
cd service
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload

# Debug tool setup
cd debug_tool
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
python debug.py "What is the system doing?"

# Docker local test
docker-compose up

# Deploy to EC2
./deployment/deploy.sh
```

### Project Structure

```
cloud-debugging-task/
├── service/            # FastAPI service (goes to EC2)
├── debug_tool/         # LLM tool (runs locally)
├── deployment/         # Docker & AWS scripts
├── examples/           # Test scenarios
└── memories/           # Session context & plans
```

### Key Files

- **Task Plan**: `memories/detailed_tasks_plan.md`
- **Session Context**: `memories/session_2026-03-26_12-30.md`
- **Dataset**: `churn-bigml-full.xlsx` (needs conversion)

## Current Focus & Tasks

### Phase 1: Setup (CURRENT)

- [ ] Create project structure
- [ ] Convert Excel to CSV
- [ ] Initialize git repo

### Phase 2: API Service

- [ ] FastAPI with 4 endpoints
- [ ] SQLite for job tracking
- [ ] Pandas operations (filter, select, groupby, sort)
- [ ] JSON structured logging

### Phase 3: Debug Tool

- [ ] Rule-based query parser
- [ ] State collector (HTTP client)
- [ ] LLM analyzer with context
- [ ] CLI interface

### Phase 4: Deployment

- [ ] Dockerize service
- [ ] Deploy to EC2
- [ ] Test remote debugging

## Key Architecture Decisions

### Data Storage

- **SQLite**: Stores job metadata only (id, status, params, errors)
- **CSV**: The actual dataset, loaded once at startup
- **Results**: Only summaries stored (row count + 10 row preview)

### Query Handling

```
User: "Why did job 123 fail?"
  ↓
Parser: {type: 'job_failure', params: {job_id: '123'}}
  ↓
Collector: GET /jobs/123 from EC2
  ↓
Context: Add dataset schema
  ↓
LLM: Analyze with full context
```

### Error Scenarios to Test

1. Wrong column names (`total_minutes` vs `Total day minutes`)
2. Invalid operations
3. Type mismatches
4. Missing parameters

## Important Constraints

- **Focus**: LLM debugging quality (main evaluation point)
- **Simplicity**: No auth, no caching initially, sync processing OK
- **Required Queries**:
  - "What is the system doing right now?"
  - "Why did job X fail?"
  - "What are recent errors?"

## Development Agents

**"Use the orchestrator agent"** - Main coordinator for complex tasks
- Analyzes requirements and delegates to specialized agents
- Example: "Use the orchestrator agent to build the complete API service"

**Specialized Agents:**
- **api-developer**: FastAPI, SQLite, pandas operations
- **debug-tool-developer**: CLI, LLM integration, query parsing  
- **devops-engineer**: Docker, AWS deployment, infrastructure
- **test-engineer**: Test scenarios, failure cases, validation
- **documentation-writer**: README, API docs, usage examples

**Direct Usage Examples:**
- "Use the api-developer agent to implement job processing"
- "Use the debug-tool-developer agent to create the query parser"
- "Use the test-engineer agent to create failure scenarios"
- "Use the devops-engineer agent to dockerize the service"

## Memory Triggers

**"check memories"**

- Read all files in `memories/` folder
- Summarize project status

**"save memories"**

- Save to `memories/session_YYYY-MM-DD_HH-MM.md`
- Update task progress
- Note decisions made

## Testing Approach

They will:

1. Send bad API request (wrong column name)
2. Run debug tool locally
3. Check if it correctly diagnoses the issue

Make sure the LLM can explain:

- What went wrong
- Why it failed (column name mismatch)
- How to fix it (correct column name)
