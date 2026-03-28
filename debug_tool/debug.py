#!/usr/bin/env python3
"""Main CLI for LLM-powered debugging tool"""

import os
import sys
import argparse
from dotenv import load_dotenv

from query_parser import QueryParser
from state_collector import StateCollector
from context_builder import ContextBuilder
from llm_analyzer import LLMAnalyzer
from cli.interactive_mode import InteractiveMode
from cli.query_processor import QueryProcessor


def main():
    """Main entry point for debug tool"""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Check API key
    if not args.api_key:
        print("Error: OpenAI API key required. Set OPENAI_API_KEY or use --api-key")
        sys.exit(1)
    
    # Initialize components
    components = initialize_components(args)
    if not components:
        sys.exit(1)
    
    query_parser, state_collector, context_builder, llm_analyzer = components
    
    # Test API connection
    test_api_connection(state_collector, args.api_url)
    
    # Handle different execution modes
    if args.interactive:
        interactive_mode = InteractiveMode(query_parser, state_collector, context_builder, llm_analyzer)
        interactive_mode.run()
    elif args.query:
        query_processor = QueryProcessor(query_parser, state_collector, context_builder, llm_analyzer)
        result = query_processor.process_query(args.query)
        print(result)
    else:
        parser.print_help()


def create_argument_parser():
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description='LLM-powered debugging tool for data processing service',
        epilog="""
Examples:
  python debug.py "What is the system doing right now?"
  python debug.py "Why did job abc-123 fail?"
  python debug.py "What are recent errors?"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('query', nargs='?', help='Natural language query about the system')
    parser.add_argument('--api-url', default=os.getenv('API_URL', 'http://localhost:8000'),
                       help='API endpoint URL (default: http://localhost:8000)')
    parser.add_argument('--api-key', default=os.getenv('OPENAI_API_KEY'),
                       help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Interactive mode for multiple queries')
    
    return parser


def initialize_components(args):
    """Initialize all required components"""
    try:
        query_parser = QueryParser()
        state_collector = StateCollector(args.api_url)
        context_builder = ContextBuilder()
        llm_analyzer = LLMAnalyzer(args.api_key)
        return query_parser, state_collector, context_builder, llm_analyzer
    except Exception as e:
        print(f"Error initializing components: {e}")
        return None


def test_api_connection(state_collector, api_url):
    """Test API connection and show warning if needed"""
    if not state_collector.test_connection():
        print(f"Warning: Cannot connect to API at {api_url}")
        print("Make sure the service is running: cd service && uvicorn api.main:app --reload")


if __name__ == '__main__':
    main()