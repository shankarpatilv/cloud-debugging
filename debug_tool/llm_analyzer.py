"""LLM analyzer wrapper that imports from analyzers and prompts"""

import os
from typing import Optional
from openai import OpenAI
from analyzers.job_analyzer import JobAnalyzer
from prompts.system_prompts import SystemPrompts


class LLMAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo"
        self.job_analyzer = JobAnalyzer(self.client, self.model)
        self.prompts = SystemPrompts()
    
    def analyze_system_status(self, context: str) -> str:
        """Analyze current system status"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.prompts.get_system_status_prompt()
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
    
    def analyze_job_failure(self, context: str) -> str:
        """Analyze why a job failed"""
        return self.job_analyzer.analyze_job_failure(context)
    
    def analyze_job_success(self, context: str) -> str:
        """Analyze a successful job"""
        return self.job_analyzer.analyze_job_success(context)
    
    def analyze_recent_errors(self, context: str) -> str:
        """Analyze patterns in recent errors"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.prompts.get_recent_errors_prompt()
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
    
    def analyze_general(self, query: str, context: str) -> str:
        """Handle general queries"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.prompts.get_general_prompt()
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nContext:\n{context}"
                    }
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error calling LLM: {str(e)}"