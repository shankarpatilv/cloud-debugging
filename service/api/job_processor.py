"""Job processor that orchestrates data operations"""

import pandas as pd
import os
from typing import Dict, Any

from .operations.filter_op import FilterOperation
from .operations.select_op import SelectOperation
from .operations.groupby_op import GroupbyOperation
from .operations.sort_op import SortOperation


class JobProcessor:
    def __init__(self):
        """Initialize processor and load dataset"""
        data_path = os.getenv('DATA_PATH', 'data/churn_data.csv')
        self.df = pd.read_csv(data_path)
        self.columns = list(self.df.columns)
        self.dtypes = self.df.dtypes.to_dict()
        print(f"Dataset loaded: {len(self.df)} rows, {len(self.columns)} columns")
        
        # Initialize operations
        self.filter_op = FilterOperation(self.df)
        self.select_op = SelectOperation(self.df)
        self.groupby_op = GroupbyOperation(self.df)
        self.sort_op = SortOperation(self.df)
    
    def process(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a job and return results or error"""
        try:
            if operation == "filter":
                result_df = self.filter_op.execute(params)
            elif operation == "select":
                result_df = self.select_op.execute(params)
            elif operation == "groupby":
                result_df = self.groupby_op.execute(params)
            elif operation == "sort":
                result_df = self.sort_op.execute(params)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            # Return summary, not full dataset
            return {
                'success': True,
                'row_count': len(result_df),
                'columns': list(result_df.columns),
                'shape': result_df.shape,
                'preview': result_df.head(10).to_dict('records')
            }
            
        except KeyError as e:
            # Column not found - provide helpful error
            wrong_column = str(e).strip("'\"")
            suggestion = self._suggest_column(wrong_column)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'KeyError',
                'message': f"Column {str(e)} not found in dataset",
                'available_columns': self.columns,
                'suggestion': suggestion
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'message': f"Operation failed: {str(e)}"
            }
    
    def _suggest_column(self, wrong_column: str) -> str:
        """Suggest correct column name"""
        wrong_lower = wrong_column.lower().replace('_', ' ')
        
        for col in self.columns:
            if col.lower() == wrong_lower:
                return f"Did you mean '{col}'? (Note: column names use spaces, not underscores)"
        
        # Look for partial matches
        for col in self.columns:
            if wrong_lower in col.lower() or col.lower() in wrong_lower:
                return f"Did you mean '{col}'?"
        
        return None