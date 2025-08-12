"""
Visualization Service
Handles chart generation and visualization operations with database storage.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import pandas as pd

from app.database.database import get_database
from app.database.models import File, Visualization, User
from app.core.visualizer import DataVisualizer
from app.models.schemas import VisualizationRequest

logger = logging.getLogger(__name__)

class VisualizationService:
    """Service for handling visualization operations."""
    
    def __init__(self):
        self.db: Session = next(get_database())
    
    async def generate_chart(self, request: VisualizationRequest) -> Dict[str, Any]:
        """Generate chart for uploaded data."""
        try:
            # Get file from database
            file = self.db.query(File).filter(File.id == request.file_id).first()
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Load data and create visualizer
            df = pd.read_csv(file.file_path) if file.file_type == 'csv' else pd.read_excel(file.file_path)
            visualizer = DataVisualizer(df)
            
            # Generate chart based on type
            chart_data = await self._generate_chart_by_type(visualizer, request)
            
            # Get available visualizations and recommendations
            available_viz = visualizer.get_available_visualizations()
            recommendations = visualizer.generate_visualization_summary().get("recommendations", [])
            
            # Store visualization in database
            db_visualization = Visualization(
                file_id=file.id,
                user_id=file.user_id,
                chart_type=request.chart_type,
                chart_data=chart_data,
                chart_options=chart_data.get("options", {}),
                metadata={
                    "columns_used": self._get_columns_used(request),
                    "available_visualizations": available_viz
                }
            )
            
            self.db.add(db_visualization)
            self.db.commit()
            self.db.refresh(db_visualization)
            
            logger.info(f"Visualization generated for file {file.original_filename}: {request.chart_type}")
            
            return {
                "chart_data": chart_data,
                "available_visualizations": list(available_viz.keys()),
                "recommendations": recommendations
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Visualization generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Visualization generation failed"
            )
    
    async def _generate_chart_by_type(self, visualizer: DataVisualizer, request: VisualizationRequest) -> Dict[str, Any]:
        """Generate chart data based on chart type."""
        try:
            if request.chart_type == "histogram":
                if not request.column:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Column is required for histogram"
                    )
                return visualizer.generate_histogram(request.column, request.bins or 20)
                
            elif request.chart_type == "bar":
                if not request.column:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Column is required for bar chart"
                    )
                return visualizer.generate_bar_chart(request.column, request.top_n or 10)
                
            elif request.chart_type == "line":
                if not request.x_column or not request.y_column:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Both x_column and y_column are required for line chart"
                    )
                return visualizer.generate_line_chart(request.x_column, request.y_column)
                
            elif request.chart_type == "pie":
                if not request.column:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Column is required for pie chart"
                    )
                return visualizer.generate_pie_chart(request.column, request.top_n or 8)
                
            elif request.chart_type == "scatter":
                if not request.x_column or not request.y_column:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Both x_column and y_column are required for scatter plot"
                    )
                return visualizer.generate_scatter_plot(request.x_column, request.y_column, request.color_column)
                
            elif request.chart_type == "heatmap":
                if not request.columns:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Columns are required for heatmap"
                    )
                return visualizer.generate_heatmap(request.columns)
                
            elif request.chart_type == "boxplot":
                if not request.columns:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Columns are required for boxplot"
                    )
                return visualizer.generate_boxplot(request.columns)
                
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported chart type: {request.chart_type}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Chart generation failed for type {request.chart_type}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate {request.chart_type} chart"
            )
    
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
        return list(set(columns))  # Remove duplicates
    
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
            
            # Load data and get available visualizations
            df = pd.read_csv(file.file_path) if file.file_type == 'csv' else pd.read_excel(file.file_path)
            visualizer = DataVisualizer(df)
            
            available_viz = visualizer.get_available_visualizations()
            summary = visualizer.generate_visualization_summary()
            
            return {
                "available_visualizations": available_viz,
                "summary": summary
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get available visualizations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get available visualizations"
            )
    
    async def get_chart_recommendations(self, file_id: str) -> Dict[str, Any]:
        """Get chart recommendations for a file."""
        try:
            file = self.db.query(File).filter(File.id == file_id).first()
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Load data and get recommendations
            df = pd.read_csv(file.file_path) if file.file_type == 'csv' else pd.read_excel(file.file_path)
            visualizer = DataVisualizer(df)
            
            summary = visualizer.generate_visualization_summary()
            
            return {
                "recommendations": summary.get("recommendations", []),
                "best_charts": summary.get("best_charts", {}),
                "data_insights": summary.get("data_insights", {})
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get chart recommendations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get chart recommendations"
            )
    
    async def list_generated_charts(self, file_id: str) -> List[Dict[str, Any]]:
        """List all charts generated for a file."""
        try:
            visualizations = self.db.query(Visualization).filter(
                Visualization.file_id == file_id
            ).order_by(Visualization.created_at.desc()).all()
            
            return [
                {
                    "id": viz.id,
                    "chart_type": viz.chart_type,
                    "created_at": viz.created_at,
                    "metadata": viz.metadata
                }
                for viz in visualizations
            ]
            
        except Exception as e:
            logger.error(f"Failed to list generated charts: {str(e)}")
            return [] 