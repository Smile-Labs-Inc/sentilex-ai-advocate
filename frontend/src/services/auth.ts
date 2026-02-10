// =============================================================================
// Authentication Service
// Handles all authentication-related API calls
// =============================================================================

import { API_CONFIG, APP_CONFIG } from '../config';
import type {
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegistrationResponse,
    UserProfile,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserType,
} from '../types/auth';

class AuthService {
    private baseUrl: string;

    constructor() {
        this.baseUrl = API_CONFIG.BASE_URL;
    }

    // Helper to get auth headers
    private getAuthHeaders(): HeadersInit {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
        };
    }

    // Token management
    getToken(): string | null {
        return localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
    }

    getRefreshToken(): string | null {
        return localStorage.getItem(APP_CONFIG.REFRESH_TOKEN_STORAGE_KEY);
    }

    setTokens(accessToken: string, refreshToken: string): void {
        localStorage.setItem(APP_CONFIG.TOKEN_STORAGE_KEY, accessToken);
        localStorage.setItem(APP_CONFIG.REFRESH_TOKEN_STORAGE_KEY, refreshToken);
    }

    clearTokens(): void {
        localStorage.removeItem(APP_CONFIG.TOKEN_STORAGE_KEY);
        localStorage.removeItem(APP_CONFIG.REFRESH_TOKEN_STORAGE_KEY);
        localStorage.removeItem(APP_CONFIG.USER_STORAGE_KEY);
        localStorage.removeItem(APP_CONFIG.USER_TYPE_STORAGE_KEY);
    }

    // Store user data
    setUser(user: UserProfile, userType: UserType): void {
        localStorage.setItem(APP_CONFIG.USER_STORAGE_KEY, JSON.stringify(user));
        localStorage.setItem(APP_CONFIG.USER_TYPE_STORAGE_KEY, userType);
    }

    getUser(): UserProfile | null {
        const userStr = localStorage.getItem(APP_CONFIG.USER_STORAGE_KEY);
        return userStr ? JSON.parse(userStr) : null;
    }

    getUserType(): UserType | null {
        return localStorage.getItem(APP_CONFIG.USER_TYPE_STORAGE_KEY) as UserType | null;
    }

    // Register new user
    async register(data: RegisterRequest): Promise<RegistrationResponse> {
        // Ensure preferred_language has a valid value
        const registrationData: any = {
            first_name: data.first_name,
            last_name: data.last_name,
            email: data.email,
            password: data.password,
            preferred_language: data.preferred_language || 'en',
        };

        // Only include district if it has a value
        if (data.district && data.district.trim()) {
            registrationData.district = data.district.trim();
        }

        console.log('Registration data being sent:', registrationData);

        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.REGISTER}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(registrationData),
        });

        if (!response.ok) {
            const error = await response.json();
            console.error('Registration error response:', error);

            // Parse Pydantic validation errors
            if (Array.isArray(error.detail)) {
                // Extract user-friendly error messages from validation errors
                const errorMessages = error.detail.map((err: any) => {
                    const field = err.loc ? err.loc[err.loc.length - 1] : 'field';
                    const msg = err.msg || 'Invalid value';
                    // Remove "Value error, " prefix if present
                    const cleanMsg = msg.replace(/^Value error,\s*/i, '');
                    return `${field}: ${cleanMsg}`;
                });
                throw new Error(errorMessages.join('\n'));
            }

            // Handle string error details
            const errorMsg = typeof error.detail === 'string'
                ? error.detail
                : 'Registration failed';
            throw new Error(errorMsg);
        }

        return response.json();
    }

    // Login
    async login(credentials: LoginRequest): Promise<LoginResponse> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.LOGIN}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials),
        });

        // If backend redirected to an HTML login page or returned non-JSON,
        // attempt to produce a friendly message for common auth failures.
        if (!response.ok) {
            const error = await response.json();
            console.error('Login error response:', error);

            // Parse Pydantic validation errors
            if (Array.isArray(error.detail)) {
                const errorMessages = error.detail.map((err: any) => {
                    const field = err.loc ? err.loc[err.loc.length - 1] : 'field';
                    const msg = err.msg || 'Invalid value';
                    const cleanMsg = msg.replace(/^Value error,\s*/i, '');
                    return `${field}: ${cleanMsg}`;
                });
                throw new Error(errorMessages.join('\n'));
            }

            // Handle string error details (like "Incorrect email or password")
            const errorMsg = typeof error.detail === 'string'
                ? error.detail
                : 'Login failed';
            throw new Error(errorMsg);
        }

        // Parse successful response
        const data: LoginResponse = await response.json();

        // Store tokens and user data
        this.setTokens(data.access_token, data.refresh_token);

        return data;
    }

    // Logout
    async logout(): Promise<void> {
        try {
            const token = this.getToken();
            if (token) {
                await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.LOGOUT}`, {
                    method: 'POST',
                    headers: this.getAuthHeaders(),
                });
            }
        } finally {
            this.clearTokens();
        }
    }

    // Refresh token
    async refreshToken(): Promise<string> {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.REFRESH}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (!response.ok) {
            this.clearTokens();
            throw new Error('Token refresh failed');
        }

        const data = await response.json();
        localStorage.setItem(APP_CONFIG.TOKEN_STORAGE_KEY, data.access_token);
        return data.access_token;
    }

    // Get current user profile
    async getCurrentUser(): Promise<UserProfile> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.ME}`, {
            method: 'GET',
            headers: this.getAuthHeaders(),
        });

        if (!response.ok) {
            throw new Error('Failed to fetch user profile');
        }

        return response.json();
    }

    // Verify email
    async verifyEmail(token: string): Promise<{ message: string }> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.VERIFY_EMAIL}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Email verification failed');
        }

        return response.json();
    }

    // Resend verification email
    async resendVerificationEmail(): Promise<{ message: string }> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.RESEND_VERIFICATION}`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to resend verification email');
        }

        return response.json();
    }

    // Request password reset
    async requestPasswordReset(data: PasswordResetRequest): Promise<{ message: string }> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.FORGOT_PASSWORD}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Password reset request failed');
        }

        return response.json();
    }

    // Confirm password reset
    async confirmPasswordReset(data: PasswordResetConfirm): Promise<{ message: string }> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.RESET_PASSWORD}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Password reset failed');
        }

        return response.json();
    }

    // Change password
    async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.CHANGE_PASSWORD}`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Password change failed');
        }

        return response.json();
    }

    // Update user profile
    async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.UPDATE_PROFILE}`, {
            method: 'PATCH',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Profile update failed');
        }

        const updatedProfile = await response.json();
        // Update local storage with new profile
        const userType = this.getUserType();
        if (userType) {
            this.setUser(updatedProfile, userType);
        }
        return updatedProfile;
    }

    // Get active sessions
    async getActiveSessions(): Promise<{ sessions: any[]; total: number }> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.SESSIONS}`, {
            method: 'GET',
            headers: this.getAuthHeaders(),
        });

        if (!response.ok) {
            throw new Error('Failed to fetch sessions');
        }

        return response.json();
    }

    // Revoke a session
    async revokeSession(sessionId: number): Promise<{ message: string }> {
        const response = await fetch(
            `${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.REVOKE_SESSION(sessionId)}`,
            {
                method: 'DELETE',
                headers: this.getAuthHeaders(),
            }
        );

        if (!response.ok) {
            throw new Error('Failed to revoke session');
        }

        return response.json();
    }

    // MFA Setup
    async setupMFA(): Promise<{ secret: string; qr_code_url: string; backup_codes: string[] }> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.MFA.SETUP}`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'MFA setup failed');
        }

        return response.json();
    }

    // Enable MFA
    async enableMFA(code: string): Promise<{ message: string }> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.MFA.ENABLE}`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify({ code }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'MFA enable failed');
        }

        return response.json();
    }

    // Disable MFA
    async disableMFA(password: string): Promise<{ message: string }> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.MFA.DISABLE}`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify({ password }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'MFA disable failed');
        }

        return response.json();
    }

    // Get MFA status
    async getMFAStatus(): Promise<{
        mfa_enabled: boolean;
        mfa_enabled_at: string | null;
        backup_codes_remaining: number;
    }> {
        const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.MFA.STATUS}`, {
            method: 'GET',
            headers: this.getAuthHeaders(),
        });

        if (!response.ok) {
            throw new Error('Failed to fetch MFA status');
        }

        return response.json();
    }

    // Regenerate backup codes
    async regenerateBackupCodes(): Promise<{ secret: string; qr_code_url: string; backup_codes: string[] }> {
        const response = await fetch(
            `${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.MFA.REGENERATE_CODES}`,
            {
                method: 'POST',
                headers: this.getAuthHeaders(),
            }
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to regenerate backup codes');
        }

        return response.json();
    }

    // Google OAuth login
    getGoogleLoginUrl(userType: UserType = 'user'): string {
        return `${this.baseUrl}${API_CONFIG.ENDPOINTS.GOOGLE_AUTH.LOGIN}?user_type=${userType}`;
    }

    // Check if user is authenticated
    isAuthenticated(): boolean {
        return !!this.getToken();
    }
}

export const authService = new AuthService();
