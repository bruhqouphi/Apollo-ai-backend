"""
Enhanced Analysis Router
Provides comprehensive business intelligence and advanced data analysis.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import AnalysisRequest
from app.services.enhanced_analysis_service import EnhancedAnalysisService
from app.services.auth_service import AuthService
from app.core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/enhanced-analysis", tags=["Enhanced Data Analysis"])

@router.post("/comprehensive")
async def analyze_data_comprehensive(
    request: AnalysisRequest,
    # current_user = Depends(get_current_user)  # Temporarily disabled for testing
):
    """
    Perform comprehensive business-focused data analysis with advanced insights.
    
    This endpoint provides:
    - Executive summary with business KPIs
    - Advanced statistical analysis with business interpretation
    - Predictive insights and trend analysis
    - Comprehensive anomaly detection
    - Actionable recommendations with priority scoring
    - Business impact and ROI assessment
    - Industry-specific insights
    - Data story and narrative
    """
    try:
        analysis_service = EnhancedAnalysisService()
        
        # Perform comprehensive analysis
        start_time = datetime.now()
        result = await analysis_service.analyze_data_comprehensive(request)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Enhanced analysis completed for file {request.file_id}")
        
        # Return comprehensive response
        return {
            "success": True,
            "file_id": request.file_id,
            "analysis_type": "comprehensive_enhanced",
            "processing_time_seconds": processing_time,
            "analysis_timestamp": datetime.now().isoformat(),
            **result,
            "message": "Comprehensive business analysis completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced analysis failed for file {request.file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced analysis failed: {str(e)}"
        )

@router.post("/business-insights")
async def generate_business_insights(
    request: AnalysisRequest,
    # current_user = Depends(get_current_user)
):
    """
    Generate focused business insights and recommendations.
    
    Provides:
    - Executive summary
    - Key business metrics
    - Strategic recommendations
    - ROI assessment
    - Implementation roadmap
    """
    try:
        analysis_service = EnhancedAnalysisService()
        
        # Get comprehensive analysis
        full_analysis = await analysis_service.analyze_data_comprehensive(request)
        
        # Extract business-focused insights
        business_summary = {
            "executive_summary": full_analysis["analysis_results"].get("executive_summary", {}),
            "business_insights": full_analysis["analysis_results"].get("business_insights", {}),
            "recommendations": full_analysis["analysis_results"].get("recommendations", [])[:5],
            "roi_potential": full_analysis["analysis_results"].get("roi_potential", {}),
            "industry_insights": full_analysis["analysis_results"].get("industry_insights", {}),
            "business_impact_score": full_analysis.get("business_impact_score", 0),
            "next_steps": full_analysis["summary"].get("next_steps", [])
        }
        
        return {
            "success": True,
            "file_id": request.file_id,
            "analysis_type": "business_insights",
            "timestamp": datetime.now().isoformat(),
            "insights": business_summary,
            "message": "Business insights generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Business insights generation failed for file {request.file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business insights generation failed: {str(e)}"
        )

@router.post("/data-quality-assessment")
async def assess_data_quality(
    request: AnalysisRequest,
    # current_user = Depends(get_current_user)
):
    """
    Perform comprehensive data quality assessment.
    
    Provides:
    - Overall quality score
    - Missing value analysis
    - Data consistency checks
    - Outlier detection
    - Improvement recommendations
    """
    try:
        analysis_service = EnhancedAnalysisService()
        
        # Get comprehensive analysis
        full_analysis = await analysis_service.analyze_data_comprehensive(request)
        
        # Extract quality assessment
        quality_assessment = {
            "data_quality": full_analysis["analysis_results"].get("data_quality_assessment", {}),
            "confidence_metrics": full_analysis["analysis_results"].get("confidence_metrics", {}),
            "quality_recommendations": [
                rec for rec in full_analysis["analysis_results"].get("recommendations", [])
                if rec.get("type") == "data_quality"
            ],
            "business_readiness": full_analysis["analysis_results"]["executive_summary"].get("business_readiness_score", 0)
        }
        
        return {
            "success": True,
            "file_id": request.file_id,
            "analysis_type": "data_quality_assessment",
            "timestamp": datetime.now().isoformat(),
            "assessment": quality_assessment,
            "message": "Data quality assessment completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data quality assessment failed for file {request.file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data quality assessment failed: {str(e)}"
        )

@router.post("/predictive-insights")
async def generate_predictive_insights(
    request: AnalysisRequest,
    # current_user = Depends(get_current_user)
):
    """
    Generate predictive insights and forecasts.
    
    Provides:
    - Trend analysis
    - Clustering insights
    - Anomaly detection
    - Predictive patterns
    - Future recommendations
    """
    try:
        analysis_service = EnhancedAnalysisService()
        
        # Get comprehensive analysis
        full_analysis = await analysis_service.analyze_data_comprehensive(request)
        
        # Extract predictive insights
        predictive_summary = {
            "predictive_insights": full_analysis["analysis_results"].get("predictive_insights", {}),
            "anomaly_detection": full_analysis["analysis_results"].get("anomaly_detection", {}),
            "statistical_analysis": full_analysis["analysis_results"].get("statistical_analysis", {}),
            "trend_recommendations": [
                rec for rec in full_analysis["analysis_results"].get("recommendations", [])
                if "trend" in rec.get("category", "").lower() or "predict" in rec.get("category", "").lower()
            ]
        }
        
        return {
            "success": True,
            "file_id": request.file_id,
            "analysis_type": "predictive_insights",
            "timestamp": datetime.now().isoformat(),
            "insights": predictive_summary,
            "message": "Predictive insights generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Predictive insights generation failed for file {request.file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Predictive insights generation failed: {str(e)}"
        )
