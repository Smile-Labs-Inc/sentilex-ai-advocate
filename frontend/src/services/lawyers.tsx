// =============================================================================
// Lawyer Service
// API calls for lawyer-related data
// =============================================================================

import { API_CONFIG, APP_CONFIG } from '../config';

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface Lawyer {
  id: number;
  name: string;
  specialties: string;
  rating: number;
  reviews_count: number;
  availability: string;
  experience_years: number;
  email: string;
  phone: string;
  district: string;
  verification_status: string;
  is_active: boolean;
}

export interface LawyerProfile extends Lawyer {
  is_email_verified: boolean;
  mfa_enabled: boolean;
  last_login: string | null;
  verification_step: number;
  created_at: string | null;
  active_sessions: number;
}

export interface LawyerRegisterRequest {
  name: string;
  email: string;
  password: string;
  phone: string;
  district: string;
  specialties: string;
  experience_years: number;
}

export interface LawyerLoginRequest {
  email: string;
  password: string;
  mfa_code?: string;
}

export interface LawyerLoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user_type: 'lawyer';
  requires_mfa: boolean;
  mfa_enabled: boolean;
  user_id: number;
  email: string;
  name: string;
  role: string;
}

export interface LawyerSearchParams {
  district?: string;
  specialty?: string;
}

export interface LawyerSession {
  id: number;
  device_info: string;
  ip_address: string;
  last_activity: string;
  created_at: string;
}

// ============================================================================
// Lawyer Service Class
// ============================================================================

class LawyerService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
  }

  // Helper to get auth headers
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  // ============================================================================
  // Public Lawyer Queries (No Auth Required)
  // ============================================================================

  /**
   * Search/List lawyers with optional filters
   */
  async searchLawyers(params?: LawyerSearchParams): Promise<Lawyer[]> {
    try {
      const url = new URL(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.LIST}`);

      if (params?.district) {
        url.searchParams.append('district', params.district);
      }

      if (params?.specialty) {
        url.searchParams.append('specialty', params.specialty);
      }

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch lawyers: ${response.statusText}`);
      }

      return response.json();
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch lawyers');
    }
  }

  /**
   * Fetch lawyers (backward compatibility)
   */
  async fetchLawyers(specialty?: string): Promise<Lawyer[]> {
    return this.searchLawyers({ specialty });
  }

  // ============================================================================
  // Lawyer Authentication
  // ============================================================================

  /**
   * Register a new lawyer account
   */
  async register(data: LawyerRegisterRequest): Promise<Lawyer> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.REGISTER}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  }

  /**
   * Login as a lawyer
   */
  async login(credentials: LawyerLoginRequest): Promise<LawyerLoginResponse> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.LOGIN}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data: LawyerLoginResponse = await response.json();

    // Store tokens
    localStorage.setItem(APP_CONFIG.TOKEN_STORAGE_KEY, data.access_token);
    localStorage.setItem(APP_CONFIG.REFRESH_TOKEN_STORAGE_KEY, data.refresh_token);
    localStorage.setItem(APP_CONFIG.USER_TYPE_STORAGE_KEY, 'lawyer');

    return data;
  }

  // ============================================================================
  // Lawyer Profile Management (Auth Required)
  // ============================================================================

  /**
   * Get current lawyer profile
   */
  async getMyProfile(): Promise<LawyerProfile> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.ME}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch lawyer profile');
    }

    return response.json();
  }

  /**
   * Update lawyer profile
   */
  async updateProfile(data: Partial<LawyerProfile>): Promise<LawyerProfile> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.UPDATE_PROFILE}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Profile update failed');
    }

    return response.json();
  }

  // ============================================================================
  // Password Management
  // ============================================================================

  /**
   * Change password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.CHANGE_PASSWORD}`, {
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

  /**
   * Request password reset
   */
  async forgotPassword(email: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.FORGOT_PASSWORD}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Password reset request failed');
    }

    return response.json();
  }

  /**
   * Reset password with token
   */
  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.RESET_PASSWORD}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token,
        new_password: newPassword,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Password reset failed');
    }

    return response.json();
  }

  // ============================================================================
  // Email Verification
  // ============================================================================

  /**
   * Verify email with token
   */
  async verifyEmail(token: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.VERIFY_EMAIL}`, {
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

  // ============================================================================
  // Session Management
  // ============================================================================

  /**
   * Get active sessions
   */
  async getSessions(): Promise<LawyerSession[]> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.SESSIONS}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch sessions');
    }

    return response.json();
  }

  /**
   * Revoke a session
   */
  async revokeSession(sessionId: number): Promise<{ message: string }> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.LAWYERS.REVOKE_SESSION(sessionId)}`,
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
}

// Export singleton instance
export const lawyerService = new LawyerService();

// Export backward compatible function
export async function fetchLawyers(specialty?: string): Promise<Lawyer[]> {
  return lawyerService.fetchLawyers(specialty);
}
