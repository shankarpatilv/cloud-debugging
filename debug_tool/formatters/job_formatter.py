"""Job formatting utilities"""

from typing import List, Dict, Any
import json


class JobFormatter:
    @staticmethod
    def format_recent_jobs(jobs: List[Dict]) -> str:
        """Format recent jobs for display"""
        if not jobs:
            return "No recent jobs"
        
        lines = []
        for job in jobs[:5]:
            job_id = job.get('id', 'Unknown')
            operation = job.get('operation', 'Unknown')
            status = job.get('status', 'Unknown')
            lines.append(f"- {job_id}: {operation} - {status}")
        return '\n'.join(lines)
    
    @staticmethod
    def format_failures(failures: List[Dict]) -> str:
        """Format failures for display"""
        if not failures:
            return "No recent failures"
        
        lines = []
        for failure in failures[:5]:
            job_id = failure.get('id')
            operation = failure.get('operation')
            created_at = failure.get('created_at')
            lines.append(f"- Job {job_id}: {operation} - Created: {created_at}")
        return '\n'.join(lines)
    
    @staticmethod
    def format_similar_failures(failures: List[Dict]) -> str:
        """Format similar failures for display"""
        if not failures:
            return "No similar failures found"
        
        lines = []
        for failure in failures:
            job_id = failure.get('id')
            operation = failure.get('operation')
            created_at = failure.get('created_at')
            lines.append(f"- Job {job_id}: {operation} - {created_at}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_job_details(job: Dict[str, Any]) -> str:
        """Format job details section"""
        return f"""Job ID: {job.get('id')}
Operation: {job.get('operation')}
Parameters: {json.dumps(job.get('params', {}), indent=2)}
Status: {job.get('status')}
Created: {job.get('created_at')}
Completed: {job.get('completed_at')}"""
    
    @staticmethod
    def format_job_error(error: Dict[str, Any]) -> str:
        """Format job error information"""
        return json.dumps(error, indent=2)
    
    @staticmethod
    def format_job_results(result: Dict[str, Any]) -> str:
        """Format job results section"""
        row_count = result.get('row_count', 0)
        columns = result.get('columns', [])
        shape = result.get('shape', 'Unknown')
        preview = result.get('preview', [])
        
        results_text = f"""- Rows processed: {row_count}
- Columns in result: {columns}
- Shape: {shape}

PREVIEW OF RESULTS:
{json.dumps(preview[:3], indent=2)}"""
        
        return results_text