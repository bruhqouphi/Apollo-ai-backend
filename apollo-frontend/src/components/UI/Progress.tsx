import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface ProgressProps {
  currentStep: number;
  totalSteps: number;
  status: 'loading' | 'success' | 'error' | 'idle';
  message: string;
  showProgress?: boolean;
}

const Progress: React.FC<ProgressProps> = ({
  currentStep,
  totalSteps,
  status,
  message,
  showProgress = true
}) => {
  const progress = (currentStep / totalSteps) * 100;

  const getStatusIcon = () => {
    switch (status) {
      case 'loading':
        return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      default:
        return null;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'loading':
        return 'border-blue-500 bg-blue-500/10';
      case 'success':
        return 'border-green-500 bg-green-500/10';
      case 'error':
        return 'border-red-500 bg-red-500/10';
      default:
        return 'border-white/20 bg-white/5';
    }
  };

  if (status === 'idle') {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-card p-4 border ${getStatusColor()}`}
    >
      <div className="flex items-center space-x-3 mb-3">
        {getStatusIcon()}
        <div className="flex-1">
          <p className="text-white font-medium">{message}</p>
          {showProgress && (
            <p className="text-white/60 text-sm">
              Step {currentStep} of {totalSteps}
            </p>
          )}
        </div>
      </div>
      
      {showProgress && (
        <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className={`h-full rounded-full ${
              status === 'loading' ? 'bg-blue-500' :
              status === 'success' ? 'bg-green-500' :
              status === 'error' ? 'bg-red-500' : 'bg-white/20'
            }`}
          />
        </div>
      )}
    </motion.div>
  );
};

export default Progress; 