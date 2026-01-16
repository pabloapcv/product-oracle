# Winner Engine - Production Deployment Guide

## 🚀 Overview

This guide covers deploying the Winner Engine to production environments. The system is designed to run as a weekly batch pipeline that identifies and ranks product opportunities.

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+ (recommended) or SQLite (development only)
- 4GB+ RAM
- 20GB+ disk space (for data storage)
- Network access for data scraping/APIs

## 🏗️ Architecture Options

### Option 1: Single Server (Recommended for Start)

**Best for:** Small teams, MVP, testing

```
┌─────────────────────────────────┐
│   Single Server (VM/EC2)        │
│                                 │
│  - PostgreSQL                   │
│  - Python Pipeline              │
│  - Cron Jobs                    │
│  - Report Storage               │
└─────────────────────────────────┘
```

**Setup:**
- Ubuntu 20.04+ or similar
- PostgreSQL installed locally
- Python virtual environment
- Cron jobs for weekly pipeline

### Option 2: Containerized (Docker)

**Best for:** Scalability, reproducibility

```
┌─────────────────────────────────┐
│   Docker Compose                │
│                                 │
│  - PostgreSQL Container         │
│  - Pipeline Container           │
│  - Volume Mounts                │
└─────────────────────────────────┘
```

### Option 3: Cloud Services (Production)

**Best for:** High availability, scaling

```
┌─────────────────────────────────┐
│   Cloud Architecture            │
│                                 │
│  - RDS (PostgreSQL)             │
│  - ECS/Lambda (Pipeline)        │
│  - S3 (Reports/Models)          │
│  - CloudWatch (Monitoring)      │
└─────────────────────────────────┘
```

## 📦 Installation Steps

### Step 1: Server Setup

**Ubuntu/Debian:**
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install -y python3.9 python3-pip python3-venv postgresql postgresql-contrib git

# Install PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql@14 python@3.9
brew services start postgresql@14
```

### Step 2: Database Setup

```bash
# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE winner_engine;
CREATE USER winner_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE winner_engine TO winner_user;
\q
EOF

# Run migrations
psql -h localhost -U winner_user -d winner_engine -f sql/001_init.sql
```

### Step 3: Application Setup

```bash
# Clone repository
git clone https://github.com/pabloapcv/product-oracle.git
cd product-oracle

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_NAME=winner_engine
export DB_USER=winner_user
export DB_PASSWORD=your_secure_password
```

Or create `.env` file:
```bash
cat > .env << EOF
DB_HOST=localhost
DB_NAME=winner_engine
DB_USER=winner_user
DB_PASSWORD=your_secure_password
EOF
```

### Step 4: Initial Data Setup

```bash
# Seed initial entities
python -m src.utils.seed_data --entities

# (Optional) Seed sample data for testing
python -m src.utils.seed_data --all --dt 2026-01-12
```

## 🔄 Pipeline Automation

### Cron Job Setup

Create weekly pipeline cron job:

```bash
# Edit crontab
crontab -e

# Add weekly pipeline (runs every Monday at 2 AM)
0 2 * * 1 cd /path/to/product-oracle && /path/to/venv/bin/python -m src.pipeline --week_start $(date +\%Y-\%m-\%d) >> /var/log/winner-engine/pipeline.log 2>&1
```

### Systemd Service (Alternative)

Create `/etc/systemd/system/winner-engine.service`:

```ini
[Unit]
Description=Winner Engine Weekly Pipeline
After=network.target postgresql.service

[Service]
Type=oneshot
User=winner
WorkingDirectory=/opt/winner-engine
Environment="DB_HOST=localhost"
Environment="DB_NAME=winner_engine"
Environment="DB_USER=winner_user"
Environment="DB_PASSWORD=your_secure_password"
ExecStart=/opt/winner-engine/venv/bin/python -m src.pipeline --week_start $(date +\%Y-\%m-\%d)
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create weekly timer `/etc/systemd/system/winner-engine.timer`:

```ini
[Unit]
Description=Run Winner Engine Weekly
Requires=winner-engine.service

[Timer]
OnCalendar=Mon *-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable winner-engine.timer
sudo systemctl start winner-engine.timer
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment
ENV PYTHONPATH=/app
ENV DB_HOST=postgres
ENV DB_NAME=winner_engine
ENV DB_USER=winner_user
ENV DB_PASSWORD=winner_password

CMD ["python", "-m", "src.pipeline", "--week_start", "$(date +%Y-%m-%d)"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: winner_engine
      POSTGRES_USER: winner_user
      POSTGRES_PASSWORD: winner_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U winner_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  pipeline:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DB_HOST: postgres
      DB_NAME: winner_engine
      DB_USER: winner_user
      DB_PASSWORD: winner_password
    volumes:
      - ./reports:/app/reports
      - ./models:/app/models
    command: python -m src.pipeline --week_start $(date +%Y-%m-%d)

volumes:
  postgres_data:
```

**Run:**
```bash
docker-compose up -d
```

## ☁️ Cloud Deployment (AWS)

### RDS Setup

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier winner-engine-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username winner_user \
  --master-user-password your_secure_password \
  --allocated-storage 100 \
  --vpc-security-group-ids sg-xxxxx
```

### ECS Task Definition

```json
{
  "family": "winner-engine-pipeline",
  "containerDefinitions": [{
    "name": "pipeline",
    "image": "your-ecr-repo/winner-engine:latest",
    "memory": 2048,
    "environment": [
      {"name": "DB_HOST", "value": "winner-engine-db.xxxxx.rds.amazonaws.com"},
      {"name": "DB_NAME", "value": "winner_engine"},
      {"name": "DB_USER", "value": "winner_user"},
      {"name": "DB_PASSWORD", "value": "from-secrets-manager"}
    ]
  }]
}
```

### Lambda Function (Alternative)

For serverless approach, package pipeline as Lambda:

```python
# lambda_handler.py
import os
from datetime import date
from src.pipeline import run_full_pipeline

def lambda_handler(event, context):
    week_start = date.today()
    run_full_pipeline(week_start)
    return {"statusCode": 200, "body": "Pipeline completed"}
```

Schedule with EventBridge (CloudWatch Events):
- Rule: `cron(0 2 ? * MON *)` (Every Monday at 2 AM UTC)

## 🔐 Security Best Practices

### 1. Database Security

```bash
# Use strong passwords
# Enable SSL connections
# Restrict network access (firewall rules)
# Regular backups
```

### 2. Environment Variables

```bash
# Never commit secrets
# Use secrets management (AWS Secrets Manager, HashiCorp Vault)
# Rotate credentials regularly
```

### 3. Network Security

- Use VPN for database access
- Enable SSL/TLS for all connections
- Restrict ingress ports (only 22, 80, 443)
- Use security groups/firewalls

### 4. Access Control

```bash
# Create dedicated user for pipeline
CREATE USER pipeline_user WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO pipeline_user;

# Use read-only user for reports
CREATE USER report_user WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO report_user;
```

## 📊 Monitoring & Logging

### Application Logging

```python
# Configure logging in configs/config.yaml
logging:
  level: INFO
  file: /var/log/winner-engine/app.log
  max_size: 100MB
  backup_count: 10
```

### Database Monitoring

```bash
# Monitor database size
SELECT pg_size_pretty(pg_database_size('winner_engine'));

# Monitor table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Health Checks

Create `/health` endpoint or script:

```python
# health_check.py
from src.utils.db import get_db_connection

def check_health():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## 🔄 Backup & Recovery

### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump -h localhost -U winner_user winner_engine | gzip > /backups/winner_engine_$DATE.sql.gz

# Keep last 30 days
find /backups -name "winner_engine_*.sql.gz" -mtime +30 -delete
```

### Automated Backups (AWS RDS)

- Enable automated backups in RDS
- Retention: 7-35 days
- Point-in-time recovery available

## 📈 Scaling Considerations

### Vertical Scaling
- Increase server RAM/CPU
- Upgrade database instance
- Add more disk space

### Horizontal Scaling
- Separate ingestion servers
- Separate feature computation
- Separate model training
- Use message queue (RabbitMQ, SQS) for job distribution

### Database Optimization
- Add indexes on frequently queried columns
- Partition large tables by date
- Use connection pooling
- Consider read replicas for reporting

## 🧪 Testing Deployment

### Smoke Tests

```bash
# Test database connection
python -c "from src.utils.db import get_db_connection; conn = get_db_connection(); print('OK'); conn.close()"

# Test feature computation
python -m src.features.build_features --week_start 2026-01-12 --entity_id <test_entity_id>

# Test scoring
python -m src.scoring.score_week --week_start 2026-01-12

# Test report generation
python -m src.serving.generate_report --week_start 2026-01-12
```

## 🚨 Troubleshooting

### Common Issues

**Database Connection Failed:**
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in environment variables
- Check firewall rules
- Verify network connectivity

**Pipeline Fails:**
- Check logs: `tail -f /var/log/winner-engine/pipeline.log`
- Verify data exists: `psql -d winner_engine -c "SELECT COUNT(*) FROM entities;"`
- Check disk space: `df -h`
- Verify Python dependencies: `pip list`

**Out of Memory:**
- Reduce batch sizes in feature computation
- Increase server RAM
- Use database connection pooling
- Optimize queries

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Docker Documentation](https://docs.docker.com/)
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)

## ✅ Deployment Checklist

- [ ] Server provisioned and configured
- [ ] PostgreSQL installed and running
- [ ] Database created and migrations run
- [ ] Python environment set up
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Initial data seeded
- [ ] Cron job/systemd timer configured
- [ ] Logging configured
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Security hardening applied
- [ ] Smoke tests passing
- [ ] Documentation updated

---

**For questions or issues, see:**
- `HOW_IT_WORKS.md` - System architecture
- `SETUP.md` - Development setup
- `README.md` - Quick start guide

