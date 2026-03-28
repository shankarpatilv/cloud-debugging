"""Sort operation for data processing"""

import pandas as pd
from typing import Dict, Any


class SortOperation:
    def __init__(self, df: pd.DataFrame):
        """Initialize sort operation with dataset"""
        self.df = df
    
    def execute(self, params: Dict[str, Any]) -> pd.DataFrame:
        """Sort data by column(s)"""
        column = params.get('column')
        ascending = params.get('ascending', True)
        
        if not column:
            raise ValueError("Sort requires column parameter")
        
        return self.df.sort_values(column, ascending=ascending)