# Cloud Debugging Task - Data Processing Service with LLM-Powered Debugging

A production-ready AWS data processing service with an intelligent debugging tool that uses LLMs to diagnose failures and provide actionable insights.

## 🎯 Project Overview

This system consists of two main components:

1. **FastAPI Data Processing Service** - Deployed on AWS EC2, processes pandas operations on customer churn dataset
2. **LLM-Powered Debug Tool** - Local CLI tool that queries the EC2 service and uses AI to analyze system state and diagnose issues

The primary use case is **intelligent error diagnosis**.

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Setup Instructions](#setup-instructions)
- [How to Deploy to AWS](#how-to-deploy-to-aws)
- [API Documentation](#api-documentation)
- [Debug Tool Usage](#debug-tool-usage)
- [Key Design Decisions](#key-design-decisions)

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                          AWS EC2 Instance                       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   FastAPI Service (Port 8000)           │    │
│  │                                                         │    │
│  │  ┌──────────┐  ┌──────────────┐  ┌─────────────────┐    │    │
│  │  │   API    │→ │Job Processor │→ │ Pandas Ops      │    │    │
│  │  │ Routes   │  │              │  │ (Filter,Select, │    │    │
│  │  │          │  │              │  │  Groupby,Sort)  │    │    │
│  │  └──────────┘  └──────────────┘  └─────────────────┘    │    │
│  │       ↓              ↓                    ↓             │    │
│  │  ┌──────────────────────────────────────────────────┐   │    │
│  │  │           Structured Logging System              │   │    │
│  │  │  ┌────────┐  ┌────────┐  ┌──────────────────┐  │     │    │
│  │  │  │SQLite  │  │ JSON   │  │ CloudWatch       │  │     │    │
│  │  │  │Storage │  │ Files  │  │ (Optional)       │  │     │    │
│  │  │  └────────┘  └────────┘  └──────────────────┘  │     │    │
│  │  └──────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │  Dataset: churn-bigml-full.csv (3,333 rows, 21 cols)    │    │
│  └─────────────────────────────────────────────────────────┘
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                               ↑ HTTP
                               │
┌─────────────────────────────────────────────────────────────────┐
│                     Local Machine (Debug Tool)                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                      CLI Debug Tool                      │    │
│  │                                                          │    │
│  │  User Query → Parser → State Collector → Context Builder │    │
│  │                              ↓                           │    │
│  │                    LLM Analyzer (OpenAI/Claude)          │    │
│  │                              ↓                           │    │
│  │                    Formatted Response                    │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### API Service Flow

```
HTTP Request → FastAPI Router → Operation Handler → Job Processor
                                        ↓
                                  Background Task
                                        ↓
                            ┌──────────────────────┐
                            │   Load DataFrame     │
                            │         ↓            │
                            │   Apply Operation    │
                            │  (filter/select/     │
                            │   groupby/sort)      │
                            │         ↓            │
                            │   Store Result/Error │
                            └──────────────────────┘
                                        ↓
                              Structured Logging
                                    ↓     ↓     ↓
                              SQLite  JSON  CloudWatch
```

### Debug Tool Flow

```
User Query: "Why did job X fail?"
                ↓
┌──────────────────────────────┐
│      Query Parser            │
│  - Extract job ID            │
│  - Identify query type       │
└──────────────────────────────┘
                ↓
┌──────────────────────────────┐
│      State Collector         │
│  - GET /jobs/{job_id}        │
│  - GET /logs/timeline/{id}   │
│  - GET /logs/structured      │
└──────────────────────────────┘
                ↓
┌──────────────────────────────┐
│      Context Builder         │
│  - Add dataset schema        │
│  - Add error details         │
│  - Add system knowledge      │
└──────────────────────────────┘
                ↓
┌──────────────────────────────┐
│      LLM Analyzer            │
│  - OpenAI GPT-3.5/4          │
│  - Specialized prompts       │
└──────────────────────────────┘
                ↓
    "The job failed because the column
     'total_day_minutes' doesn't exist.
     Use 'Total day minutes' instead."
```

### Data Flow for Error Diagnosis

```
1. Client sends request with wrong column name
   POST /jobs {"operation": "filter", "params": {"column": "total_day_minutes"}}
                                                            ↑ (incorrect: uses underscore)

2. Service attempts operation
   pandas.DataFrame → KeyError: 'total_day_minutes' not in columns

3. Error logged with structured context
   {
     "log_type": "job_event",
     "level": "ERROR",
     "job_id": "abc-123",
     "error_type": "KeyError",
     "message": "Column 'total_day_minutes' not found",
     "details": {
       "requested_column": "total_day_minutes",
       "available_columns": ["Total day minutes", "Total day calls", ...]
     }
   }

4. Debug tool queries failure
   $ python debug.py "why did job abc-123 fail?"

5. State collector fetches context
   GET /jobs/abc-123 → Job details
   GET /logs/timeline/abc-123 → Event sequence
   GET /logs/structured?job_id=abc-123 → Detailed logs

6. LLM analyzes with schema knowledge
   Context: Error shows 'total_day_minutes' but schema has 'Total day minutes'
   Analysis: Column name mismatch - use spaces instead of underscores

7. User receives actionable fix
   "The job failed because the column name 'total_day_minutes' doesn't exist.
    The correct column name is 'Total day minutes' (with spaces, not underscores).
    Fix: {"column": "Total day minutes"}"
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- AWS Account (for deployment)
- OpenAI API Key or Claude API Key

### Local Development Setup

#### 1. Clone the repository

```bash
git clone https://github.com/shankarpatilv/cloud-debugging.git
cd cloud-debugging-task
```

#### 2. Set up the API Service

```bash
cd service
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the service
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Set up the Debug Tool

```bash
# In a new terminal
cd debug_tool
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export EC2_HOST=<your-ec2-host>
export OPENAI_API_KEY="sk-your-api-key"
export API_URL="http://$EC2_HOST:8000"

# Test the tool
python3 debug.py "what is the system doing?"
```

### Environment Variables

#### Service Configuration

```bash
# Logging
export LOG_LEVEL="INFO"
export LOG_PATH="logs/app.log"

# CloudWatch (optional/Future Enchancement)
export ENABLE_CLOUDWATCH="true"
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

#### Debug Tool Configuration

```bash
# Required
export OPENAI_API_KEY="sk-your-openai-key"

# Optional (defaults shown)
export API_URL="http://localhost:8000"
export DEFAULT_MODEL="gpt-3.5-turbo"
```

### Docker Setup

#### Build and run with Docker Compose

```bash
# Development environment
docker-compose -f deployment/docker-compose.yml up --build

# Production environment
docker-compose -f deployment/docker-compose.prod.yml up -d --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## ☁️ How to Deploy to AWS

### Prerequisites

- AWS EC2 instance (Ubuntu 22.04 LTS)
- Security group allowing port 8000
- SSH key pair for access

### Deployment Script

```bash
# Set environment variables
export EC2_HOST="ec2-XX-XX-XX-XX.compute-1.amazonaws.com"
export AWS_KEY_PATH="~/.ssh/your-key.pem"

# Deploy using the automated script
./deployment/deploy.sh

# The script will:
# 1. SSH into EC2 instance
# 2. Install Docker and dependencies
# 3. Copy application files
# 4. Build and run containers
# 5. Verify health check
```

### Manual Deployment (if automated script fails)

```bash
# [To be customized based on your AWS setup]
# Basic steps:
# 1. SSH into EC2: ssh -i $AWS_KEY_PATH ubuntu@$EC2_HOST
# 2. Install Docker: sudo apt update && sudo apt install docker.io docker-compose
# 3. Clone repo: git clone https://github.com/shankarpatilv/cloud-debugging.git
# 4. Run: cd cloud-debugging-task && docker-compose -f deployment/docker-compose.prod.yml up -d
```

## 📡 API Documentation

### Base URL

- Local: `http://localhost:8000`
- Production: `http://your-ec2-host:8000`

### Core Endpoints

#### Health Check

- `GET /health` - System health status

#### Job Management

- `POST /jobs` - Submit new processing job
- `GET /jobs/{job_id}` - Get job status and results
- `GET /jobs` - List all jobs

#### Logging & Monitoring

- `GET /logs/structured` - Query structured logs with filtering
- `GET /logs/metrics` - Get system performance metrics
- `GET /logs/errors` - Get error summary
- `GET /logs/timeline/{job_id}` - Get job event timeline

### Supported Operations

#### 1. Filter

```json
{
	"operation": "filter",
	"params": {
		"column": "State",
		"operator": "==", // Options: ==, !=, >, <, >=, <=
		"value": "CA"
	}
}
```

#### 2. Select

```json
{
	"operation": "select",
	"params": {
		"columns": ["customer_id", "State", "Total day minutes"]
	}
}
```

#### 3. Groupby

```json
{
	"operation": "groupby",
	"params": {
		"column": "State",
		"agg_func": "mean", // Options: count, mean, sum, min, max
		"agg_column": "Total day minutes" // Optional
	}
}
```

#### 4. Sort

```json
{
	"operation": "sort",
	"params": {
		"column": "Total day charge",
		"ascending": false
	}
}
```

## 🔍 Debug Tool Usage

### Query Types

The debug tool accepts natural language queries to analyze system issues:

| Query Type    | Example Questions             | Purpose                         |
| ------------- | ----------------------------- | ------------------------------- |
| System Status | "What is the system doing?"   | Overview of health and activity |
| Job Status    | "Tell me about job X"         | Specific job details            |
| Job Failure   | "Why did job X fail?"         | Root cause analysis             |
| Recent Errors | "What errors occurred today?" | Error pattern analysis          |

### Basic Usage

```bash
# Check system status
python3 debug.py "what is the system doing?"

# Analyze a specific job failure
python3 debug.py "why did job abc-123 fail?"

# Review recent errors
python3 debug.py "what are the recent errors?"

```

### 📚 Full API and Debug Tool Examples with LLM Responses

For detailed examples and actual LLM outputs, see **[USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md)**

## 🎯 Key Design Decisions and Tradeoffs

### 1. Architecture Decisions

#### FastAPI for the Service

**Decision**: Use FastAPI instead of Flask/Django

- **Pros**: Simpler, lightweight
- **Cons**: Smaller ecosystem than Flask/Django

#### In-Memory DataFrame

**Decision**: Load entire dataset in memory at startup

- **Pros**: Fast operations, no disk I/O during processing
- **Cons**: Memory usage, not scalable to large datasets
- **Rationale**: Dataset is small (3333 rows), prioritizes performance for demo

#### SQLite for Job Storage

**Decision**: Use SQLite instead of PostgreSQL/MongoDB

- **Pros**: Zero configuration, embedded, perfect for single-instance
- **Cons**: Not suitable for multi-instance deployment
- **Rationale**: Simplicity for take-home assignment, easy deployment

### 2. Debug Tool Design

#### Rule-Based Query Parsing

**Decision**: Combine rule-based parsing with LLM analysis

- **Pros**: Predictable routing, lower LLM costs, faster response
- **Cons**: Limited to predefined query types
- **Rationale**: Most debugging queries fall into clear categories

#### Comprehensive Context Building

**Decision**: Fetch extensive context before LLM analysis

- **Pros**: Better diagnosis accuracy, complete picture
- **Cons**: More API calls, slightly slower
- **Rationale**: Accuracy is paramount for debugging

### 3. Error Handling Philosophy

#### Detailed Error Context

**Decision**: Capture extensive context on every error

- **Pros**: Excellent debuggability, LLM has full context
- **Cons**: Storage overhead
- **Rationale**: Core value proposition is debugging capability

## 📈 Performance Considerations

- **Dataset Loading**: ~50ms for 3333 rows
- **Operation Execution**: <100ms for most operations
- **LLM Analysis**: 2-3 seconds including API call

## ⚠️ Known Limitations & Future Enhancements

### Current Limitations

1. **CloudWatch Integration Not Active**
   - CloudWatch logger is not initialized in the current implementation
   - Logs are stored locally in SQLite and JSON files only
   - AWS credentials configuration is prepared but not connected

2. **Limited Logging Granularity**
   - Logs capture main events (job created, started, completed, failed)
   - Missing detailed intermediate processing steps
   - No debug-level logging for troubleshooting complex issues

### Proposed Enhancements (Time Permitting)

If additional development time were available, the following enhancements would significantly improve the system:

#### 1. Enhanced CloudWatch Integration

```python
# Initialize CloudWatch logger with proper credentials
if os.getenv('ENABLE_CLOUDWATCH') == 'true':
    cloudwatch = CloudWatchLogger(
        region=os.getenv('AWS_REGION'),
        log_group='/aws/ec2/cloud-debugging-service',
        log_stream=f"instance-{instance_id}"
    )
```

#### 2. Comprehensive Logging Strategy

- **Pre-operation logging**: Log parameters before validation
- **Step-by-step tracking**: Log each stage of data transformation
- **Performance metrics**: Log execution time for each operation

#### 3. Metrics Collection

- Implement Prometheus metrics for monitoring
- Add custom CloudWatch metrics for business KPIs
- Create dashboards for real-time system health

### Impact of Current Limitations

While the system successfully demonstrates the core functionality of LLM-powered debugging:

- The debug tool can still diagnose errors effectively
- Job processing and error capture work correctly
- The LLM receives sufficient context for basic troubleshooting

However, for production use, the enhanced logging would provide:

- Better observability for DevOps teams
- Faster root cause analysis for complex issues
- Performance optimization insights
- Compliance with enterprise logging standards

---

**Focus**: Demonstrating cloud deployment, data processing, and AI-powered debugging capabilities  
**Note**: This implementation prioritizes core LLM debugging functionality over comprehensive logging infrastructure due to time constraints
