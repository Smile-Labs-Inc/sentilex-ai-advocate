// =============================================================================
// useNotifications Hook
// Custom hook for managing notification state and interactions
// =============================================================================

import { useState, useEffect, useCallback } from 'preact/hooks';
import { notificationService } from '../services/notification';
import { webSocketNotificationService, type WebSocketNotification } from '../services/websocket-notification';
import type { Notification } from '../types';

export interface UseNotificationsReturn {
    notifications: Notification[];
    unreadCount: number;
    isLoading: boolean;
    error: string | null;
    markAsRead: (id: string) => Promise<void>;
    markAllAsRead: () => Promise<void>;
    refresh: () => Promise<void>;
}

export function useNotifications(): UseNotificationsReturn {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Load notifications from API
    const loadNotifications = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);

            const [notificationsData, unreadCountData] = await Promise.all([
                notificationService.getNotifications(),
                notificationService.getUnreadCount(),
            ]);



            setNotifications(notificationsData);
            setUnreadCount(unreadCountData);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to load notifications';
            setError(errorMessage);

        } finally {
            setIsLoading(false);
        }
    }, []);

    // Mark notification as read
    const markAsRead = useCallback(async (id: string) => {
        try {
            const success = await notificationService.markAsRead(id);

            if (success) {
                setNotifications(prev =>
                    prev.map(notification =>
                        notification.id === id
                            ? { ...notification, isRead: true }
                            : notification
                    )
                );

                // Update unread count
                setUnreadCount(prev => Math.max(0, prev - 1));
            } else {
                throw new Error('Failed to mark notification as read');
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to mark notification as read';
            setError(errorMessage);

        }
    }, []);

    // Mark all notifications as read
    const markAllAsRead = useCallback(async () => {
        try {
            const success = await notificationService.markAllAsRead();

            if (success) {
                setNotifications(prev =>
                    prev.map(notification => ({ ...notification, isRead: true }))
                );
                setUnreadCount(0);
            } else {
                throw new Error('Failed to mark all notifications as read');
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to mark all notifications as read';
            setError(errorMessage);

        }
    }, []);

    // Refresh notifications
    const refresh = useCallback(async () => {
        await loadNotifications();
    }, [loadNotifications]);

    // Load notifications on mount
    useEffect(() => {
        loadNotifications();
    }, [loadNotifications]);

    // WebSocket setup and real-time notifications
    useEffect(() => {
        // Connect to WebSocket for real-time notifications
        const token = localStorage.getItem('token');
        if (token) {
            webSocketNotificationService.connect();

            // Listen for new notifications
            const handleNewNotification = (wsNotification: WebSocketNotification) => {
                // Convert WebSocket notification to our Notification type
                const notification: Notification = {
                    id: wsNotification.id,
                    title: wsNotification.title,
                    message: wsNotification.message,
                    timestamp: wsNotification.created_at,
                    isRead: wsNotification.is_read,
                    type: wsNotification.notification_type as any,
                };

                // Add to notifications list
                setNotifications(prev => [notification, ...prev]);

                // Update unread count if notification is unread
                if (!wsNotification.is_read) {
                    setUnreadCount(prev => prev + 1);
                }

                // Show browser notification if supported and permission granted
                if ('Notification' in window && Notification.permission === 'granted') {
                    new Notification(wsNotification.title || 'New Notification', {
                        body: wsNotification.message,
                        icon: '/favicon.ico',
                        tag: wsNotification.id, // Prevent duplicate notifications
                    });
                }
            };

            // Listen for mark as read responses
            const handleMarkAsReadResponse = (data: { success: boolean; notification_id: string }) => {
                if (data.success) {
                    setNotifications(prev =>
                        prev.map(notification =>
                            notification.id === data.notification_id
                                ? { ...notification, isRead: true }
                                : notification
                        )
                    );
                    setUnreadCount(prev => Math.max(0, prev - 1));
                }
            };

            // Listen for connection events
            const handleConnected = () => {

                setError(null);
            };

            webSocketNotificationService.on('notification', handleNewNotification);
            webSocketNotificationService.on('mark_as_read_response', handleMarkAsReadResponse);
            webSocketNotificationService.on('connected', handleConnected);

            // Cleanup on unmount
            return () => {
                webSocketNotificationService.off('notification', handleNewNotification);
                webSocketNotificationService.off('mark_as_read_response', handleMarkAsReadResponse);
                webSocketNotificationService.off('connected', handleConnected);
                webSocketNotificationService.disconnect();
            };
        }

        // Fallback: refresh every 2 minutes if WebSocket is not connected
        const fallbackInterval = setInterval(() => {
            if (!webSocketNotificationService.isConnected() && !isLoading) {
                loadNotifications();
            }
        }, 2 * 60 * 1000); // 2 minutes

        return () => clearInterval(fallbackInterval);
    }, [loadNotifications, isLoading]);

    // Enhanced mark as read that uses WebSocket when available
    const markAsReadEnhanced = useCallback(async (id: string) => {
        try {
            // Try WebSocket first for instant feedback
            if (webSocketNotificationService.isConnected()) {
                webSocketNotificationService.markAsRead(id);
                // The response will be handled by the WebSocket listener
            } else {
                // Fallback to API call
                await markAsRead(id);
            }
        } catch (err) {
            // If WebSocket fails, try API call
            await markAsRead(id);
        }
    }, [markAsRead]);

    return {
        notifications,
        unreadCount,
        isLoading,
        error,
        markAsRead: markAsReadEnhanced,
        markAllAsRead,
        refresh,
    };
}