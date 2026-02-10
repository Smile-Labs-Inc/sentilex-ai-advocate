/**
 * Browser Notification Utility
 * Handles browser notification permissions and display
 */

export class BrowserNotificationUtil {
    static async requestPermission(): Promise<NotificationPermission> {
        if (!('Notification' in window)) {
            console.warn('This browser does not support desktop notifications');
            return 'denied';
        }

        if (Notification.permission === 'granted') {
            return 'granted';
        }

        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            return permission;
        }

        return Notification.permission;
    }

    static showNotification(title: string, options: NotificationOptions = {}): boolean {
        if (Notification.permission !== 'granted') {
            return false;
        }

        try {
            new Notification(title, {
                icon: '/favicon.ico',
                badge: '/favicon.ico',
                ...options,
            });
            return true;
        } catch (error) {
            console.error('Failed to show notification:', error);
            return false;
        }
    }

    static isSupported(): boolean {
        return 'Notification' in window;
    }

    static getPermissionStatus(): NotificationPermission {
        if (!this.isSupported()) {
            return 'denied';
        }
        return Notification.permission;
    }
}