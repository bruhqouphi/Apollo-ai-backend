import React from 'react';
import { motion } from 'framer-motion';
import { Upload, TrendingUp, BarChart3, Brain, CheckCircle, Lock } from 'lucide-react';
import { useUserContext } from '../../context/UserContext';
import { useAppStore } from '../../store/useAppStore';

interface WorkflowStepItem {
  id: string;
  label: string;
  description: string;
  icon: React.ComponentType<any>;
  status: 'pending' | 'active' | 'completed' | 'locked';
}

const Workflow: React.FC = () => {
  const { workflow, canProceedToAnalysis, canProceedToVisualization, canProceedToInsights } = useUserContext();
  const { currentFile, analysisResult, insights } = useAppStore();

  const getWorkflowSteps = (): WorkflowStepItem[] => [
    {
      id: 'upload',
      label: 'Upload Data',
      description: 'Upload your CSV or Excel file',
      icon: Upload,
      status: currentFile ? 'completed' : workflow.currentStep === 'upload' ? 'active' : 'pending'
    },
    {
      id: 'analysis',
      label: 'Data Analysis',
      description: 'Statistical analysis and insights',
      icon: TrendingUp,
      status: analysisResult ? 'completed' : 
             canProceedToAnalysis() ? 'active' : 'locked'
    },
    {
      id: 'visualization',
      label: 'Visualizations',
      description: 'Create charts and graphs',
      icon: BarChart3,
      status: canProceedToVisualization() ? 'active' : 'locked'
    },
    {
      id: 'insights',
      label: 'AI Insights',
      description: 'AI-powered recommendations',
      icon: Brain,
      status: insights ? 'completed' : 
             canProceedToInsights() ? 'active' : 'locked'
    }
  ];

  const steps = getWorkflowSteps();

  const getStepIcon = (step: WorkflowStepItem) => {
    const IconComponent = step.icon;
    
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-400" />;
      case 'active':
        return <IconComponent className="w-6 h-6 text-blue-400" />;
      case 'locked':
        return <Lock className="w-6 h-6 text-white/40" />;
      default:
        return <IconComponent className="w-6 h-6 text-white/60" />;
    }
  };

  const getStepColor = (step: WorkflowStepItem) => {
    switch (step.status) {
      case 'completed':
        return 'border-green-500 bg-green-500/10';
      case 'active':
        return 'border-blue-500 bg-blue-500/10';
      case 'locked':
        return 'border-white/20 bg-white/5 opacity-50';
      default:
        return 'border-white/20 bg-white/5';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6"
    >
      <h3 className="text-lg font-semibold text-white mb-4">Analysis Workflow</h3>
      
      <div className="space-y-4">
        {steps.map((step, index) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`flex items-center space-x-4 p-4 rounded-xl border ${getStepColor(step)}`}
          >
            <div className="flex-shrink-0">
              {getStepIcon(step)}
            </div>
            
            <div className="flex-1">
              <h4 className="text-white font-medium">{step.label}</h4>
              <p className="text-white/60 text-sm">{step.description}</p>
            </div>
            
            {index < steps.length - 1 && (
              <div className="flex-shrink-0">
                <div className="w-px h-8 bg-white/20" />
              </div>
            )}
          </motion.div>
        ))}
      </div>
      
      {workflow.completedSteps.includes('insights') && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mt-6 p-4 bg-green-500/10 border border-green-500/30 rounded-xl"
        >
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-400" />
            <div>
              <h4 className="text-white font-medium">Analysis Complete!</h4>
              <p className="text-white/60 text-sm">
                Your data has been fully analyzed. You can now explore insights and create visualizations.
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default Workflow; 