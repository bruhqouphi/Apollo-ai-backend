# app/services/visualization_service.py
"""
Apollo AI Visualization Service
Matplotlib-based chart generation and export functionality.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import io
import base64
from datetime import datetime
import warnings

# Import our chart recommender
from app.core.chart_recommender import ChartType, ChartRecommender
from app.models.schemas import ColumnType

# Suppress matplotlib warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class VisualizationService:
    """
    Service for generating matplotlib charts and exporting them.
    """
    
    def __init__(self, output_dir: str = "temp_charts"):
        """
        Initialize the visualization service.
        
        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.chart_recommender = ChartRecommender()
        
        # Set figure size and DPI for better quality
        self.default_figsize = (10, 6)
        self.default_dpi = 300
    
    def generate_chart(self, df: pd.DataFrame, chart_type: str, 
                      columns: List[str], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a chart based on the specified type and columns.
        
        Args:
            df: DataFrame containing the data
            chart_type: Type of chart to generate
            columns: List of column names to use
            options: Additional options for chart customization
            
        Returns:
            Dictionary containing chart data and metadata
        """
        if options is None:
            options = {}
        
        try:
            if chart_type == ChartType.histogram:
                return self._create_histogram(df, columns[0], options)
            elif chart_type == ChartType.bar_chart:
                return self._create_bar_chart(df, columns[0], options)
            elif chart_type == ChartType.line_chart:
                return self._create_line_chart(df, columns, options)
            elif chart_type == ChartType.scatter_plot:
                return self._create_scatter_plot(df, columns[0], columns[1], options)
            elif chart_type == ChartType.box_plot:
                return self._create_box_plot(df, columns[0], options)
            elif chart_type == ChartType.pie_chart:
                return self._create_pie_chart(df, columns[0], options)
            elif chart_type == ChartType.heatmap:
                return self._create_heatmap(df, columns, options)
            elif chart_type == ChartType.violin_plot:
                return self._create_violin_plot(df, columns[0], options)
            elif chart_type == ChartType.density_plot:
                return self._create_density_plot(df, columns[0], options)
            elif chart_type == ChartType.grouped_bar:
                return self._create_grouped_bar_chart(df, columns[0], columns[1], options)
            elif chart_type == ChartType.stacked_bar:
                return self._create_stacked_bar_chart(df, columns[0], columns[1], options)
            elif chart_type == ChartType.area_chart:
                return self._create_area_chart(df, columns, options)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'chart_type': chart_type,
                'columns': columns
            }
    
    def _create_histogram(self, df: pd.DataFrame, column: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a histogram chart."""
        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)
        
        data = pd.to_numeric(df[column], errors='coerce').dropna()
        bins = options.get('bins', 30)
        
        ax.hist(data, bins=bins, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_xlabel(column)
        ax.set_ylabel('Frequency')
        ax.set_title(f'Distribution of {column}')
        ax.grid(True, alpha=0.3)
        
        return self._finalize_chart(fig, f"histogram_{column}")
    
    def _create_bar_chart(self, df: pd.DataFrame, column: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a bar chart."""
        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)
        
        value_counts = df[column].value_counts()
        top_n = options.get('top_n', 10)
        value_counts = value_counts.head(top_n)
        
        bars = ax.bar(range(len(value_counts)), value_counts.values, 
                     color='lightcoral', alpha=0.8)
        ax.set_xlabel(column)
        ax.set_ylabel('Count')
        ax.set_title(f'Top {top_n} Values in {column}')
        ax.set_xticks(range(len(value_counts)))
        ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        return self._finalize_chart(fig, f"bar_chart_{column}")
    
    def _create_line_chart(self, df: pd.DataFrame, columns: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a line chart."""
        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)
        
        if len(columns) == 2:
            x_col, y_col = columns[0], columns[1]
            
            # Try to convert x-axis to datetime if it's not already
            try:
                x_data = pd.to_datetime(df[x_col])
                y_data = pd.to_numeric(df[y_col], errors='coerce')
            except:
                x_data = df[x_col]
                y_data = pd.to_numeric(df[y_col], errors='coerce')
            
            # Sort by x-axis
            sorted_data = pd.DataFrame({'x': x_data, 'y': y_data}).dropna().sort_values('x')
            
            ax.plot(sorted_data['x'], sorted_data['y'], marker='o', linewidth=2, markersize=4)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f'{y_col} over {x_col}')
            ax.grid(True, alpha=0.3)
            
            # Rotate x-axis labels if needed
            if len(sorted_data) > 10:
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        return self._finalize_chart(fig, f"line_chart_{'_'.join(columns)}")
    
    def _create_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a scatter plot."""
        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)
        
        x_data = pd.to_numeric(df[x_col], errors='coerce')
        y_data = pd.to_numeric(df[y_col], errors='coerce')
        
        # Remove rows with NaN values
        valid_data = pd.DataFrame({'x': x_data, 'y': y_data}).dropna()
        
        ax.scatter(valid_data['x'], valid_data['y'], alpha=0.6, s=30)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'{y_col} vs {x_col}')
        ax.grid(True, alpha=0.3)
        
        # Add trend line if requested
        if options.get('trend_line', False) and len(valid_data) > 2:
            z = np.polyfit(valid_data['x'], valid_data['y'], 1)
            p = np.poly1d(z)
            ax.plot(valid_data['x'], p(valid_data['x']), "r--", alpha=0.8)
        
        return self._finalize_chart(fig, f"scatter_{x_col}_{y_col}")
    
    def _create_box_plot(self, df: pd.DataFrame, column: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a box plot."""
        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)
        
        data = pd.to_numeric(df[column], errors='coerce').dropna()
        
        ax.boxplot(data, patch_artist=True, 
                  boxprops=dict(facecolor='lightblue', alpha=0.7))
        ax.set_ylabel(column)
        ax.set_title(f'Box Plot of {column}')
        ax.grid(True, alpha=0.3)
        
        return self._finalize_chart(fig, f"box_plot_{column}")
    
    def _create_pie_chart(self, df: pd.DataFrame, column: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a pie chart."""
        fig, ax = plt.subplots(figsize=(8, 8), dpi=self.default_dpi)
        
        value_counts = df[column].value_counts()
        top_n = options.get('top_n', 8)
        value_counts = value_counts.head(top_n)
        
        # Combine small values into "Others"
        if len(value_counts) > top_n:
            others_sum = value_counts.iloc[top_n:].sum()
            value_counts = value_counts.head(top_n)
            value_counts['Others'] = others_sum
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(value_counts)))
        wedges, texts, autotexts = ax.pie(value_counts.values, labels=value_counts.index, 
                                         autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title(f'Distribution of {column}')
        
        return self._finalize_chart(fig, f"pie_chart_{column}")
    
    def _create_heatmap(self, df: pd.DataFrame, columns: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a correlation heatmap."""
        fig, ax = plt.subplots(figsize=(10, 8), dpi=self.default_dpi)
        
        # Select numerical columns
        numerical_data = df[columns].select_dtypes(include=[np.number])
        
        if numerical_data.empty:
            raise ValueError("No numerical columns found for heatmap")
        
        # Calculate correlation matrix
        corr_matrix = numerical_data.corr()
        
        # Create heatmap
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, ax=ax, fmt='.2f')
        ax.set_title('Correlation Matrix')
        
        return self._finalize_chart(fig, f"heatmap_{'_'.join(columns[:3])}")
    
    def _create_violin_plot(self, df: pd.DataFrame, column: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a violin plot."""
        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)
        
        data = pd.to_numeric(df[column], errors='coerce').dropna()
        
        ax.violinplot(data, showmeans=True)
        ax.set_ylabel(column)
        ax.set_title(f'Distribution of {column}')
        ax.grid(True, alpha=0.3)
        
        return self._finalize_chart(fig, f"violin_plot_{column}")
    
    def _create_density_plot(self, df: pd.DataFrame, column: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a density plot."""
        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)
        
        data = pd.to_numeric(df[column], errors='coerce').dropna()
        
        data.plot.kde(ax=ax, color='purple', linewidth=2)
        ax.set_xlabel(column)
        ax.set_ylabel('Density')
        ax.set_title(f'Density Plot of {column}')
        ax.grid(True, alpha=0.3)
        
        return self._finalize_chart(fig, f"density_plot_{column}")
    
    def _create_grouped_bar_chart(self, df: pd.DataFrame, cat_col: str, num_col: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a grouped bar chart."""
        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)
        
        # Group by categorical column and calculate mean of numerical column
        grouped_data = df.groupby(cat_col)[num_col].mean().sort_values(ascending=False)
        top_n = options.get('top_n', 10)
        grouped_data = grouped_data.head(top_n)
        
        bars = ax.bar(range(len(grouped_data)), grouped_data.values, 
                     color='lightgreen', alpha=0.8)
        ax.set_xlabel(cat_col)
        ax.set_ylabel(f'Mean {num_col}')
        ax.set_title(f'Mean {num_col} by {cat_col}')
        ax.set_xticks(range(len(grouped_data)))
        ax.set_xticklabels(grouped_data.index, rotation=45, ha='right')
        
        return self._finalize_chart(fig, f"grouped_bar_{cat_col}_{num_col}")
    
    def _create_stacked_bar_chart(self, df: pd.DataFrame, cat_col: str, num_col: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a stacked bar chart."""
        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)
        
        # Create pivot table
        pivot_data = df.pivot_table(index=cat_col, columns=num_col, aggfunc='size', fill_value=0)
        
        pivot_data.plot(kind='bar', stacked=True, ax=ax)
        ax.set_xlabel(cat_col)
        ax.set_ylabel('Count')
        ax.set_title(f'Stacked Bar Chart: {num_col} by {cat_col}')
        ax.legend(title=num_col, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        return self._finalize_chart(fig, f"stacked_bar_{cat_col}_{num_col}")
    
    def _create_area_chart(self, df: pd.DataFrame, columns: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """Create an area chart."""
        fig, ax = plt.subplots(figsize=self.default_figsize, dpi=self.default_dpi)
        
        if len(columns) == 2:
            x_col, y_col = columns[0], columns[1]
            
            try:
                x_data = pd.to_datetime(df[x_col])
                y_data = pd.to_numeric(df[y_col], errors='coerce')
            except:
                x_data = df[x_col]
                y_data = pd.to_numeric(df[y_col], errors='coerce')
            
            sorted_data = pd.DataFrame({'x': x_data, 'y': y_data}).dropna().sort_values('x')
            
            ax.fill_between(sorted_data['x'], sorted_data['y'], alpha=0.6, color='lightblue')
            ax.plot(sorted_data['x'], sorted_data['y'], color='blue', linewidth=2)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f'Area Chart: {y_col} over {x_col}')
            ax.grid(True, alpha=0.3)
        
        return self._finalize_chart(fig, f"area_chart_{'_'.join(columns)}")
    
    def _finalize_chart(self, fig: plt.Figure, filename: str) -> Dict[str, Any]:
        """Finalize chart and prepare for export."""
        # Adjust layout
        plt.tight_layout()
        
        # Save to file
        file_path = self.output_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.savefig(file_path, dpi=self.default_dpi, bbox_inches='tight')
        
        # Convert to base64 for web display
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=self.default_dpi, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Close figure to free memory
        plt.close(fig)
        
        return {
            'success': True,
            'filename': file_path.name,
            'file_path': str(file_path),
            'image_base64': image_base64,
            'download_url': f"/download/{file_path.name}",
            'chart_type': filename.split('_')[0],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_available_charts(self, df: pd.DataFrame, column_types: Dict[str, ColumnType]) -> Dict[str, Any]:
        """
        Get all available chart recommendations for the dataset.
        
        Args:
            df: DataFrame to analyze
            column_types: Dictionary mapping column names to their types
            
        Returns:
            Dictionary with chart recommendations
        """
        return self.chart_recommender.recommend_charts_for_dataset(df, column_types)
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old chart files.
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
            
        Returns:
            Number of files deleted
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        deleted_count = 0
        for file_path in self.output_dir.glob("*.png"):
            if current_time - file_path.stat().st_mtime > max_age_seconds:
                file_path.unlink()
                deleted_count += 1
        
        return deleted_count 