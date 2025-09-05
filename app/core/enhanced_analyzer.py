"""
Enhanced Data Analyzer
A more sophisticated analysis engine with advanced statistical tests, business insights, and actionable recommendations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import warnings
from scipy import stats
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import re
from datetime import datetime, date
import json

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class EnhancedDataAnalyzer:
    """
    Advanced data analysis class with comprehensive insights and business intelligence.
    
    Features:
    - Advanced statistical analysis with effect sizes
    - Business pattern detection
    - Predictive insights
    - Data quality assessment with actionable recommendations
    - Anomaly detection
    - Clustering analysis
    - Time series analysis (when applicable)
    - Business intelligence metrics
    """
    
    def __init__(self, file_path: str):
        """Initialize the enhanced analyzer."""
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None
        self.analysis_results: Dict[str, Any] = {}
        self.business_insights: Dict[str, Any] = {}
        
        # Load and prepare data
        self._load_data()
        self._prepare_data()
    
    def _load_data(self) -> None:
        """Load data with comprehensive error handling."""
        try:
            file_ext = self.file_path.suffix.lower()
            
            # Try different encodings for CSV
            if file_ext == '.csv':
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        self.df = pd.read_csv(self.file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not read CSV file with any encoding")
            elif file_ext in ['.xls', '.xlsx']:
                self.df = pd.read_excel(self.file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            if self.df is None or self.df.empty:
                raise ValueError("File is empty or could not be read")
                
        except Exception as e:
            raise ValueError(f"Error loading file: {str(e)}")
    
    def _prepare_data(self) -> None:
        """Prepare and clean data for analysis."""
        # Remove completely empty rows and columns
        self.df = self.df.dropna(how='all').dropna(axis=1, how='all')
        
        # Convert obvious date columns
        for col in self.df.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated']):
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='ignore')
                except:
                    pass
        
        # Clean column names
        self.df.columns = [col.strip().replace(' ', '_').lower() for col in self.df.columns]
    
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive business-focused analysis."""
        
        results = {
            'executive_summary': self._generate_executive_summary(),
            'data_quality_assessment': self._assess_data_quality(),
            'statistical_analysis': self._perform_advanced_statistical_analysis(),
            'business_insights': self._extract_business_insights(),
            'predictive_insights': self._generate_predictive_insights(),
            'anomaly_detection': self._detect_anomalies(),
            'recommendations': self._generate_actionable_recommendations(),
            'data_story': self._create_data_story(),
            'confidence_metrics': self._calculate_confidence_metrics()
        }
        
        return results
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary with key metrics."""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        date_cols = self.df.select_dtypes(include=['datetime64']).columns
        
        # Calculate key business metrics
        data_completeness = float(((self.df.count() / len(self.df)) * 100).mean())
        data_diversity = int(len(self.df.nunique()[self.df.nunique() > 1]))
        
        # Identify potential KPIs
        potential_kpis = []
        for col in numeric_cols:
            if any(keyword in col.lower() for keyword in ['revenue', 'sales', 'profit', 'cost', 'price', 'amount', 'value']):
                potential_kpis.append({
                    'metric': col,
                    'total': float(self.df[col].sum()),
                    'average': float(self.df[col].mean()),
                    'trend': 'increasing' if self.df[col].corr(pd.Series(range(len(self.df)))) > 0 else 'decreasing'
                })
        
        return {
            'dataset_overview': {
                'total_records': len(self.df),
                'total_features': len(self.df.columns),
                'numeric_features': len(numeric_cols),
                'categorical_features': len(categorical_cols),
                'date_features': len(date_cols),
                'data_completeness_percentage': round(data_completeness, 1),
                'data_diversity_score': data_diversity
            },
            'key_findings': self._identify_key_findings(),
            'potential_kpis': potential_kpis[:5],  # Top 5 potential KPIs
            'data_quality_score': self._calculate_overall_quality_score(),
            'business_value_indicators': self._assess_business_value()
        }
    
    def _assess_data_quality(self) -> Dict[str, Any]:
        """Comprehensive data quality assessment."""
        quality_issues = []
        quality_score = 100.0
        
        # Missing values analysis
        missing_analysis = {}
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            missing_pct = (missing_count / len(self.df)) * 100
            
            if missing_pct > 0:
                missing_analysis[col] = {
                    'missing_count': missing_count,
                    'missing_percentage': missing_pct,
                    'pattern': self._analyze_missing_pattern(col)
                }
                
                if missing_pct > 50:
                    quality_score -= 15
                    quality_issues.append(f"Column '{col}' has {missing_pct:.1f}% missing values - critical data loss")
                elif missing_pct > 20:
                    quality_score -= 5
                    quality_issues.append(f"Column '{col}' has {missing_pct:.1f}% missing values - moderate concern")
        
        # Duplicate analysis
        duplicate_count = self.df.duplicated().sum()
        if duplicate_count > 0:
            duplicate_pct = (duplicate_count / len(self.df)) * 100
            quality_score -= min(20, duplicate_pct)
            quality_issues.append(f"Found {duplicate_count} duplicate rows ({duplicate_pct:.1f}%)")
        
        # Data consistency checks
        consistency_issues = self._check_data_consistency()
        quality_score -= len(consistency_issues) * 2
        quality_issues.extend(consistency_issues)
        
        # Outlier detection
        outlier_analysis = self._detect_outliers_comprehensive()
        
        return {
            'overall_score': max(0, round(quality_score, 1)),
            'missing_values_analysis': missing_analysis,
            'duplicate_analysis': {
                'duplicate_count': duplicate_count,
                'duplicate_percentage': (duplicate_count / len(self.df)) * 100 if len(self.df) > 0 else 0
            },
            'outlier_analysis': outlier_analysis,
            'consistency_issues': consistency_issues,
            'data_types_analysis': self._analyze_data_types(),
            'quality_issues': quality_issues,
            'improvement_suggestions': self._suggest_quality_improvements()
        }
    
    def _perform_advanced_statistical_analysis(self) -> Dict[str, Any]:
        """Advanced statistical analysis with effect sizes and business interpretation."""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return {'message': 'No numeric columns found for statistical analysis'}
        
        results = {}
        
        # Descriptive statistics with business context
        for col in numeric_cols:
            data = self.df[col].dropna()
            if len(data) == 0:
                continue
                
            # Calculate comprehensive statistics
            stats_dict = {
                'count': int(len(data)),
                'mean': float(data.mean()),
                'median': float(data.median()),
                'std': float(data.std()),
                'min': float(data.min()),
                'max': float(data.max()),
                'q1': float(data.quantile(0.25)),
                'q3': float(data.quantile(0.75)),
                'iqr': float(data.quantile(0.75) - data.quantile(0.25)),
                'skewness': float(stats.skew(data)),
                'kurtosis': float(stats.kurtosis(data)),
                'coefficient_of_variation': float((data.std() / data.mean() * 100) if data.mean() != 0 else 0),
                'range': float(data.max() - data.min()),
                'outlier_count': int(len(self._detect_outliers_iqr(data)))
            }
            
            # Business interpretation
            stats_dict['business_interpretation'] = self._interpret_statistics_business(col, stats_dict)
            
            # Distribution analysis
            stats_dict['distribution_analysis'] = self._analyze_distribution(data)
            
            results[col] = stats_dict
        
        # Correlation analysis with business insights
        correlation_analysis = self._advanced_correlation_analysis()
        
        # Statistical tests
        statistical_tests = self._perform_comprehensive_tests()
        
        return {
            'descriptive_statistics': results,
            'correlation_analysis': correlation_analysis,
            'statistical_tests': statistical_tests,
            'effect_sizes': self._calculate_effect_sizes(),
            'business_metrics': self._calculate_business_metrics()
        }
    
    def _extract_business_insights(self) -> Dict[str, Any]:
        """Extract actionable business insights."""
        insights = {
            'revenue_insights': self._analyze_revenue_patterns(),
            'customer_insights': self._analyze_customer_patterns(),
            'operational_insights': self._analyze_operational_patterns(),
            'growth_insights': self._analyze_growth_patterns(),
            'efficiency_insights': self._analyze_efficiency_patterns(),
            'risk_insights': self._analyze_risk_patterns()
        }
        
        # Remove empty insights
        return {k: v for k, v in insights.items() if v}
    
    def _generate_predictive_insights(self) -> Dict[str, Any]:
        """Generate predictive insights and forecasts."""
        predictions = {}
        
        # Time series forecasting (if date columns exist)
        date_cols = self.df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            predictions['time_series_forecasts'] = self._generate_time_series_forecasts()
        
        # Clustering insights
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            predictions['clustering_insights'] = self._perform_clustering_analysis()
        
        # Trend analysis
        predictions['trend_analysis'] = self._analyze_trends()
        
        # Correlation-based predictions
        predictions['correlation_predictions'] = self._generate_correlation_predictions()
        
        return predictions
    
    def _detect_anomalies(self) -> Dict[str, Any]:
        """Comprehensive anomaly detection."""
        anomalies = {}
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            data = self.df[col].dropna()
            if len(data) < 10:  # Need minimum data for meaningful anomaly detection
                continue
            
            # Multiple anomaly detection methods
            z_score_anomalies = self._detect_zscore_anomalies(data)
            iqr_anomalies = self._detect_iqr_anomalies(data)
            isolation_anomalies = self._detect_isolation_anomalies(data)
            
            anomalies[col] = {
                'z_score_anomalies': z_score_anomalies,
                'iqr_anomalies': iqr_anomalies,
                'isolation_anomalies': isolation_anomalies,
                'summary': self._summarize_anomalies(z_score_anomalies, iqr_anomalies, isolation_anomalies),
                'business_impact': self._assess_anomaly_business_impact(col, z_score_anomalies)
            }
        
        return anomalies
    
    def _generate_actionable_recommendations(self) -> List[Dict[str, Any]]:
        """Generate specific, actionable recommendations."""
        recommendations = []
        
        # Data quality recommendations
        quality_recs = self._generate_quality_recommendations()
        recommendations.extend(quality_recs)
        
        # Business optimization recommendations
        business_recs = self._generate_business_recommendations()
        recommendations.extend(business_recs)
        
        # Statistical recommendations
        stats_recs = self._generate_statistical_recommendations()
        recommendations.extend(stats_recs)
        
        # Prioritize recommendations
        for i, rec in enumerate(recommendations):
            rec['priority'] = self._calculate_recommendation_priority(rec)
            rec['id'] = i + 1
        
        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _create_data_story(self) -> Dict[str, Any]:
        """Create a compelling data narrative."""
        story = {
            'opening': self._generate_opening_narrative(),
            'key_chapters': self._generate_story_chapters(),
            'plot_points': self._identify_plot_points(),
            'conclusion': self._generate_conclusion(),
            'call_to_action': self._generate_call_to_action()
        }
        
        return story
    
    def _calculate_confidence_metrics(self) -> Dict[str, Any]:
        """Calculate confidence levels for various analyses."""
        return {
            'sample_size_adequacy': self._assess_sample_size(),
            'data_completeness_confidence': self._assess_completeness_confidence(),
            'statistical_power': self._calculate_statistical_power(),
            'analysis_reliability': self._assess_analysis_reliability(),
            'business_insight_confidence': self._assess_business_insight_confidence()
        }
    
    # Helper methods (implement key ones)
    
    def _identify_key_findings(self) -> List[str]:
        """Identify the most important findings."""
        findings = []
        
        # Data volume insights
        if len(self.df) > 10000:
            findings.append(f"Large dataset with {len(self.df):,} records provides high statistical power")
        elif len(self.df) < 100:
            findings.append(f"Small dataset with {len(self.df)} records - interpret results with caution")
        
        # Missing data insights
        missing_pct = (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
        if missing_pct > 20:
            findings.append(f"Significant data gaps ({missing_pct:.1f}% missing) require attention")
        elif missing_pct < 5:
            findings.append(f"High data completeness ({100-missing_pct:.1f}%) enables robust analysis")
        
        # Variability insights
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            high_var_cols = []
            for col in numeric_cols:
                cv = self.df[col].std() / self.df[col].mean() * 100
                if cv > 100:  # High coefficient of variation
                    high_var_cols.append(col)
            
            if high_var_cols:
                findings.append(f"High variability detected in {len(high_var_cols)} metrics suggests diverse patterns")
        
        return findings[:5]  # Return top 5 findings
    
    def _calculate_overall_quality_score(self) -> float:
        """Calculate overall data quality score."""
        score = 100.0
        
        # Penalize for missing data
        missing_pct = (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
        score -= missing_pct * 0.5
        
        # Penalize for duplicates
        duplicate_pct = (self.df.duplicated().sum() / len(self.df)) * 100
        score -= duplicate_pct * 2
        
        # Penalize for low variability
        if len(self.df.select_dtypes(include=[np.number]).columns) == 0:
            score -= 20
        
        return max(0, round(score, 1))
    
    def _assess_business_value(self) -> List[str]:
        """Assess potential business value of the dataset."""
        indicators = []
        
        # Look for business-relevant columns
        business_keywords = ['revenue', 'sales', 'profit', 'customer', 'user', 'conversion', 'cost', 'price']
        business_cols = [col for col in self.df.columns if any(keyword in col.lower() for keyword in business_keywords)]
        
        if business_cols:
            indicators.append(f"Contains {len(business_cols)} business-critical metrics")
        
        # Check for time series potential
        date_cols = self.df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            indicators.append("Time series analysis potential for trend forecasting")
        
        # Check for customer segmentation potential
        if len(self.df.select_dtypes(include=[np.number]).columns) >= 3:
            indicators.append("Customer segmentation and clustering opportunities")
        
        return indicators
    
    def _analyze_missing_pattern(self, column: str) -> str:
        """Analyze pattern of missing values."""
        missing_mask = self.df[column].isnull()
        
        if missing_mask.sum() == 0:
            return "no_missing"
        elif missing_mask.all():
            return "completely_missing"
        elif missing_mask.iloc[:len(missing_mask)//2].sum() > missing_mask.iloc[len(missing_mask)//2:].sum():
            return "front_heavy"
        elif missing_mask.iloc[:len(missing_mask)//2].sum() < missing_mask.iloc[len(missing_mask)//2:].sum():
            return "back_heavy"
        else:
            return "random_distribution"
    
    def _check_data_consistency(self) -> List[str]:
        """Check for data consistency issues."""
        issues = []
        
        # Check for mixed data types in object columns
        object_cols = self.df.select_dtypes(include=['object']).columns
        for col in object_cols:
            unique_types = set(type(x).__name__ for x in self.df[col].dropna())
            if len(unique_types) > 1:
                issues.append(f"Mixed data types in column '{col}': {', '.join(unique_types)}")
        
        # Check for unrealistic values
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if 'percentage' in col.lower() or 'percent' in col.lower():
                invalid_pct = self.df[(self.df[col] < 0) | (self.df[col] > 100)][col].count()
                if invalid_pct > 0:
                    issues.append(f"Invalid percentage values in '{col}': {invalid_pct} values outside 0-100 range")
        
        return issues
    
    def _analyze_distribution(self, data: pd.Series) -> Dict[str, Any]:
        """Analyze distribution characteristics."""
        # Normality tests
        shapiro_stat, shapiro_p = stats.shapiro(data[:5000] if len(data) > 5000 else data)
        
        # Distribution characteristics
        skewness = stats.skew(data)
        kurtosis = stats.kurtosis(data)
        
        distribution_type = "normal"
        if abs(skewness) > 1:
            distribution_type = "highly_skewed"
        elif abs(skewness) > 0.5:
            distribution_type = "moderately_skewed"
        
        if kurtosis > 3:
            distribution_type += "_heavy_tailed"
        elif kurtosis < -1:
            distribution_type += "_light_tailed"
        
        return {
            'normality_test': {
                'shapiro_statistic': shapiro_stat,
                'shapiro_p_value': shapiro_p,
                'is_normal': shapiro_p > 0.05
            },
            'distribution_type': distribution_type,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'interpretation': self._interpret_distribution(distribution_type, skewness, kurtosis)
        }
    
    def _interpret_distribution(self, dist_type: str, skewness: float, kurtosis: float) -> str:
        """Interpret distribution characteristics for business context."""
        interpretation = []
        
        if "normal" in dist_type:
            interpretation.append("Data follows a normal distribution, suitable for standard statistical tests")
        elif "skewed" in dist_type:
            if skewness > 0:
                interpretation.append("Right-skewed distribution indicates occasional high values")
            else:
                interpretation.append("Left-skewed distribution indicates occasional low values")
        
        if "heavy_tailed" in dist_type:
            interpretation.append("Heavy tails suggest presence of outliers requiring attention")
        
        return ". ".join(interpretation)
    
    def _generate_quality_recommendations(self) -> List[Dict[str, Any]]:
        """Generate data quality improvement recommendations."""
        recommendations = []
        
        # Missing value recommendations
        missing_analysis = self._assess_data_quality()['missing_values_analysis']
        for col, info in missing_analysis.items():
            if info['missing_percentage'] > 20:
                recommendations.append({
                    'type': 'data_quality',
                    'category': 'missing_values',
                    'title': f"Address missing values in {col}",
                    'description': f"Column '{col}' has {info['missing_percentage']:.1f}% missing values",
                    'action': "Consider imputation strategies or investigate data collection process",
                    'impact': 'high' if info['missing_percentage'] > 50 else 'medium',
                    'effort': 'medium'
                })
        
        return recommendations
    
    def _generate_business_recommendations(self) -> List[Dict[str, Any]]:
        """Generate business-focused recommendations."""
        recommendations = []
        
        # Look for revenue optimization opportunities
        revenue_cols = [col for col in self.df.columns if any(keyword in col.lower() for keyword in ['revenue', 'sales', 'profit'])]
        for col in revenue_cols:
            if self.df[col].dtype in ['int64', 'float64']:
                cv = self.df[col].std() / self.df[col].mean() * 100
                if cv > 50:
                    recommendations.append({
                        'type': 'business_optimization',
                        'category': 'revenue',
                        'title': f"Investigate {col} variability",
                        'description': f"High variability in {col} (CV: {cv:.1f}%) suggests optimization opportunities",
                        'action': "Analyze factors contributing to variance and standardize high-performing practices",
                        'impact': 'high',
                        'effort': 'medium'
                    })
        
        return recommendations
    
    def _generate_statistical_recommendations(self) -> List[Dict[str, Any]]:
        """Generate statistical analysis recommendations."""
        recommendations = []
        
        # Sample size recommendations
        if len(self.df) < 100:
            recommendations.append({
                'type': 'statistical',
                'category': 'sample_size',
                'title': "Increase sample size",
                'description': f"Current sample size ({len(self.df)}) may limit statistical power",
                'action': "Collect additional data to improve reliability of statistical inferences",
                'impact': 'high',
                'effort': 'high'
            })
        
        return recommendations
    
    def _calculate_recommendation_priority(self, recommendation: Dict[str, Any]) -> float:
        """Calculate priority score for recommendations."""
        impact_scores = {'high': 3, 'medium': 2, 'low': 1}
        effort_scores = {'low': 3, 'medium': 2, 'high': 1}  # Lower effort = higher priority
        
        impact = impact_scores.get(recommendation.get('impact', 'medium'), 2)
        effort = effort_scores.get(recommendation.get('effort', 'medium'), 2)
        
        return impact * effort
    
    # Additional helper methods would be implemented here...
    # (This is a substantial enhancement - the full implementation would be quite large)
    
    def _detect_outliers_iqr(self, data: pd.Series) -> List[float]:
        """Detect outliers using IQR method."""
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return data[(data < lower_bound) | (data > upper_bound)].tolist()
    
    # Placeholder implementations for remaining methods
    def _advanced_correlation_analysis(self): return {}
    def _perform_comprehensive_tests(self): return {}
    def _calculate_effect_sizes(self): return {}
    def _calculate_business_metrics(self): return {}
    def _analyze_revenue_patterns(self): return {}
    def _analyze_customer_patterns(self): return {}
    def _analyze_operational_patterns(self): return {}
    def _analyze_growth_patterns(self): return {}
    def _analyze_efficiency_patterns(self): return {}
    def _analyze_risk_patterns(self): return {}
    def _generate_time_series_forecasts(self): return {}
    def _perform_clustering_analysis(self): return {}
    def _analyze_trends(self): return {}
    def _generate_correlation_predictions(self): return {}
    def _detect_zscore_anomalies(self, data): return []
    def _detect_iqr_anomalies(self, data): return []
    def _detect_isolation_anomalies(self, data): return []
    def _summarize_anomalies(self, z, iqr, iso): return {}
    def _assess_anomaly_business_impact(self, col, anomalies): return {}
    def _generate_opening_narrative(self): return ""
    def _generate_story_chapters(self): return []
    def _identify_plot_points(self): return []
    def _generate_conclusion(self): return ""
    def _generate_call_to_action(self): return ""
    def _assess_sample_size(self): return {}
    def _assess_completeness_confidence(self): return {}
    def _calculate_statistical_power(self): return {}
    def _assess_analysis_reliability(self): return {}
    def _assess_business_insight_confidence(self): return {}
    def _interpret_statistics_business(self, col, stats): return ""
    def _detect_outliers_comprehensive(self): return {}
    def _analyze_data_types(self): return {}
    def _suggest_quality_improvements(self): return []
