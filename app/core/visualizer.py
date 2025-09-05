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
        self.df = df.copy()  # Work with a copy to avoid modifying original

        # Enhanced data type detection
        self.numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        self.datetime_columns = df.select_dtypes(include=['datetime64']).columns.tolist()

        # Detect potential date columns that are currently strings
        potential_date_columns = []
        for col in df.columns:
            if col not in self.numeric_columns and col not in self.datetime_columns:
                # Try to parse as date
                try:
                    pd.to_datetime(df[col].head(5), errors='coerce')
                    potential_date_columns.append(col)
                except:
                    pass

        # Convert detected date columns to datetime
        for col in potential_date_columns:
            try:
                self.df[col] = pd.to_datetime(df[col], errors='coerce')
                if self.df[col].notna().any():
                    self.datetime_columns.append(col)
                else:
                    self.df[col] = df[col]  # Revert if parsing failed
            except:
                pass

        # Categorical columns are everything else
        all_special_cols = set(self.numeric_columns + self.datetime_columns)
        self.categorical_columns = [col for col in df.columns if col not in all_special_cols]
        
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Visualizer initialized with {len(df)} rows and {len(df.columns)} columns")
        logger.debug(f"Numeric columns: {self.numeric_columns}")
        logger.debug(f"Categorical columns: {self.categorical_columns}")
        logger.debug(f"Datetime columns: {self.datetime_columns}")
        logger.debug(f"Detected date columns: {potential_date_columns}")
    
    def generate_histogram(self, column: str, bins: int = 20) -> Dict[str, Any]:
        """
        Generate histogram data for Chart.js
        
        Args:
            column: Column name to create histogram for
            bins: Number of bins for histogram
            
        Returns:
            Chart.js compatible histogram data
        """
        # Enhanced validation with better error messages
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in dataset. Available columns: {list(self.df.columns)}")
        
        if column not in self.numeric_columns:
            available_numeric = list(self.numeric_columns)
            raise ValueError(f"Column '{column}' is not numeric. Available numeric columns: {available_numeric}")
        
        # Check if we have enough data
        data = self.df[column].dropna()
        if len(data) == 0:
            raise ValueError(f"Column '{column}' has no valid numeric data (all values are NaN)")
        
        if len(data) < 2:
            raise ValueError(f"Column '{column}' has only {len(data)} valid value(s). Need at least 2 values for histogram.")
        
        # Validate bins parameter
        if bins < 2:
            raise ValueError(f"Number of bins ({bins}) must be at least 2")
        
        if bins > len(data):
            bins = min(len(data), 20)  # Auto-adjust bins if too many
        
        try:
            # Calculate histogram
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
        except Exception as e:
            raise ValueError(f"Failed to generate histogram for column '{column}': {str(e)}")
    
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
            column: Column name (will be converted to categorical if needed)
            top_n: Number of top categories to show
            
        Returns:
            Chart.js compatible bar chart data
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")
        
        # Convert to string and get value counts (works for any data type)
        value_counts = self.df[column].astype(str).value_counts().head(top_n)
        
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
    
    def generate_line_chart(self, x_column: str, y_column: str) -> Dict[str, Any]:
        """
        Generate line chart for time series or sequential data
        
        Args:
            x_column: X-axis column name (usually time/sequence)
            y_column: Y-axis column name (numeric values)
            
        Returns:
            Chart.js compatible line chart data
        """
        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError(f"Columns '{x_column}' or '{y_column}' not found in DataFrame")
        
        # Try to convert y_column to numeric if it's not already
        try:
            y_data = pd.to_numeric(self.df[y_column], errors='coerce')
        except:
            raise ValueError(f"Y column '{y_column}' cannot be converted to numeric values")
        
        # Get clean data and sort by x column
        df_clean = self.df[[x_column]].copy()
        df_clean[y_column] = y_data
        df_clean = df_clean.dropna()
        df_clean = df_clean.sort_values(x_column)
        
        return {
            "type": "line",
            "data": {
                "labels": df_clean[x_column].astype(str).tolist(),
                "datasets": [{
                    "label": f"{y_column} over {x_column}",
                    "data": df_clean[y_column].tolist(),
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "borderWidth": 2,
                    "fill": True,
                    "tension": 0.1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{y_column} Trend over {x_column}"
                    },
                    "legend": {
                        "display": True
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
                "total_points": len(df_clean),
                "min_value": float(df_clean[y_column].min()),
                "max_value": float(df_clean[y_column].max()),
                "trend": "increasing" if df_clean[y_column].iloc[-1] > df_clean[y_column].iloc[0] else "decreasing"
            }
        }
    
    def generate_pie_chart(self, column: str, top_n: int = 8) -> Dict[str, Any]:
        """
        Generate pie chart for categorical data
        
        Args:
            column: Column name (will be converted to categorical if needed)
            top_n: Number of top categories to show
            
        Returns:
            Chart.js compatible pie chart data
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")
        
        # Convert to string and get value counts (works for any data type)
        value_counts = self.df[column].astype(str).value_counts().head(top_n)
        
        # Generate colors
        colors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(199, 199, 199, 0.8)',
            'rgba(83, 102, 255, 0.8)'
        ]
        
        return {
            "type": "pie",
            "data": {
                "labels": value_counts.index.tolist(),
                "datasets": [{
                    "label": f"Distribution of {column}",
                    "data": value_counts.values.tolist(),
                    "backgroundColor": colors[:len(value_counts)],
                    "borderColor": "rgba(255, 255, 255, 1)",
                    "borderWidth": 2
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
                        "display": True,
                        "position": "bottom"
                    }
                }
            },
            "metadata": {
                "column": column,
                "top_n": top_n,
                "total_unique": self.df[column].nunique(),
                "total_values": len(self.df[column].dropna()),
                "largest_category": value_counts.index[0],
                "largest_percentage": float((value_counts.iloc[0] / value_counts.sum()) * 100)
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
    
    def generate_grouped_bar_chart(self, group_column: str, value_column: str, aggregation: str = 'mean') -> Dict[str, Any]:
        """
        Generate grouped bar chart (e.g., Sales by Month, Revenue by Region)
        
        Args:
            group_column: Column to group by (categorical, like Month, Region)
            value_column: Column to aggregate (numeric, like Sales, Revenue)
            aggregation: How to aggregate values ('mean', 'sum', 'count', 'median')
            
        Returns:
            Chart.js compatible bar chart data
        """
        if group_column not in self.df.columns:
            raise ValueError(f"Group column '{group_column}' not found")
        if value_column not in self.df.columns:
            raise ValueError(f"Value column '{value_column}' not found")
        
        # Group and aggregate data
        if aggregation == 'mean':
            grouped_data = self.df.groupby(group_column)[value_column].mean()
        elif aggregation == 'sum':
            grouped_data = self.df.groupby(group_column)[value_column].sum()
        elif aggregation == 'count':
            grouped_data = self.df.groupby(group_column)[value_column].count()
        elif aggregation == 'median':
            grouped_data = self.df.groupby(group_column)[value_column].median()
        else:
            grouped_data = self.df.groupby(group_column)[value_column].mean()  # Default to mean
        
        # Sort by group labels for better display
        grouped_data = grouped_data.sort_index()
        
        # Prepare labels and data
        labels = grouped_data.index.astype(str).tolist()
        values = grouped_data.values.tolist()
        
        # Generate colors
        colors = [
            f"rgba({np.random.randint(50, 255)}, {np.random.randint(50, 255)}, {np.random.randint(50, 255)}, 0.7)"
            for _ in labels
        ]
        
        return {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": f"{value_column} by {group_column} ({aggregation})",
                    "data": values,
                    "backgroundColor": colors,
                    "borderColor": [color.replace("0.7", "1.0") for color in colors],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{value_column} by {group_column}",
                        "font": {"size": 16, "weight": "bold"}
                    },
                    "legend": {
                        "display": True
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": group_column,
                            "font": {"size": 14, "weight": "bold"}
                        }
                    },
                    "y": {
                        "title": {
                            "display": True,
                            "text": f"{value_column} ({aggregation})",
                            "font": {"size": 14, "weight": "bold"}
                        },
                        "beginAtZero": True
                    }
                }
            },
            "metadata": {
                "chart_type": "grouped_bar",
                "group_column": group_column,
                "value_column": value_column,
                "aggregation": aggregation,
                "data_points": len(labels),
                "total_records": len(self.df),
                "description": f"Shows {value_column} aggregated by {group_column} using {aggregation}"
            }
        }

    def get_available_visualizations(self) -> Dict[str, any]:
        """
        Get available visualization options based on data types

        Returns:
            Dictionary of visualization types and applicable columns
        """
        return {
            "histogram": self.numeric_columns,
            "boxplot": self.numeric_columns,
            "bar": self.categorical_columns + self.datetime_columns,  # Categorical columns for bar charts
            "line": self.df.columns.tolist() if len(self.df.columns) >= 2 else [],  # Any columns for line
            "pie": self.categorical_columns,  # Only categorical for pie charts
            "scatter": self.numeric_columns if len(self.numeric_columns) >= 2 else [],
            "heatmap": self.numeric_columns if len(self.numeric_columns) >= 2 else [],
            "time_series": self.datetime_columns + self.numeric_columns if len(self.datetime_columns) > 0 else [],
            "grouped_bar": {
                "categorical": self.categorical_columns + self.datetime_columns,  # Include datetime as categorical for grouping
                "numeric": self.numeric_columns
            }
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
            recommendations.append("Pie charts to show proportions")
        
        if len(self.datetime_columns) >= 1:
            recommendations.append("Time series analysis for date-based trends")
            if len(self.numeric_columns) >= 1:
                recommendations.append("Line charts showing trends over time")

        if len(self.numeric_columns) >= 1 and len(self.categorical_columns) >= 1:
            recommendations.append("Grouped bar charts to compare categories")
        
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
