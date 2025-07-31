"""
Apollo AI Data Visualizer
Generates Chart.js compatible visualization data for various chart types.
Works with DataAnalyzer results to create frontend-ready JSON structures.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import json
from datetime import datetime


class DataVisualizer:
    """
    Generates Chart.js compatible visualization data structures.
    Supports: histogram, boxplot, bar chart, scatter plot, heatmap
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize visualizer with DataFrame
        
        Args:
            df: Pandas DataFrame to visualize
        """
        self.df = df
        self.numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.datetime_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    def generate_histogram(self, column: str, bins: int = 20) -> Dict[str, Any]:
        """
        Generate histogram data for Chart.js
        
        Args:
            column: Column name to create histogram for
            bins: Number of bins for histogram
            
        Returns:
            Chart.js compatible histogram data
        """
        if column not in self.numeric_columns:
            raise ValueError(f"Column '{column}' is not numeric")
        
        # Calculate histogram
        data = self.df[column].dropna()
        hist, bin_edges = np.histogram(data, bins=bins)
        
        # Create bin labels (midpoints)
        bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges)-1)]
        
        return {
            "type": "bar",
            "data": {
                "labels": [f"{edge:.2f}" for edge in bin_centers],
                "datasets": [{
                    "label": f"Frequency of {column}",
                    "data": hist.tolist(),
                    "backgroundColor": "rgba(54, 162, 235, 0.6)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"Distribution of {column}"
                    },
                    "legend": {
                        "display": False
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": column
                        }
                    },
                    "y": {
                        "title": {
                            "display": True,
                            "text": "Frequency"
                        }
                    }
                }
            },
            "metadata": {
                "column": column,
                "bins": bins,
                "total_values": len(data),
                "min_value": float(data.min()),
                "max_value": float(data.max()),
                "mean": float(data.mean()),
                "std": float(data.std())
            }
        }
    
    def generate_boxplot(self, columns: List[str]) -> Dict[str, Any]:
        """
        Generate boxplot data for Chart.js (using Chart.js boxplot plugin format)
        
        Args:
            columns: List of numeric columns for boxplot
            
        Returns:
            Chart.js compatible boxplot data
        """
        valid_columns = [col for col in columns if col in self.numeric_columns]
        if not valid_columns:
            raise ValueError("No valid numeric columns provided")
        
        datasets = []
        
        for i, column in enumerate(valid_columns):
            data = self.df[column].dropna()
            
            # Calculate boxplot statistics
            q1 = data.quantile(0.25)
            q2 = data.quantile(0.5)  # median
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr
            
            # Find outliers
            outliers = data[(data < lower_fence) | (data > upper_fence)].tolist()
            
            # Color palette
            colors = [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 205, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)'
            ]
            
            datasets.append({
                "label": column,
                "data": [{
                    "min": float(data.min()),
                    "q1": float(q1),
                    "median": float(q2),
                    "q3": float(q3),
                    "max": float(data.max()),
                    "outliers": outliers
                }],
                "backgroundColor": colors[i % len(colors)],
                "borderColor": colors[i % len(colors)].replace('0.6', '1'),
                "borderWidth": 1
            })
        
        return {
            "type": "boxplot",
            "data": {
                "labels": valid_columns,
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Box Plot Distribution"
                    }
                },
                "scales": {
                    "y": {
                        "title": {
                            "display": True,
                            "text": "Values"
                        }
                    }
                }
            },
            "metadata": {
                "columns": valid_columns,
                "total_columns": len(valid_columns)
            }
        }
    
    def generate_bar_chart(self, column: str, top_n: int = 10) -> Dict[str, Any]:
        """
        Generate bar chart for categorical data
        
        Args:
            column: Categorical column name
            top_n: Number of top categories to show
            
        Returns:
            Chart.js compatible bar chart data
        """
        if column not in self.categorical_columns:
            raise ValueError(f"Column '{column}' is not categorical")
        
        # Get value counts
        value_counts = self.df[column].value_counts().head(top_n)
        
        return {
            "type": "bar",
            "data": {
                "labels": value_counts.index.tolist(),
                "datasets": [{
                    "label": f"Count of {column}",
                    "data": value_counts.values.tolist(),
                    "backgroundColor": [
                        f"rgba({np.random.randint(0, 255)}, {np.random.randint(0, 255)}, {np.random.randint(0, 255)}, 0.6)"
                        for _ in range(len(value_counts))
                    ],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"Distribution of {column}"
                    },
                    "legend": {
                        "display": False
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": column
                        }
                    },
                    "y": {
                        "title": {
                            "display": True,
                            "text": "Count"
                        }
                    }
                }
            },
            "metadata": {
                "column": column,
                "top_n": top_n,
                "total_unique": self.df[column].nunique(),
                "total_values": len(self.df[column].dropna())
            }
        }
    
    def generate_scatter_plot(self, x_column: str, y_column: str, 
                             color_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate scatter plot for two numeric variables
        
        Args:
            x_column: X-axis column name
            y_column: Y-axis column name
            color_column: Optional column for color coding points
            
        Returns:
            Chart.js compatible scatter plot data
        """
        if x_column not in self.numeric_columns or y_column not in self.numeric_columns:
            raise ValueError("Both x and y columns must be numeric")
        
        # Get clean data
        df_clean = self.df[[x_column, y_column]].dropna()
        
        if color_column and color_column in self.categorical_columns:
            # Group by color column
            datasets = []
            colors = ['rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 
                     'rgba(255, 205, 86, 0.6)', 'rgba(75, 192, 192, 0.6)']
            
            for i, (category, group) in enumerate(self.df.groupby(color_column)):
                clean_group = group[[x_column, y_column]].dropna()
                datasets.append({
                    "label": str(category),
                    "data": [{"x": float(x), "y": float(y)} 
                            for x, y in zip(clean_group[x_column], clean_group[y_column])],
                    "backgroundColor": colors[i % len(colors)],
                    "borderColor": colors[i % len(colors)].replace('0.6', '1'),
                    "pointRadius": 4
                })
        else:
            # Single dataset
            datasets = [{
                "label": f"{y_column} vs {x_column}",
                "data": [{"x": float(x), "y": float(y)} 
                        for x, y in zip(df_clean[x_column], df_clean[y_column])],
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "pointRadius": 4
            }]
        
        return {
            "type": "scatter",
            "data": {
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{y_column} vs {x_column}"
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": x_column
                        }
                    },
                    "y": {
                        "title": {
                            "display": True,
                            "text": y_column
                        }
                    }
                }
            },
            "metadata": {
                "x_column": x_column,
                "y_column": y_column,
                "color_column": color_column,
                "data_points": len(df_clean),
                "correlation": float(df_clean[x_column].corr(df_clean[y_column]))
            }
        }
    
    def generate_heatmap(self, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate correlation heatmap data
        
        Args:
            columns: List of numeric columns to include (all numeric if None)
            
        Returns:
            Chart.js compatible heatmap data (using matrix format)
        """
        if columns is None:
            columns = self.numeric_columns
        else:
            columns = [col for col in columns if col in self.numeric_columns]
        
        if len(columns) < 2:
            raise ValueError("Need at least 2 numeric columns for correlation heatmap")
        
        # Calculate correlation matrix
        corr_matrix = self.df[columns].corr()
        
        # Prepare data for Chart.js heatmap
        data = []
        for i, row_name in enumerate(corr_matrix.index):
            for j, col_name in enumerate(corr_matrix.columns):
                data.append({
                    "x": col_name,
                    "y": row_name,
                    "v": float(corr_matrix.iloc[i, j])
                })
        
        return {
            "type": "scatter",  # Using scatter with point styling for heatmap effect
            "data": {
                "datasets": [{
                    "label": "Correlation",
                    "data": data,
                    "backgroundColor": lambda ctx: self._get_heatmap_color(ctx.parsed.v),
                    "pointRadius": 20,
                    "pointHoverRadius": 25
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Correlation Heatmap"
                    },
                    "legend": {
                        "display": False
                    }
                },
                "scales": {
                    "x": {
                        "type": "category",
                        "labels": columns,
                        "title": {
                            "display": True,
                            "text": "Variables"
                        }
                    },
                    "y": {
                        "type": "category",
                        "labels": columns,
                        "title": {
                            "display": True,
                            "text": "Variables"
                        }
                    }
                }
            },
            "metadata": {
                "columns": columns,
                "matrix_size": f"{len(columns)}x{len(columns)}",
                "correlation_matrix": corr_matrix.to_dict()
            }
        }
    
    def _get_heatmap_color(self, correlation_value: float) -> str:
        """
        Get color for heatmap based on correlation value
        
        Args:
            correlation_value: Correlation coefficient (-1 to 1)
            
        Returns:
            RGBA color string
        """
        # Normalize to 0-1 range
        normalized = (correlation_value + 1) / 2
        
        if normalized < 0.5:
            # Blue to white (negative correlation)
            intensity = int(255 * (1 - normalized * 2))
            return f"rgba({intensity}, {intensity}, 255, 0.8)"
        else:
            # White to red (positive correlation)
            intensity = int(255 * (normalized - 0.5) * 2)
            return f"rgba(255, {255 - intensity}, {255 - intensity}, 0.8)"
    
    def get_available_visualizations(self) -> Dict[str, List[str]]:
        """
        Get available visualization options based on data types
        
        Returns:
            Dictionary of visualization types and applicable columns
        """
        return {
            "histogram": self.numeric_columns,
            "boxplot": self.numeric_columns,
            "bar_chart": self.categorical_columns,
            "scatter_plot": self.numeric_columns,
            "heatmap": self.numeric_columns if len(self.numeric_columns) >= 2 else []
        }
    
    def generate_visualization_summary(self) -> Dict[str, Any]:
        """
        Generate summary of all possible visualizations
        
        Returns:
            Summary of available visualizations and recommendations
        """
        available = self.get_available_visualizations()
        
        recommendations = []
        
        # Recommend based on data characteristics
        if len(self.numeric_columns) >= 2:
            recommendations.append("Correlation heatmap to explore relationships")
            recommendations.append("Scatter plots for bivariate analysis")
        
        if len(self.numeric_columns) >= 1:
            recommendations.append("Histograms to understand distributions")
            recommendations.append("Box plots to identify outliers")
        
        if len(self.categorical_columns) >= 1:
            recommendations.append("Bar charts for categorical distributions")
        
        return {
            "available_visualizations": available,
            "data_summary": {
                "total_columns": len(self.df.columns),
                "numeric_columns": len(self.numeric_columns),
                "categorical_columns": len(self.categorical_columns),
                "datetime_columns": len(self.datetime_columns),
                "total_rows": len(self.df)
            },
            "recommendations": recommendations
        }
