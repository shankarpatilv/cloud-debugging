"""CloudWatch setup and initialization operations"""

import boto3
import os
from typing import Optional
from botocore.exceptions import ClientError
import logging


class CloudWatchSetup:
    def __init__(self, 
                 log_group: str = None,
                 log_stream: str = None,
                 region: str = None):
        """Initialize CloudWatch setup"""
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        self.log_group = log_group or os.getenv('CLOUDWATCH_LOG_GROUP', '/aws/ec2/cloud-debug-service')
        self.log_stream = log_stream or os.getenv('CLOUDWATCH_LOG_STREAM', f"instance-{os.getenv('EC2_INSTANCE_ID', 'local')}")
        
        try:
            self.client = boto3.client('logs', region_name=self.region)
            self.enabled = True
        except Exception as e:
            logging.warning(f"CloudWatch client initialization failed: {e}")
            self.enabled = False
            self.client = None
    
    def ensure_log_group_exists(self):
        """Create log group if it doesn't exist"""
        if not self.enabled:
            return
        
        try:
            self.client.create_log_group(logGroupName=self.log_group)
            # Set retention policy to 7 days
            self.client.put_retention_policy(
                logGroupName=self.log_group,
                retentionInDays=7
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                raise
    
    def ensure_log_stream_exists(self):
        """Create log stream if it doesn't exist"""
        if not self.enabled:
            return
        
        try:
            self.client.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                raise
    
    def get_sequence_token(self) -> Optional[str]:
        """Get the sequence token for the log stream"""
        if not self.enabled:
            return None
        
        try:
            response = self.client.describe_log_streams(
                logGroupName=self.log_group,
                logStreamNamePrefix=self.log_stream
            )
            streams = response.get('logStreams', [])
            if streams:
                return streams[0].get('uploadSequenceToken')
        except Exception:
            pass
        return None