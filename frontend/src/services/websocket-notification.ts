/**
 * WebSocket Notification Service
 * Handles real-time notification delivery from backend
 */

import { API_CONFIG, APP_CONFIG } from "../config";

export interface WebSocketMessage {
  type:
  | "notification"
  | "connection_established"
  | "pong"
  | "mark_as_read_response";
  data?: any;
  message?: string;
  notification_id?: string;
  success?: boolean;
}

export interface WebSocketNotification {
  id: string;
  title?: string;
  message: string;
  notification_type: string;
  priority: number;
  action_url?: string;
  created_at: string;
  is_read: boolean;
  metadata?: any;
}

type WebSocketListener = (data: any) => void;

class WebSocketNotificationService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000; // Start with 1 second
  private isManualClose = false;
  private listeners: { [key: string]: WebSocketListener[] } = {};

  connect(): void {
    const token = localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);

    try {
      // Convert HTTP URL to WebSocket URL
      // If API_CONFIG.BASE_URL is relative (e.g. '/api'), we need to construct an absolute URL
      const isRelative = API_CONFIG.BASE_URL.startsWith("/");
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";

      let wsUrl;
      if (isRelative) {
        const host = window.location.host; // Includes port if present
        wsUrl = `${protocol}//${host}${API_CONFIG.BASE_URL}`;
      } else {
        wsUrl = API_CONFIG.BASE_URL.replace("http://", "ws://").replace(
          "https://",
          "wss://",
        );
      }

      const url = `${wsUrl}/notifications/ws?token=${encodeURIComponent(token)}`;

      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log("WebSocket connected for notifications");
        this.reconnectAttempts = 0;
        this.reconnectInterval = 1000;

        // Send ping to keep connection alive
        this.startPingInterval();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      this.ws.onclose = (event) => {
        console.log("WebSocket connection closed:", event.code, event.reason);
        this.ws = null;

        if (!this.isManualClose) {
          this.attemptReconnect();
        }
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      this.attemptReconnect();
    }
  }

  disconnect(): void {
    this.isManualClose = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case "connection_established":
        this.emit("connected", { message: message.message });
        break;

      case "notification":
        if (message.data) {
          this.emit("notification", message.data);
        }
        break;

      case "mark_as_read_response":
        this.emit("mark_as_read_response", {
          success: message.success,
          notification_id: message.notification_id,
        });
        break;

      case "pong":
        // Handle pong response (connection health check)
        break;

      default:
        console.log("Unknown WebSocket message type:", message.type);
    }
  }

  private startPingInterval(): void {
    // Send ping every 30 seconds to keep connection alive
    setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000);
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("Max WebSocket reconnection attempts reached");
      return;
    }

    this.reconnectAttempts++;

    console.log(
      `Attempting to reconnect WebSocket (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`,
    );

    setTimeout(() => {
      if (!this.isManualClose) {
        this.connect();
      }
    }, this.reconnectInterval);

    // Exponential backoff
    this.reconnectInterval = Math.min(this.reconnectInterval * 2, 30000);
  }

  // Mark notification as read via WebSocket
  markAsRead(notificationId: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: "mark_as_read",
          notification_id: notificationId,
        }),
      );
    }
  }

  // Event listener system
  on(event: string, listener: WebSocketListener): void {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(listener);
  }

  off(event: string, listener: WebSocketListener): void {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(
        (l) => l !== listener,
      );
    }
  }

  private emit(event: string, data: any): void {
    if (this.listeners[event]) {
      this.listeners[event].forEach((listener) => listener(data));
    }
  }

  // Check if WebSocket is connected
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  // Get connection status
  getStatus(): string {
    if (!this.ws) return "disconnected";

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return "connecting";
      case WebSocket.OPEN:
        return "connected";
      case WebSocket.CLOSING:
        return "closing";
      case WebSocket.CLOSED:
        return "disconnected";
      default:
        return "unknown";
    }
  }
}

// Export singleton instance
export const webSocketNotificationService = new WebSocketNotificationService();
