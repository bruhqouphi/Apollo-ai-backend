import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  Upload, 
  Brain, 
  PieChart, 
  Activity,
  ArrowRight,
  CheckCircle
} from 'lucide-react';
import { useUserContext } from '../../context/UserContext';
import { useNavigate } from 'react-router-dom';
import WorkflowProgress from '../Workflow/WorkflowProgress';

const Dashboard: React.FC = () => {
  const { workflow, setCurrentStep, canProceedToStep } = useUserContext();
  const navigate = useNavigate();

  useEffect(() => {
    setCurrentStep('upload');
  }, []);

  const quickActions = [
    {
      title: 'Upload Data',
      description: 'Start by uploading your CSV file',
      icon: Upload,
      path: '/upload',
      color: 'from-blue-500 to-blue-600',
      available: true
    },
    {
      title: 'Data Analysis',
      description: 'Get statistical insights',
      icon: BarChart3,
      path: '/analysis',
      color: 'from-green-500 to-green-600',
      available: canProceedToStep('analysis')
    },
    {
      title: 'AI Insights',
      description: 'Get intelligent recommendations',
      icon: Brain,
      path: '/insights',
      color: 'from-purple-500 to-purple-600',
      available: canProceedToStep('insights')
    },
    {
      title: 'Visualizations',
      description: 'Create charts and graphs',
      icon: PieChart,
      path: '/charts',
      color: 'from-orange-500 to-orange-600',
      available: canProceedToStep('visualization')
    }
  ];

  const stats = [
    {
      label: 'Files Uploaded',
      value: workflow.currentFileId ? '1' : '0',
      icon: Upload,
      color: 'text-blue-400'
    },
    {
      label: 'Analyses Completed',
      value: workflow.analysisResults ? '1' : '0',
      icon: BarChart3,
      color: 'text-green-400'
    },
    {
      label: 'Insights Generated',
      value: workflow.insightsResults ? '1' : '0',
      icon: Brain,
      color: 'text-purple-400'
    },
    {
      label: 'Charts Created',
      value: workflow.visualizationResults ? '1' : '0',
      icon: PieChart,
      color: 'text-orange-400'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Workflow Progress */}
      <WorkflowProgress />

      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-8 text-center"
      >
        <motion.div
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg"
        >
          <Activity className="w-10 h-10 text-white" />
        </motion.div>
        
        <h1 className="text-4xl font-bold text-white mb-4">
          Welcome to Apollo AI
        </h1>
        <p className="text-xl text-white/60 mb-6 max-w-2xl mx-auto">
          Your intelligent no-code platform for data analysis and visualization
        </p>
        
        {!workflow.currentFileId && (
          <motion.button
            onClick={() => navigate('/upload')}
            className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-300 transform hover:scale-105"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Upload className="w-5 h-5" />
            <span>Get Started - Upload Your Data</span>
            <ArrowRight className="w-5 h-5" />
          </motion.button>
        )}
      </motion.div>

      {/* Stats Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
              className="glass-card p-6 text-center"
            >
              <div className={`w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center mx-auto mb-3`}>
                <Icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-sm text-white/60">{stat.label}</div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card p-6"
      >
        <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <motion.button
                key={action.title}
                onClick={() => action.available && navigate(action.path)}
                disabled={!action.available}
                className={`p-6 rounded-xl text-left transition-all duration-300 ${
                  action.available
                    ? 'bg-white/5 hover:bg-white/10 cursor-pointer'
                    : 'bg-white/5 opacity-50 cursor-not-allowed'
                }`}
                whileHover={action.available ? { scale: 1.02 } : {}}
                whileTap={action.available ? { scale: 0.98 } : {}}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
              >
                <div className={`w-12 h-12 bg-gradient-to-br ${action.color} rounded-xl flex items-center justify-center mb-4`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{action.title}</h3>
                <p className="text-white/60 text-sm mb-3">{action.description}</p>
                <div className="flex items-center justify-between">
                  {action.available ? (
                    <ArrowRight className="w-4 h-4 text-white/40" />
                  ) : (
                    <CheckCircle className="w-4 h-4 text-white/40" />
                  )}
                </div>
              </motion.button>
            );
          })}
        </div>
      </motion.div>

      {/* Current Status */}
      {workflow.currentFileId && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6 border border-green-500/30 bg-green-500/10"
        >
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
              <CheckCircle className="w-4 h-4 text-green-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-green-400">File Uploaded</h3>
              <p className="text-white/60">
                You have uploaded a file. Continue with analysis to get insights.
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Error Display */}
      {workflow.error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 border border-red-500/30 bg-red-500/10"
        >
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-red-500/20 rounded-full flex items-center justify-center">
              <Activity className="w-4 h-4 text-red-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-red-400">Error</h3>
              <p className="text-white/60">{workflow.error}</p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Dashboard; 