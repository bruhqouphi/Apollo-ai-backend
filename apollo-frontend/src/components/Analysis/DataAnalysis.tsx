import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Brain, 
  TrendingUp, 
  AlertCircle, 
  Activity,
  BarChart3,
  Zap,
  ArrowRight,
  CheckCircle,
  Clock,
  Sparkles
} from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import WorkflowProgress from '../Workflow/WorkflowProgress';
import { useUserContext } from '../../context/UserContext';
import { apiService } from '../../services/api';
import toast from 'react-hot-toast';
import { useNotifications } from '../../hooks/useNotifications';

const DataAnalysis: React.FC = () => {
  const navigate = useNavigate();
  const { currentFile, analysisResult, setAnalysisResult } = useAppStore();
  const { setCurrentStep, completeStep } = useUserContext();
  const { success, error: notifyError } = useNotifications();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState<string | null>(null);
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  const [showWelcomeMessage, setShowWelcomeMessage] = useState(false);
  const [autoAnalysisStarted, setAutoAnalysisStarted] = useState(false);
  // Column selection state (unused for now - will be implemented in future)
  // const [showColumnSelector, setShowColumnSelector] = useState(false);
  // const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  // const [pendingAnalysisType, setPendingAnalysisType] = useState<string | null>(null);

  // Show welcome message if user just uploaded a file
  React.useEffect(() => {
    setCurrentStep('analysis');
    if (currentFile) {
      setShowWelcomeMessage(true);
      const timer = setTimeout(() => setShowWelcomeMessage(false), 8000);
      return () => clearTimeout(timer);
    }
  }, [currentFile]);

  // Auto-start comprehensive analysis when file is uploaded
  React.useEffect(() => {
    if (currentFile && !analysisResult && !autoAnalysisStarted) {
      setAutoAnalysisStarted(true);
      // Auto-start analysis after a short delay
      const timer = setTimeout(() => {
        handleAnalysis('comprehensive');
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [currentFile, analysisResult, autoAnalysisStarted]);

  const analysisTypes = [
    {
      id: 'comprehensive',
      title: '🚀 Quick Analysis',
      description: 'Complete analysis with AI insights',
      icon: Zap,
      color: 'from-purple-500 to-pink-600',
      duration: '30s',
      recommended: true
    },
    {
      id: 'statistical',
      title: '📊 Statistical Analysis',
      description: 'Basic statistics and data distribution',
      icon: Activity,
      color: 'from-blue-500 to-blue-600',
      duration: '20s'
    },
    {
      id: 'correlation',
      title: '🔗 Correlation Analysis',
      description: 'Find relationships between variables',
      icon: TrendingUp,
      color: 'from-green-500 to-green-600',
      duration: '25s'
    },
    {
      id: 'outliers',
      title: '⚠️ Outlier Detection',
      description: 'Identify unusual data points',
      icon: AlertCircle,
      color: 'from-orange-500 to-orange-600',
      duration: '30s'
    }
  ];

  const handleAnalysis = React.useCallback(async (analysisType: string) => {
    if (!currentFile) {
      toast.error('Please upload a file first');
      navigate('/upload');
      return;
    }

    setIsAnalyzing(true);
    setSelectedAnalysis(analysisType);

    try {
      const request = {
        file_id: currentFile.file_id,
        include_correlation: analysisType === 'correlation' || analysisType === 'comprehensive',
        include_outliers: analysisType === 'outliers' || analysisType === 'comprehensive',
        include_statistical_tests: analysisType === 'statistical' || analysisType === 'comprehensive',
        outlier_method: 'iqr' as const,
        confidence_level: 0.95,
        target_columns: selectedColumns.length > 0 ? selectedColumns : undefined
      };
      
      const response = await apiService.analyzeData(request);
      setAnalysisResult(response);
      completeStep('analysis');
      
      if (analysisType === 'comprehensive') {
        // Show notification with action button
        success(
          'Analysis Complete!',
          '🎉 Your comprehensive analysis is ready with detailed insights.',
          {
            label: 'View Results',
            onClick: () => {
              navigate('/insights');
            }
          }
        );
        
        // Keep the toast for immediate feedback
        toast.success('🎉 Analysis complete! Check out your insights below.');
        
        // Auto-navigate to insights after comprehensive analysis
        setTimeout(() => {
          navigate('/insights');
        }, 1500);
      } else {
        // Show notification with action button for manual analysis
        success(
          'Analysis Complete!',
          `Your ${analysisType} analysis has been completed successfully.`,
          {
            label: 'View Results Below',
            onClick: () => {
              // Scroll to results section smoothly
              const resultsSection = document.getElementById('analysis-results');
              if (resultsSection) {
                resultsSection.scrollIntoView({ 
                  behavior: 'smooth', 
                  block: 'start' 
                });
              }
            }
          }
        );
        
        toast.success(`${analysisType} analysis completed! 📊 Scroll down to see results.`);
        
        // Auto-scroll to results after 2 seconds
        setTimeout(() => {
          const resultsSection = document.getElementById('analysis-results');
          if (resultsSection) {
            resultsSection.scrollIntoView({ 
              behavior: 'smooth', 
              block: 'start' 
            });
          }
        }, 2000);
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Analysis failed. Please try again.';
      
      // Show error notification
      notifyError(
        'Analysis Failed',
        `❌ ${errorMessage}`,
        {
          label: 'Try Again',
          onClick: () => {
            if (currentFile) {
              handleAnalysis('comprehensive');
            }
          }
        }
      );
      
      toast.error(`❌ ${errorMessage}`);
      
      // If auto-analysis fails, show manual options
      if (analysisType === 'comprehensive') {
        toast.success('💡 You can try manual analysis options below');
      }
    } finally {
      setIsAnalyzing(false);
      setSelectedAnalysis(null);
    }
  }, [currentFile, navigate, setAnalysisResult, success, notifyError, selectedColumns, completeStep]);

  // Column selection handlers (unused for now - will be implemented in future)
  // const handleSelectAllColumns = () => {
  //   if (currentFile) {
  //     setSelectedColumns([...currentFile.columns]);
  //   }
  // };

  // const handleDeselectAllColumns = () => {
  //   setSelectedColumns([]);
  // };

  // const handleColumnToggle = (column: string) => {
  //   setSelectedColumns(prev => 
  //     prev.includes(column) 
  //       ? prev.filter(col => col !== column)
  //       : [...prev, column]
  //   );
  // };

  const quickActions = [
    {
      title: 'Upload New Data',
      description: 'Import a new dataset for analysis',
      icon: Activity,
      color: 'from-blue-500 to-blue-600',
      onClick: () => navigate('/upload')
    },
    {
      title: 'View Charts',
      description: 'Explore visualizations',
      icon: BarChart3,
      color: 'from-purple-500 to-purple-600',
      onClick: () => navigate('/charts')
    },
    {
      title: 'AI Insights',
      description: 'Get intelligent recommendations',
      icon: Brain,
      color: 'from-green-500 to-green-600',
      onClick: () => navigate('/insights')
    }
  ];

  return (
    <div className="space-y-6">
      {/* Workflow */}
      <WorkflowProgress />
      {/* Welcome Message */}
      {showWelcomeMessage && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="glass-card p-6 bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/20"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <h3 className="text-white font-medium">File Uploaded Successfully!</h3>
                <p className="text-white/60 text-sm">
                  Your data is ready for analysis. Choose an analysis type below to get started.
                </p>
              </div>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowWelcomeMessage(false)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <AlertCircle className="w-5 h-5 text-white/60" />
            </motion.button>
          </div>
        </motion.div>
      )}

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-8"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Data Analysis</h1>
            <p className="text-white/60 text-lg">
              AI-powered insights and statistical analysis
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

      {/* Current File Status */}
      {currentFile ? (
        <>
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

          {/* Column Selector */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="glass-card p-6"
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-medium">Select Columns</h3>
              <div className="space-x-2">
                <button
                  className="px-3 py-1 text-xs rounded-lg border border-white/20 hover:bg-white/10 text-white"
                  onClick={() => currentFile && setSelectedColumns(currentFile.columns)}
                >
                  Select All
                </button>
                <button
                  className="px-3 py-1 text-xs rounded-lg border border-white/20 hover:bg-white/10 text-white"
                  onClick={() => setSelectedColumns([])}
                >
                  Clear
                </button>
              </div>
            </div>
            {currentFile && (
              <div className="flex flex-wrap gap-2">
                {currentFile.columns.map((col: string) => {
                  const selected = selectedColumns.includes(col);
                  return (
                    <button
                      key={col}
                      onClick={() =>
                        setSelectedColumns(prev =>
                          prev.includes(col) ? prev.filter(c => c !== col) : [...prev, col]
                        )
                      }
                      className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                        selected
                          ? 'bg-blue-500/20 border-blue-500/40 text-blue-300'
                          : 'bg-white/5 border-white/20 text-white/70 hover:bg-white/10'
                      }`}
                    >
                      {col}
                    </button>
                  );
                })}
              </div>
            )}
          </motion.div>

          {/* Analysis Prompt */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card p-8 bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-pink-500/10 border border-purple-500/20"
          >
            <div className="text-center">
              <motion.div
                animate={{ 
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ 
                  duration: 3, 
                  repeat: Infinity, 
                  repeatDelay: 2 
                }}
                className="w-24 h-24 bg-gradient-to-br from-purple-500 via-blue-500 to-pink-600 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl"
              >
                <Zap className="w-12 h-12 text-white" />
              </motion.div>
              
              <h2 className="text-3xl font-bold text-white mb-4">
                🎯 Let's Unlock Your Data's Secrets!
              </h2>
              <p className="text-white/70 text-lg mb-6 max-w-3xl mx-auto">
                Your file <span className="text-purple-400 font-bold">{currentFile.filename}</span> is ready! 
                We found <span className="text-blue-400 font-bold">{currentFile.rows_count} data points</span> across 
                <span className="text-green-400 font-bold"> {currentFile.columns_count} columns</span>.
              </p>

              {/* Auto-analysis progress */}
              {isAnalyzing && selectedAnalysis === 'comprehensive' && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-8 p-6 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-2xl border border-purple-500/30"
                >
                  <div className="flex items-center justify-center space-x-4 mb-4">
                    <Clock className="w-6 h-6 text-purple-400 animate-spin" />
                    <span className="text-purple-400 font-medium text-lg">AI is analyzing your data...</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: "100%" }}
                      transition={{ duration: 30, ease: "easeInOut" }}
                      className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full"
                    />
                  </div>
                  <p className="text-white/60 text-sm mt-2">This will take about 30 seconds</p>
                </motion.div>
              )}

              {/* Analysis Options */}
              {!isAnalyzing && (
                <div className="space-y-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-semibold text-white mb-2">Choose Your Analysis:</h3>
                    <p className="text-white/60">We recommend starting with Quick Analysis for the best experience</p>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Recommended Option */}
                    <motion.div
                      whileHover={{ scale: 1.02 }}
                      className="relative"
                    >
                      <div className="absolute -top-3 -right-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold px-3 py-1 rounded-full">
                        RECOMMENDED
                      </div>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleAnalysis('comprehensive')}
                        className="w-full p-6 rounded-2xl border-2 border-purple-500/30 bg-gradient-to-br from-purple-500/20 to-pink-500/20 hover:from-purple-500/30 hover:to-pink-500/30 transition-all shadow-lg"
                      >
                        <div className="text-center">
                          <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <Zap className="w-8 h-8 text-white" />
                          </div>
                          <h3 className="text-white font-bold text-lg mb-2">🚀 Quick Analysis</h3>
                          <p className="text-white/70 text-sm mb-3">Complete analysis with AI insights</p>
                          <div className="text-purple-400 font-medium">30 seconds</div>
                        </div>
                      </motion.button>
                    </motion.div>

                    {/* Other Options */}
                    <div className="grid grid-cols-1 gap-4">
                      {analysisTypes.filter(a => a.id !== 'comprehensive').map((analysis) => (
                        <motion.button
                          key={analysis.id}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleAnalysis(analysis.id)}
                          className="p-4 rounded-xl border border-white/20 bg-white/5 hover:bg-white/10 transition-all text-left"
                        >
                          <div className="flex items-center space-x-4">
                            <div className={`w-12 h-12 bg-gradient-to-br ${analysis.color} rounded-xl flex items-center justify-center`}>
                              <analysis.icon className="w-6 h-6 text-white" />
                            </div>
                            <div className="flex-1">
                              <h3 className="text-white font-medium">{analysis.title}</h3>
                              <p className="text-white/60 text-sm">{analysis.description}</p>
                            </div>
                            <div className="text-blue-400 text-sm font-medium">{analysis.duration}</div>
                          </div>
                        </motion.button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Quick Actions */}
              {!isAnalyzing && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="mt-8 pt-6 border-t border-white/10"
                >
                  <p className="text-white/60 text-sm mb-4">Or explore other features:</p>
                  <div className="flex flex-wrap justify-center gap-3">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => navigate('/charts')}
                      className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 rounded-lg text-blue-400 text-sm font-medium transition-all"
                    >
                      📊 View Charts
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => navigate('/insights')}
                      className="px-4 py-2 bg-green-500/20 hover:bg-green-500/30 border border-green-500/30 rounded-lg text-green-400 text-sm font-medium transition-all"
                    >
                      🧠 AI Insights
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => navigate('/upload')}
                      className="px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded-lg text-purple-400 text-sm font-medium transition-all"
                    >
                      📁 Upload New File
                    </motion.button>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        </>
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
                <p className="text-white/60 text-sm">Upload a CSV file to start analysis</p>
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

      {/* Analysis Types */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {analysisTypes.map((analysis, index) => {
          const IconComponent = analysis.icon;
          const isSelected = selectedAnalysis === analysis.id;
          const isDisabled = !currentFile || isAnalyzing;
          
          return (
            <motion.div
              key={analysis.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`glass-card p-6 cursor-pointer ${
                isDisabled ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              onClick={() => !isDisabled && handleAnalysis(analysis.id)}
              whileHover={!isDisabled ? { 
                scale: 1.05,
                boxShadow: "0 0 30px rgba(59, 130, 246, 0.3)"
              } : {}}
              whileTap={!isDisabled ? { scale: 0.95 } : {}}
            >
              <div className={`w-12 h-12 bg-gradient-to-br ${analysis.color} rounded-xl flex items-center justify-center mb-4`}>
                {isSelected && isAnalyzing ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    <Clock className="w-6 h-6 text-white" />
                  </motion.div>
                ) : (
                  <IconComponent className="w-6 h-6 text-white" />
                )}
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{analysis.title}</h3>
              <p className="text-white/60 text-sm mb-3">{analysis.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-white/40 text-xs">~{analysis.duration}</span>
                {isSelected && isAnalyzing && (
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  >
                    <Zap className="w-4 h-4 text-yellow-400" />
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

      {/* Analysis Results */}
      {analysisResult && (
        <motion.div
          id="analysis-results"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6 border-2 border-green-500/30 bg-gradient-to-br from-green-500/10 to-blue-500/10"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: 3 }}
                className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center"
              >
                <CheckCircle className="w-5 h-5 text-green-400" />
              </motion.div>
              <h3 className="text-xl font-semibold text-white">📊 Analysis Results</h3>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-secondary"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Export
            </motion.button>
          </div>
          <div className="bg-white/5 rounded-xl p-4">
            <pre className="text-white/80 text-sm overflow-x-auto">
              {JSON.stringify(analysisResult, null, 2)}
            </pre>
          </div>
        </motion.div>
      )}

      {/* Column Selector Modal - Disabled for now */}
      {/* TODO: Implement column selection in future version */}
    </div>
  );
};

export default DataAnalysis; 