"""Background job processing task"""

import time
from ..database import update_job_status
from ..structured_logger import structured_logger
from ..job_processor import JobProcessor

processor = JobProcessor()


def process_job(job_id: str, operation: str, params: dict):
    """Process a job (runs in background)"""
    start_time = time.time()
    try:
        # Update status to running
        update_job_status(job_id, 'running')
        structured_logger.log_job_event(
            event='job_started',
            job_id=job_id,
            operation=operation,
            level='INFO',
            details={'params': params}
        )
        
        # Process the data
        result = processor.process(operation, params)
        duration_ms = (time.time() - start_time) * 1000
        
        if result['success']:
            # Job completed successfully
            update_job_status(job_id, 'completed', result=result)
            structured_logger.log_job_event(
                event='job_completed',
                job_id=job_id,
                operation=operation,
                status='completed',
                level='INFO',
                duration_ms=duration_ms,
                details={
                    'row_count': result['row_count'],
                    'columns': result['columns'],
                    'shape': result['shape']
                }
            )
        else:
            # Job failed
            update_job_status(job_id, 'failed', error=result)
            structured_logger.log_job_event(
                event='job_failed',
                job_id=job_id,
                operation=operation,
                status='failed',
                level='ERROR',
                error={
                    'type': result['error_type'],
                    'message': result['message']
                },
                duration_ms=duration_ms,
                details={
                    'error_detail': result['error'],
                    'suggestion': result.get('suggestion'),
                    'available_columns': result.get('available_columns')
                }
            )
            
    except Exception as e:
        # Unexpected error
        duration_ms = (time.time() - start_time) * 1000
        error_data = {
            'error': str(e),
            'error_type': type(e).__name__,
            'message': f"Unexpected error: {str(e)}"
        }
        update_job_status(job_id, 'failed', error=error_data)
        structured_logger.log_job_event(
            event='job_failed',
            job_id=job_id,
            operation=operation,
            status='failed',
            level='ERROR',
            error={
                'type': type(e).__name__,
                'message': str(e)
            },
            duration_ms=duration_ms,
            details=error_data
        )