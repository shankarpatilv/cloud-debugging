"""State collector wrapper that imports from collectors modules"""

import requests
from collectors.job_collector import JobCollector
from collectors.log_collector import LogCollector
from collectors.metrics_collector import MetricsCollector


class StateCollector:
    def __init__(self, api_url: str):
        """Initialize with all collectors"""
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.job_collector = JobCollector(self.session, self.api_url)
        self.log_collector = LogCollector(self.session, self.api_url)
        self.metrics_collector = MetricsCollector(self.session, self.api_url)
    
    def get_system_overview(self):
        """Get comprehensive system state"""
        try:
            # Fetch different components
            jobs_response = self.session.get(f"{self.api_url}/jobs")
            stats_response = self.session.get(f"{self.api_url}/stats")
            health_response = self.session.get(f"{self.api_url}/health")
            
            jobs = jobs_response.json() if jobs_response.status_code == 200 else []
            stats = stats_response.json() if stats_response.status_code == 200 else {}
            health = health_response.json() if health_response.status_code == 200 else {}
            
            # Get recent logs
            logs_response = self.session.get(f"{self.api_url}/logs", params={'limit': 50})
            logs = logs_response.json().get('logs', []) if logs_response.status_code == 200 else []
            
            # Get performance metrics
            performance = self.get_performance_metrics()
            
            # Get recent errors
            errors = self.get_recent_errors(hours=1)
            
            # Calculate job metrics
            job_metrics = self.metrics_collector.calculate_job_metrics(jobs)
            
            return {
                'health': health,
                'stats': stats,
                'job_metrics': job_metrics,
                'recent_jobs': jobs[:10],
                'recent_logs': logs[:20],
                'performance': performance,
                'recent_errors': errors
            }
            
        except Exception as e:
            return {'error': f"Failed to fetch system overview: {str(e)}"}
    
    def get_job_details(self, job_id: str):
        """Get detailed information about a specific job"""
        return self.job_collector.get_job_details(job_id)
    
    def get_recent_errors(self, hours: int = 1):
        """Get recent errors and failures"""
        # Use get_error_patterns which exists in the refactored LogCollector
        error_data = self.log_collector.get_error_patterns(hours)
        
        # Also get recent failed jobs
        recent_failures = self.job_collector.get_recent_failures(hours)
        
        # Get error logs
        error_logs = self.log_collector.get_error_logs(hours)
        
        # Group errors by type
        error_groups = self.log_collector.group_errors_by_type(recent_failures)
        
        return {
            'recent_failures': recent_failures,
            'error_patterns': error_data,
            'error_logs': error_logs.get('error_logs', []),
            'error_groups': error_groups
        }
    
    def get_structured_logs(self, *args, **kwargs):
        """Get structured logs"""
        return self.log_collector.get_structured_logs(*args, **kwargs)
    
    def get_error_patterns(self, hours: int = 24):
        """Get error patterns"""
        return self.log_collector.get_error_patterns(hours)
    
    def get_performance_metrics(self):
        """Get performance metrics"""
        return self.metrics_collector.get_performance_metrics()
    
    def get_job_timeline(self, job_id: str):
        """Get job timeline"""
        # Use the JobCollector's get_job_timeline method since it exists there
        return self.job_collector.get_job_timeline(job_id)
    
    def test_connection(self):
        """Test if API is reachable"""
        try:
            response = self.session.get(f"{self.api_url}/health")
            return response.status_code == 200
        except:
            return False