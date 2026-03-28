"""Log collection methods for StateCollector"""

import requests
from typing import Dict, Any, Optional


class LogCollector:
    def __init__(self, session: requests.Session, api_url: str):
        """Initialize with session and API URL"""
        self.session = session
        self.api_url = api_url
    
    def get_structured_logs(self, job_id: Optional[str] = None, log_type: Optional[str] = None, 
                            level: Optional[str] = None, hours: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get structured logs with filtering"""
        try:
            params = {
                'hours': hours,
                'limit': limit
            }
            if job_id:
                params['job_id'] = job_id
            if log_type:
                params['log_type'] = log_type
            if level:
                params['level'] = level
            
            response = self.session.get(f"{self.api_url}/logs/structured", params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f"Failed to fetch structured logs: HTTP {response.status_code}",
                    'count': 0,
                    'logs': []
                }
        except requests.RequestException as e:
            return {
                'error': f"Failed to fetch structured logs: {str(e)}",
                'count': 0,
                'logs': []
            }
    
    def get_error_patterns(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary and patterns"""
        try:
            params = {'hours': hours}
            response = self.session.get(f"{self.api_url}/logs/errors", params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f"Failed to fetch error patterns: HTTP {response.status_code}",
                    'error_summary': {},
                    'patterns': []
                }
        except requests.RequestException as e:
            return {
                'error': f"Failed to fetch error patterns: {str(e)}",
                'error_summary': {},
                'patterns': []
            }
    
    def get_error_logs(self, hours: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get recent error logs (legacy method)"""
        try:
            logs_response = self.session.get(f"{self.api_url}/logs", params={'limit': limit})
            all_logs = logs_response.json().get('logs', []) if logs_response.status_code == 200 else []
            error_logs = [log for log in all_logs if log.get('level') == 'ERROR']
            return {'error_logs': error_logs[-20:]}  # Last 20 error logs
        except requests.RequestException:
            return {'error_logs': []}
    
    def group_errors_by_type(self, recent_failures):
        """Group errors by type from failed jobs"""
        error_groups = {}
        for job in recent_failures:
            try:
                # Get full job details for error information
                job_details = self.session.get(f"{self.api_url}/jobs/{job['id']}").json()
                if job_details.get('error'):
                    error_type = job_details['error'].get('error_type', 'Unknown')
                    if error_type not in error_groups:
                        error_groups[error_type] = []
                    error_groups[error_type].append({
                        'job_id': job['id'],
                        'operation': job['operation'],
                        'error': job_details['error'].get('message', str(job_details['error']))
                    })
            except:
                continue
        return error_groups