import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { 
  AppState
} from '../types';

const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial State
        currentFile: null,
        uploadedFiles: [],
        analysisResult: null,
        isAnalyzing: false,
        currentChart: null,
        chartGallery: [],
        isGeneratingChart: false,
        insights: null,
        isGeneratingInsights: false,
        isLoading: false,
        error: null,

        // File Management Actions
        setCurrentFile: (file) => set({ currentFile: file }),
        
        addUploadedFile: (file) => set((state) => ({
          uploadedFiles: [...state.uploadedFiles, file],
          currentFile: file
        })),

        // Analysis Actions
        setAnalysisResult: (result) => set({ analysisResult: result }),
        
        setAnalyzing: (analyzing) => set({ isAnalyzing: analyzing }),

        // Visualization Actions
        setCurrentChart: (chart) => set({ currentChart: chart }),
        
        addToChartGallery: (chart) => set((state) => ({
          chartGallery: [...state.chartGallery, chart],
          currentChart: chart
        })),
        
        setGeneratingChart: (generating) => set({ isGeneratingChart: generating }),

        // Insights Actions
        setInsights: (insights) => set({ insights }),
        
        setGeneratingInsights: (generating) => set({ isGeneratingInsights: generating }),

        // UI Actions
        setLoading: (loading) => set({ isLoading: loading }),
        
        setError: (error) => set({ error }),
        
        clearError: () => set({ error: null }),
      }),
      {
        name: 'apollo-ai-storage',
        partialize: (state) => ({
          uploadedFiles: state.uploadedFiles,
          chartGallery: state.chartGallery,
        }),
      }
    ),
    {
      name: 'apollo-ai-store',
    }
  )
);

export { useAppStore }; 