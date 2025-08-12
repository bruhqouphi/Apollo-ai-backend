import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bell, 
  X, 
  CheckCircle, 
  AlertCircle, 
  Info, 
  Clock,
  Trash2,
  Check
} from 'lucide-react';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface NotificationPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const NotificationPanel: React.FC<NotificationPanelProps> = ({ isOpen, onClose }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    // Load notifications from localStorage
    const saved = localStorage.getItem('apollo-notifications');
    if (saved) {
      const parsed = JSON.parse(saved).map((n: any) => ({
        ...n,
        timestamp: new Date(n.timestamp)
      }));
      setNotifications(parsed);
    } else {
      // Default notifications for demo
      setNotifications([
        {
          id: '1',
          type: 'success',
          title: 'Analysis Complete',
          message: 'Your data analysis has been completed successfully.',
          timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
          read: false
        },
        {
          id: '2',
          type: 'info',
          title: 'New Feature Available',
          message: 'Chart.js visualizations are now available in the Charts section.',
          timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
          read: false
        },
        {
          id: '3',
          type: 'warning',
          title: 'File Size Warning',
          message: 'Your uploaded file is large. Processing may take longer.',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
          read: true
        }
      ]);
    }
  }, []);

  useEffect(() => {
    // Save notifications to localStorage
    localStorage.setItem('apollo-notifications', JSON.stringify(notifications));
  }, [notifications]);

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error': return <AlertCircle className="w-5 h-5 text-red-400" />;
      case 'warning': return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      case 'info': return <Info className="w-5 h-5 text-blue-400" />;
      default: return <Bell className="w-5 h-5 text-white/60" />;
    }
  };

  const getTimeAgo = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(n => ({ ...n, read: true }))
    );
  };

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-start justify-end p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, x: 100, scale: 0.95 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 100, scale: 0.95 }}
          className="w-full max-w-md glass-card rounded-xl border border-white/20 shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10">
            <div className="flex items-center space-x-3">
              <Bell className="w-5 h-5 text-white" />
              <h3 className="text-lg font-semibold text-white">Notifications</h3>
              {unreadCount > 0 && (
                <span className="px-2 py-1 bg-red-500 text-white text-xs rounded-full">
                  {unreadCount}
                </span>
              )}
            </div>
            <div className="flex items-center space-x-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="p-1 hover:bg-white/10 rounded transition-colors"
                  title="Mark all as read"
                >
                  <Check className="w-4 h-4 text-white/60" />
                </button>
              )}
              <button
                onClick={clearAll}
                className="p-1 hover:bg-white/10 rounded transition-colors"
                title="Clear all"
              >
                <Trash2 className="w-4 h-4 text-white/60" />
              </button>
              <button
                onClick={onClose}
                className="p-1 hover:bg-white/10 rounded transition-colors"
              >
                <X className="w-4 h-4 text-white/60" />
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center">
                <Bell className="w-12 h-12 text-white/40 mx-auto mb-3" />
                <p className="text-white/60 text-sm">No notifications</p>
                <p className="text-white/40 text-xs mt-1">You're all caught up!</p>
              </div>
            ) : (
              <div className="p-2">
                {notifications.map((notification) => (
                  <motion.div
                    key={notification.id}
                    layout
                    className={`p-3 mb-2 rounded-lg border transition-all cursor-pointer ${
                      notification.read
                        ? 'bg-white/5 border-white/10 opacity-75'
                        : 'bg-white/10 border-white/20'
                    }`}
                    onClick={() => !notification.read && markAsRead(notification.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-0.5">
                        {getIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between">
                          <h4 className="text-white text-sm font-medium mb-1">
                            {notification.title}
                          </h4>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteNotification(notification.id);
                            }}
                            className="p-1 hover:bg-white/10 rounded transition-colors ml-2"
                          >
                            <X className="w-3 h-3 text-white/40" />
                          </button>
                        </div>
                        <p className="text-white/70 text-xs mb-2">
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-1 text-white/40 text-xs">
                            <Clock className="w-3 h-3" />
                            <span>{getTimeAgo(notification.timestamp)}</span>
                          </div>
                          {!notification.read && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                        </div>
                        {notification.action && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              notification.action!.onClick();
                            }}
                            className="mt-2 px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/40 rounded text-blue-300 text-xs transition-colors"
                          >
                            {notification.action.label}
                          </button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default NotificationPanel;
