# Database Setup & Migration Guide

## 📋 Prerequisites

1. **MySQL/MariaDB Server** running
2. **Python environment** with dependencies installed
3. **Environment variables** configured in `.env`

## 🚀 Quick Start

### 1. Create Database

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE sentilex CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Verify
SHOW DATABASES;
USE sentilex;
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Database
DB_DRIVER=mysql+pymysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_password
DB_NAME=sentilex

# S3/MinIO for Document Storage
S3_ENDPOINT_URL=http://localhost:9000  # MinIO for local dev
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_REGION_NAME=us-east-1
S3_BUCKET_NAME=lawyer-verification
```

### 3. Install Dependencies

```bash
pip install alembic sqlalchemy pymysql boto3 python-dotenv
```

### 4. Run Migrations

```bash
# From backend directory
cd backend

# Apply all migrations
alembic upgrade head
```

### 5. Verify Database

```sql
-- Check tables were created
SHOW TABLES;

-- Verify lawyers table structure
DESCRIBE lawyers;

-- Verify audit table
DESCRIBE lawyer_verification_audit;
```

## 🏗️ Database Schema

### Lawyers Table (Extended)

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key |
| `name` | VARCHAR(100) | Lawyer name |
| `email` | VARCHAR(100) | Unique email |
| `verification_step` | INT | Current verification step (1-4) |
| `verification_status` | ENUM | not_started, in_progress, submitted, approved, rejected |
| `sc_enrollment_number` | VARCHAR(50) | Supreme Court enrollment (unique) |
| `enrollment_year` | INT | Year of enrollment |
| `nic_front_url` | VARCHAR(500) | S3 URL for NIC front |
| `nic_front_hash` | VARCHAR(64) | SHA-256 hash |
| `declaration_accepted` | BOOLEAN | Legal declaration status |
| `verified_by_admin_id` | INT | Admin who verified |
| `rejection_reason` | TEXT | Reason if rejected |

### Lawyer Verification Audit Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key |
| `lawyer_id` | INT | Foreign key to lawyers |
| `action` | VARCHAR(50) | Action performed |
| `step_number` | INT | Verification step |
| `performed_by` | VARCHAR(50) | Who performed action |
| `ip_address` | VARCHAR(45) | IP address |
| `details` | TEXT | JSON metadata |
| `created_at` | TIMESTAMP | When action occurred |

## 🔧 MinIO Setup (Local Development)

### Install MinIO

**Windows (PowerShell):**
```powershell
# Download MinIO
Invoke-WebRequest -Uri "https://dl.min.io/server/minio/release/windows-amd64/minio.exe" -OutFile "minio.exe"

# Start MinIO
.\minio.exe server C:\minio-data --console-address ":9001"
```

**Linux/Mac:**
```bash
# Download
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio

# Start
./minio server ~/minio-data --console-address ":9001"
```

### Configure MinIO

1. **Access Console**: http://localhost:9001
2. **Login**: minioadmin / minioadmin
3. **Create Bucket**: `lawyer-verification`
4. **Set Private**: Ensure bucket is not public

## 📝 Alembic Commands

```bash
# Check current version
alembic current

# View history
alembic history --verbose

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Generate new migration
alembic revision --autogenerate -m "description"

# Stamp database without running migrations
alembic stamp head
```

## ⚠️ Troubleshooting

### "No module named 'pymysql'"
```bash
pip install pymysql
```

### "Access denied for user"
- Check DB_PASSWORD in .env
- Verify MySQL user has permissions:
  ```sql
  GRANT ALL PRIVILEGES ON sentilex.* TO 'root'@'localhost';
  FLUSH PRIVILEGES;
  ```

### "Table 'lawyers' doesn't exist"
- Run base table creation first (if you have a base schema)
- Or create lawyers table manually before running verification migration

### MinIO connection errors
- Ensure MinIO is running: `http://localhost:9000`
- Verify S3_ENDPOINT_URL in .env
- Check bucket exists in MinIO console

## 🔐 Production Considerations

Before deploying to production:

1. **Use AWS S3** instead of MinIO
2. **Enable SSL** for database connections
3. **Rotate credentials** regularly
4. **Enable S3 encryption** at rest
5. **Set up bucket lifecycle policies**
6. **Configure CORS** if needed for frontend uploads
7. **Enable versioning** on S3 bucket
8. **Set up CloudWatch/monitoring**

## 📚 Next Steps

1. Test the verification endpoints with Postman/Swagger
2. Implement JWT authentication in `auth/dependencies.py`
3. Set up frontend document upload forms
4. Configure production S3 bucket
5. Add admin dashboard for verification review
