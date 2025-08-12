import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, PieChart, TrendingUp, ScatterChart, Activity, Zap } from 'lucide-react';
import ChartRenderer from './ChartRenderer';
import { useUserContext } from '../../context/UserContext';
import { useAppStore } from '../../store/useAppStore';
import { apiService } from '../../services/api';
import toast from 'react-hot-toast';
import WorkflowProgress from '../Workflow/WorkflowProgress';
import { useNavigate } from 'react-router-dom';
import { useNotifications } from '../../hooks/useNotifications';

const ChartGallery: React.FC = () => {
  const { workflow, setCurrentStep, completeStep, setVisualizationResults, setError } = useUserContext();
  const { currentFile } = useAppStore();
  const { success } = useNotifications();
  const [availableCharts, setAvailableCharts] = useState<any>(null);
  const [selectedChart, setSelectedChart] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [chartData, setChartData] = useState<any>(null);
  const navigate = useNavigate();

  const activeFileId = workflow.currentFileId || currentFile?.file_id || null;

  useEffect(() => {
    setCurrentStep('visualization');
    
    if (activeFileId) {
      loadAvailableVisualizations(activeFileId);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeFileId]);

  const loadAvailableVisualizations = async (fileId: string) => {
    if (!fileId) {
      setError('No file selected. Please upload a file first.');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiService.getAvailableVisualizations(fileId);
      setAvailableCharts(response);
      
      if (response.available_visualizations && Object.keys(response.available_visualizations).length > 0) {
        completeStep('visualization');
      }
      
    } catch (error) {
      console.error('Failed to load visualizations:', error);
      setError(`Failed to load visualizations: ${error instanceof Error ? error.message : 'Unknown error'}`);
      toast.error('Failed to load available visualizations');
    } finally {
      setIsLoading(false);
    }
  };

  const generateChart = async (chartType: string, column?: string) => {
    if (!activeFileId) {
      setError('No file selected. Please upload a file first.');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const request = {
        file_id: activeFileId,
        chart_type: chartType,
        column: column,
        columns: column ? [column] : undefined,
        x_column: column,
        y_column: column,
        bins: 20,
        top_n: 10
      };

      const response = await apiService.generateVisualization(request);
      setChartData(response);
      setVisualizationResults(response);
      
      // Show notification with scroll action
      success(
        'Chart Generated!',
        `🎨 Your ${chartType} chart has been created successfully.`,
        {
          label: 'View Chart Below',
          onClick: () => {
            const chartSection = document.getElementById('generated-chart');
            if (chartSection) {
              chartSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
              });
            }
          }
        }
      );
      
      toast.success(`${chartType} chart generated! 📊 Scroll down to view.`);
      
      // Auto-scroll to chart after 2 seconds
      setTimeout(() => {
        const chartSection = document.getElementById('generated-chart');
        if (chartSection) {
          chartSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          });
        }
      }, 2000);
      
    } catch (error) {
      console.error('Failed to generate chart:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(`Failed to generate ${chartType} chart: ${errorMessage}`);
      toast.error(`Failed to generate ${chartType} chart`);
    } finally {
      setIsLoading(false);
    }
  };

  const getChartIcon = (chartType: string) => {
    switch (chartType.toLowerCase()) {
      case 'histogram':
      case 'bar':
        return BarChart3;
      case 'pie':
        return PieChart;
      case 'line':
        return TrendingUp;
      case 'scatter':
        return ScatterChart;
      case 'boxplot':
      case 'heatmap':
        return Activity;
      default:
        return BarChart3;
    }
  };

  const renderChartPreview = (chartType: string, columns: string[]) => {
    const Icon = getChartIcon(chartType);
    
    return (
      <motion.div
        key={chartType}
        className="glass-card p-6 cursor-pointer hover:bg-white/5 transition-all duration-200"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => {
          setSelectedChart(chartType);
          if (columns.length > 0) {
            generateChart(chartType, columns[0]);
          }
        }}
      >
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
            <Icon className="w-6 h-6 text-blue-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white capitalize">
              {chartType.replace('_', ' ')}
            </h3>
            <p className="text-white/60 text-sm">
              {columns.length} column{columns.length !== 1 ? 's' : ''} available
            </p>
          </div>
          <div className="text-white/40">
            <Zap className="w-5 h-5" />
          </div>
        </div>
      </motion.div>
    );
  };

  const renderChartData = () => {
    if (!chartData) return null;

    return (
      <motion.div
        id="generated-chart"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6 mt-6 border-2 border-blue-500/30 bg-gradient-to-br from-blue-500/10 to-purple-500/10"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <motion.div
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 2, repeat: 3 }}
              className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center"
            >
              <BarChart3 className="w-5 h-5 text-blue-400" />
            </motion.div>
            <h3 className="text-xl font-semibold text-white">
              🎨 {selectedChart?.replace('_', ' ')} Chart Generated!
            </h3>
          </div>
          <button
            onClick={() => {
              toast.success('Chart download feature coming soon!');
            }}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Zap className="w-4 h-4" />
            <span>Download</span>
          </button>
        </div>

        <ChartRenderer chartData={chartData.chart_data} className="mb-4" />
        
        {/* Debug info (collapsible) */}
        <details className="mt-4">
          <summary className="text-white/60 text-sm cursor-pointer hover:text-white/80">
            Show Chart Data (Debug)
          </summary>
          <div className="bg-white/5 rounded-lg p-4 mt-2">
            <pre className="text-white/80 text-xs overflow-auto max-h-48">
              {JSON.stringify(chartData, null, 2)}
            </pre>
          </div>
        </details>
      </motion.div>
    );
  };

  if (!activeFileId) {
    return (
      <div className="space-y-6">
        <WorkflowProgress />
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 border border-yellow-500/30 bg-yellow-500/10"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-yellow-500/20 rounded-xl flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-yellow-400" />
              </div>
              <div>
                <h3 className="text-white font-medium">No file selected</h3>
                <p className="text-white/60 text-sm">Upload a CSV to create visualizations</p>
              </div>
            </div>
            <button
              onClick={() => navigate('/upload')}
              className="px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 border border-yellow-500/40 rounded-lg text-yellow-300 text-sm font-medium transition-all"
            >
              Go to Upload
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Workflow Progress */}
      <WorkflowProgress />

      {/* Header */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Data Visualizations</h1>
            <p className="text-white/60">
              Create interactive charts and graphs from your data
            </p>
          </div>
          <button
            onClick={() => loadAvailableVisualizations(activeFileId)}
            disabled={isLoading || !activeFileId}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Zap className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="glass-card p-6 text-center"
        >
          <div className="flex items-center justify-center space-x-3">
            <div className="w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            <span className="text-white">Loading visualizations...</span>
          </div>
        </motion.div>
      )}

      {/* Available Charts */}
      {availableCharts && !isLoading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h2 className="text-2xl font-bold text-white">Available Chart Types</h2>
          
          {Object.entries(availableCharts.available_visualizations || {}).map(([chartType, columns]) => (
            <div key={chartType}>
              {renderChartPreview(chartType as string, columns as string[])}
            </div>
          ))}
        </motion.div>
      )}

      {/* Generated Chart Data */}
      {renderChartData()}

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
              <p className="text-white/70">{workflow.error}</p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ChartGallery; 