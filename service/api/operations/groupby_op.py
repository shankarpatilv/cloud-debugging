"""Groupby operation for data processing"""

import pandas as pd
from typing import Dict, Any


class GroupbyOperation:
    def __init__(self, df: pd.DataFrame):
        """Initialize groupby operation with dataset"""
        self.df = df
    
    def execute(self, params: Dict[str, Any]) -> pd.DataFrame:
        """Group by columns and aggregate"""
        by = params.get('by')
        agg = params.get('agg', {})
        
        if not by:
            raise ValueError("Groupby requires 'by' parameter")
        
        if not agg:
            # Default to count if no aggregation specified
            return self.df.groupby(by).size().reset_index(name='count')
        
        return self.df.groupby(by).agg(agg).reset_index()