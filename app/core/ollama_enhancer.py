"""
Ollama Local LLM Enhancer
Provides natural language synthesis for insights using local Ollama models.
No external APIs, complete privacy, zero cost.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class OllamaEnhancer:
    """
    Local LLM enhancer using Ollama for natural language synthesis.
    Converts structured insights into compelling business narratives.
    """
    
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama enhancer.
        
        Args:
            model_name: Ollama model to use (default: llama3.1:8b)
            base_url: Ollama server URL
        """
        self.model_name = model_name
        self.base_url = base_url
        self.available = False
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Check if Ollama is available."""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                if any(self.model_name in model for model in available_models):
                    self.available = True
                    logger.info(f"Ollama available with model {self.model_name}")
                else:
                    logger.warning(f"Model {self.model_name} not found. Available models: {available_models}")
            else:
                logger.warning("Ollama server not responding")
        except Exception as e:
            logger.info(f"Ollama not available: {str(e)} - falling back to templates")
    
    async def enhance_executive_summary(self, structured_insights: Dict[str, Any]) -> str:
        """
        Enhance executive summary with natural language processing.
        
        Args:
            structured_insights: Structured insights from LocalInsightEngine
            
        Returns:
            Enhanced executive summary
        """
        if not self.available:
            return self._template_executive_summary(structured_insights)
        
        try:
            prompt = self._create_executive_prompt(structured_insights)
            response = await self._call_ollama(prompt, max_tokens=300)
            
            if response and len(response.strip()) > 50:
                return response.strip()
            else:
                return self._template_executive_summary(structured_insights)
                
        except Exception as e:
            logger.warning(f"Ollama enhancement failed: {str(e)}")
            return self._template_executive_summary(structured_insights)
    
    async def enhance_recommendations(self, recommendations: list, business_context: Dict[str, Any]) -> list:
        """
        Enhance recommendations with natural language and business context.
        
        Args:
            recommendations: List of structured recommendations
            business_context: Business context for enhancement
            
        Returns:
            Enhanced recommendations list
        """
        if not self.available or not recommendations:
            return recommendations
        
        enhanced_recs = []
        
        for rec in recommendations[:5]:  # Enhance top 5 recommendations
            try:
                prompt = self._create_recommendation_prompt(rec, business_context)
                enhanced_desc = await self._call_ollama(prompt, max_tokens=150)
                
                if enhanced_desc and len(enhanced_desc.strip()) > 20:
                    rec['enhanced_description'] = enhanced_desc.strip()
                    rec['enhancement_source'] = 'ollama'
                else:
                    rec['enhanced_description'] = rec.get('description', '')
                    rec['enhancement_source'] = 'template'
                
                enhanced_recs.append(rec)
                
            except Exception as e:
                logger.warning(f"Failed to enhance recommendation: {str(e)}")
                rec['enhanced_description'] = rec.get('description', '')
                rec['enhancement_source'] = 'fallback'
                enhanced_recs.append(rec)
        
        return enhanced_recs
    
    async def generate_business_narrative(self, insights: Dict[str, Any]) -> str:
        """
        Generate compelling business narrative from insights.
        
        Args:
            insights: Complete insights dictionary
            
        Returns:
            Business narrative string
        """
        if not self.available:
            return self._template_business_narrative(insights)
        
        try:
            prompt = self._create_narrative_prompt(insights)
            narrative = await self._call_ollama(prompt, max_tokens=400)
            
            if narrative and len(narrative.strip()) > 100:
                return narrative.strip()
            else:
                return self._template_business_narrative(insights)
                
        except Exception as e:
            logger.warning(f"Business narrative generation failed: {str(e)}")
            return self._template_business_narrative(insights)
    
    async def _call_ollama(self, prompt: str, max_tokens: int = 300) -> str:
        """
        Call Ollama API with the given prompt.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.3,  # Lower temperature for more focused business content
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '').strip()
                    else:
                        logger.warning(f"Ollama API returned status {response.status}")
                        return ""
                        
        except asyncio.TimeoutError:
            logger.warning("Ollama request timed out")
            return ""
        except Exception as e:
            logger.warning(f"Ollama API call failed: {str(e)}")
            return ""
    
    def _create_executive_prompt(self, insights: Dict[str, Any]) -> str:
        """Create executive summary enhancement prompt."""
        
        key_findings = insights.get('key_findings', [])
        business_insights = insights.get('business_insights', {})
        confidence = insights.get('confidence_metrics', {}).get('overall_confidence', 'medium')
        
        prompt = f"""You are a senior data analyst presenting to C-level executives. Transform this analysis into a compelling executive summary.

KEY FINDINGS:
{chr(10).join(['- ' + finding for finding in key_findings[:5]])}

BUSINESS CONTEXT:
Domain: {business_insights.get('detected_domain', 'general')}
Confidence Level: {confidence}

REQUIREMENTS:
- Write exactly 2-3 sentences
- Focus on business value and ROI potential
- Use confident, professional tone
- Include specific numbers when possible
- End with clear next steps

Executive Summary:"""
        
        return prompt
    
    def _create_recommendation_prompt(self, recommendation: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Create recommendation enhancement prompt."""
        
        prompt = f"""You are a business consultant. Enhance this recommendation with specific, actionable details.

RECOMMENDATION:
Title: {recommendation.get('title', '')}
Description: {recommendation.get('description', '')}
Priority: {recommendation.get('priority', 'medium')}
Category: {recommendation.get('category', '')}

BUSINESS CONTEXT:
{json.dumps(context, indent=2)[:300]}...

REQUIREMENTS:
- Write 1-2 sentences maximum
- Be specific and actionable
- Include business impact
- Professional consulting tone

Enhanced Description:"""
        
        return prompt
    
    def _create_narrative_prompt(self, insights: Dict[str, Any]) -> str:
        """Create business narrative prompt."""
        
        exec_summary = insights.get('executive_summary', '')
        key_findings = insights.get('key_findings', [])
        recommendations = insights.get('recommendations', [])
        
        prompt = f"""You are a data storytelling expert. Create a compelling business narrative from this analysis.

EXECUTIVE SUMMARY:
{exec_summary}

KEY FINDINGS:
{chr(10).join(['- ' + finding for finding in key_findings[:3]])}

TOP RECOMMENDATIONS:
{chr(10).join(['- ' + rec.get('title', '') for rec in recommendations[:3]])}

REQUIREMENTS:
- Write exactly 3 paragraphs
- Paragraph 1: Current situation and key insights
- Paragraph 2: Opportunities and potential impact
- Paragraph 3: Recommended actions and expected outcomes
- Professional, confident tone
- Focus on business value

Business Narrative:"""
        
        return prompt
    
    def _template_executive_summary(self, insights: Dict[str, Any]) -> str:
        """Fallback template-based executive summary."""
        
        key_findings = insights.get('key_findings', [])
        business_insights = insights.get('business_insights', {})
        
        summary_parts = []
        
        # Opening
        domain = business_insights.get('detected_domain', 'business')
        summary_parts.append(f"Comprehensive {domain} data analysis reveals")
        
        # Key insights
        if key_findings:
            summary_parts.append(f"{len(key_findings)} critical insights")
        
        # Business value
        confidence = insights.get('confidence_metrics', {}).get('overall_confidence', 'medium')
        if confidence == 'high':
            summary_parts.append("with high statistical confidence")
        
        # Opportunities
        opportunities = insights.get('optimization_opportunities', [])
        if opportunities:
            high_impact_opps = [opp for opp in opportunities if opp.get('potential_impact') == 'high']
            if high_impact_opps:
                summary_parts.append(f"Multiple high-impact optimization opportunities identified with potential for 15-30% performance improvement")
        
        # Call to action
        recommendations = insights.get('recommendations', [])
        if recommendations:
            high_priority = [rec for rec in recommendations if rec.get('priority') == 'high']
            summary_parts.append(f"Immediate action recommended on {len(high_priority)} high-priority initiatives")
        
        return ". ".join(summary_parts) + "."
    
    def _template_business_narrative(self, insights: Dict[str, Any]) -> str:
        """Fallback template-based business narrative."""
        
        exec_summary = insights.get('executive_summary', '')
        key_findings = insights.get('key_findings', [])
        recommendations = insights.get('recommendations', [])
        opportunities = insights.get('optimization_opportunities', [])
        
        narrative_parts = []
        
        # Paragraph 1: Current situation
        narrative_parts.append(f"Analysis of the current data landscape reveals {len(key_findings)} significant patterns requiring executive attention. {exec_summary}")
        
        # Paragraph 2: Opportunities
        if opportunities:
            high_impact_count = len([opp for opp in opportunities if opp.get('potential_impact') == 'high'])
            narrative_parts.append(f"The analysis identifies {high_impact_count} high-impact optimization opportunities with potential for substantial performance gains. These opportunities span operational efficiency, data quality improvements, and strategic initiatives that could drive 15-30% performance improvement across key metrics.")
        else:
            narrative_parts.append("The analysis reveals moderate optimization potential with several areas for strategic improvement and enhanced operational efficiency.")
        
        # Paragraph 3: Recommendations
        if recommendations:
            high_priority = len([rec for rec in recommendations if rec.get('priority') == 'high'])
            narrative_parts.append(f"Immediate implementation of {high_priority} high-priority recommendations is advised to capture identified value. These initiatives offer clear ROI potential with manageable implementation effort, positioning the organization for enhanced performance and competitive advantage.")
        else:
            narrative_parts.append("Strategic focus on data quality and process optimization will establish a foundation for future growth and enhanced analytical capabilities.")
        
        return " ".join(narrative_parts)

class TemplateEnhancer:
    """
    Fallback template-based enhancer when Ollama is not available.
    Provides professional business language without external dependencies.
    """
    
    def __init__(self):
        self.business_templates = {
            'high_impact': [
                "Critical strategic opportunity requiring immediate executive attention",
                "High-value initiative with potential for significant ROI",
                "Priority optimization with substantial business impact potential"
            ],
            'medium_impact': [
                "Important strategic consideration for operational improvement",
                "Valuable opportunity for enhanced efficiency and performance",
                "Meaningful improvement initiative with clear business benefits"
            ],
            'low_impact': [
                "Notable observation for future strategic planning",
                "Incremental improvement opportunity worth monitoring",
                "Baseline optimization for enhanced operational foundation"
            ]
        }
        
        self.executive_phrases = [
            "Analysis reveals",
            "Strategic assessment indicates",
            "Data-driven insights demonstrate",
            "Comprehensive evaluation shows",
            "Executive analysis confirms"
        ]
        
        self.action_phrases = [
            "Immediate implementation recommended",
            "Strategic initiative advised",
            "Priority action required",
            "Executive decision needed",
            "Operational enhancement suggested"
        ]
    
    def enhance_with_templates(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance insights using professional templates."""
        
        enhanced_insights = insights.copy()
        
        # Enhance executive summary
        if 'executive_summary' in enhanced_insights:
            enhanced_insights['executive_summary'] = self._enhance_executive_summary(
                enhanced_insights['executive_summary']
            )
        
        # Enhance recommendations
        if 'recommendations' in enhanced_insights:
            enhanced_insights['recommendations'] = self._enhance_recommendations(
                enhanced_insights['recommendations']
            )
        
        # Add professional metadata
        enhanced_insights['enhancement_metadata'] = {
            'enhancement_engine': 'template_based',
            'language_level': 'executive',
            'confidence': 'template_enhanced'
        }
        
        return enhanced_insights
    
    def _enhance_executive_summary(self, summary: str) -> str:
        """Enhance executive summary with professional language."""
        
        # Replace basic phrases with executive language
        enhanced = summary
        
        replacements = {
            'Analysis of': 'Strategic assessment of',
            'shows': 'demonstrates',
            'found': 'identified',
            'indicates': 'confirms',
            'suggests': 'recommends'
        }
        
        for old, new in replacements.items():
            enhanced = enhanced.replace(old, new)
        
        return enhanced
    
    def _enhance_recommendations(self, recommendations: list) -> list:
        """Enhance recommendations with professional descriptions."""
        
        enhanced_recs = []
        
        for rec in recommendations:
            enhanced_rec = rec.copy()
            
            # Enhance description based on impact level
            impact = rec.get('potential_impact', 'medium')
            templates = self.business_templates.get(f'{impact}_impact', self.business_templates['medium_impact'])
            
            # Use template if description is basic
            if len(rec.get('description', '')) < 50:
                enhanced_rec['enhanced_description'] = templates[0]
            else:
                enhanced_rec['enhanced_description'] = rec.get('description', '')
            
            enhanced_rec['enhancement_source'] = 'template'
            enhanced_recs.append(enhanced_rec)
        
        return enhanced_recs
