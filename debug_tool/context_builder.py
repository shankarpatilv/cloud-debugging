"""Context builder wrapper that imports from formatters and templates"""

import json
from typing import Dict, Any, List
from formatters.log_formatter import LogFormatter
from formatters.job_formatter import JobFormatter
from formatters.metric_formatter import MetricFormatter
from templates.context_templates import ContextTemplates


class ContextBuilder:
    def __init__(self):
        """Initialize with all formatters and templates"""
        self.log_formatter = LogFormatter()
        self.job_formatter = JobFormatter()
        self.metric_formatter = MetricFormatter()
        self.templates = ContextTemplates()
        self.schema = self._load_schema()
        self.system_knowledge = self.templates.get_system_knowledge()
    
    def _load_schema(self):
        """Load dataset schema"""
        import os
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'service', 'data', 'schema.json'
        )
        
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
                if 'column_names' in schema and isinstance(schema.get('columns'), int):
                    schema['columns'] = schema['column_names']
                return schema
        except:
            return {
                'columns': [
                    'customer_id', 'State', 'Account length', 'Area code',
                    'International plan', 'Voice mail plan', 'Number vmail messages',
                    'Total day minutes', 'Total day calls', 'Total day charge',
                    'Total eve minutes', 'Total eve calls', 'Total eve charge',
                    'Total night minutes', 'Total night calls', 'Total night charge',
                    'Total intl minutes', 'Total intl calls', 'Total intl charge',
                    'Customer service calls', 'Churn'
                ],
                'rows': 3333,
                'note': 'Column names use spaces, not underscores'
            }
    
    def build_context_for_system_status(self, state_data: Dict[str, Any]) -> str:
        """Build context for system status query"""
        context = []
        context.append(self.system_knowledge)
        context.append("\n=== CURRENT SYSTEM STATE ===\n")
        
        if 'health' in state_data:
            context.append(f"Health Status: {state_data['health']}\n")
        
        if 'job_metrics' in state_data:
            context.append(self.metric_formatter.format_job_statistics(state_data['job_metrics']))
        
        if 'recent_jobs' in state_data:
            context.append("\n=== RECENT JOBS ===\n")
            context.append(self.job_formatter.format_recent_jobs(state_data['recent_jobs'][:5]))
        
        if 'recent_logs' in state_data:
            context.append("\n=== RECENT LOGS ===\n")
            context.append(self.log_formatter.format_logs(state_data['recent_logs']))
        
        context.append(f"\n{self.templates.get_system_status_tasks()}")
        return "\n".join(context)
    
    def build_context_for_job_failure(self, job_data: Dict[str, Any]) -> str:
        """Build context for job failure analysis"""
        context = []
        context.append(self.system_knowledge)
        context.append("\n=== DATASET SCHEMA ===\n")
        context.append(f"Columns: {self.schema.get('columns', [])}\n")
        
        if 'job' in job_data:
            context.append("\n=== FAILED JOB DETAILS ===\n")
            context.append(self.job_formatter.format_job_details(job_data['job']))
        
        if 'timeline' in job_data:
            context.append("\n=== JOB TIMELINE ===\n")
            timeline_data = job_data.get('timeline', {})
            if isinstance(timeline_data, dict):
                events = timeline_data.get('timeline', [])
            else:
                events = timeline_data if isinstance(timeline_data, list) else []
            context.append(self.log_formatter.format_timeline(events))
        
        if 'structured_logs' in job_data:
            context.append("\n=== STRUCTURED LOGS ===\n")
            logs = job_data['structured_logs'].get('logs', []) if isinstance(job_data['structured_logs'], dict) else job_data['structured_logs']
            context.append(self.log_formatter.format_structured_logs(logs))
        
        if 'similar_failures' in job_data:
            context.append("\n=== SIMILAR FAILURES ===\n")
            context.append(self.job_formatter.format_similar_failures(job_data['similar_failures']))
        
        context.append(f"\n{self.templates.get_job_failure_tasks()}")
        return "\n".join(context)
    
    def build_context_for_job_success(self, job_data: Dict[str, Any]) -> str:
        """Build context for successful job analysis"""
        context = []
        context.append(self.system_knowledge)
        
        if 'job' in job_data:
            context.append("\n=== JOB DETAILS ===\n")
            context.append(self.job_formatter.format_job_details(job_data['job']))
        
        if 'timeline' in job_data:
            context.append("\n=== JOB TIMELINE ===\n")
            timeline_data = job_data.get('timeline', {})
            if isinstance(timeline_data, dict):
                events = timeline_data.get('timeline', [])
            else:
                events = timeline_data if isinstance(timeline_data, list) else []
            context.append(self.log_formatter.format_timeline(events))
        
        if 'structured_logs' in job_data:
            context.append("\n=== STRUCTURED LOGS ===\n")
            logs = job_data['structured_logs'].get('logs', []) if isinstance(job_data['structured_logs'], dict) else job_data['structured_logs']
            context.append(self.log_formatter.format_structured_logs(logs))
        
        context.append(f"\n{self.templates.get_job_success_tasks()}")
        return "\n".join(context)
    
    def build_context_for_recent_errors(self, error_data: Dict[str, Any]) -> str:
        """Build context for recent errors analysis"""
        context = []
        context.append(self.system_knowledge)
        context.append("\n=== DATASET SCHEMA ===\n")
        context.append(f"Columns: {self.schema.get('columns', [])}\n")
        
        if 'recent_failures' in error_data:
            context.append("\n=== RECENT FAILED JOBS ===\n")
            context.append(self.job_formatter.format_failures(error_data['recent_failures'][:10]))
        
        if 'error_patterns' in error_data:
            context.append("\n=== ERROR PATTERNS ===\n")
            context.append(self.log_formatter.format_error_patterns(error_data['error_patterns']))
        
        if 'error_logs' in error_data:
            context.append("\n=== ERROR LOGS ===\n")
            context.append(self.log_formatter.format_logs(error_data['error_logs']))
        
        if 'error_groups' in error_data:
            context.append("\n=== ERRORS GROUPED BY TYPE ===\n")
            context.append(self.metric_formatter.format_error_summary(error_data))
        
        context.append(f"\n{self.templates.get_recent_errors_tasks()}")
        return "\n".join(context)