"""
Apollo AI - Professional Report Generation Module
Generates PDF and HTML reports with embedded visualizations and AI insights
"""

import base64
import io
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import json

# PDF Generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
        PageBreak, KeepTogether
    )
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# HTML to PDF conversion
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    # OSError can occur on Windows when system libraries are missing
    WEASYPRINT_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"WeasyPrint not available: {e}")

from app.models.schemas import AnalysisResult, VisualizationResult, InsightResult


@dataclass
class ReportConfig:
    """Configuration for report generation"""
    company_name: str = "Apollo AI Analytics"
    company_logo: Optional[str] = None  # Path to logo file
    report_title: str = "Data Analysis Report"
    author: str = "Apollo AI System"
    include_raw_data: bool = False
    chart_format: str = "png"  # png, svg, jpg
    theme_color: str = "#2E86AB"  # Primary brand color
    font_family: str = "Helvetica"


class ReportGenerator:
    """Professional report generator for Apollo AI analytics results"""
    
    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self.timestamp = datetime.now()
        
    def generate_pdf_report(
        self,
        analysis_results: List[AnalysisResult],
        visualizations: List[VisualizationResult],
        insights: List[InsightResult],
        output_path: str,
        **kwargs
    ) -> str:
        """Generate PDF report using ReportLab"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build report content
        story = []
        styles = self._get_pdf_styles()
        
        # Title page
        story.extend(self._build_pdf_title_page(styles))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._build_executive_summary(insights, styles))
        story.append(PageBreak())
        
        # Data Overview
        story.extend(self._build_data_overview(analysis_results, styles))
        
        # Statistical Analysis
        story.extend(self._build_statistical_analysis(analysis_results, styles))
        
        # Visualizations
        story.extend(self._build_visualizations_section(visualizations, styles))
        
        # AI Insights
        story.extend(self._build_insights_section(insights, styles))
        
        # Conclusions
        story.extend(self._build_conclusions(analysis_results, insights, styles))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def generate_html_report(
        self,
        analysis_results: List[AnalysisResult],
        visualizations: List[VisualizationResult],
        insights: List[InsightResult],
        output_path: str,
        **kwargs
    ) -> str:
        """Generate HTML report with embedded charts and styling"""
        
        html_content = self._build_html_report(
            analysis_results, visualizations, insights
        )
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def generate_pdf_from_html(
        self,
        html_content: str,
        output_path: str
    ) -> str:
        """Convert HTML report to PDF using WeasyPrint"""
        if not WEASYPRINT_AVAILABLE:
            raise ImportError("WeasyPrint is required for HTML to PDF conversion. Install with: pip install weasyprint")
        
        weasyprint.HTML(string=html_content).write_pdf(output_path)
        return output_path
    
    def _get_pdf_styles(self):
        """Get ReportLab styles for PDF generation"""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor(self.config.theme_color)
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor(self.config.theme_color),
            borderWidth=1,
            borderColor=colors.HexColor(self.config.theme_color),
            borderPadding=5
        ))
        
        styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.black
        ))
        
        return styles
    
    def _build_pdf_title_page(self, styles):
        """Build PDF title page"""
        story = []
        
        # Logo if available
        if self.config.company_logo and os.path.exists(self.config.company_logo):
            try:
                logo = Image(self.config.company_logo, width=2*inch, height=1*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 20))
            except:
                pass  # Skip logo if error
        
        # Company name
        story.append(Paragraph(self.config.company_name, styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Report title
        story.append(Paragraph(self.config.report_title, styles['Heading1']))
        story.append(Spacer(1, 30))
        
        # Report details
        details = [
            f"Generated by: {self.config.author}",
            f"Date: {self.timestamp.strftime('%B %d, %Y')}",
            f"Time: {self.timestamp.strftime('%I:%M %p')}"
        ]
        
        for detail in details:
            story.append(Paragraph(detail, styles['Normal']))
            story.append(Spacer(1, 12))
        
        return story
    
    def _build_executive_summary(self, insights: List[InsightResult], styles):
        """Build executive summary section"""
        story = []
        story.append(Paragraph("Executive Summary", styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Key insights summary
        key_insights = [insight for insight in insights if insight.confidence > 0.8][:3]
        
        if key_insights:
            summary_text = "This report presents a comprehensive analysis of the provided dataset. "
            summary_text += f"Key findings include {len(key_insights)} high-confidence insights "
            summary_text += "that provide actionable intelligence for decision-making."
            
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Top insights
            story.append(Paragraph("Key Findings:", styles['CustomSubheading']))
            
            for i, insight in enumerate(key_insights, 1):
                insight_text = f"{i}. {insight.insight} (Confidence: {insight.confidence:.1%})"
                story.append(Paragraph(insight_text, styles['Normal']))
                story.append(Spacer(1, 8))
        
        return story
    
    def _build_data_overview(self, analysis_results: List[AnalysisResult], styles):
        """Build data overview section"""
        story = []
        story.append(Paragraph("Data Overview", styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        if analysis_results:
            # Dataset summary
            total_records = sum(len(result.data) for result in analysis_results if hasattr(result, 'data'))
            columns_analyzed = len(analysis_results)
            
            overview_text = f"This analysis covers {columns_analyzed} data dimensions "
            if total_records > 0:
                overview_text += f"across {total_records} records. "
            
            overview_text += "The following sections provide detailed statistical analysis and insights."
            
            story.append(Paragraph(overview_text, styles['Normal']))
            story.append(Spacer(1, 12))
        
        return story
    
    def _build_statistical_analysis(self, analysis_results: List[AnalysisResult], styles):
        """Build statistical analysis section"""
        story = []
        story.append(Paragraph("Statistical Analysis", styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        for result in analysis_results:
            # Column analysis
            story.append(Paragraph(f"Analysis: {result.column_name}", styles['CustomSubheading']))
            
            # Statistics table
            if hasattr(result, 'statistics') and result.statistics:
                table_data = [['Metric', 'Value']]
                
                for key, value in result.statistics.items():
                    if isinstance(value, (int, float)):
                        formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
                    else:
                        formatted_value = str(value)
                    table_data.append([key.replace('_', ' ').title(), formatted_value])
                
                table = Table(table_data, colWidths=[2*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.config.theme_color)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 12))
        
        return story
    
    def _build_visualizations_section(self, visualizations: List[VisualizationResult], styles):
        """Build visualizations section"""
        story = []
        story.append(Paragraph("Data Visualizations", styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        for viz in visualizations:
            # Chart title
            story.append(Paragraph(viz.title or "Chart", styles['CustomSubheading']))
            
            # Embed chart
            if viz.chart_data:
                try:
                    # Convert base64 to image
                    if viz.chart_data.startswith('data:image'):
                        # Remove data URL prefix
                        image_data = viz.chart_data.split(',')[1]
                        image_bytes = base64.b64decode(image_data)
                        
                        # Create image from bytes
                        img = Image(io.BytesIO(image_bytes))
                        img.drawHeight = 4*inch
                        img.drawWidth = 6*inch
                        img.hAlign = 'CENTER'
                        
                        story.append(img)
                    elif os.path.exists(viz.chart_data):
                        # File path
                        img = Image(viz.chart_data, width=6*inch, height=4*inch)
                        img.hAlign = 'CENTER'
                        story.append(img)
                        
                except Exception as e:
                    # Fallback text if image fails
                    story.append(Paragraph(f"[Chart: {viz.chart_type}]", styles['Normal']))
            
            story.append(Spacer(1, 12))
        
        return story
    
    def _build_insights_section(self, insights: List[InsightResult], styles):
        """Build AI insights section"""
        story = []
        story.append(Paragraph("AI-Generated Insights", styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Group insights by confidence
        high_conf = [i for i in insights if i.confidence > 0.8]
        med_conf = [i for i in insights if 0.6 <= i.confidence <= 0.8]
        low_conf = [i for i in insights if i.confidence < 0.6]
        
        for category, insight_list, title in [
            (high_conf, "High Confidence Insights", "CustomSubheading"),
            (med_conf, "Medium Confidence Insights", "CustomSubheading"),
            (low_conf, "Additional Observations", "CustomSubheading")
        ]:
            if category:
                story.append(Paragraph(title, styles['CustomSubheading']))
                
                for insight in category:
                    bullet_text = f"• {insight.insight} (Confidence: {insight.confidence:.1%})"
                    if hasattr(insight, 'recommendation') and insight.recommendation:
                        bullet_text += f"<br/>   <i>Recommendation: {insight.recommendation}</i>"
                    
                    story.append(Paragraph(bullet_text, styles['Normal']))
                    story.append(Spacer(1, 8))
                
                story.append(Spacer(1, 12))
        
        return story
    
    def _build_conclusions(self, analysis_results: List[AnalysisResult], insights: List[InsightResult], styles):
        """Build conclusions section"""
        story = []
        story.append(Paragraph("Conclusions & Recommendations", styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Summary conclusions
        conclusions_text = "Based on the comprehensive analysis performed, several key patterns and trends have been identified. "
        conclusions_text += "The statistical analysis reveals important characteristics of the dataset, while AI-generated insights "
        conclusions_text += "provide actionable recommendations for data-driven decision making."
        
        story.append(Paragraph(conclusions_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Next steps
        story.append(Paragraph("Recommended Next Steps:", styles['CustomSubheading']))
        next_steps = [
            "Review high-confidence insights for immediate action items",
            "Validate findings with domain experts and stakeholders",
            "Implement recommended changes based on analysis results",
            "Monitor key metrics to measure impact of implemented changes",
            "Schedule regular analysis updates to track trends over time"
        ]
        
        for step in next_steps:
            story.append(Paragraph(f"• {step}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        return story
    
    def _build_html_report(
        self,
        analysis_results: List[AnalysisResult],
        visualizations: List[VisualizationResult],
        insights: List[InsightResult]
    ) -> str:
        """Build complete HTML report"""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.report_title}</title>
    <style>
        {self._get_html_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._build_html_header()}
        {self._build_html_executive_summary(insights)}
        {self._build_html_data_overview(analysis_results)}
        {self._build_html_statistical_analysis(analysis_results)}
        {self._build_html_visualizations(visualizations)}
        {self._build_html_insights(insights)}
        {self._build_html_conclusions()}
        {self._build_html_footer()}
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML report"""
        return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, {self.config.theme_color}, #1a5f7a);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .section {{
            padding: 30px 40px;
            border-bottom: 1px solid #eee;
        }}
        
        .section:last-child {{
            border-bottom: none;
        }}
        
        .section h2 {{
            color: {self.config.theme_color};
            font-size: 1.8em;
            margin-bottom: 20px;
            border-bottom: 2px solid {self.config.theme_color};
            padding-bottom: 10px;
        }}
        
        .section h3 {{
            color: #444;
            font-size: 1.3em;
            margin: 20px 0 10px 0;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid {self.config.theme_color};
        }}
        
        .stat-card h4 {{
            color: {self.config.theme_color};
            margin-bottom: 10px;
        }}
        
        .insight-item {{
            background: #f0f7ff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
            border-left: 4px solid {self.config.theme_color};
        }}
        
        .confidence {{
            font-weight: bold;
            color: {self.config.theme_color};
        }}
        
        .chart-container {{
            text-align: center;
            margin: 20px 0;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .timestamp {{
            color: #999;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
        """
    
    def _build_html_header(self) -> str:
        """Build HTML header section"""
        return f"""
        <div class="header">
            <h1>{self.config.company_name}</h1>
            <div class="subtitle">{self.config.report_title}</div>
            <div class="timestamp">Generated on {self.timestamp.strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        """
    
    def _build_html_executive_summary(self, insights: List[InsightResult]) -> str:
        """Build HTML executive summary"""
        key_insights = [i for i in insights if i.confidence > 0.8][:3]
        
        summary_html = """
        <div class="section">
            <h2>Executive Summary</h2>
            <p>This report presents a comprehensive analysis of the provided dataset with actionable insights for decision-making.</p>
        """
        
        if key_insights:
            summary_html += "<h3>Key Findings</h3>"
            for i, insight in enumerate(key_insights, 1):
                summary_html += f"""
                <div class="insight-item">
                    <strong>{i}.</strong> {insight.insight}
                    <br><span class="confidence">Confidence: {insight.confidence:.1%}</span>
                </div>
                """
        
        summary_html += "</div>"
        return summary_html
    
    def _build_html_data_overview(self, analysis_results: List[AnalysisResult]) -> str:
        """Build HTML data overview"""
        return f"""
        <div class="section">
            <h2>Data Overview</h2>
            <p>This analysis covers {len(analysis_results)} data dimensions with comprehensive statistical analysis and insights.</p>
        </div>
        """
    
    def _build_html_statistical_analysis(self, analysis_results: List[AnalysisResult]) -> str:
        """Build HTML statistical analysis"""
        html = """
        <div class="section">
            <h2>Statistical Analysis</h2>
            <div class="stats-grid">
        """
        
        for result in analysis_results:
            html += f"""
            <div class="stat-card">
                <h4>{result.column_name}</h4>
            """
            
            if hasattr(result, 'statistics') and result.statistics:
                for key, value in list(result.statistics.items())[:5]:  # Show top 5 stats
                    formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
                    html += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {formatted_value}</p>"
            
            html += "</div>"
        
        html += """
            </div>
        </div>
        """
        return html
    
    def _build_html_visualizations(self, visualizations: List[VisualizationResult]) -> str:
        """Build HTML visualizations section"""
        html = """
        <div class="section">
            <h2>Data Visualizations</h2>
        """
        
        for viz in visualizations:
            html += f"""
            <div class="chart-container">
                <h3>{viz.title or 'Chart'}</h3>
            """
            
            if viz.chart_data:
                if viz.chart_data.startswith('data:image'):
                    html += f'<img src="{viz.chart_data}" alt="{viz.title or "Chart"}">'
                elif os.path.exists(viz.chart_data):
                    with open(viz.chart_data, 'rb') as f:
                        img_data = base64.b64encode(f.read()).decode()
                        html += f'<img src="data:image/png;base64,{img_data}" alt="{viz.title or "Chart"}">'
                else:
                    html += f'<p>[Chart: {viz.chart_type}]</p>'
            
            html += "</div>"
        
        html += "</div>"
        return html
    
    def _build_html_insights(self, insights: List[InsightResult]) -> str:
        """Build HTML insights section"""
        html = """
        <div class="section">
            <h2>AI-Generated Insights</h2>
        """
        
        # Group by confidence
        high_conf = [i for i in insights if i.confidence > 0.8]
        med_conf = [i for i in insights if 0.6 <= i.confidence <= 0.8]
        
        for insight_list, title in [(high_conf, "High Confidence Insights"), (med_conf, "Additional Insights")]:
            if insight_list:
                html += f"<h3>{title}</h3>"
                for insight in insight_list:
                    html += f"""
                    <div class="insight-item">
                        {insight.insight}
                        <br><span class="confidence">Confidence: {insight.confidence:.1%}</span>
                    </div>
                    """
        
        html += "</div>"
        return html
    
    def _build_html_conclusions(self) -> str:
        """Build HTML conclusions section"""
        return """
        <div class="section">
            <h2>Conclusions & Recommendations</h2>
            <p>Based on the comprehensive analysis performed, several key patterns and trends have been identified. 
            The statistical analysis reveals important characteristics of the dataset, while AI-generated insights 
            provide actionable recommendations for data-driven decision making.</p>
            
            <h3>Recommended Next Steps</h3>
            <ul>
                <li>Review high-confidence insights for immediate action items</li>
                <li>Validate findings with domain experts and stakeholders</li>
                <li>Implement recommended changes based on analysis results</li>
                <li>Monitor key metrics to measure impact of implemented changes</li>
                <li>Schedule regular analysis updates to track trends over time</li>
            </ul>
        </div>
        """
    
    def _build_html_footer(self) -> str:
        """Build HTML footer"""
        return f"""
        <div class="footer">
            <p>Report generated by {self.config.author} using Apollo AI Analytics Platform</p>
            <p>© {self.timestamp.year} {self.config.company_name}. All rights reserved.</p>
        </div>
        """


# Utility functions for report generation
def create_sample_report_config() -> ReportConfig:
    """Create a sample report configuration"""
    return ReportConfig(
        company_name="Apollo AI Analytics",
        report_title="Quarterly Data Analysis Report",
        author="Apollo AI System",
        theme_color="#2E86AB",
        include_raw_data=False
    )


def generate_combined_report(
    analysis_results: List[AnalysisResult],
    visualizations: List[VisualizationResult],
    insights: List[InsightResult],
    output_dir: str = "./reports",
    config: Optional[ReportConfig] = None
) -> Dict[str, str]:
    """Generate both PDF and HTML reports"""
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Initialize generator
    generator = ReportGenerator(config)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Output paths
    html_path = os.path.join(output_dir, f"apollo_report_{timestamp}.html")
    pdf_path = os.path.join(output_dir, f"apollo_report_{timestamp}.pdf")
    
    results = {}
    
    try:
        # Generate HTML report
        results['html'] = generator.generate_html_report(
            analysis_results, visualizations, insights, html_path
        )
        
        # Generate PDF report
        if REPORTLAB_AVAILABLE:
            results['pdf'] = generator.generate_pdf_report(
                analysis_results, visualizations, insights, pdf_path
            )
        else:
            # Try HTML to PDF conversion
            if WEASYPRINT_AVAILABLE:
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                results['pdf'] = generator.generate_pdf_from_html(html_content, pdf_path)
            else:
                results['pdf_error'] = "PDF generation requires reportlab or weasyprint"
        
    except Exception as e:
        results['error'] = str(e)
    
    return results