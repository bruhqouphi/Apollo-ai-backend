import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../../store/useAppStore';
import { apiService } from '../../services/api';
import toast from 'react-hot-toast';
import { useUserContext } from '../../context/UserContext';

const FileUpload: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const { addUploadedFile, setCurrentFile } = useAppStore();
  const { setFileId, setCurrentStep, completeStep } = useUserContext();
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setIsUploading(true);
    setUploadError(null);

    try {
      // Optional health check: if it fails, continue and let upload determine availability
      try {
        await apiService.healthCheck();
      } catch (error) {
        console.warn('Health check failed, attempting upload anyway');
      }

      const response = await apiService.uploadFile(file);
      
      if (response.success) {
        const uploadedFile = {
          file_id: response.file_id,
          filename: response.filename,
          file_size: response.file_size,
          rows_count: response.rows_count,
          columns_count: response.columns_count,
          columns: response.columns,
          upload_time: response.timestamp || new Date().toISOString()
        };

        addUploadedFile(uploadedFile);
        setCurrentFile(uploadedFile);
        setFileId(uploadedFile.file_id);
        setCurrentStep('analysis');
        completeStep('upload');
        toast.success('🎉 File uploaded successfully! Preparing your analysis...');
        
        // Navigate to analysis page after successful upload
        setTimeout(() => {
          navigate('/analysis');
        }, 1200);
      } else {
        throw new Error(response.message || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Upload failed. Please try again.';
      setUploadError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  }, [addUploadedFile, setCurrentFile, setFileId, setCurrentStep, completeStep, navigate]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    multiple: false,
    maxSize: 50 * 1024 * 1024, // 50MB
    onDragEnter: () => {
      setUploadError(null);
    },
    onDragLeave: () => {},
    onDragOver: () => {}
  });

  const handleRetry = () => {
    setUploadError(null);
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-8 text-center"
      >
        <h1 className="text-3xl font-bold text-white mb-4">Upload Your Data</h1>
        <p className="text-white/60 text-lg mb-8">
          Upload CSV files to start analyzing your data with AI-powered insights
        </p>

        {/* Error Display */}
        {uploadError && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 text-left">
                <AlertCircle className="w-5 h-5 text-red-400" />
                <span className="text-red-300 text-sm">{uploadError}</span>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleRetry}
                className="px-3 py-1.5 text-xs border border-red-500/40 text-red-200 hover:bg-red-500/10 rounded-lg transition-colors"
              >
                Retry
              </motion.button>
            </div>
          </motion.div>
        )}

        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 transition-all duration-300 cursor-pointer ${
            isDragActive
              ? 'border-blue-400 bg-blue-500/10'
              : isDragReject
              ? 'border-red-400 bg-red-500/10'
              : uploadError
              ? 'border-red-400 bg-red-500/5'
              : 'border-white/20 hover:border-white/40 hover:bg-white/5'
          }`}
        >
          <input {...getInputProps()} type="file" />
          
          <motion.div
            animate={{ scale: isDragActive ? 1.05 : 1 }}
            className="flex flex-col items-center space-y-4"
          >
            {isUploading ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center"
              >
                <RefreshCw className="w-10 h-10 text-white" />
              </motion.div>
            ) : (
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
                <Upload className="w-10 h-10 text-white" />
              </div>
            )}
            
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">
                {isUploading 
                  ? 'Uploading your file...' 
                  : isDragActive 
                  ? 'Drop your file here' 
                  : 'Drag & drop your file here'}
              </h3>
              <p className="text-white/60">
                {isUploading ? 'Please wait while we process your data' : 'or click to browse files'}
              </p>
            </div>

            {isDragReject && (
              <div className="flex items-center space-x-2 text-red-400">
                <AlertCircle className="w-5 h-5" />
                <span>File type not supported</span>
              </div>
            )}

            <div className="text-sm text-white/40">
              Supports CSV, XLS, XLSX files up to 50MB
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* Upload Guidelines */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid md:grid-cols-3 gap-6"
      >
        <div className="glass-card p-6">
          <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mb-4">
            <FileText className="w-6 h-6 text-blue-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">CSV Format</h3>
          <p className="text-white/60 text-sm">
            Upload comma-separated values files with headers in the first row
          </p>
        </div>

        <div className="glass-card p-6">
          <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center mb-4">
            <CheckCircle className="w-6 h-6 text-green-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Data Quality</h3>
          <p className="text-white/60 text-sm">
            Ensure your data is clean and well-structured for best results
          </p>
        </div>

        <div className="glass-card p-6">
          <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center mb-4">
            <AlertCircle className="w-6 h-6 text-purple-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">File Size</h3>
          <p className="text-white/60 text-sm">
            Maximum file size is 50MB. Larger files may take longer to process
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default FileUpload; 