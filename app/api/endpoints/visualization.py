# app/api/endpoints/visualization.py
"""
Apollo AI Visualization API Endpoints
Endpoints for chart generation and download functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import tempfile
import os

from app.services.visualization_service import VisualizationService
from app.core.analyzer import DataAnalyzer
from app.models.schemas import ChartRequest, ChartResponse, ChartRecommendationResponse, ChartType

router = APIRouter(prefix="/visualization", tags=["visualization"])

# Initialize visualization service
viz_service = VisualizationService()


@router.post("/recommend-charts", response_model=ChartRecommendationResponse)
async def recommend_charts(file: UploadFile = File(...)):
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


@router.post("/generate-chart", response_model=ChartResponse)
async def generate_chart(
    file: UploadFile = File(...),
    chart_type: str = Query(..., description="Type of chart to generate"),
    columns: str = Query(..., description="Comma-separated list of columns to use for the chart"),
    options: Optional[str] = Query(None, description="Additional chart options as JSON string")
):
    """
    Generate a specific chart from uploaded CSV data.
    """
    try:
        # Parse columns from comma-separated string
        column_list = [col.strip() for col in columns.split(',')]
        
        # Parse options if provided
        chart_options = {}
        if options:
            import json
            try:
                chart_options = json.loads(options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in options parameter")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Load data
        df = pd.read_csv(tmp_file_path)
        
        # Validate columns exist
        missing_cols = [col for col in column_list if col not in df.columns]
        if missing_cols:
            raise HTTPException(status_code=400, detail=f"Columns not found: {missing_cols}")
        
        # Generate chart
        result = viz_service.generate_chart(df, chart_type, column_list, chart_options)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        if not result.get('success', False):
            raise HTTPException(status_code=400, detail=result.get('error', 'Chart generation failed'))
        
        return ChartResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating chart: {str(e)}")


@router.get("/download/{filename}")
async def download_chart(filename: str):
    """
    Download a generated chart file.
    """
    file_path = viz_service.output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='image/png'
    )


@router.get("/available-chart-types")
async def get_available_chart_types():
    """
    Get list of all available chart types.
    """
    chart_types = [
        {
            "type": chart_type.value,
            "name": chart_type.value.replace('_', ' ').title(),
            "description": get_chart_description(chart_type.value)
        }
        for chart_type in ChartType
    ]
    
    return {
        "success": True,
        "chart_types": chart_types
    }


@router.post("/auto-generate-best-charts")
async def auto_generate_best_charts(file: UploadFile = File(...)):
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