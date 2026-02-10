// =============================================================================
// useNotifications Hook
// Custom hook for managing notification state and interactions
// =============================================================================

import { useState, useEffect, useCallback } from 'preact/hooks';
import { notificationService } from '../services/notification';
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
            console.error('Error loading notifications:', err);
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
            console.error('Error marking notification as read:', err);
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
            console.error('Error marking all notifications as read:', err);
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

    // Auto-refresh every 5 minutes
    useEffect(() => {
        const interval = setInterval(() => {
            if (!isLoading) {
                loadNotifications();
            }
        }, 5 * 60 * 1000); // 5 minutes

        return () => clearInterval(interval);
    }, [loadNotifications, isLoading]);

    return {
        notifications,
        unreadCount,
        isLoading,
        error,
        markAsRead,
        markAllAsRead,
        refresh,
    };
}