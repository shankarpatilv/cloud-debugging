"""Metrics formatting utilities"""

from typing import Dict, Any


class MetricFormatter:
    @staticmethod
    def format_performance_metrics(metrics: Dict[str, Any]) -> str:
        """Format performance metrics for display"""
        if not metrics or metrics.get('error'):
            return "Performance metrics unavailable"
        
        metrics_data = metrics.get('metrics', {})
        if not metrics_data:
            return "No performance metrics available"
        
        lines = []
        for key, value in metrics_data.items():
            if isinstance(value, (int, float)):
                lines.append(f"- {key}: {value}")
            else:
                lines.append(f"- {key}: {str(value)}")
        
        return '\n'.join(lines) if lines else "No performance metrics available"
    
    @staticmethod
    def format_job_statistics(metrics: Dict[str, Any]) -> str:
        """Format job statistics section"""
        total = metrics.get('total', 0)
        pending = metrics.get('pending', 0)
        running = metrics.get('running', 0)
        completed = metrics.get('completed', 0)
        failed = metrics.get('failed', 0)
        success_rate = metrics.get('success_rate', 0)
        
        return f"""- Total jobs: {total}
- Pending: {pending}
- Running: {running}
- Completed: {completed}
- Failed: {failed}
- Success rate: {success_rate:.1f}%"""
    
    @staticmethod
    def format_system_status(health: Dict[str, Any]) -> str:
        """Format system status section"""
        status = health.get('status', 'Unknown')
        dataset_loaded = health.get('dataset_loaded', False)
        uptime_seconds = health.get('uptime_seconds', 0)
        
        return f"""- Status: {status}
- Dataset loaded: {dataset_loaded}
- Uptime: {uptime_seconds:.1f} seconds"""
    
    @staticmethod
    def format_dataset_info(schema: Dict[str, Any]) -> str:
        """Format dataset information"""
        rows = schema.get('rows', 'Unknown')
        columns = schema.get('columns', [])
        column_count = len(columns)
        sample_columns = ', '.join(columns[:5])
        
        return f"""- Total rows: {rows}
- Total columns: {column_count}
- Columns include: {sample_columns}..."""
    
    @staticmethod
    def format_error_summary(error_data: Dict[str, Any]) -> str:
        """Format recent error summary"""
        time_range = error_data.get('time_range_hours', 1)
        failure_count = error_data.get('failure_count', 0)
        structured_logs = error_data.get('structured_error_logs', {})
        log_count = structured_logs.get('count', 0)
        
        return f"""- Time range: Last {time_range} hour(s)
- Total failures: {failure_count}
- Structured error logs: {log_count}"""