# app/core/chart_recommender.py
"""
Apollo AI Chart Recommendation System
Intelligently recommends the best chart types based on data characteristics.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from app.models.schemas import ColumnType, ChartType


class ChartRecommender:
    """
    Intelligent chart recommendation system based on data characteristics.
    """
    
    def __init__(self):
        self.chart_rules = self._initialize_chart_rules()
    
    def _initialize_chart_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize rules for chart recommendations."""
        return {
            ChartType.histogram: {
                'description': 'Distribution of numerical data',
                'best_for': ['numerical_distribution', 'frequency_analysis'],
                'data_requirements': {
                    'primary_type': ColumnType.numeric,
                    'min_unique': 5,
                    'max_unique': None,
                    'sample_size': 10
                }
            },
            ChartType.bar_chart: {
                'description': 'Comparison of categorical data',
                'best_for': ['categorical_comparison', 'ranking'],
                'data_requirements': {
                    'primary_type': ColumnType.categorical,
                    'min_unique': 2,
                    'max_unique': 20,
                    'sample_size': 5
                }
            },
            ChartType.line_chart: {
                'description': 'Trends over time or continuous variables',
                'best_for': ['trends', 'time_series', 'continuous_relationships'],
                'data_requirements': {
                    'primary_type': [ColumnType.datetime, ColumnType.numeric],
                    'min_unique': 3,
                    'max_unique': None,
                    'sample_size': 10
                }
            },
            ChartType.scatter_plot: {
                'description': 'Relationship between two numerical variables',
                'best_for': ['correlation_analysis', 'outlier_detection'],
                'data_requirements': {
                    'primary_type': ColumnType.numeric,
                    'min_unique': 10,
                    'max_unique': None,
                    'sample_size': 20
                }
            },
            ChartType.box_plot: {
                'description': 'Distribution and outliers of numerical data',
                'best_for': ['outlier_analysis', 'distribution_comparison'],
                'data_requirements': {
                    'primary_type': ColumnType.numeric,
                    'min_unique': 5,
                    'max_unique': None,
                    'sample_size': 10
                }
            },
            ChartType.pie_chart: {
                'description': 'Proportions of categorical data',
                'best_for': ['proportion_analysis', 'composition'],
                'data_requirements': {
                    'primary_type': ColumnType.categorical,
                    'min_unique': 2,
                    'max_unique': 8,
                    'sample_size': 5
                }
            },
            ChartType.heatmap: {
                'description': 'Correlation matrix or categorical relationships',
                'best_for': ['correlation_matrix', 'categorical_relationships'],
                'data_requirements': {
                    'primary_type': [ColumnType.numeric, ColumnType.categorical],
                    'min_unique': 3,
                    'max_unique': 50,
                    'sample_size': 10
                }
            },
            ChartType.violin_plot: {
                'description': 'Distribution comparison across categories',
                'best_for': ['distribution_comparison', 'category_analysis'],
                'data_requirements': {
                    'primary_type': ColumnType.numeric,
                    'min_unique': 5,
                    'max_unique': None,
                    'sample_size': 15
                }
            },
            ChartType.density_plot: {
                'description': 'Probability density of numerical data',
                'best_for': ['distribution_analysis', 'probability_density'],
                'data_requirements': {
                    'primary_type': ColumnType.numeric,
                    'min_unique': 10,
                    'max_unique': None,
                    'sample_size': 20
                }
            }
        }
    
    def recommend_charts_for_column(self, column_name: str, column_data: pd.Series, 
                                  column_type: ColumnType) -> List[Dict[str, Any]]:
        """
        Recommend charts for a single column.
        
        Args:
            column_name: Name of the column
            column_data: Pandas Series containing the data
            column_type: Detected column type
            
        Returns:
            List of recommended charts with scores and reasons
        """
        recommendations = []
        non_null_data = column_data.dropna()
        
        if len(non_null_data) == 0:
            return recommendations
        
        unique_count = non_null_data.nunique()
        
        for chart_type, rules in self.chart_rules.items():
            score = self._calculate_chart_score(chart_type, rules, column_type, 
                                             non_null_data, unique_count)
            
            if score > 0:
                recommendations.append({
                    'chart_type': chart_type,
                    'score': score,
                    'description': rules['description'],
                    'reason': self._generate_reason(chart_type, column_type, unique_count, non_null_data),
                    'suitable': score >= 0.7
                })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations
    
    def recommend_charts_for_dataset(self, df: pd.DataFrame, column_types: Dict[str, ColumnType]) -> Dict[str, Any]:
        """
        Recommend charts for the entire dataset.
        
        Args:
            df: DataFrame to analyze
            column_types: Dictionary mapping column names to their types
            
        Returns:
            Dictionary with chart recommendations for each column and combinations
        """
        recommendations = {
            'single_column': {},
            'two_column': [],
            'multi_column': []
        }
        
        # Single column recommendations
        for column in df.columns:
            if column in column_types:
                col_recommendations = self.recommend_charts_for_column(
                    column, df[column], column_types[column]
                )
                recommendations['single_column'][column] = col_recommendations
        
        # Two-column combinations
        numerical_cols = [col for col, t in column_types.items() if t == ColumnType.numeric]
        categorical_cols = [col for col, t in column_types.items() if t == ColumnType.categorical]
        datetime_cols = [col for col, t in column_types.items() if t == ColumnType.datetime]
        
        # Scatter plots for numerical pairs
        for i, col1 in enumerate(numerical_cols):
            for col2 in numerical_cols[i+1:]:
                if self._is_suitable_for_scatter(df[col1], df[col2]):
                    recommendations['two_column'].append({
                        'chart_type': ChartType.SCATTER_PLOT.value,
                        'columns': [col1, col2],
                        'score': 0.9,
                        'description': f'Relationship between {col1} and {col2}',
                        'reason': 'Two numerical variables suitable for correlation analysis'
                    })
        
        # Bar charts for categorical vs numerical
        for cat_col in categorical_cols[:5]:  # Limit to first 5 categorical columns
            for num_col in numerical_cols[:3]:  # Limit to first 3 numerical columns
                if self._is_suitable_for_grouped_bar(df[cat_col], df[num_col]):
                    recommendations['two_column'].append({
                        'chart_type': ChartType.GROUPED_BAR.value,
                        'columns': [cat_col, num_col],
                        'score': 0.8,
                        'description': f'{num_col} by {cat_col}',
                        'reason': 'Categorical vs numerical comparison'
                    })
        
        # Line charts for datetime vs numerical
        for dt_col in datetime_cols:
            for num_col in numerical_cols:
                if self._is_suitable_for_line(df[dt_col], df[num_col]):
                    recommendations['two_column'].append({
                        'chart_type': ChartType.LINE_CHART.value,
                        'columns': [dt_col, num_col],
                        'score': 0.85,
                        'description': f'{num_col} over time ({dt_col})',
                        'reason': 'Time series analysis'
                    })
        
        # Multi-column recommendations
        if len(numerical_cols) >= 3:
            recommendations['multi_column'].append({
                'chart_type': ChartType.HEATMAP.value,
                'columns': numerical_cols,
                'score': 0.9,
                'description': 'Correlation matrix',
                'reason': 'Multiple numerical variables for correlation analysis'
            })
        
        return recommendations
    
    def _calculate_chart_score(self, chart_type: str, rules: Dict[str, Any], 
                             column_type: ColumnType, data: pd.Series, unique_count: int) -> float:
        """Calculate suitability score for a chart type."""
        score = 0.0
        requirements = rules['data_requirements']
        
        # Check primary type requirement
        primary_type = requirements['primary_type']
        if isinstance(primary_type, list):
            if column_type in primary_type:
                score += 0.4
        elif column_type == primary_type:
            score += 0.4
        
        # Check unique count requirements
        min_unique = requirements.get('min_unique', 0)
        max_unique = requirements.get('max_unique')
        
        if unique_count >= min_unique:
            score += 0.2
            if max_unique is None or unique_count <= max_unique:
                score += 0.2
        
        # Check sample size requirement
        min_sample = requirements.get('sample_size', 0)
        if len(data) >= min_sample:
            score += 0.2
        
        # Additional logic for specific chart types
        if chart_type == ChartType.HISTOGRAM.value and column_type == ColumnType.numeric:
            if unique_count > 5:
                score += 0.1
        
        elif chart_type == ChartType.BAR_CHART.value and column_type == ColumnType.categorical:
            if unique_count <= 20:
                score += 0.1
        
        elif chart_type == ChartType.PIE_CHART.value and column_type == ColumnType.categorical:
            if unique_count <= 8:
                score += 0.1
        
        elif chart_type == ChartType.LINE_CHART.value and column_type == ColumnType.datetime:
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_reason(self, chart_type: str, column_type: ColumnType, 
                        unique_count: int, data: pd.Series) -> str:
        """Generate human-readable reason for chart recommendation."""
        reasons = {
            ChartType.HISTOGRAM.value: f"Shows distribution of {column_type.value} data with {unique_count} unique values",
            ChartType.BAR_CHART.value: f"Compares {unique_count} categories in {column_type.value} data",
            ChartType.LINE_CHART.value: f"Shows trends over {column_type.value} data",
            ChartType.SCATTER_PLOT.value: f"Analyzes relationships in {column_type.value} data",
            ChartType.BOX_PLOT.value: f"Shows distribution and outliers in {column_type.value} data",
            ChartType.PIE_CHART.value: f"Shows proportions of {unique_count} categories",
            ChartType.HEATMAP.value: f"Visualizes correlations in {column_type.value} data",
            ChartType.VIOLIN_PLOT.value: f"Shows distribution comparison in {column_type.value} data",
            ChartType.DENSITY_PLOT.value: f"Shows probability density of {column_type.value} data"
        }
        
        return reasons.get(chart_type, f"Suitable for {column_type.value} data analysis")
    
    def _is_suitable_for_scatter(self, col1: pd.Series, col2: pd.Series) -> bool:
        """Check if two columns are suitable for scatter plot."""
        non_null1 = col1.dropna()
        non_null2 = col2.dropna()
        
        if len(non_null1) < 10 or len(non_null2) < 10:
            return False
        
        # Check if both are numerical
        try:
            pd.to_numeric(non_null1, errors='raise')
            pd.to_numeric(non_null2, errors='raise')
            return True
        except:
            return False
    
    def _is_suitable_for_grouped_bar(self, cat_col: pd.Series, num_col: pd.Series) -> bool:
        """Check if categorical and numerical columns are suitable for grouped bar chart."""
        if cat_col.nunique() > 15:  # Too many categories
            return False
        
        try:
            pd.to_numeric(num_col, errors='raise')
            return True
        except:
            return False
    
    def _is_suitable_for_line(self, dt_col: pd.Series, num_col: pd.Series) -> bool:
        """Check if datetime and numerical columns are suitable for line chart."""
        try:
            pd.to_datetime(dt_col, errors='raise')
            pd.to_numeric(num_col, errors='raise')
            return True
        except:
            return False 