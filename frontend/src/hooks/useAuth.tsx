// =============================================================================
// Authentication Context
// Provides authentication state and methods throughout the app
// =============================================================================

import { createContext } from 'preact';
import { useState, useEffect, useContext } from 'preact/hooks';
import { authService } from '../services/auth';
import type {
    AuthState,
    LoginRequest,
    RegisterRequest,
    LoginResponse,
    RegistrationResponse,
} from '../types/auth';

interface AuthContextType extends AuthState {
    login: (credentials: LoginRequest) => Promise<LoginResponse>;
    register: (data: RegisterRequest) => Promise<RegistrationResponse>;
    logout: () => Promise<void>;
    refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: preact.ComponentChildren }) {
    const [state, setState] = useState<AuthState>({
        isAuthenticated: false,
        user: null,
        userType: null,
        token: null,
        refreshToken: null,
        isLoading: true,
        error: null,
    });

    // Initialize auth state from localStorage
    useEffect(() => {
        const initAuth = async () => {
            const token = authService.getToken();
            const refreshToken = authService.getRefreshToken();
            const user = authService.getUser();
            const userType = authService.getUserType();

            if (token && user) {
                try {
                    // Verify token is still valid by fetching current user
                    const currentUser = await authService.getCurrentUser();
                    setState({
                        isAuthenticated: true,
                        user: currentUser,
                        userType,
                        token,
                        refreshToken,
                        isLoading: false,
                        error: null,
                    });
                } catch (error) {
                    // Token is invalid, clear everything
                    authService.clearTokens();
                    setState({
                        isAuthenticated: false,
                        user: null,
                        userType: null,
                        token: null,
                        refreshToken: null,
                        isLoading: false,
                        error: null,
                    });
                }
            } else {
                setState((prev) => ({ ...prev, isLoading: false }));
            }
        };

        initAuth();
    }, []);

    const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
        try {
            setState((prev) => ({ ...prev, isLoading: true, error: null }));

            const response = await authService.login(credentials);

            // Fetch full user profile
            const user = await authService.getCurrentUser();
            authService.setUser(user, response.user_type);

            setState({
                isAuthenticated: true,
                user,
                userType: response.user_type,
                token: response.access_token,
                refreshToken: response.refresh_token,
                isLoading: false,
                error: null,
            });

            return response;
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Login failed';
            setState((prev) => ({
                ...prev,
                isLoading: false,
                error: errorMessage,
            }));
            throw error;
        }
    };

    const register = async (data: RegisterRequest): Promise<RegistrationResponse> => {
        try {
            setState((prev) => ({ ...prev, isLoading: true, error: null }));

            const response = await authService.register(data);

            setState((prev) => ({
                ...prev,
                isLoading: false,
                error: null,
            }));

            return response;
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Registration failed';
            setState((prev) => ({
                ...prev,
                isLoading: false,
                error: errorMessage,
            }));
            throw error;
        }
    };

    const logout = async (): Promise<void> => {
        try {
            await authService.logout();
        } finally {
            setState({
                isAuthenticated: false,
                user: null,
                userType: null,
                token: null,
                refreshToken: null,
                isLoading: false,
                error: null,
            });
        }
    };

    const refreshAuth = async (): Promise<void> => {
        try {
            const user = await authService.getCurrentUser();
            const token = authService.getToken();
            const refreshToken = authService.getRefreshToken();
            const userType = authService.getUserType();

            setState({
                isAuthenticated: true,
                user,
                userType,
                token,
                refreshToken,
                isLoading: false,
                error: null,
            });
        } catch (error) {
            await logout();
            throw error;
        }
    };

    const value: AuthContextType = {
        ...state,
        login,
        register,
        logout,
        refreshAuth,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
