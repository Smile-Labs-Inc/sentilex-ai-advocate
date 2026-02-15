// Environment variables (can be overridden by .env file)
const ENV = {
  API_URL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8001",
  FRONTEND_URL: import.meta.env.VITE_FRONTEND_URL || "http://localhost:5173",
  ENABLE_GOOGLE_AUTH:
    import.meta.env.VITE_ENABLE_GOOGLE_AUTH === "true" || false,
  PAYPAL_CLIENT_ID: import.meta.env.VITE_PAYPAL_CLIENT_ID || "",
};

export const API_CONFIG = {
  BASE_URL: ENV.API_URL,
  TIMEOUT: 30000,
  PAYPAL_CLIENT_ID: ENV.PAYPAL_CLIENT_ID,
  ENDPOINTS: {
    AUTH: {
      REGISTER: "/auth/register",
      LOGIN: "/auth/login",
      LOGOUT: "/auth/logout",
      REFRESH: "/auth/refresh",
      VERIFY_EMAIL: "/auth/verify-email",
      RESEND_VERIFICATION: "/auth/resend-verification",
      FORGOT_PASSWORD: "/auth/forgot-password",
      RESET_PASSWORD: "/auth/reset-password",
      CHANGE_PASSWORD: "/auth/change-password",
      ME: "/auth/me",
      UPDATE_PROFILE: "/auth/me",
      SESSIONS: "/auth/sessions",
      REVOKE_SESSION: (id: number) => `/auth/sessions/${id}`,
      MFA: {
        SETUP: "/auth/mfa/setup",
        ENABLE: "/auth/mfa/enable",
        DISABLE: "/auth/mfa/disable",
        STATUS: "/auth/mfa/status",
        REGENERATE_CODES: "/auth/mfa/regenerate-backup-codes",
      },
    },

    ADMIN_AUTH: {
      LOGIN: "/admin/auth/login",
      MFA: {
        SETUP: "/admin/auth/mfa/setup",
        ENABLE: "/admin/auth/mfa/enable",
        VERIFY: "/admin/auth/mfa/verify",
        DISABLE: "/admin/auth/mfa/disable",
        REGENERATE_CODES: "/admin/auth/mfa/regenerate-backup-codes",
      },
    },

    GOOGLE_AUTH: {
      LOGIN: "/auth/google/login",
      CALLBACK: "/auth/google/callback",
      COMPLETE_PROFILE_USER: "/auth/google/complete-profile/user",
      COMPLETE_PROFILE_LAWYER: "/auth/google/complete-profile/lawyer",
      PROFILE_STATUS: "/auth/google/profile-status",
    },

    LAWBOOK: {
      CHAT: "/lawbook/chat", // Legacy?
      LAWS: "/lawbook/",
      LAW_CONTENT: (filename: string) => `/lawbook/${filename}`,
      QUERY: "/lawbook/query",
    },

    CHAT: {
      SEND: "/chat/send",
      HISTORY: "/chat/history",
      SESSIONS: "/chat/sessions",
      SESSION: (id: string) => `/chat/sessions/${id}`,
      DELETE_SESSION: (id: string) => `/chat/sessions/${id}`,
      UPDATE_SESSION: (id: string) => `/chat/sessions/${id}`,
      MESSAGES: "/chat/messages",
      DELETE_MESSAGE: (id: number) => `/chat/messages/${id}`,
      STATS: "/chat/stats",
    },

    LAWYERS: {
      LIST: "/lawyers/",
      REGISTER: "/lawyers/register",
      LOGIN: "/lawyers/login",
      ME: "/lawyers/me",
      UPDATE_PROFILE: "/lawyers/me",
      VERIFY_EMAIL: "/lawyers/verify-email",
      CHANGE_PASSWORD: "/lawyers/change-password",
      FORGOT_PASSWORD: "/lawyers/forgot-password",
      RESET_PASSWORD: "/lawyers/reset-password",
      SESSIONS: "/lawyers/sessions",
      REVOKE_SESSION: (id: number) => `/lawyers/sessions/${id}`,
    },

    VERIFICATION: {
      STATUS: "/lawyer/verification/status",
      STEP2: "/lawyer/verification/step2",
      UPLOAD: (type: string) => `/lawyer/verification/step3/upload/${type}`,
      DECLARE: "/lawyer/verification/step4/declare",
      ADMIN_VERIFY: (id: number) => `/lawyer/verification/admin/${id}/verify`,
      ADMIN_DOCUMENTS: (id: number) =>
        `/lawyer/verification/admin/${id}/documents`,
    },

    LEGAL_QUERIES: {
      // Points to Lawbook query or Legal router
      CREATE: "/lawbook/query",
      AUDIT: (sessionId: string) => `/legal/audit/${sessionId}`,
      EXPORT: (sessionId: string) => `/legal/export/${sessionId}`,
    },

    INCIDENTS: {
      LIST: "/incidents/",
      CREATE: "/incidents/",
      GET: (id: number) => `/incidents/${id}`,
      UPDATE: (id: number) => `/incidents/${id}`,
      DELETE: (id: number) => `/incidents/${id}`,
      MESSAGES: {
        SEND: (id: number) => `/incidents/${id}/messages`,
        LIST: (id: number) => `/incidents/${id}/messages`,
      },
      EVIDENCE: {
        UPLOAD: (id: number) => `/incidents/${id}/evidence`,
        LIST: (id: number) => `/incidents/${id}/evidence`,
        DELETE: (incidentId: number, evidenceId: number) =>
          `/incidents/${incidentId}/evidence/${evidenceId}`,
      },
      AGENT: (id: number) => `/incidents/${id}/agent`,
    },

    OCCURRENCES: {
      CREATE: (incidentId: number) => `/incidents/${incidentId}/occurrences`,
      LIST: (incidentId: number) => `/incidents/${incidentId}/occurrences`,
      GET: (incidentId: number, occurrenceId: number) =>
        `/incidents/${incidentId}/occurrences/${occurrenceId}`,
      UPDATE: (incidentId: number, occurrenceId: number) =>
        `/incidents/${incidentId}/occurrences/${occurrenceId}`,
      DELETE: (incidentId: number, occurrenceId: number) =>
        `/incidents/${incidentId}/occurrences/${occurrenceId}`,
    },

    EVIDENCE: {
      LIST_ALL: "/evidence/",
      GET: (id: number) => `/evidence/${id}`,
      DOWNLOAD: (id: number) => `/evidence/${id}/download`,
      PREVIEW: (id: number) => `/evidence/${id}/preview`,
      DELETE: (id: number) => `/evidence/${id}`,
    },

    NOTIFICATIONS: {
      LIST: "/notifications/my",
      UNREAD: "/notifications/my/unread",
      COUNT: "/notifications/my/count",
      MARK_READ: "/notifications/my/mark-read",
      MARK_ALL_READ: "/notifications/my/mark-all-read",
      DELETE: (id: number) => `/notifications/my/${id}`,
      STATS: "/notifications/my/stats",
      WS: "/notifications/ws",
    },

    PAYMENTS: {
      UPGRADE: "/payments/upgrade",
      STATUS: "/payments/subscription",
    },

    DOCUMENTS: {
      POLICE_STATEMENT: (id: number) =>
        `/documents/incidents/${id}/export/police-statement`,
      CERT_REPORT: (id: number) =>
        `/documents/incidents/${id}/export/cert-report`,
      EVIDENCE_MANIFEST: (id: number) =>
        `/documents/incidents/${id}/export/evidence-manifest`,
      CASE_FILE: (id: number) => `/documents/incidents/${id}/export/case-file`,
    },

    STATS: {
      USER: "/stats/user",
      GLOBAL: "/stats/global",
    },
  },
};

export const APP_CONFIG = {
  NAME: "Sentilex AI Advocate",
  FRONTEND_URL: ENV.FRONTEND_URL,
  GOOGLE_AUTH_ENABLED: ENV.ENABLE_GOOGLE_AUTH,
  TOKEN_STORAGE_KEY: "sentilex_auth_token",
  REFRESH_TOKEN_STORAGE_KEY: "sentilex_refresh_token",
  USER_STORAGE_KEY: "sentilex_user",
  USER_TYPE_STORAGE_KEY: "sentilex_user_type",
};

export const API_BASE_URL = API_CONFIG.BASE_URL;
