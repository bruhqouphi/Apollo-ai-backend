"""
Apollo AI Smart Chart Service
Intelligent chart generation system that selects the best visualization library
based on user requirements and chart type needs.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import uuid
import json
from datetime import datetime
from enum import Enum
import logging

# Import visualization libraries with error handling
try:
    import matplotlib.pyplot as plt
    import matplotlib.style as style
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.offline as pyo
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import bokeh
    from bokeh.plotting import figure, save, output_file
    from bokeh.models import HoverTool
    from bokeh.layouts import column
    from bokeh.embed import components
    BOKEH_AVAILABLE = True
except ImportError:
    BOKEH_AVAILABLE = False

logger = logging.getLogger(__name__)

class ChartMode(Enum):
    """Chart rendering modes"""
    INTERACTIVE = "interactive"
    STATIC = "static"
    AUTO = "auto"

class ChartLibrary(Enum):
    """Available visualization libraries"""
    MATPLOTLIB = "matplotlib"
    SEABORN = "seaborn"
    PLOTLY = "plotly"
    BOKEH = "bokeh"

class SmartChartService:
    """
    Smart chart generation service that automatically selects the best
    visualization library based on chart requirements and user preferences.
    """
    
    def __init__(self, output_dir: str = "./charts"):
        """Initialize smart chart service."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure theme settings for consistent black/white/grey styling
        self._setup_unified_theme()
        
        # Define library capabilities and preferences
        self._setup_library_preferences()
    
    def _setup_unified_theme(self):
        """Setup consistent black/white/grey theme across all libraries."""
        
        # Common color palette for all libraries
        self.color_palette = {
            'primary': '#404040',      # Dark grey
            'secondary': '#666666',    # Medium grey  
            'tertiary': '#808080',     # Light grey
            'quaternary': '#999999',   # Lighter grey
            'background': '#ffffff',   # White
            'text': '#333333',         # Dark text
            'grid': '#e5e5e5',        # Light grid
            'accent': '#b3b3b3'       # Very light grey
        }
        
        # Matplotlib/Seaborn theme
        if MATPLOTLIB_AVAILABLE:
            plt.style.use('default')
            plt.rcParams.update({
                'figure.facecolor': self.color_palette['background'],
                'axes.facecolor': self.color_palette['background'],
                'axes.edgecolor': self.color_palette['secondary'],
                'axes.titlecolor': self.color_palette['text'],
                'axes.labelcolor': self.color_palette['secondary'],
                'text.color': self.color_palette['text'],
                'xtick.color': self.color_palette['secondary'],
                'ytick.color': self.color_palette['secondary'],
                'grid.color': self.color_palette['grid'],
                'axes.grid': True,
                'grid.alpha': 0.7,
                'font.family': 'sans-serif',
                'font.sans-serif': ['Inter', 'Arial', 'Helvetica', 'DejaVu Sans'],
                'figure.dpi': 100,
                'savefig.dpi': 150,
                'savefig.facecolor': self.color_palette['background'],
                'axes.spines.top': False,
                'axes.spines.right': False,
            })
        
        # Plotly theme
        self.plotly_theme = {
            'layout': {
                'plot_bgcolor': self.color_palette['background'],
                'paper_bgcolor': self.color_palette['background'],
                'font': {'family': 'Inter, Arial, sans-serif', 'color': self.color_palette['text']},
                'colorway': [self.color_palette['primary'], self.color_palette['secondary'], 
                           self.color_palette['tertiary'], self.color_palette['quaternary']],
                'xaxis': {
                    'gridcolor': self.color_palette['grid'],
                    'tickcolor': self.color_palette['secondary'],
                    'titlefont': {'color': self.color_palette['text']},
                    'tickfont': {'color': self.color_palette['secondary']}
                },
                'yaxis': {
                    'gridcolor': self.color_palette['grid'],
                    'tickcolor': self.color_palette['secondary'],
                    'titlefont': {'color': self.color_palette['text']},
                    'tickfont': {'color': self.color_palette['secondary']}
                }
            }
        }
    
    def _setup_library_preferences(self):
        """Define which libraries work best for different chart types and modes."""
        
        self.library_preferences = {
            # Chart types that benefit from interactivity
            'interactive_preferred': {
                'scatter_plot': [ChartLibrary.PLOTLY, ChartLibrary.BOKEH],
                'line_chart': [ChartLibrary.PLOTLY, ChartLibrary.BOKEH],
                'heatmap': [ChartLibrary.PLOTLY, ChartLibrary.SEABORN],
                'bubble_chart': [ChartLibrary.PLOTLY, ChartLibrary.BOKEH],
                '3d_plot': [ChartLibrary.PLOTLY],
            },
            
            # Chart types that work well as static images
            'static_preferred': {
                'histogram': [ChartLibrary.SEABORN, ChartLibrary.MATPLOTLIB],
                'box_plot': [ChartLibrary.SEABORN, ChartLibrary.MATPLOTLIB],
                'violin_plot': [ChartLibrary.SEABORN],
                'correlation_matrix': [ChartLibrary.SEABORN],
                'distribution': [ChartLibrary.SEABORN, ChartLibrary.MATPLOTLIB],
            },
            
            # Chart types that work well with either approach
            'flexible': {
                'bar_chart': [ChartLibrary.PLOTLY, ChartLibrary.SEABORN, ChartLibrary.MATPLOTLIB],
                'pie_chart': [ChartLibrary.PLOTLY, ChartLibrary.MATPLOTLIB],
                'area_chart': [ChartLibrary.PLOTLY, ChartLibrary.MATPLOTLIB],
            }
        }
    
    def select_optimal_library(self, chart_type: str, mode: ChartMode, 
                              data_size: int = 0, has_time_series: bool = False) -> ChartLibrary:
        """
        Intelligently select the best visualization library based on requirements.
        
        Args:
            chart_type: Type of chart to generate
            mode: Interactive, static, or auto mode
            data_size: Number of data points
            has_time_series: Whether data contains time series
            
        Returns:
            Selected chart library
        """
        
        # Check library availability
        available_libraries = []
        if MATPLOTLIB_AVAILABLE:
            available_libraries.extend([ChartLibrary.MATPLOTLIB, ChartLibrary.SEABORN])
        if PLOTLY_AVAILABLE:
            available_libraries.append(ChartLibrary.PLOTLY)
        if BOKEH_AVAILABLE:
            available_libraries.append(ChartLibrary.BOKEH)
        
        if not available_libraries:
            raise RuntimeError("No visualization libraries available")
        
        # Auto mode: decide based on chart type and data characteristics
        if mode == ChartMode.AUTO:
            # Large datasets (>1000 points) benefit from interactivity
            if data_size > 1000:
                mode = ChartMode.INTERACTIVE
            # Time series often benefit from interactivity
            elif has_time_series:
                mode = ChartMode.INTERACTIVE
            # Statistical charts often better as static
            elif chart_type in ['histogram', 'box_plot', 'violin_plot', 'correlation_matrix']:
                mode = ChartMode.STATIC
            else:
                mode = ChartMode.INTERACTIVE
        
        # Select library based on mode and preferences
        if mode == ChartMode.INTERACTIVE:
            # Prefer interactive libraries
            for category in ['interactive_preferred', 'flexible']:
                if chart_type in self.library_preferences[category]:
                    for lib in self.library_preferences[category][chart_type]:
                        if lib in available_libraries:
                            return lib
            
            # Fallback to any available interactive library
            if ChartLibrary.PLOTLY in available_libraries:
                return ChartLibrary.PLOTLY
            elif ChartLibrary.BOKEH in available_libraries:
                return ChartLibrary.BOKEH
        
        else:  # Static mode
            # Prefer static libraries
            for category in ['static_preferred', 'flexible']:
                if chart_type in self.library_preferences[category]:
                    for lib in self.library_preferences[category][chart_type]:
                        if lib in available_libraries:
                            return lib
            
            # Fallback to any available static library
            if ChartLibrary.SEABORN in available_libraries:
                return ChartLibrary.SEABORN
            elif ChartLibrary.MATPLOTLIB in available_libraries:
                return ChartLibrary.MATPLOTLIB
        
        # Final fallback
        return available_libraries[0]
    
    def generate_chart(self, df: pd.DataFrame, chart_type: str, columns: List[str], 
                      mode: ChartMode = ChartMode.AUTO, **kwargs) -> Dict[str, Any]:
        """
        Generate a chart using the optimal library for the given requirements.
        
        Args:
            df: DataFrame containing the data
            chart_type: Type of chart to generate
            columns: Columns to use for the chart
            mode: Chart rendering mode
            **kwargs: Additional chart options
            
        Returns:
            Dictionary containing chart information and file paths/HTML
        """
        
        try:
            # Analyze data characteristics
            data_size = len(df)
            has_time_series = any(pd.api.types.is_datetime64_any_dtype(df[col]) for col in df.columns)
            
            # Select optimal library
            selected_library = self.select_optimal_library(chart_type, mode, data_size, has_time_series)
            
            # Generate chart using selected library
            if selected_library == ChartLibrary.MATPLOTLIB:
                return self._generate_matplotlib_chart(df, chart_type, columns, **kwargs)
            elif selected_library == ChartLibrary.SEABORN:
                return self._generate_seaborn_chart(df, chart_type, columns, **kwargs)
            elif selected_library == ChartLibrary.PLOTLY:
                return self._generate_plotly_chart(df, chart_type, columns, **kwargs)
            elif selected_library == ChartLibrary.BOKEH:
                return self._generate_bokeh_chart(df, chart_type, columns, **kwargs)
            else:
                raise ValueError(f"Unsupported library: {selected_library}")
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'chart_type': chart_type,
                'library_used': None
            }
    
    def _generate_matplotlib_chart(self, df: pd.DataFrame, chart_type: str, columns: List[str], **kwargs) -> Dict[str, Any]:
        """Generate interactive chart using Matplotlib."""
        
        try:
            # Import the interactive matplotlib service
            from app.services.interactive_matplotlib_service import InteractiveMatplotlibChartService
            
            # Create interactive matplotlib service
            matplotlib_service = InteractiveMatplotlibChartService(str(self.output_dir))
            
            # Generate interactive chart
            result = matplotlib_service.generate_chart(df, chart_type, columns, **kwargs)
            
            if result.get('success', False):
                # Add library information
                result['library_used'] = 'matplotlib'
                result['mode'] = 'interactive'
                return result
            else:
                raise ValueError(result.get('error', 'Matplotlib chart generation failed'))
            
        except Exception as e:
            logger.error(f"Matplotlib chart generation failed: {str(e)}")
            raise e
    
    def _generate_seaborn_chart(self, df: pd.DataFrame, chart_type: str, columns: List[str], **kwargs) -> Dict[str, Any]:
        """Generate chart using Seaborn (optimized for statistical visualizations)."""
        
        try:
            # Set Seaborn style to match our theme
            sns.set_style("whitegrid")
            sns.set_palette([self.color_palette['primary'], self.color_palette['secondary'], 
                           self.color_palette['tertiary'], self.color_palette['quaternary']])
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            if chart_type == 'histogram' and len(columns) >= 1:
                col = columns[0]
                bins = kwargs.get('bins', 30)
                sns.histplot(data=df, x=col, bins=bins, ax=ax, color=self.color_palette['primary'])
                ax.set_title(f'Distribution of {col}', fontweight='bold', pad=20)
                
            elif chart_type == 'box_plot' and len(columns) >= 1:
                col = columns[0]
                sns.boxplot(data=df, y=col, ax=ax, color=self.color_palette['primary'])
                ax.set_title(f'Box Plot of {col}', fontweight='bold', pad=20)
                
            elif chart_type == 'violin_plot' and len(columns) >= 1:
                col = columns[0]
                sns.violinplot(data=df, y=col, ax=ax, color=self.color_palette['primary'])
                ax.set_title(f'Violin Plot of {col}', fontweight='bold', pad=20)
                
            elif chart_type == 'correlation_matrix':
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    corr_matrix = df[numeric_cols].corr()
                    sns.heatmap(corr_matrix, annot=True, cmap='RdGy_r', center=0, ax=ax,
                              square=True, linewidths=0.5, cbar_kws={"shrink": .8})
                    ax.set_title('Correlation Matrix', fontweight='bold', pad=20)
                else:
                    raise ValueError("Insufficient numeric columns for correlation matrix")
                    
            elif chart_type == 'scatter_plot' and len(columns) >= 2:
                x_col, y_col = columns[0], columns[1]
                sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax, color=self.color_palette['primary'])
                ax.set_title(f'{y_col} vs {x_col}', fontweight='bold', pad=20)
                
            else:
                raise ValueError(f"Chart type '{chart_type}' not supported with Seaborn or insufficient columns")
            
            # Save chart
            filename = f"seaborn_{chart_type}_{uuid.uuid4().hex[:8]}.png"
            filepath = self.output_dir / filename
            plt.tight_layout()
            plt.savefig(filepath, format='png', bbox_inches='tight', pad_inches=0.1)
            plt.close()
            
            return {
                'success': True,
                'chart_type': chart_type,
                'library_used': 'seaborn',
                'mode': 'static',
                'filename': filename,
                'filepath': str(filepath),
                'image_url': f"/api/v1/visualization/image/{filename}",
                'title': ax.get_title(),
                'columns': columns
            }
            
        except Exception as e:
            plt.close()
            raise e
    
    def _generate_plotly_chart(self, df: pd.DataFrame, chart_type: str, columns: List[str], **kwargs) -> Dict[str, Any]:
        """Generate interactive chart using Plotly."""
        
        try:
            fig = None
            title = ""
            
            if chart_type == 'histogram' and len(columns) >= 1:
                col = columns[0]
                bins = kwargs.get('bins', 30)
                fig = px.histogram(df, x=col, nbins=bins, 
                                 color_discrete_sequence=[self.color_palette['primary']])
                title = f'Distribution of {col}'
                
            elif chart_type == 'bar_chart' and len(columns) >= 1:
                col = columns[0]
                value_counts = df[col].value_counts().head(20)
                fig = px.bar(x=value_counts.index, y=value_counts.values,
                           color_discrete_sequence=[self.color_palette['primary']])
                fig.update_xaxes(title=col)
                fig.update_yaxes(title='Count')
                title = f'Count of {col} Values'
                
            elif chart_type == 'line_chart' and len(columns) >= 2:
                x_col, y_col = columns[0], columns[1]
                fig = px.line(df.sort_values(x_col), x=x_col, y=y_col,
                            color_discrete_sequence=[self.color_palette['primary']])
                title = f'{y_col} vs {x_col}'
                
            elif chart_type == 'scatter_plot' and len(columns) >= 2:
                x_col, y_col = columns[0], columns[1]
                fig = px.scatter(df, x=x_col, y=y_col,
                               color_discrete_sequence=[self.color_palette['primary']])
                title = f'{y_col} vs {x_col}'
                
            elif chart_type == 'pie_chart' and len(columns) >= 1:
                col = columns[0]
                value_counts = df[col].value_counts().head(10)
                fig = px.pie(values=value_counts.values, names=value_counts.index,
                           color_discrete_sequence=[self.color_palette['primary'], self.color_palette['secondary'], 
                                                  self.color_palette['tertiary'], self.color_palette['quaternary']])
                title = f'Distribution of {col}'
                
            else:
                raise ValueError(f"Chart type '{chart_type}' not supported with Plotly or insufficient columns")
            
            if fig:
                # Apply consistent theming
                fig.update_layout(self.plotly_theme['layout'])
                fig.update_layout(title=title, title_font_size=16, title_font_color=self.color_palette['text'])
                
                # Save as HTML for interactivity
                filename = f"plotly_{chart_type}_{uuid.uuid4().hex[:8]}.html"
                filepath = self.output_dir / filename
                fig.write_html(str(filepath))
                
                # Also save as static image for fallback
                static_filename = f"plotly_{chart_type}_{uuid.uuid4().hex[:8]}.png"
                static_filepath = self.output_dir / static_filename
                try:
                    fig.write_image(str(static_filepath), width=1200, height=800)
                except Exception as e:
                    logger.warning(f"Could not generate static image fallback: {e}")
                    static_filename = None
                    static_filepath = None
                
                result = {
                    'success': True,
                    'chart_type': chart_type,
                    'library_used': 'plotly',
                    'mode': 'interactive',
                    'filename': filename,
                    'filepath': str(filepath),
                    'html_url': f"/api/v1/visualization/interactive/{filename}",
                    'title': title,
                    'columns': columns,
                    'plotly_json': fig.to_json()
                }
                
                # Add static image information if generation succeeded
                if static_filename and static_filepath:
                    result.update({
                        'static_filename': static_filename,
                        'static_filepath': str(static_filepath),
                        'image_url': f"/api/v1/visualization/image/{static_filename}"
                    })
                
                return result
            
        except Exception as e:
            raise e
    
    def _generate_bokeh_chart(self, df: pd.DataFrame, chart_type: str, columns: List[str], **kwargs) -> Dict[str, Any]:
        """Generate interactive chart using Bokeh."""
        
        # Note: Bokeh implementation would go here
        # For now, fallback to Plotly
        return self._generate_plotly_chart(df, chart_type, columns, **kwargs)
    
    def cleanup_old_files(self, hours: int = 24) -> int:
        """Clean up old chart files."""
        try:
            current_time = datetime.now()
            deleted_count = 0
            
            for file_path in self.output_dir.glob("*"):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if (current_time - file_time).total_seconds() > hours * 3600:
                        file_path.unlink()
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
            return 0
    
    def get_available_libraries(self) -> Dict[str, bool]:
        """Get information about available visualization libraries."""
        return {
            'matplotlib': MATPLOTLIB_AVAILABLE,
            'seaborn': MATPLOTLIB_AVAILABLE,  # Seaborn requires matplotlib
            'plotly': PLOTLY_AVAILABLE,
            'bokeh': BOKEH_AVAILABLE
        }
