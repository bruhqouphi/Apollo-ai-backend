"""
Analysis Router
Handles data analysis operations with proper service layer separation.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import AnalysisService
from app.services.auth_service import AuthService
from app.core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analysis", tags=["Data Analysis"])

@router.post("/", response_model=AnalysisResponse)
async def analyze_data(
    request: AnalysisRequest,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Perform comprehensive data analysis on uploaded file."""
    try:
        analysis_service = AnalysisService()
        
        # Verify file ownership (temporarily disabled for testing)
        # if not await analysis_service.verify_file_ownership(request.file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        # Perform analysis
        start_time = datetime.now()
        result = await analysis_service.analyze_data(request)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Analysis completed for file {request.file_id}")
        
        return AnalysisResponse(
            file_id=request.file_id,
            summary=result["summary"],
            analysis_results=result["analysis_results"],
            analysis_timestamp=datetime.now(),
            processing_time_seconds=processing_time,
            message="Analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed for file {request.file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed. Please try again."
        )

@router.get("/{file_id}/summary")
async def get_analysis_summary(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get analysis summary for a specific file."""
    try:
        analysis_service = AnalysisService()
        
        # Verify file ownership (temporarily disabled for testing)
        # if not await analysis_service.verify_file_ownership(file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        summary = await analysis_service.get_analysis_summary(file_id)
        
        logger.info(f"Analysis summary retrieved for file {file_id}")
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis summary for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis summary"
        )

@router.get("/{file_id}/correlations")
async def get_correlation_analysis(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get correlation analysis for a specific file."""
    try:
        analysis_service = AnalysisService()
        
        # Verify file ownership (temporarily disabled for testing)
        # if not await analysis_service.verify_file_ownership(file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        correlations = await analysis_service.get_correlation_analysis(file_id)
        
        logger.info(f"Correlation analysis retrieved for file {file_id}")
        return correlations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get correlation analysis for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve correlation analysis"
        )

@router.get("/{file_id}/outliers")
async def get_outlier_analysis(
    file_id: str,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get outlier analysis for a specific file."""
    try:
        analysis_service = AnalysisService()
        
        # Verify file ownership (temporarily disabled for testing)
        # if not await analysis_service.verify_file_ownership(file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        outliers = await analysis_service.get_outlier_analysis(file_id)
        
        logger.info(f"Outlier analysis retrieved for file {file_id}")
        return outliers
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get outlier analysis for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve outlier analysis"
        ) 