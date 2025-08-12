import React, { createContext, useContext, useState, ReactNode } from 'react';

// Define the user workflow steps
export type WorkflowStep = 
  | 'upload' 
  | 'analysis' 
  | 'insights' 
  | 'visualization' 
  | 'export';

export interface WorkflowState {
  currentStep: WorkflowStep;
  completedSteps: WorkflowStep[];
  currentFileId: string | null;
  analysisResults: any | null;
  insightsResults: any | null;
  visualizationResults: any | null;
  isProcessing: boolean;
  error: string | null;
}

interface UserContextType {
  // Workflow state
  workflow: WorkflowState;
  
  // Workflow actions
  setCurrentStep: (step: WorkflowStep) => void;
  completeStep: (step: WorkflowStep) => void;
  setFileId: (fileId: string) => void;
  setAnalysisResults: (results: any) => void;
  setInsightsResults: (results: any) => void;
  setVisualizationResults: (results: any) => void;
  setProcessing: (isProcessing: boolean) => void;
  setError: (error: string | null) => void;
  resetWorkflow: () => void;
  
  // Navigation helpers
  canProceedToStep: (step: WorkflowStep) => boolean;
  canProceedToAnalysis: () => boolean;
  canProceedToVisualization: () => boolean;
  canProceedToInsights: () => boolean;
  getNextStep: () => WorkflowStep | null;
  getPreviousStep: () => WorkflowStep | null;
  
  // User preferences
  preferences: {
    theme: 'light' | 'dark';
    autoSave: boolean;
    notifications: boolean;
  };
  updatePreferences: (prefs: Partial<UserContextType['preferences']>) => void;
}

const defaultWorkflow: WorkflowState = {
  currentStep: 'upload',
  completedSteps: [],
  currentFileId: null,
  analysisResults: null,
  insightsResults: null,
  visualizationResults: null,
  isProcessing: false,
  error: null,
};

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUserContext = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUserContext must be used within a UserContextProvider');
  }
  return context;
};

interface UserContextProviderProps {
  children: ReactNode;
}

export const UserContextProvider: React.FC<UserContextProviderProps> = ({ children }) => {
  const [workflow, setWorkflow] = useState<WorkflowState>(() => {
    // Load from localStorage if available
    const saved = localStorage.getItem('apollo-workflow');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return defaultWorkflow;
      }
    }
    return defaultWorkflow;
  });

  const [preferences, setPreferences] = useState<{
    theme: 'light' | 'dark';
    autoSave: boolean;
    notifications: boolean;
  }>({
    theme: 'dark',
    autoSave: true,
    notifications: true,
  });

  // Save workflow to localStorage whenever it changes
  React.useEffect(() => {
    localStorage.setItem('apollo-workflow', JSON.stringify(workflow));
  }, [workflow]);

  const setCurrentStep = (step: WorkflowStep) => {
    setWorkflow(prev => ({ ...prev, currentStep: step, error: null }));
  };

  const completeStep = (step: WorkflowStep) => {
    setWorkflow(prev => ({
      ...prev,
      completedSteps: Array.from(new Set([...prev.completedSteps, step])),
      error: null
    }));
  };

  const setFileId = (fileId: string) => {
    setWorkflow(prev => ({ ...prev, currentFileId: fileId, error: null }));
  };

  const setAnalysisResults = (results: any) => {
    setWorkflow(prev => ({ ...prev, analysisResults: results, error: null }));
  };

  const setInsightsResults = (results: any) => {
    setWorkflow(prev => ({ ...prev, insightsResults: results, error: null }));
  };

  const setVisualizationResults = (results: any) => {
    setWorkflow(prev => ({ ...prev, visualizationResults: results, error: null }));
  };

  const setProcessing = (isProcessing: boolean) => {
    setWorkflow(prev => ({ ...prev, isProcessing, error: null }));
  };

  const setError = (error: string | null) => {
    setWorkflow(prev => ({ ...prev, error }));
  };

  const resetWorkflow = () => {
    setWorkflow(defaultWorkflow);
  };

  // Navigation logic
  const stepOrder: WorkflowStep[] = ['upload', 'analysis', 'insights', 'visualization', 'export'];

  const canProceedToStep = (step: WorkflowStep): boolean => {
    const stepIndex = stepOrder.indexOf(step);
    
    // Can always go back to upload
    if (step === 'upload') return true;
    
    // Check if previous steps are completed
    for (let i = 0; i < stepIndex; i++) {
      const requiredStep = stepOrder[i];
      if (!workflow.completedSteps.includes(requiredStep)) {
        return false;
      }
    }
    
    return true;
  };

  const getNextStep = (): WorkflowStep | null => {
    const currentIndex = stepOrder.indexOf(workflow.currentStep);
    if (currentIndex < stepOrder.length - 1) {
      return stepOrder[currentIndex + 1];
    }
    return null;
  };

  const getPreviousStep = (): WorkflowStep | null => {
    const currentIndex = stepOrder.indexOf(workflow.currentStep);
    if (currentIndex > 0) {
      return stepOrder[currentIndex - 1];
    }
    return null;
  };

  // Add helper methods for specific step checks
  const canProceedToAnalysis = (): boolean => {
    return canProceedToStep('analysis');
  };

  const canProceedToVisualization = (): boolean => {
    return canProceedToStep('visualization');
  };

  const canProceedToInsights = (): boolean => {
    return canProceedToStep('insights');
  };

  const updatePreferences = (newPrefs: Partial<UserContextType['preferences']>) => {
    setPreferences(prev => ({ ...prev, ...newPrefs }));
  };

  const value: UserContextType = {
    workflow,
    setCurrentStep,
    completeStep,
    setFileId,
    setAnalysisResults,
    setInsightsResults,
    setVisualizationResults,
    setProcessing,
    setError,
    resetWorkflow,
    canProceedToStep,
    canProceedToAnalysis,
    canProceedToVisualization,
    canProceedToInsights,
    getNextStep,
    getPreviousStep,
    preferences,
    updatePreferences,
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}; 