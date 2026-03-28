"""Log formatting utilities"""

from typing import List, Dict, Any


class LogFormatter:
    @staticmethod
    def format_logs(logs: List[Dict]) -> str:
        """Format logs for display"""
        if not logs:
            return "No logs available"
        
        lines = []
        for log in logs[-10:]:  # Last 10 logs
            timestamp = log.get('timestamp', '')
            level = log.get('level', '')
            event = log.get('event', '')
            error = log.get('error', '')
            lines.append(f"[{timestamp}] {level}: {event} - {error}")
        return '\n'.join(lines)
    
    @staticmethod
    def format_structured_logs(logs: List[Dict]) -> str:
        """Format structured logs for display"""
        if not logs:
            return "No structured logs available"
        
        lines = []
        for log in logs[-15:]:  # Last 15 structured logs
            timestamp = log.get('timestamp', '')
            level = log.get('level', 'INFO')
            log_type = log.get('log_type', 'general')
            event = log.get('event', '')
            job_id = log.get('job_id', '')
            
            # Build log line
            log_line = f"[{timestamp}] {level} ({log_type})"
            if job_id:
                log_line += f" [Job: {job_id}]"
            log_line += f": {event}"
            
            # Add error details if present
            if log.get('error'):
                error_info = log['error']
                if isinstance(error_info, dict):
                    log_line += f" - Error: {error_info.get('message', str(error_info))}"
                else:
                    log_line += f" - Error: {str(error_info)}"
            
            lines.append(log_line)
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_error_patterns(patterns: Dict[str, Any]) -> str:
        """Format error patterns for display"""
        if not patterns or patterns.get('error'):
            return "Error patterns unavailable"
        
        error_summary = patterns.get('error_summary', {})
        pattern_list = patterns.get('patterns', [])
        
        lines = []
        
        if error_summary:
            lines.append("Error Summary:")
            for error_type, count in error_summary.items():
                lines.append(f"  - {error_type}: {count} occurrences")
            lines.append("")
        
        if pattern_list:
            lines.append("Detected Patterns:")
            for pattern in pattern_list[:5]:  # Top 5 patterns
                lines.append(f"  - {pattern.get('description', 'Unknown pattern')}")
                if pattern.get('count'):
                    lines.append(f"    Frequency: {pattern['count']}")
            lines.append("")
        
        return '\n'.join(lines) if lines else "No error patterns detected"
    
    @staticmethod
    def format_timeline(timeline: List[Dict]) -> str:
        """Format job timeline for display"""
        if not timeline:
            return "No timeline available"
        
        lines = []
        for event in timeline:
            timestamp = event.get('timestamp', '')
            event_type = event.get('event', '')
            level = event.get('level', 'INFO')
            
            line = f"[{timestamp}] {level}: {event_type}"
            
            # Add additional context
            if event.get('duration'):
                line += f" (took {event['duration']}ms)"
            if event.get('error'):
                line += f" - ERROR: {event['error']}"
            
            lines.append(line)
        
        return '\n'.join(lines)