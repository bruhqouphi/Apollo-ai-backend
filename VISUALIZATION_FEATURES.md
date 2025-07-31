# Apollo AI Visualization Features

## Overview

This document describes the new intelligent visualization system added to Apollo AI, which includes:

1. **Fixed Column Type Detection** - Resolved the issue where numerical columns were being misclassified as datetime
2. **Intelligent Chart Recommendations** - Automatically suggests the best chart types based on data characteristics
3. **Matplotlib-based Visualization Service** - Generates high-quality charts with download functionality
4. **REST API Endpoints** - Complete API for chart generation and management

## Key Improvements

### 1. Fixed Column Type Detection

**Problem**: Previously, numerical columns were being incorrectly classified as datetime, preventing statistical analysis.

**Solution**:

- Reordered detection logic to check for numerical data **before** datetime
- Enhanced datetime detection with additional validation to reduce false positives
- Added debug methods for troubleshooting

```python
# Before: datetime check came before numerical check
elif self._is_datetime_column(col_data):
    self.column_types[column] = ColumnType.datetime
elif self._is_numerical_column(col_data):
    self.column_types[column] = ColumnType.numeric

# After: numerical check comes first
elif self._is_numerical_column(col_data):
    self.column_types[column] = ColumnType.numeric
elif self._is_datetime_column(col_data):
    self.column_types[column] = ColumnType.datetime
```

### 2. Intelligent Chart Recommendations

The system now automatically recommends the best chart types based on:

- **Data type** (numerical, categorical, datetime, boolean)
- **Data characteristics** (unique values, sample size, distribution)
- **Chart suitability rules** (defined for each chart type)

**Supported Chart Types**:

- Histogram (numerical distribution)
- Bar Chart (categorical comparison)
- Line Chart (trends over time)
- Scatter Plot (correlation analysis)
- Box Plot (outlier detection)
- Pie Chart (proportions)
- Heatmap (correlation matrix)
- Violin Plot (distribution comparison)
- Density Plot (probability density)
- Grouped Bar Chart (categorical vs numerical)
- Stacked Bar Chart (composition)
- Area Chart (trends with filled area)

### 3. Matplotlib Visualization Service

**Features**:

- High-quality chart generation (300 DPI)
- Multiple output formats (PNG with base64 encoding)
- Download functionality
- Automatic file cleanup
- Customizable chart options

**Chart Options**:

- Bins for histograms
- Top N values for bar charts
- Trend lines for scatter plots
- Color schemes and styling

### 4. REST API Endpoints

#### Chart Recommendations

```http
POST /visualization/recommend-charts
Content-Type: multipart/form-data

Upload CSV file to get intelligent chart recommendations
```

#### Generate Specific Chart

```http
POST /visualization/generate-chart
Content-Type: multipart/form-data

Parameters:
- file: CSV file
- chart_type: Type of chart to generate
- columns: List of columns to use
- options: Additional chart options (optional)
```

#### Download Generated Chart

```http
GET /visualization/download/{filename}
```

#### Auto-Generate Best Charts

```http
POST /visualization/auto-generate-best-charts
Content-Type: multipart/form-data

Automatically generates the best charts for the dataset
```

#### Available Chart Types

```http
GET /visualization/available-chart-types
```

#### Cleanup Old Files

```http
DELETE /visualization/cleanup?hours=24
```

## Usage Examples

### Python API Usage

```python
from app.core.analyzer import DataAnalyzer
from app.core.chart_recommender import ChartRecommender
from app.services.visualization_service import VisualizationService

# Analyze data
analyzer = DataAnalyzer("data.csv")
df = analyzer.df
column_types = analyzer.column_types

# Get chart recommendations
recommender = ChartRecommender()
recommendations = recommender.recommend_charts_for_dataset(df, column_types)

# Generate charts
viz_service = VisualizationService()
result = viz_service.generate_chart(df, 'histogram', ['age'])
if result['success']:
    print(f"Chart saved: {result['filename']}")
    print(f"Download URL: {result['download_url']}")
```

### API Usage with curl

```bash
# Get chart recommendations
curl -X POST "http://localhost:8000/visualization/recommend-charts" \
  -F "file=@data.csv"

# Generate histogram
curl -X POST "http://localhost:8000/visualization/generate-chart" \
  -F "file=@data.csv" \
  -F "chart_type=histogram" \
  -F "columns=age"

# Download generated chart
curl -O "http://localhost:8000/visualization/download/histogram_age_20231201_143022.png"
```

## File Structure

```
app/
├── core/
│   ├── analyzer.py              # Enhanced with fixed column detection
│   └── chart_recommender.py     # New: Intelligent chart recommendations
├── services/
│   └── visualization_service.py # New: Matplotlib chart generation
├── api/endpoints/
│   └── visualization.py         # New: REST API endpoints
└── models/
    └── schemas.py               # Enhanced with visualization schemas
```

## Configuration

The visualization service uses these default settings:

- **Output Directory**: `temp_charts/`
- **Image Format**: PNG
- **DPI**: 300 (high quality)
- **Figure Size**: 10x6 inches
- **Auto Cleanup**: 24 hours

## Testing

Run the test script to verify functionality:

```bash
python test_visualization.py
```

This will:

1. Test column type detection
2. Test chart recommendations
3. Generate sample charts
4. Verify API functionality

## Benefits

1. **Automatic Intelligence**: No need to manually select chart types
2. **High Quality**: Professional-grade matplotlib charts
3. **Downloadable**: Users can download charts as PNG files
4. **Scalable**: REST API supports multiple concurrent users
5. **Maintainable**: Clean separation of concerns
6. **Extensible**: Easy to add new chart types

## Future Enhancements

1. **Interactive Charts**: Add Plotly support for interactive visualizations
2. **Custom Themes**: Allow users to customize chart appearance
3. **Batch Processing**: Generate multiple charts in parallel
4. **Chart Templates**: Pre-defined chart configurations
5. **Export Formats**: Support for PDF, SVG, and other formats
6. **Real-time Updates**: WebSocket support for live chart updates

## Troubleshooting

### Common Issues

1. **Column Type Misclassification**

   - Use `analyzer.debug_column_types()` to see detection details
   - Use `analyzer.override_column_types()` to manually fix types

2. **Chart Generation Fails**

   - Check column data types and values
   - Verify column names exist in dataset
   - Check for sufficient data points

3. **File Download Issues**
   - Verify file exists in temp_charts directory
   - Check file permissions
   - Use cleanup endpoint to remove old files

### Debug Methods

```python
# Debug column type detection
debug_info = analyzer.debug_column_types()
print(debug_info['column_name'])

# Override column types
analyzer.override_column_types({
    'column_name': ColumnType.numeric
})
```
