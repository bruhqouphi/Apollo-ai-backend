#!/usr/bin/env python3
"""
Debug script to test CSV loading and identify the column issue
"""

import pandas as pd
from pathlib import Path

def test_csv_loading():
    """Test loading the sample CSV file"""
    
    # Test the sample sales data
    csv_path = Path("sample_sales_data.csv")
    
    print(f"CSV file exists: {csv_path.exists()}")
    print(f"CSV file size: {csv_path.stat().st_size} bytes")
    
    try:
        # Try to read the CSV
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        print(f"Successfully loaded CSV")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Number of columns: {len(df.columns)}")
        print(f"First few rows:")
        print(df.head(3))
        
        # Check for any issues
        print(f"\nColumn info:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: '{col}' (type: {df[col].dtype})")
            
    except Exception as e:
        print(f"Error loading CSV: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_csv_loading() 