"""Structured JSON logging configuration"""

import logging
import os
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger


def setup_logging():
    """Configure structured JSON logging"""
    log_path = os.getenv('LOG_PATH', 'logs/app.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    # Create custom formatter
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super().add_fields(log_record, record, message_dict)
            log_record['timestamp'] = datetime.now().isoformat()
            log_record['level'] = record.levelname
    
    # Configure handler
    handler = logging.FileHandler(log_path)
    handler.setFormatter(CustomJsonFormatter())
    
    # Configure logger
    logger = logging.getLogger('api')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Also log to console for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(console_handler)
    
    return logger


def log_job_event(logger, event: str, job_id: str, **kwargs):
    """Helper to log job-related events with consistent structure"""
    log_data = {
        'event': event,
        'job_id': job_id,
        **kwargs
    }
    
    if event.endswith('failed'):
        logger.error(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))