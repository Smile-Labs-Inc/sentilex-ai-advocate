# Google OAuth Authentication Setup Guide

This guide explains how to set up Google OAuth authentication for both users and lawyers in the SentiLex AI Advocate platform.

## Overview

The application supports Google OAuth 2.0 authentication, allowing users and lawyers to sign in using their Google accounts. This provides:

- **Seamless authentication** - No need to remember another password
- **Auto-verified emails** - Google-authenticated emails are automatically verified
- **Secure login** - Leverages Google's security infrastructure
- **Separate flows** - Different authentication paths for users and lawyers

## Architecture

### User Types

1. **Users (Citizens)**: Regular users seeking legal information
2. **Lawyers**: Legal professionals providing services

Both user types can authenticate via:
- Traditional email/password
- Google OAuth (new feature)

### Database Schema

#### Users Table
```sql
- oauth_provider: VARCHAR(20) - e.g., "google"
- oauth_id: VARCHAR(255) - Google's unique user ID (sub)
- password_hash: VARCHAR(255) - NULL for OAuth users
- email_verified: BOOLEAN - Auto-set to TRUE for OAuth users
```

#### Lawyers Table
```sql
- oauth_provider: VARCHAR(20) - e.g., "google"
- oauth_id: VARCHAR(255) - Google's unique user ID (sub)
- password_hash: VARCHAR(255) - NULL for OAuth users
- is_email_verified: BOOLEAN - Auto-set to TRUE for OAuth users
```

## Setup Instructions

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Create a new project or select an existing one

3. Enable Google+ API:
   - Navigate to **APIs & Services** > **Library**
   - Search for "Google+ API"
   - Click **Enable**

4. Create OAuth 2.0 Credentials:
   - Go to **APIs & Services** > **Credentials**
   - Click **Create Credentials** > **OAuth client ID**
   - Select **Web application**
   - Configure:
     - **Name**: SentiLex AI Advocate
     - **Authorized JavaScript origins**:
       - `http://localhost:5173` (frontend dev)
       - `http://localhost:8000` (backend dev)
       - `https://yourdomain.com` (production)
     - **Authorized redirect URIs**:
       - `http://localhost:8000/auth/google/callback` (dev)
       - `https://api.yourdomain.com/auth/google/callback` (production)

5. Copy the **Client ID** and **Client Secret**

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Frontend URL for redirects
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. Install Required Packages

The following packages are required (already in requirements.txt):

```bash
pip install authlib
pip install itsdangerous  # For session management
```

### 4. Run Database Migration

Apply the OAuth migration to add new columns:

```bash
cd backend
alembic upgrade head
```

This will add `oauth_provider` and `oauth_id` columns to the `lawyers` table.

## API Endpoints

### For Users

#### Initiate Google Login (User)
```http
GET /auth/google/login?user_type=user
```

**Response**: Redirects to Google's OAuth consent screen

**Flow**:
1. User clicks "Sign in with Google" on frontend
2. Frontend redirects to `/auth/google/login?user_type=user`
3. Backend redirects to Google OAuth
4. User grants permission
5. Google redirects to `/auth/google/callback`
6. Backend creates/logs in user
7. Backend redirects to frontend with JWT token

#### OAuth Callback
```http
GET /auth/google/callback?code=...&state=user
```

**Response**: Redirects to frontend with token
```
http://localhost:5173/oauth-callback?token=<JWT_TOKEN>&type=user
```

### For Lawyers

#### Initiate Google Login (Lawyer)
```http
GET /auth/google/login?user_type=lawyer
```

**Response**: Redirects to Google's OAuth consent screen

**Flow**:
1. Lawyer clicks "Sign in with Google" on lawyer portal
2. Frontend redirects to `/auth/google/login?user_type=lawyer`
3. Backend redirects to Google OAuth
4. Lawyer grants permission
5. Google redirects to `/auth/google/callback`
6. Backend creates/logs in lawyer with default values
7. Backend redirects to lawyer dashboard with JWT token

#### OAuth Callback
```http
GET /auth/google/callback?code=...&state=lawyer
```

**Response**: Redirects to frontend with token
```
http://localhost:5173/lawyer/oauth-callback?token=<JWT_TOKEN>&type=lawyer
```

## Frontend Integration

### User Login Button (React Example)

```javascript
import React from 'react';

const GoogleLoginButton = () => {
  const handleGoogleLogin = () => {
    // Redirect to backend OAuth endpoint
    window.location.href = 'http://localhost:8000/auth/google/login?user_type=user';
  };

  return (
    <button 
      onClick={handleGoogleLogin}
      className="google-login-btn"
    >
      <img src="/google-icon.svg" alt="Google" />
      Sign in with Google
    </button>
  );
};

export default GoogleLoginButton;
```

### Lawyer Login Button

```javascript
const GoogleLawyerLoginButton = () => {
  const handleGoogleLogin = () => {
    window.location.href = 'http://localhost:8000/auth/google/login?user_type=lawyer';
  };

  return (
    <button onClick={handleGoogleLogin}>
      Sign in with Google (Lawyer)
    </button>
  );
};
```

### OAuth Callback Handler

Create route handlers in your frontend to receive the token:

```javascript
// User callback: /oauth-callback
import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get('token');
    const type = searchParams.get('type');

    if (token) {
      // Store token
      localStorage.setItem('access_token', token);
      
      // Redirect based on type
      if (type === 'user') {
        navigate('/dashboard');
      } else if (type === 'lawyer') {
        navigate('/lawyer/dashboard');
      }
    } else {
      navigate('/login?error=oauth_failed');
    }
  }, [searchParams, navigate]);

  return <div>Processing login...</div>;
};
```

## User Experience Flow

### First-Time User (OAuth)

1. User clicks "Sign in with Google"
2. Redirected to Google consent screen
3. User grants permission
4. Account automatically created with:
   - Email from Google
   - Name from Google profile
   - Email verified = true
   - OAuth provider = "google"
   - No password required
5. User redirected to dashboard with JWT token

### Returning User (OAuth)

1. User clicks "Sign in with Google"
2. System finds existing account by email
3. User logged in immediately
4. Redirected to dashboard

### First-Time Lawyer (OAuth)

1. Lawyer clicks "Sign in with Google" on lawyer portal
2. Account created with default values:
   - Name from Google
   - Email verified = true
   - Specialties = "General Practice" (can update later)
   - Experience = 0 (can update later)
   - District = "Colombo" (can update later)
   - Phone = "" (must update later)
   - Verification status = "not_started"
3. Lawyer needs to complete profile and verification process

## Security Considerations

### Password Handling
- OAuth users have `password_hash = NULL`
- They cannot use traditional login
- Password reset is disabled for OAuth users

### Email Verification
- OAuth emails are automatically verified
- `email_verified` or `is_email_verified` set to `true`

### Account Linking
- Currently, accounts are NOT linked by email
- OAuth creates separate accounts from email/password accounts
- Future: Implement account linking for same email

### Token Security
- JWT tokens include user ID, role, and email
- Tokens expire based on `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- Refresh tokens supported separately

## Testing

### Manual Testing

1. Start backend:
```bash
cd backend
uvicorn main:app --reload
```

2. Test user OAuth:
```
http://localhost:8000/auth/google/login?user_type=user
```

3. Test lawyer OAuth:
```
http://localhost:8000/auth/google/login?user_type=lawyer
```

### Database Verification

Check if OAuth users were created:

```sql
-- Check users
SELECT id, email, oauth_provider, oauth_id, email_verified, password_hash
FROM users 
WHERE oauth_provider = 'google';

-- Check lawyers
SELECT id, email, oauth_provider, oauth_id, is_email_verified, password_hash
FROM lawyers 
WHERE oauth_provider = 'google';
```

## Troubleshooting

### "Redirect URI mismatch" error
- Verify the redirect URI in Google Cloud Console matches exactly
- Check for http vs https
- Ensure port numbers match

### "Invalid client" error
- Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Ensure credentials are for the correct project

### Users not being created
- Check database connection
- Verify migrations have run
- Check backend logs for errors

### Token not received on frontend
- Verify `CORS_ORIGINS` includes your frontend URL
- Check browser console for redirect issues
- Ensure frontend callback route exists

## Production Deployment

### Google Cloud Console
1. Add production redirect URI:
   ```
   https://api.yourdomain.com/auth/google/callback
   ```

2. Add production JavaScript origins:
   ```
   https://yourdomain.com
   ```

### Environment Variables
```bash
GOOGLE_REDIRECT_URI=https://api.yourdomain.com/auth/google/callback
CORS_ORIGINS=https://yourdomain.com
```

### SSL/TLS
- Google requires HTTPS for production OAuth
- Use proper SSL certificates
- Redirect HTTP to HTTPS

## Future Enhancements

1. **Account Linking**: Link OAuth and email/password accounts by email
2. **Multiple Providers**: Add Facebook, LinkedIn, Apple Sign-In
3. **Profile Completion**: Prompt OAuth lawyers to complete required fields
4. **Admin Dashboard**: View OAuth vs password users
5. **Account Merging**: Allow users to merge duplicate accounts

## Support

For issues or questions:
- Check [FastAPI OAuth Documentation](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)
- Review [Authlib Documentation](https://docs.authlib.org/en/latest/)
- Contact: support@sentilex.lk

---

**Last Updated**: January 31, 2026
**Version**: 1.0.0
