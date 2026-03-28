"""Job-specific analysis methods"""

from openai import OpenAI
from prompts.system_prompts import SystemPrompts


class JobAnalyzer:
    def __init__(self, client: OpenAI, model: str = "gpt-3.5-turbo"):
        """Initialize with OpenAI client and model"""
        self.client = client
        self.model = model
    
    def analyze_job_failure(self, context: str) -> str:
        """Analyze why a job failed"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": SystemPrompts.get_job_failure_prompt()
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.2,
                max_tokens=600
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
    
    def analyze_job_success(self, context: str) -> str:
        """Analyze a successful job"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": SystemPrompts.get_job_success_prompt()
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