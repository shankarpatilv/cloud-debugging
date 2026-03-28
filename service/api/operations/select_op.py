"""Select operation for data processing"""

import pandas as pd
from typing import Dict, Any


class SelectOperation:
    def __init__(self, df: pd.DataFrame):
        """Initialize select operation with dataset"""
        self.df = df
    
    def execute(self, params: Dict[str, Any]) -> pd.DataFrame:
        """Select specific columns"""
        columns = params.get('columns', [])
        if not columns:
            raise ValueError("Select requires columns list")
        
        return self.df[columns]