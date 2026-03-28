"""AWS CloudWatch client operations"""

import boto3
import json
import time
from typing import Dict, Any, List
from botocore.exceptions import ClientError
import logging

from .cloudwatch_setup import CloudWatchSetup


class CloudWatchClient:
    def __init__(self, 
                 log_group: str = None,
                 log_stream: str = None,
                 region: str = None):
        """Initialize CloudWatch client"""
        self.setup = CloudWatchSetup(log_group, log_stream, region)
        self.client = self.setup.client
        self.enabled = self.setup.enabled
        self.log_group = self.setup.log_group
        self.log_stream = self.setup.log_stream
        
        if self.enabled:
            self.setup.ensure_log_group_exists()
            self.setup.ensure_log_stream_exists()
            self.sequence_token = self.setup.get_sequence_token()
        else:
            self.sequence_token = None
    
    def send_logs(self, entries: List[Dict]):
        """Send logs to CloudWatch"""
        if not self.enabled or not entries:
            return
        
        try:
            # Prepare log events
            log_events = []
            for entry in entries:
                log_events.append({
                    'timestamp': int(time.time() * 1000),
                    'message': json.dumps(entry)
                })
            
            # Sort by timestamp (CloudWatch requirement)
            log_events.sort(key=lambda x: x['timestamp'])
            
            # Send to CloudWatch
            kwargs = {
                'logGroupName': self.log_group,
                'logStreamName': self.log_stream,
                'logEvents': log_events
            }
            
            if self.sequence_token:
                kwargs['sequenceToken'] = self.sequence_token
            
            response = self.client.put_log_events(**kwargs)
            self.sequence_token = response.get('nextSequenceToken')
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidSequenceTokenException':
                # Update sequence token and retry
                self.sequence_token = e.response['Error']['Message'].split(' ')[-1]
                self.send_logs(entries)
            else:
                logging.error(f"Failed to send logs to CloudWatch: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get CloudWatch metrics for the service"""
        if not self.enabled:
            return {}
        
        try:
            cloudwatch = boto3.client('cloudwatch', region_name=self.region)
            
            # Get custom metrics if any
            metrics = {
                'log_group': self.log_group,
                'log_stream': self.log_stream,
                'region': self.region
            }
            
            return metrics
            
        except Exception as e:
            logging.error(f"Failed to get CloudWatch metrics: {e}")
            return {}