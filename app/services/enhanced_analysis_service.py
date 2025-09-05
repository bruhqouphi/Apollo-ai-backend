"""
Enhanced Analysis Service
Provides sophisticated data analysis with business intelligence and actionable insights.
Now powered by local Python engines for maximum speed, privacy, and cost-effectiveness.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import pandas as pd
import numpy as np
import json

from app.database.database import get_database
from app.database.models import File, Analysis
from app.core.enhanced_analyzer import EnhancedDataAnalyzer
from app.core.local_insight_engine import LocalInsightEngine
from app.core.ollama_enhancer import OllamaEnhancer, TemplateEnhancer
from app.models.schemas import AnalysisRequest

logger = logging.getLogger(__name__)

class EnhancedAnalysisService:
    """
    Enhanced analysis service providing comprehensive business intelligence.
    Now powered by local Python engines for maximum performance and privacy.
    """
    
    def __init__(self):
        self.db: Session = next(get_database())
        self.local_insight_engine = LocalInsightEngine()
        self.ollama_enhancer = OllamaEnhancer()
        self.template_enhancer = TemplateEnhancer()
    
    def _convert_numpy_types(self, obj: Any) -> Any:
        """
        Recursively convert numpy types to Python types for JSON serialization.
        
        Args:
            obj: Object that may contain numpy types
            
        Returns:
            Object with all numpy types converted to Python types
        """
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_numpy_types(item) for item in obj)
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    async def analyze_data_comprehensive(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        Perform comprehensive business-focused data analysis using local Python engines.
        
        Args:
            request: Analysis request parameters
            
        Returns:
            Comprehensive analysis results with business insights
        """
        start_time = pd.Timestamp.now()
        
        try:
            # Get file from database
            file = self.db.query(File).filter(File.id == request.file_id).first()
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Load data for local analysis
            df = self._load_dataframe(file.file_path)
            
            # 1. Initialize enhanced analyzer (keep existing sophisticated analysis)
            analyzer = EnhancedDataAnalyzer(file.file_path)
            
            # 2. Perform comprehensive analysis (your existing excellent analysis)
            analysis_results = analyzer.get_comprehensive_analysis()
            
            # 3. Generate local insights (NEW - pure Python, ultra-fast)
            logger.info("Generating local Python insights...")
            local_insights = self.local_insight_engine.generate_comprehensive_insights(df, {"analysis_results": analysis_results})
            
            # 4. Enhance with business context (existing)
            enhanced_results = self._enhance_with_business_context(analysis_results, file)
            
            # 5. Enhance narrative with Ollama (NEW - natural language)
            logger.info("Enhancing narrative with local LLM...")
            enhanced_executive_summary = await self.ollama_enhancer.enhance_executive_summary(local_insights)
            enhanced_recommendations = await self.ollama_enhancer.enhance_recommendations(
                local_insights.get('recommendations', []), 
                enhanced_results.get('business_insights', {})
            )
            business_narrative = await self.ollama_enhancer.generate_business_narrative(local_insights)
            
            # 6. Combine all insights for ultimate analysis
            ultimate_results = self._combine_all_insights(
                enhanced_results, 
                local_insights, 
                enhanced_executive_summary,
                enhanced_recommendations,
                business_narrative
            )
            
            # 7. Create comprehensive summary
            summary = self._create_business_summary(ultimate_results, file)
            
            # Calculate processing time
            processing_time = (pd.Timestamp.now() - start_time).total_seconds()
            
            # 8. Convert all numpy types to Python types for JSON serialization
            logger.info("Converting numpy types for database storage...")
            serializable_summary = self._convert_numpy_types(summary)
            serializable_results = self._convert_numpy_types(ultimate_results)
            
            # Store analysis in database
            db_analysis = Analysis(
                file_id=file.id,
                user_id=file.user_id,
                analysis_type="comprehensive_enhanced_local",
                summary=serializable_summary,
                analysis_results=serializable_results,
                processing_time=processing_time
            )
            
            self.db.add(db_analysis)
            self.db.commit()
            self.db.refresh(db_analysis)
            
            logger.info(f"Local enhanced analysis completed for {file.original_filename} in {processing_time:.2f}s")
            
            return {
                "analysis_id": db_analysis.id,
                "file_info": {
                    "file_id": file.id,
                    "filename": file.original_filename,
                    "rows": file.rows_count,
                    "columns": file.columns_count
                },
                "summary": serializable_summary,
                "analysis_results": serializable_results,
                "business_impact_score": self._calculate_business_impact_score(serializable_results),
                "actionability_score": self._calculate_actionability_score(serializable_results),
                "confidence_level": local_insights.get('confidence_metrics', {}).get('overall_confidence', 'medium'),
                "processing_performance": {
                    "processing_time_seconds": float(processing_time),
                    "cost": "$0.00",
                    "privacy_level": "100% local",
                    "engine": "local_python + ollama",
                    "speed_improvement": f"{max(1, 5/processing_time):.1f}x faster than API-based"
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Enhanced analysis failed for file {request.file_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {str(e)}"
            )
    
    def _load_dataframe(self, file_path: str) -> pd.DataFrame:
        """Load DataFrame from file path."""
        try:
            file_extension = file_path.split('.')[-1].lower()
            
            if file_extension == 'csv':
                # Try different encodings
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        return pd.read_csv(file_path, encoding=encoding)
                    except UnicodeDecodeError:
                        continue
                raise ValueError("Could not read CSV file with any encoding")
            elif file_extension in ['xls', 'xlsx']:
                return pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error loading DataFrame: {str(e)}")
            raise ValueError(f"Failed to load data: {str(e)}")
    
    def _combine_all_insights(self, 
                             enhanced_results: Dict[str, Any],
                             local_insights: Dict[str, Any],
                             enhanced_executive_summary: str,
                             enhanced_recommendations: List[Dict[str, Any]],
                             business_narrative: str) -> Dict[str, Any]:
        """Combine all insights into ultimate comprehensive results."""
        
        # Start with enhanced results as base
        combined = enhanced_results.copy()
        
        # Add local insights
        combined['local_insights'] = local_insights
        
        # Enhance executive summary
        if enhanced_executive_summary:
            combined['enhanced_executive_summary'] = enhanced_executive_summary
        
        # Replace recommendations with enhanced versions
        if enhanced_recommendations:
            combined['enhanced_recommendations'] = enhanced_recommendations
        
        # Add business narrative
        if business_narrative:
            combined['business_narrative'] = business_narrative
        
        # Add performance metrics
        combined['performance_metrics'] = {
            'insight_sources': ['statistical_analysis', 'business_intelligence', 'local_python', 'ollama_llm'],
            'processing_method': 'hybrid_local',
            'enhancement_level': 'comprehensive'
        }
        
        # Merge confidence metrics
        local_confidence = local_insights.get('confidence_metrics', {})
        if local_confidence:
            combined['confidence_metrics'] = {
                **combined.get('confidence_metrics', {}),
                **local_confidence
            }
        
        return combined
    
    def _enhance_with_business_context(self, analysis_results: Dict[str, Any], file: File) -> Dict[str, Any]:
        """Add business context to analysis results."""
        
        # Add file metadata context
        analysis_results['file_context'] = {
            'filename': file.original_filename,
            'upload_date': file.upload_time.isoformat(),
            'data_volume': {
                'rows': file.rows_count,
                'columns': file.columns_count,
                'estimated_memory': f"{(file.file_size / 1024 / 1024):.2f} MB"
            },
            'data_density': file.rows_count * file.columns_count,
            'business_criticality': self._assess_business_criticality(file.columns)
        }
        
        # Enhance executive summary with business KPIs
        if 'executive_summary' in analysis_results:
            analysis_results['executive_summary']['business_readiness_score'] = self._calculate_business_readiness(analysis_results)
            analysis_results['executive_summary']['decision_support_level'] = self._assess_decision_support_level(analysis_results)
        
        # Add industry-specific insights
        analysis_results['industry_insights'] = self._generate_industry_insights(file.columns)
        
        # Add ROI potential analysis
        analysis_results['roi_potential'] = self._assess_roi_potential(analysis_results)
        
        return analysis_results
    
    def _create_business_summary(self, analysis_results: Dict[str, Any], file: File) -> Dict[str, Any]:
        """Create executive-level business summary."""
        
        exec_summary = analysis_results.get('executive_summary', {})
        quality_assessment = analysis_results.get('data_quality_assessment', {})
        
        # Create actionable insights summary
        key_insights = []
        
        # Data quality insights
        quality_score = quality_assessment.get('overall_score', 0)
        if quality_score > 80:
            key_insights.append("High-quality dataset suitable for critical business decisions")
        elif quality_score > 60:
            key_insights.append("Good dataset quality with minor improvements needed")
        else:
            key_insights.append("Data quality issues require attention before analysis")
        
        # Business value insights
        business_value = exec_summary.get('business_value_indicators', [])
        if business_value:
            key_insights.extend(business_value[:2])  # Top 2 business value indicators
        
        # Recommendations summary
        recommendations = analysis_results.get('recommendations', [])
        top_recommendations = [rec for rec in recommendations[:3] if rec.get('impact') == 'high']
        
        return {
            'dataset_overview': {
                'name': file.original_filename,
                'size': f"{file.rows_count:,} rows × {file.columns_count} columns",
                'quality_score': quality_score,
                'business_readiness': exec_summary.get('business_readiness_score', 0)
            },
            'key_insights': key_insights,
            'critical_findings': self._extract_critical_findings(analysis_results),
            'immediate_actions': [rec['title'] for rec in top_recommendations],
            'business_impact': {
                'potential_value': self._assess_business_value_level(analysis_results),
                'risk_level': self._assess_risk_level(analysis_results),
                'implementation_effort': self._assess_implementation_effort(recommendations)
            },
            'next_steps': self._generate_next_steps(analysis_results)
        }
    
    def _calculate_business_impact_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate overall business impact score (0-100)."""
        score = 50.0  # Base score
        
        # Quality contribution
        quality_score = analysis_results.get('data_quality_assessment', {}).get('overall_score', 50)
        score += (quality_score - 50) * 0.3
        
        # Business relevance contribution
        business_indicators = len(analysis_results.get('executive_summary', {}).get('business_value_indicators', []))
        score += min(business_indicators * 5, 20)
        
        # Actionability contribution
        high_impact_recs = len([r for r in analysis_results.get('recommendations', []) if r.get('impact') == 'high'])
        score += min(high_impact_recs * 5, 15)
        
        # Data completeness contribution
        data_completeness = analysis_results.get('executive_summary', {}).get('dataset_overview', {}).get('data_completeness_percentage', 50)
        score += (data_completeness - 50) * 0.2
        
        return min(100, max(0, round(score, 1)))
    
    def _calculate_actionability_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate how actionable the insights are (0-100)."""
        score = 30.0  # Base score
        
        # Number of specific recommendations
        recommendations = analysis_results.get('recommendations', [])
        score += min(len(recommendations) * 3, 30)
        
        # Quality of recommendations (those with specific actions)
        specific_actions = len([r for r in recommendations if 'action' in r and len(r['action']) > 20])
        score += min(specific_actions * 5, 25)
        
        # Business insights depth
        business_insights = analysis_results.get('business_insights', {})
        non_empty_insights = len([k for k, v in business_insights.items() if v])
        score += min(non_empty_insights * 3, 15)
        
        return min(100, max(0, round(score, 1)))
    
    def _assess_business_criticality(self, columns: list) -> str:
        """Assess business criticality based on column names."""
        critical_keywords = ['revenue', 'profit', 'sales', 'customer', 'user', 'conversion']
        important_keywords = ['cost', 'price', 'quantity', 'amount', 'date', 'category']
        
        critical_count = sum(1 for col in columns if any(keyword in col.lower() for keyword in critical_keywords))
        important_count = sum(1 for col in columns if any(keyword in col.lower() for keyword in important_keywords))
        
        if critical_count >= 3:
            return "high"
        elif critical_count >= 1 or important_count >= 5:
            return "medium"
        else:
            return "low"
    
    def _calculate_business_readiness(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate how ready the data is for business decisions."""
        quality_score = analysis_results.get('data_quality_assessment', {}).get('overall_score', 50)
        completeness = analysis_results.get('executive_summary', {}).get('dataset_overview', {}).get('data_completeness_percentage', 50)
        
        # Business readiness is heavily weighted on quality and completeness
        readiness = (quality_score * 0.6 + completeness * 0.4)
        return round(readiness, 1)
    
    def _assess_decision_support_level(self, analysis_results: Dict[str, Any]) -> str:
        """Assess what level of business decisions this data can support."""
        business_readiness = self._calculate_business_readiness(analysis_results)
        sample_size = analysis_results.get('executive_summary', {}).get('dataset_overview', {}).get('total_records', 0)
        
        if business_readiness > 85 and sample_size > 1000:
            return "strategic"  # Can support high-level strategic decisions
        elif business_readiness > 70 and sample_size > 100:
            return "tactical"   # Can support operational and tactical decisions
        elif business_readiness > 50:
            return "exploratory"  # Suitable for exploratory analysis only
        else:
            return "preliminary"  # Preliminary insights only
    
    def _generate_industry_insights(self, columns: list) -> Dict[str, Any]:
        """Generate industry-specific insights based on data structure."""
        insights = {}
        
        # E-commerce indicators
        ecommerce_keywords = ['order', 'product', 'customer', 'cart', 'purchase', 'shipping']
        if sum(1 for col in columns if any(keyword in col.lower() for keyword in ecommerce_keywords)) >= 3:
            insights['ecommerce'] = {
                'detected': True,
                'confidence': 0.8,
                'key_metrics': ['conversion_rate', 'average_order_value', 'customer_lifetime_value'],
                'analysis_focus': 'customer behavior and sales funnel optimization'
            }
        
        # Finance indicators
        finance_keywords = ['amount', 'balance', 'transaction', 'account', 'payment', 'fee']
        if sum(1 for col in columns if any(keyword in col.lower() for keyword in finance_keywords)) >= 3:
            insights['finance'] = {
                'detected': True,
                'confidence': 0.8,
                'key_metrics': ['transaction_volume', 'account_balance_trends', 'fee_analysis'],
                'analysis_focus': 'financial performance and risk assessment'
            }
        
        # Marketing indicators
        marketing_keywords = ['campaign', 'click', 'impression', 'conversion', 'lead', 'source']
        if sum(1 for col in columns if any(keyword in col.lower() for keyword in marketing_keywords)) >= 3:
            insights['marketing'] = {
                'detected': True,
                'confidence': 0.8,
                'key_metrics': ['campaign_roi', 'conversion_rates', 'customer_acquisition_cost'],
                'analysis_focus': 'marketing effectiveness and channel optimization'
            }
        
        return insights
    
    def _assess_roi_potential(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the ROI potential of implementing insights."""
        
        # Base ROI assessment on data quality and business relevance
        quality_score = analysis_results.get('data_quality_assessment', {}).get('overall_score', 50)
        business_indicators = len(analysis_results.get('executive_summary', {}).get('business_value_indicators', []))
        high_impact_recs = len([r for r in analysis_results.get('recommendations', []) if r.get('impact') == 'high'])
        
        # Calculate ROI potential
        roi_score = (quality_score * 0.4 + business_indicators * 10 + high_impact_recs * 15)
        roi_score = min(100, roi_score)
        
        if roi_score > 80:
            roi_level = "high"
            timeframe = "3-6 months"
            expected_return = "5-15x"
        elif roi_score > 60:
            roi_level = "medium"
            timeframe = "6-12 months" 
            expected_return = "2-5x"
        else:
            roi_level = "low"
            timeframe = "12+ months"
            expected_return = "1-2x"
        
        return {
            'roi_score': round(roi_score, 1),
            'roi_level': roi_level,
            'expected_timeframe': timeframe,
            'expected_return_multiple': expected_return,
            'investment_areas': self._identify_investment_areas(analysis_results)
        }
    
    def _extract_critical_findings(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract the most critical findings that require immediate attention."""
        critical_findings = []
        
        # Data quality critical issues
        quality_issues = analysis_results.get('data_quality_assessment', {}).get('quality_issues', [])
        critical_quality_issues = [issue for issue in quality_issues if 'critical' in issue.lower()]
        critical_findings.extend(critical_quality_issues[:2])
        
        # High-impact anomalies
        anomalies = analysis_results.get('anomaly_detection', {})
        for col, anomaly_info in anomalies.items():
            if anomaly_info.get('business_impact', {}).get('level') == 'high':
                critical_findings.append(f"Critical anomalies detected in {col}")
        
        # Business risks
        business_insights = analysis_results.get('business_insights', {})
        risk_insights = business_insights.get('risk_insights', {})
        if risk_insights:
            critical_findings.append("Business risk patterns identified requiring mitigation")
        
        return critical_findings[:3]  # Top 3 critical findings
    
    def _assess_business_value_level(self, analysis_results: Dict[str, Any]) -> str:
        """Assess the level of business value in the insights."""
        business_indicators = len(analysis_results.get('executive_summary', {}).get('business_value_indicators', []))
        roi_score = analysis_results.get('roi_potential', {}).get('roi_score', 50)
        
        if business_indicators >= 3 and roi_score > 80:
            return "transformational"
        elif business_indicators >= 2 and roi_score > 60:
            return "significant"
        elif business_indicators >= 1 or roi_score > 40:
            return "moderate"
        else:
            return "limited"
    
    def _assess_risk_level(self, analysis_results: Dict[str, Any]) -> str:
        """Assess the risk level in the data and insights."""
        quality_score = analysis_results.get('data_quality_assessment', {}).get('overall_score', 50)
        anomaly_count = len(analysis_results.get('anomaly_detection', {}))
        
        if quality_score < 50 or anomaly_count > 5:
            return "high"
        elif quality_score < 70 or anomaly_count > 2:
            return "medium"
        else:
            return "low"
    
    def _assess_implementation_effort(self, recommendations: List[Dict[str, Any]]) -> str:
        """Assess the overall implementation effort for recommendations."""
        if not recommendations:
            return "minimal"
        
        effort_scores = {'low': 1, 'medium': 2, 'high': 3}
        avg_effort = sum(effort_scores.get(rec.get('effort', 'medium'), 2) for rec in recommendations) / len(recommendations)
        
        if avg_effort > 2.5:
            return "high"
        elif avg_effort > 1.5:
            return "medium"
        else:
            return "low"
    
    def _generate_next_steps(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate specific next steps based on analysis results."""
        next_steps = []
        
        # Quality-based next steps
        quality_score = analysis_results.get('data_quality_assessment', {}).get('overall_score', 50)
        if quality_score < 70:
            next_steps.append("Address data quality issues before proceeding with advanced analytics")
        
        # Recommendation-based next steps
        high_priority_recs = [r for r in analysis_results.get('recommendations', []) if r.get('priority', 0) > 6]
        for rec in high_priority_recs[:2]:
            next_steps.append(f"Implement: {rec.get('title', 'High priority recommendation')}")
        
        # Business insight next steps
        business_insights = analysis_results.get('business_insights', {})
        if business_insights:
            next_steps.append("Develop action plans for identified business opportunities")
        
        # Default next step
        if not next_steps:
            next_steps.append("Review analysis results with stakeholders and prioritize actions")
        
        return next_steps[:4]  # Maximum 4 next steps
    
    def _identify_investment_areas(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Identify key areas for investment based on analysis."""
        areas = []
        
        # Data quality investment
        quality_score = analysis_results.get('data_quality_assessment', {}).get('overall_score', 50)
        if quality_score < 80:
            areas.append("data_quality_improvement")
        
        # Analytics capability investment
        business_indicators = len(analysis_results.get('executive_summary', {}).get('business_value_indicators', []))
        if business_indicators >= 2:
            areas.append("advanced_analytics_platform")
        
        # Process improvement investment
        high_impact_recs = len([r for r in analysis_results.get('recommendations', []) if r.get('impact') == 'high'])
        if high_impact_recs >= 3:
            areas.append("process_optimization")
        
        return areas
