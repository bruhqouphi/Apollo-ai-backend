import { 
  UploadResponse, 
  AnalysisRequest, 
  AnalysisResponse, 
  VisualizationRequest, 
  VisualizationResponse, 
  InsightRequest, 
  InsightResponse
} from '../types';
import { authService } from './auth';

// Hardcode API base URL for the demo to ensure frontend always targets the backend
// Use 127.0.0.1 to avoid potential IPv6 localhost (::1) resolution issues
export const API_BASE_URL = 'http://127.0.0.1:8000';

class ApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    // Don't set default Content-Type for FormData requests
    const defaultHeaders: Record<string, string> = {};
    if (!(options.body instanceof FormData)) {
      defaultHeaders['Content-Type'] = 'application/json';
    }

    // Add authentication header if available
    const token = authService.getAccessToken();
    if (token) {
      defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else if (typeof errorData === 'string') {
            errorMessage = errorData;
          } else if (errorData && typeof errorData === 'object') {
            errorMessage = JSON.stringify(errorData);
          }
        } catch (parseError) {
          // If we can't parse the error response, use the status text
          errorMessage = response.statusText || `HTTP error! status: ${response.status}`;
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      // Convert datetime objects to strings for frontend compatibility
      if (data.timestamp && typeof data.timestamp === 'object') {
        data.timestamp = new Date(data.timestamp).toISOString();
      }
      if (data.analysis_timestamp && typeof data.analysis_timestamp === 'object') {
        data.analysis_timestamp = new Date(data.analysis_timestamp).toISOString();
      }
      if (data.generation_timestamp && typeof data.generation_timestamp === 'object') {
        data.generation_timestamp = new Date(data.generation_timestamp).toISOString();
      }
      
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; message: string; version: string }> {
    try {
      return await this.request('/api/v1/health');
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error('Backend server is not available');
    }
  }

  // File Upload
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    console.log('Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type);

    return this.request('/api/v1/upload/', {
      method: 'POST',
      body: formData,
    });
  }

  // Data Analysis
  async analyzeData(request: AnalysisRequest): Promise<AnalysisResponse> {
    return this.request('/api/v1/analysis/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Generate Visualization
  async generateVisualization(request: VisualizationRequest): Promise<VisualizationResponse> {
    return this.request('/api/v1/visualization/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Generate Insights
  async generateInsights(request: InsightRequest): Promise<InsightResponse> {
    return this.request('/api/v1/insights/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get Available Visualizations
  async getAvailableVisualizations(fileId: string): Promise<{
    file_id: string;
    available_visualizations: Record<string, string[]>;
    visualization_summary: any;
  }> {
    return this.request(`/api/v1/visualization/${fileId}/available`);
  }

  // List Uploaded Files
  async listFiles(): Promise<{
    total_files: number;
    files: Array<{
      file_id: string;
      filename: string;
      upload_time: string;
      file_size: number;
      rows: number;
      columns: number;
      column_names: string[];
    }>;
  }> {
    return this.request('/api/v1/upload/files');
  }

  // Delete File
  async deleteFile(fileId: string): Promise<{ message: string }> {
    return this.request(`/api/v1/upload/files/${fileId}`, {
      method: 'DELETE',
    });
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();

// Export the class for testing purposes
export { ApiService }; 