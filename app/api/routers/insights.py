"""
Insights Router
Handles AI-powered insights generation and report generation.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from typing import Optional

from app.models.schemas import InsightRequest, InsightResponse
from app.services.insight_service import InsightService
from app.core.security import get_current_user

# Import report generator with error handling
try:
    from app.core.report_generator import ReportGenerator, ReportConfig
    REPORT_GENERATOR_AVAILABLE = True
except (ImportError, OSError) as e:
    REPORT_GENERATOR_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Report generator not fully available: {e}")

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

@router.post("/{file_id}/generate-report")
async def generate_comprehensive_report(
    file_id: str,
    format: str = Query("html", description="Report format: 'html' or 'pdf'"),
    include_raw_data: bool = Query(False, description="Include raw data in the report"),
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Generate a comprehensive PDF/HTML report with analysis, insights, and visualizations."""
    
    # Check if report generator is available
    if not REPORT_GENERATOR_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Report generation is not available. Missing system dependencies."
        )
    
    try:
        from app.services.analysis_service import AnalysisService
        from app.services.visualization_service import VisualizationService
        from pathlib import Path
        import os
        
        # Initialize services
        insight_service = InsightService()
        analysis_service = AnalysisService()
        viz_service = VisualizationService()
        
        # Verify file ownership (temporarily disabled for testing)
        # if not await insight_service.verify_file_ownership(file_id, current_user.id):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied to this file"
        #     )
        
        # Get analysis results (mock structure for now - you'll need to adapt based on your actual data structure)
        try:
            # This would need to be adapted based on how you store and retrieve analysis results
            analysis_results = []  # You'll need to implement getting stored analysis results
            visualizations = []    # You'll need to implement getting stored visualizations
            insights = []          # You'll need to implement getting stored insights
            
            # For now, let's create a simple report with available data
            logger.info(f"Generating {format} report for file {file_id}")
            
        except Exception as e:
            logger.error(f"Error retrieving data for report generation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not retrieve data for report generation"
            )
        
        # Configure report generation
        config = ReportConfig(
            report_title=f"Data Analysis Report - File {file_id}",
            author="Apollo AI System",
            include_raw_data=include_raw_data
        )
        
        # Initialize report generator
        generator = ReportGenerator(config)
        
        # Create reports directory if it doesn't exist
        reports_dir = Path("./reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate report based on format
        if format.lower() == "pdf":
            filename = f"apollo_report_{file_id}_{timestamp}.pdf"
            output_path = reports_dir / filename
            
            try:
                generator.generate_pdf_report(
                    analysis_results=analysis_results,
                    visualizations=visualizations,
                    insights=insights,
                    output_path=str(output_path)
                )
            except ImportError as e:
                logger.error(f"PDF generation dependencies missing: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="PDF generation is not available. Missing dependencies."
                )
                
        elif format.lower() == "html":
            filename = f"apollo_report_{file_id}_{timestamp}.html"
            output_path = reports_dir / filename
            
            generator.generate_html_report(
                analysis_results=analysis_results,
                visualizations=visualizations,
                insights=insights,
                output_path=str(output_path)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Use 'html' or 'pdf'"
            )
        
        # Check if file was created successfully
        if not output_path.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Report generation failed"
            )
        
        logger.info(f"Report generated successfully: {filename}")
        
        # Return the file for download
        media_type = "application/pdf" if format.lower() == "pdf" else "text/html"
        
        return FileResponse(
            path=str(output_path),
            filename=filename,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation failed for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Report generation failed. Please try again."
        ) 