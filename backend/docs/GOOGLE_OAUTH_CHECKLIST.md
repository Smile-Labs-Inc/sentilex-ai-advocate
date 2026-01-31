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

**Create OAuth callback route:**
```javascript
// Route: /oauth-callback
const token = new URLSearchParams(window.location.search).get('token');
localStorage.setItem('access_token', token);
```

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

- OAuth users have NULL password_hash
- Email is automatically verified
- JWT tokens expire per JWT_ACCESS_TOKEN_EXPIRE_MINUTES
- Use HTTPS in production
- Store Client Secret securely (never commit to git)
- Consider account linking for existing email users

---

**Need help?** See full documentation in `docs/GOOGLE_OAUTH_SETUP.md`
