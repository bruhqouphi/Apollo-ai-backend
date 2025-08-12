import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  ArcElement,
  ScatterController,
  LineController,
  BarController,
  PieController,
} from 'chart.js';
import { Bar, Line, Pie, Scatter } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  ScatterController,
  LineController,
  BarController,
  PieController
);

interface ChartRendererProps {
  chartData: any;
  className?: string;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({ chartData, className = "" }) => {
  if (!chartData || !chartData.type) {
    return (
      <div className={`flex items-center justify-center h-64 bg-white/5 rounded-lg ${className}`}>
        <p className="text-white/60">No chart data available</p>
      </div>
    );
  }

  const { type, data, options } = chartData;

  // Default options for better appearance
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            size: 12
          }
        }
      },
      title: {
        color: 'rgba(255, 255, 255, 0.9)',
        font: {
          size: 16,
          weight: 'bold' as const
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
          font: {
            size: 11
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        title: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            size: 12,
            weight: 'bold' as const
          }
        }
      },
      y: {
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
          font: {
            size: 11
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        title: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            size: 12,
            weight: 'bold' as const
          }
        }
      }
    }
  };

  // Merge with provided options
  const mergedOptions = {
    ...defaultOptions,
    ...options,
    plugins: {
      ...defaultOptions.plugins,
      ...options?.plugins
    },
    scales: {
      ...defaultOptions.scales,
      ...options?.scales
    }
  };

  const renderChart = () => {
    switch (type.toLowerCase()) {
      case 'bar':
        return <Bar data={data} options={mergedOptions} />;
      case 'line':
        return <Line data={data} options={mergedOptions} />;
      case 'pie':
        return <Pie data={data} options={mergedOptions} />;
      case 'scatter':
        return <Scatter data={data} options={mergedOptions} />;
      default:
        return (
          <div className="flex items-center justify-center h-64 bg-white/5 rounded-lg">
            <div className="text-center">
              <p className="text-white/60 mb-2">Chart type "{type}" not supported yet</p>
              <p className="text-white/40 text-sm">Supported: bar, line, pie, scatter</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className={`bg-white/5 rounded-lg p-4 ${className}`}>
      <div className="h-96">
        {renderChart()}
      </div>
      {chartData.metadata && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <p className="text-white/60 text-sm">
            {Object.entries(chartData.metadata).slice(0, 3).map(([key, value]) => (
              <span key={key} className="mr-4">
                <span className="text-white/40">{key}:</span> {String(value)}
              </span>
            ))}
          </p>
        </div>
      )}
    </div>
  );
};

export default ChartRenderer;