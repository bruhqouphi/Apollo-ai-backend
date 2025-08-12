import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import { 
  Download, 
  Settings, 
  HelpCircle 
} from 'lucide-react';

// Components
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import Dashboard from './components/Dashboard/Dashboard';
import FileUpload from './components/Upload/FileUpload';
import DataAnalysis from './components/Analysis/DataAnalysis';
import ChartGallery from './components/Charts/ChartGallery';
import Insights from './components/Insights/Insights';
import LandingPage from './components/Landing/LandingPage';
import { ErrorBoundaryWrapper } from './components/ErrorBoundary';

// Context
import { AuthProvider } from './context/AuthContext';
import { UserContextProvider } from './context/UserContext';

// Store
import { useAppStore } from './store/useAppStore';

// Navigation items
const navigationItems = [
  { 
    id: 'dashboard', 
    label: 'Dashboard', 
    path: '/dashboard', 
    icon: 'BarChart3', 
    description: 'Overview and statistics' 
  },
  { 
    id: 'upload', 
    label: 'Upload Data', 
    path: '/upload', 
    icon: 'Upload', 
    description: 'Upload your datasets' 
  },
  { 
    id: 'analysis', 
    label: 'Data Analysis', 
    path: '/analysis', 
    icon: 'TrendingUp', 
    description: 'Statistical analysis' 
  },
  { 
    id: 'charts', 
    label: 'Visualizations', 
    path: '/charts', 
    icon: 'BarChart3', 
    description: 'Create charts and graphs' 
  },
  { 
    id: 'insights', 
    label: 'AI Insights', 
    path: '/insights', 
    icon: 'Brain', 
    description: 'AI-powered insights' 
  },
  { 
    id: 'downloads', 
    label: 'Export', 
    path: '/downloads', 
    icon: 'Download', 
    description: 'Export reports and data' 
  },
  { 
    id: 'settings', 
    label: 'Settings', 
    path: '/settings', 
    icon: 'Settings', 
    description: 'Preferences and configuration' 
  },
  { 
    id: 'help', 
    label: 'Help & Support', 
    path: '/help', 
    icon: 'HelpCircle', 
    description: 'Documentation and support' 
  }
];

const AppContent: React.FC = () => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const { setLoading } = useAppStore();

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setIsLoading(false);
      setLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, [setLoading]);

  const getActiveItem = () => {
    const path = location.pathname;
    if (path === '/') return 'dashboard';
    return path.substring(1);
  };

  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/') return 'Apollo AI';
    const item = navigationItems.find(item => item.path === path);
    return item ? item.label : 'Apollo AI';
  };

  const handleSidebarItemClick = () => {
    setSidebarOpen(false);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg"
          >
            <div className="w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin" />
          </motion.div>
          <h1 className="text-2xl font-bold text-white mb-2">Apollo AI</h1>
          <p className="text-white/60">Loading your workspace...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-float" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '4s' }} />
      </div>

      {/* Main Layout */}
      <div className="relative z-10 flex min-h-screen">
        {/* Sidebar - Only show on non-landing pages */}
        {location.pathname !== '/' && (
          <Sidebar
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            activeItem={getActiveItem()}
            navigationItems={navigationItems}
            onItemClick={handleSidebarItemClick}
          />
        )}

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header - Only show on non-landing pages */}
          {location.pathname !== '/' && (
            <Header
              onMenuClick={() => setSidebarOpen(true)}
              title={getPageTitle()}
            />
          )}

          {/* Page Content */}
          <main className={`flex-1 overflow-y-auto ${location.pathname !== '/' ? 'p-6' : ''}`}>
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
              >
                <Routes location={location}>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/upload" element={<FileUpload />} />
                  <Route path="/analysis" element={<DataAnalysis />} />
                  <Route path="/charts" element={<ChartGallery />} />
                  <Route path="/insights" element={<Insights />} />
                  <Route path="/downloads" element={<div className="glass-card p-8 text-center">
                    <Download className="w-16 h-16 mx-auto mb-4 text-blue-400" />
                    <h2 className="text-2xl font-bold mb-2">Downloads</h2>
                    <p className="text-white/70">Download your reports and visualizations</p>
                  </div>} />
                  <Route path="/settings" element={<div className="glass-card p-8 text-center">
                    <Settings className="w-16 h-16 mx-auto mb-4 text-blue-400" />
                    <h2 className="text-2xl font-bold mb-2">Settings</h2>
                    <p className="text-white/70">Configure your preferences</p>
                  </div>} />
                  <Route path="/help" element={<div className="glass-card p-8 text-center">
                    <HelpCircle className="w-16 h-16 mx-auto mb-4 text-blue-400" />
                    <h2 className="text-2xl font-bold mb-2">Help & Support</h2>
                    <p className="text-white/70">Get help and documentation</p>
                  </div>} />
                </Routes>
              </motion.div>
            </AnimatePresence>
          </main>
        </div>
      </div>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'rgba(15, 23, 42, 0.9)',
            color: '#fff',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
          },
        }}
      />
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <UserContextProvider>
          <ErrorBoundaryWrapper>
            <AppContent />
          </ErrorBoundaryWrapper>
        </UserContextProvider>
      </AuthProvider>
    </Router>
  );
};

export default App;
