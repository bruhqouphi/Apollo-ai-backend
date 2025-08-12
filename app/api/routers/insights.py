"""
Insights Router
Handles AI-powered insights generation.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import InsightRequest, InsightResponse
from app.services.insight_service import InsightService
from app.core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/insights", tags=["AI Insights"])

@router.post("/", response_model=InsightResponse)
async def generate_insights(
    request: InsightRequest,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Generate AI-powered insights for uploaded data."""
    try:
        insight_service = InsightService()
        
        # Verify file ownership (temporarily disabled for testing)
        # if not await insight_service.verify_file_ownership(request.file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        # Generate insights
        start_time = datetime.now()
        result = await insight_service.generate_insights(request)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Insights generated for file {request.file_id}")
        
        return InsightResponse(
            file_id=request.file_id,
            insights=result["insights"],
            generation_timestamp=datetime.now(),
            processing_time_seconds=processing_time,
            message="Insights generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Insight generation failed for file {request.file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Insight generation failed. Please try again."
        )

@router.get("/{file_id}/summary")
async def get_insight_summary(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get insight summary for a specific file."""
    try:
        insight_service = InsightService()
        
        # Verify file ownership (temporarily disabled for testing)
        # if not await insight_service.verify_file_ownership(file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        summary = await insight_service.get_insight_summary(file_id)
        
        logger.info(f"Insight summary retrieved for file {file_id}")
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get insight summary for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve insight summary"
        )

@router.get("/{file_id}/recommendations")
async def get_insight_recommendations(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get AI recommendations for a specific file."""
    try:
        insight_service = InsightService()
        
        # Verify file ownership (temporarily disabled for testing)
        # if not await insight_service.verify_file_ownership(file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        recommendations = await insight_service.get_recommendations(file_id)
        
        logger.info(f"Insight recommendations retrieved for file {file_id}")
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get insight recommendations for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve insight recommendations"
        )

@router.get("/{file_id}/quality-assessment")
async def get_data_quality_assessment(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get data quality assessment for a specific file."""
    try:
        insight_service = InsightService()
        
        # Verify file ownership (temporarily disabled for testing)
        # if not await insight_service.verify_file_ownership(file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        quality_assessment = await insight_service.get_data_quality_assessment(file_id)
        
        logger.info(f"Data quality assessment retrieved for file {file_id}")
        return quality_assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get data quality assessment for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve data quality assessment"
        ) 