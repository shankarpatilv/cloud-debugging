"""Filter operation for data processing"""

import pandas as pd
from typing import Dict, Any


class FilterOperation:
    def __init__(self, df: pd.DataFrame):
        """Initialize filter operation with dataset"""
        self.df = df
    
    def execute(self, params: Dict[str, Any]) -> pd.DataFrame:
        """Filter rows based on condition"""
        column = params.get('column')
        operator = params.get('operator')
        value = params.get('value')
        
        if not all([column, operator, value]):
            raise ValueError("Filter requires column, operator, and value")
        
        if operator == '==':
            return self.df[self.df[column] == value]
        elif operator == '!=':
            return self.df[self.df[column] != value]
        elif operator == '>':
            return self.df[self.df[column] > value]
        elif operator == '<':
            return self.df[self.df[column] < value]
        elif operator == '>=':
            return self.df[self.df[column] >= value]
        elif operator == '<=':
            return self.df[self.df[column] <= value]
        else:
            raise ValueError(f"Unsupported operator: {operator}")