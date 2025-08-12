"""
Visualization Router
Handles chart generation and visualization operations.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import VisualizationRequest, VisualizationResponse
from app.services.visualization_service import VisualizationService
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
            chart_data=result["chart_data"],
            available_visualizations=result["available_visualizations"],
            recommendations=result["recommendations"],
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