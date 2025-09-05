"""
Insight Service
Handles AI-powered insights generation with database storage.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.database.database import get_database
from app.database.models import File, Insight, User
from app.core.local_insight_engine import LocalInsightEngine
from app.core.ollama_enhancer import OllamaEnhancer, TemplateEnhancer
from app.models.schemas import InsightRequest

logger = logging.getLogger(__name__)

class InsightService:
    """Service for handling AI insights operations."""
    
    def __init__(self):
        self.db: Session = next(get_database())
        self.local_insight_engine = LocalInsightEngine()
        self.ollama_enhancer = OllamaEnhancer()
        self.template_enhancer = TemplateEnhancer()
    
    async def generate_insights(self, request: InsightRequest) -> Dict[str, Any]:
        """Generate AI-powered insights for uploaded data."""
        try:
            # Get file from database
            file = self.db.query(File).filter(File.id == request.file_id).first()
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Load the data for analysis
            import pandas as pd
            df = pd.read_csv(file.file_path)
            
            # Get analysis results first (we need this for insights)
            from app.services.analysis_service import AnalysisService
            from app.models.schemas import AnalysisRequest
            analysis_service = AnalysisService()
            analysis_request = AnalysisRequest(
                file_id=request.file_id,
                include_correlation=True,
                include_outliers=True,
                include_statistical_tests=True,
                outlier_method="iqr",
                confidence_level=0.95
            )
            
            logger.info("Running analysis for insight generation...")
            analysis_result = await analysis_service.analyze_data(analysis_request)
            logger.info("Analysis completed successfully")
            
            # Generate insights using local engines
            logger.info("Starting local insight generation...")
            insights_result = self.local_insight_engine.generate_comprehensive_insights(df)
            logger.info("Local insights generated successfully")
            
            # Enhance with local LLM narrative
            try:
                enhanced_summary = await self.ollama_enhancer.enhance_executive_summary(insights_result.get('executive_summary', {}))
                enhanced_recommendations = await self.ollama_enhancer.enhance_recommendations(insights_result.get('recommendations', []))
                
                insights_result['enhanced_executive_summary'] = enhanced_summary
                insights_result['enhanced_recommendations'] = enhanced_recommendations
            except Exception as e:
                logger.warning(f"LLM enhancement failed, using template: {e}")
                # Fallback to template enhancer
                enhanced_summary = self.template_enhancer.enhance_executive_summary(insights_result.get('executive_summary', {}))
                enhanced_recommendations = self.template_enhancer.enhance_recommendations(insights_result.get('recommendations', []))
                
                insights_result['enhanced_executive_summary'] = enhanced_summary
                insights_result['enhanced_recommendations'] = enhanced_recommendations
            
            logger.info("Insights enhancement completed")
            
            # Convert datetime objects to strings for JSON serialization
            def convert_datetime_to_string(obj):
                if isinstance(obj, dict):
                    return {k: convert_datetime_to_string(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime_to_string(item) for item in obj]
                elif hasattr(obj, 'isoformat'):  # datetime objects
                    return obj.isoformat()
                else:
                    return obj
            
            # Clean the insights result for database storage
            clean_insights_result = convert_datetime_to_string(insights_result)
            
            # Store insights in database
            db_insight = Insight(
                file_id=file.id,
                user_id=file.user_id,
                llm_provider=request.llm_provider,
                insights_data=clean_insights_result,
                processing_time=insights_result.get("processing_time", 0)
            )
            
            self.db.add(db_insight)
            self.db.commit()
            self.db.refresh(db_insight)
            
            logger.info(f"Insights generated for file {file.original_filename} using {request.llm_provider}")
            
            return {
                "insights": insights_result
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Insight generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Insight generation failed"
            )
    
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
    
    async def get_insight_summary(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get insight summary for a file."""
        try:
            insight = self.db.query(Insight).filter(
                Insight.file_id == file_id
            ).order_by(Insight.created_at.desc()).first()
            
            if not insight:
                return None
            
            insights_data = insight.insights_data
            
            return {
                "executive_summary": insights_data.get("executive_summary", ""),
                "key_findings": insights_data.get("key_findings", []),
                "confidence_level": insights_data.get("confidence_level", ""),
                "llm_provider": insight.llm_provider,
                "created_at": insight.created_at,
                "processing_time": insight.processing_time
            }
            
        except Exception as e:
            logger.error(f"Failed to get insight summary: {str(e)}")
            return None
    
    async def get_recommendations(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get AI recommendations for a file."""
        try:
            insight = self.db.query(Insight).filter(
                Insight.file_id == file_id
            ).order_by(Insight.created_at.desc()).first()
            
            if not insight:
                return None
            
            insights_data = insight.insights_data
            
            return {
                "recommendations": insights_data.get("recommendations", []),
                "next_steps": insights_data.get("next_steps", []),
                "data_quality_assessment": insights_data.get("data_quality_assessment", ""),
                "statistical_significance": insights_data.get("statistical_significance", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {str(e)}")
            return None
    
    async def get_data_quality_assessment(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get data quality assessment for a file."""
        try:
            insight = self.db.query(Insight).filter(
                Insight.file_id == file_id
            ).order_by(Insight.created_at.desc()).first()
            
            if not insight:
                return None
            
            insights_data = insight.insights_data
            
            return {
                "data_quality_assessment": insights_data.get("data_quality_assessment", ""),
                "statistical_significance": insights_data.get("statistical_significance", {}),
                "detailed_insights": insights_data.get("detailed_insights", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get data quality assessment: {str(e)}")
            return None
    
    async def get_user_insights(self, user_id: str) -> list:
        """Get all insights for a user."""
        try:
            insights = self.db.query(Insight).filter(
                Insight.user_id == user_id
            ).order_by(Insight.created_at.desc()).all()
            
            return [
                {
                    "id": insight.id,
                    "file_id": insight.file_id,
                    "llm_provider": insight.llm_provider,
                    "created_at": insight.created_at,
                    "processing_time": insight.processing_time
                }
                for insight in insights
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user insights: {str(e)}")
            return [] 