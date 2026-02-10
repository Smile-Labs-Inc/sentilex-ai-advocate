// =============================================================================
// API Client with Automatic Token Refresh
// Centralized HTTP client that handles token refresh automatically
// =============================================================================

import { API_CONFIG, APP_CONFIG } from '../config';
import { authService } from './auth';

interface ApiClientOptions extends RequestInit {
    skipAuth?: boolean;
    skipRefresh?: boolean;
}

class ApiClient {
    private isRefreshing = false;
    private refreshPromise: Promise<string | null> | null = null;

    /**
     * Make an API request with automatic token refresh
     */
    async fetch(url: string, options: ApiClientOptions = {}): Promise<Response> {
        const { skipAuth, skipRefresh, ...fetchOptions } = options;

        // Add authorization header if not skipped
        if (!skipAuth) {
            const token = authService.getToken();
            if (token) {
                fetchOptions.headers = {
                    ...fetchOptions.headers,
                    Authorization: `Bearer ${token}`,
                };
            }
        }

        // Make the request
        let response = await fetch(url, fetchOptions);

        // If unauthorized and not already refreshing, try to refresh token
        if (response.status === 401 && !skipAuth && !skipRefresh) {
            const newToken = await this.refreshAccessToken();

            if (newToken) {
                // Retry the request with new token
                fetchOptions.headers = {
                    ...fetchOptions.headers,
                    Authorization: `Bearer ${newToken}`,
                };
                response = await fetch(url, fetchOptions);
            } else {
                // Refresh failed, logout user
                this.handleAuthFailure();
            }
        }

        return response;
    }

    /**
     * Refresh the access token using refresh token
     * Uses a promise to prevent multiple simultaneous refresh attempts
     */
    private async refreshAccessToken(): Promise<string | null> {
        // If already refreshing, wait for that promise
        if (this.isRefreshing && this.refreshPromise) {
            return this.refreshPromise;
        }

        const refreshToken = authService.getRefreshToken();
        if (!refreshToken) {
            return null;
        }

        this.isRefreshing = true;
        this.refreshPromise = this.performTokenRefresh(refreshToken);

        try {
            const newToken = await this.refreshPromise;
            return newToken;
        } finally {
            this.isRefreshing = false;
            this.refreshPromise = null;
        }
    }

    /**
     * Perform the actual token refresh API call
     */
    private async performTokenRefresh(refreshToken: string): Promise<string | null> {
        try {
            const response = await fetch(
                `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH.REFRESH}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: refreshToken }),
                }
            );

            if (!response.ok) {
                // Refresh token is invalid or expired
                console.error('Token refresh failed:', response.status);
                return null;
            }

            const data = await response.json();
            const newAccessToken = data.access_token;

            // Update token in localStorage
            localStorage.setItem(APP_CONFIG.TOKEN_STORAGE_KEY, newAccessToken);

            console.log('Token refreshed successfully');
            return newAccessToken;
        } catch (error) {
            console.error('Token refresh error:', error);
            return null;
        }
    }

    /**
     * Handle authentication failure (logout user)
     */
    private handleAuthFailure(): void {
        console.warn('Authentication failed - logging out user');

        // Clear tokens
        authService.clearTokens();

        // Redirect to login page
        const currentPath = window.location.pathname;
        if (currentPath !== '/auth/login' && currentPath !== '/auth/register') {
            window.location.href = '/auth/login';
        }
    }

    /**
     * Convenience methods for common HTTP methods
     */
    async get(url: string, options?: ApiClientOptions): Promise<Response> {
        return this.fetch(url, { ...options, method: 'GET' });
    }

    async post(url: string, body?: any, options?: ApiClientOptions): Promise<Response> {
        return this.fetch(url, {
            ...options,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
            body: body ? JSON.stringify(body) : undefined,
        });
    }

    async put(url: string, body?: any, options?: ApiClientOptions): Promise<Response> {
        return this.fetch(url, {
            ...options,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
            body: body ? JSON.stringify(body) : undefined,
        });
    }

    async patch(url: string, body?: any, options?: ApiClientOptions): Promise<Response> {
        return this.fetch(url, {
            ...options,
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
            body: body ? JSON.stringify(body) : undefined,
        });
    }

    async delete(url: string, options?: ApiClientOptions): Promise<Response> {
        return this.fetch(url, { ...options, method: 'DELETE' });
    }
}

// Export singleton instance
export const apiClient = new ApiClient();
