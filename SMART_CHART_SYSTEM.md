# Apollo AI Smart Chart Rendering System

## Overview

The smart chart rendering system automatically selects the optimal visualization library based on chart type, data characteristics, and user preferences. It supports both interactive and static chart generation with a consistent black/white/grey theme.

## Architecture

### Backend Components

#### 1. Smart Chart Service (`app/services/smart_chart_service.py`)

- **Purpose**: Intelligent library selection and chart generation
- **Libraries Supported**:
  - Matplotlib (static, high-quality images)
  - Seaborn (statistical visualizations)
  - Plotly (interactive charts)
  - Bokeh (planned, currently falls back to Plotly)

**Key Features:**

- Automatic library selection based on:
  - Chart type requirements
  - Data size (>1000 points prefer interactive)
  - Time series detection
  - User mode preference
- Consistent theming across all libraries
- Error handling for missing dependencies

#### 2. Updated API Endpoints (`app/api/endpoints/visualization.py`)

- **New Parameters**:
  - `mode`: 'auto', 'interactive', or 'static'
  - Smart library selection based on requirements
- **New Endpoints**:
  - `/interactive/{filename}` - Serve HTML charts
  - Enhanced `/generate-chart` with mode selection

### Frontend Components

#### 1. Smart Chart Renderer (`apollo-frontend/src/components/Charts/SmartChartRenderer.tsx`)

- **Purpose**: Universal chart display component
- **Features**:
  - Handles both static images and interactive HTML
  - Library badges (Plotly, Matplotlib, Seaborn)
  - Mode indicators (Interactive/Static)
  - Zoom functionality
  - Download options
  - Error handling with retry

#### 2. Chart Mode Selector (`apollo-frontend/src/components/Charts/ChartModeSelector.tsx`)

- **Purpose**: User interface for selecting rendering mode
- **Options**:
  - **Smart Auto**: Intelligent selection (recommended)
  - **Interactive**: Plotly with hover, zoom, click
  - **Static**: High-quality PNG images

#### 3. Updated Chart Gallery (`apollo-frontend/src/components/Charts/ChartGallery.tsx`)

- **Changes**:
  - Integrated chart mode selection
  - Settings modal for mode configuration
  - Smart chart renderer integration
  - Enhanced download functionality

## Library Selection Logic

### Auto Mode Decision Tree

```
if data_size > 1000:
    mode = INTERACTIVE
elif has_time_series:
    mode = INTERACTIVE
elif chart_type in ['histogram', 'box_plot', 'violin_plot', 'correlation_matrix']:
    mode = STATIC
else:
    mode = INTERACTIVE
```

### Library Preferences

- **Interactive Preferred**: scatter_plot, line_chart, heatmap, bubble_chart
- **Static Preferred**: histogram, box_plot, violin_plot, correlation_matrix
- **Flexible**: bar_chart, pie_chart, area_chart

## Design System (HCI Compliance)

### Color Palette (All Libraries)

```javascript
{
  'primary': '#404040',      // Dark grey
  'secondary': '#666666',    // Medium grey
  'tertiary': '#808080',     // Light grey
  'quaternary': '#999999',   // Lighter grey
  'background': '#ffffff',   // White
  'text': '#333333',         // Dark text
  'grid': '#e5e5e5',        // Light grid
  'accent': '#b3b3b3'       // Very light grey
}
```

### Typography & Accessibility

- Font family: Inter, Arial, sans-serif
- High contrast ratios (WCAG compliant)
- Consistent spacing and alignment
- Clear visual hierarchy

## Usage Examples

### Backend API Call

```python
POST /api/v1/visualization/generate-chart
{
  "chart_type": "scatter_plot",
  "columns": "age,income",
  "mode": "auto",  # or 'interactive', 'static'
  "bins": 30,
  "title": "Age vs Income"
}
```

### Frontend Integration

```tsx
<SmartChartRenderer
  chartData={chartData}
  onRefresh={handleRefresh}
  onDownload={handleDownload}
  onSettings={openModeSelector}
/>
```

## Chart Types Supported

| Chart Type         | Libraries                   | Recommended Mode | Use Case                 |
| ------------------ | --------------------------- | ---------------- | ------------------------ |
| Histogram          | Matplotlib, Seaborn, Plotly | Static           | Distribution analysis    |
| Bar Chart          | All                         | Interactive      | Categorical comparisons  |
| Line Chart         | Matplotlib, Plotly          | Interactive      | Trends over time         |
| Scatter Plot       | All                         | Interactive      | Correlation analysis     |
| Pie Chart          | Matplotlib, Plotly          | Interactive      | Proportional data        |
| Box Plot           | Matplotlib, Seaborn         | Static           | Statistical distribution |
| Violin Plot        | Seaborn                     | Static           | Distribution comparison  |
| Correlation Matrix | Seaborn, Plotly             | Static           | Variable relationships   |

## Benefits

### For Users

1. **Automatic Optimization**: Best library chosen automatically
2. **Consistent Experience**: Same UI regardless of backend library
3. **Flexible Control**: Can override auto-selection when needed
4. **High Performance**: Interactive for exploration, static for reports

### For Developers

1. **Modular Design**: Easy to add new libraries
2. **Consistent API**: Same interface regardless of backend
3. **Error Resilience**: Graceful fallbacks
4. **Maintainable Code**: Clear separation of concerns

## Future Enhancements

1. **Bokeh Integration**: Full implementation for specialized interactive charts
2. **3D Visualizations**: Plotly 3D charts for spatial data
3. **Animation Support**: Time-series animations
4. **Custom Themes**: User-defined color schemes
5. **Export Options**: PDF, SVG, high-res PNG
6. **Real-time Charts**: WebSocket integration for live data

## Error Handling

- **Missing Libraries**: Graceful fallback to available options
- **Invalid Data**: Clear error messages and suggestions
- **Network Issues**: Retry mechanisms and offline fallbacks
- **Large Datasets**: Automatic sampling for performance

This smart chart system provides a Julius AI-like experience with intelligent automation while maintaining full user control when needed.

