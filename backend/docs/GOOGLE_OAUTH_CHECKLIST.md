# Google OAuth Setup Checklist

## ✅ Quick Setup Guide

### 1. Google Cloud Console Setup
- [ ] Go to https://console.cloud.google.com/
- [ ] Create new project or select existing one
- [ ] Enable Google+ API
- [ ] Create OAuth 2.0 Client ID credentials
- [ ] Add authorized redirect URIs:
  - `http://localhost:8000/auth/google/callback` (development)
  - `https://yourdomain.com/auth/google/callback` (production)
- [ ] Copy Client ID and Client Secret

### 2. Environment Configuration
- [ ] Open `backend/.env` file
- [ ] Add Google OAuth credentials:
  ```bash
  GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
  GOOGLE_CLIENT_SECRET=your_client_secret_here
  GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
  ```
- [ ] Verify CORS_ORIGINS includes your frontend URL:
  ```bash
  CORS_ORIGINS=http://localhost:5173,http://localhost:3000
  ```

### 3. Install Dependencies
```bash
cd backend
pip install authlib itsdangerous
```

### 4. Run Database Migration
```bash
cd backend
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade 003_add_mfa_password -> cb7f6be58644, add_oauth_to_lawyers
```

### 5. Verify Installation

**Check database columns:**
```sql
DESCRIBE lawyers;
-- Should see: oauth_provider, oauth_id columns
```

**Start backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Test endpoints:**
- User OAuth: http://localhost:8000/auth/google/login?user_type=user
- Lawyer OAuth: http://localhost:8000/auth/google/login?user_type=lawyer

### 6. Frontend Integration

**Option A: Use demo HTML**
Open `frontend/google-oauth-demo.html` in browser

**Option B: Add to your React app**
```javascript
// User login button
<a href="http://localhost:8000/auth/google/login?user_type=user">
  Sign in with Google (User)
</a>

// Lawyer login button
<a href="http://localhost:8000/auth/google/login?user_type=lawyer">
  Sign in with Google (Lawyer)
</a>
```

**⚠️ SECURITY WARNING: Current Implementation**

The current OAuth flow passes JWT tokens in URL query parameters and suggests storing them in localStorage. This has serious security implications:

- **URL Token Leakage**: Tokens in URLs can leak via:
  - Browser history
  - Server logs
  - Referrer headers
  - Shared URLs
- **localStorage XSS Risk**: Any XSS vulnerability can steal tokens from localStorage
- **Token Replay**: Stolen tokens can impersonate users until expiration

**🔒 RECOMMENDED: Secure OAuth Callback Pattern**

Instead of the insecure pattern, implement this secure approach:

```javascript
// Route: /oauth-callback
// DON'T DO THIS (insecure):
// const token = new URLSearchParams(window.location.search).get('token');
// localStorage.setItem('access_token', token);

// DO THIS (secure):
async function handleOAuthCallback() {
  const code = new URLSearchParams(window.location.search).get('code');
  const state = new URLSearchParams(window.location.search).get('state');
  
  // Verify state to prevent CSRF
  const savedState = sessionStorage.getItem('oauth_state');
  if (state !== savedState) {
    throw new Error('Invalid OAuth state');
  }
  
  // Exchange code for token server-side (not exposed to browser)
  const response = await fetch('http://localhost:8000/auth/google/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, state }),
    credentials: 'include' // Send/receive HTTP-only cookies
  });
  
  if (response.ok) {
    // Token stored in HTTP-only cookie by backend
    // Redirect to dashboard
    window.location.href = '/dashboard';
  }
}
```

**Backend changes needed:**
1. Return authorization code instead of token in redirect
2. Create `/auth/google/token` endpoint to exchange code for token
3. Set token in HTTP-only cookie (not accessible to JavaScript)
4. Include CSRF protection with state parameter

## 🧪 Testing Checklist

### User Flow
- [ ] Click "Sign in with Google" (user)
- [ ] Grant Google permissions
- [ ] Redirected back to app
- [ ] User account created in database
- [ ] Email verified automatically
- [ ] JWT token received

### Lawyer Flow
- [ ] Click "Sign in with Google" (lawyer)
- [ ] Grant Google permissions
- [ ] Redirected back to app
- [ ] Lawyer account created in database
- [ ] Email verified automatically
- [ ] Profile needs completion

### Database Verification
```sql
-- Check OAuth users
SELECT id, email, oauth_provider, oauth_id, email_verified 
FROM users 
WHERE oauth_provider = 'google';

-- Check OAuth lawyers
SELECT id, name, email, oauth_provider, oauth_id, is_email_verified
FROM lawyers 
WHERE oauth_provider = 'google';
```

## 📋 Files Modified/Created

### Modified Files:
- ✅ `backend/models/lawyers.py` - Added OAuth fields
- ✅ `backend/routers/google_oauth.py` - Updated for user/lawyer support
- ✅ `backend/.env.example` - Added Google OAuth config

### Created Files:
- ✅ `backend/alembic/versions/cb7f6be58644_add_oauth_to_lawyers.py` - Migration
- ✅ `backend/docs/GOOGLE_OAUTH_SETUP.md` - Full documentation
- ✅ `frontend/google-oauth-demo.html` - Demo page
- ✅ `backend/docs/GOOGLE_OAUTH_CHECKLIST.md` - This file

## 🚨 Common Issues

### Issue: "Redirect URI mismatch"
**Solution:** Verify redirect URI in Google Console matches exactly:
```
http://localhost:8000/auth/google/callback
```

### Issue: "Invalid client"
**Solution:** Check .env file has correct credentials without quotes or extra spaces

### Issue: CORS errors
**Solution:** Add frontend URL to CORS_ORIGINS in .env

### Issue: OAuth users can't reset password
**Expected:** OAuth users don't have passwords - this is correct behavior

## 📚 Documentation

Full documentation available at:
- `backend/docs/GOOGLE_OAUTH_SETUP.md` - Complete setup guide
- Demo page: `frontend/google-oauth-demo.html`

## 🎯 Next Steps

After successful setup:
1. Test both user and lawyer OAuth flows
2. Customize redirect URLs for your frontend
3. Add Google login buttons to your UI
4. Handle OAuth callback in frontend
5. Display user/lawyer profile after login
6. For lawyers: Prompt to complete profile fields
7. Deploy to production with HTTPS

## 🔐 Security Notes

### Critical Security Issues in Current Implementation

**⚠️ URGENT: The current OAuth flow has serious security vulnerabilities**

Current issues:
- ❌ JWT tokens passed in URL query parameters (leak risk)
- ❌ Tokens stored in localStorage (XSS vulnerability)
- ❌ No CSRF protection with state parameter
- ❌ No authorization code exchange flow

**Required Security Improvements:**

1. **Implement Authorization Code Flow**
   - Backend should return authorization code (not token) in redirect
   - Frontend exchanges code for token via secure endpoint
   - Token never exposed in URL or browser

2. **Use HTTP-Only Cookies**
   - Store JWT in HTTP-only cookie (not accessible to JavaScript)
   - Prevents XSS attacks from stealing tokens
   - Set SameSite=Strict for CSRF protection

3. **Add CSRF Protection**
   - Generate random state parameter before OAuth flow
   - Verify state matches after callback
   - Prevents cross-site request forgery

4. **Backend Code Required:**
   ```python
   # New endpoint needed: /auth/google/token
   @router.post("/google/token")
   async def exchange_code_for_token(
       code: str,
       state: str,
       response: Response
   ):
       # 1. Verify state parameter
       # 2. Exchange code with Google
       # 3. Create/login user
       # 4. Generate JWT
       # 5. Set HTTP-only cookie
       response.set_cookie(
           key="access_token",
           value=jwt_token,
           httponly=True,
           secure=True,  # HTTPS only in production
           samesite="strict",
           max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
       )
       return {"success": True}
   ```

### Additional Security Best Practices

- OAuth users have NULL password_hash
- Email is automatically verified
- JWT tokens expire per JWT_ACCESS_TOKEN_EXPIRE_MINUTES
- **ALWAYS use HTTPS in production** (required for secure cookies)
- Store Client Secret securely (never commit to git)
- Consider account linking for existing email users
- Implement token refresh mechanism
- Add rate limiting on OAuth endpoints
- Log all OAuth authentication attempts

---

**Need help?** See full documentation in `docs/GOOGLE_OAUTH_SETUP.md`
