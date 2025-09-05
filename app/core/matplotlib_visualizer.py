"""
Apollo AI Matplotlib Visualizer
Generates interactive matplotlib visualizations with plotly for web integration.
Replaces Chart.js with more professional, interactive charts.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional, Union
import json
import base64
from io import BytesIO
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set style for better-looking plots
style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class MatplotlibVisualizer:
    """
    Professional matplotlib/plotly visualizer for interactive charts.
    Julius AI-style interactive visualizations.
    """
    
    def __init__(self, df: pd.DataFrame):
        """Initialize visualizer with DataFrame."""
        self.df = df
        self.numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.datetime_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Configure plotly default theme
        self.plotly_theme = "plotly_white"
        self.color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                             '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    def generate_histogram(self, column: str, bins: int = 30) -> Dict[str, Any]:
        """Generate interactive histogram using Plotly."""
        if column not in self.numeric_columns:
            raise ValueError(f"Column '{column}' is not numeric")
        
        # Create plotly histogram
        fig = px.histogram(
            self.df, 
            x=column,
            nbins=bins,
            title=f'Distribution of {column}',
            template=self.plotly_theme,
            color_discrete_sequence=self.color_palette
        )
        
        # Customize layout
        fig.update_layout(
            title={
                'text': f'Distribution of {column}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title=column,
            yaxis_title='Frequency',
            showlegend=False,
            hovermode='x unified'
        )
        
        # Add statistical info
        stats = {
            'mean': float(self.df[column].mean()),
            'median': float(self.df[column].median()),
            'std': float(self.df[column].std()),
            'min': float(self.df[column].min()),
            'max': float(self.df[column].max())
        }
        
        return {
            'chart_type': 'histogram',
            'plotly_json': fig.to_json(),
            'statistics': stats,
            'insights': [
                f"Mean: {stats['mean']:.2f}",
                f"Median: {stats['median']:.2f}",
                f"Standard Deviation: {stats['std']:.2f}",
                f"Range: {stats['min']:.2f} to {stats['max']:.2f}"
            ]
        }
    
    def generate_scatter_plot(self, x_column: str, y_column: str, color_column: Optional[str] = None) -> Dict[str, Any]:
        """Generate interactive scatter plot using Plotly."""
        if x_column not in self.numeric_columns or y_column not in self.numeric_columns:
            raise ValueError("Both X and Y columns must be numeric")
        
        # Create scatter plot
        if color_column and color_column in self.categorical_columns:
            fig = px.scatter(
                self.df, 
                x=x_column, 
                y=y_column,
                color=color_column,
                title=f'{y_column} vs {x_column}',
                template=self.plotly_theme,
                hover_data=[color_column]
            )
        else:
            fig = px.scatter(
                self.df, 
                x=x_column, 
                y=y_column,
                title=f'{y_column} vs {x_column}',
                template=self.plotly_theme,
                color_discrete_sequence=self.color_palette
            )
        
        # Customize layout
        fig.update_layout(
            title={
                'text': f'{y_column} vs {x_column}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title=x_column,
            yaxis_title=y_column
        )
        
        # Calculate correlation
        correlation = self.df[x_column].corr(self.df[y_column])
        
        return {
            'chart_type': 'scatter',
            'plotly_json': fig.to_json(),
            'correlation': float(correlation),
            'insights': [
                f"Correlation coefficient: {correlation:.3f}",
                f"Relationship strength: {self._interpret_correlation(correlation)}"
            ]
        }
    
    def generate_bar_chart(self, column: str, limit: int = 20) -> Dict[str, Any]:
        """Generate interactive bar chart for categorical data."""
        if column not in self.categorical_columns:
            raise ValueError(f"Column '{column}' is not categorical")
        
        # Get value counts
        value_counts = self.df[column].value_counts().head(limit)
        
        # Create bar chart
        fig = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            title=f'Distribution of {column}',
            template=self.plotly_theme,
            color_discrete_sequence=self.color_palette
        )
        
        # Customize layout
        fig.update_layout(
            title={
                'text': f'Distribution of {column}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title=column,
            yaxis_title='Count',
            showlegend=False
        )
        
        # Rotate x-axis labels if too long
        if len(str(value_counts.index[0])) > 10:
            fig.update_xaxes(tickangle=45)
        
        return {
            'chart_type': 'bar',
            'plotly_json': fig.to_json(),
            'top_values': value_counts.to_dict(),
            'insights': [
                f"Most common value: {value_counts.index[0]} ({value_counts.iloc[0]} occurrences)",
                f"Total unique values: {self.df[column].nunique()}",
                f"Showing top {min(limit, len(value_counts))} values"
            ]
        }
    
    def generate_line_chart(self, x_column: str, y_column: str) -> Dict[str, Any]:
        """Generate interactive line chart for time series or ordered data."""
        # Sort by x_column for proper line ordering
        df_sorted = self.df.sort_values(x_column)
        
        # Create line chart
        fig = px.line(
            df_sorted,
            x=x_column,
            y=y_column,
            title=f'{y_column} over {x_column}',
            template=self.plotly_theme,
            color_discrete_sequence=self.color_palette
        )
        
        # Customize layout
        fig.update_layout(
            title={
                'text': f'{y_column} over {x_column}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis_title=x_column,
            yaxis_title=y_column
        )
        
        return {
            'chart_type': 'line',
            'plotly_json': fig.to_json(),
            'insights': [
                f"Data points: {len(df_sorted)}",
                f"Range: {df_sorted[y_column].min():.2f} to {df_sorted[y_column].max():.2f}"
            ]
        }
    
    def generate_box_plot(self, column: str, group_by: Optional[str] = None) -> Dict[str, Any]:
        """Generate interactive box plot for statistical distribution."""
        if column not in self.numeric_columns:
            raise ValueError(f"Column '{column}' is not numeric")
        
        if group_by and group_by in self.categorical_columns:
            fig = px.box(
                self.df,
                x=group_by,
                y=column,
                title=f'Distribution of {column} by {group_by}',
                template=self.plotly_theme,
                color=group_by
            )
        else:
            fig = px.box(
                self.df,
                y=column,
                title=f'Distribution of {column}',
                template=self.plotly_theme,
                color_discrete_sequence=self.color_palette
            )
        
        # Customize layout
        fig.update_layout(
            title={
                'text': f'Distribution of {column}' + (f' by {group_by}' if group_by else ''),
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            }
        )
        
        # Calculate quartiles
        q1 = self.df[column].quantile(0.25)
        q2 = self.df[column].quantile(0.5)
        q3 = self.df[column].quantile(0.75)
        iqr = q3 - q1
        
        return {
            'chart_type': 'box',
            'plotly_json': fig.to_json(),
            'quartiles': {
                'Q1': float(q1),
                'Q2 (Median)': float(q2),
                'Q3': float(q3),
                'IQR': float(iqr)
            },
            'insights': [
                f"Median: {q2:.2f}",
                f"IQR: {iqr:.2f}",
                f"Potential outliers detected" if self._detect_outliers(column) else "No outliers detected"
            ]
        }
    
    def generate_correlation_heatmap(self, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate interactive correlation heatmap."""
        if columns:
            numeric_cols = [col for col in columns if col in self.numeric_columns]
        else:
            numeric_cols = self.numeric_columns[:10]  # Limit to first 10 for readability
        
        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for correlation heatmap")
        
        # Calculate correlation matrix
        corr_matrix = self.df[numeric_cols].corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            title='Correlation Heatmap',
            template=self.plotly_theme,
            color_continuous_scale='RdBu',
            zmin=-1,
            zmax=1
        )
        
        # Customize layout
        fig.update_layout(
            title={
                'text': 'Correlation Heatmap',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            }
        )
        
        return {
            'chart_type': 'heatmap',
            'plotly_json': fig.to_json(),
            'correlation_matrix': corr_matrix.to_dict(),
            'insights': [
                f"Strongest positive correlation: {self._find_strongest_correlation(corr_matrix, positive=True)}",
                f"Strongest negative correlation: {self._find_strongest_correlation(corr_matrix, positive=False)}"
            ]
        }
    
    def get_available_visualizations(self) -> Dict[str, List[str]]:
        """Get available visualization types based on data."""
        visualizations = {
            'single_column': {},
            'two_column': {},
            'multi_column': {}
        }
        
        # Single column charts
        for col in self.numeric_columns:
            visualizations['single_column'][col] = ['histogram', 'box_plot']
        
        for col in self.categorical_columns:
            visualizations['single_column'][col] = ['bar_chart']
        
        # Two column charts
        for i, col1 in enumerate(self.numeric_columns):
            for col2 in self.numeric_columns[i+1:]:
                key = f"{col1}_vs_{col2}"
                visualizations['two_column'][key] = ['scatter_plot', 'line_chart']
        
        # Multi-column charts
        if len(self.numeric_columns) >= 2:
            visualizations['multi_column']['all_numeric'] = ['correlation_heatmap']
        
        return visualizations
    
    def _interpret_correlation(self, corr: float) -> str:
        """Interpret correlation strength."""
        abs_corr = abs(corr)
        if abs_corr >= 0.7:
            return "Strong"
        elif abs_corr >= 0.3:
            return "Moderate"
        else:
            return "Weak"
    
    def _detect_outliers(self, column: str) -> bool:
        """Simple outlier detection using IQR method."""
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = self.df[(self.df[column] < lower_bound) | (self.df[column] > upper_bound)]
        return len(outliers) > 0
    
    def _find_strongest_correlation(self, corr_matrix: pd.DataFrame, positive: bool = True) -> str:
        """Find strongest correlation in matrix."""
        # Create copy and remove self-correlations
        corr_copy = corr_matrix.copy()
        np.fill_diagonal(corr_copy.values, 0)
        
        if positive:
            max_corr = corr_copy.max().max()
            if max_corr > 0:
                max_loc = corr_copy.stack().idxmax()
                return f"{max_loc[0]} & {max_loc[1]} ({max_corr:.3f})"
        else:
            min_corr = corr_copy.min().min()
            if min_corr < 0:
                min_loc = corr_copy.stack().idxmin()
                return f"{min_loc[0]} & {min_loc[1]} ({min_corr:.3f})"
        
        return "None found"
