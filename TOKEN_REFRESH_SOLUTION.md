# Token Refresh Solution

## Problem Summary

The application was experiencing "unauthorized" errors when access tokens expired because:

1. **No automatic token refresh** - Access tokens expire after a set time (default: 30 minutes), but the frontend didn't automatically refresh them
2. **No 401 error handling** - Failed API requests didn't trigger token refresh attempts
3. **No expired refresh token handling** - When refresh tokens expired (default: 7 days), users weren't properly redirected to login

## Solution Overview

I've implemented a centralized API client (`apiClient.ts`) that:

1. ✅ **Automatically detects 401 errors** and attempts to refresh the access token
2. ✅ **Prevents race conditions** during token refresh with a singleton pattern
3. ✅ **Handles expired refresh tokens** by clearing storage and redirecting to login
4. ✅ **Maintains authentication state** across all API calls
5. ✅ **Works with all HTTP methods** (GET, POST, PUT, PATCH, DELETE)
6. ✅ **Supports FormData uploads** for file handling

## How It Works

```
User makes API request
    ↓
API Client adds Bearer token
    ↓
Request sent to backend
    ↓
Response received
    ↓
Is response 401 Unauthorized?
    │
    ├── NO → Return response to caller
    │
    └── YES → Try to refresh token
          ↓
          Refresh successful?
          │
          ├── YES → Retry original request with new token
          │         Return response to caller
          │
          └── NO → Clear tokens
                   Redirect to login page
```

## Implementation Details

### 1. API Client (`apiClient.ts`)

Located at: `frontend/src/services/apiClient.ts`

**Key Features:**
- Singleton instance prevents duplicate refresh attempts
- Uses promise-based token refresh to prevent race conditions
- Automatically adds Authorization headers to all requests
- Handles both JSON and FormData requests

**API:**
```typescript
// Main method - handles all request types
apiClient.fetch(url, options)

// Convenience methods
apiClient.get(url, options)
apiClient.post(url, body, options)
apiClient.put(url, body, options)
apiClient.patch(url, body, options)
apiClient.delete(url, options)
```

### 2. Updated Service Example (`incident.ts`)

The incident service has been fully updated to use the new API client.

**Before:**
```typescript
export async function getIncidents(): Promise<IncidentListResponse> {
  const token = authService.getToken();

  if (!token) {
    throw new Error("User is not authenticated");
  }

  const response = await fetch(`${API_BASE_URL}/incidents/`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch incidents: ${response.status}`);
  }

  return response.json();
}
```

**After:**
```typescript
export async function getIncidents(): Promise<IncidentListResponse> {
  const response = await apiClient.get(`${API_BASE_URL}/incidents/`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch incidents: ${response.status}`,
    );
  }

  return response.json();
}
```

**Benefits:**
- 50% less code
- Automatic token refresh on 401 errors
- No manual token management needed
- Consistent error handling

## Migration Guide

### Step 1: Update Service Imports

**Old:**
```typescript
import { API_BASE_URL, APP_CONFIG } from "../config";
```

**New:**
```typescript
import { API_BASE_URL } from "../config";
import { apiClient } from "./apiClient";
```

### Step 2: Remove `getAuthToken()` Helper

Remove this function if it exists in your service file:
```typescript
function getAuthToken(): string | null {
  return localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
}
```

### Step 3: Update Each API Function

#### For GET requests:
```typescript
// Before
const token = getAuthToken();
if (!token) throw new Error("User is not authenticated");

const response = await fetch(url, {
  method: "GET",
  headers: { Authorization: `Bearer ${token}` },
});

// After
const response = await apiClient.get(url);
```

#### For POST/PUT/PATCH requests:
```typescript
// Before
const token = getAuthToken();
if (!token) throw new Error("User is not authenticated");

const response = await fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify(data),
});

// After
const response = await apiClient.post(url, data);
```

#### For DELETE requests:
```typescript
// Before
const token = getAuthToken();
if (!token) throw new Error("User is not authenticated");

const response = await fetch(url, {
  method: "DELETE",
  headers: { Authorization: `Bearer ${token}` },
});

// After
const response = await apiClient.delete(url);
```

#### For FormData uploads:
```typescript
// Before
const token = getAuthToken();
if (!token) throw new Error("User is not authenticated");

const formData = new FormData();
formData.append("files", file);

const response = await fetch(url, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
  body: formData,
});

// After
const formData = new FormData();
formData.append("files", file);

const response = await apiClient.fetch(url, {
  method: "POST",
  body: formData,
});
```

## Services That Need Migration

The following service files still need to be updated:

1. ✅ `frontend/src/services/incident.ts` - **COMPLETED**
2. ⏳ `frontend/src/services/auth.ts` - Partially needs updates (skip login/register/refresh endpoints)
3. ⏳ `frontend/src/services/evidence.ts`
4. ⏳ `frontend/src/services/notification.ts`
5. ⏳ `frontend/src/services/documents.ts`
6. ⏳ `frontend/src/services/lawbook.tsx`
7. ⏳ `frontend/src/services/lawyers.tsx`

### Special Cases

#### `auth.ts` Service
- Keep using direct `fetch` for: `login()`, `register()`, `refreshToken()`
- These endpoints shouldn't trigger auto-refresh (would cause infinite loops)
- Use `apiClient` for: `getCurrentUser()`, `updateProfile()`, `getActiveSessions()`, etc.

Example for auth.ts:
```typescript
// GET current user - should use apiClient (can auto-refresh)
async getCurrentUser(): Promise<UserProfile> {
  const response = await apiClient.get(
    `${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.ME}`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch user profile');
  }

  return response.json();
}

// Login - should NOT use apiClient (manual fetch)
async login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.LOGIN}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });
  // ... rest of login logic
}
```

## Testing Checklist

After migration, test these scenarios:

1. **Normal API calls**: Make API requests with valid tokens - should work normally
2. **Expired access token**: Wait for token to expire, make request - should auto-refresh and succeed
3. **Expired refresh token**: Clear tokens or wait 7 days - should redirect to login
4. **Concurrent requests**: Make multiple API calls simultaneously - should only refresh once
5. **File uploads**: Test file upload functionality - should work with FormData
6. **Logout**: Logout and try to make requests - should redirect to login

## Benefits

1. **Seamless UX**: Users no longer see "unauthorized" errors when tokens expire
2. **Better DX**: Developers don't need to handle token refresh in each service
3. **Centralized logic**: All token handling is in one place
4. **Future-proof**: Easy to add retry logic, rate limiting, or other features
5. **Type-safe**: Full TypeScript support with proper types
6. **Less code**: 40-60% reduction in boilerplate code per service

## Configuration

Token expiration times are configured in the backend:

```python
# backend/config.py
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 days
```

To adjust these values, modify the backend configuration and restart the server.

## Troubleshooting

### Issue: Infinite refresh loop
**Solution**: Make sure `auth.ts` login/register/refresh methods don't use `apiClient`

### Issue: Still getting 401 errors
**Solution**: Check that the service is using `apiClient` instead of direct `fetch`

### Issue: FormData uploads failing
**Solution**: Don't set `Content-Type` header - let the browser set it with boundary

### Issue: Redirect to login not working
**Solution**: Check that routing is configured properly and `/auth/login` route exists

## Next Steps

1. Migrate remaining services to use `apiClient`
2. Test all API endpoints after migration
3. Monitor for any issues in production
4. Consider adding request retry logic for network failures
5. Add loading indicators during token refresh (optional)

## Resources

- API Client: `frontend/src/services/apiClient.ts`
- Example Migration: `frontend/src/services/incident.ts`
- Backend Auth: `backend/routers/auth.py`
- Token Utils: `backend/utils/auth.py`
