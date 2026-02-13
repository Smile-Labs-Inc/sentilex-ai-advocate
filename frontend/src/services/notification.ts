// =============================================================================
// Notification Service
// API interactions for notification management
// =============================================================================

import { API_CONFIG, APP_CONFIG } from "../config";
import type { Notification } from "../types";

export interface NotificationResponse {
  id: string;
  title?: string;
  message: string;
  notification_type: string;
  created_at: string;
  read_at?: string;
  recipient_id: string;
  recipient_type: string;
}

export interface UnreadCountResponse {
  unread_count: number;
}

class NotificationService {
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  // Get all notifications for the current user
  async getNotifications(): Promise<Notification[]> {
    try {
      const response = await fetch(
        `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.NOTIFICATIONS.LIST}`,
        {
          headers: this.getHeaders(),
        },
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const notifications = this.transformNotifications(
        data.notifications || [],
      );
      return notifications;
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
      return [];
    }
  }

  // Get unread notifications count
  async getUnreadCount(): Promise<number> {
    try {
      const response = await fetch(
        `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.NOTIFICATIONS.COUNT}`,
        {
          headers: this.getHeaders(),
        },
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: UnreadCountResponse = await response.json();
      return data.unread_count;
    } catch (error) {
      console.error("Failed to fetch unread count:", error);
      return 0;
    }
  }

  // Mark a notification as read
  async markAsRead(notificationId: string): Promise<boolean> {
    try {
      const response = await fetch(
        `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.NOTIFICATIONS.MARK_READ}`,
        {
          method: "POST",
          headers: this.getHeaders(),
          body: JSON.stringify({
            notification_ids: [notificationId],
          }),
        },
      );

      return response.ok;
    } catch (error) {
      console.error("Failed to mark notification as read:", error);
      return false;
    }
  }

  // Mark all notifications as read
  async markAllAsRead(): Promise<boolean> {
    try {
      const response = await fetch(
        `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.NOTIFICATIONS.MARK_ALL_READ}`,
        {
          method: "POST",
          headers: this.getHeaders(),
        },
      );

      return response.ok;
    } catch (error) {
      console.error("Failed to mark all notifications as read:", error);
      return false;
    }
  }

  // Transform backend response to frontend format
  private transformNotifications(
    backendNotifications: NotificationResponse[],
  ): Notification[] {
    return backendNotifications.map((notification) => ({
      id: notification.id,
      title: notification.title,
      message: notification.message,
      timestamp: notification.created_at,
      isRead: !!notification.read_at,
      type: this.mapNotificationType(notification.notification_type),
    }));
  }

  // Map backend notification types to frontend types
  private mapNotificationType(backendType: string): Notification["type"] {
    switch (backendType) {
      case "CASE_UPDATE":
      case "CASE_STATUS_CHANGE":
        return "case";
      case "LEGAL_CONSULTATION":
      case "COURT_DATE":
        return "legal";
      case "ACCOUNT_UPDATE":
      case "PROFILE_UPDATE":
        return "account";
      case "SYSTEM_MAINTENANCE":
      case "SYSTEM_UPDATE":
        return "system";
      default:
        return "system";
    }
  }
}

// Export singleton instance
export const notificationService = new NotificationService();
