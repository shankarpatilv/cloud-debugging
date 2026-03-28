"""Rule-based query parser for natural language queries"""

import re
from typing import Dict, Optional, Any


class QueryParser:
    def __init__(self):
        """Initialize with query patterns"""
        self.patterns = {
            'system_status': {
                'keywords': ['system', 'doing', 'happening', 'now', 'current', 'what is'],
                'regex': r'(what.*system.*doing|what.*happening|system.*status|right now)',
                'type': 'system_status'
            },
            'job_status': {
                'keywords': ['status', 'job', 'tell', 'about', 'check', 'show'],
                'regex': r'(status.*job|job.*status|tell.*job|check.*job|show.*job)',
                'type': 'job_status'
            },
            'job_failure': {
                'keywords': ['fail', 'error', 'why', 'wrong', 'broken', 'issue', 'problem'],
                'regex': r'(job.*fail|why.*job|what.*wrong.*job|job.*error|why.*fail)',
                'type': 'job_failure'
            },
            'recent_errors': {
                'keywords': ['recent', 'errors', 'failures', 'problems', 'issues', 'latest'],
                'regex': r'(recent.*error|recent.*fail|what.*error|latest.*problem)',
                'type': 'recent_errors'
            }
        }
    
    def parse(self, query: str) -> Dict[str, Any]:
        """Parse natural language query and extract intent"""
        query_lower = query.lower().strip()
        
        # Score each pattern
        best_match = None
        best_score = 0
        
        for pattern_name, pattern_data in self.patterns.items():
            score = 0
            
            # Check keyword matches
            for keyword in pattern_data['keywords']:
                if keyword in query_lower:
                    score += 2
            
            # Check regex match
            if re.search(pattern_data['regex'], query_lower):
                score += 5
            
            if score > best_score:
                best_score = score
                best_match = pattern_name
        
        # Extract parameters based on match type
        params = {}
        
        if best_match in ['job_failure', 'job_status']:
            job_id = self._extract_job_id(query)
            if job_id:
                params['job_id'] = job_id
        
        elif best_match == 'recent_errors':
            time_range = self._extract_time_range(query)
            params['hours'] = time_range
        
        return {
            'type': best_match or 'unknown',
            'params': params,
            'original_query': query,
            'confidence': min(best_score / 10, 1.0)  # Normalize score
        }
    
    def _extract_job_id(self, query: str) -> Optional[str]:
        """Extract job ID from query"""
        # Look for UUID pattern
        uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
        match = re.search(uuid_pattern, query.lower())
        if match:
            return match.group()
        
        # Look for "job XXX" or "job #XXX" pattern
        job_pattern = r'job\s+#?([a-zA-Z0-9-]+)'
        match = re.search(job_pattern, query, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Look for quoted ID
        quote_pattern = r'["\']([a-f0-9-]+)["\']'
        match = re.search(quote_pattern, query)
        if match:
            potential_id = match.group(1)
            if len(potential_id) > 8:  # Likely a job ID
                return potential_id
        
        return None
    
    def _extract_time_range(self, query: str) -> int:
        """Extract time range in hours from query"""
        query_lower = query.lower()
        
        if 'hour' in query_lower:
            # Try to extract number before 'hour'
            match = re.search(r'(\d+)\s*hour', query_lower)
            if match:
                return int(match.group(1))
            elif 'last hour' in query_lower or 'past hour' in query_lower:
                return 1
        
        if 'today' in query_lower:
            return 24
        
        if 'yesterday' in query_lower:
            return 48
        
        if 'week' in query_lower:
            return 168
        
        # Default to last hour
        return 1