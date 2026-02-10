// =============================================================================
// Authentication Types
// Type definitions for authentication, users, and related data
// =============================================================================

export type UserType = 'user' | 'lawyer' | 'admin';

export interface UserProfile {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    role: string;
    is_active: boolean;
    email_verified: boolean;
    mfa_enabled: boolean;
    preferred_language: string;
    district?: string;
    last_login_at?: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    preferred_language: string;  // Required: must be 'en', 'si', or 'ta'
    district?: string;
}

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
    user_type: UserType;
    requires_mfa: boolean;
    mfa_enabled: boolean;
    user_id: number;
    email: string;
    name: string;
}

export interface RegistrationResponse {
    message: string;
    user: UserProfile;
    verification_sent: boolean;
}

export interface AuthState {
    isAuthenticated: boolean;
    user: UserProfile | null;
    userType: UserType | null;
    token: string | null;
    refreshToken: string | null;
    isLoading: boolean;
    error: string | null;
}

export interface PasswordResetRequest {
    email: string;
}

export interface PasswordResetConfirm {
    token: string;
    new_password: string;
}

export interface PasswordChangeRequest {
    current_password: string;
    new_password: string;
}

export interface SessionInfo {
    id: string;
    ip_address: string;
    user_agent: string;
    device_info: string;
    created_at: string;
    last_activity_at: string;
    is_current: boolean;
}
