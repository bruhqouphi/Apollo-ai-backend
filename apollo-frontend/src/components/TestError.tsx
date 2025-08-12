import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, CheckCircle, XCircle, Upload } from 'lucide-react';
import { apiService, API_BASE_URL } from '../services/api';

const TestError: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [apiErrors, setApiErrors] = useState<string[]>([]);
  const [testFile, setTestFile] = useState<File | null>(null);

  useEffect(() => {
    const testBackend = async () => {
      try {
        const response = await apiService.healthCheck();
        console.log('Backend health check response:', response);
        setBackendStatus('online');
      } catch (error) {
        console.error('Backend health check failed:', error);
        setBackendStatus('offline');
        setApiErrors(prev => [...prev, `Backend connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`]);
      }
    };

    testBackend();
  }, []);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setTestFile(file);
    }
  };

  const testApiEndpoints = async () => {
    const errors: string[] = [];
    
    // Test file upload endpoint with a real file
    if (testFile) {
      try {
        const response = await apiService.uploadFile(testFile);
        console.log('Upload test successful:', response);
        // Test analysis endpoint with the uploaded file
        if (response.file_id) {
          try {
            await apiService.analyzeData({
              file_id: response.file_id,
              include_correlation: true,
              include_outliers: true,
              include_statistical_tests: true
            });
            console.log('Analysis test successful');
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            errors.push(`Analysis endpoint error: ${errorMessage}`);
          }
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        errors.push(`Upload endpoint error: ${errorMessage}`);
      }
    } else {
      errors.push('Please select a file to test upload functionality');
    }

    setApiErrors(errors);
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-8"
      >
        <h1 className="text-3xl font-bold text-white mb-6">System Diagnostics</h1>
        
        {/* Backend Status */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-white mb-4">Backend Status</h2>
          <div className="flex items-center space-x-3">
            {backendStatus === 'checking' && (
              <div className="w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            )}
            {backendStatus === 'online' && (
              <CheckCircle className="w-6 h-6 text-green-400" />
            )}
            {backendStatus === 'offline' && (
              <XCircle className="w-6 h-6 text-red-400" />
            )}
            <span className={`font-medium ${
              backendStatus === 'online' ? 'text-green-400' : 
              backendStatus === 'offline' ? 'text-red-400' : 'text-blue-400'
            }`}>
              {backendStatus === 'checking' ? 'Checking...' :
               backendStatus === 'online' ? 'Backend Online' : 'Backend Offline'}
            </span>
          </div>
        </div>

        {/* File Upload for Testing */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-white mb-4">Test File Upload</h2>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <input
                type="file"
                accept=".csv,.xls,.xlsx"
                onChange={handleFileChange}
                className="block w-full text-sm text-white/60 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-blue-500 file:text-white hover:file:bg-blue-600 file:cursor-pointer"
              />
              {testFile && (
                <span className="text-green-400 text-sm">
                  ✓ {testFile.name} selected
                </span>
              )}
            </div>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={testApiEndpoints}
              disabled={!testFile}
              className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                testFile 
                  ? 'bg-blue-500 text-white hover:bg-blue-600' 
                  : 'bg-gray-500 text-gray-300 cursor-not-allowed'
              }`}
            >
              <Upload className="w-4 h-4 inline mr-2" />
              Test API Endpoints
            </motion.button>
          </div>
        </div>

        {/* Error Display */}
        {apiErrors.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-xl font-semibold text-white mb-4">API Test Results</h2>
            {apiErrors.map((error, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`flex items-start space-x-3 p-4 rounded-lg ${
                  error.includes('successful') 
                    ? 'bg-green-500/10 border border-green-500/20' 
                    : 'bg-red-500/10 border border-red-500/20'
                }`}
              >
                {error.includes('successful') ? (
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
                )}
                <span className={`text-sm ${
                  error.includes('successful') ? 'text-green-400' : 'text-red-400'
                }`}>
                  {error}
                </span>
              </motion.div>
            ))}
          </div>
        )}

        {/* Environment Info */}
        <div className="mt-8 p-4 bg-white/5 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-3">Environment Information</h3>
          <div className="space-y-2 text-sm text-white/60">
            <div>API Base URL: {API_BASE_URL || '(relative / proxied)'}</div>
            <div>Node Environment: {process.env.NODE_ENV}</div>
            <div>React Version: {React.version}</div>
            <div>Backend Status: {backendStatus === 'online' ? '✅ Connected' : '❌ Disconnected'}</div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default TestError; 