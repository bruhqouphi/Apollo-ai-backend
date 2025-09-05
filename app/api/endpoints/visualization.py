# app/api/endpoints/visualization.py
"""
Apollo AI Visualization API Endpoints  
Pure Matplotlib implementation - generates chart images on backend.
Replaces Chart.js with server-side generated PNG images.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, Form, File
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import tempfile
import os
import logging

# Changed: Import smart chart service for intelligent library selection
from app.services.smart_chart_service import SmartChartService, ChartMode
from app.core.analyzer import DataAnalyzer
from app.models.schemas import ChartRequest, ChartResponse, ChartRecommendationResponse, ChartType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/visualization", tags=["visualization"])

# Changed: Initialize smart chart service
chart_service = SmartChartService()

# Alias for backward compatibility
viz_service = chart_service


@router.post("/recommend-charts", response_model=ChartRecommendationResponse)
async def recommend_charts(file: UploadFile):
    """
    Get intelligent chart recommendations for uploaded CSV data.
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Analyze the data
        analyzer = DataAnalyzer(tmp_file_path)
        df = analyzer.df
        column_types = analyzer.column_types
        
        # Get chart recommendations
        recommendations = viz_service.get_available_charts(df, column_types)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return ChartRecommendationResponse(
            success=True,
            recommendations=recommendations,
            total_columns=len(df.columns),
            column_types=column_types
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@router.post("/generate-chart")
async def generate_chart(
    file: UploadFile,
    chart_type: str = Query(..., description="Type of chart to generate"),
    columns: str = Query(..., description="Comma-separated list of columns to use for the chart"),
    mode: str = Query("auto", description="Chart mode: 'interactive', 'static', or 'auto'"),
    bins: Optional[int] = Query(30, description="Number of bins for histogram"),
    title: Optional[str] = Query(None, description="Custom chart title")
):
    """
    Generate a chart using smart library selection.
    Automatically chooses the best visualization library based on chart type and requirements.
    """
    try:
        # Parse columns from comma-separated string
        column_list = [col.strip() for col in columns.split(',')]
        
        # Validate chart mode
        try:
            chart_mode = ChartMode(mode.lower())
        except ValueError:
            chart_mode = ChartMode.AUTO
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Load data
        df = pd.read_csv(tmp_file_path)

        logger.info(f"Loaded CSV with columns: {list(df.columns)}")
        logger.info(f"Requested columns: {column_list}")

        # Create normalized column mapping for flexible matching
        def normalize_column_name(col_name: str) -> str:
            """Normalize column names for flexible matching."""
            return str(col_name).strip().lower().replace(' ', '_').replace('-', '_')

        # Create mapping from normalized names to actual column names
        column_mapping = {normalize_column_name(col): col for col in df.columns}
        logger.info(f"Column mapping: {column_mapping}")

        # Validate and map columns
        mapped_columns = []
        missing_cols = []

        for requested_col in column_list:
            normalized_requested = normalize_column_name(requested_col)
            logger.info(f"Requested: '{requested_col}' -> Normalized: '{normalized_requested}'")
            if normalized_requested in column_mapping:
                actual_col = column_mapping[normalized_requested]
                mapped_columns.append(actual_col)
                logger.info(f"[SUCCESS] Mapped '{requested_col}' to '{actual_col}'")
            else:
                missing_cols.append(requested_col)
                logger.error(f"[ERROR] Column '{requested_col}' not found")

        if missing_cols:
            available_cols = list(df.columns)
            normalized_available = [normalize_column_name(col) for col in available_cols]
            logger.error(f"Missing columns: {missing_cols}")
            logger.info(f"Available: {available_cols}")
            logger.info(f"Normalized available: {normalized_available}")
            raise HTTPException(
                status_code=400,
                detail=f"Columns not found: {missing_cols}. Available columns: {available_cols}. Normalized available: {normalized_available}"
            )

        # Use mapped columns instead of original column_list
        logger.info(f"Final mapped columns: {mapped_columns}")
        column_list = mapped_columns
        
        # Generate chart using smart chart service
        chart_options = {}
        if bins and chart_type == 'histogram':
            chart_options['bins'] = bins
        if title:
            chart_options['title'] = title
            
        result = chart_service.generate_chart(df, chart_type, column_list, chart_mode, **chart_options)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        if not result.get('success', False):
            raise HTTPException(status_code=400, detail=result.get('error', 'Chart generation failed'))
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating chart: {str(e)}")


@router.get("/image/{filename}")
async def get_chart_image(filename: str):
    """
    Serve generated chart image for display in frontend.
    """
    file_path = chart_service.output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Chart image not found")
    
    return FileResponse(
        path=file_path,
        media_type='image/png',
        headers={"Cache-Control": "max-age=3600"}  # Cache for 1 hour
    )

@router.get("/interactive/{filename}")
async def get_interactive_chart(filename: str):
    """
    Serve interactive chart HTML for display in frontend.
    """
    # Check both chart service and temp_charts directory
    file_path = chart_service.output_dir / filename
    
    if not file_path.exists():
        # Try temp_charts directory
        temp_charts_dir = Path("./temp_charts")
        file_path = temp_charts_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Interactive chart not found")
    
    return FileResponse(
        path=file_path,
        media_type='text/html',
        headers={"Cache-Control": "max-age=3600"}  # Cache for 1 hour
    )

@router.get("/download/{filename}")
async def download_chart(filename: str):
    """
    Download a generated chart file.
    """
    file_path = chart_service.output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='image/png',
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/available-chart-types")
async def get_available_chart_types():
    """
    Get list of all available chart types with smart library support.
    """
    chart_types = [
        {
            "type": "histogram",
            "name": "Histogram",
            "description": "Shows distribution of numerical data",
            "columns_required": 1,
            "column_types": ["numeric"],
            "modes": ["static", "interactive"],
            "recommended_mode": "static"
        },
        {
            "type": "bar_chart", 
            "name": "Bar Chart",
            "description": "Compares categorical data or shows counts",
            "columns_required": "1-2",
            "column_types": ["categorical", "numeric"],
            "modes": ["static", "interactive"],
            "recommended_mode": "interactive"
        },
        {
            "type": "line_chart",
            "name": "Line Chart", 
            "description": "Shows trends over time or continuous variables",
            "columns_required": 2,
            "column_types": ["numeric", "datetime"],
            "modes": ["static", "interactive"],
            "recommended_mode": "interactive"
        },
        {
            "type": "scatter_plot",
            "name": "Scatter Plot",
            "description": "Shows relationship between two numerical variables",
            "columns_required": 2,
            "column_types": ["numeric"],
            "modes": ["static", "interactive"],
            "recommended_mode": "interactive"
        },
        {
            "type": "pie_chart",
            "name": "Pie Chart",
            "description": "Shows proportions of categorical data",
            "columns_required": 1,
            "column_types": ["categorical"],
            "modes": ["static", "interactive"],
            "recommended_mode": "interactive"
        },
        {
            "type": "box_plot",
            "name": "Box Plot",
            "description": "Shows distribution and outliers of numerical data",
            "columns_required": 1,
            "column_types": ["numeric"],
            "modes": ["static", "interactive"],
            "recommended_mode": "static"
        },
        {
            "type": "violin_plot",
            "name": "Violin Plot",
            "description": "Shows distribution comparison across categories",
            "columns_required": 1,
            "column_types": ["numeric"],
            "modes": ["static"],
            "recommended_mode": "static"
        },
        {
            "type": "correlation_matrix",
            "name": "Correlation Matrix",
            "description": "Shows correlation between numeric variables",
            "columns_required": "2+",
            "column_types": ["numeric"],
            "modes": ["static", "interactive"],
            "recommended_mode": "static"
        }
    ]
    
    # Get available libraries
    available_libraries = chart_service.get_available_libraries()
    
    return {
        "success": True,
        "chart_types": chart_types,
        "available_libraries": available_libraries
    }


@router.post("/auto-generate-best-charts")
async def auto_generate_best_charts(file: UploadFile):
    """
    Automatically generate the best charts for the dataset.
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Analyze the data
        analyzer = DataAnalyzer(tmp_file_path)
        df = analyzer.df
        column_types = analyzer.column_types
        
        # Get recommendations
        recommendations = viz_service.get_available_charts(df, column_types)
        
        # Generate top charts
        generated_charts = []
        
        # Single column charts (top 3 recommendations per column)
        for column, col_recommendations in recommendations['single_column'].items():
            top_recommendations = [rec for rec in col_recommendations if rec['suitable']][:3]
            for rec in top_recommendations:
                try:
                    result = viz_service.generate_chart(df, rec['chart_type'], [column])
                    if result['success']:
                        generated_charts.append({
                            'column': column,
                            'chart_type': rec['chart_type'],
                            'reason': rec['reason'],
                            'result': result
                        })
                except Exception as e:
                    continue
        
        # Two column charts (top 2 recommendations)
        for rec in recommendations['two_column'][:2]:
            try:
                result = viz_service.generate_chart(df, rec['chart_type'], rec['columns'])
                if result['success']:
                    generated_charts.append({
                        'columns': rec['columns'],
                        'chart_type': rec['chart_type'],
                        'reason': rec['reason'],
                        'result': result
                    })
            except Exception as e:
                continue
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return {
            "success": True,
            "generated_charts": generated_charts,
            "total_generated": len(generated_charts)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error auto-generating charts: {str(e)}")


@router.delete("/cleanup")
async def cleanup_old_charts(hours: int = Query(24, description="Delete files older than this many hours")):
    """
    Clean up old chart files.
    """
    try:
        deleted_count = viz_service.cleanup_old_files(hours)
        return {
            "success": True,
            "deleted_files": deleted_count,
            "message": f"Deleted {deleted_count} files older than {hours} hours"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up files: {str(e)}")


def get_chart_description(chart_type: str) -> str:
    """Get description for chart type."""
    descriptions = {
        ChartType.histogram: "Shows distribution of numerical data",
        ChartType.bar_chart: "Compares categorical data",
        ChartType.line_chart: "Shows trends over time or continuous variables",
        ChartType.scatter_plot: "Shows relationship between two numerical variables",
        ChartType.box_plot: "Shows distribution and outliers of numerical data",
        ChartType.pie_chart: "Shows proportions of categorical data",
        ChartType.heatmap: "Shows correlation matrix or categorical relationships",
        ChartType.violin_plot: "Shows distribution comparison across categories",
        ChartType.density_plot: "Shows probability density of numerical data",
        ChartType.stacked_bar: "Shows composition of categorical data",
        ChartType.grouped_bar: "Compares numerical data across categories",
        ChartType.area_chart: "Shows trends with filled area"
    }
    return descriptions.get(chart_type, "Chart visualization") 