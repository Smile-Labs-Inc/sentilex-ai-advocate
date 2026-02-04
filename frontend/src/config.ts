
// Environment variables (can be overridden by .env file)
const ENV = {
    API_URL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
    FRONTEND_URL: import.meta.env.VITE_FRONTEND_URL || 'http://localhost:5173',
    ENABLE_GOOGLE_AUTH: import.meta.env.VITE_ENABLE_GOOGLE_AUTH === 'true' || false,
};


export const API_CONFIG = {
    BASE_URL: ENV.API_URL,
    TIMEOUT: 30000,
    ENDPOINTS: {

        AUTH: {
            REGISTER: '/auth/register',
            LOGIN: '/auth/login',
            LOGOUT: '/auth/logout',
            REFRESH: '/auth/refresh',
            VERIFY_EMAIL: '/auth/verify-email',
            RESEND_VERIFICATION: '/auth/resend-verification',
            FORGOT_PASSWORD: '/auth/forgot-password',
            RESET_PASSWORD: '/auth/reset-password',
            CHANGE_PASSWORD: '/auth/change-password',
            ME: '/auth/me',
            UPDATE_PROFILE: '/auth/me',
            SESSIONS: '/auth/sessions',
            REVOKE_SESSION: (id: number) => `/auth/sessions/${id}`,
            MFA: {
                SETUP: '/auth/mfa/setup',
                ENABLE: '/auth/mfa/enable',
                DISABLE: '/auth/mfa/disable',
                STATUS: '/auth/mfa/status',
                REGENERATE_CODES: '/auth/mfa/regenerate-backup-codes',
            },
        },

        GOOGLE_AUTH: {
            LOGIN: '/auth/google/login',
            CALLBACK: '/auth/google/callback',
        },

        LAWBOOK: {
            CHAT: '/lawbook/chat',
            LAWS: '/lawbook/laws',
        },

        CHAT: {
            SEND: '/api/chat/send',
            HISTORY: '/api/chat/history',
            SESSIONS: '/api/chat/sessions',
            SESSION: (id: string) => `/api/chat/sessions/${id}`,
            DELETE_SESSION: (id: string) => `/api/chat/sessions/${id}`,
            UPDATE_SESSION: (id: string) => `/api/chat/sessions/${id}`,
            STATS: '/api/chat/stats',
        },

        LAWYERS: {
            LIST: '/lawyers/',
            REGISTER: '/lawyers/register',
            LOGIN: '/lawyers/login',
            ME: '/lawyers/me',
            UPDATE_PROFILE: '/lawyers/me',
            VERIFY_EMAIL: '/lawyers/verify-email',
            CHANGE_PASSWORD: '/lawyers/change-password',
            FORGOT_PASSWORD: '/lawyers/forgot-password',
            RESET_PASSWORD: '/lawyers/reset-password',
            SESSIONS: '/lawyers/sessions',
            REVOKE_SESSION: (id: number) => `/lawyers/sessions/${id}`,
        },

        LEGAL_QUERIES: {
            CREATE: '/legal-queries',
            GET: '/legal-queries',
        },
    },
};


export const APP_CONFIG = {
    NAME: 'Sentilex AI Advocate',
    FRONTEND_URL: ENV.FRONTEND_URL,
    GOOGLE_AUTH_ENABLED: ENV.ENABLE_GOOGLE_AUTH,
    TOKEN_STORAGE_KEY: 'sentilex_auth_token',
    REFRESH_TOKEN_STORAGE_KEY: 'sentilex_refresh_token',
    USER_STORAGE_KEY: 'sentilex_user',
    USER_TYPE_STORAGE_KEY: 'sentilex_user_type',
};

export const API_BASE_URL = API_CONFIG.BASE_URL;
