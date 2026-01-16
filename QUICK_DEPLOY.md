# Quick Deployment Guide

## 🚀 Fastest Way to Deploy

### Option 1: Docker (Recommended - 5 minutes)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env (optional - defaults work for testing)
nano .env

# 3. Deploy
./deploy.sh
```

That's it! The system will:
- Start PostgreSQL database
- Run migrations
- Build application container
- Start services

### Option 2: Local Setup (10 minutes)

```bash
# 1. Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14

# 2. Run setup script
./setup_postgres.sh

# 3. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 4. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Seed data
python -m src.utils.seed_data --entities

# 6. Run pipeline
python -m src.pipeline --week_start 2026-01-12
```

## 📋 Deployment Checklist

- [ ] Docker installed (for Docker deployment)
- [ ] PostgreSQL installed (for local deployment)
- [ ] `.env` file configured
- [ ] Database migrations run
- [ ] Initial data seeded
- [ ] Pipeline tested
- [ ] Automation set up (cron/systemd)

## 🔍 Verify Deployment

```bash
# Check services (Docker)
docker-compose ps

# Check database
docker-compose exec postgres psql -U winner_user -d winner_engine -c "SELECT COUNT(*) FROM entities;"

# Check logs
docker-compose logs pipeline

# Run test
docker-compose run --rm pipeline python test_full_pipeline.py
```

## 📊 Access Reports

Reports are generated in `reports/` directory:

```bash
# View latest report
ls -lt reports/*.md | head -1 | awk '{print $NF}' | xargs cat

# View JSON
ls -lt reports/*.json | head -1 | awk '{print $NF}' | xargs cat | python3 -m json.tool
```

## 🛠️ Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Run pipeline manually
docker-compose run --rm pipeline python -m src.pipeline --week_start 2026-01-12

# Access database
docker-compose exec postgres psql -U winner_user -d winner_engine

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d
```

## 🎯 Next Steps After Deployment

1. **Collect Real Data**
   ```bash
   docker-compose run --rm pipeline python -m src.ingest.data_collection_manager \
       --dt 2026-01-12 --all
   ```

2. **Generate First Report**
   ```bash
   docker-compose run --rm pipeline python -m src.pipeline --week_start 2026-01-12
   ```

3. **Set Up Weekly Automation**
   - Cron: `./scripts/setup_cron.sh`
   - Or use Docker scheduler service

4. **Monitor**
   - Check logs: `docker-compose logs -f`
   - Check reports: `ls -lh reports/`

---

**Ready to deploy? Run: `./deploy.sh`**

