"""Metrics and performance collection methods"""

import requests
from typing import Dict, Any


class MetricsCollector:
    def __init__(self, session: requests.Session, api_url: str):
        """Initialize with session and API URL"""
        self.session = session
        self.api_url = api_url
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            response = self.session.get(f"{self.api_url}/logs/metrics")
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f"Failed to fetch performance metrics: HTTP {response.status_code}",
                    'metrics': {}
                }
        except requests.RequestException as e:
            return {
                'error': f"Failed to fetch performance metrics: {str(e)}",
                'metrics': {}
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status"""
        try:
            health_response = self.session.get(f"{self.api_url}/health")
            return health_response.json() if health_response.status_code == 200 else {}
        except requests.RequestException:
            return {'status': 'unknown'}
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            stats_response = self.session.get(f"{self.api_url}/stats")
            return stats_response.json() if stats_response.status_code == 200 else {}
        except requests.RequestException:
            return {}
    
    def calculate_job_metrics(self, jobs) -> Dict[str, Any]:
        """Calculate job-related metrics"""
        if not jobs:
            return {
                'total': 0,
                'pending': 0,
                'running': 0,
                'completed': 0,
                'failed': 0,
                'success_rate': 0
            }
        
        pending = len([j for j in jobs if j['status'] == 'pending'])
        running = len([j for j in jobs if j['status'] == 'running'])
        completed = len([j for j in jobs if j['status'] == 'completed'])
        failed = len([j for j in jobs if j['status'] == 'failed'])
        
        return {
            'total': len(jobs),
            'pending': pending,
            'running': running,
            'completed': completed,
            'failed': failed,
            'success_rate': (completed / len(jobs) * 100) if jobs else 0
        }