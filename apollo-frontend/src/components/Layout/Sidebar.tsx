import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Zap } from 'lucide-react';
import { NavigationItem } from '../../types';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  activeItem: string;
  navigationItems: NavigationItem[];
  onItemClick: (item: NavigationItem) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  activeItem,
  navigationItems,
  onItemClick
}) => {
  const getIconComponent = (iconName: string) => {
    const iconMap: { [key: string]: React.ComponentType<any> } = {
      BarChart3: require('lucide-react').BarChart3,
      Upload: require('lucide-react').Upload,
      TrendingUp: require('lucide-react').TrendingUp,
      Brain: require('lucide-react').Brain,
      Settings: require('lucide-react').Settings,
      HelpCircle: require('lucide-react').HelpCircle,
      Download: require('lucide-react').Download,
      FileText: require('lucide-react').FileText,
      Database: require('lucide-react').Database,
    };
    return iconMap[iconName] || require('lucide-react').Circle;
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          />
          
          {/* Sidebar */}
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 h-full w-80 bg-white/10 backdrop-blur-xl border-r border-white/20 z-50 lg:relative lg:translate-x-0"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/10">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gradient">Apollo AI</h1>
                  <p className="text-sm text-white/60">Data Intelligence</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="lg:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5 text-white" />
              </button>
            </div>

            {/* Navigation */}
            <nav className="p-4 space-y-2">
              {navigationItems.map((item, index) => {
                const IconComponent = getIconComponent(item.icon);
                const isActive = activeItem === item.id;
                
                return (
                  <motion.button
                    key={item.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => onItemClick(item)}
                    className={`w-full flex items-center space-x-3 p-4 rounded-xl transition-all duration-300 group ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 text-white'
                        : 'text-white/70 hover:bg-white/10 hover:text-white'
                    }`}
                  >
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-300 ${
                      isActive
                        ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white'
                        : 'bg-white/10 text-white/70 group-hover:bg-white/20 group-hover:text-white'
                    }`}>
                      <IconComponent className="w-5 h-5" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="font-medium">{item.label}</div>
                      <div className="text-sm opacity-60">{item.description}</div>
                    </div>
                  </motion.button>
                );
              })}
            </nav>

            {/* Footer */}
            <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/10">
              <div className="text-center">
                <p className="text-sm text-white/50">Version 1.0.0</p>
                <p className="text-xs text-white/40 mt-1">Powered by AI</p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default Sidebar; 