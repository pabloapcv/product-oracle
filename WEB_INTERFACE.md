# Winner Engine Web Interface

## 🚀 Quick Start

### Start the Web Interface

```bash
./start_web.sh
```

Or manually:
```bash
export USE_SQLITE=true
python3 web_app.py
```

Then open your browser to: **http://localhost:5000**

## 📊 Features

### Dashboard
- **System Statistics**: View total entities, Amazon listings, TikTok metrics
- **Latest Report**: See when the most recent report was generated
- **Real-time Updates**: Refresh button to update stats

### Reports View
- **Report List**: Sidebar showing all available weekly reports
- **Week Selection**: Dropdown to quickly select any week
- **Opportunity Count**: See how many opportunities each report contains

### Opportunities View
- **Ranked List**: Top opportunities sorted by winner probability
- **Detailed Cards**: Each opportunity shows:
  - Winner probability (color-coded)
  - Component scores (Demand, Competition, Margin, Risk)
  - Innovation angles
  - Experiment plans
  - Category badges

### Visual Design
- **Modern UI**: Clean, professional interface
- **Color-coded Scores**: Green (high), Yellow (medium), Red (low) probabilities
- **Responsive**: Works on desktop and mobile
- **Interactive**: Hover effects and smooth transitions

## 🎨 Interface Screenshots

The interface includes:
- Gradient header with Winner Engine branding
- Statistics cards showing system metrics
- Sidebar with report navigation
- Main content area with opportunity cards
- Color-coded probability indicators

## 🔧 API Endpoints

The web interface uses these API endpoints:

- `GET /api/reports` - List all reports
- `GET /api/report/<week_start>` - Get full report data
- `GET /api/opportunities/<week_start>` - Get top opportunities
- `GET /api/stats` - Get system statistics
- `GET /api/entities` - List entities
- `GET /api/entity/<entity_id>` - Get entity details

## 📱 Usage

1. **View Reports**: Click on any report in the sidebar or select from dropdown
2. **Browse Opportunities**: Scroll through ranked opportunities
3. **Check Stats**: View system statistics at the top
4. **Refresh Data**: Click refresh button to update

## 🎯 Next Steps

Future enhancements could include:
- Search/filter opportunities
- Detailed entity pages
- Data visualization charts
- Export reports (PDF, CSV)
- Run pipeline from interface
- Experiment tracking dashboard

---

**Start the interface: `./start_web.sh`**

