"""
Visualization Service - IMPROVED FIXED VERSION
Handles chart generation with Chart.js compatible output and proper CSV loading.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path

from app.database.database import get_database
from app.database.models import File, Visualization, User
from app.models.schemas import VisualizationRequest

logger = logging.getLogger(__name__)

class VisualizationService:
    """Service for handling visualization operations with Chart.js compatibility."""
    
    def __init__(self):
        self.db: Session = next(get_database())
    
    async def generate_chart(self, request: VisualizationRequest) -> Dict[str, Any]:
        """Generate chart for uploaded data - IMPROVED VERSION."""
        try:
            logger.info(f"Starting chart generation for request: {request}")
            
            # Get file from database
            file = self.db.query(File).filter(File.id == request.file_id).first()
            if not file:
                logger.error(f"File not found with id: {request.file_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            logger.info(f"Found file: {file.original_filename}, path: {file.file_path}, type: {file.file_type}")
            
            # CRITICAL FIX: Proper file loading with error handling
            df = await self._load_file_data(file)
            logger.info(f"Loaded DataFrame with shape: {df.shape}")
            logger.info(f"Columns: {list(df.columns)}")
            
            # VALIDATION: Check if DataFrame has data
            if df.empty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The uploaded file contains no data"
                )
            
            # Generate chart based on type with Chart.js compatibility
            chart_data = await self._generate_chartjs_compatible(df, request)
            
            # VALIDATION: Ensure chart_data is properly formatted
            if not chart_data or not isinstance(chart_data, dict):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate chart configuration"
                )
            
            # Store visualization in database
            try:
                db_visualization = Visualization(
                    file_id=file.id,
                    user_id=file.user_id or "default-user-id",  # Use default if None
                    chart_type=request.chart_type,
                    chart_data=chart_data,  # Already JSON serializable from json_serialize function
                    chart_options=chart_data.get("options", {}),
                    chart_metadata={
                        "columns_used": self._get_columns_used(request),
                        "data_shape": list(df.shape),  # Convert to list for JSON serialization
                        "columns_available": list(df.columns)
                    }
                )
                
                self.db.add(db_visualization)
                self.db.commit()
                self.db.refresh(db_visualization)
                logger.info(f"Visualization stored in database with ID: {db_visualization.id}")
            except Exception as db_error:
                logger.warning(f"Failed to store visualization in database: {str(db_error)}")
                # Continue without storing - the chart can still be returned
            
            # Return Chart.js compatible response
            response = {
                "success": True,
                "chart_type": request.chart_type,
                "library_used": "chartjs",
                "mode": "interactive",
                "title": f"{request.chart_type.title()} Chart - {file.original_filename}",
                "chart_data": chart_data,  # Chart.js compatible format (matches frontend expectation)
                "metadata": {
                    "file_name": file.original_filename,
                    "data_shape": list(df.shape),
                    "columns": list(df.columns),
                    "columns_used": self._get_columns_used(request),
                    "total_rows": len(df),
                    "total_columns": len(df.columns)
                }
            }

            logger.info(f"Chart generated successfully: {request.chart_type}")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Visualization generation failed: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chart generation failed: {str(e)}"
            )
    
    async def _load_file_data(self, file) -> pd.DataFrame:
        """Load file data with proper error handling - IMPROVED VERSION."""
        try:
            file_path = file.file_path
            logger.info(f"Loading file from path: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File does not exist at path: {file_path}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File not found at path: {file_path}"
                )
            
            # Check file size (limit to 50MB)
            file_size = os.path.getsize(file_path)
            logger.info(f"File size: {file_size} bytes")
            
            if file_size > 50 * 1024 * 1024:  # 50MB
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File too large (max 50MB)"
                )
            
            # Read file based on type
            df = None
            if file.file_type.lower() == 'csv':
                # Try different encodings and separators
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                separators = [',', ';', '\t']
                
                for encoding in encodings:
                    for sep in separators:
                        try:
                            logger.info(f"Trying CSV with encoding: {encoding}, separator: '{sep}'")
                            df = pd.read_csv(file_path, encoding=encoding, sep=sep)
                            
                            # Check if we got meaningful columns (more than 1 column or meaningful data)
                            if len(df.columns) > 1 or (len(df.columns) == 1 and len(df) > 0):
                                logger.info(f"Successfully loaded CSV with {encoding} encoding and '{sep}' separator")
                                break
                        except Exception as e:
                            logger.debug(f"Failed with {encoding}/{sep}: {str(e)}")
                            continue
                    
                    if df is not None and len(df.columns) > 1:
                        break
                
                if df is None or len(df.columns) <= 1:
                    # Try with automatic detection
                    try:
                        df = pd.read_csv(file_path, encoding='utf-8', sep=None, engine='python')
                        logger.info("Successfully loaded CSV with automatic separator detection")
                    except Exception as e:
                        raise ValueError(f"Could not read CSV file: {str(e)}")
                    
            elif file.file_type.lower() in ['xlsx', 'xls']:
                try:
                    df = pd.read_excel(file_path, sheet_name=0)  # Read first sheet
                    logger.info("Successfully loaded Excel file")
                except Exception as e:
                    raise ValueError(f"Could not read Excel file: {str(e)}")
            else:
                raise ValueError(f"Unsupported file type: {file.file_type}")
            
            # Validate DataFrame
            if df is None:
                raise ValueError("Failed to load file - no data found")
            
            if df.empty:
                raise ValueError("File is empty or contains no data")
            
            # Clean and prepare DataFrame
            df = self._clean_dataframe(df)
            
            logger.info(f"DataFrame loaded successfully: {df.shape}")
            logger.info(f"Columns after cleaning: {list(df.columns)}")
            
            return df
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to load file data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load file data: {str(e)}"
            )
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare DataFrame for visualization."""
        try:
            # Clean column names (remove extra whitespace and special characters)
            df.columns = df.columns.astype(str).str.strip()
            
            # Remove completely empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Limit DataFrame size for performance (keep first 10,000 rows)
            if len(df) > 10000:
                logger.warning(f"Large dataset ({len(df)} rows), limiting to first 10,000 rows")
                df = df.head(10000)
            
            # Convert columns to appropriate types
            for col in df.columns:
                try:
                    # Try to convert to numeric
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
            
            # Replace infinite values with NaN
            df = df.replace([np.inf, -np.inf], np.nan)
            
            return df
            
        except Exception as e:
            logger.error(f"DataFrame cleaning failed: {str(e)}")
            return df  # Return original if cleaning fails
    
    async def _generate_chartjs_compatible(self, df: pd.DataFrame, request: VisualizationRequest) -> Dict[str, Any]:
        """Generate Chart.js compatible data - IMPROVED VERSION."""
        try:
            logger.info(f"Generating Chart.js data for {request.chart_type}")
            
            # Get numeric and categorical columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
            
            logger.info(f"Numeric columns: {numeric_cols}")
            logger.info(f"Categorical columns: {categorical_cols}")
            
            # Generate chart based on type
            chart_generators = {
                "histogram": self._generate_histogram_chartjs,
                "bar": self._generate_bar_chartjs,
                "line": self._generate_line_chartjs,
                "pie": self._generate_pie_chartjs,
                "scatter": self._generate_scatter_chartjs
            }
            
            chart_type = request.chart_type.lower()
            if chart_type not in chart_generators:
                logger.warning(f"Unsupported chart type {chart_type}, defaulting to bar")
                chart_type = "bar"
            
            generator = chart_generators[chart_type]
            return await generator(df, request, numeric_cols, categorical_cols)
                
        except Exception as e:
            logger.error(f"Chart.js generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chart generation failed: {str(e)}"
            )
    
    async def _generate_histogram_chartjs(self, df: pd.DataFrame, request: VisualizationRequest, 
                                        numeric_cols: List[str], categorical_cols: List[str]) -> Dict[str, Any]:
        """Generate histogram for Chart.js - IMPROVED VERSION."""
        # Determine column to use
        column = request.column or (request.columns[0] if request.columns else None)
        
        if not column:
            if numeric_cols:
                column = numeric_cols[0]
                logger.info(f"No column specified, using first numeric: {column}")
            elif categorical_cols:
                column = categorical_cols[0]
                logger.info(f"No numeric columns, using first categorical: {column}")
            else:
                raise ValueError("No suitable columns found for histogram")
        
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found. Available: {list(df.columns)}")
        
        # For categorical data, create frequency chart
        if column in categorical_cols or df[column].dtype == 'object':
            logger.info(f"Column {column} is categorical, creating frequency chart")
            
            # Get value counts and handle NaN
            value_counts = df[column].fillna('Missing').value_counts().head(20)
            
            if value_counts.empty:
                raise ValueError(f"Column '{column}' has no valid data")
            
            return {
                "type": "bar",
                "data": {
                    "labels": [str(label) for label in value_counts.index.tolist()],
                    "datasets": [{
                        "label": f"Count of {column}",
                        "data": value_counts.values.tolist(),
                        "backgroundColor": "rgba(54, 162, 235, 0.6)",
                        "borderColor": "rgba(54, 162, 235, 1)",
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": f"Distribution of {column}"
                        }
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Count"
                            }
                        },
                        "x": {
                            "title": {
                                "display": True,
                                "text": column
                            }
                        }
                    }
                }
            }
        
        # For numeric data, create histogram
        else:
            logger.info(f"Column {column} is numeric, creating histogram")
            data_clean = df[column].dropna()
            
            if data_clean.empty:
                raise ValueError(f"Column '{column}' has no valid numeric data")
            
            # Create bins
            bins = min(request.bins or 20, 50)  # Limit bins to 50
            try:
                counts, bin_edges = np.histogram(data_clean, bins=bins)
                
                # Create labels for bins
                labels = []
                for i in range(len(bin_edges)-1):
                    start = bin_edges[i]
                    end = bin_edges[i+1]
                    labels.append(f"{start:.2f}-{end:.2f}")
                
                return {
                    "type": "bar",
                    "data": {
                        "labels": labels,
                        "datasets": [{
                            "label": f"Frequency of {column}",
                            "data": counts.tolist(),
                            "backgroundColor": "rgba(75, 192, 192, 0.6)",
                            "borderColor": "rgba(75, 192, 192, 1)",
                            "borderWidth": 1
                        }]
                    },
                    "options": {
                        "responsive": True,
                        "maintainAspectRatio": False,
                        "plugins": {
                            "title": {
                                "display": True,
                                "text": f"Histogram of {column}"
                            }
                        },
                        "scales": {
                            "y": {
                                "beginAtZero": True,
                                "title": {
                                    "display": True,
                                    "text": "Frequency"
                                }
                            },
                            "x": {
                                "title": {
                                    "display": True,
                                    "text": column
                                }
                            }
                        }
                    }
                }
            except Exception as e:
                raise ValueError(f"Failed to create histogram bins: {str(e)}")
    
    async def _generate_bar_chartjs(self, df: pd.DataFrame, request: VisualizationRequest,
                                  numeric_cols: List[str], categorical_cols: List[str]) -> Dict[str, Any]:
        """Generate bar chart for Chart.js - IMPROVED VERSION."""
        column = request.column or (request.columns[0] if request.columns else None)
        
        if not column:
            if categorical_cols:
                column = categorical_cols[0]
                logger.info(f"No column specified, using first categorical: {column}")
            else:
                # Use first column anyway
                column = df.columns[0]
                logger.info(f"No categorical columns, using first column: {column}")
        
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found. Available: {list(df.columns)}")
        
        top_n = min(request.top_n or 20, 50)  # Limit to 50 bars
        
        # Handle different data types
        if df[column].dtype in ['object', 'category', 'string']:
            value_counts = df[column].fillna('Missing').value_counts().head(top_n)
        else:
            # For numeric columns, create bins
            try:
                binned_data = pd.cut(df[column].dropna(), bins=min(top_n, 10), duplicates='drop')
                value_counts = binned_data.value_counts().sort_index()
            except Exception:
                # Fallback to value counts for numeric data
                value_counts = df[column].fillna('Missing').value_counts().head(top_n)
        
        if value_counts.empty:
            raise ValueError(f"Column '{column}' has no valid data")
        
        return {
            "type": "bar",
            "data": {
                "labels": [str(label) for label in value_counts.index.tolist()],
                "datasets": [{
                    "label": f"Count of {column}",
                    "data": value_counts.values.tolist(),
                    "backgroundColor": "rgba(255, 99, 132, 0.6)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"Top {len(value_counts)} values in {column}"
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": "Count"
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": column
                        }
                    }
                }
            }
        }
    
    async def _generate_line_chartjs(self, df: pd.DataFrame, request: VisualizationRequest,
                                   numeric_cols: List[str], categorical_cols: List[str]) -> Dict[str, Any]:
        """Generate line chart for Chart.js - IMPROVED VERSION."""
        x_col = request.x_column
        y_col = request.y_column
        
        if not x_col or not y_col:
            if len(numeric_cols) >= 2:
                x_col = numeric_cols[0]
                y_col = numeric_cols[1]
                logger.info(f"Using default numeric columns: {x_col}, {y_col}")
            elif len(df.columns) >= 2:
                x_col = df.columns[0]
                y_col = df.columns[1]
                logger.info(f"Using first two columns: {x_col}, {y_col}")
            else:
                raise ValueError("Need at least 2 columns for line chart")
        
        if x_col not in df.columns or y_col not in df.columns:
            raise ValueError(f"Columns not found. Available: {list(df.columns)}")
        
        # Filter and prepare data
        df_clean = df[[x_col, y_col]].dropna()
        
        if df_clean.empty:
            raise ValueError("No valid data found for the selected columns")
        
        # Sort by x column and limit size
        try:
            if df_clean[x_col].dtype in ['object', 'category']:
                # For categorical x-axis, don't sort
                df_sorted = df_clean.head(100)
            else:
                # For numeric x-axis, sort by x
                df_sorted = df_clean.sort_values(x_col).head(100)
        except Exception:
            df_sorted = df_clean.head(100)
        
        # Prepare labels and data
        labels = [str(val) for val in df_sorted[x_col].tolist()]
        data_values = df_sorted[y_col].tolist()
        
        return {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": y_col,
                    "data": data_values,
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "backgroundColor": "rgba(54, 162, 235, 0.1)",
                    "borderWidth": 2,
                    "fill": False,
                    "tension": 0.1
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{y_col} vs {x_col}"
                    }
                },
                "scales": {
                    "y": {
                        "title": {
                            "display": True,
                            "text": y_col
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": x_col
                        }
                    }
                }
            }
        }
    
    async def _generate_pie_chartjs(self, df: pd.DataFrame, request: VisualizationRequest,
                                  numeric_cols: List[str], categorical_cols: List[str]) -> Dict[str, Any]:
        """Generate pie chart for Chart.js - IMPROVED VERSION."""
        column = request.column or (request.columns[0] if request.columns else None)
        
        if not column:
            if categorical_cols:
                column = categorical_cols[0]
            else:
                column = df.columns[0]
        
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found. Available: {list(df.columns)}")
        
        top_n = min(request.top_n or 8, 10)  # Limit pie slices to 10
        value_counts = df[column].fillna('Missing').value_counts().head(top_n)
        
        if value_counts.empty:
            raise ValueError(f"Column '{column}' has no valid data")
        
        # Generate colors
        colors = [
            "rgba(255, 99, 132, 0.8)",
            "rgba(54, 162, 235, 0.8)",
            "rgba(255, 205, 86, 0.8)",
            "rgba(75, 192, 192, 0.8)",
            "rgba(153, 102, 255, 0.8)",
            "rgba(255, 159, 64, 0.8)",
            "rgba(199, 199, 199, 0.8)",
            "rgba(83, 102, 255, 0.8)",
            "rgba(255, 99, 255, 0.8)",
            "rgba(99, 255, 132, 0.8)"
        ]
        
        return {
            "type": "pie",
            "data": {
                "labels": [str(label) for label in value_counts.index.tolist()],
                "datasets": [{
                    "label": f"Distribution of {column}",
                    "data": value_counts.values.tolist(),
                    "backgroundColor": colors[:len(value_counts)]
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"Distribution of {column}"
                    }
                }
            }
        }
    
    async def _generate_scatter_chartjs(self, df: pd.DataFrame, request: VisualizationRequest,
                                      numeric_cols: List[str], categorical_cols: List[str]) -> Dict[str, Any]:
        """Generate scatter plot for Chart.js - IMPROVED VERSION."""
        x_col = request.x_column
        y_col = request.y_column
        
        if not x_col or not y_col:
            if len(numeric_cols) >= 2:
                x_col = numeric_cols[0]
                y_col = numeric_cols[1]
            else:
                raise ValueError("Need at least 2 numeric columns for scatter plot")
        
        if x_col not in df.columns or y_col not in df.columns:
            raise ValueError(f"Columns not found. Available: {list(df.columns)}")
        
        # Prepare data
        df_clean = df[[x_col, y_col]].dropna()
        
        if df_clean.empty:
            raise ValueError("No valid data found for the selected columns")
        
        # Sample data if too large (limit to 1000 points for performance)
        if len(df_clean) > 1000:
            df_sample = df_clean.sample(n=1000, random_state=42)
            logger.info(f"Sampled {len(df_sample)} points from {len(df_clean)} total")
        else:
            df_sample = df_clean
        
        # Convert to scatter data format
        scatter_data = []
        for _, row in df_sample.iterrows():
            try:
                x_val = float(row[x_col]) if pd.notnull(row[x_col]) else 0
                y_val = float(row[y_col]) if pd.notnull(row[y_col]) else 0
                scatter_data.append({"x": x_val, "y": y_val})
            except (ValueError, TypeError):
                continue  # Skip invalid data points
        
        if not scatter_data:
            raise ValueError("No valid numeric data points found")
        
        return {
            "type": "scatter",
            "data": {
                "datasets": [{
                    "label": f"{y_col} vs {x_col}",
                    "data": scatter_data,
                    "backgroundColor": "rgba(255, 99, 132, 0.6)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "pointRadius": 4,
                    "pointHoverRadius": 6
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{y_col} vs {x_col} Scatter Plot"
                    }
                },
                "scales": {
                    "y": {
                        "title": {
                            "display": True,
                            "text": y_col
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": x_col
                        }
                    }
                }
            }
        }
    
    def _get_columns_used(self, request: VisualizationRequest) -> List[str]:
        """Get list of columns used in the visualization."""
        columns = []
        if request.column:
            columns.append(request.column)
        if request.columns:
            columns.extend(request.columns)
        if request.x_column:
            columns.append(request.x_column)
        if request.y_column:
            columns.append(request.y_column)
        if request.color_column:
            columns.append(request.color_column)
        return list(set(filter(None, columns)))  # Remove None values and duplicates
    
    async def verify_file_ownership(self, file_id: str, user_id: str) -> bool:
        """Verify that a file belongs to a user."""
        try:
            file = self.db.query(File).filter(
                File.id == file_id,
                File.user_id == user_id
            ).first()
            
            return file is not None
            
        except Exception as e:
            logger.error(f"File ownership verification failed: {str(e)}")
            return False
    
    async def get_available_visualizations(self, file_id: str) -> Dict[str, Any]:
        """Get available visualization types for a file."""
        try:
            file = self.db.query(File).filter(File.id == file_id).first()
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Load data and analyze
            df = await self._load_file_data(file)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
            
            available_viz = {
                "bar": {
                    "suitable": len(df.columns) > 0,
                    "columns": categorical_cols + numeric_cols,
                    "description": "Show counts or frequencies of categorical data"
                },
                "histogram": {
                    "suitable": len(numeric_cols) > 0 or len(categorical_cols) > 0,
                    "columns": numeric_cols + categorical_cols,
                    "description": "Show distribution of values in a column"
                },
                "line": {
                    "suitable": len(df.columns) >= 2,
                    "columns": list(df.columns),
                    "description": "Show trends over time or relationships between two variables"
                },
                "scatter": {
                    "suitable": len(numeric_cols) >= 2,
                    "columns": numeric_cols,
                    "description": "Show correlation between two numeric variables"
                },
                "pie": {
                    "suitable": len(categorical_cols) > 0 or len(df.columns) > 0,
                    "columns": categorical_cols if categorical_cols else list(df.columns),
                    "description": "Show proportions of different categories"
                }
            }

            return {
                "available_visualizations": available_viz,
                "summary": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "numeric_columns": len(numeric_cols),
                    "categorical_columns": len(categorical_cols),
                    "column_info": {
                        "numeric": numeric_cols,
                        "categorical": categorical_cols,
                        "all_columns": list(df.columns)
                    }
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get available visualizations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get available visualizations"
            )