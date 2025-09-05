"""
Visualization Router
Handles chart generation and visualization operations.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import VisualizationRequest, VisualizationResponse
from app.services.visualization_service import VisualizationService
from app.database.models import File
# from app.core.security import get_current_user  # Temporarily disabled

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/visualization", tags=["Data Visualization"])

@router.post("/", response_model=VisualizationResponse)
async def generate_visualization(
    request: VisualizationRequest,
    # current_user = Depends(get_current_user)  # Temporarily disabled
):
    """Generate visualization for uploaded data."""
    try:
        visualization_service = VisualizationService()
        
        # Verify file ownership (temporarily disabled)
        # if not await visualization_service.verify_file_ownership(request.file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        # Generate visualization
        start_time = datetime.now()
        result = await visualization_service.generate_chart(request)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Visualization generated for file {request.file_id}")  # Removed user reference
        
        return VisualizationResponse(
            file_id=request.file_id,
            chart_type=request.chart_type,
            chart_data=result["chart_data"],  # Chart.js compatible data
            available_visualizations=["histogram", "bar", "line", "pie", "scatter"],  # Default available types as list
            recommendations=[],  # No recommendations for now
            generation_timestamp=datetime.now(),
            message="Visualization generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Visualization generation failed for file {request.file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visualization generation failed. Please try again."
        )

@router.get("/{file_id}/available")
async def get_available_visualizations(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled
):
    """Get available visualization types for a file."""
    try:
        visualization_service = VisualizationService()
        
        # Verify file ownership (temporarily disabled)
        # if not await visualization_service.verify_file_ownership(file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        available_viz = await visualization_service.get_available_visualizations(file_id)
        
        logger.info(f"Available visualizations retrieved for file {file_id}")  # Removed user reference
        return available_viz
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get available visualizations for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available visualizations"
        )

@router.get("/{file_id}/recommendations")
async def get_visualization_recommendations(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled
):
    """Get chart recommendations for a file."""
    try:
        visualization_service = VisualizationService()
        
        # Verify file ownership (temporarily disabled)
        # if not await visualization_service.verify_file_ownership(file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        recommendations = await visualization_service.get_chart_recommendations(file_id)
        
        logger.info(f"Visualization recommendations retrieved for file {file_id}")  # Removed user reference
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get visualization recommendations for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve visualization recommendations"
        )

@router.get("/{file_id}/charts")
async def list_generated_charts(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled
):
    """List all charts generated for a file."""
    try:
        visualization_service = VisualizationService()
        
        # Verify file ownership (temporarily disabled)
        # if not await visualization_service.verify_file_ownership(file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        charts = await visualization_service.list_generated_charts(file_id)
        
        logger.info(f"Generated charts list retrieved for file {file_id}")  # Removed user reference
        return charts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list generated charts for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve generated charts"
        )

@router.get("/{file_id}/columns")
async def get_file_columns(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled
):
    """Get detailed column information for a file."""
    try:
        visualization_service = VisualizationService()

        # Get file data
        file = visualization_service.db.query(File).filter(File.id == file_id).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        # Load data and analyze
        import pandas as pd
        df = pd.read_csv(file.file_path)

        # Create visualizer for proper data type detection
        from app.core.visualizer import DataVisualizer
        visualizer = DataVisualizer(df)

        # Get column information with proper type detection
        columns = []
        for col in df.columns:
            # Determine column type based on visualizer's classification
            if col in visualizer.numeric_columns:
                col_type = 'numeric'
            elif col in visualizer.datetime_columns:
                col_type = 'datetime'
            elif col in visualizer.categorical_columns:
                col_type = 'categorical'
            else:
                col_type = 'text'

            # Get sample values
            sample_values = df[col].dropna().head(3).tolist()

            columns.append({
                "name": col,
                "type": col_type,
                "sample_values": sample_values
            })

        return {
            "file_id": file_id,
            "columns": columns,
            "total_columns": len(columns)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get column information for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get column information: {str(e)}"
        )

@router.get("/{file_id}/debug")
async def debug_file_visualization(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled
):
    """Debug endpoint to check file data and column types for visualization."""
    try:
        visualization_service = VisualizationService()

        # Get file data
        file = visualization_service.db.query(File).filter(File.id == file_id).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        # Load data and analyze
        import pandas as pd
        df = pd.read_csv(file.file_path)

        # Get column information
        column_info = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            sample_values = df[col].dropna().head(3).tolist()
            null_count = df[col].isnull().sum()
            unique_count = df[col].nunique()

            column_info[col] = {
                "dtype": dtype,
                "sample_values": sample_values,
                "null_count": int(null_count),
                "unique_count": int(unique_count),
                "total_count": int(len(df))
            }

        return {
            "file_id": file_id,
            "filename": file.original_filename,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": column_info,
            "data_preview": df.head(5).to_dict(orient='records')
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debug failed for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug failed: {str(e)}"
        ) 