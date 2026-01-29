# Alembic Database Migrations

This directory contains database migrations for the SentiLex AI Advocate system.

## Setup

1. **Configure Database Connection**
   ```bash
   # Update your .env file with database credentials
   DB_DRIVER=mysql+pymysql
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=sentilex
   ```

2. **Install Alembic** (if not already installed)
   ```bash
   pip install alembic
   ```

## Running Migrations

### Apply All Migrations
```bash
# From the backend directory
alembic upgrade head
```

### Check Current Version
```bash
alembic current
```

### View Migration History
```bash
alembic history --verbose
```

### Rollback Last Migration
```bash
alembic downgrade -1
```

### Rollback to Specific Version
```bash
alembic downgrade <revision_id>
```

## Creating New Migrations

### Auto-generate Migration from Model Changes
```bash
alembic revision --autogenerate -m "description of changes"
```

### Create Empty Migration
```bash
alembic revision -m "description of changes"
```

## Migration Files

- `001_add_verification.py` - Adds lawyer verification system tables and columns
  - Adds verification workflow columns to `lawyers` table
  - Creates `lawyer_verification_audit` table for audit trail
  - Adds indexes for performance

## Verification System Schema

### Lawyers Table Extensions
- **Verification Flow**: `verification_step`, `verification_status`, timestamps
- **Legal Enrollment**: `sc_enrollment_number`, `enrollment_year`, `law_college_reg_number`
- **Document URLs**: NIC front/back, attorney certificate, practising certificate (with hashes)
- **Declaration**: `declaration_accepted`, IP address, timestamp
- **Admin Review**: `verified_by_admin_id`, `verified_at`, `rejection_reason`, `admin_notes`

### Lawyer Verification Audit Table
- Immutable audit log of all verification actions
- Tracks: lawyer_id, action, step, performer, IP, timestamp, details

## Important Notes

⚠️ **Before running migrations in production:**
1. Backup your database
2. Review migration files
3. Test in staging environment first
4. Ensure all dependencies are installed

## Troubleshooting

### "Table already exists" error
If you already have tables, you may need to stamp the current version:
```bash
alembic stamp head
```

### Connection errors
- Verify database is running
- Check .env credentials
- Ensure database exists: `CREATE DATABASE sentilex;`

### Import errors
Make sure you're running commands from the `backend/` directory where the models are located.
