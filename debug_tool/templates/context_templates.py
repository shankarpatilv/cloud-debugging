"""Context string templates"""


class ContextTemplates:
    @staticmethod
    def get_system_knowledge() -> str:
        """Get system knowledge and rules template"""
        return """
SYSTEM ARCHITECTURE:
- FastAPI service running on AWS EC2
- SQLite database for job metadata tracking
- CSV dataset with customer churn data
- JSON structured logging for events

SUPPORTED OPERATIONS:
1. filter: Filter rows by condition
   - Operators: ==, !=, >, <, >=, <=
   - Example: {"column": "State", "operator": "==", "value": "KS"}

2. select: Choose specific columns
   - Example: {"columns": ["State", "Total day minutes"]}

3. groupby: Group and aggregate data
   - Example: {"by": "State", "agg": {"Total day minutes": "mean"}}

4. sort: Sort by column(s)
   - Example: {"column": "Total day charge", "ascending": false}

COMMON ERRORS:
- KeyError: Column name not found (usually due to underscore vs space)
- TypeError: Type mismatch in operations
- ValueError: Invalid parameters or values

IMPORTANT NOTES:
- Column names use SPACES, not underscores
- Example: "Total day minutes" NOT "total_day_minutes"
- Column names are case-sensitive
"""
    
    @staticmethod
    def get_system_status_tasks() -> str:
        """Get system status analysis tasks"""
        return """
Please provide a concise summary of what the system is doing right now, including performance status and any concerning patterns.
"""
    
    @staticmethod
    def get_job_failure_tasks() -> str:
        """Get job failure analysis tasks"""
        return """
TASK:
1. Analyze the complete job timeline to understand the failure sequence
2. Identify the root cause based on structured logs and error information
3. Explain why this specific error occurred and at what stage
4. Provide the correct way to fix it with a working example
5. If it's a column name issue, show the correct column name from the schema
6. Check if this is part of a pattern based on similar failures
"""
    
    @staticmethod
    def get_recent_errors_tasks() -> str:
        """Get recent errors analysis tasks"""
        return """
TASK:
1. Analyze both structured logs and error patterns to identify root causes
2. Summarize the recent errors and their frequency
3. Identify patterns or common issues across different error types
4. Suggest preventive measures based on the error trends
5. Highlight any column name issues (underscore vs space)
6. Check for performance-related issues in the patterns
"""
    
    @staticmethod
    def get_job_success_tasks() -> str:
        """Get job success analysis tasks"""
        return """
TASK:
1. Explain what this job successfully did based on the timeline and logs
2. Describe the operation performed and its parameters
3. Summarize the results obtained
4. Confirm the job completed without errors and show the execution flow
"""