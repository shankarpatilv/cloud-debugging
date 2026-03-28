"""Interactive mode handler for CLI"""

from query_parser import QueryParser
from state_collector import StateCollector
from context_builder import ContextBuilder
from llm_analyzer import LLMAnalyzer
from .query_processor import QueryProcessor


class InteractiveMode:
    def __init__(self, query_parser: QueryParser, state_collector: StateCollector,
                 context_builder: ContextBuilder, llm_analyzer: LLMAnalyzer):
        """Initialize with required components"""
        self.query_processor = QueryProcessor(
            query_parser, state_collector, context_builder, llm_analyzer
        )
    
    def run(self):
        """Run interactive mode"""
        print("🔍 LLM Debug Tool - Interactive Mode")
        print("Type 'quit' or 'exit' to leave")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n> ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                if query:
                    result = self.query_processor.process_query(query)
                    print("\n" + result)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    @staticmethod
    def show_header():
        """Show interactive mode header"""
        print("🔍 LLM Debug Tool - Interactive Mode")
        print("Type 'quit' or 'exit' to leave")
        print("-" * 50)