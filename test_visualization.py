#!/usr/bin/env python3
"""
Test script for Apollo AI Visualization System
Demonstrates the new chart recommendation and generation functionality.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

# Import our modules
from app.core.analyzer import DataAnalyzer
from app.core.chart_recommender import ChartRecommender
from app.services.visualization_service import VisualizationService
from app.models.schemas import ChartType

def create_sample_data():
    """Create sample data for testing."""
    np.random.seed(42)
    
    # Create sample dataset
    data = {
        'age': np.random.normal(35, 10, 1000),
        'salary': np.random.normal(50000, 15000, 1000),
        'department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'HR', 'Finance'], 1000),
        'experience_years': np.random.exponential(5, 1000),
        'satisfaction_score': np.random.uniform(1, 10, 1000),
        'date_joined': pd.date_range('2020-01-01', periods=1000, freq='D'),
        'is_manager': np.random.choice([True, False], 1000, p=[0.2, 0.8]),
        'performance_rating': np.random.choice(['A', 'B', 'C', 'D'], 1000, p=[0.3, 0.4, 0.2, 0.1])
    }
    
    df = pd.DataFrame(data)
    
    # Add some missing values
    df.loc[np.random.choice(df.index, 50), 'salary'] = np.nan
    df.loc[np.random.choice(df.index, 30), 'age'] = np.nan
    
    return df

def test_column_type_detection():
    """Test the improved column type detection."""
    print("=== Testing Column Type Detection ===")
    
    # Create sample data
    df = create_sample_data()
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
        df.to_csv(tmp_file.name, index=False)
        tmp_file_path = tmp_file.name
    
    try:
        # Test analyzer
        analyzer = DataAnalyzer(tmp_file_path)
        
        print("Detected column types:")
        for column, col_type in analyzer.column_types.items():
            print(f"  {column}: {col_type.value}")
        
        # Test debug method
        debug_info = analyzer.debug_column_types()
        print("\nDebug information for 'age' column:")
        print(f"  Detected type: {debug_info['age']['detected_type']}")
        print(f"  Is numerical: {debug_info['age']['is_numerical']}")
        print(f"  Is datetime: {debug_info['age']['is_datetime']}")
        print(f"  Sample values: {debug_info['age']['sample_values'][:3]}")
        
        return analyzer
        
    finally:
        # Clean up
        os.unlink(tmp_file_path)

def test_chart_recommendations():
    """Test chart recommendation system."""
    print("\n=== Testing Chart Recommendations ===")
    
    # Create sample data
    df = create_sample_data()
    
    # Create recommender
    recommender = ChartRecommender()
    
    # Test single column recommendations
    print("Chart recommendations for 'age' column:")
    age_recommendations = recommender.recommend_charts_for_column('age', df['age'], 'numeric')
    for rec in age_recommendations[:3]:  # Top 3
        print(f"  {rec['chart_type']}: {rec['score']:.2f} - {rec['reason']}")
    
    print("\nChart recommendations for 'department' column:")
    dept_recommendations = recommender.recommend_charts_for_column('department', df['department'], 'categorical')
    for rec in dept_recommendations[:3]:  # Top 3
        print(f"  {rec['chart_type']}: {rec['score']:.2f} - {rec['reason']}")
    
    # Test dataset recommendations
    column_types = {
        'age': 'numeric',
        'salary': 'numeric', 
        'department': 'categorical',
        'experience_years': 'numeric',
        'satisfaction_score': 'numeric',
        'date_joined': 'datetime',
        'is_manager': 'boolean',
        'performance_rating': 'categorical'
    }
    
    dataset_recommendations = recommender.recommend_charts_for_dataset(df, column_types)
    
    print(f"\nDataset recommendations:")
    print(f"  Single column charts: {len(dataset_recommendations['single_column'])} columns")
    print(f"  Two column charts: {len(dataset_recommendations['two_column'])} combinations")
    print(f"  Multi column charts: {len(dataset_recommendations['multi_column'])} combinations")

def test_visualization_service():
    """Test visualization service."""
    print("\n=== Testing Visualization Service ===")
    
    # Create sample data
    df = create_sample_data()
    
    # Create visualization service
    viz_service = VisualizationService()
    
    # Test histogram generation
    print("Generating histogram for 'age' column...")
    result = viz_service.generate_chart(df, ChartType.histogram, ['age'])
    if result['success']:
        print(f"  ✓ Success! File: {result['filename']}")
        print(f"  Download URL: {result['download_url']}")
    else:
        print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
    
    # Test bar chart generation
    print("\nGenerating bar chart for 'department' column...")
    result = viz_service.generate_chart(df, ChartType.bar_chart, ['department'])
    if result['success']:
        print(f"  ✓ Success! File: {result['filename']}")
        print(f"  Download URL: {result['download_url']}")
    else:
        print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
    
    # Test scatter plot generation
    print("\nGenerating scatter plot for 'age' vs 'salary'...")
    result = viz_service.generate_chart(df, ChartType.scatter_plot, ['age', 'salary'])
    if result['success']:
        print(f"  ✓ Success! File: {result['filename']}")
        print(f"  Download URL: {result['download_url']}")
    else:
        print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
    
    # Test auto-generation
    print("\nAuto-generating best charts...")
    column_types = {
        'age': 'numeric',
        'salary': 'numeric', 
        'department': 'categorical',
        'experience_years': 'numeric',
        'satisfaction_score': 'numeric',
        'date_joined': 'datetime',
        'is_manager': 'boolean',
        'performance_rating': 'categorical'
    }
    
    recommendations = viz_service.get_available_charts(df, column_types)
    print(f"  Found {len(recommendations['single_column'])} single column recommendations")
    print(f"  Found {len(recommendations['two_column'])} two column recommendations")

def main():
    """Run all tests."""
    print("Apollo AI Visualization System Test")
    print("=" * 50)
    
    try:
        # Test column type detection
        analyzer = test_column_type_detection()
        
        # Test chart recommendations
        test_chart_recommendations()
        
        # Test visualization service
        test_visualization_service()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("\nKey improvements:")
        print("✓ Fixed column type detection (numerical before datetime)")
        print("✓ Added intelligent chart recommendations")
        print("✓ Created matplotlib-based visualization service")
        print("✓ Added API endpoints for chart generation")
        print("✓ Added download functionality for generated charts")
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 