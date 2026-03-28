# Usage Examples & Sample Responses

This document provides detailed examples of API requests, responses, and debug tool outputs.

## 📡 API Request Examples

### Health Check

**Request:**

```bash
curl -X GET "http://$EC2_HOST:8000/health"
```

**Response:**

```json
{
	"status": "healthy",
	"database": true,
	"dataset_loaded": true,
	"dataset_rows": 3333,
	"uptime_seconds": 42.254227
}
```

### Submit Job - Filter Operation

**Request:**

```bash
curl -X POST "http://$EC2_HOST:8000/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "filter",
    "params": {
      "column": "State",
      "operator": "==",
      "value": "CA"
    }
  }'
```

**Response:**

```json
{
	"job_id": "2776f4ec-275a-451b-a6ef-6c9ff4531dce",
	"status": "pending",
	"message": "Job submitted successfully"
}
```

### Submit Job - Select Operation

**Request:**

```bash
curl -X POST "http://$EC2_HOST:8000/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "select",
    "params": {
      "columns": ["customer_id", "State", "Total day minutes"]
    }
  }'
```

**Response:**

```json
{
	"job_id": "a208f1f0-e6fe-463d-b49a-d57dd311f528",
	"status": "pending",
	"message": "Job submitted successfully"
}
```

### Submit Job - Groupby Operation

**Request:**

```bash
curl -X POST "http://$EC2_HOST:8000/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "groupby",
    "params": {
      "column": "State",
      "agg_func": "mean",
      "agg_column": "Total day minutes"
    }
  }'
```

**Response:**

```json
{
	"job_id": "55dc211a-6daf-42ce-a94f-c2a330c6d627",
	"status": "pending",
	"message": "Job submitted successfully"
}
```

### Get Job Status - Success Case

**Request:**

```bash
curl -X GET "http://$EC2_HOST:8000/jobs/2776f4ec-275a-451b-a6ef-6c9ff4531dce"
```

**Response:**

```json
{
  "id": "2776f4ec-275a-451b-a6ef-6c9ff4531dce",
  "operation": "filter",
  "params": {
    "column": "State",
    "operator": "==",
    "value": "CA"
  },
  "status": "completed",
  "result": {
    "success": true,
    "row_count": 34,
    "columns": [
      "customer_id",
      "State",
      ...
    ],
    "shape": [
      34,
      21
    ],
    "preview": [
        {
        ...
        },
        {
          ...
        }

    ]
  },
  "error": null,
  "created_at": "2026-03-28T00:47:47.823730",
  "updated_at": "2026-03-28T00:47:47.896660",
  "completed_at": "2026-03-28T00:47:47.896670"
}
```

### Get Job Status - Failure Case

**Request:**

```bash
 curl -X GET "http://$EC2_HOST:8000/jobs/55dc211a-6daf-42ce-a94f-c2a330c6d627"
```

**Response:**

```json
{
	"id": "55dc211a-6daf-42ce-a94f-c2a330c6d627",
	"operation": "groupby",
	"params": {
		"column": "State",
		"agg_func": "mean",
		"agg_column": "Total day minutes"
	},
	"status": "failed",
	"result": null,
	"error": {
		"success": false,
		"error": "Groupby requires 'by' parameter",
		"error_type": "ValueError",
		"message": "Operation failed: Groupby requires 'by' parameter"
	},
	"created_at": "2026-03-28T00:48:35.664331",
	"updated_at": "2026-03-28T00:48:35.689100",
	"completed_at": "2026-03-28T00:48:35.689112"
}
```

### Get Structured Logs

**Request:**

```bash
curl -X GET "http://$EC2_HOST:8000/logs/structured?job_id=55dc211a-6daf-42ce-a94f-c2a330c6d627&hours=24&limit=100"
```

**Response:**

```json
{
	"count": 3,
	"filters": {
		"job_id": "55dc211a-6daf-42ce-a94f-c2a330c6d627",
		"log_type": null,
		"level": null,
		"hours": 24
	},
	"logs": [
		{
			"id": 21,
			"timestamp": "2026-03-28 00:48:35",
			"log_type": "job_event",
			"level": "INFO",
			"event": "job_created",
			"job_id": "55dc211a-6daf-42ce-a94f-c2a330c6d627",
			"operation": "groupby",
			"status": "pending",
			"error_type": null,
			"message": null,
			"details": {
				"params": {
					"column": "State",
					"agg_func": "mean",
					"agg_column": "Total day minutes"
				}
			},
			"duration_ms": null
		},
		{
			"id": 22,
			"timestamp": "2026-03-28 00:48:35",
			"log_type": "job_event",
			"level": "INFO",
			"event": "job_started",
			"job_id": "55dc211a-6daf-42ce-a94f-c2a330c6d627",
			"operation": "groupby",
			"status": null,
			"error_type": null,
			"message": null,
			"details": {
				"params": {
					"column": "State",
					"agg_func": "mean",
					"agg_column": "Total day minutes"
				}
			},
			"duration_ms": null
		},
		{
			"id": 23,
			"timestamp": "2026-03-28 00:48:35",
			"log_type": "job_event",
			"level": "ERROR",
			"event": "job_failed",
			"job_id": "55dc211a-6daf-42ce-a94f-c2a330c6d627",
			"operation": "groupby",
			"status": "failed",
			"error_type": "ValueError",
			"message": "Operation failed: Groupby requires 'by' parameter",
			"details": {
				"error_detail": "Groupby requires 'by' parameter",
				"suggestion": null,
				"available_columns": null
			},
			"duration_ms": 11.966705322265625
		}
	]
}
```

### Get System Metrics

**Request:**

```bash
curl -X GET "http://$EC2_HOST:8000/logs/metrics"
```

**Response:**

```json
{
	"performance_by_operation": {
		"filter": {
			"avg_ms": 11.2,
			"min_ms": 0.9908676147460938,
			"max_ms": 52.60610580444336,
			"count": 6
		},
		"groupby": {
			"avg_ms": 8.76,
			"min_ms": 5.557060241699219,
			"max_ms": 11.966705322265625,
			"count": 2
		},
		"select": {
			"avg_ms": 50.98,
			"min_ms": 50.97675323486328,
			"max_ms": 50.97675323486328,
			"count": 1
		},
		"sort": {
			"avg_ms": 5.69,
			"min_ms": 5.694150924682617,
			"max_ms": 5.694150924682617,
			"count": 1
		}
	},
	"timestamp": "2026-03-28T00:54:34.775864"
}
```

## 🔍 Debug Tool Examples

### System Status Query

**Command:**

```bash
python3 debug.py "How is the system doing?"
```

**LLM Response:**

```
[Detected query type: system_status]
[Fetching system state...]
**System Summary:**

1. **Current System State:**
   - The system health status is reported as 'healthy'.
   - The SQLite database is operational.
   - The dataset is loaded with 3333 rows.
   - Uptime duration is 542.47 seconds.
   - There have been 3 total jobs, with 2 completed, and 1 failed (66.7% success rate).

2. **Recent Jobs:**
   - One job for 'groupby' operation failed, while 'select' and 'filter' operations were completed successfully.

3. **Recent Logs:**
   - There are multiple 'service_started' logs recorded, indicating service activity.

**Observations:**
- The system is currently stable and healthy based on the reported metrics.
- The recent job failures, especially the 'groupby' operation, require investigation to understand the root cause of the failure.
- The service seems to be starting multiple times within short intervals, which might indicate a potential issue with service stability or unexpected restarts.

**Action Items:**
1. Investigate the cause of the failed 'groupby' job to address any potential issues with the operation.
2. Monitor the service start logs closely to determine if there are any underlying issues causing frequent restarts.
3. Consider implementing additional logging or monitoring to capture more detailed information about job failures for better troubleshooting in the future.
```

### Job Failure Analysis -

**Command:**

```bash
python3 debug.py "why did job 55dc211a-6daf-42ce-a94f-c2a330c6d627 fail?"
```

**LLM Response:**

````
[Detected query type: job_failure]
[Fetching details for job 55dc211a-6daf-42ce-a94f-c2a330c6d627...]
Based on the provided information, let's analyze the failure of the job with the following details:

- Job ID: 55dc211a-6daf-42ce-a94f-c2a330c6d627
- Operation: groupby
- Parameters: {"column": "State", "agg_func": "mean", "agg_column": "Total day minutes"}
- Status: failed
- Timeline: job_created -> job_started -> job_failed

### Root Cause Analysis:

1. **Timeline Analysis:**
   - The job was created successfully.
   - The job started without any issues.
   - The failure occurred immediately after the job started, indicating that the error was in the initial processing stage.

2. **Error Information:**
   - The structured logs show that the job failed at the starting stage.
   - The error message is not specific about the root cause of the failure.

3. **Root Cause:**
   - The root cause of this failure is likely a column name mismatch issue.
   - The parameter "agg_column" in the job operation is specified as "Total day minutes".
   - However, based on the dataset schema, the correct column name should be "Total day minutes" (with spaces, not underscores).

4. **Solution:**
   - To fix this issue, the correct column name should be used in the groupby operation.
   - Update the job parameters to use the correct column name "Total day minutes" as follows:

```json
{
  "column": "State",
  "agg_func": "mean",
  "agg_column": "Total day minutes"
}
```

### Conclusion:

The job failed due to a column name mismatch where the actual column name in the dataset schema uses spaces instead of underscores. By correcting the column name in the job parameters, the groupby operation should work as expected.

### Pattern Check:

Since there are no similar failures found, this specific error seems to be an isolated incident related to the column name mismatch. It's essential to ensure consistency in column names across operations to prevent such failures in the future.

````

### Recent Errors Analysis

**Command:**

```bash
python3 debug.py "what are the recent errors?"
```

**LLM Response:**

```
[Detected query type: recent_errors]
[Fetching errors from last 1 hour(s)...]
Based on the provided information, here is the analysis of the recent failed job and potential preventive measures:

1. **Recent Failed Job**:
   - Job ID: 55dc211a-6daf-42ce-a94f-c2a330c6d627
   - Operation: groupby

2. **Error Analysis**:
   - No specific error patterns detected in the recent logs.
   - Total failures in the last hour: 0

3. **Common Issues**:
   - No specific error logs available to identify common issues across different error types.

4. **Preventive Measures**:
   - Implement input validation checks to ensure that the provided column names in operations like filter, select, groupby, and sort match the exact column names in the dataset schema.
   - Provide clear error messages indicating the expected column names and formats to guide users in avoiding common mistakes.
   - Consider implementing auto-suggestions or dropdowns for column names to prevent manual entry errors.
   - Regularly update documentation to emphasize the correct format of column names (spaces instead of underscores) to prevent KeyError issues.

5. **Column Name Issues**:
   - Highlight the importance of using column names with spaces instead of underscores in all operations to avoid KeyError issues.
   - Example: Use "Total day minutes" instead of "total_day_minutes".

6. **Performance Considerations**:
   - Since no specific error patterns were detected, there are no immediate performance-related issues to address. However, monitoring performance metrics during peak usage times can help identify potential bottlenecks or resource constraints.

In conclusion, while no specific error patterns were identified in the recent logs, focusing on preventive measures related to input validation, clear error messaging, and emphasizing correct column name formats can help reduce common errors and improve the overall user experience. Regular monitoring of both error logs and performance
```
