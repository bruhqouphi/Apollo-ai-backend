"""
Analysis Service
Handles data analysis operations with database storage.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import pandas as pd

from app.database.database import get_database
from app.database.models import File, Analysis, User
from app.core.analyzer import DataAnalyzer
from app.models.schemas import AnalysisRequest, DatasetSummary, ColumnStats

logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for handling data analysis operations."""
    
    def __init__(self):
        self.db: Session = next(get_database())
    
    async def analyze_data(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Perform comprehensive data analysis."""
        try:
            # Get file from database
            file = self.db.query(File).filter(File.id == request.file_id).first()
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Perform analysis using existing analyzer
            analyzer = DataAnalyzer(file.file_path)
            analysis_result = analyzer.analyze(
                include_correlation=request.include_correlation,
                include_outliers=request.include_outliers,
                include_statistical_tests=request.include_statistical_tests,
                outlier_method=request.outlier_method,
                confidence_level=request.confidence_level,
                target_columns=request.target_columns
            )
            
            # Store analysis result in database
            db_analysis = Analysis(
                file_id=file.id,
                user_id=file.user_id,
                analysis_type="comprehensive",
                summary=analysis_result["basic_info"],  # Use basic_info as summary
                analysis_results=analysis_result,
                processing_time=analysis_result.get("processing_time", 0)
            )
            
            self.db.add(db_analysis)
            self.db.commit()
            self.db.refresh(db_analysis)
            
            logger.info(f"Analysis completed for file {file.original_filename}")
            
            # Create DatasetSummary from analysis results
            columns_stats = []
            for col_info in analysis_result.get("columns_info", []):
                column_stat = ColumnStats(
                    name=col_info["name"],
                    dtype=col_info["dtype"],
                    count=col_info["non_null"],
                    missing=col_info["nulls"],
                    unique=col_info["unique"]
                )
                columns_stats.append(column_stat)
            
            summary = DatasetSummary(
                rows=analysis_result["basic_info"]["rows"],
                cols=analysis_result["basic_info"]["columns"],
                columns=columns_stats
            )
            
            return {
                "summary": summary,
                "analysis_results": analysis_result
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Analysis failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analysis failed"
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
    
    async def get_analysis_summary(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis summary for a file."""
        try:
            analysis = self.db.query(Analysis).filter(
                Analysis.file_id == file_id
            ).order_by(Analysis.created_at.desc()).first()
            
            if not analysis:
                return None
            
            return {
                "summary": analysis.summary,
                "analysis_type": analysis.analysis_type,
                "created_at": analysis.created_at,
                "processing_time": analysis.processing_time
            }
            
        except Exception as e:
            logger.error(f"Failed to get analysis summary: {str(e)}")
            return None
    
    async def get_correlation_analysis(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get correlation analysis for a file."""
        try:
            analysis = self.db.query(Analysis).filter(
                Analysis.file_id == file_id
            ).order_by(Analysis.created_at.desc()).first()
            
            if not analysis:
                return None
            
            analysis_results = analysis.analysis_results
            if "correlation_analysis" in analysis_results:
                return analysis_results["correlation_analysis"]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get correlation analysis: {str(e)}")
            return None
    
    async def get_outlier_analysis(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get outlier analysis for a file."""
        try:
            analysis = self.db.query(Analysis).filter(
                Analysis.file_id == file_id
            ).order_by(Analysis.created_at.desc()).first()
            
            if not analysis:
                return None
            
            analysis_results = analysis.analysis_results
            if "outlier_analysis" in analysis_results:
                return analysis_results["outlier_analysis"]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get outlier analysis: {str(e)}")
            return None
    
    async def get_user_analyses(self, user_id: str) -> list:
        """Get all analyses for a user."""
        try:
            analyses = self.db.query(Analysis).filter(
                Analysis.user_id == user_id
            ).order_by(Analysis.created_at.desc()).all()
            
            return [
                {
                    "id": analysis.id,
                    "file_id": analysis.file_id,
                    "analysis_type": analysis.analysis_type,
                    "created_at": analysis.created_at,
                    "processing_time": analysis.processing_time
                }
                for analysis in analyses
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user analyses: {str(e)}")
            return [] 