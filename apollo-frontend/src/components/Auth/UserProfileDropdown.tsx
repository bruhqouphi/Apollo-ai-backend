import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, 
  Settings, 
  Shield, 
  CreditCard, 
  HelpCircle, 
  LogOut,
  ChevronDown,
  Mail,
  Crown
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';

const UserProfileDropdown: React.FC = () => {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close dropdown on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const handleLogout = () => {
    logout();
    setIsOpen(false);
    toast.success('Logged out successfully');
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const menuItems = [
    {
      icon: User,
      label: 'Profile',
      onClick: () => {
        console.log('Profile clicked');
        setIsOpen(false);
      }
    },
    {
      icon: Settings,
      label: 'Settings',
      onClick: () => {
        console.log('Settings clicked');
        setIsOpen(false);
      }
    },
    {
      icon: Shield,
      label: 'Privacy',
      onClick: () => {
        console.log('Privacy clicked');
        setIsOpen(false);
      }
    },
    {
      icon: CreditCard,
      label: 'Billing',
      onClick: () => {
        console.log('Billing clicked');
        setIsOpen(false);
      }
    },
    {
      icon: HelpCircle,
      label: 'Help & Support',
      onClick: () => {
        console.log('Help clicked');
        setIsOpen(false);
      }
    }
  ];

  if (!user) {
    return null;
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* User Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 p-2 rounded-lg hover:bg-white/10 transition-colors duration-200"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {/* Avatar */}
        <div className="relative">
          {user.avatar ? (
            <img
              src={user.avatar}
              alt={user.name}
              className="w-8 h-8 rounded-full object-cover"
            />
          ) : (
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
              {getInitials(user.name)}
            </div>
          )}
          
          {/* Role Badge */}
          {user.role === 'admin' && (
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-500 rounded-full flex items-center justify-center">
              <Crown className="w-2.5 h-2.5 text-white" />
            </div>
          )}
        </div>

        {/* User Info */}
        <div className="hidden md:block text-left">
          <div className="text-sm font-medium text-white">{user.name}</div>
          <div className="text-xs text-white/60 flex items-center">
            <Mail className="w-3 h-3 mr-1" />
            {user.email}
          </div>
        </div>

        {/* Dropdown Arrow */}
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="w-4 h-4 text-white/60" />
        </motion.div>
      </motion.button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="absolute right-0 top-full mt-2 w-64 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl z-50"
            style={{
              zIndex: 9999,
              position: 'absolute',
              top: '100%',
              right: 0,
              marginTop: '0.5rem'
            }}
          >
            {/* User Header */}
            <div className="p-4 border-b border-white/10">
              <div className="flex items-center space-x-3">
                {user.avatar ? (
                  <img
                    src={user.avatar}
                    alt={user.name}
                    className="w-10 h-10 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {getInitials(user.name)}
                  </div>
                )}
                <div>
                  <div className="text-white font-medium">{user.name}</div>
                  <div className="text-white/60 text-sm">{user.email}</div>
                  <div className="text-white/40 text-xs capitalize">{user.role}</div>
                </div>
              </div>
            </div>

            {/* Menu Items */}
            <div className="p-2">
              {menuItems.map((item, index) => {
                const Icon = item.icon;
                return (
                  <motion.button
                    key={item.label}
                    onClick={item.onClick}
                    className="w-full flex items-center space-x-3 p-3 rounded-lg text-white hover:bg-white/10 transition-colors duration-200"
                    whileHover={{ x: 4 }}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Icon className="w-4 h-4 text-white/60" />
                    <span className="text-sm">{item.label}</span>
                  </motion.button>
                );
              })}

              {/* Divider */}
              <div className="border-t border-white/10 my-2" />

              {/* Logout Button */}
              <motion.button
                onClick={handleLogout}
                className="w-full flex items-center space-x-3 p-3 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors duration-200"
                whileHover={{ x: 4 }}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: menuItems.length * 0.05 }}
              >
                <LogOut className="w-4 h-4" />
                <span className="text-sm">Sign Out</span>
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UserProfileDropdown; 