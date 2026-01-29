# Database Migration Guide

## Overview

This guide covers database migrations for the authentication and security system.

## Migration: 002_auth_system

**Created:** January 29, 2026  
**Dependencies:** 001_add_verification

### What This Migration Does

This migration adds comprehensive authentication and security features:

1. **Admin User System**
   - Creates `admins` table with role-based access (admin, superadmin)
   - Password authentication with bcrypt/argon2 hashing
   - Mandatory MFA (Multi-Factor Authentication) support
   - Account lockout and security features
   - Session management

2. **Lawyer Authentication**
   - Extends `lawyers` table with authentication fields
   - Password hashing and security
   - Optional MFA support
   - Email verification
   - Password reset functionality

3. **Token Management**
   - Creates `token_blacklist` table for JWT revocation
   - Supports logout, password changes, and security events

4. **Security Monitoring**
   - Creates `login_attempts` table for tracking all login attempts
   - Failed login tracking for account lockout
   - Suspicious activity detection

5. **Session Tracking**
   - Creates `active_sessions` table
   - Device/browser identification
   - Remote logout capability
   - Session expiration management

## Running Migrations

### Using Python Script (Recommended)

```bash
# Navigate to backend directory
cd backend

# Check current migration status
python run_migration.py current

# View migration history
python run_migration.py history

# Apply all pending migrations
python run_migration.py upgrade

# Rollback last migration
python run_migration.py downgrade

# Stamp database (mark as migrated without running)
python run_migration.py stamp head
```

### Using Alembic Directly

```bash
# Navigate to backend directory
cd backend

# Check current revision
alembic current

# View migration history
alembic history

# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade 002_auth_system

# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade 001_add_verification

# View pending migrations
alembic show head
```

### Using PowerShell

```powershell
# Navigate to backend directory
cd backend

# Apply migrations
python run_migration.py upgrade
```

## New Database Schema

### Admins Table

```sql
CREATE TABLE admins (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'superadmin') DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(32),
    last_login TIMESTAMP,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- ... additional fields
);
```

### Lawyers Table Extensions

```sql
ALTER TABLE lawyers ADD COLUMN (
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    -- ... additional fields
);
```

### Token Blacklist Table

```sql
CREATE TABLE token_blacklist (
    jti VARCHAR(36) PRIMARY KEY,
    token_type VARCHAR(10) NOT NULL,
    user_id INT NOT NULL,
    user_type VARCHAR(10) NOT NULL,
    blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    reason VARCHAR(50) NOT NULL,
    -- ... additional fields
);
```

### Login Attempts Table

```sql
CREATE TABLE login_attempts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) NOT NULL,
    user_type VARCHAR(10) NOT NULL,
    success BOOLEAN NOT NULL,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) NOT NULL,
    failure_reason VARCHAR(100),
    is_suspicious BOOLEAN DEFAULT FALSE,
    -- ... additional fields
);
```

### Active Sessions Table

```sql
CREATE TABLE active_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    jti VARCHAR(36) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    user_type VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    device_type VARCHAR(20),
    browser VARCHAR(50),
    -- ... additional fields
);
```

## Post-Migration Tasks

After running the migration:

1. **Create Initial Admin Account**
   ```python
   # Run this script to create the first admin
   python scripts/create_admin.py
   ```

2. **Update Existing Lawyers**
   - Existing lawyers will have `password_hash` as NULL
   - They will need to register/set password through the auth flow
   - Or bulk update via admin panel

3. **Configure Environment Variables**
   - Add JWT secrets to `.env`
   - Configure password requirements
   - Set session timeouts

4. **Test Authentication**
   - Test admin login
   - Test lawyer registration
   - Test MFA setup
   - Test password reset flow

## Rollback Procedure

If you need to rollback this migration:

```bash
# Rollback to previous version
python run_migration.py downgrade

# Or use Alembic
alembic downgrade -1
```

**⚠️ WARNING:** Rolling back will:
- Drop all admin accounts
- Remove authentication fields from lawyers table
- Delete all login history
- Remove all active sessions
- Delete token blacklist

**Backup your database before rollback!**

## Troubleshooting

### Migration Fails Due to Existing Columns

If you've manually added columns that conflict:

```bash
# Check current state
python run_migration.py current

# Stamp database at correct revision
python run_migration.py stamp 002_auth_system
```

### MySQL Enum Type Issues

If you encounter enum issues:

```sql
-- Check existing enums
SHOW COLUMNS FROM lawyers LIKE 'verification_status';
SHOW COLUMNS FROM admins LIKE 'role';
```

### Index Creation Errors

If indexes already exist:

```sql
-- Drop conflicting indexes
DROP INDEX idx_admin_email ON admins;
DROP INDEX idx_lawyer_email_verified ON lawyers;
```

Then retry migration.

## Verification

After migration, verify tables exist:

```sql
-- Check tables
SHOW TABLES;

-- Verify admins structure
DESCRIBE admins;

-- Verify lawyers extensions
DESCRIBE lawyers;

-- Check other tables
DESCRIBE token_blacklist;
DESCRIBE login_attempts;
DESCRIBE active_sessions;

-- Verify indexes
SHOW INDEX FROM admins;
SHOW INDEX FROM lawyers;
```

## Next Steps

1. Run the migration
2. Create initial admin account
3. Implement JWT authentication (next phase)
4. Test authentication flows
5. Update frontend to use new auth system
