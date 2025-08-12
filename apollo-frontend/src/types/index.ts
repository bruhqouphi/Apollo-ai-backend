// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// File Upload Types
export interface UploadedFile {
  file_id: string;
  filename: string;
  file_size: string;
  rows_count: number;
  columns_count: number;
  columns: string[];
  upload_time: string;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  timestamp: string;
  file_id: string;
  filename: string;
  file_size: string;
  rows_count: number;
  columns_count: number;
  columns: string[];
}

// Analysis Types
export interface AnalysisRequest {
  file_id: string;
  include_correlation?: boolean;
  include_outliers?: boolean;
  include_statistical_tests?: boolean;
  outlier_method?: 'iqr' | 'zscore';
  confidence_level?: number;
  target_columns?: string[];
}

export interface ColumnStats {
  name: string;
  dtype: string;
  count: number;
  missing: number;
  unique: number;
  mean?: number;
  std?: number;
  min?: number;
  max?: number;
  top?: string;
  freq?: number;
}

export interface DatasetSummary {
  rows: number;
  cols: number;
  columns: ColumnStats[];
}

export interface AnalysisResponse {
  file_id: string;
  summary: DatasetSummary;
  analysis_results: any;
  analysis_timestamp: string;
  processing_time_seconds: number;
  message: string;
}

// Visualization Types
export interface VisualizationRequest {
  file_id: string;
  chart_type: string;
  column?: string;
  columns?: string[];
  x_column?: string;
  y_column?: string;
  color_column?: string;
  bins?: number;
  top_n?: number;
}

export interface ChartData {
  labels?: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }[];
}

export interface VisualizationResponse {
  file_id: string;
  chart_type: string;
  chart_data: any; // Chart.js compatible data structure
  available_visualizations: string[];
  recommendations: string[];
  generation_timestamp: string;
  message: string;
}

// Insight Types
export interface InsightRequest {
  file_id: string;
  llm_provider?: string;
  user_context?: string;
}

export interface InsightResponse {
  file_id: string;
  insights: {
    executive_summary: string;
    key_findings: string[];
    detailed_insights: Record<string, any>;
    recommendations: string[];
    data_quality_assessment: string;
    statistical_significance: Record<string, any>;
    visualizations_explained?: Record<string, any>;
    next_steps: string[];
    confidence_level: string;
    generation_metadata?: Record<string, any>;
    // Optional fields for backward compatibility
    trends?: string[];
    anomalies?: string[];
    summary?: string;
  };
  generation_timestamp: string;
  processing_time_seconds: number;
  message: string;
}

// UI State Types
export interface AppState {
  // File Management
  currentFile: UploadedFile | null;
  uploadedFiles: UploadedFile[];
  
  // Analysis State
  analysisResult: AnalysisResponse | null;
  isAnalyzing: boolean;
  
  // Visualization State
  currentChart: VisualizationResponse | null;
  chartGallery: VisualizationResponse[];
  isGeneratingChart: boolean;
  
  // Insights State
  insights: InsightResponse | null;
  isGeneratingInsights: boolean;
  
  // UI State
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setCurrentFile: (file: UploadedFile | null) => void;
  addUploadedFile: (file: UploadedFile) => void;
  setAnalysisResult: (result: AnalysisResponse | null) => void;
  setAnalyzing: (analyzing: boolean) => void;
  setCurrentChart: (chart: VisualizationResponse | null) => void;
  addToChartGallery: (chart: VisualizationResponse) => void;
  setGeneratingChart: (generating: boolean) => void;
  setInsights: (insights: InsightResponse | null) => void;
  setGeneratingInsights: (generating: boolean) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

// Navigation Types
export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon: string;
  description?: string;
}

// Chart Types
export type ChartType = 'histogram' | 'boxplot' | 'bar' | 'scatter' | 'heatmap' | 'line' | 'pie' | 'area';

export interface ChartConfig {
  type: ChartType;
  title: string;
  description: string;
  icon: string;
  color: string;
  requirements: {
    minColumns: number;
    maxColumns?: number;
    dataTypes: string[];
  };
}

// Theme Types
export interface Theme {
  name: string;
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
}

// User Preferences
export interface UserPreferences {
  theme: string;
  language: string;
  autoSave: boolean;
  notifications: boolean;
  defaultChartType: ChartType;
} 