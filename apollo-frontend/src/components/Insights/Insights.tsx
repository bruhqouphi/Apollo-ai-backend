import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Brain, 
  Zap, 
  TrendingUp, 
  Lightbulb, 
  Target,
  ArrowRight,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Download,
  Share2,
  BookOpen,
  Sparkles
} from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { apiService } from '../../services/api';
import toast from 'react-hot-toast';
import WorkflowProgress from '../Workflow/WorkflowProgress';

const Insights: React.FC = () => {
  const navigate = useNavigate();
  const { currentFile, insights, setInsights } = useAppStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedInsightType, setSelectedInsightType] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState('groq'); // Default to Groq

  const insightTypes = [
    {
      id: 'summary',
      title: 'Data Summary',
      description: 'Get a comprehensive overview of your data',
      icon: BookOpen,
      color: 'from-blue-500 to-blue-600',
      duration: '30s'
    },
    {
      id: 'trends',
      title: 'Trend Analysis',
      description: 'Identify patterns and trends in your data',
      icon: TrendingUp,
      color: 'from-green-500 to-green-600',
      duration: '45s'
    },
    {
      id: 'anomalies',
      title: 'Anomaly Detection',
      description: 'Find unusual patterns and outliers',
      icon: AlertCircle,
      color: 'from-orange-500 to-orange-600',
      duration: '60s'
    },
    {
      id: 'comprehensive',
      title: '🎯 Professional Analysis',
      description: 'Advanced statistical analysis with business insights',
      icon: Target,
      color: 'from-purple-500 to-purple-600',
      duration: '60s',
      isNew: true,
      badge: 'Enhanced'
    }
  ];

  const handleGenerateInsights = async (insightType: string) => {
    if (!currentFile) {
      toast.error('Please upload a file first');
      navigate('/upload');
      return;
    }

    setIsGenerating(true);
    setSelectedInsightType(insightType);

    try {
      const request = {
        file_id: currentFile.file_id,
        llm_provider: selectedProvider, // Use selected provider
        user_context: insightType === 'comprehensive' 
          ? 'Professional business analytics and data science analysis' 
          : `Generate ${insightType} insights for this dataset`
      };
      
      const response = await apiService.generateInsights(request);
      setInsights(response);
      toast.success(`${insightType} insights generated successfully!`);
    } catch (error) {
      console.error('Insights generation failed:', error);
      toast.error('Insights generation failed. Please try again.');
    } finally {
      setIsGenerating(false);
      setSelectedInsightType(null);
    }
  };

  const aiProviders = [
    {
      id: 'groq',
      name: 'Groq',
      description: 'Fast & Free (1000 requests/day)',
      icon: Zap,
      color: 'from-green-500 to-green-600',
      status: 'Recommended'
    },
    {
      id: 'huggingface',
      name: 'HuggingFace',
      description: 'Open Source Models',
      icon: Brain,
      color: 'from-purple-500 to-purple-600',
      status: 'Alternative'
    },
    {
      id: 'anthropic',
      name: 'Anthropic Claude',
      description: 'High Quality (Free tier)',
      icon: Sparkles,
      color: 'from-blue-500 to-blue-600',
      status: 'Premium'
    }
  ];

  const quickActions = [
    {
      title: 'Upload New Data',
      description: 'Import a new dataset for insights',
      icon: BookOpen,
      color: 'from-blue-500 to-blue-600',
      onClick: () => navigate('/upload')
    },
    {
      title: 'Run Analysis',
      description: 'Get statistical insights',
      icon: TrendingUp,
      color: 'from-green-500 to-green-600',
      onClick: () => navigate('/analysis')
    },
    {
      title: 'Create Charts',
      description: 'Generate visualizations',
      icon: TrendingUp,
      color: 'from-purple-500 to-purple-600',
      onClick: () => navigate('/charts')
    }
  ];

  return (
    <div className="space-y-6">
      {/* Workflow Progress */}
      <WorkflowProgress />
      
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-8"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">AI Insights</h1>
            <p className="text-white/60 text-lg">
              Discover hidden patterns and get intelligent recommendations
            </p>
          </div>
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg"
          >
            <Brain className="w-8 h-8 text-white" />
          </motion.div>
        </div>
      </motion.div>

      {/* Enhancement Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="glass-card p-4 border-2 border-purple-500/30 bg-gradient-to-r from-purple-500/10 to-blue-500/10"
      >
        <div className="flex items-center space-x-3">
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center"
          >
            <Sparkles className="w-5 h-5 text-purple-400" />
          </motion.div>
          <div>
            <h3 className="text-purple-300 font-semibold">🎯 Enhanced Data Analysis</h3>
            <p className="text-white/70 text-sm">
              Now powered by real pandas statistical analysis + specialized AI prompts for professional business insights
            </p>
          </div>
          <div className="ml-auto">
            <span className="px-3 py-1 bg-purple-500/20 text-purple-300 text-xs font-bold rounded-full">
              NEW
            </span>
          </div>
        </div>
      </motion.div>

      {/* Current File Status */}
      {currentFile ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <h3 className="text-white font-medium">{currentFile.filename}</h3>
                <p className="text-white/60 text-sm">
                  {currentFile.rows_count} rows, {currentFile.columns_count} columns
                </p>
              </div>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/upload')}
              className="btn-secondary"
            >
              Change File
            </motion.button>
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-orange-500/20 rounded-xl flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-orange-400" />
              </div>
              <div>
                <h3 className="text-white font-medium">No file uploaded</h3>
                <p className="text-white/60 text-sm">Upload a CSV file to generate insights</p>
              </div>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/upload')}
              className="btn-primary"
            >
              Upload File
            </motion.button>
          </div>
        </motion.div>
      )}

      {/* AI Provider Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="glass-card p-6"
      >
        <h3 className="text-lg font-semibold text-white mb-4">Choose AI Provider</h3>
        <div className="grid md:grid-cols-3 gap-4">
          {aiProviders.map((provider, index) => {
            const IconComponent = provider.icon;
            const isSelected = selectedProvider === provider.id;
            
            return (
              <motion.button
                key={provider.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedProvider(provider.id)}
                className={`p-4 rounded-xl border transition-all duration-300 ${
                  isSelected
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-white/20 bg-white/5 hover:bg-white/10'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 bg-gradient-to-br ${provider.color} rounded-lg flex items-center justify-center`}>
                    <IconComponent className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 text-left">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-white">{provider.name}</span>
                      {provider.status === 'Recommended' && (
                        <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                          {provider.status}
                        </span>
                      )}
                    </div>
                    <p className="text-white/60 text-sm">{provider.description}</p>
                  </div>
                </div>
              </motion.button>
            );
          })}
        </div>
      </motion.div>

      {/* Insight Types */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {insightTypes.map((insight, index) => {
          const IconComponent = insight.icon;
          const isSelected = selectedInsightType === insight.id;
          const isDisabled = !currentFile || isGenerating;
          
          return (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`glass-card p-6 cursor-pointer relative ${
                isDisabled ? 'opacity-50 cursor-not-allowed' : ''
              } ${insight.isNew ? 'border-2 border-purple-500/40 bg-gradient-to-br from-purple-500/10 to-blue-500/10' : ''}`}
              onClick={() => !isDisabled && handleGenerateInsights(insight.id)}
              whileHover={!isDisabled ? { 
                scale: 1.05,
                boxShadow: insight.isNew ? "0 0 30px rgba(168, 85, 247, 0.4)" : "0 0 30px rgba(59, 130, 246, 0.3)"
              } : {}}
              whileTap={!isDisabled ? { scale: 0.95 } : {}}
            >
              {/* Enhanced Badge */}
              {insight.badge && (
                <div className="absolute -top-2 -right-2">
                  <motion.span
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="px-2 py-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold rounded-full shadow-lg"
                  >
                    {insight.badge}
                  </motion.span>
                </div>
              )}
              
              <div className={`w-12 h-12 bg-gradient-to-br ${insight.color} rounded-xl flex items-center justify-center mb-4`}>
                {isSelected && isGenerating ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    <RefreshCw className="w-6 h-6 text-white" />
                  </motion.div>
                ) : (
                  <IconComponent className="w-6 h-6 text-white" />
                )}
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{insight.title}</h3>
              <p className="text-white/60 text-sm mb-3">{insight.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-white/40 text-xs">~{insight.duration}</span>
                {isSelected && isGenerating && (
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  >
                    <Sparkles className="w-4 h-4 text-yellow-400" />
                  </motion.div>
                )}
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid md:grid-cols-3 gap-6"
      >
        {quickActions.map((action, index) => {
          const IconComponent = action.icon;
          
          return (
            <motion.button
              key={action.title}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ 
                scale: 1.02,
                boxShadow: "0 0 20px rgba(59, 130, 246, 0.2)"
              }}
              whileTap={{ scale: 0.98 }}
              onClick={action.onClick}
              className="w-full flex items-center space-x-3 p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-300 text-white cursor-pointer"
            >
              <div className={`w-10 h-10 bg-gradient-to-br ${action.color} rounded-lg flex items-center justify-center`}>
                <IconComponent className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 text-left">
                <div className="font-medium">{action.title}</div>
                <div className="text-sm opacity-60">{action.description}</div>
              </div>
              <ArrowRight className="w-4 h-4 text-white/40" />
            </motion.button>
          );
        })}
      </motion.div>

      {/* Generated Insights */}
      {insights && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-white">AI Insights</h3>
            <div className="flex space-x-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn-secondary"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn-secondary"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </motion.button>
            </div>
          </div>

          {/* Executive Summary */}
          {insights.insights.executive_summary && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <Lightbulb className="w-5 h-5 text-yellow-400 mr-2" />
                Executive Summary
              </h4>
              <div className="bg-white/5 rounded-xl p-4">
                <p className="text-white/80 leading-relaxed">{insights.insights.executive_summary}</p>
              </div>
            </div>
          )}

          {/* Data Quality Assessment */}
          {insights.insights.data_quality_assessment && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <CheckCircle className="w-5 h-5 text-green-400 mr-2" />
                Data Quality Assessment
              </h4>
              <div className="bg-white/5 rounded-xl p-4">
                <p className="text-white/80 leading-relaxed">{insights.insights.data_quality_assessment}</p>
              </div>
            </div>
          )}

          {/* Key Findings */}
          {insights.insights.key_findings && insights.insights.key_findings.length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <Target className="w-5 h-5 text-blue-400 mr-2" />
                Key Findings
              </h4>
              <div className="space-y-2">
                {insights.insights.key_findings.map((finding: string, index: number) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start space-x-3 p-3 bg-white/5 rounded-lg"
                  >
                    <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0" />
                    <p className="text-white/80 text-sm">{finding}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {insights.insights.recommendations && insights.insights.recommendations.length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <Zap className="w-5 h-5 text-green-400 mr-2" />
                Recommendations
              </h4>
              <div className="space-y-2">
                {insights.insights.recommendations.map((recommendation: string, index: number) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start space-x-3 p-3 bg-white/5 rounded-lg"
                  >
                    <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                    <p className="text-white/80 text-sm">{recommendation}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Next Steps */}
          {insights.insights.next_steps && insights.insights.next_steps.length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <ArrowRight className="w-5 h-5 text-blue-400 mr-2" />
                Next Steps
              </h4>
              <div className="space-y-2">
                {insights.insights.next_steps.map((step: string, index: number) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start space-x-3 p-3 bg-white/5 rounded-lg"
                  >
                    <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0" />
                    <p className="text-white/80 text-sm">{step}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Insights */}
          {insights.insights.detailed_insights && Object.keys(insights.insights.detailed_insights).length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <BookOpen className="w-5 h-5 text-indigo-400 mr-2" />
                Detailed Analysis
              </h4>
              <div className="space-y-4">
                {Object.entries(insights.insights.detailed_insights).map(([key, value], index) => (
                  <motion.div
                    key={key}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white/5 rounded-lg p-4"
                  >
                    <h5 className="text-white font-medium mb-2 capitalize">
                      {key.replace(/_/g, ' ')}
                    </h5>
                    <p className="text-white/80 text-sm leading-relaxed">{String(value)}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Statistical Significance */}
          {insights.insights.statistical_significance && Object.keys(insights.insights.statistical_significance).length > 0 && (
            <div>
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <TrendingUp className="w-5 h-5 text-purple-400 mr-2" />
                Statistical Significance
              </h4>
              <div className="space-y-2">
                {Object.entries(insights.insights.statistical_significance).map(([key, value], index) => (
                  <motion.div
                    key={key}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start space-x-3 p-3 bg-white/5 rounded-lg"
                  >
                    <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 flex-shrink-0" />
                    <div>
                      <p className="text-white/60 text-xs capitalize">{key.replace(/_/g, ' ')}</p>
                      <p className="text-white/80 text-sm">{String(value)}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default Insights; 