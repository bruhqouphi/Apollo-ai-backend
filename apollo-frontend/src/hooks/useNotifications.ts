import { useState, useCallback } from 'react';
import { Notification } from '../components/Notifications/NotificationPanel';

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    };

    setNotifications(prev => [newNotification, ...prev]);
    
    // Save to localStorage
    const updated = [newNotification, ...notifications];
    localStorage.setItem('apollo-notifications', JSON.stringify(updated));

    return newNotification.id;
  }, [notifications]);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => {
      const updated = prev.filter(n => n.id !== id);
      localStorage.setItem('apollo-notifications', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => {
      const updated = prev.map(n => n.id === id ? { ...n, read: true } : n);
      localStorage.setItem('apollo-notifications', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
    localStorage.removeItem('apollo-notifications');
  }, []);

  // Convenience methods for different notification types
  const success = useCallback((title: string, message: string, action?: Notification['action']) => {
    return addNotification({ type: 'success', title, message, action });
  }, [addNotification]);

  const error = useCallback((title: string, message: string, action?: Notification['action']) => {
    return addNotification({ type: 'error', title, message, action });
  }, [addNotification]);

  const info = useCallback((title: string, message: string, action?: Notification['action']) => {
    return addNotification({ type: 'info', title, message, action });
  }, [addNotification]);

  const warning = useCallback((title: string, message: string, action?: Notification['action']) => {
    return addNotification({ type: 'warning', title, message, action });
  }, [addNotification]);

  const unreadCount = notifications.filter(n => !n.read).length;

  return {
    notifications,
    addNotification,
    removeNotification,
    markAsRead,
    clearAll,
    success,
    error,
    info,
    warning,
    unreadCount
  };
};

export default useNotifications;
