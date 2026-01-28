# 🚀 Quick Migration Setup Guide

## Step-by-Step Instructions

### 1️⃣ Update Environment Variables

Add these to your `.env` file (copy from `.env.example`):

```env
# S3/MinIO Configuration for Document Storage
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_REGION_NAME=us-east-1
S3_BUCKET_NAME=lawyer-verification
```

### 2️⃣ Install Required Packages

```bash
pip install alembic pymysql boto3
```

### 3️⃣ Create Database

```sql
CREATE DATABASE sentilex CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4️⃣ Run Migration

```bash
# From backend directory
alembic upgrade head
```

### 5️⃣ Verify Tables

```sql
USE sentilex;
SHOW TABLES;
DESCRIBE lawyers;
DESCRIBE lawyer_verification_audit;
```

## ✅ What Was Added

### Files Created:
- ✅ `alembic.ini` - Alembic configuration
- ✅ `alembic/env.py` - Migration environment
- ✅ `alembic/versions/001_add_verification.py` - Verification migration
- ✅ `config.py` - Centralized settings
- ✅ `auth/dependencies.py` - Auth helpers (mock for now)
- ✅ `DATABASE_SETUP.md` - Full setup guide

### Environment Variables Added:
- ✅ S3_ENDPOINT_URL
- ✅ S3_ACCESS_KEY
- ✅ S3_SECRET_KEY
- ✅ S3_REGION_NAME
- ✅ S3_BUCKET_NAME

### Database Changes:
- ✅ 27 new columns added to `lawyers` table
- ✅ New `lawyer_verification_audit` table
- ✅ 3 indexes for performance

## 🎯 Next Steps

1. **Update .env** with your actual database credentials
2. **Run migration**: `alembic upgrade head`
3. **Start MinIO** (for local dev) or configure AWS S3
4. **Test endpoints** at http://localhost:8000/docs
5. **Implement JWT auth** in auth/dependencies.py

## 📍 Endpoint Routes Available

```
Verification Endpoints:
  POST /api/lawyer/verification/step2          - Submit enrollment details
  POST /api/lawyer/verification/step3/upload/... - Upload documents
  POST /api/lawyer/verification/step4/declare   - Accept declaration
  GET  /api/lawyer/verification/status          - Get verification status
  
Admin Endpoints:
  POST /api/lawyer/verification/admin/{id}/verify    - Approve/reject
  GET  /api/lawyer/verification/admin/{id}/documents - View documents
```

## 🔧 Test with Swagger

1. Start server: `python app.py`
2. Open: http://localhost:8000/docs
3. Try the verification endpoints
4. Check audit logs in database

---

**Need help?** See [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed troubleshooting.
