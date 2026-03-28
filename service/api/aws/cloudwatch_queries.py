"""CloudWatch log query operations"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
import logging


class CloudWatchQueries:
    def __init__(self, client, log_group: str):
        """Initialize query operations"""
        self.client = client
        self.log_group = log_group
    
    def query_logs(self,
                   start_time: datetime,
                   end_time: datetime,
                   filter_pattern: str = None,
                   limit: int = 100) -> List[Dict]:
        """Query CloudWatch logs"""
        if not self.client:
            return []
        
        try:
            # Build filter pattern for structured logs
            if not filter_pattern:
                filter_pattern = ""
            
            # Start query
            query_string = f"""
                fields @timestamp, @message
                | parse @message /\\{{(?<data>.*)\\}}/
                | fields @timestamp, data
                | filter @message like /{filter_pattern}/
                | sort @timestamp desc
                | limit {limit}
            """
            
            response = self.client.start_query(
                logGroupName=self.log_group,
                startTime=int(start_time.timestamp()),
                endTime=int(end_time.timestamp()),
                queryString=query_string,
                limit=limit
            )
            
            query_id = response['queryId']
            
            # Wait for query to complete
            status = 'Running'
            while status == 'Running':
                time.sleep(0.5)
                result = self.client.get_query_results(queryId=query_id)
                status = result['status']
            
            # Parse results
            logs = []
            for row in result.get('results', []):
                for field in row:
                    if field['field'] == 'data':
                        try:
                            logs.append(json.loads('{' + field['value'] + '}'))
                        except:
                            pass
            
            return logs
            
        except Exception as e:
            logging.error(f"Failed to query CloudWatch logs: {e}")
            return []