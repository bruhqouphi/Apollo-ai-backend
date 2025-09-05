 
# app/core/analyzer.py
"""
Apollo AI Data Analyzer
Core class for statistical analysis, column type detection, and data profiling.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import warnings
from scipy import stats
from sklearn.preprocessing import LabelEncoder
import re
from datetime import datetime

# Import our custom models
from app.models.schemas import (
    ColumnType, ColumnInfo, NumericalStats, CategoricalStats, 
    CorrelationData, StatisticalTest
)
from app.config.settings import Settings

settings = Settings()

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class DataAnalyzer:
    """
    Comprehensive data analysis class for Apollo AI.
    
    Handles:
    - Column type detection
    - Statistical analysis
    - Data quality assessment
    - Missing value analysis
    - Correlation analysis
    - Statistical tests
    """
    
    def __init__(self, csv_file_path: str):
        """
        Initialize the analyzer with a CSV file.
        
        Args:
            csv_file_path: Path to the CSV file to analyze
        """
        self.file_path = Path(csv_file_path)
        self.df: Optional[pd.DataFrame] = None
        self.column_types: Dict[str, ColumnType] = {}
        self.analysis_results: Dict[str, Any] = {}
        
        # Load and validate the data
        self._load_data()
        self._detect_column_types()
    
    def _load_data(self) -> None:
        """Load CSV data with error handling."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(self.file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if self.df is None:
                raise ValueError("Could not read CSV file with any encoding")
            
            # Basic validation
            if self.df.empty:
                raise ValueError("CSV file is empty")
            
            if len(self.df.columns) < settings.MIN_COLUMNS:
                raise ValueError(f"CSV must have at least {settings.MIN_COLUMNS} columns")
            
            if len(self.df) > settings.MAX_ROWS:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Dataset has {len(self.df)} rows. Limiting to {settings.MAX_ROWS} for analysis.")
                self.df = self.df.head(settings.MAX_ROWS)
            
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {str(e)}")
    
    def _detect_column_types(self) -> None:
        """
        Automatically detect the type of each column.
        
        Types: numerical, categorical, datetime, boolean, text
        """
        for column in self.df.columns:
            col_data = self.df[column].dropna()
            
            if len(col_data) == 0:
                self.column_types[column] = ColumnType.text
                continue
            
            # Check for boolean
            if self._is_boolean_column(col_data):
                self.column_types[column] = ColumnType.boolean
            
            # Check for numerical FIRST (before datetime to avoid misclassification)
            elif self._is_numerical_column(col_data):
                self.column_types[column] = ColumnType.numeric
            
            # Check for datetime
            elif self._is_datetime_column(col_data):
                self.column_types[column] = ColumnType.datetime
            
            # Check for categorical (limited unique values)
            elif self._is_categorical_column(col_data):
                self.column_types[column] = ColumnType.categorical
            
            # Default to text
            else:
                self.column_types[column] = ColumnType.text
    
    def _is_boolean_column(self, col_data: pd.Series) -> bool:
        """Check if column contains boolean data."""
        unique_values = set(col_data.astype(str).str.lower().unique())
        boolean_patterns = [
            {'true', 'false'},
            {'yes', 'no'},
            {'y', 'n'},
            {'1', '0'},
            {'on', 'off'}
        ]
        return any(unique_values.issubset(pattern) for pattern in boolean_patterns)
    
    def _is_datetime_column(self, col_data: pd.Series) -> bool:
        """Check if column contains datetime data."""
        if col_data.dtype == 'datetime64[ns]':
            return True
        
        # Try to parse a sample of values as datetime
        sample_size = min(10, len(col_data))
        sample = col_data.sample(sample_size) if len(col_data) > sample_size else col_data
        
        try:
            parsed_dates = pd.to_datetime(sample, errors='raise')
            
            # Additional checks to avoid false positives
            # Check if the parsed dates make sense (not all the same year, reasonable range)
            if len(parsed_dates) > 0:
                years = parsed_dates.dt.year
                # If all years are the same or very close, it might be a numerical column
                if years.nunique() <= 1:
                    return False
                
                # Check if years are in a reasonable range (not all 1970s or future dates)
                if years.min() < 1900 or years.max() > 2030:
                    return False
                
                # Check if the original data looks more like dates than numbers
                sample_str = sample.astype(str)
                # Look for date-like patterns (contains slashes, dashes, or common date formats)
                date_patterns = ['/', '-', ':', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                               'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                has_date_patterns = any(pattern in sample_str.str.lower().str.cat() 
                                      for pattern in date_patterns)
                
                if not has_date_patterns:
                    return False
            
            return True
        except:
            return False
    
    def _is_numerical_column(self, col_data: pd.Series) -> bool:
        """Check if column contains numerical data."""
        if pd.api.types.is_numeric_dtype(col_data):
            return True
        
        # Try to convert to numeric
        try:
            pd.to_numeric(col_data, errors='raise')
            return True
        except:
            return False
    
    def _is_categorical_column(self, col_data: pd.Series) -> bool:
        """Check if column should be treated as categorical."""
        unique_count = col_data.nunique()
        total_count = len(col_data)
        
        # If less than 50% unique values and under max categories, treat as categorical
        if unique_count <= settings.MAX_CATEGORIES and unique_count / total_count < 0.5:
            return True
        
        return False
    
    def get_column_info(self) -> List[ColumnInfo]:
        """
        Get detailed information about each column.
        
        Returns:
            List of ColumnInfo objects with metadata for each column
        """
        columns_info = []
        
        for column in self.df.columns:
            col_data = self.df[column]
            missing_count = col_data.isnull().sum()
            missing_percentage = (missing_count / len(col_data)) * 100
            
            # Get sample values (non-null)
            sample_values = col_data.dropna().head(5).tolist()
            
            column_info = ColumnInfo(
                name=column,
                dtype=self.column_types[column],
                non_null=int(len(col_data) - missing_count),
                nulls=int(missing_count),
                unique=int(col_data.nunique()),
                sample_values=sample_values
            )
            
            columns_info.append(column_info)
        
        return columns_info
    
    def analyze_numerical_columns(self) -> List[NumericalStats]:
        """
        Perform statistical analysis on numerical columns.
        
        Returns:
            List of NumericalStats objects with statistical summaries
        """
        numerical_stats = []
        
        numerical_columns = [
            col for col, col_type in self.column_types.items() 
            if col_type == ColumnType.numeric
        ]
        
        for column in numerical_columns:
            col_data = pd.to_numeric(self.df[column], errors='coerce').dropna()
            
            if len(col_data) == 0:
                continue
            
            # Basic statistics
            stats_dict = {
                'count': int(len(col_data)),
                'mean': float(col_data.mean()),
                'std': float(col_data.std()),
                'min': float(col_data.min()),
                'q25': float(col_data.quantile(0.25)),
                'median': float(col_data.median()),
                'q75': float(col_data.quantile(0.75)),
                'max': float(col_data.max())
            }
            
            # Outlier detection using IQR method
            outliers = self._detect_outliers(col_data)
            
            numerical_stat = NumericalStats(
                column=column,
                count=int(len(col_data)),
                mean=float(col_data.mean()) if len(col_data) > 0 else None,
                std=float(col_data.std()) if len(col_data) > 0 else None,
                min=float(col_data.min()) if len(col_data) > 0 else None,
                q1=float(col_data.quantile(0.25)) if len(col_data) > 0 else None,
                median=float(col_data.median()) if len(col_data) > 0 else None,
                q3=float(col_data.quantile(0.75)) if len(col_data) > 0 else None,
                max=float(col_data.max()) if len(col_data) > 0 else None,
                skewness=float(col_data.skew()) if len(col_data) > 0 else None,
                kurtosis=float(col_data.kurtosis()) if len(col_data) > 0 else None,
                iqr=float(col_data.quantile(0.75) - col_data.quantile(0.25)) if len(col_data) > 0 else None,
                outliers=outliers[:10] if len(outliers) > 0 else None  # Limit to first 10 outliers
            )
            
            numerical_stats.append(numerical_stat)
        
        return numerical_stats
    
    def analyze_categorical_columns(self) -> List[CategoricalStats]:
        """
        Perform analysis on categorical columns.
        
        Returns:
            List of CategoricalStats objects with categorical summaries
        """
        categorical_stats = []
        
        categorical_columns = [
            col for col, col_type in self.column_types.items() 
            if col_type in [ColumnType.categorical, ColumnType.boolean]
        ]
        
        for column in categorical_columns:
            col_data = self.df[column].dropna()
            
            if len(col_data) == 0:
                continue
            
            value_counts = col_data.value_counts()
            
            categorical_stat = CategoricalStats(
                column=column,
                count=int(len(col_data)),
                unique=int(col_data.nunique()),
                top=str(value_counts.index[0]) if len(value_counts) > 0 else None,
                freq=int(value_counts.iloc[0]) if len(value_counts) > 0 else None,
                distribution={str(k): int(v) for k, v in value_counts.head(20).items()} if len(value_counts) > 0 else None  # Top 20 categories
            )
            
            categorical_stats.append(categorical_stat)
        
        return categorical_stats
    
    def _detect_outliers(self, data: pd.Series, method: str = "iqr") -> List[float]:
        """
        Detect outliers in numerical data.
        
        Args:
            data: Numerical data series
            method: Detection method ('iqr' or 'zscore')
            
        Returns:
            List of outlier values
        """
        if method == "iqr":
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = data[(data < lower_bound) | (data > upper_bound)]
        
        elif method == "zscore":
            z_scores = np.abs(stats.zscore(data))
            outliers = data[z_scores > 3]
        
        else:
            return []
        
        return outliers.tolist()
    
    def analyze_correlations(self) -> Optional[CorrelationData]:
        """
        Perform correlation analysis on numerical columns.
        
        Returns:
            CorrelationData object with correlation matrix and insights
        """
        numerical_columns = [
            col for col, col_type in self.column_types.items() 
            if col_type == ColumnType.numeric
        ]
        
        if len(numerical_columns) < 2:
            return None
        
        # Get numerical data
        numerical_data = self.df[numerical_columns].select_dtypes(include=[np.number])
        
        if numerical_data.empty:
            return None
        
        # Calculate correlation matrix
        corr_matrix = numerical_data.corr()
        
        # Convert to dictionary format
        corr_dict = {}
        for col1 in corr_matrix.columns:
            corr_dict[col1] = {}
            for col2 in corr_matrix.columns:
                corr_dict[col1][col2] = float(corr_matrix.loc[col1, col2])
        
        # Find strong correlations (> 0.7 or < -0.7)
        strong_correlations = []
        for i, col1 in enumerate(corr_matrix.columns):
            for j, col2 in enumerate(corr_matrix.columns):
                if i < j:  # Avoid duplicates
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': round(float(corr_value), 3),
                            'strength': 'strong positive' if corr_value > 0 else 'strong negative'
                        })
        
        return CorrelationData(
            method="pearson",
            matrix=corr_dict,
            strong_correlations=strong_correlations
        )
    
    def perform_statistical_tests(self) -> List[StatisticalTest]:
        """
        Perform various statistical tests on the data.
        
        Returns:
            List of StatisticalTest objects with test results
        """
        tests = []
        
        # Get numerical and categorical columns
        numerical_cols = [col for col, t in self.column_types.items() if t == ColumnType.numeric]
        categorical_cols = [col for col, t in self.column_types.items() if t == ColumnType.categorical]
        
        # Normality tests for numerical columns
        for col in numerical_cols:
            data = pd.to_numeric(self.df[col], errors='coerce').dropna()
            if len(data) > 3:
                try:
                    statistic, p_value = stats.shapiro(data.sample(min(5000, len(data))))
                    
                    test = StatisticalTest(
                        test_name=f"Shapiro-Wilk Normality Test ({col})",
                        statistic=float(statistic),
                        p_value=float(p_value),
                        significant=p_value < settings.SIGNIFICANCE_LEVEL,
                        interpretation=f"Data is {'not ' if p_value < settings.SIGNIFICANCE_LEVEL else ''}normally distributed"
                    )
                    tests.append(test)
                except Exception:
                    pass
        
        # Chi-square test for categorical columns
        if len(categorical_cols) >= 2:
            for i, col1 in enumerate(categorical_cols):
                for col2 in categorical_cols[i+1:]:
                    try:
                        contingency_table = pd.crosstab(self.df[col1], self.df[col2])
                        if contingency_table.shape[0] > 1 and contingency_table.shape[1] > 1:
                            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
                            
                            test = StatisticalTest(
                                test_name=f"Chi-square Independence Test ({col1} vs {col2})",
                                statistic=float(chi2),
                                p_value=float(p_value),
                                significant=p_value < settings.SIGNIFICANCE_LEVEL,
                                interpretation=f"Variables are {'not ' if p_value >= settings.SIGNIFICANCE_LEVEL else ''}independent"
                            )
                            tests.append(test)
                    except Exception:
                        pass
        
        return tests
    
    def calculate_data_quality_score(self) -> Tuple[float, List[str]]:
        """
        Calculate overall data quality score and recommendations.
        
        Returns:
            Tuple of (quality_score, recommendations_list)
        """
        score = 100.0
        recommendations = []
        
        # Check missing values
        missing_percentages = []
        for col in self.df.columns:
            missing_pct = (self.df[col].isnull().sum() / len(self.df)) * 100
            missing_percentages.append(missing_pct)
            
            if missing_pct > 50:
                score -= 15
                recommendations.append(f"Column '{col}' has {missing_pct:.1f}% missing values - consider imputation or removal")
            elif missing_pct > 20:
                score -= 5
                recommendations.append(f"Column '{col}' has {missing_pct:.1f}% missing values - review data collection")
        
        # Check for duplicate rows
        duplicate_count = self.df.duplicated().sum()
        if duplicate_count > 0:
            duplicate_pct = (duplicate_count / len(self.df)) * 100
            score -= min(20, duplicate_pct)
            recommendations.append(f"Found {duplicate_count} duplicate rows ({duplicate_pct:.1f}%) - consider removing duplicates")
        
        # Check column variety
        if len(self.column_types) < 3:
            score -= 10
            recommendations.append("Dataset has limited column variety - consider adding more features")
        
        # Check data volume
        if len(self.df) < 100:
            score -= 15
            recommendations.append("Small dataset size - results may not be statistically significant")
        
        # Add positive recommendations
        if score > 80:
            recommendations.append("Overall good data quality - ready for analysis")
        elif score > 60:
            recommendations.append("Moderate data quality - some improvements recommended")
        else:
            recommendations.append("Data quality needs improvement before reliable analysis")
        
        return max(0, score), recommendations
    
    def debug_column_types(self) -> Dict[str, Any]:
        """
        Debug method to see detailed information about column type detection.
        
        Returns:
            Dictionary with debugging information for each column
        """
        debug_info = {}
        
        for column in self.df.columns:
            col_data = self.df[column].dropna()
            
            debug_info[column] = {
                'detected_type': self.column_types[column].value,
                'sample_values': col_data.head(5).tolist(),
                'unique_count': col_data.nunique(),
                'dtype': str(col_data.dtype),
                'is_boolean': self._is_boolean_column(col_data),
                'is_numerical': self._is_numerical_column(col_data),
                'is_datetime': self._is_datetime_column(col_data),
                'is_categorical': self._is_categorical_column(col_data),
                'total_rows': len(self.df),
                'non_null_rows': len(col_data)
            }
        
        return debug_info
    
    def override_column_types(self, column_type_overrides: Dict[str, ColumnType]) -> None:
        """
        Manually override detected column types.
        
        Args:
            column_type_overrides: Dictionary mapping column names to desired ColumnType
        """
        import logging
        logger = logging.getLogger(__name__)
        for column, col_type in column_type_overrides.items():
            if column in self.df.columns:
                self.column_types[column] = col_type
                logger.info(f"Overridden column '{column}' type to {col_type.value}")
            else:
                logger.warning(f"Column '{column}' not found in dataset")
    
    def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        Perform data analysis based on provided options.
        
        Args:
            **kwargs: Analysis options including:
                - include_correlation: bool
                - include_outliers: bool
                - include_statistical_tests: bool
                - outlier_method: str
                - confidence_level: float
                
        Returns:
            Dictionary with analysis results
        """
        results = {}
        
        # Basic dataset info
        results['basic_info'] = {
            'filename': self.file_path.name,
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            'column_types_summary': {
                col_type.value: sum(1 for t in self.column_types.values() if t == col_type)
                for col_type in ColumnType
            }
        }
        
        # Column information
        results['columns_info'] = [col.dict() for col in self.get_column_info()]
        
        # Descriptive statistics
        results['descriptive_stats'] = {
            'numerical': [stat.dict() for stat in self.analyze_numerical_columns()],
            'categorical': [stat.dict() for stat in self.analyze_categorical_columns()]
        }
        
        # Correlation analysis (if requested)
        if kwargs.get('include_correlation', True):
            correlation_analysis = self.analyze_correlations()
            results['correlation_analysis'] = correlation_analysis.dict() if correlation_analysis else None
        
        # Outlier analysis (if requested)
        if kwargs.get('include_outliers', True):
            outlier_method = kwargs.get('outlier_method', 'iqr')
            outlier_results = {}
            for col in self.df.select_dtypes(include=[np.number]).columns:
                outliers = self._detect_outliers(self.df[col], outlier_method)
                if outliers:
                    outlier_results[col] = outliers
            results['outlier_analysis'] = outlier_results
        
        # Statistical tests (if requested)
        if kwargs.get('include_statistical_tests', False):
            statistical_tests = self.perform_statistical_tests()
            results['statistical_tests'] = [test.dict() for test in statistical_tests]
        
        # Data quality assessment
        quality_score, recommendations = self.calculate_data_quality_score()
        results['data_quality'] = {
            'score': round(quality_score, 1),
            'recommendations': recommendations
        }
        
        return results

    def get_complete_analysis(self) -> Dict[str, Any]:
        """
        Perform complete data analysis and return results.
        
        Returns:
            Dictionary with all analysis results
        """
        # Basic dataset info
        dataset_info = {
            'filename': self.file_path.name,
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            'column_types_summary': {
                col_type.value: sum(1 for t in self.column_types.values() if t == col_type)
                for col_type in ColumnType
            }
        }
        
        # Perform all analyses
        columns_info = self.get_column_info()
        numerical_stats = self.analyze_numerical_columns()
        categorical_stats = self.analyze_categorical_columns()
        correlation_analysis = self.analyze_correlations()
        statistical_tests = self.perform_statistical_tests()
        quality_score, recommendations = self.calculate_data_quality_score()
        
        return {
            'dataset_info': dataset_info,
            'columns_info': [col.dict() for col in columns_info],
            'numerical_stats': [stat.dict() for stat in numerical_stats],
            'categorical_stats': [stat.dict() for stat in categorical_stats],
            'correlation_analysis': correlation_analysis.dict() if correlation_analysis else None,
            'statistical_tests': [test.dict() for test in statistical_tests],
            'data_quality_score': round(quality_score, 1),
            'recommendations': recommendations
        }
    
    def get_structured_business_analysis(self) -> Dict[str, Any]:
        """
        Get structured analysis specifically formatted for business insights and LLM consumption.
        This method provides concrete numbers and patterns that can be fed to LLM for 
        specialized data analysis insights.
        
        Returns:
            Structured business analysis with concrete metrics
        """
        analysis = {}
        
        # 1. Dataset Overview
        analysis["dataset_summary"] = {
            "total_records": len(self.df),
            "total_features": len(self.df.columns),
            "memory_usage_mb": round(self.df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "data_types": {
                "numerical": len([col for col in self.column_types if self.column_types[col] == ColumnType.numeric]),
                "categorical": len([col for col in self.column_types if self.column_types[col] == ColumnType.categorical]),
                "datetime": len([col for col in self.column_types if self.column_types[col] == ColumnType.datetime]),
                "boolean": len([col for col in self.column_types if self.column_types[col] == ColumnType.boolean])
            }
        }
        
        # 2. Detailed Numerical Analysis
        numerical_cols = [col for col in self.df.columns if self.column_types[col] == ColumnType.numeric]
        if numerical_cols:
            analysis["numerical_insights"] = {}
            
            for col in numerical_cols:
                col_data = self.df[col].dropna()
                if len(col_data) > 0:
                    analysis["numerical_insights"][col] = {
                        "mean": round(col_data.mean(), 2),
                        "median": round(col_data.median(), 2),
                        "std": round(col_data.std(), 2),
                        "min": round(col_data.min(), 2),
                        "max": round(col_data.max(), 2),
                        "range": round(col_data.max() - col_data.min(), 2),
                        "coefficient_of_variation": round((col_data.std() / col_data.mean()) * 100, 2) if col_data.mean() != 0 else 0,
                        "skewness": round(col_data.skew(), 2),
                        "kurtosis": round(col_data.kurtosis(), 2),
                        "percentile_25": round(col_data.quantile(0.25), 2),
                        "percentile_75": round(col_data.quantile(0.75), 2),
                        "outlier_count": len(self._detect_outliers(col_data)),
                        "missing_count": self.df[col].isnull().sum(),
                        "missing_percentage": round((self.df[col].isnull().sum() / len(self.df)) * 100, 2)
                    }
        
        # 3. Categorical Analysis
        categorical_cols = [col for col in self.df.columns if self.column_types[col] == ColumnType.categorical]
        if categorical_cols:
            analysis["categorical_insights"] = {}
            
            for col in categorical_cols:
                value_counts = self.df[col].value_counts()
                analysis["categorical_insights"][col] = {
                    "unique_values": self.df[col].nunique(),
                    "most_frequent": value_counts.index[0] if len(value_counts) > 0 else None,
                    "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    "most_frequent_percentage": round((value_counts.iloc[0] / len(self.df)) * 100, 2) if len(value_counts) > 0 else 0,
                    "least_frequent": value_counts.index[-1] if len(value_counts) > 0 else None,
                    "least_frequent_count": int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
                    "missing_count": self.df[col].isnull().sum(),
                    "missing_percentage": round((self.df[col].isnull().sum() / len(self.df)) * 100, 2),
                    "top_5_values": dict(value_counts.head().to_dict())
                }
        
        # 4. Correlation Analysis
        if len(numerical_cols) > 1:
            corr_matrix = self.df[numerical_cols].corr()
            analysis["correlation_insights"] = {}
            
            # Find strongest correlations
            correlations = []
            for i in range(len(numerical_cols)):
                for j in range(i+1, len(numerical_cols)):
                    corr_value = corr_matrix.iloc[i, j]
                    if not np.isnan(corr_value):
                        correlations.append({
                            "variable_1": numerical_cols[i],
                            "variable_2": numerical_cols[j],
                            "correlation": round(corr_value, 3),
                            "strength": self._interpret_correlation_strength(abs(corr_value)),
                            "direction": "positive" if corr_value > 0 else "negative"
                        })
            
            # Sort by absolute correlation strength
            correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
            analysis["correlation_insights"]["strongest_correlations"] = correlations[:10]
            analysis["correlation_insights"]["average_correlation"] = round(np.mean([abs(c["correlation"]) for c in correlations]), 3)
        
        # 5. Data Quality Assessment
        total_cells = len(self.df) * len(self.df.columns)
        missing_cells = self.df.isnull().sum().sum()
        
        analysis["data_quality"] = {
            "completeness_percentage": round(((total_cells - missing_cells) / total_cells) * 100, 2),
            "missing_values_total": int(missing_cells),
            "columns_with_missing_data": int((self.df.isnull().sum() > 0).sum()),
            "duplicate_rows": int(self.df.duplicated().sum()),
            "columns_with_outliers": len([col for col in numerical_cols if len(self._detect_outliers(self.df[col].dropna())) > 0])
        }
        
        # 6. Business Insights Patterns
        analysis["business_patterns"] = self._identify_business_patterns()
        
        return analysis
    
    def _interpret_correlation_strength(self, abs_corr: float) -> str:
        """Interpret correlation strength in business terms."""
        if abs_corr >= 0.8:
            return "very_strong"
        elif abs_corr >= 0.6:
            return "strong"
        elif abs_corr >= 0.4:
            return "moderate"
        elif abs_corr >= 0.2:
            return "weak"
        else:
            return "very_weak"
    
    def _identify_business_patterns(self) -> Dict[str, Any]:
        """Identify key business patterns in the data."""
        patterns = {
            "high_variance_features": [],
            "potential_target_variables": [],
            "features_with_extreme_values": [],
            "categorical_concentration": {}
        }
        
        numerical_cols = [col for col in self.df.columns if self.column_types[col] == ColumnType.numeric]
        categorical_cols = [col for col in self.df.columns if self.column_types[col] == ColumnType.categorical]
        
        # High variance features (potential key drivers)
        for col in numerical_cols:
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                cv = (col_data.std() / col_data.mean()) * 100 if col_data.mean() != 0 else 0
                if cv > 50:  # High coefficient of variation
                    patterns["high_variance_features"].append({
                        "feature": col,
                        "coefficient_of_variation": round(cv, 2)
                    })
        
        # Potential target variables (numerical columns with specific patterns)
        for col in numerical_cols:
            col_name_lower = col.lower()
            if any(keyword in col_name_lower for keyword in ['price', 'cost', 'value', 'amount', 'revenue', 'profit', 'rating', 'score']):
                patterns["potential_target_variables"].append(col)
        
        # Features with extreme values
        for col in numerical_cols:
            outlier_count = len(self._detect_outliers(self.df[col].dropna()))
            if outlier_count > len(self.df) * 0.05:  # More than 5% outliers
                patterns["features_with_extreme_values"].append({
                    "feature": col,
                    "outlier_count": outlier_count,
                    "outlier_percentage": round((outlier_count / len(self.df)) * 100, 2)
                })
        
        # Categorical concentration (how concentrated the categorical data is)
        for col in categorical_cols:
            value_counts = self.df[col].value_counts()
            if len(value_counts) > 0:
                concentration = value_counts.iloc[0] / len(self.df)
                patterns["categorical_concentration"][col] = {
                    "top_category_concentration": round(concentration * 100, 2),
                    "diversity_score": round(1 - concentration, 2)
                }
        
        return patterns