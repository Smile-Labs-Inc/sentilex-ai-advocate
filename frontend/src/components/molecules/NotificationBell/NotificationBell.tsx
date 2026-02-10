// =============================================================================
// NotificationBell Molecule
// Professional notification bell with dropdown for legal applications
// =============================================================================

import { useState, useEffect, useRef } from 'preact/hooks';
import { cn } from '../../../lib/utils';
import { Icon } from '../../atoms/Icon/Icon';
import { Button } from '../../atoms/Button/Button';
import type { Notification } from '../../../types';
import type { JSX } from 'preact';
import './NotificationBell.css';

export interface NotificationBellProps {
    notifications: Notification[];
    onMarkAsRead: (id: string) => void;
    onMarkAllAsRead: () => void;
    onViewAll: () => void;
    className?: string;
}

export function NotificationBell({
    notifications,
    onMarkAsRead,
    onMarkAllAsRead,
    onViewAll,
    className,
}: NotificationBellProps) {
    const [isOpen, setIsOpen] = useState(false);
    const bellRef = useRef<HTMLDivElement>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Count unread notifications
    const unreadCount = notifications.filter(n => !n.isRead).length;

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                bellRef.current &&
                !bellRef.current.contains(event.target as Node) &&
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target as Node)
            ) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
            return () => document.removeEventListener('mousedown', handleClickOutside);
        }
    }, [isOpen]);

    // Keyboard accessibility
    const handleKeyDown = (event: JSX.TargetedKeyboardEvent<HTMLButtonElement>) => {
        if (event.key === 'Escape') {
            setIsOpen(false);
        }
    };

    const handleNotificationClick = (notification: Notification) => {
        if (!notification.isRead) {
            onMarkAsRead(notification.id);
        }
    };

    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

        if (diffInHours < 1) {
            return 'Just now';
        } else if (diffInHours < 24) {
            return `${diffInHours}h ago`;
        } else {
            const diffInDays = Math.floor(diffInHours / 24);
            return `${diffInDays}d ago`;
        }
    };

    return (
        <div className={cn('notification-bell-container', className)} ref={bellRef}>
            {/* Bell Button */}
            <button
                className="notification-bell-button"
                onClick={() => setIsOpen(!isOpen)}
                onKeyDown={handleKeyDown}
                aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ''}`}
                aria-expanded={isOpen}
                aria-haspopup="true"
            >
                <Icon name="Bell" size="sm" className="notification-bell-icon" />

                {/* Unread Badge */}
                {unreadCount > 0 && (
                    <span className="notification-bell-badge" aria-hidden="true">
                        {unreadCount > 99 ? '99+' : unreadCount}
                    </span>
                )}
            </button>

            {/* Dropdown Panel */}
            {isOpen && (
                <div
                    className="notification-dropdown"
                    ref={dropdownRef}
                    role="region"
                    aria-label="Notifications panel"
                >
                    {/* Header */}
                    <div className="notification-dropdown-header">
                        <h3 className="notification-dropdown-title">Notifications</h3>
                        {unreadCount > 0 && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={onMarkAllAsRead}
                                className="notification-mark-all-read"
                            >
                                Mark all read
                            </Button>
                        )}
                    </div>

                    {/* Notifications List */}
                    <div className="notification-list">
                        {notifications.length === 0 ? (
                            <div className="notification-empty">
                                <Icon name="Bell" size="md" className="notification-empty-icon" />
                                <p className="notification-empty-text">No notifications</p>
                            </div>
                        ) : (
                            notifications.map((notification) => (
                                <div
                                    key={notification.id}
                                    className={cn(
                                        'notification-item',
                                        !notification.isRead && 'notification-item-unread'
                                    )}
                                    onClick={() => handleNotificationClick(notification)}
                                    role="button"
                                    tabIndex={0}
                                    onKeyDown={(e: JSX.TargetedKeyboardEvent<HTMLDivElement>) => {
                                        if (e.key === 'Enter' || e.key === ' ') {
                                            e.preventDefault();
                                            handleNotificationClick(notification);
                                        }
                                    }}
                                >
                                    <div className="notification-content">
                                        {notification.title && (
                                            <div className="notification-title">{notification.title}</div>
                                        )}
                                        <div className="notification-message">{notification.message}</div>
                                        <div className="notification-timestamp">
                                            {formatTimestamp(notification.timestamp)}
                                        </div>
                                    </div>

                                    {/* Unread Indicator */}
                                    {!notification.isRead && (
                                        <div className="notification-unread-indicator" aria-hidden="true" />
                                    )}
                                </div>
                            ))
                        )}
                    </div>

                    {/* Footer */}
                    {notifications.length > 0 && (
                        <div className="notification-dropdown-footer">
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={onViewAll}
                                className="notification-view-all"
                            >
                                View all notifications
                            </Button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}