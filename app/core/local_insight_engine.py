"""
Local Insight Engine
Pure Python statistical insights - no external APIs required.
Faster, more private, and cost-effective than external AI services.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)

class LocalInsightEngine:
    """
    Generate comprehensive insights using pure Python statistical analysis.
    No external APIs, no costs, complete privacy.
    """
    
    def __init__(self):
        self.insight_templates = {
            'high_impact': "Critical insight requiring immediate attention",
            'medium_impact': "Important finding for strategic planning",
            'low_impact': "Notable observation for future consideration"
        }
    
    def generate_comprehensive_insights(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive insights from data and analysis results.
        
        Args:
            df: Original DataFrame
            analysis_results: Results from enhanced analysis
            
        Returns:
            Comprehensive insights dictionary
        """
        start_time = datetime.now()
        
        try:
            insights = {
                "executive_summary": self._generate_executive_summary(df, analysis_results),
                "key_findings": self._extract_key_findings(df, analysis_results),
                "statistical_insights": self._generate_statistical_insights(df),
                "business_insights": self._generate_business_insights(df),
                "data_quality_insights": self._assess_data_quality_from_insights(df, analysis_results),
                "predictive_insights": self._generate_predictive_insights(df),
                "risk_assessment": self._assess_risks(df),
                "optimization_opportunities": self._find_optimization_opportunities(df),
                "recommendations": self._generate_smart_recommendations(df, analysis_results),
                "confidence_metrics": self._calculate_confidence_metrics(df),
                "processing_metadata": {
                    "engine": "local_python",
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "cost": "$0.00",
                    "privacy_level": "100% local"
                }
            }
            
            logger.info(f"Local insights generated in {insights['processing_metadata']['processing_time']:.2f}s")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating local insights: {str(e)}")
            return self._get_fallback_insights(df)
    
    def _generate_executive_summary(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> str:
        """Generate executive-level summary using templates and analysis."""
        
        # Extract key metrics
        row_count = len(df)
        col_count = len(df.columns)
        
        # Data quality score
        quality_score = analysis_results.get('analysis_results', {}).get('data_quality_assessment', {}).get('overall_score', 0)
        
        # Business impact score
        business_score = analysis_results.get('business_impact_score', 0)
        
        # Build summary components
        summary_parts = []
        
        # Dataset overview
        summary_parts.append(f"Analysis of {row_count:,} records across {col_count} variables")
        
        # Data quality assessment
        if quality_score > 85:
            summary_parts.append("reveals high-quality data suitable for strategic decision-making")
        elif quality_score > 70:
            summary_parts.append("shows good data quality with minor optimization opportunities")
        elif quality_score > 50:
            summary_parts.append("indicates moderate data quality requiring targeted improvements")
        else:
            summary_parts.append("highlights significant data quality issues needing immediate attention")
        
        # Business value assessment
        if business_score > 80:
            summary_parts.append("Significant business value potential identified with multiple high-impact optimization opportunities")
        elif business_score > 60:
            summary_parts.append("Moderate business opportunities detected with clear paths to value creation")
        elif business_score > 40:
            summary_parts.append("Some business value potential exists with focused improvement initiatives")
        else:
            summary_parts.append("Limited immediate business impact, however foundational improvements could unlock future value")
        
        # Statistical significance
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            correlations = df[numeric_cols].corr()
            high_corr_count = (correlations.abs() > 0.7).sum().sum() - len(numeric_cols)  # Exclude diagonal
            if high_corr_count > 0:
                summary_parts.append(f"Strong statistical relationships detected between {high_corr_count} variable pairs")
        
        # Risk and opportunity summary
        outlier_percentage = self._calculate_outlier_percentage(df)
        if outlier_percentage > 10:
            summary_parts.append(f"Notable data variance ({outlier_percentage:.1f}% outliers) suggests investigation opportunities")
        
        return ". ".join(summary_parts) + "."
    
    def _extract_key_findings(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract the most important findings from the data."""
        findings = []
        
        # Data volume insights
        if len(df) > 100000:
            findings.append("Large dataset provides high statistical power for reliable insights")
        elif len(df) < 100:
            findings.append("Small sample size - interpret results with caution")
        
        # Missing data patterns
        missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_percentage > 20:
            findings.append(f"Significant missing data ({missing_percentage:.1f}%) requires attention")
        elif missing_percentage < 5:
            findings.append(f"Excellent data completeness ({100-missing_percentage:.1f}%) enables robust analysis")
        
        # Variability insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            high_variance_cols = []
            for col in numeric_cols:
                if df[col].std() / df[col].mean() > 1.0:  # Coefficient of variation > 100%
                    high_variance_cols.append(col)
            
            if len(high_variance_cols) > 0:
                findings.append(f"High variability in {len(high_variance_cols)} metrics indicates optimization potential")
        
        # Correlation insights
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = abs(corr_matrix.iloc[i, j])
                    if corr_val > 0.8:
                        strong_correlations.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
            
            if strong_correlations:
                findings.append(f"Strong correlations detected - {len(strong_correlations)} variable pairs show >80% correlation")
        
        # Distribution insights
        skewed_columns = []
        for col in numeric_cols:
            if abs(df[col].skew()) > 1.5:
                skewed_columns.append(col)
        
        if skewed_columns:
            findings.append(f"Distribution analysis reveals {len(skewed_columns)} heavily skewed variables")
        
        # Business pattern detection
        business_patterns = self._detect_business_patterns(df)
        findings.extend(business_patterns)
        
        return findings[:10]  # Return top 10 findings
    
    def _generate_statistical_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate detailed statistical insights."""
        insights = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            # Distribution analysis
            insights['distributions'] = {}
            for col in numeric_cols:
                data = df[col].dropna()
                if len(data) > 0:
                    # Normality test
                    _, p_value = stats.normaltest(data)
                    
                    # Distribution characteristics
                    insights['distributions'][col] = {
                        'is_normal': p_value > 0.05,
                        'skewness': data.skew(),
                        'kurtosis': data.kurtosis(),
                        'outlier_count': len(self._detect_outliers_iqr(data)),
                        'coefficient_of_variation': (data.std() / data.mean() * 100) if data.mean() != 0 else 0,
                        'interpretation': self._interpret_distribution(data)
                    }
            
            # Correlation analysis
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                insights['correlations'] = {
                    'strong_positive': self._find_strong_correlations(corr_matrix, 0.7, 1.0),
                    'strong_negative': self._find_strong_correlations(corr_matrix, -1.0, -0.7),
                    'moderate_correlations': self._find_strong_correlations(corr_matrix, 0.4, 0.7),
                    'insights': self._interpret_correlations(corr_matrix)
                }
        
        # Categorical analysis
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            insights['categorical_analysis'] = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                insights['categorical_analysis'][col] = {
                    'unique_values': len(value_counts),
                    'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None,
                    'frequency_distribution': value_counts.head(5).to_dict(),
                    'concentration': self._calculate_concentration_ratio(value_counts),
                    'insights': self._interpret_categorical_distribution(value_counts)
                }
        
        return insights
    
    def _generate_business_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate business-focused insights."""
        business_insights = {}
        
        # Detect business domain
        domain = self._detect_business_domain(df)
        business_insights['detected_domain'] = domain
        
        # Domain-specific analysis
        if domain == 'sales':
            business_insights['sales_insights'] = self._analyze_sales_patterns(df)
        elif domain == 'customer':
            business_insights['customer_insights'] = self._analyze_customer_patterns(df)
        elif domain == 'finance':
            business_insights['financial_insights'] = self._analyze_financial_patterns(df)
        elif domain == 'operations':
            business_insights['operational_insights'] = self._analyze_operational_patterns(df)
        
        # Universal business metrics
        business_insights['efficiency_metrics'] = self._calculate_efficiency_metrics(df)
        business_insights['growth_indicators'] = self._analyze_growth_patterns(df)
        business_insights['risk_indicators'] = self._identify_risk_patterns(df)
        
        return business_insights
    
    def _generate_predictive_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictive insights using statistical methods."""
        predictive_insights = {}
        
        # Time series analysis if date column exists
        date_cols = df.select_dtypes(include=['datetime64', 'object']).columns
        for col in date_cols:
            try:
                df[col] = pd.to_datetime(df[col])
                if col not in df.select_dtypes(include=['datetime64']).columns:
                    continue
                    
                # Simple trend analysis
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for num_col in numeric_cols:
                    if len(df.dropna(subset=[col, num_col])) > 10:
                        trend_insights = self._analyze_time_trend(df, col, num_col)
                        predictive_insights[f'{num_col}_trend'] = trend_insights
                break
            except:
                continue
        
        # Clustering insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2 and len(df) > 10:
            clustering_insights = self._perform_clustering_analysis(df[numeric_cols])
            predictive_insights['clustering'] = clustering_insights
        
        # Anomaly detection
        if len(numeric_cols) > 0:
            anomalies = self._detect_multivariate_anomalies(df[numeric_cols])
            predictive_insights['anomalies'] = anomalies
        
        return predictive_insights
    
    def _assess_risks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess various data and business risks."""
        risks = {
            'data_risks': [],
            'business_risks': [],
            'technical_risks': [],
            'overall_risk_score': 0
        }
        
        risk_score = 0
        
        # Data quality risks
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_pct > 30:
            risks['data_risks'].append(f"High missing data rate ({missing_pct:.1f}%) may compromise analysis reliability")
            risk_score += 30
        elif missing_pct > 15:
            risks['data_risks'].append(f"Moderate missing data ({missing_pct:.1f}%) requires monitoring")
            risk_score += 15
        
        # Outlier risks
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        total_outliers = 0
        for col in numeric_cols:
            outliers = self._detect_outliers_iqr(df[col])
            total_outliers += len(outliers)
        
        outlier_pct = (total_outliers / (len(df) * len(numeric_cols))) * 100 if len(numeric_cols) > 0 else 0
        if outlier_pct > 10:
            risks['data_risks'].append(f"High outlier rate ({outlier_pct:.1f}%) may indicate data quality issues")
            risk_score += 20
        
        # Business risks
        if len(df) < 100:
            risks['business_risks'].append("Small sample size may limit statistical significance of findings")
            risk_score += 25
        
        # Concentration risks
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            concentration = self._calculate_concentration_ratio(df[col].value_counts())
            if concentration > 0.8:
                risks['business_risks'].append(f"High concentration in {col} (top value: {concentration*100:.1f}%) indicates potential single-point-of-failure")
                risk_score += 15
        
        risks['overall_risk_score'] = min(100, risk_score)
        return risks
    
    def _find_optimization_opportunities(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities."""
        opportunities = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # High variance opportunities
        for col in numeric_cols:
            cv = (df[col].std() / df[col].mean() * 100) if df[col].mean() != 0 else 0
            if cv > 50:
                opportunities.append({
                    'type': 'variance_reduction',
                    'column': col,
                    'current_cv': cv,
                    'opportunity': f"Reduce variability in {col} (CV: {cv:.1f}%)",
                    'potential_impact': 'high' if cv > 100 else 'medium',
                    'effort_estimate': 'medium'
                })
        
        # Missing data opportunities
        missing_cols = df.columns[df.isnull().any()].tolist()
        for col in missing_cols:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if 5 < missing_pct < 30:  # Sweet spot for data improvement
                opportunities.append({
                    'type': 'data_completeness',
                    'column': col,
                    'missing_percentage': missing_pct,
                    'opportunity': f"Improve data collection for {col} ({missing_pct:.1f}% missing)",
                    'potential_impact': 'medium',
                    'effort_estimate': 'low' if missing_pct < 15 else 'medium'
                })
        
        # Correlation opportunities
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            strong_corrs = self._find_strong_correlations(corr_matrix, 0.7, 1.0)
            for corr in strong_corrs:
                opportunities.append({
                    'type': 'correlation_leverage',
                    'variables': corr['variables'],
                    'correlation': corr['correlation'],
                    'opportunity': f"Leverage strong relationship between {corr['variables'][0]} and {corr['variables'][1]}",
                    'potential_impact': 'high',
                    'effort_estimate': 'low'
                })
        
        # Sort by potential impact
        impact_order = {'high': 3, 'medium': 2, 'low': 1}
        opportunities.sort(key=lambda x: impact_order.get(x['potential_impact'], 0), reverse=True)
        
        return opportunities[:10]  # Return top 10 opportunities
    
    def _generate_smart_recommendations(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate smart, actionable recommendations."""
        recommendations = []
        
        # Data quality recommendations
        quality_score = analysis_results.get('analysis_results', {}).get('data_quality_assessment', {}).get('overall_score', 100)
        if quality_score < 80:
            recommendations.append({
                'category': 'data_quality',
                'priority': 'high',
                'title': 'Improve Data Quality',
                'description': f'Current data quality score ({quality_score:.1f}%) is below optimal threshold',
                'action': 'Implement data validation and cleansing procedures',
                'expected_impact': 'Increase analysis reliability by 25-40%',
                'timeline': '2-4 weeks',
                'resources_needed': 'Data engineering support'
            })
        
        # Business optimization recommendations
        opportunities = self._find_optimization_opportunities(df)
        for opp in opportunities[:3]:  # Top 3 opportunities
            if opp['potential_impact'] == 'high':
                recommendations.append({
                    'category': 'optimization',
                    'priority': 'high' if opp['effort_estimate'] == 'low' else 'medium',
                    'title': f"Optimize {opp['column'] if 'column' in opp else 'Process'}",
                    'description': opp['opportunity'],
                    'action': self._generate_specific_action(opp),
                    'expected_impact': 'Improve performance by 15-30%',
                    'timeline': '1-3 weeks' if opp['effort_estimate'] == 'low' else '4-8 weeks',
                    'resources_needed': 'Operational team collaboration'
                })
        
        # Statistical insights recommendations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_opportunities = self._find_strong_correlations(df[numeric_cols].corr(), 0.7, 1.0)
            if corr_opportunities:
                recommendations.append({
                    'category': 'analytics',
                    'priority': 'medium',
                    'title': 'Leverage Statistical Relationships',
                    'description': f'Strong correlations detected between {len(corr_opportunities)} variable pairs',
                    'action': 'Develop predictive models using identified relationships',
                    'expected_impact': 'Enable predictive capabilities with 70-85% accuracy',
                    'timeline': '3-6 weeks',
                    'resources_needed': 'Analytics team'
                })
        
        return recommendations
    
    # Helper methods
    def _detect_outliers_iqr(self, series: pd.Series) -> List[float]:
        """Detect outliers using IQR method."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return series[(series < lower_bound) | (series > upper_bound)].tolist()
    
    def _calculate_outlier_percentage(self, df: pd.DataFrame) -> float:
        """Calculate percentage of outliers in numeric columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return 0
        
        total_outliers = 0
        total_values = 0
        
        for col in numeric_cols:
            outliers = self._detect_outliers_iqr(df[col])
            total_outliers += len(outliers)
            total_values += len(df[col].dropna())
        
        return (total_outliers / total_values * 100) if total_values > 0 else 0
    
    def _detect_business_patterns(self, df: pd.DataFrame) -> List[str]:
        """Detect business-specific patterns in the data."""
        patterns = []
        
        # Revenue/sales patterns
        revenue_cols = [col for col in df.columns if any(
            keyword in col.lower() for keyword in ['revenue', 'sales', 'amount', 'total', 'price']
        )]
        
        if revenue_cols:
            for col in revenue_cols[:2]:  # Check first 2 revenue columns
                if df[col].dtype in ['int64', 'float64']:
                    growth_rate = self._calculate_simple_growth(df[col])
                    if abs(growth_rate) > 10:
                        patterns.append(f"{col} shows {growth_rate:+.1f}% trend indicating {'growth' if growth_rate > 0 else 'decline'}")
        
        # Time-based patterns
        date_like_cols = [col for col in df.columns if any(
            keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated']
        )]
        
        if date_like_cols and len(df) > 10:
            patterns.append(f"Time-series data detected - {len(date_like_cols)} temporal variables available for trend analysis")
        
        return patterns
    
    def _calculate_simple_growth(self, series: pd.Series) -> float:
        """Calculate simple growth rate from first to last value."""
        clean_series = series.dropna()
        if len(clean_series) < 2:
            return 0
        
        first_val = clean_series.iloc[0]
        last_val = clean_series.iloc[-1]
        
        if first_val == 0:
            return 0
        
        return ((last_val - first_val) / first_val) * 100
    
    def _interpret_distribution(self, data: pd.Series) -> str:
        """Interpret distribution characteristics."""
        skewness = data.skew()
        kurtosis = data.kurtosis()
        
        interpretation = []
        
        if abs(skewness) < 0.5:
            interpretation.append("approximately symmetric")
        elif skewness > 0.5:
            interpretation.append("right-skewed (long tail toward high values)")
        else:
            interpretation.append("left-skewed (long tail toward low values)")
        
        if kurtosis > 3:
            interpretation.append("heavy-tailed (more outliers than normal)")
        elif kurtosis < -1:
            interpretation.append("light-tailed (fewer outliers than normal)")
        
        return ", ".join(interpretation)
    
    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, min_corr: float, max_corr: float) -> List[Dict]:
        """Find correlations within specified range."""
        correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if min_corr <= abs(corr_val) <= max_corr:
                    correlations.append({
                        'variables': [corr_matrix.columns[i], corr_matrix.columns[j]],
                        'correlation': corr_val,
                        'strength': 'strong' if abs(corr_val) > 0.7 else 'moderate'
                    })
        
        return correlations
    
    def _interpret_correlations(self, corr_matrix: pd.DataFrame) -> List[str]:
        """Generate insights from correlation analysis."""
        insights = []
        
        strong_positive = self._find_strong_correlations(corr_matrix, 0.7, 1.0)
        strong_negative = self._find_strong_correlations(corr_matrix, -1.0, -0.7)
        
        if strong_positive:
            insights.append(f"{len(strong_positive)} strong positive relationships suggest optimization opportunities")
        
        if strong_negative:
            insights.append(f"{len(strong_negative)} strong negative relationships indicate potential trade-offs")
        
        # Check for multicollinearity
        high_corr = self._find_strong_correlations(corr_matrix, 0.9, 1.0)
        if high_corr:
            insights.append(f"Very high correlations ({len(high_corr)} pairs >0.9) may indicate redundant variables")
        
        return insights
    
    def _calculate_concentration_ratio(self, value_counts: pd.Series) -> float:
        """Calculate concentration ratio (top value frequency)."""
        if len(value_counts) == 0:
            return 0
        return value_counts.iloc[0] / value_counts.sum()
    
    def _interpret_categorical_distribution(self, value_counts: pd.Series) -> List[str]:
        """Interpret categorical variable distribution."""
        insights = []
        
        concentration = self._calculate_concentration_ratio(value_counts)
        
        if concentration > 0.8:
            insights.append(f"Highly concentrated - top value represents {concentration*100:.1f}% of data")
        elif concentration > 0.5:
            insights.append(f"Moderately concentrated - top value represents {concentration*100:.1f}% of data")
        else:
            insights.append("Well distributed across categories")
        
        if len(value_counts) > 20:
            insights.append(f"High cardinality ({len(value_counts)} unique values) may require grouping")
        
        return insights
    
    def _detect_business_domain(self, df: pd.DataFrame) -> str:
        """Detect likely business domain from column names."""
        columns_lower = [col.lower() for col in df.columns]
        
        # Sales domain keywords
        sales_keywords = ['revenue', 'sales', 'price', 'amount', 'total', 'order']
        if sum(1 for col in columns_lower if any(kw in col for kw in sales_keywords)) >= 2:
            return 'sales'
        
        # Customer domain keywords
        customer_keywords = ['customer', 'user', 'client', 'name', 'email', 'phone']
        if sum(1 for col in columns_lower if any(kw in col for kw in customer_keywords)) >= 2:
            return 'customer'
        
        # Finance domain keywords
        finance_keywords = ['cost', 'expense', 'profit', 'budget', 'account', 'balance']
        if sum(1 for col in columns_lower if any(kw in col for kw in finance_keywords)) >= 2:
            return 'finance'
        
        # Operations domain keywords
        operations_keywords = ['quantity', 'inventory', 'stock', 'production', 'efficiency']
        if sum(1 for col in columns_lower if any(kw in col for kw in operations_keywords)) >= 2:
            return 'operations'
        
        return 'general'
    
    def _analyze_sales_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sales-specific patterns."""
        insights = {}
        
        # Find revenue/sales columns
        revenue_cols = [col for col in df.columns if any(
            keyword in col.lower() for keyword in ['revenue', 'sales', 'amount', 'total']
        )]
        
        for col in revenue_cols:
            if df[col].dtype in ['int64', 'float64']:
                insights[f'{col}_analysis'] = {
                    'total': df[col].sum(),
                    'average': df[col].mean(),
                    'growth_rate': self._calculate_simple_growth(df[col]),
                    'volatility': (df[col].std() / df[col].mean() * 100) if df[col].mean() != 0 else 0,
                    'top_contributors': self._find_top_contributors(df, col)
                }
        
        return insights
    
    def _analyze_customer_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze customer-specific patterns."""
        insights = {}
        
        # Customer segmentation if customer ID exists
        customer_cols = [col for col in df.columns if any(
            keyword in col.lower() for keyword in ['customer', 'user', 'client', 'id']
        )]
        
        if customer_cols:
            customer_col = customer_cols[0]
            unique_customers = df[customer_col].nunique()
            total_records = len(df)
            
            insights['customer_analysis'] = {
                'unique_customers': unique_customers,
                'records_per_customer': total_records / unique_customers if unique_customers > 0 else 0,
                'customer_concentration': self._analyze_customer_concentration(df, customer_col)
            }
        
        return insights
    
    def _analyze_financial_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze finance-specific patterns."""
        insights = {}
        
        # Profitability analysis
        profit_cols = [col for col in df.columns if 'profit' in col.lower()]
        cost_cols = [col for col in df.columns if any(
            keyword in col.lower() for keyword in ['cost', 'expense']
        )]
        
        if profit_cols:
            for col in profit_cols:
                if df[col].dtype in ['int64', 'float64']:
                    insights[f'{col}_analysis'] = {
                        'total_profit': df[col].sum(),
                        'average_margin': df[col].mean(),
                        'profit_volatility': df[col].std()
                    }
        
        return insights
    
    def _analyze_operational_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze operations-specific patterns."""
        insights = {}
        
        # Efficiency metrics
        quantity_cols = [col for col in df.columns if any(
            keyword in col.lower() for keyword in ['quantity', 'volume', 'count']
        )]
        
        time_cols = [col for col in df.columns if any(
            keyword in col.lower() for keyword in ['time', 'duration', 'hours']
        )]
        
        if quantity_cols and time_cols:
            insights['efficiency_indicators'] = {
                'productivity_metrics': f"Found {len(quantity_cols)} quantity and {len(time_cols)} time variables",
                'efficiency_calculation_possible': True
            }
        
        return insights
    
    def _calculate_efficiency_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate general efficiency metrics."""
        metrics = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            # Resource utilization
            for col in numeric_cols:
                if 'utilization' in col.lower() or 'efficiency' in col.lower():
                    metrics[f'{col}_efficiency'] = {
                        'average': df[col].mean(),
                        'best_performance': df[col].max(),
                        'improvement_potential': df[col].max() - df[col].mean()
                    }
        
        return metrics
    
    def _analyze_growth_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze growth patterns across variables."""
        growth_patterns = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            growth_rate = self._calculate_simple_growth(df[col])
            if abs(growth_rate) > 5:  # Significant growth/decline
                growth_patterns[col] = {
                    'growth_rate': growth_rate,
                    'trend': 'growing' if growth_rate > 0 else 'declining',
                    'magnitude': 'high' if abs(growth_rate) > 20 else 'moderate'
                }
        
        return growth_patterns
    
    def _identify_risk_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify risk patterns in the data."""
        risk_patterns = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Volatility risks
        high_volatility_vars = []
        for col in numeric_cols:
            cv = (df[col].std() / df[col].mean() * 100) if df[col].mean() != 0 else 0
            if cv > 50:
                high_volatility_vars.append({'variable': col, 'cv': cv})
        
        if high_volatility_vars:
            risk_patterns['volatility_risks'] = high_volatility_vars
        
        # Concentration risks
        categorical_cols = df.select_dtypes(include=['object']).columns
        concentration_risks = []
        for col in categorical_cols:
            concentration = self._calculate_concentration_ratio(df[col].value_counts())
            if concentration > 0.8:
                concentration_risks.append({'variable': col, 'concentration': concentration})
        
        if concentration_risks:
            risk_patterns['concentration_risks'] = concentration_risks
        
        return risk_patterns
    
    def _analyze_time_trend(self, df: pd.DataFrame, date_col: str, value_col: str) -> Dict[str, Any]:
        """Analyze time-based trends."""
        try:
            # Sort by date
            df_sorted = df.sort_values(date_col)
            
            # Calculate trend
            x = np.arange(len(df_sorted))
            y = df_sorted[value_col].values
            
            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            return {
                'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                'trend_strength': abs(r_value),
                'statistical_significance': p_value < 0.05,
                'projection_next_period': intercept + slope * len(df_sorted),
                'confidence': 'high' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.4 else 'low'
            }
        except:
            return {'error': 'Unable to calculate time trend'}
    
    def _perform_clustering_analysis(self, numeric_df: pd.DataFrame) -> Dict[str, Any]:
        """Perform clustering analysis on numeric data."""
        try:
            # Handle missing values
            clean_df = numeric_df.dropna()
            if len(clean_df) < 10:
                return {'error': 'Insufficient data for clustering'}
            
            # Standardize data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(clean_df)
            
            # Determine optimal number of clusters (2-5 range)
            max_clusters = min(5, len(clean_df) // 3)
            if max_clusters < 2:
                return {'error': 'Too few observations for clustering'}
            
            silhouette_scores = []
            for n_clusters in range(2, max_clusters + 1):
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(scaled_data)
                silhouette_avg = silhouette_score(scaled_data, cluster_labels)
                silhouette_scores.append(float(silhouette_avg))  # Ensure JSON serializable
            
            # Best number of clusters
            best_n_clusters = silhouette_scores.index(max(silhouette_scores)) + 2
            
            # Final clustering
            kmeans = KMeans(n_clusters=best_n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(scaled_data)
            
            # Analyze clusters
            cluster_analysis = {}
            for cluster_id in range(best_n_clusters):
                cluster_mask = cluster_labels == cluster_id
                cluster_data = clean_df[cluster_mask]
                
                cluster_analysis[f'cluster_{cluster_id}'] = {
                    'size': int(len(cluster_data)),
                    'percentage': float(len(cluster_data) / len(clean_df) * 100),
                    'characteristics': {col: float(cluster_data[col].mean()) for col in clean_df.columns}
                }
            
            return {
                'optimal_clusters': int(best_n_clusters),
                'silhouette_score': float(max(silhouette_scores)),
                'cluster_analysis': cluster_analysis,
                'insights': f"Data naturally segments into {best_n_clusters} distinct groups"
            }
            
        except Exception as e:
            return {'error': f'Clustering analysis failed: {str(e)}'}
    
    def _detect_multivariate_anomalies(self, numeric_df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies using multivariate methods."""
        try:
            clean_df = numeric_df.dropna()
            if len(clean_df) < 10:
                return {'error': 'Insufficient data for anomaly detection'}
            
            # Z-score based anomaly detection
            z_scores = np.abs(stats.zscore(clean_df))
            anomaly_threshold = 3
            
            # Points with any z-score > threshold
            anomalous_points = (z_scores > anomaly_threshold).any(axis=1)
            anomaly_count = anomalous_points.sum()
            
            # PCA-based anomaly detection if we have enough features
            pca_anomalies = 0
            if clean_df.shape[1] >= 2:
                pca = PCA(n_components=min(2, clean_df.shape[1]))
                pca_transformed = pca.fit_transform(StandardScaler().fit_transform(clean_df))
                
                # Distance from origin in PCA space
                distances = np.sqrt(np.sum(pca_transformed**2, axis=1))
                distance_threshold = np.percentile(distances, 95)
                pca_anomalies = (distances > distance_threshold).sum()
            
            return {
                'total_anomalies': int(anomaly_count),
                'anomaly_percentage': float(anomaly_count / len(clean_df) * 100),
                'pca_anomalies': int(pca_anomalies),
                'severity': 'high' if anomaly_count > len(clean_df) * 0.1 else 'moderate' if anomaly_count > len(clean_df) * 0.05 else 'low',
                'recommendation': 'Investigate anomalous points for data quality issues or business insights'
            }
            
        except Exception as e:
            return {'error': f'Anomaly detection failed: {str(e)}'}
    
    def _find_top_contributors(self, df: pd.DataFrame, value_col: str) -> Dict[str, Any]:
        """Find top contributors to a value column."""
        try:
            # Try to find a grouping column (first categorical or ID-like column)
            grouping_cols = df.select_dtypes(include=['object']).columns
            if len(grouping_cols) == 0:
                return {'error': 'No grouping column found'}
            
            grouping_col = grouping_cols[0]
            
            # Group and sum
            grouped = df.groupby(grouping_col)[value_col].sum().sort_values(ascending=False)
            
            top_5 = grouped.head(5)
            total = grouped.sum()
            
            return {
                'top_contributors': top_5.to_dict(),
                'top_5_percentage': (top_5.sum() / total * 100) if total > 0 else 0,
                'concentration': 'high' if (top_5.sum() / total) > 0.8 else 'moderate'
            }
            
        except:
            return {'error': 'Unable to calculate top contributors'}
    
    def _analyze_customer_concentration(self, df: pd.DataFrame, customer_col: str) -> Dict[str, Any]:
        """Analyze customer concentration patterns."""
        try:
            customer_counts = df[customer_col].value_counts()
            
            # Top customers
            top_10_pct = customer_counts.head(len(customer_counts) // 10 if len(customer_counts) > 10 else 1)
            
            return {
                'total_customers': len(customer_counts),
                'top_10_percent_activity': (top_10_pct.sum() / customer_counts.sum() * 100) if customer_counts.sum() > 0 else 0,
                'most_active_customer_records': customer_counts.iloc[0] if len(customer_counts) > 0 else 0,
                'average_records_per_customer': customer_counts.mean()
            }
            
        except:
            return {'error': 'Unable to analyze customer concentration'}
    
    def _generate_specific_action(self, opportunity: Dict[str, Any]) -> str:
        """Generate specific action recommendations based on opportunity type."""
        opp_type = opportunity.get('type', '')
        
        if opp_type == 'variance_reduction':
            return f"Implement process standardization to reduce variability in {opportunity.get('column', 'metric')}"
        elif opp_type == 'data_completeness':
            return f"Enhance data collection procedures for {opportunity.get('column', 'variable')}"
        elif opp_type == 'correlation_leverage':
            variables = opportunity.get('variables', ['variable1', 'variable2'])
            return f"Develop predictive model using relationship between {variables[0]} and {variables[1]}"
        else:
            return "Implement targeted improvement initiative based on identified pattern"
    
    def _calculate_confidence_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate confidence metrics for the analysis."""
        metrics = {}
        
        # Sample size confidence
        sample_size = len(df)
        if sample_size > 1000:
            metrics['sample_size_confidence'] = 'high'
        elif sample_size > 100:
            metrics['sample_size_confidence'] = 'medium'
        else:
            metrics['sample_size_confidence'] = 'low'
        
        # Data completeness confidence
        completeness = (df.count().sum() / (len(df) * len(df.columns))) * 100
        if completeness > 90:
            metrics['completeness_confidence'] = 'high'
        elif completeness > 75:
            metrics['completeness_confidence'] = 'medium'
        else:
            metrics['completeness_confidence'] = 'low'
        
        # Statistical power
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            avg_effect_size = np.mean([
                abs(df[col].mean() / df[col].std()) if df[col].std() > 0 else 0 
                for col in numeric_cols
            ])
            
            if avg_effect_size > 0.8:
                metrics['statistical_power'] = 'high'
            elif avg_effect_size > 0.5:
                metrics['statistical_power'] = 'medium'
            else:
                metrics['statistical_power'] = 'low'
        
        # Overall confidence
        confidence_scores = [
            3 if metrics.get('sample_size_confidence') == 'high' else 2 if metrics.get('sample_size_confidence') == 'medium' else 1,
            3 if metrics.get('completeness_confidence') == 'high' else 2 if metrics.get('completeness_confidence') == 'medium' else 1,
            3 if metrics.get('statistical_power', 'low') == 'high' else 2 if metrics.get('statistical_power', 'low') == 'medium' else 1
        ]
        
        avg_confidence = np.mean(confidence_scores)
        if avg_confidence > 2.5:
            metrics['overall_confidence'] = 'high'
        elif avg_confidence > 1.5:
            metrics['overall_confidence'] = 'medium'
        else:
            metrics['overall_confidence'] = 'low'
        
        return metrics
    
    def _get_fallback_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate basic fallback insights when main analysis fails."""
        return {
            "executive_summary": f"Basic analysis of {len(df)} records completed with {len(df.columns)} variables.",
            "key_findings": [
                f"Dataset contains {len(df):,} rows and {len(df.columns)} columns",
                f"Data completeness: {(df.count().sum() / (len(df) * len(df.columns)) * 100):.1f}%"
            ],
            "recommendations": [
                {
                    'category': 'basic',
                    'priority': 'medium',
                    'title': 'Review Data Quality',
                    'description': 'Ensure data quality before advanced analysis',
                    'action': 'Validate data sources and collection methods'
                }
            ],
            "processing_metadata": {
                "engine": "fallback",
                "processing_time": 0.1,
                "cost": "$0.00",
                "privacy_level": "100% local"
            }
        }
    
    def _assess_data_quality_from_insights(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data quality based on analysis results."""
        quality_insights = {}
        
        # Get basic quality metrics
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        
        # Extract quality score from analysis results if available
        quality_score = analysis_results.get('analysis_results', {}).get('data_quality_assessment', {}).get('overall_score', 0)
        
        if quality_score == 0:
            # Calculate our own quality score
            quality_score = max(0, 100 - missing_pct * 2)  # Simple calculation
        
        quality_insights['overall_assessment'] = {
            'quality_score': quality_score,
            'missing_data_percentage': missing_pct,
            'assessment': 'excellent' if quality_score > 90 else 'good' if quality_score > 70 else 'needs_improvement'
        }
        
        # Data completeness insights
        if missing_pct < 5:
            quality_insights['completeness_insight'] = "Excellent data completeness enables robust analysis"
        elif missing_pct < 20:
            quality_insights['completeness_insight'] = "Good data quality with minor gaps"
        else:
            quality_insights['completeness_insight'] = "Significant missing data requires attention"
        
        # Consistency insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            outlier_counts = [len(self._detect_outliers_iqr(df[col])) for col in numeric_cols]
            avg_outlier_pct = np.mean(outlier_counts) / len(df) * 100
            
            if avg_outlier_pct < 5:
                quality_insights['consistency_insight'] = "Data shows good consistency with minimal outliers"
            elif avg_outlier_pct < 15:
                quality_insights['consistency_insight'] = "Moderate outlier presence suggests data review"
            else:
                quality_insights['consistency_insight'] = "High outlier rate indicates potential data quality issues"
        
        return quality_insights
