import React from 'react';
import { motion } from 'framer-motion';
import { Check, ArrowRight, Upload, BarChart3, Brain, PieChart, Download } from 'lucide-react';
import { useUserContext, WorkflowStep } from '../../context/UserContext';
import { useNavigate } from 'react-router-dom';

const stepConfig = {
  upload: {
    label: 'Upload Data',
    icon: Upload,
    path: '/upload',
    description: 'Upload your CSV file'
  },
  analysis: {
    label: 'Data Analysis',
    icon: BarChart3,
    path: '/analysis',
    description: 'Statistical analysis'
  },
  insights: {
    label: 'AI Insights',
    icon: Brain,
    path: '/insights',
    description: 'AI-powered insights'
  },
  visualization: {
    label: 'Visualizations',
    icon: PieChart,
    path: '/charts',
    description: 'Create charts'
  },
  export: {
    label: 'Export',
    icon: Download,
    path: '/downloads',
    description: 'Export reports'
  }
};

const WorkflowProgress: React.FC = () => {
  const { workflow, canProceedToStep, getNextStep, getPreviousStep } = useUserContext();
  const navigate = useNavigate();

  const steps: WorkflowStep[] = ['upload', 'analysis', 'insights', 'visualization', 'export'];

  const handleStepClick = (step: WorkflowStep) => {
    if (canProceedToStep(step)) {
      navigate(stepConfig[step].path);
    }
  };

  const getStepStatus = (step: WorkflowStep) => {
    if (workflow.currentStep === step) {
      return 'current';
    }
    if (workflow.completedSteps.includes(step)) {
      return 'completed';
    }
    if (canProceedToStep(step)) {
      return 'available';
    }
    return 'locked';
  };

  return (
    <div className="glass-card p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Analysis Workflow</h3>
        <div className="text-sm text-white/60">
          Step {steps.indexOf(workflow.currentStep) + 1} of {steps.length}
        </div>
      </div>

      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const status = getStepStatus(step);
          const config = stepConfig[step];
          const Icon = config.icon;
          const isClickable = status !== 'locked';

          return (
            <React.Fragment key={step}>
              <motion.div
                className={`flex flex-col items-center cursor-pointer transition-all duration-200 ${
                  isClickable ? 'hover:scale-105' : ''
                }`}
                onClick={() => isClickable && handleStepClick(step)}
                whileHover={isClickable ? { scale: 1.05 } : {}}
                whileTap={isClickable ? { scale: 0.95 } : {}}
              >
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all duration-200 ${
                    status === 'completed'
                      ? 'bg-green-500 text-white'
                      : status === 'current'
                      ? 'bg-blue-500 text-white ring-4 ring-blue-500/30'
                      : status === 'available'
                      ? 'bg-white/20 text-white/80 border-2 border-white/30'
                      : 'bg-white/10 text-white/40'
                  }`}
                >
                  {status === 'completed' ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                <div className="text-center">
                  <div
                    className={`text-sm font-medium transition-colors duration-200 ${
                      status === 'completed'
                        ? 'text-green-400'
                        : status === 'current'
                        ? 'text-blue-400'
                        : status === 'available'
                        ? 'text-white/80'
                        : 'text-white/40'
                    }`}
                  >
                    {config.label}
                  </div>
                  <div
                    className={`text-xs transition-colors duration-200 ${
                      status === 'completed'
                        ? 'text-green-400/70'
                        : status === 'current'
                        ? 'text-blue-400/70'
                        : 'text-white/50'
                    }`}
                  >
                    {config.description}
                  </div>
                </div>
              </motion.div>

              {index < steps.length - 1 && (
                <div className="flex-1 mx-4">
                  <div
                    className={`h-0.5 transition-all duration-300 ${
                      workflow.completedSteps.includes(step)
                        ? 'bg-green-500'
                        : 'bg-white/20'
                    }`}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Navigation buttons */}
      <div className="flex justify-between mt-6">
        <motion.button
          onClick={() => {
            const prevStep = getPreviousStep();
            if (prevStep) {
              navigate(stepConfig[prevStep].path);
            }
          }}
          disabled={!getPreviousStep()}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
            getPreviousStep()
              ? 'bg-white/10 text-white hover:bg-white/20'
              : 'bg-white/5 text-white/40 cursor-not-allowed'
          }`}
          whileHover={getPreviousStep() ? { scale: 1.02 } : {}}
          whileTap={getPreviousStep() ? { scale: 0.98 } : {}}
        >
          <ArrowRight className="w-4 h-4 rotate-180" />
          <span>Previous</span>
        </motion.button>

        <motion.button
          onClick={() => {
            const nextStep = getNextStep();
            if (nextStep && canProceedToStep(nextStep)) {
              navigate(stepConfig[nextStep].path);
            }
          }}
          disabled={!getNextStep() || !canProceedToStep(getNextStep()!)}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
            getNextStep() && canProceedToStep(getNextStep()!)
              ? 'bg-blue-500 text-white hover:bg-blue-600'
              : 'bg-white/5 text-white/40 cursor-not-allowed'
          }`}
          whileHover={
            getNextStep() && canProceedToStep(getNextStep()!) ? { scale: 1.02 } : {}
          }
          whileTap={
            getNextStep() && canProceedToStep(getNextStep()!) ? { scale: 0.98 } : {}
          }
        >
          <span>Next</span>
          <ArrowRight className="w-4 h-4" />
        </motion.button>
      </div>

      {/* Error display */}
      {workflow.error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg"
        >
          <div className="text-red-400 text-sm">{workflow.error}</div>
        </motion.div>
      )}

      {/* Processing indicator */}
      {workflow.isProcessing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 flex items-center justify-center space-x-2 text-blue-400"
        >
          <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm">Processing...</span>
        </motion.div>
      )}
    </div>
  );
};

export default WorkflowProgress; 