from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ------------------ CORE ENUMS ------------------
class ColumnType(str, Enum):
    numeric = "numeric"
    categorical = "categorical"
    datetime = "datetime"
    text = "text"
    boolean = "boolean"

class ChartType(str, Enum):
    """Available chart types for visualization."""
    histogram = "histogram"
    bar_chart = "bar_chart"
    line_chart = "line_chart"
    scatter_plot = "scatter_plot"
    box_plot = "box_plot"
    pie_chart = "pie_chart"
    heatmap = "heatmap"
    violin_plot = "violin_plot"
    density_plot = "density_plot"
    stacked_bar = "stacked_bar"
    grouped_bar = "grouped_bar"
    area_chart = "area_chart"


# ------------------ AUTHENTICATION SCHEMAS ------------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    email: Optional[str] = None


# ------------------ EXTRA TYPES USED BY analyzer.py ------------------
from enum import Enum
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class ColumnInfo(BaseModel):
    name: str
    dtype: ColumnType
    non_null: Optional[int] = None
    nulls: Optional[int] = None
    unique: Optional[int] = None
    sample_values: Optional[List[Any]] = None

class NumericalStats(BaseModel):
    column: str
    count: int
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    q1: Optional[float] = None
    median: Optional[float] = None
    q3: Optional[float] = None
    max: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    iqr: Optional[float] = None
    outliers: Optional[List[float]] = None

class CategoricalStats(BaseModel):
    column: str
    count: int
    unique: int
    top: Optional[str] = None
    freq: Optional[int] = None
    distribution: Optional[Dict[str, int]] = None

class CorrelationData(BaseModel):
    method: str  # e.g. "pearson", "spearman", "kendall"
    matrix: Dict[str, Dict[str, float]]

class StatisticalTest(BaseModel):
    test_name: str
    column: Optional[str] = None
    target: Optional[str] = None
    statistic: Optional[float] = None
    p_value: Optional[float] = None
    df: Optional[int] = None
    conclusion: Optional[str] = None
    significant: Optional[bool] = None
    interpretation: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

# ------------------ General Responses ------------------
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime

# ------------------ Upload ------------------
class UploadResponse(BaseModel):
    success: bool = True
    message: str
    timestamp: datetime
    file_id: str
    filename: str
    file_size: str
    file_size_bytes: int
    rows_count: int
    columns_count: int
    columns: List[str]

class FileInfo(BaseModel):
    file_id: str
    filename: str
    file_size: str
    file_size_bytes: int
    rows_count: int
    columns_count: int
    columns: List[str]
    upload_time: datetime
    user_id: str

class ColumnStats(BaseModel):
    name: str
    dtype: ColumnType
    count: int
    missing: int = 0
    unique: Optional[int] = None
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    top: Optional[str] = None
    freq: Optional[int] = None

class DatasetSummary(BaseModel):
    rows: int
    cols: int
    columns: List[ColumnStats]

class AnalysisRequest(BaseModel):
    file_id: str
    include_correlation: bool = True
    include_outliers: bool = True
    include_statistical_tests: bool = False
    outlier_method: str = "iqr"
    confidence_level: float = 0.95
    target_columns: Optional[List[str]] = None

class AnalysisResponse(BaseModel):
    file_id: str
    summary: DatasetSummary
    analysis_results: Dict[str, Any]
    analysis_timestamp: datetime
    processing_time_seconds: float
    message: str

# ------------------ Visualization ------------------
class VisualizationRequest(BaseModel):
    file_id: str
    chart_type: str
    column: Optional[str] = None
    columns: Optional[List[str]] = None
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    bins: Optional[int] = 20
    top_n: Optional[int] = 10

class VisualizationResponse(BaseModel):
    file_id: str
    chart_type: str
    chart_data: Dict[str, Any]
    available_visualizations: List[str]
    recommendations: List[str]
    generation_timestamp: datetime
    message: str

# ------------------ Report Generation ------------------
class AnalysisResult(BaseModel):
    """Result model for analysis data used in report generation"""
    file_id: str
    summary: DatasetSummary
    analysis_results: Dict[str, Any]
    analysis_timestamp: datetime
    processing_time_seconds: float
    message: str

class VisualizationResult(BaseModel):
    """Result model for visualization data used in report generation"""
    file_id: str
    chart_type: str
    chart_data: Dict[str, Any]
    available_visualizations: List[str]
    recommendations: List[str]
    generation_timestamp: datetime
    message: str

class InsightResult(BaseModel):
    """Result model for AI insights used in report generation"""
    executive_summary: str
    key_findings: List[str]
    detailed_insights: Dict[str, Any]
    recommendations: List[str]
    data_quality_assessment: str
    statistical_significance: Dict[str, Any]
    visualizations_explained: Dict[str, Any]
    next_steps: List[str]
    confidence_level: str
    generation_metadata: Dict[str, Any]

# ------------------ Insight Generation ------------------
class InsightRequest(BaseModel):
    file_id: str
    analysis_id: Optional[str] = None
    include_executive_summary: bool = True
    include_recommendations: bool = True
    include_next_steps: bool = True
    user_context: Optional[str] = None
    analysis_type: str = "comprehensive"  # Type of analysis (summary, trends, anomalies, comprehensive)
    processing_method: str = "hybrid_local"  # hybrid_local, local_only, enhanced_local

class InsightResponse(BaseModel):
    file_id: str
    analysis_type: str
    processing_method: str
    insights: InsightResult
    generation_timestamp: datetime
    processing_time_seconds: float
    message: str

# ------------------ Visualization Schemas ------------------
class ChartRequest(BaseModel):
    chart_type: str
    columns: List[str]
    options: Optional[Dict[str, Any]] = None

class ChartResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    file_path: Optional[str] = None
    image_base64: Optional[str] = None
    download_url: Optional[str] = None
    chart_type: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None

class ChartRecommendationResponse(BaseModel):
    success: bool
    recommendations: Dict[str, Any]
    total_columns: int
    column_types: Dict[str, ColumnType]
