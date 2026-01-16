# Deploy Winner Engine Now

## 🚀 Quick Start (Choose One)

### Option A: Docker Deployment (Easiest)

```bash
# 1. Make sure Docker is running
docker --version

# 2. Deploy
./deploy.sh
```

The script will:
- ✅ Check Docker installation
- ✅ Create .env file if needed
- ✅ Build Docker images
- ✅ Start PostgreSQL
- ✅ Run migrations
- ✅ Start pipeline service

### Option B: Manual Docker Setup

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env if needed

# 2. Start database
docker-compose up -d postgres

# 3. Wait for database (10 seconds)
sleep 10

# 4. Run migrations
docker-compose exec -T postgres psql -U winner_user -d winner_engine -f /docker-entrypoint-initdb.d/001_init.sql

# 5. Seed initial data
docker-compose run --rm pipeline python -m src.utils.seed_data --entities

# 6. Run first pipeline
docker-compose run --rm pipeline python -m src.pipeline --week_start 2026-01-12
```

### Option C: Local Development

```bash
# 1. Use SQLite (no PostgreSQL needed)
export USE_SQLITE=true

# 2. Set up database
python3 setup_sqlite.py

# 3. Seed data
python3 -m src.utils.seed_data --all --dt 2026-01-12

# 4. Run pipeline
python3 -m src.pipeline --week_start 2026-01-12
```

## ✅ Verify Deployment

```bash
# Check services
docker-compose ps

# Check database
docker-compose exec postgres psql -U winner_user -d winner_engine -c "SELECT COUNT(*) FROM entities;"

# View reports
ls -lh reports/

# Check logs
docker-compose logs pipeline | tail -20
```

## 📊 First Report

After deployment, your first report will be in:
- `reports/2026-01-12.md` (Markdown)
- `reports/2026-01-12.json` (JSON)

View it:
```bash
cat reports/2026-01-12.md
```

## 🔄 Weekly Automation

### Docker (Scheduler Service)
The `scheduler` service in docker-compose.yml runs weekly (Monday 2 AM).

### Local (Cron)
```bash
./scripts/setup_cron.sh
```

## 🛠️ Troubleshooting

**Database connection failed:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart
docker-compose restart postgres
```

**Pipeline fails:**
```bash
# Check logs
docker-compose logs pipeline

# Run manually with debug
docker-compose run --rm pipeline python -m src.pipeline --week_start 2026-01-12
```

**No data:**
```bash
# Seed sample data
docker-compose run --rm pipeline python -m src.utils.seed_data --all --dt 2026-01-12
```

## 📝 Environment Variables

Edit `.env` file:
```bash
nano .env
```

Key variables:
- `DB_PASSWORD` - Database password (change from default!)
- `AMAZON_API_ACCESS_KEY` - For Amazon API (optional)
- `NOTIFICATION_EMAIL` - For alerts (optional)

## 🎯 What Happens After Deployment

1. **Database** - PostgreSQL running on port 5432
2. **Pipeline** - Ready to run weekly
3. **Reports** - Generated in `reports/` directory
4. **Models** - Saved in `models/` directory (after training)

## 📈 Next Steps

1. ✅ **Deploy** - Run `./deploy.sh`
2. **Collect Data** - Add real ASINs/queries
3. **Generate Reports** - Run weekly pipeline
4. **Train Models** - After 8+ weeks of data
5. **Scale** - Move to cloud when ready

---

**Ready? Run: `./deploy.sh`**

