import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Menu, Bell, LogIn } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../Search/SearchBar';
import LoginModal from '../Auth/LoginModal';
import SignupModal from '../Auth/SignupModal';
import UserProfileDropdown from '../Auth/UserProfileDropdown';
import NotificationPanel from '../Notifications/NotificationPanel';
import { useNotifications } from '../../hooks/useNotifications';

interface HeaderProps {
  onMenuClick: () => void;
  title: string;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick, title }) => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showSignupModal, setShowSignupModal] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const { unreadCount } = useNotifications();

  const handleSearch = (query: string) => {
    console.log('Search query:', query);
    // Implement global search functionality
  };

  const handleSearchResultSelect = (result: any) => {
    navigate(result.path);
  };

  const handleAuthClick = () => {
    setShowLoginModal(true);
  };

  const switchToSignup = () => {
    setShowLoginModal(false);
    setShowSignupModal(true);
  };

  const switchToLogin = () => {
    setShowSignupModal(false);
    setShowLoginModal(true);
  };

  return (
    <>
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card border-b border-white/10 p-4 lg:p-6"
      >
        <div className="flex items-center justify-between">
          {/* Left Section */}
          <div className="flex items-center space-x-4">
            <button
              onClick={onMenuClick}
              className="lg:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              <Menu className="w-6 h-6 text-white" />
            </button>
            
            <div>
              <h1 className="text-2xl font-bold text-white">{title}</h1>
              <p className="text-sm text-white/60">
                {isAuthenticated ? `Welcome back, ${user?.name}` : 'Welcome to Apollo AI'}
              </p>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="hidden md:block w-80">
              <SearchBar onSearch={handleSearch} onResultSelect={handleSearchResultSelect} />
            </div>

            {/* Notifications */}
            <button 
              onClick={() => setShowNotifications(true)}
              className="relative p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              <Bell className="w-5 h-5 text-white" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs font-medium">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                </span>
              )}
            </button>

            {/* User Profile / Auth */}
            {isAuthenticated ? (
              <UserProfileDropdown />
            ) : (
              <button
                onClick={handleAuthClick}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg transition-all duration-200 transform hover:scale-105"
              >
                <LogIn className="w-4 h-4 text-white" />
                <span className="text-white font-medium text-sm">Sign In</span>
              </button>
            )}
          </div>
        </div>
      </motion.header>

      {/* Auth Modals */}
      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        onSwitchToSignup={switchToSignup}
      />
      
      <SignupModal
        isOpen={showSignupModal}
        onClose={() => setShowSignupModal(false)}
        onSwitchToLogin={switchToLogin}
      />

      {/* Notification Panel */}
      <NotificationPanel
        isOpen={showNotifications}
        onClose={() => setShowNotifications(false)}
      />
    </>
  );
};

export default Header; 