"""Job collection methods for StateCollector"""

import requests
from typing import Dict, List, Any
from datetime import datetime, timedelta


class JobCollector:
    def __init__(self, session: requests.Session, api_url: str):
        """Initialize with session and API URL"""
        self.session = session
        self.api_url = api_url
    
    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific job"""
        try:
            # Get job details
            job_response = self.session.get(f"{self.api_url}/jobs/{job_id}")
            if job_response.status_code != 200:
                return {'error': f"Job {job_id} not found"}
            
            job = job_response.json()
            
            # Get related logs
            logs_response = self.session.get(
                f"{self.api_url}/logs",
                params={'job_id': job_id, 'limit': 20}
            )
            logs = logs_response.json().get('logs', []) if logs_response.status_code == 200 else []
            
            # Get structured logs for this job
            structured_logs = self._get_structured_logs_for_job(job_id, hours=24, limit=50)
            
            # Get job timeline
            timeline = self.get_job_timeline(job_id)
            
            # Find similar failures if this job failed
            similar_failures = []
            if job.get('status') == 'failed' and job.get('error'):
                all_jobs = self.session.get(f"{self.api_url}/jobs").json()
                similar_failures = [
                    j for j in all_jobs
                    if j.get('status') == 'failed' 
                    and j['id'] != job_id
                    and j.get('operation') == job.get('operation')
                ][:5]
            
            return {
                'job': job,
                'logs': logs,
                'structured_logs': structured_logs,
                'timeline': timeline,
                'similar_failures': similar_failures
            }
            
        except requests.RequestException as e:
            return {'error': f"Failed to fetch job details: {str(e)}"}
    
    def get_job_timeline(self, job_id: str) -> Dict[str, Any]:
        """Get complete timeline of events for a specific job"""
        try:
            response = self.session.get(f"{self.api_url}/logs/timeline/{job_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {
                    'error': f"No timeline found for job {job_id}",
                    'job_id': job_id,
                    'timeline': []
                }
            else:
                return {
                    'error': f"Failed to fetch job timeline: HTTP {response.status_code}",
                    'job_id': job_id,
                    'timeline': []
                }
        except requests.RequestException as e:
            return {
                'error': f"Failed to fetch job timeline: {str(e)}",
                'job_id': job_id,
                'timeline': []
            }
    
    def get_recent_failures(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get recent failed jobs"""
        try:
            # Fetch all jobs
            jobs_response = self.session.get(f"{self.api_url}/jobs", params={'limit': 200})
            all_jobs = jobs_response.json() if jobs_response.status_code == 200 else []
            
            # Filter for recent failures
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_failures = []
            
            for job in all_jobs:
                if job['status'] == 'failed':
                    try:
                        job_time = datetime.fromisoformat(job['created_at'].replace('Z', '+00:00'))
                        if job_time > cutoff_time:
                            recent_failures.append(job)
                    except:
                        # If date parsing fails, include it anyway
                        recent_failures.append(job)
            
            return recent_failures
            
        except requests.RequestException:
            return []
    
    def _get_structured_logs_for_job(self, job_id: str, hours: int, limit: int) -> Dict[str, Any]:
        """Get structured logs for a specific job"""
        try:
            params = {
                'hours': hours,
                'limit': limit,
                'job_id': job_id
            }
            
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