"""
Apollo AI FastAPI Backend
Main application with endpoints for CSV upload, data analysis, and visualization.
"""

import os
import uuid
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import our custom modules
from app.config.settings import Settings
from app.models.schemas import (
    HealthResponse, 
    UploadResponse, 
    AnalysisRequest, 
    AnalysisResponse,
    VisualizationRequest,
    VisualizationResponse,
    ErrorResponse,
    ColumnType,
    ColumnStats,
    DatasetSummary,
    InsightRequest,
    InsightResponse
)
from app.core.analyzer import DataAnalyzer
from app.core.visualizer import DataVisualizer
from app.core.insight_generator import InsightGenerator
from app.api.endpoints.visualization import router as visualization_router

# Initialize settings
settings = Settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Intelligent no-code platform for data analysis and visualization",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Create required directories
for directory in [settings.UPLOAD_DIR, settings.EXPORT_DIR, settings.STATIC_DIR]:
    Path(directory).mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Include visualization router
app.include_router(visualization_router)

# Global storage for uploaded files (in production, use database or Redis)
uploaded_files: Dict[str, Dict[str, Any]] = {}


def validate_file(file: UploadFile) -> None:
    """
    Validate uploaded file for size and format
    
    Args:
        file: Uploaded file object
        
    Raises:
        HTTPException: If file validation fails
    """
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Supported: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check file size (reset file pointer first)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )


def load_dataframe(file_id: str) -> pd.DataFrame:
    """
    Load DataFrame from stored file information
    
    Args:
        file_id: Unique file identifier
        
    Returns:
        Pandas DataFrame
        
    Raises:
        HTTPException: If file not found or loading fails
    """
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[file_id]
    file_path = file_info["file_path"]
    
    try:
        # Load CSV with error handling
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Validate data size
        if len(df) > settings.MAX_ROWS:
            raise HTTPException(
                status_code=413,
                detail=f"Dataset too large. Maximum rows: {settings.MAX_ROWS}"
            )
        
        if len(df.columns) < settings.MIN_COLUMNS:  # Changed from > to <
            raise HTTPException(
                status_code=400,  # Changed from 413 to 400
                detail=f"Dataset must have at least {settings.MIN_COLUMNS} columns"  # Updated error message
            )
        
        return df
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading file: {str(e)}")


def get_file_path(file_id: str) -> str:
    """
    Get file path from stored file information
    
    Args:
        file_id: Unique file identifier
        
    Returns:
        File path string
        
    Raises:
        HTTPException: If file not found
    """
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    return uploaded_files[file_id]["file_path"]


@app.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Application status and metadata
    """
    return HealthResponse(
        status="healthy",
        message="Apollo AI Backend is running",
        version=settings.VERSION,
        timestamp=datetime.now()
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload CSV file for analysis
    
    Args:
        file: CSV file upload
        
    Returns:
        Upload confirmation with file metadata
    """
    try:
        # Validate file
        validate_file(file)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create safe filename
        safe_filename = f"{file_id}_{file.filename}"
        file_path = Path(settings.UPLOAD_DIR) / safe_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Load and validate CSV
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Store file information
        uploaded_files[file_id] = {
            "original_filename": file.filename,
            "file_path": str(file_path),
            "upload_time": datetime.now(),
            "file_size": len(content),
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist()
        }
        
        # Return the correct response format
        return UploadResponse(
            success=True,
            message="File uploaded successfully",
            timestamp=datetime.now(),
            file_id=file_id,
            filename=file.filename,
            file_size=str(len(content)),  # Convert to string
            rows_count=len(df),           # Fixed field name
            columns_count=len(df.columns), # Fixed field name
            columns=df.columns.tolist()    # Fixed field name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest):
    """
    Perform statistical analysis on uploaded CSV
    
    Args:
        request: Analysis configuration
        
    Returns:
        Comprehensive statistical analysis results
    """
    try:
        # Get file path instead of loading DataFrame first
        file_path = get_file_path(request.file_id)
        
        # Initialize analyzer with file path (as your DataAnalyzer expects)
        analyzer = DataAnalyzer(file_path)
        
        # Configure analysis options
        analysis_options = {
            "include_correlation": request.include_correlation,
            "include_outliers": request.include_outliers,
            "include_statistical_tests": request.include_statistical_tests,
            "outlier_method": request.outlier_method,
            "confidence_level": request.confidence_level
        }
        
        # Perform analysis
        if request.target_columns:
            # Load DataFrame for column validation
            df = load_dataframe(request.file_id)
            
            # Filter DataFrame to only include target columns
            valid_columns = [col for col in request.target_columns if col in df.columns]
            if len(valid_columns) < 2:
                raise HTTPException(
                    status_code=400, 
                    detail=f"At least 2 valid columns required. Found: {len(valid_columns)}"
                )
            
            # Create filtered DataFrame with target columns
            filtered_df = df[valid_columns]
            temp_file = f"temp_{request.file_id}_filtered.csv"
            temp_path = Path(settings.UPLOAD_DIR) / temp_file
            
            # Save filtered DataFrame to temporary file
            filtered_df.to_csv(temp_path, index=False)
            
            # Analyze with temporary file
            filtered_analyzer = DataAnalyzer(str(temp_path))
            analysis_results = filtered_analyzer.analyze(**analysis_options)
            
            # Clean up temporary file
            os.remove(temp_path)
        else:
            # Full dataset analysis
            analysis_results = analyzer.analyze(**analysis_options)
        
        # Create DatasetSummary from analyzer results
        df = load_dataframe(request.file_id)
        column_stats = []
        
        for col in df.columns:
            col_data = df[col]
            col_type = analyzer.column_types.get(col, ColumnType.text)
            
            stats = ColumnStats(
                name=col,
                dtype=col_type,
                count=len(col_data),
                missing=col_data.isnull().sum(),
                unique=col_data.nunique(),
                mean=col_data.mean() if col_type == ColumnType.numeric else None,
                std=col_data.std() if col_type == ColumnType.numeric else None,
                min=col_data.min() if col_type == ColumnType.numeric else None,
                max=col_data.max() if col_type == ColumnType.numeric else None,
                top=col_data.mode().iloc[0] if col_type == ColumnType.categorical and len(col_data.mode()) > 0 else None,
                freq=col_data.value_counts().iloc[0] if col_type == ColumnType.categorical else None
            )
            column_stats.append(stats)
        
        summary = DatasetSummary(
            rows=len(df),
            cols=len(df.columns),
            columns=column_stats
        )
        
        return AnalysisResponse(
            file_id=request.file_id,
            summary=summary,
            analysis_results=analysis_results,
            analysis_timestamp=datetime.now(),
            processing_time_seconds=0.0,  # Could add timing logic
            message="Analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/visualize", response_model=VisualizationResponse)
async def generate_visualization(request: VisualizationRequest):
    """
    Generate Chart.js compatible visualization data
    
    Args:
        request: Visualization configuration
        
    Returns:
        Chart.js ready visualization data
    """
    try:
        # Load DataFrame for visualizer (assuming DataVisualizer accepts DataFrame)
        df = load_dataframe(request.file_id)
        
        # Initialize visualizer
        visualizer = DataVisualizer(df)
        
        # Generate requested visualization
        chart_data = None
        
        if request.chart_type == "histogram":
            if not request.column:
                raise HTTPException(status_code=400, detail="Column required for histogram")
            chart_data = visualizer.generate_histogram(
                column=request.column,
                bins=request.bins or 20
            )
            
        elif request.chart_type == "boxplot":
            columns = request.columns or visualizer.numeric_columns[:5]  # Limit to 5 columns
            chart_data = visualizer.generate_boxplot(columns=columns)
            
        elif request.chart_type == "bar":
            if not request.column:
                raise HTTPException(status_code=400, detail="Column required for bar chart")
            chart_data = visualizer.generate_bar_chart(
                column=request.column,
                top_n=request.top_n or 10
            )
            
        elif request.chart_type == "scatter":
            if not request.x_column or not request.y_column:
                raise HTTPException(status_code=400, detail="x_column and y_column required for scatter plot")
            chart_data = visualizer.generate_scatter_plot(
                x_column=request.x_column,
                y_column=request.y_column,
                color_column=request.color_column
            )
            
        elif request.chart_type == "heatmap":
            columns = request.columns or None
            chart_data = visualizer.generate_heatmap(columns=columns)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported chart type: {request.chart_type}")
        
        # Get available visualizations for recommendations
        available_viz_dict = visualizer.get_available_visualizations()
        viz_summary = visualizer.generate_visualization_summary()
        
        # Convert available visualizations to list format
        available_viz_list = []
        for viz_type, columns in available_viz_dict.items():
            if columns:  # Only include visualization types that have applicable columns
                available_viz_list.append(viz_type)
        
        return VisualizationResponse(
            file_id=request.file_id,
            chart_type=request.chart_type,
            chart_data=chart_data,
            available_visualizations=available_viz_list,
            recommendations=viz_summary["recommendations"],
            generation_timestamp=datetime.now(),
            message="Visualization generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization generation failed: {str(e)}")


@app.post("/insight", response_model=InsightResponse)
async def generate_insight(request: InsightRequest):
    """
    Generate AI-powered insights from uploaded CSV
    
    Args:
        request: Insight configuration
        
    Returns:
        AI-generated insights and recommendations
    """
    try:
        # Load DataFrame for insight generator
        df = load_dataframe(request.file_id)
        
        # Get analysis results first
        file_path = get_file_path(request.file_id)
        analyzer = DataAnalyzer(file_path)
        analysis_results = analyzer.analyze(
            include_correlation=True,
            include_outliers=True,
            include_statistical_tests=True
        )
        
        # Initialize insight generator
        insight_generator = InsightGenerator(
            llm_provider=request.llm_provider
        )
        
        # Generate comprehensive insights
        insights = await insight_generator.generate_comprehensive_insights(
            analysis_results=analysis_results,
            df=df,
            user_context=request.user_context
        )
        
        return InsightResponse(
            file_id=request.file_id,
            insights=insights,
            generation_timestamp=datetime.now(),
            processing_time_seconds=0.0,  # Could add timing logic
            message="AI insights generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")


@app.get("/files")
async def list_uploaded_files():
    """
    List all uploaded files with metadata
    
    Returns:
        List of uploaded files and their information
    """
    files_info = []
    
    for file_id, info in uploaded_files.items():
        files_info.append({
            "file_id": file_id,
            "filename": info["original_filename"],
            "upload_time": info["upload_time"],
            "file_size": info["file_size"],
            "rows": info["rows"],
            "columns": info["columns"],
            "column_names": info["column_names"][:10]  # Limit column names shown
        })
    
    return {
        "total_files": len(files_info),
        "files": files_info
    }


@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    Delete uploaded file and cleanup
    
    Args:
        file_id: File identifier to delete
        
    Returns:
        Deletion confirmation
    """
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Remove physical file
        file_path = uploaded_files[file_id]["file_path"]
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from memory
        del uploaded_files[file_id]
        
        return {"message": f"File {file_id} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@app.get("/visualizations/available/{file_id}")
async def get_available_visualizations(file_id: str):
    """
    Get available visualization options for a specific file
    
    Args:
        file_id: File identifier
        
    Returns:
        Available visualization types and columns
    """
    try:
        df = load_dataframe(file_id)
        visualizer = DataVisualizer(df)
        
        return {
            "file_id": file_id,
            "available_visualizations": visualizer.get_available_visualizations(),
            "visualization_summary": visualizer.generate_visualization_summary()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting visualizations: {str(e)}")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message=str(exc) if settings.DEBUG else "An unexpected error occurred",
            timestamp=datetime.now()
        ).dict()
    )


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )