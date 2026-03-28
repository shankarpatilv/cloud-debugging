"""Query processing logic"""

from query_parser import QueryParser
from state_collector import StateCollector
from context_builder import ContextBuilder
from llm_analyzer import LLMAnalyzer


class QueryProcessor:
    def __init__(self, query_parser: QueryParser, state_collector: StateCollector,
                 context_builder: ContextBuilder, llm_analyzer: LLMAnalyzer):
        """Initialize with required components"""
        self.query_parser = query_parser
        self.state_collector = state_collector
        self.context_builder = context_builder
        self.llm_analyzer = llm_analyzer
    
    def process_query(self, query: str) -> str:
        """Process a single query and return the result"""
        
        # Parse the query
        parsed = self.query_parser.parse(query)
        query_type = parsed['type']
        params = parsed['params']
        
        print(f"[Detected query type: {query_type}]")
        
        # Collect appropriate state based on query type
        if query_type == 'system_status':
            return self._handle_system_status()
            
        elif query_type in ['job_failure', 'job_status']:
            return self._handle_job_query(params)
            
        elif query_type == 'recent_errors':
            return self._handle_recent_errors(params)
            
        else:
            return self._handle_general_query(query)
    
    def _handle_system_status(self) -> str:
        """Handle system status queries"""
        print("[Fetching system state...]")
        state_data = self.state_collector.get_system_overview()
        context = self.context_builder.build_context_for_system_status(state_data)
        return self.llm_analyzer.analyze_system_status(context)
    
    def _handle_job_query(self, params: dict) -> str:
        """Handle job-related queries"""
        job_id = params.get('job_id')
        if not job_id:
            return "Please specify a job ID. Example: 'Why did job abc-123 fail?' or 'Tell me about job abc-123'"
        
        print(f"[Fetching details for job {job_id}...]")
        job_data = self.state_collector.get_job_details(job_id)
        
        if 'error' in job_data and 'not found' in job_data['error'].lower():
            return f"Job {job_id} not found. Please check the job ID."
        
        # Check if job actually failed or succeeded
        job_status = job_data.get('job', {}).get('status', '')
        if job_status == 'completed':
            # Build context for successful job analysis
            context = self.context_builder.build_context_for_job_success(job_data)
            return self.llm_analyzer.analyze_job_success(context)
        else:
            context = self.context_builder.build_context_for_job_failure(job_data)
            return self.llm_analyzer.analyze_job_failure(context)
    
    def _handle_recent_errors(self, params: dict) -> str:
        """Handle recent errors queries"""
        hours = params.get('hours', 1)
        print(f"[Fetching errors from last {hours} hour(s)...]")
        error_data = self.state_collector.get_recent_errors(hours)
        context = self.context_builder.build_context_for_recent_errors(error_data)
        return self.llm_analyzer.analyze_recent_errors(context)
    
    def _handle_general_query(self, query: str) -> str:
        """Handle general queries"""
        print("[Processing general query with enhanced log data...]")
        state_data = self.state_collector.get_system_overview()
        context = self.context_builder.build_context_for_system_status(state_data)
        return self.llm_analyzer.analyze_with_logs(query, context)